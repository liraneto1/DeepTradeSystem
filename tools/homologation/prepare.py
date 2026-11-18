"""Create an offline, reviewable package from the exact candidate, never the worktree.

No Docker, network, SSH, image extraction into the host, or VPS access.
A draft without --test-image-tar is intentionally not executable.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any

CANDIDATE = "a26c0a86ade2ec64d14c4bb06e27c93b2aea5205"
SERVER_ID = "sha256:750c0c91aac5f4ec3b33942d74da652ef6c393f8572d21e9e46f5f0d6cdd780f"
SERVER_TAR = "05077379fc3442d11607a4634661a5ab0e55586d97a523794fd81de50cab7a5a"
RUNTIME_ID = "sha256:cf6e38c179717e442524e69b4062b34d2470eb6f873ce55641548da4f211b088"
RUNTIME_TAR = "f41d02884114d833def58d590c807dd011b683862597e2b687325f3e3a4293b5"
AUDIT_SHA = "0c18178dcbc4d4e8468c4344ec0f1682826534afc902d59587d02434ac46412c"
AUDIT_BASE_SHA = "6f1020ff12a807be4d7f942b80de8bbc4d2f78c4f677b093467d5061bdb070a4"
SCANNER = (
    "aquasec/trivy@sha256:"
    "8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb"
)
ROOT = Path(__file__).resolve().parents[2]
INPUTS = [
    "src",
    "infrastructure",
    "apps",
    "contracts",
    "tests",
    "tools/client_profile",
    "deploy/docker",
    "pyproject.toml",
    "uv.lock",
    ".python-version",
    ".dockerignore",
    ".gitignore",
    "README.md",
    "alembic.ini",
]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_write(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def safe_member(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
        raise ValueError("Unsafe archive path")
    return path


def export_source(destination: Path) -> dict[str, str]:
    raw = subprocess.check_output(
        ["git", "-C", str(ROOT), "archive", CANDIDATE, "--", *INPUTS]
    )
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        for member in archive.getmembers():
            relative = safe_member(member.name)
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError("Links/special files forbidden in source export")
            data = archive.extractfile(member)
            if data is None:
                raise ValueError("Missing archive content")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data.read())
    path = destination / "tests/integration/test_postgres_migrations.py"
    base = path.read_bytes().replace(b"\r\n", b"\n")
    audit_path = (
        ROOT
        / "docs/evidence/ts-st-001-004-a26c0a8/technical-trials"
        / "test_postgres_migrations.py"
    )
    audit = audit_path.read_bytes().replace(b"\r\n", b"\n")
    if (
        hashlib.sha256(base).hexdigest() != AUDIT_BASE_SHA
        or hashlib.sha256(audit).hexdigest() != AUDIT_SHA
        or not audit.startswith(base)
    ):
        raise ValueError("Audit extension does not match the approved base")
    path.write_bytes(audit)
    return {
        p.relative_to(destination).as_posix(): digest(p)
        for p in sorted(destination.rglob("*"))
        if p.is_file()
    }


def image_id(path: Path) -> str:
    """Verify OCI manifest/config/layers or a legacy Docker-save config identity."""
    with tarfile.open(path) as archive:

        def read(name: str) -> bytes:
            stream = archive.extractfile(safe_member(name).as_posix())
            if stream is None:
                raise ValueError("Missing image descriptor")
            return stream.read()

        def blob(descriptor: dict[str, Any]) -> bytes:
            algorithm, checksum = descriptor["digest"].split(":", 1)
            if algorithm != "sha256" or len(checksum) != 64:
                raise ValueError("SHA256 descriptor required")
            data = read("blobs/sha256/" + checksum)
            if (
                hashlib.sha256(data).hexdigest() != checksum
                or len(data) != descriptor["size"]
            ):
                raise ValueError("OCI blob digest/size mismatch")
            return data

        manifests = json.loads(read("manifest.json"))
        if len(manifests) != 1:
            raise ValueError("Exactly one image required")
        data = read(manifests[0]["Config"])
        obj = json.loads(data)
        if (obj.get("os"), obj.get("architecture")) != ("linux", "amd64"):
            raise ValueError("Linux/amd64 image required")
        config_id = "sha256:" + hashlib.sha256(data).hexdigest()
        if "index.json" not in archive.getnames():
            return config_id
        index = json.loads(read("index.json"))
        if len(index["manifests"]) != 1:
            raise ValueError("Single-platform OCI manifest required")
        descriptor = index["manifests"][0]
        leaves: list[tuple[dict[str, Any], dict[str, Any]]] = []
        seen: set[str] = set()

        def walk(item: dict[str, Any], depth: int = 0) -> None:
            if depth > 8 or item["digest"] in seen:
                raise ValueError("OCI cycle, duplicate manifest or excessive nesting")
            seen.add(item["digest"])
            document = json.loads(blob(item))
            if "manifests" in document:
                for child in document["manifests"]:
                    walk(child, depth + 1)
            else:
                blob(document["config"])
                for layer in document["layers"]:
                    blob(layer)
                leaves.append((item, document))

        walk(descriptor)
        candidates = [
            (item, doc) for item, doc in leaves if doc["config"]["digest"] == config_id
        ]
        if len(candidates) != 1:
            raise ValueError("Exactly one matching platform image required")
        selected, manifest = candidates[0]
        if manifests[0]["Layers"] != [
            "blobs/sha256/" + layer["digest"].split(":", 1)[1]
            for layer in manifest["layers"]
        ]:
            raise ValueError("Docker-save and OCI layers differ")
        for item, _ in leaves:
            if item["digest"] == selected["digest"]:
                continue
            annotations = item.get("annotations", {})
            if (
                annotations.get("vnd.docker.reference.type") != "attestation-manifest"
                or annotations.get("vnd.docker.reference.digest") != selected["digest"]
                or item.get("platform") != {"architecture": "unknown", "os": "unknown"}
            ):
                raise ValueError("Unexpected second platform or unrelated attestation")
        return str(descriptor["digest"])


def prepare(output: Path, test_tar: Path | None = None) -> None:
    if output.exists():
        raise ValueError("Output must not exist; no overwrite")
    output.mkdir(parents=True)
    hashes = export_source(output / "source")
    (output / "harness").mkdir()
    for name in [
        "runner.py",
        "inside.py",
        "prepare.py",
        "preflight.sh",
        "run-functional.sh",
        "collect-evidence.sh",
        "cleanup.sh",
    ]:
        (output / "harness" / name).write_bytes(
            (ROOT / "tools/homologation" / name).read_bytes()
        )
    (output / "compose.yml").write_bytes(
        (ROOT / "deploy/compose/homologation-functional.yml").read_bytes()
    )
    json_write(output / "harness/source-manifest.json", hashes)
    test = None
    if test_tar:
        test = {
            "id": image_id(test_tar),
            "tar_sha256": digest(test_tar),
            "bytes": test_tar.stat().st_size,
            "filename": "test-image.tar",
        }
    manifest = {
        "schema": 1,
        "plan": "TS-PLAN-HML-002",
        "candidate": CANDIDATE,
        "audit_base_sha256": AUDIT_BASE_SHA,
        "audit_extension_sha256": AUDIT_SHA,
        "ready_for_execution_review": test is not None,
        "server": {"id": SERVER_ID, "tar_sha256": SERVER_TAR, "filename": "server.tar"},
        "runtime": {
            "id": RUNTIME_ID,
            "tar_sha256": RUNTIME_TAR,
            "filename": "runtime.tar",
        },
        "test": test,
        "scanner": SCANNER,
        "downloads": [
            "Only pinned Trivy image if absent, when --allow-downloads is authorized",
            "Trivy vulnerability database refresh over HTTPS",
            "Test image must be built separately from source/; never built by runner",
        ],
        "backup_automation": "DEFERRED_BY_USER",
        "pending": [
            "Separate execution authorization",
            "Review package SHA256",
            "External network verification",
            "Persistent adoption not authorized",
        ],
    }
    json_write(output / "manifest.json", manifest)
    (output / "artifacts").mkdir()
    files = [p for p in sorted(output.rglob("*")) if p.is_file()]
    (output / "PACKAGE-SHA256SUMS").write_text(
        "".join(f"{digest(p)}  {p.relative_to(output).as_posix()}\n" for p in files),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "package": str(output),
                "files": len(files),
                "ready_for_execution_review": test is not None,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--test-image-tar", type=Path)
    args = parser.parse_args()
    prepare(args.output.resolve(), args.test_image_tar)
