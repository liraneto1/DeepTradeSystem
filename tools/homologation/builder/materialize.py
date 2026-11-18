"""Reconstruct approved inputs from public commits, without source publication."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
from collections.abc import Callable

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from build_test_image import guard_environment  # noqa: E402
from prepare import CANDIDATE, digest, safe_member  # noqa: E402
from runner import verify_package  # noqa: E402

AUDIT = "9815c022bdbc336433165a4d9ebe44872f97085c"
AUDIT_FILE = "tests/integration/test_postgres_migrations.py"


def approved_eol(data: bytes, expected: str) -> bytes:
    """Restore only LF/CRLF, never change substantive source content."""
    lf = data.replace(b"\r\n", b"\n")
    for candidate in [data, lf, lf.replace(b"\n", b"\r\n")]:
        if hashlib.sha256(candidate).hexdigest() == expected:
            return candidate
    raise ValueError("Public source differs from approved input")


def git_source(commit: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", commit + ":" + path],
        cwd=ROOT,
        timeout=30,
    )


def materialize(
    output: pathlib.Path, loader: Callable[[str, str], bytes] = git_source
) -> str:
    policy = json.loads((HERE / "policy.json").read_text(encoding="utf-8"))
    metadata = HERE / "approved-inputs"
    expected = str(policy["approved_package_sha256"])
    if output.exists():
        raise ValueError("Fresh output required")
    if digest(metadata / "PACKAGE-SHA256SUMS") != expected:
        raise ValueError("Approved input checksum manifest changed")
    output.mkdir(parents=True)
    sums = (metadata / "PACKAGE-SHA256SUMS").read_text(encoding="utf-8")
    for line in sums.splitlines():
        checksum, name = line.split("  ", 1)
        relative = safe_member(name)
        if name.startswith("source/"):
            source = name[len("source/") :]
            commit = AUDIT if source == AUDIT_FILE else CANDIDATE
            data = approved_eol(loader(commit, source), checksum)
        elif name == "harness/source-manifest.json":
            data = (metadata / "source-manifest.json").read_bytes()
        elif name.startswith("harness/") and "/" not in name[len("harness/") :]:
            data = (HERE.parent / name[len("harness/") :]).read_bytes()
        elif name in {"manifest.json", "compose.yml"}:
            data = (metadata / name).read_bytes()
        else:
            raise ValueError("Unrecognized approved package path")
        if hashlib.sha256(data).hexdigest() != checksum:
            raise ValueError("Approved harness/metadata byte mismatch")
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (output / "artifacts").mkdir()
    (output / "PACKAGE-SHA256SUMS").write_bytes(
        (metadata / "PACKAGE-SHA256SUMS").read_bytes()
    )
    verify_package(output, expected)
    return expected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    args = parser.parse_args()
    guard_environment(dict(os.environ))
    output = args.output.resolve()
    temp = pathlib.Path(os.environ["RUNNER_TEMP"]).resolve()
    if output == temp or not output.is_relative_to(temp):
        raise ValueError("Output must stay in runner temp")
    origin = subprocess.check_output(
        ["git", "remote", "get-url", "origin"], cwd=ROOT, text=True, timeout=30
    ).strip()
    if origin not in {
        "https://github.com/liraneto1/DeepTradeSystem",
        "https://github.com/liraneto1/DeepTradeSystem.git",
    }:
        raise ValueError("Only the already-public project origin is allowed")
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    subprocess.run(
        [
            "git",
            "-c",
            "credential.helper=",
            "fetch",
            "--no-tags",
            "origin",
            CANDIDATE,
            AUDIT,
        ],
        cwd=ROOT,
        env=env,
        check=True,
        timeout=180,
    )
    print(
        json.dumps(
            {
                "materialized_package_sha256": materialize(output),
                "source": "existing public commits",
                "vps_access": False,
            }
        )
    )


if __name__ == "__main__":
    main()
