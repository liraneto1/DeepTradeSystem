"""Versioned features for a window of closed five-minute candles."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, localcontext

WINDOW = 21
STEP = timedelta(minutes=5)
FEATURE_VERSION = "1.0.0"


@dataclass(frozen=True)
class Candle:
    opened_at: datetime
    closed_at: datetime
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    available_at: datetime
    source: dict[str, str]


def calculate(candles: Sequence[Candle]) -> dict[str, str | None]:
    if len(candles) != WINDOW:
        raise ValueError("Market State requires 21 available closed candles.")
    for index, candle in enumerate(candles):
        if candle.closed_at - candle.opened_at != STEP or (
            index > 0 and candles[index - 1].closed_at != candle.opened_at
        ):
            raise ValueError("Market State requires a contiguous five-minute window.")

    last = candles[-1]
    with localcontext() as context:
        context.prec = 34
        previous_volume = sum((item.volume for item in candles[:-1]), Decimal(0)) / 20
        true_ranges = [
            max(
                current.high - current.low,
                abs(current.high - previous.close),
                abs(current.low - previous.close),
            )
            for previous, current in zip(candles[-15:-1], candles[-14:], strict=True)
        ]
        return {
            "close": format(last.close, "f"),
            "return_1": format(last.close / candles[-2].close - 1, "f"),
            "sma_20": format(sum(item.close for item in candles[-20:]) / 20, "f"),
            "atr_sma_14": format(sum(true_ranges) / 14, "f"),
            "relative_volume_20": (
                format(last.volume / previous_volume, "f") if previous_volume else None
            ),
        }
