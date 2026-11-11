"""Normalize and validate one UTC day of Binance candles."""

import csv
import re
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from io import StringIO

INTERVAL_MINUTES = {"1m": 1, "5m": 5, "15m": 15, "1h": 60}
HEADER = (
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "count",
    "taker_buy_volume",
    "taker_buy_quote_volume",
    "ignore",
)
NORMALIZED_HEADER = (
    "open_time_utc",
    "close_time_exclusive_utc",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "trade_count",
    "taker_buy_volume",
    "taker_buy_quote_volume",
)
EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
MICROSECOND_START = date(2025, 1, 1)
DECIMAL_TEXT = re.compile(r"[0-9]+(?:\.[0-9]+)?")
INTEGER_TEXT = re.compile(r"[0-9]+")


def normalize_day(
    source: bytes, day: date, interval: str, *, market: str
) -> tuple[bytes, int, str]:
    """Return normalized CSV, row count and the original timestamp unit."""
    reader = csv.reader(StringIO(source.decode("utf-8"), newline=""), strict=True)
    rows = list(reader)
    if rows and tuple(rows[0]) == HEADER:
        rows.pop(0)

    minutes = INTERVAL_MINUTES[interval]
    expected_count = 1440 // minutes
    if len(rows) != expected_count:
        raise ValueError(f"Expected {expected_count} candles, received {len(rows)}.")

    microseconds = market == "spot" and day >= MICROSECOND_START
    ticks_per_second = 1_000_000 if microseconds else 1000
    step = minutes * 60 * ticks_per_second
    midnight = datetime.combine(day, time(), tzinfo=UTC)
    start = (midnight - EPOCH).days * 86400 * ticks_per_second
    normalized = StringIO(newline="")
    writer = csv.writer(normalized, lineterminator="\n")
    writer.writerow(NORMALIZED_HEADER)

    for index, row in enumerate(rows):
        position = index + 1
        if len(row) != len(HEADER):
            raise ValueError(f"Candle {position}: unexpected number of fields.")
        (
            opened,
            open_,
            high,
            low,
            close,
            volume,
            closed,
            quote,
            trades,
            buy,
            buy_quote,
            _,
        ) = row
        expected_open = start + index * step
        if (
            not INTEGER_TEXT.fullmatch(opened)
            or not INTEGER_TEXT.fullmatch(closed)
            or int(opened) != expected_open
            or int(closed) != expected_open + step - 1
        ):
            raise ValueError(
                f"Candle {position}: gap, duplicate, order or timestamp mismatch."
            )

        values = (open_, high, low, close, volume, quote, buy, buy_quote)
        if not all(DECIMAL_TEXT.fullmatch(value) for value in values):
            raise ValueError(f"Candle {position}: invalid decimal field.")
        opening, highest, lowest, closing, total, total_quote, taker, taker_quote = map(
            Decimal, values
        )
        if not (
            0 < lowest <= min(opening, closing) <= max(opening, closing) <= highest
            and taker <= total
            and taker_quote <= total_quote
        ):
            raise ValueError(f"Candle {position}: inconsistent OHLCV values.")
        if not INTEGER_TEXT.fullmatch(trades):
            raise ValueError(f"Candle {position}: invalid trade count.")

        opened_at = midnight + timedelta(minutes=index * minutes)
        closed_at = opened_at + timedelta(minutes=minutes)
        writer.writerow(
            (
                opened_at.isoformat(),
                closed_at.isoformat(),
                *values[:6],
                trades,
                buy,
                buy_quote,
            )
        )

    return (
        normalized.getvalue().encode("utf-8"),
        expected_count,
        ("microseconds" if microseconds else "milliseconds"),
    )
