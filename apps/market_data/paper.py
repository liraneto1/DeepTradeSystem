"""Price a PAPER Spot intent from a point-in-time BTCUSDT Market State."""

from datetime import UTC, datetime
from decimal import Decimal
from typing import cast

from apps.market_data.state import read_state
from infrastructure.database.paper_ledger import PaperLedger, market_state_reference
from trade_system.control.paper import TradingIntent
from trade_system.execution.paper import PaperFill
from trade_system.risk.paper import SyntheticQuote


def submit_market_intent(
    ledger: PaperLedger, intent: TradingIntent, *, close_at: datetime, now: datetime
) -> PaperFill:
    if close_at.utcoffset() is None:
        raise ValueError("market_state: timezone_required")
    close_at = close_at.astimezone(UTC)

    def price() -> tuple[SyntheticQuote, dict[str, object]]:
        state = read_state(
            "spot", close_at, intent.issued_at.astimezone(UTC), extended=True
        )
        intervals = cast(dict[str, dict[str, object]], state["intervals"])
        features = cast(dict[str, str | None], intervals["5m"]["features"])
        closing_price = features["close"]
        if closing_price is None:
            raise ValueError("market_state: closing_price_required")
        quote = SyntheticQuote(
            market_state_reference(state),
            intent.symbol,
            Decimal(closing_price),
            close_at,
        )
        return quote, state

    return ledger.submit_with_quote_provider(
        intent, now, price, pricing_close_at=close_at.isoformat()
    )
