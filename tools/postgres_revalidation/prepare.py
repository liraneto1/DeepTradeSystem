"""Verify the preserved PostgreSQL artifact and prepare an isolated pairing probe."""

import hashlib
import json
import os
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ARCHIVE_SHA = "78e0b41b43043fbba71d5c7a8e074402bc0b38a6fd96b27713e2554e354760eb"
SERVER_ID = "sha256:57e55d6e7bd1f06e5d75408d4d5f5a5ef33513b7a4eaef424530363f53ea3759"
IMAGE_TAR_SHA = "2dd7d8194012efb4d4b09053a2d7150060e61f120d13152eb814c524f8c1e661"


class ArtifactRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None and redirected.host != req.host:
            redirected.remove_header("Authorization")
        return redirected


def digest(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def main() -> None:
    temporary = Path(os.environ["RUNNER_TEMP"])
    out = temporary / "server-pair"
    old = temporary / "preserved-gosu"
    out.mkdir(exist_ok=True)
    old.mkdir(exist_ok=True)
    archive = old / "original.zip"
    request = urllib.request.Request(
        "https://api.github.com/repos/liraneto1/DeepTradeSystem/actions/artifacts/14353852908/zip",
        headers={
            "Authorization": "Bearer " + os.environ["GH_TOKEN"],
            "Accept": "application/vnd.github+json",
            "User-Agent": "DeepTradeSystem-PostgreSQL-revalidation",
        },
    )
    opener = urllib.request.build_opener(ArtifactRedirect())
    with opener.open(request, timeout=120) as response:
        with archive.open("wb") as target:
            while chunk := response.read(4 * 1024 * 1024):
                target.write(chunk)
    assert digest(archive) == ARCHIVE_SHA
    with zipfile.ZipFile(archive) as bundle:
        for info in bundle.infolist():
            assert (old / info.filename).resolve().is_relative_to(old.resolve())
        bundle.extractall(old)
    restored = []
    verified = []
    for line in (old / "audit-SHA256SUMS").read_text().splitlines():
        expected, relative = line.split("  ", 1)
        path = old / relative
        assert path.resolve().is_relative_to(old.resolve())
        if not path.exists():
            prefix = "audit/gosu-source/"
            assert relative.startswith(prefix)
            suffix = relative.removeprefix(prefix)
            with tarfile.open(old / "audit/gosu-source.tar.gz") as source:
                member = next(
                    m
                    for m in source.getmembers()
                    if m.name.split("/", 1)[-1] == suffix and m.isfile()
                )
                extracted = source.extractfile(member)
                assert extracted is not None
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(extracted.read())
            restored.append(relative)
        assert digest(path) == expected, relative
        verified.append(relative)
    assert len(verified) == 46
    assert digest(old / "audit/corrected-image.tar") == IMAGE_TAR_SHA
    assert (old / "audit/corrected-image-id.txt").read_text().strip() == SERVER_ID
    assert digest(old / "audit/gosu") == (
        "99450e87c219ee02cf76f2a34285c75036e74de7c2d1831e8e129ff9ba45e1cb"
    )
    identity = {
        "original_run_id": 44140610698,
        "original_artifact_id": 14353852908,
        "archive_sha256": ARCHIVE_SHA,
        "image_tar_sha256": IMAGE_TAR_SHA,
        "server_image_id": SERVER_ID,
        "manifest_hashes_verified": len(verified),
        "hidden_files_restored_from_verified_source": restored,
        "rebuild_performed": False,
    }
    (out / "ORIGINAL-ARTIFACT-VERIFICATION.json").write_text(
        json.dumps(identity, indent=2) + "\n"
    )
    original = Path("tools/client_profile/verify.sh").read_text()
    replacements = [
        (
            'server="postgres@sha256:a77aa70e641402a21411b92b721c58d10f23b50ae5fdd2333efd22d166e1e5f7"',
            'server="' + SERVER_ID + '"',
        ),
        (
            'docker pull --platform linux/amd64 "$server"',
            'docker image inspect "$server" >/dev/null',
        ),
        (
            "tls=$(mktemp -d)",
            """docker exec "$pg" psql -X -v ON_ERROR_STOP=1 \\
  -U trade_system -d trade_system -c "
CREATE TABLE public.server_revalidation_probe (
  marker text PRIMARY KEY, amount numeric(30,12) NOT NULL,
  observed_at timestamptz NOT NULL
);
INSERT INTO public.server_revalidation_probe VALUES (
  'gosu-pair', 12345.678901234567, '2026-11-17T00:00:00Z'
);" > "$out/results/persistence-before.log"
tls=$(mktemp -d)""",
        ),
        (
            'cp "$tls/server.crt" "$out/results/test-server-public.crt"',
            """docker exec "$pg" psql -X -v ON_ERROR_STOP=1 \\
  -U trade_system -d trade_system -Atc "
SELECT count(*) FROM public.server_revalidation_probe
WHERE marker='gosu-pair' AND amount=12345.678901234567
AND observed_at='2026-11-17T00:00:00Z'::timestamptz;
" > "$out/results/persistence-after.log"
test "$(cat "$out/results/persistence-after.log")" = 1
cp "$tls/server.crt" "$out/results/test-server-public.crt" """.rstrip(),
        ),
    ]
    modified = original
    for needle, replacement in replacements:
        assert modified.count(needle) == 1, needle
        modified = modified.replace(needle, replacement)
    (out / "pair-verification.sh").write_text(modified)
    (out / "original-verification.sh").write_text(original)
    print(json.dumps(identity))


if __name__ == "__main__":
    main()
