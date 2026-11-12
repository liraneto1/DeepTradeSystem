"""Read the current public BTCUSDT USD-M mark price."""

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from urllib.parse import urlencode
from urllib.request import urlopen

from trade_system.market_data.binance_archive import MAX_BYTES, SYMBOL
from trade_system.market_data.binance_stream import epoch_ms
from trade_system.market_data.klines import DECIMAL_TEXT, EPOCH
from trade_system.risk.futures import LiquidationMark

URL = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={SYMBOL}"


def fetch_mark(
    *, now: Callable[[], datetime] = lambda: datetime.now(UTC)
) -> LiquidationMark:
    with urlopen(URL, timeout=15) as response:
        raw = response.read(MAX_BYTES + 1)
        received_at = now()
    if len(raw) > MAX_BYTES:
        raise ValueError("mark_price: oversized_response")
    row = json.loads(raw)
    if not isinstance(row, dict) or row.get("symbol") != SYMBOL:
        raise ValueError("mark_price: invalid_symbol")
    timestamp = row.get("time")
    price = row.get("markPrice")
    if type(timestamp) is not int or timestamp <= 0:
        raise ValueError("mark_price: invalid_timestamp")
    if not isinstance(price, str) or not DECIMAL_TEXT.fullmatch(price):
        raise ValueError("mark_price: invalid_decimal")
    return LiquidationMark(
        EPOCH + timedelta(milliseconds=timestamp), received_at, Decimal(price), URL
    )


HISTORY_URL = "https://fapi.binance.com/fapi/v1/markPriceKlines"
MINUTE = timedelta(minutes=1)
PAGE_SIZE = 500


@dataclass(frozen=True)
class MarkCandle:
    opened_at: datetime
    closed_at: datetime
    available_at: datetime
    opening: Decimal
    high: Decimal
    low: Decimal
    closing: Decimal
    source: str


def fetch_mark_history(
    start: datetime,
    end: datetime,
    *,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> list[MarkCandle]:
    query = urlencode(
        {
            "symbol": SYMBOL,
            "interval": "1m",
            "startTime": epoch_ms(start),
            "endTime": epoch_ms(end) - 1,
            "limit": PAGE_SIZE,
        }
    )
    with urlopen(f"{HISTORY_URL}?{query}", timeout=15) as response:
        raw = response.read(MAX_BYTES + 1)
        received_at = now()
    if len(raw) > MAX_BYTES:
        raise ValueError("mark_history: oversized_response")
    rows = json.loads(raw)
    if not isinstance(rows, list) or len(rows) > PAGE_SIZE:
        raise ValueError("mark_history: invalid_response")
    candles: list[MarkCandle] = []
    for row in rows:
        if (
            not isinstance(row, list)
            or len(row) != 12
            or type(row[0]) is not int
            or type(row[6]) is not int
            or row[6] - row[0] != 59999
        ):
            raise ValueError("mark_history: invalid_candle")
        opened_at = EPOCH + timedelta(milliseconds=row[0])
        closed_at = opened_at + MINUTE
        if not start <= opened_at < closed_at <= end:
            raise ValueError("mark_history: outside_window")
        if not all(isinstance(v, str) and DECIMAL_TEXT.fullmatch(v) for v in row[1:5]):
            raise ValueError("mark_history: invalid_decimal")
        opening, high, low, closing = (Decimal(v) for v in row[1:5])
        if not 0 < low <= min(opening, closing) <= max(opening, closing) <= high:
            raise ValueError("mark_history: invalid_ohlc")
        candles.append(
            MarkCandle(
                opened_at,
                closed_at,
                received_at,
                opening,
                high,
                low,
                closing,
                HISTORY_URL,
            )
        )
    return candles
