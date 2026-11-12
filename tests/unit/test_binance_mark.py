import json
from datetime import timedelta
from decimal import Decimal
from io import BytesIO

import pytest

from trade_system.market_data.binance_mark import URL, fetch_mark
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
