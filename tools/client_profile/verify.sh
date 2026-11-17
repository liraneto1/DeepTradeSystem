#!/usr/bin/env bash
# Disposable local test resources only; the PostgreSQL server image is unchanged.
set -euo pipefail
out=$(realpath -m "$1")
mkdir -p "$out/results"
root=$(git rev-parse --show-toplevel)
cd "$root"
case "$(uname -sm)" in "Linux x86_64") ;; *) echo "Linux/amd64 required"; exit 1;; esac
pg="client-check-$(date +%s)-$$"
volume="$pg-data"
server="postgres@sha256:a77aa70e641402a21411b92b721c58d10f23b50ae5fdd2333efd22d166e1e5f7"
scanner="aquasec/trivy@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb"
cleanup() {
  docker logs "$pg" > "$out/postgres.log" 2>&1 || true
  docker rm -f "$pg" >/dev/null 2>&1 || true
  docker volume rm "$volume" >/dev/null 2>&1 || true
  if test -n "$tls"; then rm -f "$tls/server.key" "$tls/server.crt"; rmdir "$tls" 2>/dev/null || true; fi
  find "$out" -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > "$out/SHA256SUMS"
}
tls=""
trap cleanup EXIT
git rev-parse HEAD > "$out/validation-sha.txt"
sha256sum pyproject.toml uv.lock > "$out/input-hashes.txt"
docker build --platform linux/amd64 --progress plain --target test -f deploy/docker/client-runtime.Dockerfile -t local/deeptrade-client-test:check . 2>&1 | tee "$out/build-test.log"
docker build --platform linux/amd64 --progress plain --target runtime -f deploy/docker/client-runtime.Dockerfile -t local/deeptrade-client-runtime:check . 2>&1 | tee "$out/build-runtime.log"
for kind in test runtime; do
  docker image inspect "local/deeptrade-client-$kind:check" > "$out/$kind-image.json"
  container=$(docker create "local/deeptrade-client-$kind:check")
  mkdir -p "$out/$kind"
  docker cp "$container:/audit/." "$out/$kind/"
  docker rm "$container"
done
python tools/client_profile/verify.py "$out"
test_image=$(docker image inspect --format '{{.Id}}' local/deeptrade-client-test:check)
runtime=$(docker image inspect --format '{{.Id}}' local/deeptrade-client-runtime:check)
printf '%s\n' "$test_image" > "$out/tested-image-id.txt"
printf '%s\n' "$runtime" > "$out/runtime-tested-image-id.txt"
export POSTGRES_PASSWORD
POSTGRES_PASSWORD=$(python -c 'import secrets; print(secrets.token_hex(24))')
if test "${GITHUB_ACTIONS:-false}" = true; then echo "::add-mask::$POSTGRES_PASSWORD"; fi
export LIVE_ENABLED=false TRADE_SYSTEM_ENVIRONMENT=PAPER RUN_POSTGRES_TESTS=1
docker pull --platform linux/amd64 "$server"
docker image inspect "$server" > "$out/server-image.json"
docker volume create "$volume"
docker run -d --name "$pg" -p 127.0.0.1:55432:5432 \
  -e POSTGRES_USER=trade_system -e POSTGRES_DB=trade_system -e POSTGRES_PASSWORD \
  --mount "type=volume,source=$volume,target=/var/lib/postgresql/data" \
  "$server"
ready=false
for n in $(seq 1 60); do
  if docker exec "$pg" pg_isready -h 127.0.0.1 -U trade_system -d trade_system; then ready=true; break; fi
  sleep 1
done
test "$ready" = true
docker inspect --format '{{.Image}}' "$pg" > "$out/server-running-id.txt"
docker run --rm --network host --mount "type=bind,source=$out/results,target=/results" \
  -e POSTGRES_PASSWORD -e LIVE_ENABLED -e TRADE_SYSTEM_ENVIRONMENT -e RUN_POSTGRES_TESTS \
  "$test_image" bash -ec '
    set -o pipefail
    ruff check src infrastructure apps tests tools/client_profile 2>&1 | tee /results/ruff.log
    ruff format --check src infrastructure apps tests tools/client_profile 2>&1 | tee /results/format.log
    mypy 2>&1 | tee /results/mypy.log
    pytest --junitxml=/results/pytest.xml 2>&1 | tee /results/pytest.log
  '
tls=$(mktemp -d)
openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj '/CN=localhost' \
  -addext 'subjectAltName=DNS:localhost,IP:127.0.0.1' \
  -keyout "$tls/server.key" -out "$tls/server.crt" 2>/dev/null
docker cp "$tls/server.key" "$pg:/tmp/profile-server.key"
docker cp "$tls/server.crt" "$pg:/tmp/profile-server.crt"
docker exec -u root "$pg" sh -ec 'cp /tmp/profile-server.key "$PGDATA/server.key"; cp /tmp/profile-server.crt "$PGDATA/server.crt"; chown postgres:postgres "$PGDATA/server.key" "$PGDATA/server.crt"; chmod 0600 "$PGDATA/server.key"; printf "\nssl=on\nssl_cert_file=\047server.crt\047\nssl_key_file=\047server.key\047\n" >> "$PGDATA/postgresql.conf"'
docker restart "$pg"
ready=false
for n in $(seq 1 30); do
  if docker exec "$pg" pg_isready -h 127.0.0.1 -U trade_system -d trade_system; then ready=true; break; fi
  sleep 1
done
test "$ready" = true
cp "$tls/server.crt" "$out/results/test-server-public.crt"
cp tools/client_profile/tls.py "$out/results/check_tls.py"
docker run --rm --network host --mount "type=bind,source=$out/results,target=/results" \
  -e POSTGRES_PASSWORD "$runtime" python /results/check_tls.py | tee "$out/results/tls.log"
docker save "$runtime" -o "$out/client-runtime.tar"
docker pull --platform linux/amd64 "$scanner"
docker image inspect "$scanner" > "$out/scanner-image.json"
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$out:/output" \
  "$scanner" image --format cyclonedx --output /output/runtime-sbom.cdx.json "$runtime"
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$out:/output" \
  "$scanner" image --scanners vuln --exit-code 1 --format json --output /output/runtime-trivy.json "$runtime"
sha256sum pyproject.toml uv.lock > "$out/final-input-hashes.txt"
diff -u "$out/input-hashes.txt" "$out/final-input-hashes.txt"
