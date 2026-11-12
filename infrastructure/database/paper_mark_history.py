"""Recover closed mark candles with point-in-time availability in PAPER."""

from collections.abc import Callable
from dataclasses import asdict
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.engine import Engine

from infrastructure.database.paper_ledger import require_paper
from trade_system.market_data.binance_mark import (
    MINUTE,
    PAGE_SIZE,
    MarkCandle,
    fetch_mark_history,
)
from trade_system.market_data.klines import EPOCH


class IncompleteMarkHistory(ConnectionError):
    """The source has not returned every closed candle in the requested page."""


def recover_mark_history(
    engine: Engine,
    start: datetime,
    *,
    fetch: Callable[[datetime, datetime], list[MarkCandle]] = fetch_mark_history,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> datetime:
    require_paper()
    cutoff = now()
    if (
        start.utcoffset() is None
        or cutoff.utcoffset() is None
        or start < EPOCH
        or (start - EPOCH) % MINUTE
    ):
        raise ValueError("mark_history: invalid_cutoff")
    end = EPOCH + ((cutoff - EPOCH) // MINUTE) * MINUTE
    while start < end:
        stop = min(start + PAGE_SIZE * MINUTE, end)
        expected = [start + i * MINUTE for i in range((stop - start) // MINUTE)]
        with engine.connect() as connection:
            known: set[datetime] = set(
                connection.execute(
                    text("""
                SELECT opened_at FROM trade_system.paper_mark_candle
                WHERE opened_at >= :start AND opened_at < :stop
                """),
                    {"start": start, "stop": stop},
                ).scalars()
            )
        missing = next((opened for opened in expected if opened not in known), None)
        if missing is not None:
            candles = fetch(missing, stop)
            if [candle.opened_at for candle in candles] != expected[
                expected.index(missing) :
            ]:
                raise IncompleteMarkHistory("mark_history: incomplete_page")
            received_cutoff = now()
            if any(
                candle.available_at.utcoffset() is None
                or candle.closed_at != candle.opened_at + MINUTE
                or not candle.closed_at <= candle.available_at <= received_cutoff
                for candle in candles
            ):
                raise ValueError("mark_history: invalid_availability")
            with engine.begin() as connection:
                for candle in candles:
                    saved = connection.execute(
                        text("""
                        INSERT INTO trade_system.paper_mark_candle AS saved
                        (opened_at, closed_at, available_at, opening, high, low,
                         closing, source)
                        VALUES (:opened_at, :closed_at, :available_at, :opening,
                                :high, :low, :closing, :source)
                        ON CONFLICT (opened_at) DO UPDATE SET source = saved.source
                        WHERE (saved.opening, saved.high, saved.low, saved.closing,
                               saved.source) =
                              (excluded.opening, excluded.high, excluded.low,
                               excluded.closing, excluded.source)
                        RETURNING opened_at
                        """),
                        asdict(candle),
                    ).scalar_one_or_none()
                    if saved is None:
                        raise ValueError("mark_history: conflicting_candle")
        start = stop
    return start


def read_mark_history(
    engine: Engine, start: datetime, end: datetime, *, as_of: datetime
) -> list[MarkCandle]:
    require_paper()
    if any(value.utcoffset() is None for value in (start, end, as_of)):
        raise ValueError("mark_history: invalid_cutoff")
    with engine.connect() as connection:
        rows = connection.execute(
            text("""
            SELECT * FROM trade_system.paper_mark_candle
            WHERE opened_at >= :start AND closed_at <= :end AND available_at <= :as_of
            ORDER BY opened_at
            """),
            {"start": start, "end": end, "as_of": as_of},
        ).mappings()
        return [MarkCandle(**row) for row in rows]
