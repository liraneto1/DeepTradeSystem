"""Replay BTCUSDT PAPER liquidation against recovered mark candle closes."""

import argparse
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal, DecimalException

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from infrastructure.database.config import local_database_url
from infrastructure.database.paper_futures import decode_balance
from infrastructure.database.paper_ledger import require_paper
from infrastructure.telemetry import run_worker
from trade_system.risk.futures import (
    FuturesBalance,
    LiquidationMark,
    LiquidationSettlement,
    settle_liquidation,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReplayResult:
    candles_evaluated: int
    trigger: LiquidationMark | None = None
    hypothetical_settlement: LiquidationSettlement | None = None


def replay_liquidation(
    engine: Engine,
    account_id: str,
    *,
    start: datetime,
    end: datetime,
    as_of: datetime,
    maintenance_rate: Decimal,
) -> ReplayResult:
    require_paper()
    if (
        any(value.utcoffset() is None for value in (start, end, as_of))
        or not start < end <= as_of
    ):
        raise ValueError("liquidation_replay: invalid_cutoff")
    if not maintenance_rate.is_finite() or not 0 < maintenance_rate < 1:
        raise ValueError("liquidation: invalid_maintenance_rate")

    with (
        engine.connect().execution_options(
            isolation_level="REPEATABLE READ"
        ) as connection,
        connection.begin(),
    ):
        connection.execute(text("SET TRANSACTION READ ONLY"))
        opening: Decimal | None = connection.execute(
            text("""
            SELECT opening_cash FROM trade_system.paper_futures_account
            WHERE account_id = :account
            """),
            {"account": account_id},
        ).scalar_one_or_none()
        if opening is None:
            raise ValueError("control: paper_futures_account_missing")

        rows = connection.execute(
            text("""
            WITH entries AS (
                SELECT sequence_id, filled_at AS applied_at, fill->'after' AS balance
                FROM trade_system.paper_futures_fill WHERE account_id = :account
                UNION ALL
                SELECT sequence_id, applied_at, balance_after
                FROM trade_system.paper_futures_funding WHERE account_id = :account
                UNION ALL
                SELECT sequence_id, applied_at, balance_after
                FROM trade_system.paper_futures_liquidation WHERE account_id = :account
            ), snapshots AS (
                SELECT sequence_id, balance,
                       max(applied_at) OVER (ORDER BY sequence_id) AS valid_from
                FROM entries
            )
            SELECT candle.closed_at, candle.available_at, candle.closing, candle.source,
                   snapshot.balance
            FROM trade_system.paper_mark_candle AS candle
            LEFT JOIN LATERAL (
                SELECT balance FROM snapshots
                WHERE valid_from <= candle.closed_at
                ORDER BY sequence_id DESC LIMIT 1
            ) AS snapshot ON true
            WHERE candle.opened_at >= :start AND candle.closed_at <= :end
              AND candle.available_at <= :as_of
            ORDER BY candle.opened_at
            """),
            {"account": account_id, "start": start, "end": end, "as_of": as_of},
        ).mappings()
        count = 0
        for count, row in enumerate(rows, start=1):
            mark = LiquidationMark(
                row["closed_at"], row["available_at"], row["closing"], row["source"]
            )
            balance = (
                decode_balance(row["balance"])
                if row["balance"] is not None
                else FuturesBalance(opening)
            )
            try:
                settlement = settle_liquidation(balance, mark, maintenance_rate)
            except DecimalException as error:
                raise ValueError("liquidation: arithmetic_out_of_range") from error
            if settlement is not None:
                return ReplayResult(count, mark, settlement)
        return ReplayResult(count)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account", required=True)
    parser.add_argument("--start", required=True, type=datetime.fromisoformat)
    parser.add_argument("--end", required=True, type=datetime.fromisoformat)
    parser.add_argument("--as-of", required=True, type=datetime.fromisoformat)
    parser.add_argument("--maintenance-rate", required=True, type=Decimal)
    args = parser.parse_args()
    require_paper()
    engine = create_engine(
        local_database_url(), hide_parameters=True, connect_args={"connect_timeout": 5}
    )
    try:
        result = replay_liquidation(
            engine,
            args.account,
            start=args.start,
            end=args.end,
            as_of=args.as_of,
            maintenance_rate=args.maintenance_rate,
        )
        print(json.dumps(asdict(result), default=str))
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_worker(main, logger)
