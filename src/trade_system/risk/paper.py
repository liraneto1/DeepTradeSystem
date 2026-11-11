"""Bound synthetic Spot fills by explicit PAPER risk limits."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, Inexact, localcontext

from trade_system.control.paper import TradingIntent


@dataclass(frozen=True)
class PaperBalance:
    cash: Decimal
    quantity: Decimal


@dataclass(frozen=True)
class SyntheticQuote:
    reference: str
    symbol: str
    price: Decimal
    observed_at: datetime


@dataclass(frozen=True)
class RiskLimits:
    max_order_notional: Decimal
    max_position_quantity: Decimal
    max_quote_age: timedelta


def assess(
    intent: TradingIntent,
    quote: SyntheticQuote,
    balance: PaperBalance,
    limits: RiskLimits,
    now: datetime,
    *,
    fee: Decimal = Decimal(0),
) -> tuple[Decimal, PaperBalance]:
    positive = (
        intent.quantity,
        quote.price,
        limits.max_order_notional,
        limits.max_position_quantity,
    )
    if any(not value.is_finite() or value <= 0 for value in positive):
        raise ValueError("risk: invalid_quantity_price_or_limit")
    if any(
        not value.is_finite() or value < 0 for value in (balance.cash, balance.quantity)
    ):
        raise ValueError("risk: invalid_balance")
    if (
        not quote.reference.strip()
        or quote.symbol != intent.symbol
        or quote.observed_at.utcoffset() is None
        or limits.max_quote_age <= timedelta(0)
        or not timedelta(0) <= now - quote.observed_at <= limits.max_quote_age
    ):
        raise ValueError("risk: invalid_or_stale_quote")

    with localcontext() as context:
        context.prec = 50
        context.traps[Inexact] = True
        notional = intent.quantity * quote.price
        if not fee.is_finite() or not 0 <= fee <= notional:
            raise ValueError("risk: invalid_fee")
        if notional > limits.max_order_notional:
            raise ValueError("risk: order_limit")

        if intent.side == "BUY":
            after = PaperBalance(
                balance.cash - notional - fee, balance.quantity + intent.quantity
            )
            if after.cash < 0:
                raise ValueError("risk: insufficient_cash")
            if after.quantity > limits.max_position_quantity:
                raise ValueError("risk: position_limit")
        else:
            after = PaperBalance(
                balance.cash + notional - fee, balance.quantity - intent.quantity
            )
            if after.quantity < 0:
                raise ValueError("risk: insufficient_position")

    return notional, after
