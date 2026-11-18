"""Review-only package runner; no action on import. Linux/amd64, explicit run token.

preflight is read-only. run requires the exact reviewed package checksum, a sealed
test image, and a separate authorization token. No builder, registry publication,
host network, daemon socket mount, backup scheduler or permanent services.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import secrets
import shutil
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from threading import Event, Thread
from typing import Any

sys.dont_write_bytecode = True
from prepare import (  # noqa: E402 - disable bytecode before importing package module
    CANDIDATE,
    SCANNER,
    SERVER_ID,
    digest,
    image_id,
    json_write,
)

LABEL = "io.deeptrade.hml.run"
OWNER = "io.deeptrade.hml.owner"
OWNER_VALUE = "TS-PLAN-HML-002"
GOSU_HASH = "99450e87c219ee02cf76f2a34285c75036e74de7c2d1831e8e129ff9ba45e1cb"
PG_HASH = "0d21e79710dd311f8ae671c0a4cda5b622652dfe7ddc624a019590c59a694c93"
RUN_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,31}\Z")


def checked_run_id(value: str) -> str:
    if not RUN_PATTERN.fullmatch(value):
        raise ValueError("Invalid run-id")
    return value


def redact(data: str, password: str = "") -> str:
    if password:
        data = data.replace(password, "[REDACTED]")
    return re.sub(
        r"(postgres(?:ql)?(?:\+psycopg)?://[^:\s/]+:)[^@\s]+@", r"\1[REDACTED]@", data
    )


def verify_package(package: Path, expected: str | None = None) -> dict[str, Any]:
    sums = package / "PACKAGE-SHA256SUMS"
    if expected and digest(sums) != expected.lower():
        raise ValueError("Reviewed package checksum mismatch")
    listed = set()
    for line in sums.read_text().splitlines():
        checksum, name = line.split("  ", 1)
        path = package / name
        if (
            not path.resolve().is_relative_to(package.resolve())
            or path.is_symlink()
            or not path.is_file()
            or digest(path) != checksum
        ):
            raise ValueError("Package content mismatch: " + name)
        listed.add(name)
    for path in package.rglob("*"):
        if path.is_symlink():
            raise ValueError("Package symlinks forbidden")
        if path.is_file():
            name = path.relative_to(package).as_posix()
            if name not in listed and name != "PACKAGE-SHA256SUMS":
                if name not in {
                    "artifacts/server.tar",
                    "artifacts/runtime.tar",
                    "artifacts/test-image.tar",
                }:
                    raise ValueError("Unreviewed extra file: " + name)
    manifest: dict[str, Any] = json.loads((package / "manifest.json").read_text())
    if manifest["candidate"] != CANDIDATE or manifest["plan"] != OWNER_VALUE:
        raise ValueError("Wrong candidate or plan")
    if manifest["server"]["id"] != SERVER_ID or manifest["scanner"] != SCANNER:
        raise ValueError("Unapproved server/scanner")
    return manifest


def junit(path: Path, concurrency: bool = False) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    suites = [x for x in root.iter("testsuite")]
    cases = list(root.iter("testcase"))
    if not cases or any(
        c.find("failure") is not None
        or c.find("error") is not None
        or c.find("skipped") is not None
        for c in cases
    ):
        raise ValueError("Empty/failing/skipped required JUnit")
    if any(
        int(s.attrib.get("errors", "0")) or int(s.attrib.get("failures", "0"))
        for s in suites
    ):
        raise ValueError("Suite-level failure")
    proofs = []
    if concurrency:
        if len(cases) != 6:
            raise ValueError("Six concurrency cases required")
        for case in cases:
            prop = case.find('./properties/property[@name="concurrency_proof"]')
            if prop is None:
                raise ValueError("Missing concurrency proof")
            proof = json.loads(prop.attrib["value"])
            if (
                proof["waiting_pid"] == proof["blocking_pid"]
                or proof["wait_event_type"] != "Lock"
                or proof["durable_effects"] != 1
                or proof["durable_processed_ids"] != 1
                or proof["durable_acknowledgements"] != 2
                or proof["pending_after_restart"] != 0
            ):
                raise ValueError("Concurrency invariant failed")
            proofs.append(proof)
    return {
        "passed": len(cases),
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "proofs": proofs,
    }


def allowed_finding(v: dict[str, Any], server: bool) -> bool:
    return (
        server
        and v.get("VulnerabilityID") == "CVE-2026-39824"
        and v.get("PkgName") == "golang.org/x/sys"
        and v.get("InstalledVersion") == "v0.1.0"
        and v.get("Severity") == "UNKNOWN"
    )


def owned_resource(
    obj: dict[str, Any], run_id: str, project: str, kind: str
) -> dict[str, Any]:
    labels = (
        obj.get("Config", {}).get("Labels")
        if kind == "container"
        else obj.get("Labels")
    )
    labels = labels or {}
    if (
        labels.get(LABEL) != run_id
        or labels.get(OWNER) != OWNER_VALUE
        or labels.get("com.docker.compose.project") not in {None, project}
    ):
        raise ValueError("Foreign resource; refusing operation")
    key = obj.get("Name", "").lstrip("/") if kind == "volume" else obj.get("Id", "")
    if not key or (kind != "volume" and not re.fullmatch(r"[0-9a-f]{64}", key)):
        raise ValueError("Invalid resource identity")
    return {"kind": kind, "id": key}


class Runner:
    def __init__(self, package: Path, run_id: str) -> None:
        self.package = package.resolve()
        self.run_id = checked_run_id(run_id)
        self.project = "dts-hml-functional-" + self.run_id
        self.root = Path.home() / "dts-hml-trials" / self.run_id
        if self.root.is_symlink() or self.root.parent.is_symlink():
            raise ValueError("Run directory symlinks forbidden")
        self.evidence = self.root / "evidence"
        self.private = self.root / "private"
        self.manifest = verify_package(self.package)
        self.password = ""
        self.deadline = time.monotonic() + 5400
        self.env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(Path.home()),
            "LANG": "C.UTF-8",
            "HML_OPERATOR_UID": str(getattr(os, "getuid", lambda: 0)()),
            "HML_OPERATOR_GID": str(getattr(os, "getgid", lambda: 0)()),
            "HML_RUN_ID": self.run_id,
            "HML_PROJECT": self.project,
            "HML_SERVER_IMAGE": "local/dts-hml-server:" + self.run_id,
            "HML_RUNTIME_IMAGE": "local/dts-hml-runtime:" + self.run_id,
            "HML_TEST_IMAGE": "local/dts-hml-tests:" + self.run_id,
            "HML_HARNESS": str(self.package / "harness"),
            "HML_EVIDENCE": str(self.evidence),
            "HML_PASSWORD_FILE": str(self.private / "postgres-password"),
        }

    def command(
        self,
        args: list[str],
        log: str | None = None,
        timeout: int = 180,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        remaining = int(self.deadline - time.monotonic())
        if remaining <= 0:
            raise TimeoutError("Global 90-minute deadline")
        result = subprocess.run(
            args,
            env=self.env,
            text=True,
            capture_output=True,
            timeout=min(timeout, remaining),
            check=False,
        )
        if log:
            (self.evidence / log).write_text(
                redact(result.stdout + result.stderr, self.password), encoding="utf-8"
            )
        if check and result.returncode:
            raise RuntimeError("Command failed; inspect sanitized evidence")
        return result

    def docker(self, *args: str, **kw: Any) -> subprocess.CompletedProcess[str]:
        return self.command(
            ["sudo", "-n", "docker", "--context", "default", *args], **kw
        )

    def compose(self, *args: str, **kw: Any) -> subprocess.CompletedProcess[str]:
        return self.docker(
            "compose",
            "--env-file",
            "/dev/null",
            "-p",
            self.project,
            "-f",
            str(self.package / "compose.yml"),
            *args,
            **kw,
        )

    def inventory(self) -> dict[str, Any]:
        return {
            "containers": self.docker("ps", "-aq", "--no-trunc").stdout.split(),
            "networks": self.docker("network", "ls", "-q", "--no-trunc").stdout.split(),
            "volumes": self.docker("volume", "ls", "-q").stdout.split(),
            "images": sorted(
                set(self.docker("image", "ls", "-q", "--no-trunc").stdout.split())
            ),
        }

    def owned(self) -> list[dict[str, Any]]:
        result = []
        for kind, command in [
            ("container", ["ps", "-aq", "--no-trunc"]),
            ("network", ["network", "ls", "-q", "--no-trunc"]),
            ("volume", ["volume", "ls", "-q"]),
        ]:
            ids = self.docker(
                *command, "--filter", f"label={LABEL}={self.run_id}"
            ).stdout.split()
            for identifier in ids:
                args = (
                    ["inspect", identifier]
                    if kind == "container"
                    else [kind, "inspect", identifier]
                )
                obj = json.loads(self.docker(*args).stdout)[0]
                result.append(owned_resource(obj, self.run_id, self.project, kind))
        return sorted(result, key=lambda x: (x["kind"], x["id"]))

    def inspect_image(self, alias: str, expected: str) -> dict[str, Any]:
        obj: dict[str, Any] = json.loads(self.docker("image", "inspect", alias).stdout)[
            0
        ]
        if obj["Id"] != expected or (obj["Os"], obj["Architecture"]) != (
            "linux",
            "amd64",
        ):
            raise ValueError("Image identity/platform mismatch")
        return obj

    def preflight(self, require_artifacts: bool = True) -> dict[str, Any]:
        if platform.system() != "Linux" or platform.machine() not in {
            "x86_64",
            "amd64",
        }:
            raise ValueError("Linux/amd64 required")
        if getattr(os, "geteuid", lambda: 0)() == 0 or Path.home() != Path(
            "/home/dts-admin"
        ):
            raise ValueError("Run as dts-admin, not root; use sudo only for Docker")
        self.docker("version", "--format", "{{json .}}")
        endpoint = self.docker(
            "context", "inspect", "default", "--format", "{{.Endpoints.docker.Host}}"
        ).stdout.strip()
        if endpoint != "unix:///var/run/docker.sock":
            raise ValueError("Local Docker endpoint required")
        mem = re.search(r"MemAvailable:\s+(\d+)", Path("/proc/meminfo").read_text())
        if not mem or int(mem.group(1)) * 1024 < 4 * 1024**3:
            raise ValueError("At least 4 GiB available RAM required")
        if shutil.disk_usage(Path.home()).free < 20 * 1024**3:
            raise ValueError("At least 20 GiB free disk required")
        if self.owned() or self.root.exists():
            raise ValueError("Run-id already used; never reuse")
        for name in ["openssl", "ss"]:
            if not shutil.which(name):
                raise ValueError("Required host tool missing: " + name)
        artifacts = {}
        if require_artifacts:
            if (
                not self.manifest["ready_for_execution_review"]
                or not self.manifest["test"]
            ):
                raise ValueError(
                    "Draft package: test image TAR/ID must be sealed and reviewed"
                )
            for kind in ["server", "runtime", "test"]:
                spec = self.manifest[kind]
                path = self.package / "artifacts" / spec["filename"]
                if digest(path) != spec["tar_sha256"] or image_id(path) != spec["id"]:
                    raise ValueError("Artifact identity mismatch: " + kind)
                artifacts[kind] = spec["id"]
        # Evaluate the model without creating volumes or secret files.
        config = self.compose("config", "--format", "json").stdout
        obj = json.loads(config)
        if any(
            s.get("ports") or s.get("privileged") or s.get("network_mode") == "host"
            for s in obj["services"].values()
        ):
            raise ValueError("Forbidden port publication/privileged/host networking")
        if not obj["networks"]["isolated"].get("internal"):
            raise ValueError("Internal isolated network required")
        self.compose("config", "--quiet")
        return {
            "phase": "E00",
            "result": "PASS",
            "artifacts": artifacts,
            "before": self.inventory(),
            "endpoint": endpoint,
            "backup_automation": "DEFERRED_BY_USER",
        }

    def record_state(self, phase: str, status: str) -> None:
        json_write(
            self.root / "state.json",
            {
                "run_id": self.run_id,
                "project": self.project,
                "package": str(self.package),
                "package_sha256": digest(self.package / "PACKAGE-SHA256SUMS"),
                "phase": phase,
                "status": status,
                "resources": self.owned(),
                "persistent_adoption": False,
                "backup_automation": "DEFERRED_BY_USER",
            },
        )

    def load_images(self) -> None:
        for kind, env_name in [
            ("server", "HML_SERVER_IMAGE"),
            ("runtime", "HML_RUNTIME_IMAGE"),
            ("test", "HML_TEST_IMAGE"),
        ]:
            spec = self.manifest[kind]
            alias = self.env[env_name]
            if self.docker("image", "inspect", alias, check=False).returncode == 0:
                raise ValueError("Run alias already exists")
            path = self.package / "artifacts" / spec["filename"]
            # Docker-save archives may carry aliases. Do not overwrite a foreign tag.
            import tarfile

            with tarfile.open(path) as archive:
                stream = archive.extractfile("manifest.json")
                if stream is None:
                    raise ValueError("Missing archive manifest")
                for entry in json.load(stream):
                    for tag in entry.get("RepoTags") or []:
                        found = self.docker("image", "inspect", tag, check=False)
                        if (
                            found.returncode == 0
                            and json.loads(found.stdout)[0]["Id"] != spec["id"]
                        ):
                            raise ValueError(
                                "Archive would overwrite preexisting image alias"
                            )
            self.docker("load", "-i", str(path), log=kind + "-load.log", timeout=300)
            self.inspect_image(spec["id"], spec["id"])
            self.docker("tag", spec["id"], alias)

    def scan(self, allow_downloads: bool) -> None:
        scanner = self.manifest["scanner"]
        if self.docker("image", "inspect", scanner, check=False).returncode:
            if not allow_downloads:
                raise ValueError("Scanner absent; download not authorized")
            self.docker(
                "pull",
                "--platform",
                "linux/amd64",
                scanner,
                log="scanner-pull.log",
                timeout=300,
            )
        if not allow_downloads:
            raise ValueError(
                "Fresh vulnerability database download requires authorization"
            )
        self.docker(
            "image",
            "inspect",
            scanner,
            "--format",
            "{{.Id}}",
            log="scanner-image-id.txt",
        )
        cache = self.private / "scanner-cache"
        cache.mkdir()
        base = [
            "run",
            "--pull",
            "never",
            "--rm",
            "--memory",
            "2g",
            "--cpus",
            "2",
            "--label",
            f"{LABEL}={self.run_id}",
            "--label",
            f"{OWNER}={OWNER_VALUE}",
            "--mount",
            f"type=bind,source={cache},target=/cache",
            "--mount",
            f"type=bind,source={self.package / 'artifacts'},target=/input,readonly",
            "--mount",
            f"type=bind,source={self.evidence},target=/output",
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
            log="scanner-db-update.log",
            timeout=600,
        )
        metadata = json.loads((cache / "db/metadata.json").read_text())
        json_write(self.evidence / "scanner-database.json", metadata)
        from datetime import UTC, datetime, timedelta

        updated = datetime.fromisoformat(metadata["UpdatedAt"].replace("Z", "+00:00"))
        age = datetime.now(UTC) - updated
        if age < timedelta(minutes=-5) or age > timedelta(hours=48):
            raise ValueError("Scanner database is not fresh (48-hour maximum)")
        for kind in ["server", "runtime"]:
            args = [
                *base,
                "--network",
                "none",
                scanner,
                "--cache-dir",
                "/cache",
                "image",
                "--skip-db-update",
                "--input",
                "/input/" + self.manifest[kind]["filename"],
            ]
            self.docker(
                *args,
                "--scanners",
                "vuln",
                "--list-all-pkgs",
                "--format",
                "json",
                "--output",
                "/output/" + kind + "-scan.json",
                log=kind + "-scan.log",
                timeout=600,
            )
            self.docker(
                *args,
                "--format",
                "cyclonedx",
                "--output",
                "/output/" + kind + "-sbom.cdx.json",
                log=kind + "-sbom.log",
                timeout=300,
            )
            report = json.loads((self.evidence / (kind + "-scan.json")).read_text())
            findings = [
                v
                for target in report.get("Results", [])
                for v in target.get("Vulnerabilities", [])
            ]
            json_write(
                self.evidence / (kind + "-dispositions.json"),
                [
                    {
                        "finding": v,
                        "accepted_prior_linux_exception": allowed_finding(
                            v, kind == "server"
                        ),
                    }
                    for v in findings
                ],
            )
            if any(not allowed_finding(v, kind == "server") for v in findings):
                raise ValueError("New finding requires human review")

    def identity_check(self) -> None:
        script = (
            'test "$GOSU_VERSION" = 1.20; gosu --version; postgres --version; '
            f'echo "{GOSU_HASH}  /usr/local/bin/gosu" | sha256sum -c -; '
            f'echo "{PG_HASH}  /usr/local/bin/postgres" | sha256sum -c -; '
            'test "$(gosu postgres id -u)" != 0; gosu postgres id; '
            'test "$(gosu nobody id -u)" = "$(id -u nobody)"'
        )
        self.docker(
            "run",
            "--pull",
            "never",
            "--rm",
            "--network",
            "none",
            "--memory",
            "256m",
            "--cpus",
            "1",
            "--label",
            f"{LABEL}={self.run_id}",
            "--label",
            f"{OWNER}={OWNER_VALUE}",
            "--entrypoint",
            "sh",
            self.manifest["server"]["id"],
            "-ec",
            script,
            log="server-binary-identity.log",
        )

    def job(self, service: str, action: str) -> None:
        name = self.project + "-" + action
        self.compose(
            "run",
            "--no-deps",
            "--name",
            name,
            service,
            action,
            log=action + ".log",
            timeout=1200,
        )
        self.record_state(action, "IN_PROGRESS")

    def postgres_id(self) -> str:
        return self.compose("ps", "-q", "postgres").stdout.strip()

    def assert_postgres(self) -> None:
        obj = json.loads(self.docker("inspect", self.postgres_id()).stdout)[0]
        owned_resource(obj, self.run_id, self.project, "container")
        if obj["Image"] != SERVER_ID or obj["HostConfig"].get("PortBindings"):
            raise ValueError("Server image/port mismatch")
        if obj["State"].get("OOMKilled"):
            raise ValueError("Server OOM")
        if obj["State"].get("Health", {}).get("Status") != "healthy":
            raise ValueError("Server not healthy")

    def audit_network(self) -> None:
        records = []
        for item in self.owned():
            if item["kind"] == "container":
                obj = json.loads(self.docker("inspect", item["id"]).stdout)[0]
                host = obj["HostConfig"]
                if (
                    host.get("PortBindings")
                    or host.get("Privileged")
                    or host.get("NetworkMode") == "host"
                ):
                    raise ValueError("Forbidden container exposure")
                for mount in obj.get("Mounts", []):
                    if mount.get("Destination") == "/var/run/docker.sock":
                        raise ValueError("Docker socket mount forbidden")
                records.append(
                    {
                        "id": item["id"],
                        "ports": host.get("PortBindings"),
                        "network_mode": host.get("NetworkMode"),
                        "oom_killed": obj["State"].get("OOMKilled", False),
                    }
                )
                if obj["State"].get("OOMKilled"):
                    raise ValueError("Test resource was OOM-killed")
            elif item["kind"] == "network":
                obj = json.loads(self.docker("network", "inspect", item["id"]).stdout)[
                    0
                ]
                if not obj.get("Internal"):
                    raise ValueError("Non-internal trial network")
        json_write(self.evidence / "network-audit.json", records)

    def tls_setup(self) -> None:
        self.command(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-nodes",
                "-days",
                "1",
                "-subj",
                "/CN=localhost",
                "-addext",
                "subjectAltName=DNS:localhost,IP:127.0.0.1",
                "-keyout",
                str(self.private / "server.key"),
                "-out",
                str(self.evidence / "test-server-public.crt"),
            ]
        )
        self.docker(
            "cp",
            str(self.private / "server.key"),
            self.postgres_id() + ":/tmp/hml-server.key",
        )
        self.docker(
            "cp",
            str(self.evidence / "test-server-public.crt"),
            self.postgres_id() + ":/tmp/hml-server.crt",
        )
        self.docker(
            "exec",
            "-u",
            "root",
            self.postgres_id(),
            "sh",
            "-ec",
            'cp /tmp/hml-server.key "$PGDATA/server.key"; '
            'cp /tmp/hml-server.crt "$PGDATA/server.crt"; '
            'chown postgres:postgres "$PGDATA/server.key" "$PGDATA/server.crt"; '
            'chmod 0600 "$PGDATA/server.key"; '
            'printf "\\nssl=on\\nssl_cert_file=\x27server.crt\x27\\n'
            'ssl_key_file=\x27server.key\x27\\n" >> "$PGDATA/postgresql.conf"',
        )
        self.compose("restart", "postgres")
        self.wait_ready()

    def wait_ready(self) -> None:
        end = time.monotonic() + 90
        while time.monotonic() < end:
            try:
                self.assert_postgres()
                return
            except ValueError:
                time.sleep(1)
        raise TimeoutError("PostgreSQL readiness timeout")

    def compare_native(self) -> None:
        a = json.loads(
            (self.evidence / "test-inventory/client-native.json").read_text()
        )
        b = json.loads(
            (self.evidence / "runtime-inventory/client-native.json").read_text()
        )
        left = {Path(x["file"]).name: x["sha256"] for x in a["loaded_libraries"]}
        right = {Path(x["file"]).name: x["sha256"] for x in b["loaded_libraries"]}
        common = left.keys() & right.keys()
        extensions = [n for n in right if n.startswith(("_psycopg.", "pq.cpython"))]
        if len(extensions) != 2 or any(n not in common for n in extensions):
            raise ValueError("Missing native Psycopg extension identity")
        if any(left[n] != right[n] for n in common):
            raise ValueError("Test/runtime native libraries differ")
        json_write(
            self.evidence / "native-match.json",
            {"matched": len(common), "extensions": extensions, "differences": []},
        )

    def stop_owned(self) -> None:
        self.deadline = max(self.deadline, time.monotonic() + 120)
        # Stop, never delete, only labelled resources. No compose down/prune.
        for item in self.owned():
            if item["kind"] == "container":
                self.docker("stop", "--time", "15", item["id"], check=False, timeout=30)

    def collect(self) -> None:
        state = json.loads((self.root / "state.json").read_text())
        if state["run_id"] != self.run_id or state["project"] != self.project:
            raise ValueError("State/run mismatch")
        secret = self.private / "postgres-password"
        if secret.exists():
            self.password = secret.read_text().strip()
        for item in self.owned():
            if item["kind"] == "container":
                self.docker(
                    "logs",
                    item["id"],
                    log="container-" + item["id"][:12] + ".log",
                    check=False,
                )
                self.docker(
                    "inspect",
                    "--format",
                    "{{json .State}}",
                    item["id"],
                    log="state-" + item["id"][:12] + ".json",
                )
        # Sanitize generated text; never copy private/ or full inspect.
        for path in self.evidence.rglob("*"):
            if path.is_symlink():
                raise ValueError("Evidence symlink forbidden")
            if path.is_file():
                data = path.read_text(encoding="utf-8")
                clean = redact(data, self.password)
                if clean != data:
                    path.write_text(clean, encoding="utf-8")
        after = self.inventory()
        json_write(self.evidence / "inventory-after.json", after)
        before_file = self.evidence / "inventory-before.json"
        if before_file.exists():
            before = json.loads(before_file.read_text())["before"]
            missing = {
                kind: sorted(set(values) - set(after[kind]))
                for kind, values in before.items()
            }
            json_write(
                self.evidence / "preexisting-preservation.json",
                {"missing_resources": missing, "preserved": not any(missing.values())},
            )
            if any(missing.values()):
                raise ValueError(
                    "Preexisting resource disappeared; investigation required"
                )
        files = [
            p
            for p in sorted(self.evidence.rglob("*"))
            if p.is_file() and p.name != "SHA256SUMS"
        ]
        (self.evidence / "SHA256SUMS").write_text(
            "".join(
                f"{digest(p)}  {p.relative_to(self.evidence).as_posix()}\n"
                for p in files
            )
        )

    def sudo_keepalive(self, stop: Event) -> None:
        # Refresh only during this authorized foreground run, never a scheduled job.
        while not stop.wait(30):
            refreshed = subprocess.run(
                ["sudo", "-n", "-v"],
                env=self.env,
                capture_output=True,
                timeout=10,
                check=False,
            )
            if refreshed.returncode:
                return

    def run(self, expected: str, allow_downloads: bool) -> None:
        verify_package(self.package, expected)
        if not allow_downloads:
            raise ValueError("Database refresh/downloads must be reviewed before run")
        before = self.preflight()
        os.umask(0o077)
        self.root.mkdir(parents=True, exist_ok=False)
        self.private.mkdir()
        self.evidence.mkdir()
        self.password = secrets.token_hex(32)
        (self.private / "postgres-password").write_text(self.password)
        json_write(self.evidence / "inventory-before.json", before)
        self.record_state("E00", "IN_PROGRESS")
        refresh_stop = Event()
        refresh_thread = Thread(
            target=self.sudo_keepalive, args=(refresh_stop,), daemon=True
        )
        refresh_thread.start()
        previous_signals = {}

        def interrupt(signum: int, frame: Any) -> None:
            raise KeyboardInterrupt("Signal " + str(signum))

        for signum in [signal.SIGTERM, getattr(signal, "SIGHUP", signal.SIGTERM)]:
            previous_signals[signum] = signal.signal(signum, interrupt)
        try:
            self.load_images()
            self.identity_check()
            self.scan(allow_downloads)
            self.record_state("E01", "PASS")
            self.compose(
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
            self.assert_postgres()
            self.audit_network()
            self.job("runtime", "auth")
            self.tls_setup()
            self.job("runtime", "tls")
            for action in ["inventory", "base", "concurrency", "monitor"]:
                self.job("tests", action)
            self.job("runtime", "runtime-inventory")
            self.compare_native()
            results = {
                kind: junit(self.evidence / (kind + ".xml"), kind == "concurrency")
                for kind in ["base", "concurrency", "monitor"]
            }
            self.job("runtime", "persist-write")
            self.compose("restart", "postgres")
            self.wait_ready()
            self.job("runtime", "persist-read")
            self.audit_network()
            self.command(["ss", "-lntp"], log="host-listeners.txt")
            json_write(
                self.evidence / "functional-results.json",
                {
                    "tests": results,
                    "persistent_adoption": False,
                    "external_network_check": "PENDING_OPERATOR",
                    "external_supervisor_and_alerts": "NOT_CONFIGURED",
                    "backup_automation": "DEFERRED_BY_USER",
                    "status": "LOCAL_CHECKS_PASSED_WITH_OPERATIONAL_PENDING",
                },
            )
            self.stop_owned()
            self.record_state("E07", "STOPPED_FOR_REVIEW")
        except BaseException as error:
            json_write(
                self.evidence / "interruption.json",
                {
                    "type": type(error).__name__,
                    "reason": redact(str(error), self.password),
                    "persistent_adoption": False,
                },
            )
            self.stop_owned()
            self.record_state("INTERRUPTED", "FAILED_OR_INTERRUPTED")
            raise
        finally:
            try:
                self.collect()
            finally:
                refresh_stop.set()
                refresh_thread.join(timeout=12)
                for signum, handler in previous_signals.items():
                    signal.signal(signum, handler)

    def cleanup(self, authorization: str, plan_hash: str | None) -> None:
        if authorization != OWNER_VALUE + ":" + self.run_id + ":cleanup":
            raise ValueError("Explicit cleanup token required")
        state_path = self.root / "state.json"
        state = json.loads(state_path.read_text())
        if (
            state["run_id"] != self.run_id
            or state["project"] != self.project
            or state["package_sha256"] != digest(self.package / "PACKAGE-SHA256SUMS")
        ):
            raise ValueError("State/package mismatch")
        if state["status"] not in {"STOPPED_FOR_REVIEW", "FAILED_OR_INTERRUPTED"}:
            raise ValueError("Run must be stopped before cleanup")
        current = self.owned()
        if current != state["resources"]:
            raise ValueError("Resource list differs from recorded state")
        plan: dict[str, Any] = {
            "run_id": self.run_id,
            "resources": current,
            "private_files": ["postgres-password", "server.key"],
            "images": "RETAINED",
            "evidence": "RETAINED",
        }
        encoded = (json.dumps(plan, sort_keys=True, indent=2) + "\n").encode()
        checksum = hashlib.sha256(encoded).hexdigest()
        if plan_hash is None:
            (self.evidence / "DELETE-PLAN.json").write_bytes(encoded)
            self.collect()
            print(
                json.dumps(
                    {
                        "deletion_plan": plan,
                        "plan_sha256": checksum,
                        "action": "PREVIEW_ONLY",
                    }
                )
            )
            return
        if plan_hash != checksum:
            raise ValueError("Deletion plan checksum mismatch")
        if not (self.evidence / "SHA256SUMS").exists():
            raise ValueError("Collect evidence before deletion")
        self.collect()
        # Order matters: stop/remove exact containers, then labelled network/volume.
        for kind in ["container", "network", "volume"]:
            for item in current:
                if item["kind"] != kind:
                    continue
                args = (
                    ["inspect", item["id"]]
                    if kind == "container"
                    else [kind, "inspect", item["id"]]
                )
                obj = json.loads(self.docker(*args).stdout)[0]
                if owned_resource(obj, self.run_id, self.project, kind) != item:
                    raise ValueError("Resource changed during deletion")
                if kind == "container":
                    self.docker("stop", "--time", "15", item["id"], timeout=30)
                    self.docker("rm", item["id"])
                else:
                    self.docker(kind, "rm", item["id"])
        for name in plan["private_files"]:
            path = self.private / name
            if path.is_symlink():
                raise ValueError("Private file symlink forbidden")
            path.unlink(missing_ok=True)
        self.password = ""
        self.record_state("E07", "CLEANED")
        self.collect()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["preflight", "run", "collect", "cleanup"])
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--package-sha256")
    parser.add_argument("--authorize")
    parser.add_argument("--allow-downloads", action="store_true")
    parser.add_argument("--delete-plan-sha256")
    args = parser.parse_args()
    runner = Runner(args.package, args.run_id)
    if args.action == "preflight":
        print(json.dumps(runner.preflight(), indent=2))
    elif args.action == "run":
        if args.authorize != OWNER_VALUE + ":" + args.run_id or not args.package_sha256:
            parser.error(
                "Exact reviewed package checksum and explicit execution token required"
            )
        runner.run(args.package_sha256, args.allow_downloads)
    elif args.action == "collect":
        runner.collect()
    else:
        runner.cleanup(args.authorize or "", args.delete_plan_sha256)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("STOP: " + type(error).__name__ + " — " + str(error), file=sys.stderr)
        sys.exit(1)
