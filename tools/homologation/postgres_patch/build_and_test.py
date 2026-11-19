"""Disposable GitHub builder only: patch server, scan and exercise preserved clients."""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.dont_write_bytecode = True
import prepare  # noqa: E402
import runner as harness  # noqa: E402

POLICY = json.loads((HERE / "policy.json").read_text())


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def safe_name(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        bool(name)
        and not path.is_absolute()
        and ".." not in path.parts
        and not any(char in name for char in ("\\", ":", "\x00"))
    )


def validate_package_changes(
    before: list[str], after: list[str]
) -> tuple[list[str], list[str]]:
    removed = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    if removed != ["libcrypto3-3.5.9-r0", "libssl3-3.5.9-r0"] or added != [
        "libcrypto3-3.5.9-r1",
        "libssl3-3.5.9-r1",
    ]:
        raise ValueError("Unexpected APK change")
    return removed, added


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def download_artifact(spec: dict[str, Any], target: Path) -> None:
    url = (
        "https://api.github.com/repos/liraneto1/DeepTradeSystem/"
        f"actions/artifacts/{spec['id']}/zip"
    )
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": "Bearer " + os.environ["GH_ARTIFACT_TOKEN"],
            "Accept": "application/vnd.github+json",
            "User-Agent": "DeepTrade-HML",
        },
    )
    try:
        response = urllib.request.build_opener(NoRedirect).open(request, timeout=60)
    except urllib.error.HTTPError as error:
        if error.code != 302:
            raise RuntimeError(f"Artifact HTTP {error.code}") from None
        location = error.headers.get("Location", "")
        parsed = urllib.parse.urlparse(location)
        if parsed.scheme != "https" or not (parsed.hostname or "").endswith(
            ".blob.core.windows.net"
        ):
            raise ValueError("Unexpected artifact redirect") from None
        # Never forward the GitHub credential to artifact storage.
        response = urllib.request.urlopen(location, timeout=180)
    with response, target.open("xb") as stream:
        shutil.copyfileobj(response, stream)
    if digest(target) != spec["sha256"]:
        raise ValueError("Artifact ZIP checksum mismatch")


def copy_member(archive: zipfile.ZipFile, name: str, dest: Path) -> None:
    if not safe_name(name):
        raise ValueError("Unsafe ZIP member")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with archive.open(name) as source, dest.open("xb") as target:
        shutil.copyfileobj(source, target)


