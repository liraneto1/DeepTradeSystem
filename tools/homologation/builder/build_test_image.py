"""GitHub-hosted builder only; explicit manual approval, no VPS/registry deployment."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare import digest, image_id, json_write  # noqa: E402
from runner import verify_package  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from freeze import freeze_package  # noqa: E402

HERE = Path(__file__).resolve().parent


def guard_environment(env: dict[str, str]) -> None:
    expected = {
        "GITHUB_ACTIONS": "true",
        "RUNNER_ENVIRONMENT": "github-hosted",
        "RUNNER_OS": "Linux",
        "RUNNER_ARCH": "X64",
        "HML_BUILD_AUTHORIZATION": "TS-PLAN-HML-002:build-test-image",
        "LIVE_ENABLED": "false",
        "TRADE_SYSTEM_ENVIRONMENT": "PAPER",
    }
    if any(env.get(key) != value for key, value in expected.items()):
        raise ValueError("Explicit GitHub-hosted build environment required")
    sha = env.get("HML_REVIEWED_COMMIT", "")
    if not re.fullmatch(r"[0-9a-f]{40}", sha) or env.get("GITHUB_SHA") != sha:
        raise ValueError("Reviewed commit must equal the dispatched commit")
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "amd64"}:
        raise ValueError("Linux/amd64 builder required")
    if platform.node() == "srv2174312":
        raise ValueError("Never execute the builder on the VPS")


def check_context_source(package: Path, manifest: dict[str, Any]) -> None:
    expected = json.loads((package / "harness/source-manifest.json").read_text())
    actual = {
        p.relative_to(package / "source").as_posix(): digest(p)
        for p in (package / "source").rglob("*")
        if p.is_file()
    }
    if actual != expected:
        raise ValueError("Build context differs from reviewed source manifest")
    forbidden = [
        p
        for p in (package / "source").rglob("*")
        if p.name == ".git" or p.name == ".env" or p.name.endswith((".key", ".pem"))
    ]
    if forbidden:
        raise ValueError("Unexpected credentials/private files in context")
    dockerfile = (
        package / "source/deploy/docker/client-runtime.Dockerfile"
    ).read_text()
    if "ARG BASE=" + manifest["base"] not in dockerfile:
        raise ValueError("Unexpected Python base")
    if "ARG UVBASE=" + manifest["uvbase"] not in dockerfile:
        raise ValueError("Unexpected uv base")


def probe_script() -> str:
    return r"""
import hashlib, importlib.metadata as m, json, os, pathlib, subprocess
assert os.environ["LIVE_ENABLED"] == "false"
assert os.environ["TRADE_SYSTEM_ENVIRONMENT"] == "PAPER"
root=pathlib.Path("/workspace")
expected=json.loads(pathlib.Path("/review/source-manifest.json").read_text())
for name,checksum in expected.items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==checksum,name
import pytest, psycopg
from psycopg import pq
assert psycopg.__version__=="3.3.8" and pq.__impl__=="c"
assert pq.version()==pq.__build_version__==180007
assert not any(d.metadata["Name"].lower().replace("_","-")=="psycopg-binary"
               for d in m.distributions())
versions={}
for cmd in [["pytest","--version"],["ruff","--version"],["mypy","--version"]]:
    versions[cmd[0]]=subprocess.check_output(cmd,text=True).strip()
print(json.dumps({"source_verification":"PASS","probe_result":"PASS",
                  "psycopg":psycopg.__version__,"implementation":pq.__impl__,
                  "libpq":pq.version(),"tools":versions},sort_keys=True))
