"""Risk and accounting for one synthetic linear USDⓈ-M position at 1×."""

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal, Inexact, localcontext

from trade_system.control.paper import Side, TradingIntent
from trade_system.risk.execution_costs import ExecutionCosts, execution_price_and_fee
from trade_system.risk.paper import RiskLimits, SyntheticQuote

ZERO = Decimal(0)


@dataclass(frozen=True)
class FuturesBalance:
    cash: Decimal
    quantity: Decimal = ZERO
    entry_price: Decimal = ZERO
    margin: Decimal = ZERO
    realized_pnl: Decimal = ZERO


@dataclass(frozen=True)
class FuturesFill:
    price: Decimal
    notional: Decimal
    fee: Decimal
    realized_pnl: Decimal
    after: FuturesBalance


def apply_fill(
    balance: FuturesBalance,
    side: Side,
    quantity: Decimal,
    reference: Decimal,
    costs: ExecutionCosts,
    *,
    reduce_only: bool,
) -> FuturesFill:
    with localcontext() as context:
        context.prec = 50
        context.traps[Inexact] = True
        price, fee = execution_price_and_fee(side, reference, quantity, costs)
        notional = price * quantity
        signed = quantity if side == "BUY" else -quantity
        if reduce_only:
            if not balance.quantity or signed != -balance.quantity:
                raise ValueError("risk: full_reduce_only_required")
            pnl = balance.quantity * (price - balance.entry_price)
            settlement = balance.margin + pnl
            if settlement < 0:
                raise ValueError("risk: isolated_margin_exhausted")
            after = FuturesBalance(
                balance.cash + settlement - fee,
                realized_pnl=balance.realized_pnl + pnl,
            )
        else:
            if balance.quantity:
                raise ValueError("risk: position_already_open")
            pnl = ZERO
            after = FuturesBalance(
                balance.cash - notional - fee,
                signed,
                price,
                notional,
                balance.realized_pnl,
            )
        if after.cash < 0:
            raise ValueError("risk: insufficient_futures_collateral")
        return FuturesFill(price, notional, fee, pnl, after)


@dataclass(frozen=True)
class FundingObservation:
    funding_at: datetime
    available_at: datetime
    mark_price: Decimal
    rate: Decimal
    reference: str

    def validate(self, as_of: datetime) -> None:
        if (
            any(
                t.utcoffset() is None
                for t in (self.funding_at, self.available_at, as_of)
            )
            or not self.funding_at <= self.available_at <= as_of
        ):
            raise ValueError("funding: invalid_cutoff")
        if (
            not self.mark_price.is_finite()
            or self.mark_price <= 0
            or not self.rate.is_finite()
            or self.rate.copy_abs() > 1
            or not self.reference.strip()
        ):
            raise ValueError("funding: invalid_observation")


@dataclass(frozen=True)
class FundingSettlement:
    cash_delta: Decimal
    after: FuturesBalance


def settle_funding(
    balance: FuturesBalance, observation: FundingObservation
) -> FundingSettlement:
    with localcontext() as context:
        context.prec = 50
        context.traps[Inexact] = True
        delta = -balance.quantity * observation.mark_price * observation.rate
        cash = balance.cash + delta
    if cash < 0:
        raise ValueError("funding: insufficient_cash")
    return FundingSettlement(delta, replace(balance, cash=cash))


class LiquidationCutoffError(ValueError):
    """The mark cannot be used at the requested point in time."""


@dataclass(frozen=True)
class LiquidationMark:
    observed_at: datetime
    available_at: datetime
    price: Decimal
    reference: str

    def validate(self, as_of: datetime, max_age: timedelta) -> None:
        if (
            any(
                t.utcoffset() is None
                for t in (self.observed_at, self.available_at, as_of)
            )
            or not self.observed_at <= self.available_at <= as_of
            or not timedelta(0) < max_age
            or as_of - self.observed_at > max_age
        ):
            raise LiquidationCutoffError("liquidation: invalid_cutoff")
        if not self.price.is_finite() or self.price <= 0 or not self.reference.strip():
            raise ValueError("liquidation: invalid_mark")


@dataclass(frozen=True)
class LiquidationSettlement:
    isolated_equity: Decimal
    maintenance_margin: Decimal
    released_margin: Decimal
    after: FuturesBalance


def settle_liquidation(
    balance: FuturesBalance, mark: LiquidationMark, maintenance_rate: Decimal
) -> LiquidationSettlement | None:
    if not maintenance_rate.is_finite() or not 0 < maintenance_rate < 1:
        raise ValueError("liquidation: invalid_maintenance_rate")
    if not balance.quantity:
        return None
    with localcontext() as context:
        context.prec = 50
        context.traps[Inexact] = True
        equity = balance.margin + balance.quantity * (mark.price - balance.entry_price)
        required = balance.quantity.copy_abs() * mark.price * maintenance_rate
        if equity > required:
            return None
        released = max(ZERO, equity)
        after = FuturesBalance(
            balance.cash + released,
            realized_pnl=balance.realized_pnl + (released - balance.margin),
        )
        return LiquidationSettlement(equity, required, released, after)


def assess_futures(
    intent: TradingIntent,
    quote: SyntheticQuote,
    balance: FuturesBalance,
    limits: RiskLimits,
    costs: ExecutionCosts,
    now: datetime,
    *,
    reduce_only: bool,
) -> FuturesFill:
    if (
        not quote.reference.strip()
        or quote.symbol != intent.symbol
        or quote.observed_at.utcoffset() is None
        or limits.max_quote_age <= timedelta(0)
        or not timedelta(0) <= now - quote.observed_at <= limits.max_quote_age
    ):
        raise ValueError("risk: invalid_or_stale_quote")
    if any(
        not amount.is_finite() or amount <= 0
        for amount in (limits.max_order_notional, limits.max_position_quantity)
    ):
        raise ValueError("risk: invalid_futures_limits")
    fill = apply_fill(
        balance,
        intent.side,
        intent.quantity,
        quote.price,
        costs,
        reduce_only=reduce_only,
    )
    if fill.notional > limits.max_order_notional:
        raise ValueError("risk: order_limit")
    if fill.after.quantity.copy_abs() > limits.max_position_quantity:
        raise ValueError("risk: position_limit")
    return fill