class Build:
    def __init__(self) -> None:
        if os.environ.get("GITHUB_ACTIONS") != "true":
            raise RuntimeError("GitHub-hosted disposable builder required")
        if (
            os.environ.get("HML_BUILD_AUTHORIZATION")
            != "TS-PLAN-HML-002:patch-postgres"
        ):
            raise RuntimeError("Explicit patch authorization required")
        if os.environ.get("HML_REVIEWED_COMMIT") != os.environ.get("GITHUB_SHA"):
            raise RuntimeError("Reviewed builder SHA mismatch")
        self.work = Path(os.environ["RUNNER_TEMP"]) / "postgres-openssl-work"
        self.output = Path(os.environ["RUNNER_TEMP"]) / "postgres-openssl-review"
        self.work.mkdir(exist_ok=False)
        self.output.mkdir(exist_ok=False)
        self.logs = self.output / "logs"
        self.logs.mkdir()
        self.env = {
            key: os.environ[key]
            for key in ("PATH", "HOME", "LANG")
            if key in os.environ
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

    def docker(
        self, *args: str, log: str | None = None, timeout: int = 180, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        remaining = int(self.deadline - time.monotonic())
        if remaining <= 0:
            raise TimeoutError("Builder deadline")
        result = subprocess.run(
            ["docker", "--context", self.context, *args],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=min(timeout, remaining),
            check=False,
        )
        self.count += 1
        filename = log or f"command-{self.count:03}.log"
        (self.logs / filename).write_text(
            result.stdout + result.stderr, encoding="utf-8"
        )
        if check and result.returncode:
            raise RuntimeError(f"Docker command failed: {filename}")
        return result

    def inspect(self, image: str) -> dict[str, Any]:
        obj = json.loads(self.docker("image", "inspect", image).stdout)[0]
        if (obj["Os"], obj["Architecture"]) != ("linux", "amd64"):
            raise ValueError("Image platform mismatch")
        return obj

    def inputs(self) -> None:
        for index, spec in enumerate(POLICY["artifacts"]):
            path = self.work / f"artifact-{index}.zip"
            download_artifact(spec, path)
            with zipfile.ZipFile(path) as archive:
                if index == 0:
                    for name, target in [
                        ("server/rebuilt-image.tar", "server.tar"),
                        ("pair/client-runtime.tar", "runtime.tar"),
                    ]:
                        copy_member(archive, name, self.work / target)
                else:
                    for name in archive.namelist():
                        if name.startswith("sealed-package/") and not name.endswith(
                            "/"
                        ):
                            copy_member(archive, name, self.work / name)
        if digest(self.package / "PACKAGE-SHA256SUMS") != POLICY["package_sha256"]:
            raise ValueError("Frozen package changed")
        harness.verify_package(self.package, POLICY["package_sha256"])
        for key, path in [
            ("parent", self.work / "server.tar"),
            ("runtime", self.work / "runtime.tar"),
            ("test", self.package / "artifacts/test-image.tar"),
        ]:
            expected = POLICY[
                "parent_tar_sha256" if key == "parent" else key + "_tar_sha256"
            ]
            if digest(path) != expected:
                raise ValueError("Input TAR hash mismatch: " + key)
            self.docker("load", "-i", str(path), timeout=300, log=key + "-load.log")
            identifier = POLICY["parent_server_id" if key == "parent" else key + "_id"]
            if self.inspect(identifier)["Id"] != identifier:
                raise ValueError("Loaded image ID mismatch")
        # Revoke artifact credential from this process after the download stage.
        os.environ.pop("GH_ARTIFACT_TOKEN", None)
        write(self.output / "INPUTS.json", POLICY)

    def image_probe(self, image: str, name: str) -> dict[str, Any]:
        script = (
            'set -eu; test "$GOSU_VERSION" = 1.20; '
            "gosu --version; postgres --version; "
            f"echo '{POLICY['gosu_sha256']}  /usr/local/bin/gosu' | sha256sum -c -; "
            f"echo '{POLICY['postgres_sha256']}  /usr/local/bin/postgres' "
            "| sha256sum -c -; "
            "gosu postgres id; gosu nobody id; "
            'test "$(gosu postgres id -u)" != 0; '
            'test "$(gosu nobody id -u)" = "$(id -u nobody)"; '
            "printf '\\nPACKAGES\\n'; apk info -v | sort"
        )
        raw = self.docker(
            "run",
            "--rm",
            "--pull",
            "never",
            "--network",
            "none",
            "--memory",
            "256m",
            "--cpus",
            "1",
            "--entrypoint",
            "sh",
            image,
            "-ec",
            script,
            log=name + "-identity.log",
        ).stdout
        return {
            "checks": raw.split("\nPACKAGES\n", 1)[0],
            "packages": raw.split("\nPACKAGES\n", 1)[1].splitlines(),
        }

    def build(self) -> str:
        engine = json.loads(self.docker("version", "--format", "{{json .}}").stdout)
        if engine["Server"]["Version"] != "29.10.0":
            raise ValueError("Unexpected Engine version")
        buildx = self.docker("buildx", "version").stdout
        if not re.search(r"\bv0\.39\.0\b", buildx):
            raise ValueError("Unexpected Buildx version")
        write(
            self.output / "BUILDER.json",
            {"docker": engine, "buildx": buildx, "context": self.context},
        )
        parent = self.inspect(POLICY["parent_server_id"])
        before = self.image_probe(parent["Id"], "parent")
        context = self.work / "context"
        context.mkdir()
        for spec in POLICY["apks"]:
            path = context / f"{spec['name']}-{spec['version']}.apk"
            with (
                urllib.request.urlopen(spec["url"], timeout=60) as source,
                path.open("xb") as target,
            ):
                shutil.copyfileobj(source, target)
            if digest(path) != spec["sha256"]:
                raise ValueError("APK SHA256 mismatch")
        self.docker("tag", parent["Id"], "local/dts-postgres-parent:verified")
        text = (
            "FROM local/dts-postgres-parent:verified\n"
            "RUN --mount=type=bind,source=.,target=/patch,readonly "
            "apk add --no-network --no-cache "
            "/patch/libcrypto3-3.5.9-r1.apk /patch/libssl3-3.5.9-r1.apk\n"
        )
        (context / "Dockerfile").write_text(text)
        (self.output / "Dockerfile").write_text(text)
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
            "local/dts-postgres-patched:review",
        ]
        for limit in ["memory=3g", "cpu-period=100000", "cpu-quota=200000"]:
            args += ["--resource", limit]
        self.docker(*args, str(context), log="build.log", timeout=900)
        image = self.inspect("local/dts-postgres-patched:review")
        # No entrypoint/user/environment/healthcheck or PostgreSQL upgrade is implicit.
        if image["Config"] != parent["Config"]:
            raise ValueError("Unexpected image execution configuration change")
        after = self.image_probe(image["Id"], "patched")
        removed, added = validate_package_changes(before["packages"], after["packages"])
        tar = self.output / "postgres-patched.tar"
        self.docker("save", "-o", str(tar), image["Id"], timeout=300)
        if prepare.image_id(tar) != image["Id"]:
            raise ValueError("Exported OCI image identity mismatch")
        write(
            self.output / "SERVER-RESULT.json",
            {
                "id": image["Id"],
                "tar_sha256": digest(tar),
                "bytes": tar.stat().st_size,
                "parent_id": parent["Id"],
                "removed": removed,
                "added": added,
                "gosu_version": "1.20",
                "gosu_sha256": POLICY["gosu_sha256"],
                "postgres_sha256": POLICY["postgres_sha256"],
                "execution_config_unchanged": True,
                "builder_commit": os.environ["GITHUB_SHA"],
                "run_id": os.environ["GITHUB_RUN_ID"],
                "signed_provenance": False,
                "persistent_adoption": False,
            },
        )
        return image["Id"]

    def scan(self) -> bool:
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
        base = [
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
            *base,
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
            raise ValueError("Scanner database age invalid")
        write(self.output / "SCANNER-DATABASE.json", metadata)
        self.docker(
            "run",
            "--rm",
            "--network",
            "none",
            scanner,
            "--version",
            log="scanner-version.txt",
        )
        # Place the output TAR in the read-only scan input tree without modifying it.
        shutil.copyfile(self.output / "postgres-patched.tar", self.work / "patched.tar")
        inputs = {
            "parent": "server.tar",
            "server": "patched.tar",
            "runtime": "runtime.tar",
            "test": "sealed-package/artifacts/test-image.tar",
        }
        summaries = {}
        for name, path in inputs.items():
            self.docker(
                *base,
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
            self.docker(
                *base,
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
            data = json.loads((self.output / f"{name}-scan.json").read_text())
            findings = [
                v for r in data.get("Results", []) for v in r.get("Vulnerabilities", [])
            ]
            secret_count = sum(
                len(r.get("Secrets", [])) for r in data.get("Results", [])
            )
            # No image secrets may be exported as public evidence.
            if secret_count:
                (self.output / f"{name}-scan.json").unlink()
                raise RuntimeError("Secret detected; raw scan withheld from artifact")
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
                "secret_count": secret_count,
                "config_findings": [
                    {k: v.get(k) for k in ["ID", "Severity", "Title"]}
                    for r in data.get("Results", [])
                    for v in r.get("Misconfigurations", [])
                ],
                "server_prior_exception_only": all(
                    harness.allowed_finding(v, True) for v in findings
                )
                if name == "server"
                else None,
            }
        write(self.output / "SCAN-SUMMARY.json", summaries)
        return bool(summaries["server"]["server_prior_exception_only"])

    def pair(self, server: str) -> None:
        trial = harness.Runner(self.package, "pgfix-" + os.environ["GITHUB_RUN_ID"])
        # Builder-only experiment; approved package and constants are preserved.
        trial.root = self.work / "trial"
        trial.root.mkdir()
        trial.private = self.private
        trial.evidence = self.evidence
        trial.manifest["server"] = trial.manifest["server"] | {"id": server}
        trial.env["HML_EVIDENCE"] = str(self.evidence)
        trial.env["HML_PASSWORD_FILE"] = str(self.private / "postgres-password")
        trial.env["HML_OPERATOR_UID"] = str(os.getuid())
        trial.env["HML_OPERATOR_GID"] = str(os.getgid())
        trial.password = secrets.token_hex(32)
        (self.private / "postgres-password").write_text(trial.password)
        (self.private / "postgres-password").chmod(0o600)

        def docker(*args: str, **kwargs: Any) -> subprocess.CompletedProcess[str]:
            return trial.command(["docker", "--context", self.context, *args], **kwargs)

        trial.docker = docker

        def assert_postgres() -> None:
            obj = json.loads(trial.docker("inspect", trial.postgres_id()).stdout)[0]
            harness.owned_resource(obj, trial.run_id, trial.project, "container")
            if obj["Image"] != server or obj["HostConfig"].get("PortBindings"):
                raise ValueError("Wrong server or published port")
            if (
                obj["State"].get("OOMKilled")
                or obj["State"].get("Health", {}).get("Status") != "healthy"
            ):
                raise ValueError("Server not healthy or OOM")

        trial.assert_postgres = assert_postgres
        for key, image in [
            ("SERVER", server),
            ("RUNTIME", POLICY["runtime_id"]),
            ("TEST", POLICY["test_id"]),
        ]:
            trial.docker("tag", image, trial.env[f"HML_{key}_IMAGE"])
        trial.compose("config", "--quiet")
        before = trial.inventory()
        write(self.evidence / "inventory-before.json", {"before": before})
        trial.record_state("PAIR", "IN_PROGRESS")
        try:
            trial.identity_check()
            trial.compose(
                "up",
                "-d",
                "--no-build",
                "--pull",
                "never",
                "--wait",
                "--wait-timeout",
                "90",
                "postgres",
                log="postgres-up.log",
            )
            trial.assert_postgres()
            trial.audit_network()
            trial.job("runtime", "auth")
            trial.tls_setup()
            trial.job("runtime", "tls")
            for action in ["inventory", "base", "concurrency", "monitor"]:
                trial.job("tests", action)
            trial.job("runtime", "runtime-inventory")
            trial.compare_native()
            results = {
                name: harness.junit(
                    self.evidence / f"{name}.xml", name == "concurrency"
                )
                for name in ["base", "concurrency", "monitor"]
            }
            trial.job("runtime", "persist-write")
            trial.compose("restart", "postgres")
            trial.wait_ready()
            trial.job("runtime", "persist-read")
            trial.audit_network()
            write(
                self.output / "PAIR-RESULT.json",
                {
                    "result": "PASS",
                    "tests": results,
                    "server_id": server,
                    "runtime_id": POLICY["runtime_id"],
                    "test_id": POLICY["test_id"],
                    "auth": json.loads((self.evidence / "auth.json").read_text()),
                    "tls": json.loads((self.evidence / "tls.json").read_text()),
                    "persistence": json.loads(
                        (self.evidence / "persistence-after.json").read_text()
                    ),
                    "candidate": POLICY["candidate"],
                    "persistent_adoption": False,
                    "clients_remain_security_review_pending": True,
                    "backup_automation": "DEFERRED_BY_USER",
                    "vps_access": False,
                },
            )
        except BaseException as error:
            write(
                self.output / "PAIR-INTERRUPTION.json",
                {
                    "type": type(error).__name__,
                    "reason": harness.redact(str(error), trial.password),
                },
            )
            raise
        finally:
            trial.stop_owned()
            trial.record_state("PAIR", "STOPPED_FOR_REVIEW")
            trial.collect()
            shutil.copyfile(trial.root / "state.json", self.output / "PAIR-STATE.json")
            # Remove only the labelled trial resources inside this disposable VM.
            trial.compose(
                "down", "--volumes", "--remove-orphans", log="builder-cleanup.log"
            )

    def run(self) -> None:
        try:
            self.inputs()
            server = self.build()
            if not self.scan():
                raise RuntimeError(
                    "Patched server has findings requiring review; pair not started"
                )
            self.pair(server)
            write(
                self.output / "STATUS.json",
                {
                    "result": "COMPLETED_FOR_REVIEW",
                    "vps_access": False,
                    "backup_automation": "DEFERRED_BY_USER",
                    "persistent_adoption": False,
                },
            )
        except BaseException as error:
            write(
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
                    f"{digest(p)}  {p.relative_to(self.output).as_posix()}\n"
                    for p in sorted(self.output.rglob("*"))
                    if p.is_file() and p.name != "SHA256SUMS"
                )
            )


if __name__ == "__main__":
    Build().run()
