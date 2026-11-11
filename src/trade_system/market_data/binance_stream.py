"""Read closed BTCUSDT candles from Binance public market data."""

import json
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from websockets.sync.client import connect

from trade_system.market_data.binance_archive import MAX_BYTES, SYMBOL
from trade_system.market_data.klines import DECIMAL_TEXT, EPOCH, INTERVAL_MINUTES

REST = {
    "spot": "https://data-api.binance.vision/api/v3/klines",
    "futures-um": "https://fapi.binance.com/fapi/v1/klines",
}
WS = {
    "spot": "wss://data-stream.binance.vision/ws",
    "futures-um": "wss://fstream.binance.com/market/ws",
}
PAGE_SIZE = 500


@dataclass(frozen=True)
class Observation:
    open_time: datetime
    close_time: datetime
    decimals: tuple[Decimal, ...]
    trades: int
    source_kind: str
    source_url: str
    received_at: datetime
    payload: list[object] | dict[str, object]


def epoch_ms(value: datetime) -> int:
    return (value - EPOCH) // timedelta(milliseconds=1)


class BinanceKlines:
    def __init__(self, market: str, interval: str) -> None:
        self.interval = interval
        self.step = timedelta(minutes=INTERVAL_MINUTES[interval])
        self.rest_url = REST[market]
        self.websocket_url = f"{WS[market]}/{SYMBOL.lower()}@kline_{interval}"

    def _parse(
        self,
        row: list[Any],
        *,
        kind: str,
        url: str,
        payload: list[object] | dict[str, object],
    ) -> Observation:
        if len(row) != 12 or any(type(row[index]) is not int for index in (0, 6, 8)):
            raise ValueError("Unexpected Binance kline schema.")
        start, end, trades = row[0], row[6], row[8]
        step_ms = self.step // timedelta(milliseconds=1)
        if start < 0 or start % step_ms or end != start + step_ms - 1 or trades < 0:
            raise ValueError("Invalid kline timestamps or trade count.")

        text_values = [row[index] for index in (1, 2, 3, 4, 5, 7, 9, 10)]
        if not all(
            isinstance(value, str) and DECIMAL_TEXT.fullmatch(value)
            for value in text_values
        ):
            raise ValueError("Invalid kline decimal.")
        values = tuple(Decimal(value) for value in text_values)
        opening, highest, lowest, closing, volume, quote, taker, taker_quote = values
        if not (
            0 < lowest <= min(opening, closing) <= max(opening, closing) <= highest
            and taker <= volume
            and taker_quote <= quote
        ):
            raise ValueError("Inconsistent kline OHLCV.")

        return Observation(
            EPOCH + timedelta(milliseconds=start),
            EPOCH + timedelta(milliseconds=end + 1),
            values,
            trades,
            kind,
            url,
            datetime.now(UTC),
            payload,
        )

    def parse_message(self, raw: str | bytes) -> Observation | None:
        message = json.loads(raw)
        if isinstance(message, dict) and message.get("e") == "serverShutdown":
            raise ConnectionError("Binance announced stream shutdown.")
        if not isinstance(message, dict) or message.get("e") != "kline":
            raise ValueError("Unexpected Binance stream event.")
        kline = message["k"]
        if (
            message.get("s") != SYMBOL
            or kline["s"] != SYMBOL
            or kline["i"] != self.interval
        ):
            raise ValueError("Kline symbol or interval mismatch.")
        if kline["x"] is False:
            return None
        if kline["x"] is not True:
            raise ValueError("Missing final kline flag.")
        row = [
            kline[key]
            for key in ("t", "o", "h", "l", "c", "v", "T", "q", "n", "V", "Q", "B")
        ]
        return self._parse(
            row, kind="websocket", url=self.websocket_url, payload=message
        )

    @contextmanager
    def stream(self) -> Iterator[Iterator[Observation | None]]:
        with connect(
            self.websocket_url, open_timeout=10, close_timeout=3, max_size=MAX_BYTES
        ) as ws:

            def messages() -> Iterator[Observation | None]:
                while True:
                    yield self.parse_message(ws.recv(timeout=45))

            yield messages()

    def backfill(self, start: datetime, end: datetime) -> list[Observation]:
        url = (
            self.rest_url
            + "?"
            + urlencode(
                {
                    "symbol": SYMBOL,
                    "interval": self.interval,
                    "startTime": epoch_ms(start),
                    "endTime": epoch_ms(end) - 1,
                    "limit": PAGE_SIZE,
                }
            )
        )
        with urlopen(url, timeout=20) as response:
            data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("Binance REST response exceeds the size limit.")
        rows = json.loads(data)
        if not isinstance(rows, list) or any(not isinstance(row, list) for row in rows):
            raise ValueError("Unexpected Binance REST response.")
        return [self._parse(row, kind="rest", url=url, payload=row) for row in rows]
