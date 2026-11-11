from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from trade_system.features.candles import STEP, WINDOW, Candle
from trade_system.market_state.snapshot import build_state

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
