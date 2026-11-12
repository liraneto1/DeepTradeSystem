"""Poll the public BTCUSDT mark and evaluate liquidation in local Futures PAPER."""

import argparse
import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from urllib.error import HTTPError

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from infrastructure.database.config import local_database_url
from infrastructure.database.paper_futures import evaluate_liquidation
from infrastructure.database.paper_ledger import require_paper
from infrastructure.database.paper_mark_history import (
    IncompleteMarkHistory,
    recover_mark_history,
)
from infrastructure.telemetry import log_event, run_worker
from trade_system.market_data.binance_mark import fetch_mark
from trade_system.risk.futures import LiquidationCutoffError, LiquidationMark

logger = logging.getLogger(__name__)


def poll_mark(
    engine: Engine,
    account_id: str,
    *,
    maintenance_rate: Decimal,
    max_age: timedelta,
    fetch: Callable[[], LiquidationMark] = fetch_mark,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> bool:
    require_paper()
    mark = fetch()
    return (
        evaluate_liquidation(
            engine,
            account_id,
            mark,
            maintenance_rate=maintenance_rate,
            as_of=now(),
            max_age=max_age,
            recollected=True,
        )
        is not None
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--account", required=True, help="Existing Futures PAPER account"
    )
    parser.add_argument("--maintenance-rate", type=Decimal, required=True)
    parser.add_argument("--max-age-seconds", type=int, required=True)
    parser.add_argument(
        "--once", action="store_true", help="Evaluate one mark and exit"
    )
    parser.add_argument(
        "--recover-from",
        type=datetime.fromisoformat,
        help="Recover closed 1m mark candles starting at this timestamp",
    )
    args = parser.parse_args()
    recovery_cursor = args.recover_from
    if not args.maintenance_rate.is_finite() or not 0 < args.maintenance_rate < 1:
        parser.error("--maintenance-rate must be between 0 and 1 (exclusive)")
    if args.max_age_seconds <= 0:
        parser.error("--max-age-seconds must be positive")
    max_age = timedelta(seconds=args.max_age_seconds)
    require_paper()
    engine = create_engine(
        local_database_url(), hide_parameters=True, connect_args={"connect_timeout": 5}
    )
    try:
        with engine.connect() as lock:
            acquired: bool = lock.execute(
                text("SELECT pg_try_advisory_lock(hashtextextended(:key, 0))"),
                {"key": f"paper-liquidation:{args.account}"},
            ).scalar_one()
            if not acquired:
                raise RuntimeError("This PAPER account already has a mark collector.")
            lock.commit()
            while True:
                delay = 5
                try:
                    if recovery_cursor is not None:
                        try:
                            recovery_cursor = recover_mark_history(
                                engine, recovery_cursor
                            )
                        except IncompleteMarkHistory:
                            if args.once:
                                raise
                            log_event(
                                logger, "mark_history_pending", level=logging.WARNING
                            )
                    applied = poll_mark(
                        engine,
                        args.account,
                        maintenance_rate=args.maintenance_rate,
                        max_age=max_age,
                    )
                except LiquidationCutoffError:
                    if args.once:
                        raise
                    log_event(logger, "liquidation_mark_skipped", level=logging.WARNING)
                except HTTPError as error:
                    if args.once or (error.code != 429 and error.code < 500):
                        raise
                    header = error.headers.get("Retry-After", "")
                    delay = max(delay, int(header) if header.isdecimal() else 60)
                    log_event(
                        logger,
                        "liquidation_retry",
                        level=logging.WARNING,
                        retry_delay_seconds=delay,
                    )
                except OSError:
                    if args.once:
                        raise
                    log_event(
                        logger,
                        "liquidation_retry",
                        level=logging.WARNING,
                        retry_delay_seconds=delay,
                    )
                else:
                    if applied or args.once:
                        print(f"Liquidations applied: {int(applied)}", flush=True)
                    if args.once:
                        return
                time.sleep(delay)
    except KeyboardInterrupt:
        pass
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_worker(main, logger)
