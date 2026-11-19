"""Patch only OpenSSL in preserved clients; disposable GitHub builder, no VPS."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
import urllib.request
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import build_and_test as base  # noqa: E402

POLICY = json.loads((HERE / "client_policy.json").read_text())


def validate_client_delta(kind: str, before: dict, after: dict) -> None:
    expected = POLICY["allowed_package_updates"][kind]
    old, new = before["apks"], after["apks"]
    if set(old) != set(new):
        raise ValueError("APK package set changed")
    changed = sorted(name for name in old if old[name] != new[name])
    if changed != expected or any(
        old[n] != "3.5.9-r0" or new[n] != "3.5.9-r1" for n in changed
    ):
        raise ValueError("Unexpected APK update")
    for field in (
        "source_hashes",
        "python_packages",
        "psycopg",
        "libpq",
        "implementation",
    ):
        if before[field] != after[field]:
            raise ValueError("Client input changed: " + field)
    if not before["pip_absent"] or not after["pip_absent"]:
        raise ValueError("pip reintroduced")
    if before["native_hashes"].keys() != after["native_hashes"].keys():
        raise ValueError("Loaded native library set changed")
    for name, old_hash in before["native_hashes"].items():
        filename = Path(name).name
        new_hash = after["native_hashes"][name]
        if filename in POLICY["expected_library_hashes"]:
            if (
                new_hash != POLICY["expected_library_hashes"][filename]
                or new_hash == old_hash
            ):
                raise ValueError("Patched OpenSSL hash mismatch")
        elif new_hash != old_hash:
            raise ValueError("Unrelated native binary changed: " + name)
    loaded_names = {Path(name).name for name in after["native_hashes"]}
    if not set(POLICY["expected_library_hashes"]) <= loaded_names:
        raise ValueError("OpenSSL not loaded for verification")


def accepted_finding(v: dict[str, Any], kind: str) -> bool:
    if kind == "server":
        return base.harness.allowed_finding(v, True)
    return (
        kind == "test"
        and v.get("VulnerabilityID") == "GHSA-xmj3-9gf7-h52w"
        and v.get("PkgName") == "setuptools"
        and v.get("InstalledVersion") == "83.0.0"
        and v.get("Severity") == "LOW"
    )


def probe_script(kind: str) -> str:
    return r"""
import hashlib,importlib.metadata as m,json,os,pathlib,subprocess
import psycopg
from psycopg import pq
assert os.environ['LIVE_ENABLED']=='false'
assert os.environ['TRADE_SYSTEM_ENVIRONMENT']=='PAPER'
assert psycopg.__version__=='3.3.8' and pq.__impl__=='c'
assert pq.version()==pq.__build_version__==180007
packages=sorted((d.metadata['Name'],d.version) for d in m.distributions())
assert not any(n.lower().replace('_','-')=='psycopg-binary' for n,v in packages)
assert not any(n.lower()=='pip' for n,v in packages)
assert not list(pathlib.Path('/usr/local/bin').glob('pip*'))
bundled=pathlib.Path('/usr/local/lib/python3.12/ensurepip/_bundled')
assert not list(bundled.glob('*.whl'))
subprocess.run(['/usr/local/bin/python3.12','-c',
 "import importlib.util; assert importlib.util.find_spec('pip') is None"],check=True)
