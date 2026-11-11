"""Build a diagnostic market snapshot with point-in-time lineage."""

from collections.abc import Sequence
from datetime import datetime

from trade_system.features.candles import FEATURE_VERSION, Candle, calculate


def build_state(
    candles: Sequence[Candle], *, market: str, close_at: datetime, as_of: datetime
) -> dict[str, object]:
    if close_at.tzinfo is None or as_of.tzinfo is None or close_at > as_of:
        raise ValueError("Use timezone-aware cutoffs with close_at <= as_of.")
    if any(item.closed_at > close_at or item.available_at > as_of for item in candles):
        raise ValueError("A candle exceeds the event-time or availability cutoff.")
    values = calculate(candles)
    if candles[-1].closed_at != close_at:
        raise ValueError("The requested closing candle is unavailable.")

    return {
        "schema_version": "1.0.0",
        "feature_version": FEATURE_VERSION,
        "market": market,
        "symbol": "BTCUSDT",
        "interval": "5m",
        "close_at": close_at.isoformat(),
        "as_of": as_of.isoformat(),
        "features": values,
        "lineage": [
            {
                "open_time_utc": item.opened_at.isoformat(),
                "available_at": item.available_at.isoformat(),
                **item.source,
            }
            for item in candles
        ],
    }
