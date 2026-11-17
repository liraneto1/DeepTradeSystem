"""Verify that functional tests exercise the native artifacts of the runtime."""

import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
test = json.loads((root / "test/test-inventory/client-native.json").read_text())
runtime = json.loads(
    (root / "runtime/runtime-inventory/client-native.json").read_text()
)
a = {Path(x["file"]).name: x["sha256"] for x in test["loaded_libraries"]}
b = {Path(x["file"]).name: x["sha256"] for x in runtime["loaded_libraries"]}
extensions = [name for name in b if name.startswith(("_psycopg.", "pq.cpython"))]
assert len(extensions) == 2 and all(name in a for name in extensions)
different = [name for name in a.keys() & b.keys() if a[name] != b[name]]
assert not different, different
(root / "native-match.json").write_text(
    json.dumps(
        {
            "matched_common_files": len(a.keys() & b.keys()),
            "c_extensions": extensions,
            "differences": different,
        },
        indent=2,
    )
)
# Exclude the outputs of the build itself from the source identity.
files = [
    Path(".dockerignore"),
    Path(".gitignore"),
    Path("pyproject.toml"),
    Path("uv.lock"),
    *Path("deploy/docker").glob("client*"),
    *Path("tools/client_profile").glob("*"),
]
manifest = {
    str(p): hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    for p in sorted(files)
    if p.is_file()
}
(root / "source-inputs.json").write_text(json.dumps(manifest, indent=2))
