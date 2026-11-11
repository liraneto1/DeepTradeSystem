import json
from datetime import timedelta
from decimal import Decimal
from io import BytesIO

import pytest

from trade_system.market_data.binance_funding import fetch_funding_page
from trade_system.market_data.klines import EPOCH


def test_funding_page_records_receipt_and_rejects_out_of_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = {
        "symbol": "BTCUSDT",
        "fundingTime": 1000,
        "fundingRate": "-0.00010000",
        "markPrice": "20000.10",
    }
    received = EPOCH + timedelta(seconds=3)

    def response(url: str, timeout: int) -> BytesIO:
        assert "symbol=BTCUSDT&startTime=1000&endTime=2000" in url
        assert timeout == 15
        return BytesIO(json.dumps([row]).encode())

    monkeypatch.setattr("trade_system.market_data.binance_funding.urlopen", response)
    [observation] = fetch_funding_page(1000, 2000, now=lambda: received)
    assert observation.available_at == received
    assert observation.funding_at == EPOCH + timedelta(seconds=1)
    assert observation.rate == Decimal("-0.0001")
    assert observation.mark_price == Decimal("20000.10")
    assert "startTime=1000&endTime=1000" in observation.reference

    row["fundingTime"] = 2001
    with pytest.raises(ValueError, match="invalid_timestamp_order"):
        fetch_funding_page(1000, 2000, now=lambda: received)
