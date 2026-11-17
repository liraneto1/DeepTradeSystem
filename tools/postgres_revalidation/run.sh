#!/usr/bin/env bash
# Revalidate a preserved server in an isolated runner; do not adopt it.
set -euo pipefail
out="$RUNNER_TEMP/server-pair"
server="sha256:57e55d6e7bd1f06e5d75408d4d5f5a5ef33513b7a4eaef424530363f53ea3759"
scanner="aquasec/trivy@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb"
builder="golang@sha256:70bd7ddea8b6cbe5d6943cde279d6b67feb10cc924fb9100d1d8757c1575b280"
mkdir -p "$out/server"
finish() {
  find "$out" -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > "$out/SHA256SUMS"
}
trap finish EXIT
test "$(uname -sm)" = "Linux x86_64"
git rev-parse HEAD > "$out/trial-sha.txt"
git diff --exit-code "$BASE_SHA" HEAD -- src infrastructure apps contracts deploy tools/client_profile pyproject.toml uv.lock
printf '%s\n' "$BASE_SHA" > "$out/base-sha.txt"
python tools/postgres_revalidation/prepare.py
cp tools/postgres_revalidation/prepare.py tools/postgres_revalidation/run.sh "$out/"
docker load -i "$RUNNER_TEMP/preserved-gosu/audit/corrected-image.tar" | tee "$out/server/load.log"
test "$(docker image inspect --format '{{.Id}}' "$server")" = "$server"
test "$(docker image inspect --format '{{.Os}}/{{.Architecture}}' "$server")" = linux/amd64
docker image inspect "$server" > "$out/server/image.json"
docker run --rm --network none --entrypoint cat "$server" /usr/local/bin/gosu > "$out/server/gosu"
printf '%s  %s\n' "99450e87c219ee02cf76f2a34285c75036e74de7c2d1831e8e129ff9ba45e1cb" "$out/server/gosu" | sha256sum -c -
docker run --rm --network none --entrypoint sh "$server" -ec '
  gosu --version
  test "$(gosu nobody id -u)" = "$(id -u nobody)"
  test "$(gosu postgres id -u)" = "$(id -u postgres)"
  test "$(gosu postgres id -u)" != 0
  gosu postgres id
  postgres --version
' | tee "$out/server/gosu-check.log"
docker run --rm --network none --entrypoint sh "$server" -ec '
  cat /etc/os-release
  apk info -vv
' > "$out/server/package-inventory.txt"
docker pull --platform linux/amd64 "$builder"
docker image inspect "$builder" > "$out/server/go-builder.json"
docker run --rm --network none -v "$out/server:/input:ro" "$builder" go version -m /input/gosu > "$out/server/gosu-build-info.txt"
grep -q 'go1.27.4' "$out/server/gosu-build-info.txt"
grep -q 'GOOS=linux' "$out/server/gosu-build-info.txt"
grep -q 'GOARCH=amd64' "$out/server/gosu-build-info.txt"
grep -q 'CGO_ENABLED=0' "$out/server/gosu-build-info.txt"
docker pull --platform linux/amd64 "$scanner"
docker image inspect "$scanner" > "$out/server/scanner-image.json"
docker run --rm "$scanner" --version > "$out/server/scanner-version.txt"
cache="$RUNNER_TEMP/server-trivy-cache"
mkdir -p "$cache"
docker run --rm -v "$cache:/cache" "$scanner" --cache-dir /cache image --download-db-only
cp "$cache/db/metadata.json" "$out/server/database-before.json"
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$out/server:/output" -v "$cache:/cache" "$scanner" --cache-dir /cache image --format cyclonedx --output /output/sbom.cdx.json "$server"
# Preserve every severity and every finding for review; this is not an adoption gate.
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$out/server:/output" -v "$cache:/cache" "$scanner" --cache-dir /cache image --scanners vuln --list-all-pkgs --format json --output /output/trivy.json "$server"
cp "$cache/db/metadata.json" "$out/server/database-after.json"
bash "$out/pair-verification.sh" "$out/pair"
test "$(cat "$out/pair/server-running-id.txt")" = "$server"
test "$(cat "$out/pair/results/persistence-after.log")" = 1
python - "$out" <<'PY'
import json, sys, xml.etree.ElementTree as ET
from pathlib import Path
out = Path(sys.argv[1])
cases = ET.parse(out / "pair/results/pytest.xml").getroot().findall(".//testcase")
assert len(cases) == 170
assert all(c.find("failure") is None and c.find("error") is None and c.find("skipped") is None for c in cases)
proofs = []
for case in cases:
    if "test_concurrent_duplicate_consumer_workers" not in case.attrib["name"]:
        continue
    p = case.find('./properties/property[@name="concurrency_proof"]')
    assert p is not None
    proof = json.loads(p.attrib["value"])
    proof["case"] = case.attrib["name"]
    assert proof["waiting_pid"] != proof["blocking_pid"]
    assert proof["wait_event_type"] == "Lock"
    assert proof["durable_effects"] == proof["durable_processed_ids"] == 1
    assert proof["durable_acknowledgements"] == 2 and proof["pending_after_restart"] == 0
    proofs.append(proof)
assert len(proofs) == 6
tls = json.loads((out / "pair/results/tls.json").read_text())
assert [x["result"] for x in tls] == ["PASS", "PASS_REJECTED", "PASS_REJECTED"]
findings = [
    dict(v, Target=r.get("Target", ""))
    for r in json.loads((out / "server/trivy.json").read_text()).get("Results", [])
    for v in r.get("Vulnerabilities", [])
]
(out / "server/findings.json").write_text(json.dumps(findings, indent=2) + "\n")
(out / "CONCURRENCY-PROOFS.json").write_text(json.dumps(proofs, indent=2) + "\n")
(out / "PAIR-RESULTS.json").write_text(json.dumps({
    "tests_passed": len(cases), "tests_failed": 0, "tests_skipped": 0,
    "concurrency_cases_passed": len(proofs), "tls_cases_passed": 3,
    "persistence_after_server_restart": True,
    "server_findings_count": len(findings), "adoption_performed": False,
}, indent=2) + "\n")
print((out / "PAIR-RESULTS.json").read_text())
PY
