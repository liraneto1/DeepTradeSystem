"""Record the exact libraries and package origins used by the client."""

import hashlib
import importlib.metadata as metadata
import json
import re
import subprocess
import sys
from pathlib import Path

import psycopg
from psycopg import pq

out = Path(sys.argv[1])
out.mkdir(exist_ok=True, parents=True)
assert psycopg.__version__ == "3.3.8" and pq.__impl__ == "c"
assert pq.version() == pq.__build_version__ == 180007
packages = sorted((d.metadata["Name"], d.version) for d in metadata.distributions())
assert not any(n.lower().replace("_", "-") == "psycopg-binary" for n, _ in packages)
(out / "python-packages.json").write_text(json.dumps(packages, indent=2))
libraries = sorted(
    {
        line.split()[-1]
        for line in Path("/proc/self/maps").read_text().splitlines()
        if "/" in line and ".so" in line.split()[-1]
    }
)
records = []
for name in libraries:
    file = Path(name)
    if file.is_file():
        owner = subprocess.run(
            ["apk", "info", "--who-owns", name], capture_output=True, text=True
        )
        records.append(
            {
                "file": name,
                "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
                "apk_owner": owner.stdout.strip(),
            }
        )
result = {
    "psycopg": psycopg.__version__,
    "implementation": pq.__impl__,
    "libpq_runtime": pq.version(),
    "libpq_build": pq.__build_version__,
    "python": sys.version,
    "loaded_libraries": records,
}
(out / "client-native.json").write_text(json.dumps(result, indent=2))
raw = Path("/lib/apk/db/installed").read_text()
(out / "apk-installed-db.txt").write_text(raw)
(out / "apk-repositories.txt").write_bytes(Path("/etc/apk/repositories").read_bytes())
apk_packages = []
for block in raw.split("\n\n"):
    fields = {
        line[0]: line[2:]
        for line in block.splitlines()
        if len(line) > 1 and line[1] == ":" and line[0] in "PVATopcumt"
    }
    if "P" in fields:
        apk_packages.append(fields)
(out / "apk-packages.json").write_text(json.dumps(apk_packages, indent=2))
if out.name == "runtime-inventory":
    assert not any(n.lower() in {"pip", "setuptools", "wheel"} for n, _ in packages)
    assert not any(
        p["P"] in {"libldap", "libsasl", "py3-pip", "py3-setuptools"}
        for p in apk_packages
    )
    libpq = next(
        Path(r["file"]) for r in records if re.match(r"libpq\.so", Path(r["file"]).name)
    )
    content = libpq.read_bytes()
    assert b"GSSAPI support is not compiled in" in content
    assert b"GSSAPI authentication not supported" in content
    assert b"ldap_initialize" not in content
    assert not any(Path("/usr/local/lib/python3.12/ensurepip/_bundled").glob("*.whl"))
print(json.dumps(result, indent=2))
