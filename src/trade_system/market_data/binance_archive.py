"""Collect a verified daily BTCUSDT archive from Binance public data."""

import json
import re
from collections.abc import Callable
from datetime import UTC, date, datetime
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlopen
from uuid import uuid4
from zipfile import ZipFile

from trade_system.market_data.klines import INTERVAL_MINUTES, normalize_day

MARKETS = {"spot": "spot", "futures-um": "futures/um"}
SYMBOL = "BTCUSDT"
MAX_BYTES = 2 * 1024 * 1024


def download(url: str) -> bytes:
    with urlopen(url, timeout=20) as response:
        data: bytes = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Public archive response exceeds the size limit.")
    return data


def normalize_archive(
    archive: bytes, day: date, interval: str, *, market: str
) -> tuple[bytes, int, str]:
    """Validate the expected CSV member and normalize its candles."""
    member = f"{SYMBOL}-{interval}-{day.isoformat()}.csv"
    with ZipFile(BytesIO(archive)) as zipped:
        if (
            zipped.namelist() != [member]
            or zipped.getinfo(member).file_size > MAX_BYTES
        ):
            raise ValueError("Unexpected Binance archive contents.")
        return normalize_day(zipped.read(member), day, interval, market=market)


def collect_day(
    *,
    market: str,
    day: date,
    interval: str,
    output: Path,
    fetch: Callable[[str], bytes] = download,
) -> Path:
    """Publish a complete validated run and return its manifest path."""
    if market not in MARKETS or interval not in INTERVAL_MINUTES:
        raise ValueError("Unsupported market or candle interval.")
    if day >= datetime.now(UTC).date():
        raise ValueError("Select a completed UTC day.")

    stem = f"{SYMBOL}-{interval}-{day.isoformat()}"
    source_url = (
        f"https://data.binance.vision/data/{MARKETS[market]}"
        f"/daily/klines/{SYMBOL}/{interval}/{stem}.zip"
    )
    checksum_url = source_url + ".CHECKSUM"
    checksum = fetch(checksum_url).decode("ascii").split()
    if (
        len(checksum) != 2
        or not re.fullmatch(r"[0-9a-fA-F]{64}", checksum[0])
        or checksum[1] != f"{stem}.zip"
    ):
        raise ValueError("Unexpected Binance checksum format.")

    archive = fetch(source_url)
    received_at = datetime.now(UTC).isoformat()
    archive_hash = sha256(archive).hexdigest()
    if archive_hash != checksum[0].lower():
        raise ValueError("Binance archive SHA-256 mismatch.")

    normalized, rows, timestamp_unit = normalize_archive(
        archive, day, interval, market=market
    )

    run_id = uuid4().hex
    target = output / market / SYMBOL / interval / day.isoformat() / run_id
    manifest = {
        "schema_version": "1.0.0",
        "run_id": run_id,
        "exchange": "binance",
        "market": market,
        "symbol": SYMBOL,
        "interval": interval,
        "date_utc": day.isoformat(),
        "received_at": received_at,
        "available_at": datetime.now(UTC).isoformat(),
        "source": {
            "archive_url": source_url,
            "checksum_url": checksum_url,
            "timestamp_unit": timestamp_unit,
        },
        "quality": {
            "status": "passed",
            "expected_rows": 1440 // INTERVAL_MINUTES[interval],
            "rows": rows,
            "gaps": 0,
            "duplicate_open_times": 0,
        },
        "sha256": {
            "source.zip": archive_hash,
            "candles.csv": sha256(normalized).hexdigest(),
        },
    }

    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=target.parent) as temporary:
        staging = Path(temporary) / "snapshot"
        staging.mkdir()
        (staging / "source.zip").write_bytes(archive)
        (staging / "candles.csv").write_bytes(normalized)
        (staging / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        staging.rename(target)
    return target / "manifest.json"
