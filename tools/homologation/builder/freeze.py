"""Offline sealing for review. No subprocess, network, Docker or VPS commands."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare import digest, image_id, json_write  # noqa: E402
from runner import verify_package  # noqa: E402


def freeze_package(
    approved: Path,
    test_tar: Path,
    receipt: dict[str, Any],
    output: Path,
    expected_package: str,
) -> dict[str, Any]:
    approved = approved.resolve()
    output = output.resolve()
    if output.exists() or output.is_relative_to(approved):
        raise ValueError("Output must be new and outside the approved package")
    manifest = verify_package(approved, expected_package)
    if manifest["test"] is not None or manifest["ready_for_execution_review"]:
        raise ValueError("Expected the approved draft, not a previously sealed package")
    identity = image_id(test_tar)
    checksum = digest(test_tar)
    if receipt.get("image_id") != identity or receipt.get("tar_sha256") != checksum:
        raise ValueError("Build receipt/image identity mismatch")
    if receipt.get("approved_package_sha256") != expected_package:
        raise ValueError("Receipt refers to another source package")
    if (
        receipt.get("source_verification") != "PASS"
        or receipt.get("probe_result") != "PASS"
    ):
        raise ValueError("Source and isolated tools probe must pass first")
    output.mkdir(parents=True)
    for line in (
        (approved / "PACKAGE-SHA256SUMS").read_text(encoding="utf-8").splitlines()
    ):
        _, name = line.split("  ", 1)
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(approved / name, target)
    (output / "artifacts").mkdir(exist_ok=True)
    shutil.copyfile(test_tar, output / "artifacts/test-image.tar")
    json_write(output / "BUILD-RECEIPT.json", receipt)
    manifest["test"] = {
        "id": identity,
        "tar_sha256": checksum,
        "bytes": test_tar.stat().st_size,
        "filename": "test-image.tar",
    }
    manifest["ready_for_execution_review"] = True
    manifest["build_receipt_sha256"] = digest(output / "BUILD-RECEIPT.json")
    manifest["source_approved_package_sha256"] = expected_package
    manifest["human_execution_approval"] = "NOT_GRANTED_BY_FREEZING"
    json_write(output / "manifest.json", manifest)
    files = sorted(
        (p for p in output.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(output).as_posix(),
    )
    (output / "PACKAGE-SHA256SUMS").write_text(
        "".join(f"{digest(p)}  {p.relative_to(output).as_posix()}\n" for p in files),
        encoding="utf-8",
    )
    verify_package(output)
    return {
        "package_sha256": digest(output / "PACKAGE-SHA256SUMS"),
        "test_image_id": identity,
        "test_tar_sha256": checksum,
        "ready_for_execution_review": True,
        "vps_execution_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--test-image-tar", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--approved-package-sha256", required=True)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    print(
        json.dumps(
            freeze_package(
                args.package,
                args.test_image_tar,
                receipt,
                args.output,
                args.approved_package_sha256,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
