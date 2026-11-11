import csv
import json
import os
import subprocess
import sys
from datetime import UTC, date, datetime
from hashlib import sha256
from io import BytesIO, StringIO
from pathlib import Path
from zipfile import ZipFile

import pytest

from trade_system.market_data.binance_archive import collect_day
from trade_system.market_data.klines import HEADER, normalize_day

DAY = date(2025, 11, 10)
STEM = "BTCUSDT-1h-2025-11-10"


def sample_rows(ticks_per_second: int) -> list[list[str]]:
    start = int(datetime(2025, 11, 10, tzinfo=UTC).timestamp()) * ticks_per_second
    step = 3600 * ticks_per_second
    return [
        [
            str(opened),
            "2.00000001",
            "3.00",
            "1.00",
            "2.50",
            "5.00",
            str(opened + step - 1),
            "10.00",
            "3",
            "4.00",
            "8.00",
            "0",
        ]
        for opened in range(start, start + step * 24, step)
    ]


def csv_bytes(rows: list[list[str]]) -> bytes:
    target = StringIO()
    csv.writer(target).writerows(rows)
    return target.getvalue().encode()


@pytest.mark.parametrize(
    ("market", "ticks_per_second", "unit"),
    [("spot", 1_000_000, "microseconds"), ("futures-um", 1000, "milliseconds")],
)
def test_collects_complete_day_and_hashes_files(
    tmp_path: Path, market: str, ticks_per_second: int, unit: str
) -> None:
    rows = sample_rows(ticks_per_second)
    if market == "futures-um":
        rows.insert(0, list(HEADER))

    target = BytesIO()
    with ZipFile(target, "w") as archive:
        archive.writestr(STEM + ".csv", csv_bytes(rows))
    raw = target.getvalue()
    digest = sha256(raw).hexdigest()
    requests: list[str] = []

    def fetch(url: str) -> bytes:
        requests.append(url)
        if url.endswith(".CHECKSUM"):
            return f"{digest}  {STEM}.zip\n".encode()
        return raw

    path = collect_day(
        market=market, day=DAY, interval="1h", output=tmp_path, fetch=fetch
    )
    manifest = json.loads(path.read_bytes())
    expected_segment = "spot" if market == "spot" else "futures/um"
    assert requests[0] == (
        f"https://data.binance.vision/data/{expected_segment}"
        f"/daily/klines/BTCUSDT/1h/{STEM}.zip.CHECKSUM"
    )
    assert requests[1] == manifest["source"]["archive_url"]
    assert manifest["source"]["timestamp_unit"] == unit
    assert manifest["quality"] == {
        "status": "passed",
        "expected_rows": 24,
        "rows": 24,
        "gaps": 0,
        "duplicate_open_times": 0,
    }
    for name, sha in manifest["sha256"].items():
        assert sha256((path.parent / name).read_bytes()).hexdigest() == sha
    with (path.parent / "candles.csv").open(newline="", encoding="utf-8") as result:
        candles = list(csv.DictReader(result))
    assert candles[0]["open"] == "2.00000001"
    assert candles[0]["open_time_utc"] == "2025-11-10T00:00:00+00:00"
    assert candles[-1]["close_time_exclusive_utc"] == "2025-11-11T00:00:00+00:00"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        (0, "1762732800000000", "gap, duplicate"),
        (6, "0", "timestamp mismatch"),
        (2, "1.00", "inconsistent OHLCV"),
        (5, "-1", "invalid decimal"),
        (8, "", "invalid trade count"),
    ],
)
def test_rejects_inconsistent_rows(field: int, value: str, message: str) -> None:
    rows = sample_rows(1_000_000)
    rows[1][field] = value
    with pytest.raises(ValueError, match=message):
        normalize_day(csv_bytes(rows), DAY, "1h", market="spot")


def test_rejects_missing_candle() -> None:
    with pytest.raises(ValueError, match="Expected 24 candles, received 23"):
        normalize_day(csv_bytes(sample_rows(1000)[1:]), DAY, "1h", market="futures-um")


def test_checksum_failure_publishes_no_snapshot(tmp_path: Path) -> None:
    def fetch(url: str) -> bytes:
        if url.endswith(".CHECKSUM"):
            return f"{'0' * 64}  {STEM}.zip\n".encode()
        return b"altered archive"

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        collect_day(market="spot", day=DAY, interval="1h", output=tmp_path, fetch=fetch)
    assert not list(tmp_path.iterdir())


def test_cli_blocks_live(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "apps.market_data",
            "--market",
            "spot",
            "--date",
            DAY.isoformat(),
            "--output",
            str(tmp_path),
        ],
        env={**os.environ, "TRADE_SYSTEM_ENVIRONMENT": "LIVE", "LIVE_ENABLED": "false"},
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 1
    assert "TRADE_SYSTEM_ENVIRONMENT must be TRAINING or PAPER" in result.stderr
    assert not list(tmp_path.iterdir())
