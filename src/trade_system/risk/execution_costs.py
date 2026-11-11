"""Deterministic costs for synthetic Spot fills, expressed in basis points."""

from dataclasses import dataclass
from decimal import Decimal, Inexact, localcontext

from trade_system.control.paper import Side

BASIS_POINTS = Decimal(10000)


@dataclass(frozen=True)
class ExecutionCosts:
    fee_bps: Decimal = Decimal(0)
    slippage_bps: Decimal = Decimal(0)

    def __post_init__(self) -> None:
        if (
            not self.fee_bps.is_finite()
            or not self.slippage_bps.is_finite()
            or not 0 <= self.fee_bps <= BASIS_POINTS
            or not 0 <= self.slippage_bps < BASIS_POINTS
        ):
            raise ValueError("risk: invalid_execution_costs")


def execution_price_and_fee(
    side: Side, reference: Decimal, quantity: Decimal, costs: ExecutionCosts
) -> tuple[Decimal, Decimal]:
    if any(not value.is_finite() or value <= 0 for value in (reference, quantity)):
        raise ValueError("risk: invalid_quantity_price_or_limit")

    with localcontext() as context:
        context.prec = 50
        context.traps[Inexact] = True
        slippage = costs.slippage_bps / BASIS_POINTS
        multiplier = 1 + slippage if side == "BUY" else 1 - slippage
        price = reference * multiplier
        fee = price * quantity * costs.fee_bps / BASIS_POINTS
        return price, fee