source={}
for tree in ['src','infrastructure','apps']:
 for f in sorted((pathlib.Path('/workspace')/tree).rglob('*.py')):
  source[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
if KIND=='test':
 expected=json.loads(pathlib.Path('/review/source-manifest.json').read_text())
 for name,h in expected.items():
  content=(pathlib.Path('/workspace')/name).read_bytes()
  assert hashlib.sha256(content).hexdigest()==h,name
actual={}
for block in pathlib.Path('/lib/apk/db/installed').read_text().split('\n\n'):
 row=dict(line.split(':',1) for line in block.splitlines() if ':' in line)
 if 'P' in row:actual[row['P']]=row['V']
libraries={}
for line in pathlib.Path('/proc/self/maps').read_text().splitlines():
 name=line.split()[-1]
 if '/' in name and '.so' in name:
  f=pathlib.Path(name)
  if f.is_file():libraries[name]=hashlib.sha256(f.read_bytes()).hexdigest()
print(json.dumps({'apks':actual,'source_hashes':source,'python_packages':packages,
 'native_hashes':libraries,'pip_absent':True,'psycopg':psycopg.__version__,
 'libpq':pq.version(),'implementation':pq.__impl__},sort_keys=True))
""".replace("KIND", repr(kind))


class ClientBuild(base.Build):
    def __init__(self) -> None:
        if os.environ.get("GITHUB_ACTIONS") != "true":
            raise RuntimeError("Disposable GitHub builder required")
        if os.environ.get("HML_BUILD_AUTHORIZATION") != POLICY["authorization"]:
            raise RuntimeError("Explicit client patch authorization required")
        if os.environ.get("HML_REVIEWED_COMMIT") != os.environ.get("GITHUB_SHA"):
            raise RuntimeError("Reviewed client builder SHA mismatch")
        self.work = Path(os.environ["RUNNER_TEMP"]) / "client-openssl-work"
        self.output = Path(os.environ["RUNNER_TEMP"]) / "client-openssl-review"
        self.work.mkdir(exist_ok=False)
        self.output.mkdir(exist_ok=False)
        self.logs = self.output / "logs"
        self.logs.mkdir()
        self.env = {
            k: os.environ[k] for k in ("PATH", "HOME", "LANG") if k in os.environ
        }
        self.env.update(LIVE_ENABLED="false", TRADE_SYSTEM_ENVIRONMENT="PAPER")
        self.context = POLICY["context"]
        self.package = self.work / "sealed-package"
        self.evidence = self.output / "evidence"
        self.evidence.mkdir()
        self.private = self.work / "private"
        self.private.mkdir(mode=0o700)
        self.deadline = time.monotonic() + 3300
        self.count = 0
        self.results: dict[str, dict[str, Any]] = {}

    def inputs(self) -> None:
        for index, spec in enumerate(POLICY["artifacts"]):
            path = self.work / f"artifact-{index}.zip"
            base.download_artifact(spec, path)
            with zipfile.ZipFile(path) as archive:
                if index == 0:
                    base.copy_member(
                        archive,
                        "pair/client-runtime.tar",
                        self.work / "runtime-parent.tar",
                    )
                elif index == 1:
                    for name in archive.namelist():
                        if name.startswith("sealed-package/") and not name.endswith(
                            "/"
                        ):
                            base.copy_member(archive, name, self.work / name)
                else:
                    base.copy_member(
                        archive, "postgres-patched.tar", self.work / "server.tar"
                    )
                    base.copy_member(
                        archive,
                        "SERVER-RESULT.json",
                        self.output / "SERVER-RESULT.json",
                    )
        base.harness.verify_package(self.package, POLICY["package_sha256"])
        sources = {
            "runtime": (
                self.work / "runtime-parent.tar",
                POLICY["parent_runtime_tar_sha256"],
                POLICY["parent_runtime_id"],
            ),
            "test": (
                self.package / "artifacts/test-image.tar",
                POLICY["parent_test_tar_sha256"],
                POLICY["parent_test_id"],
            ),
            "server": (
                self.work / "server.tar",
                POLICY["server_tar_sha256"],
                POLICY["server_id"],
            ),
        }
        for name, (path, checksum, identifier) in sources.items():
            if (
                base.digest(path) != checksum
                or base.prepare.image_id(path) != identifier
            ):
                raise ValueError("Input identity mismatch: " + name)
            self.docker("load", "-i", str(path), timeout=300, log=name + "-load.log")
            if self.inspect(identifier)["Id"] != identifier:
                raise ValueError("Loaded image identity mismatch")
        os.environ.pop("GH_ARTIFACT_TOKEN", None)
        base.write(self.output / "INPUTS.json", POLICY)

    def probe(self, image: str, kind: str, stage: str) -> dict[str, Any]:
        result = self.docker(
            "run",
            "--rm",
            "--pull",
            "never",
            "--network",
            "none",
            "--memory",
            "512m",
            "--cpus",
            "1",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--user",
            f"{os.getuid()}:{os.getgid()}",
            "--mount",
            f"type=bind,source={self.package / 'harness'},target=/review,readonly",
            "--entrypoint",
            "python",
            image,
            "-c",
            probe_script(kind),
            log=f"{kind}-{stage}-probe.log",
        )
        data = json.loads(result.stdout)
        base.write(self.output / f"{kind}-{stage}-probe.json", data)
        return data

    def build_clients(self) -> None:
        engine = json.loads(self.docker("version", "--format", "{{json .}}").stdout)
        buildx = self.docker("buildx", "version").stdout
        if engine["Server"]["Version"] != "29.10.0" or not re.search(
            r"\bv0\.39\.0\b", buildx
        ):
            raise ValueError("Builder version mismatch")
        base.write(
            self.output / "BUILDER.json",
            {"docker": engine, "buildx": buildx, "context": self.context},
        )
        for kind in ("runtime", "test"):
            parent = self.inspect(POLICY[f"parent_{kind}_id"])
            before = self.probe(parent["Id"], kind, "before")
            context = self.work / (kind + "-context")
            context.mkdir()
            selected = [
                s
                for s in POLICY["apks"]
                if s["name"] in POLICY["allowed_package_updates"][kind]
            ]
            for spec in selected:
                path = context / f"{spec['name']}-{spec['version']}.apk"
                with (
                    urllib.request.urlopen(spec["url"], timeout=60) as source,
                    path.open("xb") as target,
                ):
                    shutil.copyfileobj(source, target)
                if base.digest(path) != spec["sha256"]:
                    raise ValueError("Client APK hash mismatch")
            tag = f"local/dts-client-{kind}-parent:verified"
            self.docker("tag", parent["Id"], tag)
            apks = " ".join(f"/patch/{s['name']}-{s['version']}.apk" for s in selected)
            inventory = (
                "/tools/inventory.py"
                if kind == "runtime"
                else "/workspace/tools/client_profile/inventory.py"
            )
            archived = " ".join(
                f"/audit/apks/{name}-3.5.9-r0.apk"
                for name in POLICY["allowed_package_updates"][kind]
            )
            text = (
                f"FROM {tag}\n"
                "RUN --mount=type=bind,source=.,target=/patch,readonly "
                f"apk add --no-network --no-cache {apks} "
                f"&& rm -f {archived} "
                f"&& python {inventory} /audit/openssl-patch/{kind}-inventory "
                ">/dev/null\n"
            )
            (context / "Dockerfile").write_text(text)
            (self.output / f"{kind}.Dockerfile").write_text(text)
            target_tag = f"local/dts-client-{kind}-patched:review"
            args = [
                "buildx",
                "build",
                "--builder",
                self.context,
                "--platform",
                "linux/amd64",
                "--network",
                "none",
                "--no-cache",
                "--provenance=false",
                "--sbom=false",
                "--load",
                "--progress",
                "plain",
                "-t",
                target_tag,
            ]
            for limit in ("memory=3g", "cpu-period=100000", "cpu-quota=200000"):
                args += ["--resource", limit]
            self.docker(*args, str(context), timeout=900, log=kind + "-build.log")
            image = self.inspect(target_tag)
            if image["Config"] != parent["Config"]:
                raise ValueError("Client execution config changed")
            after = self.probe(image["Id"], kind, "after")
            validate_client_delta(kind, before, after)
            target = self.output / f"{kind}-patched.tar"
            self.docker("save", "-o", str(target), image["Id"], timeout=300)
            if base.prepare.image_id(target) != image["Id"]:
                raise ValueError("Client export identity mismatch")
            self.results[kind] = {
                "id": image["Id"],
                "tar_sha256": base.digest(target),
                "bytes": target.stat().st_size,
                "parent_id": parent["Id"],
                "packages_changed": POLICY["allowed_package_updates"][kind],
                "new_package_version": "3.5.9-r1",
                "pip_absent": True,
                "source_unchanged": True,
                "python_packages_unchanged": True,
                "non_openssl_native_binaries_unchanged": True,
                "execution_config_unchanged": True,
                "new_inventory": f"/audit/openssl-patch/{kind}-inventory",
                "original_source_lock_and_audit_records": (
                    "Historical pre-patch inputs, preserved; "
                    "use new inventory for current resolved state"
                ),
                "builder_commit": os.environ["GITHUB_SHA"],
                "run_id": os.environ["GITHUB_RUN_ID"],
                "signed_provenance": False,
                "persistent_adoption": False,
            }
            base.write(self.output / "CLIENT-RESULTS.json", self.results)

    def scan_clients(self) -> bool:
        scanner = POLICY["scanner"]
        self.docker(
            "pull",
            "--platform",
            "linux/amd64",
            scanner,
            timeout=300,
            log="scanner-pull.log",
        )
        cache = self.work / "scanner-cache"
        cache.mkdir()
        common = [
            "run",
            "--rm",
            "--pull",
            "never",
            "--memory",
            "2g",
            "--cpus",
            "2",
            "--user",
            f"{os.getuid()}:{os.getgid()}",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--mount",
            f"type=bind,source={cache},target=/cache",
            "--mount",
            f"type=bind,source={self.work},target=/input,readonly",
            "--mount",
            f"type=bind,source={self.output},target=/output",
        ]
        self.docker(
            *common,
            "--network",
            "bridge",
            scanner,
            "--cache-dir",
            "/cache",
            "image",
            "--download-db-only",
            timeout=600,
            log="scanner-db.log",
        )
        metadata = json.loads((cache / "db/metadata.json").read_text())
        updated = datetime.fromisoformat(metadata["UpdatedAt"].replace("Z", "+00:00"))
        if (
            not timedelta(minutes=-5)
            <= datetime.now(UTC) - updated
            <= timedelta(hours=48)
        ):
            raise ValueError("Scanner database not current")
        base.write(self.output / "SCANNER-DATABASE.json", metadata)
        self.docker(
            "run",
            "--rm",
            "--network",
            "none",
            scanner,
            "--version",
            log="scanner-version.txt",
        )
        for kind in ("runtime", "test"):
            shutil.copyfile(
                self.output / f"{kind}-patched.tar", self.work / f"{kind}-patched.tar"
            )
        inputs = {
            "server": "server.tar",
            "runtime-parent": "runtime-parent.tar",
            "test-parent": "sealed-package/artifacts/test-image.tar",
            "runtime": "runtime-patched.tar",
            "test": "test-patched.tar",
        }
        summaries = {}
        for name, path in inputs.items():
            self.docker(
                *common,
                "--network",
                "none",
                scanner,
                "--cache-dir",
                "/cache",
                "image",
                "--skip-db-update",
                "--offline-scan",
                "--input",
                "/input/" + path,
                "--scanners",
                "vuln,secret",
                "--image-config-scanners",
                "misconfig,secret",
                "--list-all-pkgs",
                "--format",
                "json",
                "--output",
                f"/output/{name}-scan.json",
                timeout=600,
                log=name + "-scan.log",
            )
            data = json.loads((self.output / f"{name}-scan.json").read_text())
            secret_hits = sum(
                len(t.get("Secrets", [])) for t in data.get("Results", [])
            )
            if secret_hits:
                (self.output / f"{name}-scan.json").unlink()
                raise RuntimeError("Secret detected; raw report withheld")
            self.docker(
                *common,
                "--network",
                "none",
                scanner,
                "convert",
                "--format",
                "cyclonedx",
                "--output",
                f"/output/{name}-sbom.cdx.json",
                f"/output/{name}-scan.json",
                timeout=120,
                log=name + "-sbom.log",
            )
            findings = [
                v for t in data.get("Results", []) for v in t.get("Vulnerabilities", [])
            ]
            summaries[name] = {
                "findings": [
                    {
                        k: v.get(k)
                        for k in [
                            "VulnerabilityID",
                            "PkgName",
                            "InstalledVersion",
                            "FixedVersion",
                            "Severity",
                        ]
                    }
                    for v in findings
                ],
                "secret_hits": secret_hits,
                "config_findings": [
                    {k: v.get(k) for k in ["ID", "Severity", "Title"]}
                    for t in data.get("Results", [])
                    for v in t.get("Misconfigurations", [])
                ],
                "only_prior_scope_findings": all(
                    accepted_finding(v, name) for v in findings
                )
                if name in {"server", "runtime", "test"}
                else None,
            }
        base.write(self.output / "SCAN-SUMMARY.json", summaries)
        return all(
            summaries[k]["only_prior_scope_findings"]
            for k in ("server", "runtime", "test")
        )

    def run(self) -> None:
        try:
            self.inputs()
            self.build_clients()
            if not self.scan_clients():
                raise RuntimeError(
                    "New security finding requires review before pair tests"
                )
            # Select new client IDs in memory for the inherited isolated pair checks.
            original = base.POLICY.copy()
            base.POLICY.update(
                runtime_id=self.results["runtime"]["id"],
                test_id=self.results["test"]["id"],
            )
            try:
                self.pair(POLICY["server_id"])
            finally:
                base.POLICY.clear()
                base.POLICY.update(original)
            record = json.loads((self.output / "PAIR-RESULT.json").read_text())
            record.update(
                client_openssl_corrected=True,
                client_sources_and_psycopg_libpq_preserved=True,
            )
            base.write(self.output / "PAIR-RESULT.json", record)
            base.write(
                self.output / "STATUS.json",
                {
                    "result": "COMPLETED_FOR_REVIEW",
                    "vps_access": False,
                    "backup_automation": "DEFERRED_BY_USER",
                    "persistent_adoption": False,
                },
            )
        except BaseException as error:
            base.write(
                self.output / "INTERRUPTION.json",
                {
                    "type": type(error).__name__,
                    "reason": str(error)[:1000],
                    "vps_access": False,
                },
            )
            raise
        finally:
            (self.output / "SHA256SUMS").write_text(
                "".join(
                    f"{base.digest(p)}  {p.relative_to(self.output).as_posix()}\n"
                    for p in sorted(self.output.rglob("*"))
                    if p.is_file() and p.name != "SHA256SUMS"
                )
            )


if __name__ == "__main__":
    ClientBuild().run()