"""


def parse_buildkit_inspect(text: str, context: str, endpoint: str) -> dict[str, Any]:
    """Buildx 0.39 inspect has text output; do not assume a --format flag."""
    drivers = re.findall(r"^Driver:\s+(\S+)\s*$", text, re.MULTILINE)
    endpoints = re.findall(r"^\s*Endpoint:\s+(\S+)\s*$", text, re.MULTILINE)
    statuses = re.findall(r"^\s*Status:\s+(\S+)\s*$", text, re.MULTILINE)
    versions = re.findall(r"^\s*BuildKit version:\s+(\S+)", text, re.MULTILINE)
    if (
        drivers != ["docker"]
        or len(endpoints) != 1
        or endpoints[0] not in {context, endpoint}
        or statuses != ["running"]
    ):
        raise ValueError("Builder must use the pinned local engine context")
    return {
        "driver": drivers[0],
        "endpoint": endpoints[0],
        "status": statuses[0],
        "buildkit_versions": versions,
    }


class Builder:
    def __init__(self, policy: dict[str, Any], output: Path) -> None:
        self.policy = policy
        self.output = output
        self.context = str(policy["context"])
        self.deadline = time.monotonic() + 2400

    def command(self, args: list[str], logfile: str, timeout: int = 120) -> str:
        remaining = int(self.deadline - time.monotonic())
        if remaining <= 0:
            raise TimeoutError("Builder deadline exceeded")
        env = dict(os.environ)
        for name in [
            "DOCKER_HOST",
            "DOCKER_CONTEXT",
            "BUILDX_BUILDER",
            "BUILDKIT_HOST",
            "DOCKER_TLS",
            "DOCKER_TLS_VERIFY",
        ]:
            env.pop(name, None)
        result = subprocess.run(
            args,
            env=env,
            check=False,
            text=True,
            capture_output=True,
            timeout=min(timeout, remaining),
        )
        (self.output / logfile).write_text(
            result.stdout + result.stderr,
            encoding="utf-8",
        )
        if result.returncode:
            raise RuntimeError("Builder command failed; inspect artifact locally")
        return result.stdout

    def docker(self, args: list[str], logfile: str, timeout: int = 120) -> str:
        return self.command(
            ["docker", "--context", self.context, *args], logfile, timeout
        )

    def run(self, package: Path) -> dict[str, Any]:
        guard_environment(dict(os.environ))
        policy = self.policy
        verify_package(package, policy["approved_package_sha256"])
        check_context_source(package, policy)
        checked = self.command(["git", "rev-parse", "HEAD"], "checkout-sha.txt").strip()
        if checked != os.environ["HML_REVIEWED_COMMIT"]:
            raise ValueError("Checkout is not the reviewed builder commit")
        info = json.loads(
            self.docker(["info", "--format", "{{json .}}"], "docker-info.json")
        )
        if (
            info["ServerVersion"] != policy["docker_version"]
            or info["OSType"] != "linux"
        ):
            raise ValueError("Pinned Docker version/platform required")
        if info["Driver"] != "overlayfs" or [
            "driver-type",
            "io.containerd.snapshotter.v1",
        ] not in info.get("DriverStatus", []):
            raise ValueError("OCI-preserving containerd image store required")
        endpoint = self.docker(
            [
                "context",
                "inspect",
                self.context,
                "--format",
                "{{.Endpoints.docker.Host}}",
            ],
            "docker-endpoint.txt",
        ).strip()
        if not endpoint.startswith("unix://"):
            raise ValueError("Local builder socket required")
        version = self.docker(["buildx", "version"], "buildx-version.txt")
        if not re.search(
            r"\bv" + re.escape(policy["buildx_required_version"]) + r"(?:\s|$)", version
        ):
            raise ValueError(
                "Reviewed Buildx version required; no automatic replacement"
            )
        help_text = self.docker(["buildx", "build", "--help"], "buildx-help.txt")
        if "--resource" not in help_text:
            raise ValueError("Per-step build resource support required")
        buildkit_text = self.docker(
            ["buildx", "inspect", self.context], "buildkit-before.txt"
        )
        buildkit = parse_buildkit_inspect(buildkit_text, self.context, endpoint)
        json_write(self.output / "buildkit-before.json", buildkit)
        import shutil

        if shutil.disk_usage(self.output).free < policy["minimum_free_disk_bytes"]:
            raise ValueError(
                "Insufficient builder disk; do not prune unrelated resources"
            )
        match = re.search(r"MemAvailable:\s+(\d+)", Path("/proc/meminfo").read_text())
        if (
            not match
            or int(match.group(1)) * 1024 < policy["minimum_available_ram_bytes"]
        ):
            raise ValueError("Insufficient builder memory")
        run_id = os.environ["GITHUB_RUN_ID"] + "-" + os.environ["GITHUB_RUN_ATTEMPT"]
        tag = "local/dts-hml-tests:build-" + run_id
        args = [
            "buildx",
            "build",
            "--builder",
            self.context,
            "--platform",
            "linux/amd64",
            "--target",
            "test",
            "--pull",
            "--no-cache",
            "--provenance=false",
            "--sbom=false",
            "--load",
            "--progress",
            "plain",
            "--label",
            "org.opencontainers.image.revision=" + policy["candidate"],
            "--label",
            "io.deeptrade.hml.source-package=" + policy["approved_package_sha256"],
            "--label",
            "io.deeptrade.hml.audit-extension=0c18178dcbc4d4e8468c4344ec0f1682826534afc902d59587d02434ac46412c",
            "--metadata-file",
            str(self.output / "build-metadata.json"),
            "--file",
            str(package / "source/deploy/docker/client-runtime.Dockerfile"),
            "--tag",
            tag,
        ]
        for resource in policy["per_build_step_limits"]:
            args += ["--resource", resource]
        args += [str(package / "source")]
        self.docker(args, "build.log", policy["timeouts"]["build_seconds"])
        image = json.loads(
            self.docker(["image", "inspect", tag], "test-image-inspect.json")
        )[0]
        if (image["Os"], image["Architecture"]) != ("linux", "amd64"):
            raise ValueError("Unexpected output platform")
        name = "dts-hml-builder-probe-" + run_id
        try:
            raw = self.docker(
                [
                    "run",
                    "--pull",
                    "never",
                    "--name",
                    name,
                    "--rm",
                    "--network",
                    "none",
                    "--user",
                    f"{getattr(os, 'getuid')()}:{getattr(os, 'getgid')()}",
                    "--memory",
                    "3g",
                    "--cpus",
                    "2",
                    "--cap-drop",
                    "ALL",
                    "--security-opt",
                    "no-new-privileges:true",
                    "--mount",
                    f"type=bind,source={package / 'harness'},target=/review,readonly",
                    "-e",
                    "HOME=/tmp",
                    "-e",
                    "LIVE_ENABLED=false",
                    "-e",
                    "TRADE_SYSTEM_ENVIRONMENT=PAPER",
                    "--entrypoint",
                    "python",
                    image["Id"],
                    "-c",
                    probe_script(),
                ],
                "probe.json",
                policy["timeouts"]["probe_seconds"],
            )
        except BaseException:
            # The name is unique within this disposable builder, never on the VPS.
            try:
                self.docker(["stop", "--time", "10", name], "probe-stop.log", 30)
            except Exception:
                pass  # The --rm probe may already be gone; preserve original failure.
            raise
        probe = json.loads(raw)
        test_tar = self.output / "test-image.tar"
        self.docker(["save", image["Id"], "-o", str(test_tar)], "docker-save.log", 180)
        with tarfile.open(test_tar) as archive:
            if "index.json" not in archive.getnames():
                raise ValueError("OCI index missing; do not freeze legacy-only export")
        tar_identity = image_id(test_tar)
        if tar_identity != image["Id"]:
            raise ValueError("Engine/export identity differs; review before freezing")
        receipt = {
            "schema": 1,
            "plan": policy["plan"],
            "candidate": policy["candidate"],
            "builder_commit": checked,
            "runner": policy["runner"],
            "run_id": os.environ["GITHUB_RUN_ID"],
            "run_attempt": os.environ["GITHUB_RUN_ATTEMPT"],
            "runner_image_os": os.environ.get("ImageOS"),
            "runner_image_version": os.environ.get("ImageVersion"),
            "repository": os.environ["GITHUB_REPOSITORY"],
            "approved_package_sha256": policy["approved_package_sha256"],
            "image_id": tar_identity,
            "tar_sha256": digest(test_tar),
            "tar_bytes": test_tar.stat().st_size,
            "source_verification": probe["source_verification"],
            "probe_result": probe["probe_result"],
            "tools": probe["tools"],
            "policy_sha256": digest(HERE / "policy.json"),
            "builder_script_sha256": digest(Path(__file__)),
            "source_manifest_sha256": digest(package / "harness/source-manifest.json"),
            "vps_execution": False,
            "registry_push": False,
            "signed_provenance": False,
            "full_sbom": "PENDING_SECURITY_REVIEW",
            "backup_automation": "DEFERRED_BY_USER",
        }
        result = freeze_package(
            package,
            test_tar,
            receipt,
            self.output / "sealed-package",
            policy["approved_package_sha256"],
        )
        json_write(self.output / "FROZEN-RESULT.json", result)
        json_write(self.output / "BUILD-RECEIPT.json", receipt)
        # Keep only one TAR in the published review artifact.
        test_tar.unlink()
        json_write(
            self.output / "STATUS.json",
            {
                "build": "PASS",
                "freeze": "PASS",
                "human_review": "PENDING",
                "vps_execution": False,
                "persistent_adoption": False,
            },
        )
        files = sorted(
            (p for p in self.output.rglob("*") if p.is_file()),
            key=lambda p: p.relative_to(self.output).as_posix(),
        )
        (self.output / "SHA256SUMS").write_text(
            "".join(
                f"{digest(p)}  {p.relative_to(self.output).as_posix()}\n" for p in files
            ),
            encoding="utf-8",
        )
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    guard_environment(dict(os.environ))  # before any file creation or Docker invocation
    output = args.output.resolve()
    runner_temp = Path(os.environ["RUNNER_TEMP"]).resolve()
    if (
        output.exists()
        or output == runner_temp
        or not output.is_relative_to(runner_temp)
    ):
        raise ValueError("Fresh output directory within runner temp required")
    output.mkdir(parents=True)
    policy = json.loads((HERE / "policy.json").read_text(encoding="utf-8"))
    print(json.dumps(Builder(policy, output).run(args.package.resolve()), indent=2))


if __name__ == "__main__":
    main()
