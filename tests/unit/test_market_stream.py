import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from io import BytesIO
from urllib.parse import parse_qs, urlsplit

import pytest

from trade_system.market_data.binance_stream import BinanceKlines, epoch_ms

OPEN = datetime(2025, 11, 10, tzinfo=UTC)
STEP = timedelta(minutes=5)
ROW = [
    epoch_ms(OPEN),
    "2.00000001",
    "3",
    "1",
    "2.5",
    "5",
    epoch_ms(OPEN + STEP) - 1,
    "10",
    3,
    "4",
    "8",
    "0",
]


@pytest.mark.parametrize("market", ["spot", "futures-um"])
def test_websocket_accepts_only_closed_matching_candles(market: str) -> None:
    feed = BinanceKlines(market, "5m")
    kline = dict(
        zip(
            ("t", "o", "h", "l", "c", "v", "T", "q", "n", "V", "Q", "B"),
            ROW,
            strict=True,
        )
    )
    kline.update({"s": "BTCUSDT", "i": "5m", "x": False})
    message = {"e": "kline", "s": "BTCUSDT", "k": kline}
    assert feed.parse_message(json.dumps(message)) is None
    kline["x"] = True
    closed = feed.parse_message(json.dumps(message))
    assert closed is not None
    assert closed.open_time == OPEN and closed.close_time == OPEN + STEP
    assert closed.decimals[0] == Decimal("2.00000001")
    assert closed.source_kind == "websocket"
    kline["i"] = "1m"
    with pytest.raises(ValueError, match="symbol or interval mismatch"):
        feed.parse_message(json.dumps(message))


def test_rest_uses_exclusive_end_and_preserves_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    feed = BinanceKlines("spot", "5m")

    def fetch(url: str, *, timeout: int) -> BytesIO:
        assert timeout == 20
        assert parse_qs(urlsplit(url).query)["endTime"] == [
            str(epoch_ms(OPEN + STEP) - 1)
        ]
        return BytesIO(json.dumps([ROW]).encode())

    monkeypatch.setattr("trade_system.market_data.binance_stream.urlopen", fetch)
    (closed,) = feed.backfill(OPEN, OPEN + STEP)
    assert closed.source_kind == "rest"
    assert closed.payload == ROW
    assert closed.close_time == OPEN + STEP
