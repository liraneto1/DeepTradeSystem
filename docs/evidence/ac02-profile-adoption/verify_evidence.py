"""Verify the remote evidence archive and compare it with the pending BUSINESS files."""
import hashlib
import json
import tarfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent
archive = root / "linux-profile.zip"
output = root / "artifacts"
output.mkdir(exist_ok=True)
errors = []
with zipfile.ZipFile(archive) as z:
    names = set(z.namelist())
    manifest = z.read("SHA256SUMS").decode()
    count = 0
    for line in manifest.splitlines():
        expected, remote = line.split("  ", 1)
        name = remote.split("/client-profile/", 1)[1]
        digest = hashlib.sha256()
        with z.open(name) as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        if digest.hexdigest() != expected:
            errors.append(name)
        count += 1
    assert not errors, errors
    # Keep the complete raw ZIP; materialize reports, the built wheel and runtime image.
    for name in names:
        selected = (
            name.endswith((".json", ".log", ".xml", ".tsv", ".txt"))
            or name in {"SHA256SUMS", "client-runtime.tar"}
            or ("/wheels/" in name and name.endswith(".whl"))
        )
        if selected and not name.endswith("/") and "/source/" not in name:
            target = (output / name).resolve()
            assert target.is_relative_to(output.resolve())
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(name) as source, target.open("wb") as dest:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    dest.write(chunk)
    scan = json.loads(z.read("runtime-trivy.json"))
    findings = [
        v for item in scan.get("Results", [])
        for v in item.get("Vulnerabilities", []) or []
    ]
    assert not findings, findings
    tests = ET.fromstring(z.read("results/pytest.xml"))
    suites = list(tests.iter("testsuite"))
    linux = {
        key: sum(int(s.get(key, "0")) for s in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }
    assert linux == {"tests": 164, "failures": 0, "errors": 0, "skipped": 0}
    native_match = json.loads(z.read("native-match.json"))
    assert not native_match["differences"]
    source_inputs = json.loads(z.read("source-inputs.json"))
    source_errors = []
    project = root.parents[2]
    for path, expected in source_inputs.items():
        actual = hashlib.sha256(
            (project / path).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        if actual != expected:
            source_errors.append(path)
    assert not source_errors, source_errors
    tls = json.loads(z.read("results/tls.json"))
    assert [r["result"] for r in tls] == ["PASS", "PASS_REJECTED", "PASS_REJECTED"]
    runtime = json.loads(z.read("runtime-image.json"))[0]["Id"]
    assert runtime == z.read("runtime-tested-image-id.txt").decode().strip()
    test_id = json.loads(z.read("test-image.json"))[0]["Id"]
    assert test_id == z.read("tested-image-id.txt").decode().strip()
    assert z.read("input-hashes.txt") == z.read("final-input-hashes.txt")
    inventory = json.loads(z.read("runtime/runtime-inventory/client-native.json"))
    assert inventory["implementation"] == "c"
    packages = json.loads(z.read("runtime/runtime-inventory/apk-packages.json"))
    assert not any(p["P"] in {"libldap", "libsasl", "py3-pip"} for p in packages)
    assert not any(
        n.lower() in {"pip", "setuptools", "wheel", "psycopg-binary"}
        for n, _ in json.loads(z.read("runtime/runtime-inventory/python-packages.json"))
    )
image = output / "client-runtime.tar"
with tarfile.open(image) as t:
    info = json.load(t.extractfile("manifest.json"))[0]
    config = t.extractfile(info["Config"]).read()
    config_id = "sha256:" + hashlib.sha256(config).hexdigest()
    assert info["Config"].endswith(config_id.split(":")[1])
    index = json.load(t.extractfile("index.json"))
    assert index["manifests"][0]["digest"] == runtime
    verified = set()
    def verify_descriptor(descriptor):
        digest = descriptor["digest"]
        if digest in verified:
            return
        name = "blobs/" + digest.replace(":", "/")
        stream = t.extractfile(name)
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
        assert "sha256:" + actual == digest, name
        verified.add(digest)
        if "index" in descriptor["mediaType"] or "manifest" in descriptor["mediaType"]:
            body = json.load(t.extractfile(name))
            children = body.get("manifests", [])
            if "config" in body:
                children += [body["config"], *body.get("layers", [])]
            for child in children:
                verify_descriptor(child)
    verify_descriptor(index["manifests"][0])
    assert config_id in verified
win_xml = ET.parse(root / "windows-pytest.xml")
windows = {
    key: sum(int(s.get(key, "0")) for s in win_xml.getroot().iter("testsuite"))
    for key in ("tests", "failures", "errors", "skipped")
}
assert windows == linux
wheel_names = sorted(str(p.relative_to(output)) for p in output.rglob("*.whl"))
summary = {
    "manifest_files_verified": count, "manifest_errors": errors,
    "source_inputs_verified": len(source_inputs), "source_input_errors": source_errors,
    "linux_junit": linux, "windows_local_junit": windows,
    "native_match": native_match, "runtime_image_id": runtime,
    "saved_image_oci_index_matches": True,
    "saved_image_config_digest": config_id, "oci_blobs_verified": len(verified),
    "runtime_image_tar_sha256": hashlib.file_digest(image.open("rb"), "sha256").hexdigest(),
    "runtime_findings": len(findings), "libpq_runtime": inventory["libpq_runtime"],
    "libpq_build": inventory["libpq_build"], "tls": tls,
    "built_wheels": wheel_names,
}
(root / "VERIFICATION.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
