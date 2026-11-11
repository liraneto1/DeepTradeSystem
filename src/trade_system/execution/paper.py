"""Apply approved synthetic fills in a single local PAPER session."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, DecimalException
from threading import Lock

from trade_system.control.paper import ControlPolicy, TradingIntent, authorize
from trade_system.risk.paper import PaperBalance, RiskLimits, SyntheticQuote, assess


@dataclass(frozen=True)
class PaperFill:
    intent_id: str
    correlation_id: str
    quote_reference: str
    filled_at: datetime
    price: Decimal
    quantity: Decimal
    notional: Decimal
    balance_after: PaperBalance
    reference_price: Decimal | None = None
    fee: Decimal = Decimal(0)
    fee_bps: Decimal = Decimal(0)
    slippage_bps: Decimal = Decimal(0)


class PaperSimulator:
    def __init__(
        self, control: ControlPolicy, limits: RiskLimits, balance: PaperBalance
    ) -> None:
        self.control = control
        self.limits = limits
        self._balance = balance
        self._fills: dict[str, tuple[TradingIntent, PaperFill]] = {}
        self._lock = Lock()

    @property
    def balance(self) -> PaperBalance:
        with self._lock:
            return self._balance

    def submit(
        self, intent: TradingIntent, quote: SyntheticQuote, now: datetime
    ) -> PaperFill:
        with self._lock:
            authorize(intent, self.control, now)
            previous = self._fills.get(intent.intent_id)
            if previous is not None:
                original, fill = previous
                if original != intent:
                    raise ValueError("control: conflicting_intent_id")
                return fill

            try:
                notional, after = assess(intent, quote, self._balance, self.limits, now)
            except DecimalException as error:
                raise ValueError("risk: arithmetic_out_of_range") from error

            fill = PaperFill(
                intent.intent_id,
                intent.correlation_id,
                quote.reference,
                now,
                quote.price,
                intent.quantity,
                notional,
                after,
            )
            self._fills[intent.intent_id] = (intent, fill)
            self._balance = after
            return fill
