"""Install the approved, exact APK set for the Linux/amd64 client profile."""

import argparse
import json
import platform
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("profile", choices=("test", "runtime"))
parser.add_argument("--archive", action="store_true")
args = parser.parse_args()
if platform.machine() != "x86_64":
    raise SystemExit("This profile is qualified only for Linux/amd64.")
lock = json.loads(Path("deploy/docker/client-apk-lock.json").read_text())
pins = lock[args.profile]
subprocess.run(
    [
        "apk",
        "--no-cache",
        "add",
        "--upgrade",
        *[f"{p['name']}={p['version']}" for p in pins],
    ],
    check=True,
)
actual = {}
for block in Path("/lib/apk/db/installed").read_text().split("\n\n"):
    fields = dict(line.split(":", 1) for line in block.splitlines() if ":" in line)
    if "P" in fields and not fields["P"].startswith("."):
        actual[fields["P"]] = fields["V"]
expected = {p["name"]: p["version"] for p in pins}
if actual != expected:
    raise SystemExit(f"APK inventory differs from approved profile: {actual!r}")
out = Path("/audit")
out.mkdir(exist_ok=True)
(out / f"apk-{args.profile}-resolved.json").write_text(json.dumps(actual, indent=2))
if args.archive:
    archive = out / "apks"
    archive.mkdir(exist_ok=True)
    subprocess.run(
        [
            "apk",
            "fetch",
            "--recursive",
            "--output",
            str(archive),
            *[f"{p['name']}={p['version']}" for p in pins],
        ],
        check=True,
    )
