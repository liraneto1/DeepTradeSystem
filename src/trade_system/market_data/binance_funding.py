"""Read finalized BTCUSDT funding from Binance public USD-M market data."""

import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from urllib.parse import urlencode
from urllib.request import urlopen

from trade_system.market_data.binance_archive import MAX_BYTES, SYMBOL
from trade_system.market_data.binance_stream import epoch_ms
from trade_system.market_data.klines import DECIMAL_TEXT, EPOCH
from trade_system.risk.futures import FundingObservation

URL = "https://fapi.binance.com/fapi/v1/fundingRate"
PAGE_SIZE = 1000


def fetch_funding_page(
    start_ms: int,
    end_ms: int,
    *,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> list[FundingObservation]:
    query = urlencode(
        {"symbol": SYMBOL, "startTime": start_ms, "endTime": end_ms, "limit": PAGE_SIZE}
    )
    with urlopen(f"{URL}?{query}", timeout=15) as response:
        raw = response.read(MAX_BYTES + 1)
        received_at = now()
    if len(raw) > MAX_BYTES:
        raise ValueError("funding: oversized_response")
    rows = json.loads(raw)
    if not isinstance(rows, list) or len(rows) > PAGE_SIZE:
        raise ValueError("funding: invalid_response")

    result: list[FundingObservation] = []
    previous_ms = start_ms - 1
    for row in rows:
        if not isinstance(row, dict) or row.get("symbol") != SYMBOL:
            raise ValueError("funding: invalid_symbol")
        timestamp = row.get("fundingTime")
        if type(timestamp) is not int or not previous_ms < timestamp <= end_ms:
            raise ValueError("funding: invalid_timestamp_order")
        rate = row.get("fundingRate")
        mark = row.get("markPrice")
        if (
            not isinstance(rate, str)
            or not DECIMAL_TEXT.fullmatch(rate.removeprefix("-"))
            or not isinstance(mark, str)
            or not DECIMAL_TEXT.fullmatch(mark)
        ):
            raise ValueError("funding: invalid_decimal")
        observation = FundingObservation(
            EPOCH + timedelta(milliseconds=timestamp),
            received_at,
            Decimal(mark),
            Decimal(rate),
            f"{URL}?symbol={SYMBOL}&startTime={timestamp}&endTime={timestamp}",
        )
        observation.validate(received_at)
        result.append(observation)
        previous_ms = epoch_ms(observation.funding_at)
    return result
