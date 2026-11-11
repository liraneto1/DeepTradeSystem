"""Download and validate daily Binance BTCUSDT candle archives."""

import argparse
import csv
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from zipfile import BadZipFile

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from infrastructure.database.config import local_database_url
from infrastructure.database.market_history import persist_history
from infrastructure.security.config import ConfigurationError, runtime_environment
from trade_system.market_data.binance_archive import MARKETS, collect_day
from trade_system.market_data.klines import INTERVAL_MINUTES


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", choices=MARKETS, required=True)
    window = parser.add_mutually_exclusive_group(required=True)
    window.add_argument("--date", type=date.fromisoformat, dest="day")
    window.add_argument("--start", type=date.fromisoformat)
    parser.add_argument("--end", type=date.fromisoformat)
    parser.add_argument("--interval", choices=INTERVAL_MINUTES, default="5m")
    parser.add_argument("--output", type=Path, default=Path("data/market-history"))
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()

    if (args.start is None) != (args.end is None):
        parser.error("--start and --end must be supplied together.")
    start: date = args.day or args.start
    end: date = args.day or args.end
    if start > end or end >= datetime.now(UTC).date():
        parser.error("Select an ordered range of completed UTC days.")

    try:
        runtime_environment()
        url = local_database_url() if args.persist else None
        manifests = []
        for offset in range((end - start).days + 1):
            manifest = collect_day(
                market=args.market,
                day=start + timedelta(days=offset),
                interval=args.interval,
                output=args.output,
            )
            manifests.append(manifest)
            print(manifest)

        if url is not None:
            engine = create_engine(
                url, hide_parameters=True, connect_args={"connect_timeout": 5}
            )
            try:
                inserted, skipped = persist_history(engine, manifests)
            finally:
                engine.dispose()
            print(f"PostgreSQL: {inserted} candles inserted, {skipped} days skipped.")
    except SQLAlchemyError as error:
        parser.exit(1, f"PostgreSQL persistence failed ({type(error).__name__}).\n")
    except (ConfigurationError, ValueError, OSError, BadZipFile, csv.Error) as error:
        parser.exit(1, f"Collection failed ({type(error).__name__}): {error}\n")


if __name__ == "__main__":
    main()
