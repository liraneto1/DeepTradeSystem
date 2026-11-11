"""Versioned features for a window of closed five-minute candles."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, localcontext

WINDOW = 21
STEP = timedelta(minutes=5)
FEATURE_VERSION = "1.0.0"
EXTENDED_FEATURE_VERSION = "1.1.0"


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
    taker_buy_volume: Decimal | None = None


def calculate(
    candles: Sequence[Candle], *, step: timedelta = STEP, extended: bool = False
) -> dict[str, str | None]:
    if len(candles) != WINDOW:
        raise ValueError("Market State requires 21 available closed candles.")
    for index, candle in enumerate(candles):
        if candle.closed_at - candle.opened_at != step or (
            index > 0 and candles[index - 1].closed_at != candle.opened_at
        ):
            raise ValueError("Market State requires a contiguous candle window.")

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
        values: dict[str, str | None] = {
            "close": format(last.close, "f"),
            "return_1": format(last.close / candles[-2].close - 1, "f"),
            "sma_20": format(sum(item.close for item in candles[-20:]) / 20, "f"),
            "atr_sma_14": format(sum(true_ranges) / 14, "f"),
            "relative_volume_20": (
                format(last.volume / previous_volume, "f") if previous_volume else None
            ),
        }
        if extended:
            changes = [
                current.close - previous.close
                for previous, current in zip(
                    candles[-15:-1], candles[-14:], strict=True
                )
            ]
            gain = sum((max(change, Decimal(0)) for change in changes), Decimal(0))
            loss = sum((max(-change, Decimal(0)) for change in changes), Decimal(0))
            rsi = 100 * gain / (gain + loss) if gain + loss else Decimal(50)
            buy_volume = last.taker_buy_volume
            values.update(
                momentum_return_5=format(last.close / candles[-6].close - 1, "f"),
                rsi_sma_14=format(rsi, "f"),
                range_over_close=format((last.high - last.low) / last.close, "f"),
                taker_buy_fraction=(
                    format(buy_volume / last.volume, "f")
                    if buy_volume is not None and last.volume
                    else None
                ),
            )
        return values
