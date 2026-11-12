import json
from datetime import timedelta
from decimal import Decimal
from io import BytesIO

import pytest

from trade_system.market_data.binance_mark import (
    HISTORY_URL,
    URL,
    fetch_mark,
    fetch_mark_history,
)
from trade_system.market_data.klines import EPOCH


def test_mark_records_observation_and_receipt(monkeypatch: pytest.MonkeyPatch) -> None:
    row = {"symbol": "BTCUSDT", "time": 1000, "markPrice": "16000.10"}
    received = EPOCH + timedelta(seconds=2)

    def response(url: str, timeout: int) -> BytesIO:
        assert url == URL and timeout == 15
        return BytesIO(json.dumps(row).encode())

    monkeypatch.setattr("trade_system.market_data.binance_mark.urlopen", response)
    mark = fetch_mark(now=lambda: received)
    assert mark.observed_at == EPOCH + timedelta(seconds=1)
    assert mark.available_at == received
    assert mark.price == Decimal("16000.10") and mark.reference == URL

    row["symbol"] = "ETHUSDT"
    with pytest.raises(ValueError, match="invalid_symbol"):
        fetch_mark(now=lambda: received)


def test_mark_history_uses_exclusive_end_and_records_receipt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    start = EPOCH + timedelta(minutes=1)
    end = start + timedelta(minutes=1)
    received = end + timedelta(seconds=3)
    row = [60000, "100", "110", "90", "105", "0", 119999, "0", 0, "0", "0", "0"]

    def response(url: str, timeout: int) -> BytesIO:
        assert url.startswith(HISTORY_URL)
        assert "startTime=60000&endTime=119999" in url
        return BytesIO(json.dumps([row]).encode())

    monkeypatch.setattr("trade_system.market_data.binance_mark.urlopen", response)
    [candle] = fetch_mark_history(start, end, now=lambda: received)
    assert candle.closed_at == end and candle.available_at == received
    assert candle.closing == Decimal(105)
    row[6] = 120000
    with pytest.raises(ValueError, match="invalid_candle"):
        fetch_mark_history(start, end, now=lambda: received)
