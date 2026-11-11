from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from trade_system.features.candles import STEP, WINDOW, Candle, calculate
from trade_system.market_state.snapshot import (
    build_multi_state,
    build_state,
    closing_times,
)

START = datetime(2025, 11, 10, tzinfo=UTC)
CLOSE = START + WINDOW * STEP


def window() -> list[Candle]:
    return [
        Candle(
            START + index * STEP,
            START + (index + 1) * STEP,
            Decimal(101),
            Decimal(99),
            Decimal(100),
            Decimal(20 if index == 20 else 10),
            CLOSE,
            {"kind": "fixture"},
        )
        for index in range(WINDOW)
    ]


def test_versioned_features_and_lineage() -> None:
    state = build_state(window(), market="spot", close_at=CLOSE, as_of=CLOSE)
    assert state["features"] == {
        "close": "100",
        "return_1": "0",
        "sma_20": "100",
        "atr_sma_14": "2",
        "relative_volume_20": "2",
    }
    assert len(state["lineage"]) == WINDOW  # type: ignore[arg-type]


def test_rejects_late_candles_and_gaps() -> None:
    candles = window()
    candles[-1] = replace(candles[-1], available_at=CLOSE + STEP)
    with pytest.raises(ValueError, match="availability cutoff"):
        build_state(candles, market="spot", close_at=CLOSE, as_of=CLOSE)
    candles = window()
    candles[10] = candles[9]
    with pytest.raises(ValueError, match="contiguous"):
        build_state(candles, market="spot", close_at=CLOSE, as_of=CLOSE)


def test_multi_interval_uses_only_aligned_and_available_candles() -> None:
    decision = datetime(2025, 11, 10, 22, 35, tzinfo=UTC)
    cutoffs = closing_times(decision, decision)
    assert [value.strftime("%H:%M") for value in cutoffs.values()] == [
        "22:35",
        "22:35",
        "22:30",
        "22:00",
    ]
    windows = {}
    for (interval, cutoff), minutes in zip(
        cutoffs.items(), (1, 5, 15, 60), strict=True
    ):
        step = timedelta(minutes=minutes)
        windows[interval] = [
            replace(
                candle,
                opened_at=cutoff - (WINDOW - index) * step,
                closed_at=cutoff - (WINDOW - index - 1) * step,
            )
            for index, candle in enumerate(window())
        ]
    state = build_multi_state(windows, market="spot", close_at=decision, as_of=decision)
    assert state["schema_version"] == "2.0.0"
    assert state["intervals"] == {
        interval: {key: substate[key] for key in ("close_at", "features", "lineage")}
        for interval, cutoff in cutoffs.items()
        for substate in [
            build_state(
                windows[interval],
                market="spot",
                close_at=cutoff,
                as_of=decision,
                interval=interval,
            )
        ]
    }
    windows["1h"][-1] = replace(windows["1h"][-1], available_at=decision + STEP)
    with pytest.raises(ValueError, match="1h: .*availability cutoff"):
        build_multi_state(windows, market="spot", close_at=decision, as_of=decision)
    with pytest.raises(ValueError, match="five-minute UTC"):
        closing_times(decision - timedelta(minutes=1), decision)


def test_extended_features_known_values() -> None:
    candles = window()
    candles[-1] = replace(
        candles[-1],
        high=Decimal(130),
        low=Decimal(120),
        close=Decimal(125),
        taker_buy_volume=Decimal(15),
    )
    values = calculate(candles, extended=True)
    assert values["momentum_return_5"] == "0.25"
    assert values["rsi_sma_14"] == "100"
    assert values["range_over_close"] == "0.08"
    assert values["taker_buy_fraction"] == "0.75"
    assert "momentum_return_5" not in calculate(candles)


def test_extended_features_handle_flat_losses_and_empty_volume() -> None:
    candles = window()
    candles[-1] = replace(candles[-1], volume=Decimal(0), taker_buy_volume=Decimal(0))
    flat = calculate(candles, extended=True)
    assert flat["rsi_sma_14"] == "50"
    assert flat["taker_buy_fraction"] is None
    candles[-1] = replace(candles[-1], close=Decimal(99))
    assert calculate(candles, extended=True)["rsi_sma_14"] == "0"
