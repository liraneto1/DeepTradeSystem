"""Persist complete, verified daily snapshots in one PostgreSQL transaction."""

import csv
import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from io import StringIO
from pathlib import Path
from typing import Any

from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    MetaData,
    Numeric,
    Table,
    Text,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.engine import Engine

from trade_system.market_data.binance_archive import MARKETS, SYMBOL, normalize_archive
from trade_system.market_data.klines import INTERVAL_MINUTES

SCHEMA = "trade_system"
DECIMAL_FIELDS = (
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "taker_buy_volume",
    "taker_buy_quote_volume",
)

SOURCE = Table(
    "market_history_source",
    MetaData(),
    Column("market", Text(), primary_key=True),
    Column("symbol", Text(), primary_key=True),
    Column("interval", Text(), primary_key=True),
    Column("day_utc", Date(), primary_key=True),
    Column("archive_sha256", Text(), nullable=False),
    Column("csv_sha256", Text(), nullable=False),
    Column("manifest", JSONB(), nullable=False),
    schema=SCHEMA,
)
CANDLE = Table(
    "market_candle",
    MetaData(),
    Column("market", Text(), primary_key=True),
    Column("symbol", Text(), primary_key=True),
    Column("interval", Text(), primary_key=True),
    Column("open_time_utc", DateTime(timezone=True), primary_key=True),
    Column("day_utc", Date(), nullable=False),
    Column("close_time_exclusive_utc", DateTime(timezone=True), nullable=False),
    Column("trade_count", BigInteger(), nullable=False),
    *(Column(name, Numeric(), nullable=False) for name in DECIMAL_FIELDS),
    schema=SCHEMA,
)


@dataclass(frozen=True)
class Snapshot:
    market: str
    interval: str
    day: date
    archive_hash: str
    csv_hash: str
    manifest: dict[str, Any]
    csv_text: str


def read_snapshot(path: Path) -> Snapshot:
    manifest: dict[str, Any] = json.loads(path.read_bytes())
    market: str = manifest["market"]
    interval: str = manifest["interval"]
    if (
        market not in MARKETS
        or interval not in INTERVAL_MINUTES
        or manifest.get("symbol") != SYMBOL
        or manifest.get("exchange") != "binance"
        or manifest.get("schema_version") != "1.0.0"
    ):
        raise ValueError("Unsupported market-history manifest.")

    day = date.fromisoformat(manifest["date_utc"])
    raw = (path.parent / "source.zip").read_bytes()
    normalized = (path.parent / "candles.csv").read_bytes()
    archive_hash = sha256(raw).hexdigest()
    csv_hash = sha256(normalized).hexdigest()
    if manifest["sha256"] != {"source.zip": archive_hash, "candles.csv": csv_hash}:
        raise ValueError("Market-history snapshot SHA-256 mismatch.")

    canonical, count, unit = normalize_archive(raw, day, interval, market=market)
    if (
        canonical != normalized
        or manifest["quality"]["rows"] != count
        or manifest["source"]["timestamp_unit"] != unit
    ):
        raise ValueError("Market-history snapshot differs from the source archive.")

    return Snapshot(
        market, interval, day, archive_hash, csv_hash, manifest, normalized.decode()
    )


def persist_history(engine: Engine, manifests: Sequence[Path]) -> tuple[int, int]:
    """Return inserted candles and skipped identical days."""
    snapshots = [read_snapshot(path) for path in manifests]
    if not snapshots:
        raise ValueError("At least one market-history snapshot is required.")
    first = snapshots[0]
    for offset, item in enumerate(snapshots):
        if (item.market, item.interval, item.day) != (
            first.market,
            first.interval,
            first.day + timedelta(days=offset),
        ):
            raise ValueError(
                "Expected contiguous UTC days for one market and interval."
            )

    inserted = skipped = 0
    with engine.begin() as connection:
        for item in snapshots:
            key = {
                "market": item.market,
                "symbol": SYMBOL,
                "interval": item.interval,
                "day_utc": item.day,
            }
            source = (
                insert(SOURCE)
                .values(
                    **key,
                    archive_sha256=item.archive_hash,
                    csv_sha256=item.csv_hash,
                    manifest=item.manifest,
                )
                .on_conflict_do_nothing(index_elements=list(SOURCE.primary_key.columns))
                .returning(SOURCE.c.day_utc)
            )
            if connection.execute(source).scalar_one_or_none() is None:
                existing = connection.execute(
                    select(SOURCE.c.archive_sha256, SOURCE.c.csv_sha256).filter_by(
                        **key
                    )
                ).one()
                if existing != (item.archive_hash, item.csv_hash):
                    raise ValueError(f"Source changed for {item.market} on {item.day}.")
                skipped += 1
                continue

            rows = [
                {
                    **key,
                    "open_time_utc": datetime.fromisoformat(row["open_time_utc"]),
                    "close_time_exclusive_utc": datetime.fromisoformat(
                        row["close_time_exclusive_utc"]
                    ),
                    "trade_count": int(row["trade_count"]),
                    **{name: Decimal(row[name]) for name in DECIMAL_FIELDS},
                }
                for row in csv.DictReader(StringIO(item.csv_text))
            ]
            connection.execute(CANDLE.insert(), rows)
            inserted += len(rows)
    return inserted, skipped
