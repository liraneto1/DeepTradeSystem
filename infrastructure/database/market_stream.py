"""Record continuous candles and their first public observation."""

from datetime import datetime

from sqlalchemy import Column, DateTime, MetaData, Table, Text, func, select
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.engine import Engine

from infrastructure.database.market_history import (
    DECIMAL_FIELDS,
    SCHEMA,
    SOURCE,
    store_candles,
)
from trade_system.market_data.binance_archive import SYMBOL
from trade_system.market_data.binance_stream import Observation

OBSERVATION = Table(
    "market_candle_observation",
    MetaData(),
    Column("market", Text(), primary_key=True),
    Column("symbol", Text(), primary_key=True),
    Column("interval", Text(), primary_key=True),
    Column("open_time_utc", DateTime(timezone=True), primary_key=True),
    Column("source_kind", Text(), nullable=False),
    Column("source_url", Text(), nullable=False),
    Column("received_at", DateTime(timezone=True), nullable=False),
    Column("available_at", DateTime(timezone=True), nullable=False),
    Column("payload", JSONB(), nullable=False),
    schema=SCHEMA,
)


class StreamStore:
    def __init__(self, engine: Engine, market: str, interval: str) -> None:
        self.engine = engine
        self.key = {"market": market, "symbol": SYMBOL, "interval": interval}

    def latest(self) -> datetime | None:
        with self.engine.connect() as connection:
            result: datetime | None = connection.execute(
                select(func.max(OBSERVATION.c.open_time_utc)).filter_by(**self.key)
            ).scalar_one()
            return result

    def persist(self, observations: list[Observation]) -> None:
        with self.engine.begin() as connection:
            for item in observations:
                key = {**self.key, "open_time_utc": item.open_time}
                values = dict(zip(DECIMAL_FIELDS, item.decimals, strict=True))
                day = item.open_time.date()
                connection.execute(
                    insert(SOURCE)
                    .values(
                        **self.key,
                        day_utc=day,
                        manifest={
                            "schema_version": "1.0.0",
                            "kind": "public_continuous",
                        },
                    )
                    .on_conflict_do_nothing(
                        index_elements=list(SOURCE.primary_key.columns)
                    )
                )
                candle: dict[str, object] = {
                    **key,
                    **values,
                    "day_utc": day,
                    "close_time_exclusive_utc": item.close_time,
                    "trade_count": item.trades,
                }
                store_candles(connection, [candle])
                connection.execute(
                    insert(OBSERVATION)
                    .values(
                        **key,
                        source_kind=item.source_kind,
                        source_url=item.source_url,
                        received_at=item.received_at,
                        payload=item.payload,
                    )
                    .on_conflict_do_nothing(
                        index_elements=list(OBSERVATION.primary_key.columns)
                    )
                )
