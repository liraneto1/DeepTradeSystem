"""Run continuous public BTCUSDT candle ingestion."""

import argparse
import logging
import time
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager
from datetime import UTC, datetime, timedelta
from typing import Protocol
from urllib.error import HTTPError

from sqlalchemy import create_engine, text
from websockets.exceptions import ConnectionClosed, InvalidStatus

from infrastructure.database.config import local_database_url
from infrastructure.database.market_stream import StreamStore
from infrastructure.telemetry import log_event, run_worker
from trade_system.market_data.binance_archive import MARKETS
from trade_system.market_data.binance_stream import (
    PAGE_SIZE,
    BinanceKlines,
    Observation,
)
from trade_system.market_data.klines import EPOCH, INTERVAL_MINUTES

logger = logging.getLogger(__name__)


class Feed(Protocol):
    step: timedelta

    def stream(self) -> AbstractContextManager[Iterator[Observation | None]]: ...
    def backfill(self, start: datetime, end: datetime) -> list[Observation]: ...


class IncompleteBackfill(ConnectionError):
    """A REST window is not yet complete."""


def ingest(
    feed: Feed,
    store: StreamStore,
    *,
    once: bool = False,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    step = feed.step
    last = store.latest()
    cursor = (
        last + step
        if last is not None
        else EPOCH + ((now() - EPOCH) // step - 1) * step
    )

    def recover(until: datetime) -> None:
        nonlocal cursor
        while cursor < until:
            end = min(cursor + PAGE_SIZE * step, until)
            batch = feed.backfill(cursor, end)
            count = (end - cursor) // step
            expected = [cursor + index * step for index in range(count)]
            if [item.open_time for item in batch] != expected:
                raise IncompleteBackfill("Missing or out-of-order REST candles.")
            store.persist(batch)
            cursor = end

    delay = 1
    while True:
        retry_after = 0
        try:
            with feed.stream() as messages:
                recover(EPOCH + ((now() - EPOCH) // step) * step)
                for item in messages:
                    delay = 1
                    if item is None:
                        continue
                    recover(item.open_time)
                    store.persist([item])
                    cursor = max(cursor, item.close_time)
                    if once:
                        return
        except HTTPError as error:
            if error.code != 429 and error.code < 500:
                raise
            header = error.headers.get("Retry-After", "")
            retry_after = (
                int(header) if header.isdecimal() else (60 if error.code == 429 else 0)
            )
        except InvalidStatus as error:
            if error.response.status_code < 500:
                raise
        except (OSError, ConnectionClosed):
            pass

        log_event(
            logger,
            "market_stream_reconnecting",
            level=logging.WARNING,
            retry_delay_seconds=max(delay, retry_after),
        )
        sleep(max(delay, retry_after))
        delay = min(delay * 2, 30)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True, choices=MARKETS)
    parser.add_argument("--interval", choices=INTERVAL_MINUTES, default="5m")
    parser.add_argument(
        "--once", action="store_true", help="Exit after a closed WebSocket candle"
    )
    args = parser.parse_args()
    engine = create_engine(
        local_database_url(), hide_parameters=True, connect_args={"connect_timeout": 5}
    )
    try:
        with engine.connect() as lock:
            key = f"market-stream:{args.market}:{args.interval}"
            acquired: bool = lock.execute(
                text("SELECT pg_try_advisory_lock(hashtextextended(:key, 0))"),
                {"key": key},
            ).scalar_one()
            if not acquired:
                raise RuntimeError("This market and interval already have a collector.")
            lock.commit()
            ingest(
                BinanceKlines(args.market, args.interval),
                StreamStore(engine, args.market, args.interval),
                once=args.once,
            )
    except KeyboardInterrupt:
        pass
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_worker(main, logger)
