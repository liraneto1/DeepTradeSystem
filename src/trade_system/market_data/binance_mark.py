"""Read the current public BTCUSDT USD-M mark price."""

import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from urllib.request import urlopen

from trade_system.market_data.binance_archive import MAX_BYTES, SYMBOL
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
