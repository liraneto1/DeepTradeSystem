"""Poll public BTCUSDT funding and settle it in a local Futures PAPER account."""

import argparse
import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from urllib.error import HTTPError

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from infrastructure.database.config import local_database_url
from infrastructure.database.paper_futures import (
    apply_funding,
    latest_funding_at,
)
from infrastructure.database.paper_ledger import require_paper
from infrastructure.telemetry import log_event, run_worker
from trade_system.market_data.binance_funding import fetch_funding_page
from trade_system.market_data.binance_stream import epoch_ms
from trade_system.market_data.klines import EPOCH
from trade_system.risk.futures import FundingObservation

logger = logging.getLogger(__name__)
FundingFeed = Callable[[int, int], list[FundingObservation]]


def collect_funding(
    engine: Engine,
    account_id: str,
    *,
    start: datetime,
    fetch: FundingFeed = fetch_funding_page,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> int:
    if start.utcoffset() is None or start < EPOCH:
        raise ValueError("funding: invalid_start")
    last = latest_funding_at(engine, account_id)
    start_ms = epoch_ms(start)
    if EPOCH + timedelta(milliseconds=start_ms) < start:
        start_ms += 1
    if last is not None:
        start_ms = max(start_ms, epoch_ms(last) + 1)
    cutoff = now()
    if cutoff.utcoffset() is None:
        raise ValueError("funding: invalid_cutoff")
    end_ms = epoch_ms(cutoff)
    applied = 0
    while start_ms <= end_ms:
        batch = fetch(start_ms, end_ms)
        if not batch:
            break
        cursor = start_ms
        as_of = now()
        for event in batch:
            event.validate(as_of)
            timestamp = epoch_ms(event.funding_at)
            if not cursor <= timestamp <= end_ms or event.funding_at > cutoff:
                raise ValueError("funding: observation_outside_window")
            cursor = timestamp + 1
        for event in batch:
            apply_funding(engine, account_id, event, as_of=as_of)
            applied += 1
        start_ms = cursor
    return applied


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--account", required=True, help="Existing Futures PAPER account"
    )
    parser.add_argument("--start", required=True, type=datetime.fromisoformat)
    parser.add_argument("--once", action="store_true", help="Exit after one collection")
    args = parser.parse_args()
    require_paper()
    engine = create_engine(
        local_database_url(), hide_parameters=True, connect_args={"connect_timeout": 5}
    )
    try:
        with engine.connect() as lock:
            acquired: bool = lock.execute(
                text("SELECT pg_try_advisory_lock(hashtextextended(:key, 0))"),
                {"key": f"paper-funding:{args.account}"},
            ).scalar_one()
            if not acquired:
                raise RuntimeError(
                    "This PAPER account already has a funding collector."
                )
            lock.commit()
            while True:
                delay = 60
                try:
                    applied = collect_funding(engine, args.account, start=args.start)
                except HTTPError as error:
                    if args.once or (error.code != 429 and error.code < 500):
                        raise
                    header = error.headers.get("Retry-After", "")
                    if header.isdecimal():
                        delay = max(delay, int(header))
                except OSError:
                    if args.once:
                        raise
                else:
                    if applied or args.once:
                        print(f"Funding entries applied: {applied}", flush=True)
                    if args.once:
                        return
                    time.sleep(delay)
                    continue
                log_event(
                    logger,
                    "funding_retry",
                    level=logging.WARNING,
                    retry_delay_seconds=delay,
                )
                time.sleep(delay)
    except KeyboardInterrupt:
        pass
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_worker(main, logger)
