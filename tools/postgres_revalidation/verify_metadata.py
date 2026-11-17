"""Prove that the derived image changes only the intended runtime metadata."""

import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
new_id = sys.argv[2]
parent = json.loads((out / "server/parent-image.json").read_text())[0]
rebuilt = json.loads((out / "server/image.json").read_text())[0]
parent_id = "sha256:57e55d6e7bd1f06e5d75408d4d5f5a5ef33513b7a4eaef424530363f53ea3759"
assert parent["Id"] == parent_id
assert rebuilt["Id"] == new_id and new_id != parent_id
assert rebuilt["Os"] == parent["Os"] == "linux"
assert rebuilt["Architecture"] == parent["Architecture"] == "amd64"
assert rebuilt["RootFS"]["Layers"] == parent["RootFS"]["Layers"]
expected = dict(parent["Config"])
assert expected["Env"].count("GOSU_VERSION=1.19") == 1
expected["Env"] = [
    "GOSU_VERSION=1.20" if value == "GOSU_VERSION=1.19" else value
    for value in expected["Env"]
]
assert rebuilt["Config"] == expected
assert rebuilt["Config"]["Env"].count("GOSU_VERSION=1.20") == 1
procedure = out / "pair-verification.sh"
text = procedure.read_text()
assert text.count(parent_id) == 1
procedure.write_text(text.replace(parent_id, new_id))
result = {
    "parent_image_id": parent_id,
    "rebuilt_image_id": new_id,
    "parent_environment_value": "1.19",
    "rebuilt_environment_value": "1.20",
    "rootfs_layers_identical": True,
    "image_config_only_gosu_version_changed": True,
    "rebuild_performed": True,
    "adoption_performed": False,
}
(out / "METADATA-VERIFICATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
