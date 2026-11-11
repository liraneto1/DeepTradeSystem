"""Build a diagnostic market snapshot with point-in-time lineage."""

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime, timedelta

from trade_system.features.candles import FEATURE_VERSION, Candle, calculate
from trade_system.market_data.klines import EPOCH, INTERVAL_MINUTES

STATE_INTERVALS = ("1m", "5m", "15m", "1h")


def closing_times(decision_at: datetime, as_of: datetime) -> dict[str, datetime]:
    if decision_at.tzinfo is None or as_of.tzinfo is None or decision_at > as_of:
        raise ValueError("Use timezone-aware cutoffs with close_at <= as_of.")
    decision_at = decision_at.astimezone(UTC)
    if (decision_at - EPOCH) % timedelta(minutes=5):
        raise ValueError("The decision must align with a five-minute UTC close.")
    return {
        interval: decision_at
        - (decision_at - EPOCH) % timedelta(minutes=INTERVAL_MINUTES[interval])
        for interval in STATE_INTERVALS
    }


def build_state(
    candles: Sequence[Candle],
    *,
    market: str,
    close_at: datetime,
    as_of: datetime,
    interval: str = "5m",
) -> dict[str, object]:
    if close_at.tzinfo is None or as_of.tzinfo is None or close_at > as_of:
        raise ValueError("Use timezone-aware cutoffs with close_at <= as_of.")
    if any(item.closed_at > close_at or item.available_at > as_of for item in candles):
        raise ValueError("A candle exceeds the event-time or availability cutoff.")
    values = calculate(candles, step=timedelta(minutes=INTERVAL_MINUTES[interval]))
    if candles[-1].closed_at != close_at:
        raise ValueError("The requested closing candle is unavailable.")

    return {
        "schema_version": "1.0.0",
        "feature_version": FEATURE_VERSION,
        "market": market,
        "symbol": "BTCUSDT",
        "interval": interval,
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


def build_multi_state(
    windows: Mapping[str, Sequence[Candle]],
    *,
    market: str,
    close_at: datetime,
    as_of: datetime,
) -> dict[str, object]:
    cutoffs = closing_times(close_at, as_of)
    intervals: dict[str, dict[str, object]] = {}
    for interval, cutoff in cutoffs.items():
        try:
            state = build_state(
                windows.get(interval, ()),
                market=market,
                close_at=cutoff,
                as_of=as_of,
                interval=interval,
            )
        except ValueError as error:
            raise ValueError(f"{interval}: {error}") from error
        intervals[interval] = {
            field: state[field] for field in ("close_at", "features", "lineage")
        }

    return {
        "schema_version": "2.0.0",
        "feature_version": FEATURE_VERSION,
        "market": market,
        "symbol": "BTCUSDT",
        "close_at": close_at.astimezone(UTC).isoformat(),
        "as_of": as_of.astimezone(UTC).isoformat(),
        "intervals": intervals,
    }
