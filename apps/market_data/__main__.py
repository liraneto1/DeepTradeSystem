"""Download and validate a daily Binance BTCUSDT candle archive."""

import argparse
import csv
from datetime import date
from pathlib import Path
from zipfile import BadZipFile

from infrastructure.security.config import ConfigurationError, runtime_environment
from trade_system.market_data.binance_archive import MARKETS, collect_day
from trade_system.market_data.klines import INTERVAL_MINUTES


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", choices=MARKETS, required=True)
    parser.add_argument("--date", type=date.fromisoformat, required=True, dest="day")
    parser.add_argument("--interval", choices=INTERVAL_MINUTES, default="5m")
    parser.add_argument("--output", type=Path, default=Path("data/market-history"))
    args = parser.parse_args()

    try:
        runtime_environment()
        manifest = collect_day(
            market=args.market, day=args.day, interval=args.interval, output=args.output
        )
    except (ConfigurationError, ValueError, OSError, BadZipFile, csv.Error) as error:
        parser.exit(1, f"Collection failed ({type(error).__name__}): {error}\n")

    print(manifest)


if __name__ == "__main__":
    main()
