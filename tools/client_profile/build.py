"""Build the client from the locked sdist and reuse its wheel in both environments."""

import hashlib
import importlib.metadata as metadata
import json
import subprocess
import tarfile
import tomllib
import urllib.request
from pathlib import Path

audit = Path("/audit")
audit.mkdir(exist_ok=True)


def run(args, log):
    process = subprocess.run(args, capture_output=True, text=True)
    (audit / log).write_text(process.stdout + "\n" + process.stderr)
    print(log, process.returncode, flush=True)
    if process.returncode:
        print(process.stdout, process.stderr)
        raise SystemExit(process.returncode)


def snapshot(name):
    packages = sorted((d.metadata["Name"], d.version) for d in metadata.distributions())
    (audit / name).write_text(json.dumps(packages, indent=2))


snapshot("build-tools.json")
lock = tomllib.loads(Path("uv.lock").read_text())
package = next(p for p in lock["package"] if p["name"] == "psycopg-c")
assert package["version"] == "3.3.8"
sdist = package["sdist"]
payload = urllib.request.urlopen(sdist["url"], timeout=90).read()
assert "sha256:" + hashlib.sha256(payload).hexdigest() == sdist["hash"]
archive = audit / sdist["url"].rsplit("/", 1)[1]
archive.write_bytes(payload)
(audit / "psycopg-c-source.json").write_text(json.dumps(sdist, indent=2))
source_root = audit / "source"
source_root.mkdir(exist_ok=True)
with tarfile.open(archive) as tar:
    tar.extractall(source_root, filter="data")
source = next(source_root.iterdir())
run(
    [
        "uv",
        "build",
        "--wheel",
        "--no-build-isolation",
        str(source),
        "--out-dir",
        "/audit/wheels",
    ],
    "client-wheel-build.log",
)
run(
    ["uv", "sync", "--locked", "--group", "build", "--no-build-isolation"],
    "test-install.log",
)
wheel = next((audit / "wheels").glob("psycopg_c-*.whl"))
run(
    ["uv", "pip", "install", "--no-deps", "--reinstall", str(wheel)],
    "test-client-wheel.log",
)
snapshot("test-packages.json")
assert not any(
    d.metadata["Name"].lower().replace("_", "-") == "psycopg-binary"
    for d in metadata.distributions()
)
run(["uv", "pip", "check"], "test-dependency-check.log")
run(["uv", "build", "--no-sources", "--no-build-isolation"], "project-build.log")
run(
    [
        "uv",
        "export",
        "--frozen",
        "--no-dev",
        "--no-emit-project",
        "--no-hashes",
        "--no-header",
        "--output-file",
        "/audit/runtime-requirements.txt",
    ],
    "runtime-export.log",
)
requirements = (audit / "runtime-requirements.txt").read_text()
requirements = requirements.replace("psycopg-c==3.3.8", str(wheel))
(audit / "runtime-requirements-local.txt").write_text(requirements)
run(
    ["uv", "venv", "--python", "/usr/local/bin/python3.12", "/opt/runtime"],
    "runtime-venv.log",
)
run(
    [
        "uv",
        "pip",
        "sync",
        "--python",
        "/opt/runtime/bin/python",
        "--no-build",
        "/audit/runtime-requirements-local.txt",
    ],
    "runtime-install.log",
)
project_wheel = next(Path("dist").glob("*.whl"))
run(
    [
        "uv",
        "pip",
        "install",
        "--python",
        "/opt/runtime/bin/python",
        "--no-deps",
        str(project_wheel),
    ],
    "runtime-project.log",
)
run(
    ["uv", "pip", "check", "--python", "/opt/runtime/bin/python"],
    "runtime-dependency-check.log",
)
for file in ("pyproject.toml", "uv.lock"):
    (audit / file).write_bytes(Path(file).read_bytes())
