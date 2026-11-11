"""Read a versioned BTCUSDT Market State from PostgreSQL."""

import argparse
import json
from datetime import UTC, datetime

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from infrastructure.database.config import local_database_url
from infrastructure.security.config import ConfigurationError
from trade_system.features.candles import WINDOW, Candle
from trade_system.market_data.binance_archive import MARKETS
from trade_system.market_state.snapshot import build_state

WINDOW_QUERY = text("""
WITH candidates AS (
    SELECT c.open_time_utc, c.close_time_exclusive_utc, c.high, c.low,
           c.close, c.volume,
           CASE WHEN s.archive_sha256 IS NOT NULL
                THEN CAST(s.manifest ->> 'available_at' AS timestamptz)
           END AS archive_at,
           o.available_at AS observation_at, o.source_kind, o.source_url,
           s.manifest ->> 'run_id' AS run_id, s.archive_sha256,
           s.manifest -> 'source' ->> 'archive_url' AS archive_url
    FROM trade_system.market_candle c
    JOIN trade_system.market_history_source s USING (market, symbol, interval, day_utc)
    LEFT JOIN trade_system.market_candle_observation o
      USING (market, symbol, interval, open_time_utc)
    WHERE c.market = :market AND c.symbol = 'BTCUSDT' AND c.interval = '5m'
      AND c.close_time_exclusive_utc <= :close_at
)
SELECT *, LEAST(archive_at, observation_at) AS available_at
FROM candidates
WHERE LEAST(archive_at, observation_at) <= :as_of
ORDER BY open_time_utc DESC
LIMIT :window
""")


def utc_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("Provide a timestamp with a UTC offset.")
    return parsed.astimezone(UTC)


def read_state(market: str, close_at: datetime, as_of: datetime) -> dict[str, object]:
    engine = create_engine(
        local_database_url(), hide_parameters=True, connect_args={"connect_timeout": 5}
    )
    try:
        with engine.connect() as connection:
            rows = (
                connection.execute(
                    WINDOW_QUERY,
                    {
                        "market": market,
                        "close_at": close_at,
                        "as_of": as_of,
                        "window": WINDOW,
                    },
                )
                .mappings()
                .all()
            )
    finally:
        engine.dispose()

    candles = []
    for row in reversed(rows):
        source = (
            {
                "kind": "archive",
                "run_id": row["run_id"],
                "sha256": row["archive_sha256"],
                "url": row["archive_url"],
            }
            if row["available_at"] == row["archive_at"]
            else {"kind": row["source_kind"], "url": row["source_url"]}
        )
        candles.append(
            Candle(
                row["open_time_utc"].astimezone(UTC),
                row["close_time_exclusive_utc"].astimezone(UTC),
                row["high"],
                row["low"],
                row["close"],
                row["volume"],
                row["available_at"].astimezone(UTC),
                source,
            )
        )
    return build_state(candles, market=market, close_at=close_at, as_of=as_of)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True, choices=MARKETS)
    parser.add_argument("--close-at", required=True, type=utc_time)
    parser.add_argument("--as-of", type=utc_time)
    args = parser.parse_args()
    try:
        print(
            json.dumps(
                read_state(args.market, args.close_at, args.as_of or datetime.now(UTC)),
                indent=2,
            )
        )
    except (ValueError, ConfigurationError) as error:
        parser.exit(1, f"Market State unavailable: {error}\n")
    except SQLAlchemyError as error:
        parser.exit(1, f"PostgreSQL read failed ({type(error).__name__}).\n")


if __name__ == "__main__":
    main()
