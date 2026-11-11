from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from trade_system.control.paper import ControlPolicy, TradingIntent
from trade_system.execution.paper import PaperSimulator
from trade_system.risk.execution_costs import ExecutionCosts
from trade_system.risk.futures import FuturesBalance, assess_futures
from trade_system.risk.paper import PaperBalance, RiskLimits, SyntheticQuote

NOW = datetime(2025, 11, 10, tzinfo=UTC)
INTENT = TradingIntent(
    "intent-1",
    "corr-1",
    "paper-test",
    "actor-test",
    "PAPER",
    "BTCUSDT",
    "BUY",
    Decimal("0.01"),
    NOW,
    NOW + timedelta(seconds=5),
)
QUOTE = SyntheticQuote("fixture-quote-1", "BTCUSDT", Decimal("10000.12345678"), NOW)
CONTROL = ControlPolicy("paper-test", frozenset({"actor-test"}), paused=False)
LIMITS = RiskLimits(Decimal("200"), Decimal("0.02"), timedelta(seconds=2))
INITIAL = PaperBalance(Decimal("1000"), Decimal("0"))


def test_paper_buy_sell_and_replay_use_exact_balances() -> None:
    simulator = PaperSimulator(CONTROL, LIMITS, INITIAL)
    fill = simulator.submit(INTENT, QUOTE, NOW)
    assert fill.notional == Decimal("100.0012345678")
    assert fill.correlation_id == "corr-1"
    assert fill.quote_reference == "fixture-quote-1"
    assert fill.balance_after == PaperBalance(
        Decimal("899.9987654322"), Decimal("0.01")
    )
    assert simulator.submit(INTENT, QUOTE, NOW) == fill
    assert simulator.balance == fill.balance_after
    with pytest.raises(ValueError, match="conflicting_intent_id"):
        simulator.submit(replace(INTENT, quantity=Decimal("0.005")), QUOTE, NOW)
    simulator.submit(replace(INTENT, intent_id="intent-2", side="SELL"), QUOTE, NOW)
    assert simulator.balance == INITIAL


@pytest.mark.parametrize("environment", ["LIVE", "TRAINING", ""])
def test_control_blocks_non_paper_before_risk(environment: str) -> None:
    simulator = PaperSimulator(CONTROL, LIMITS, INITIAL)
    with pytest.raises(ValueError, match="control: paper_required"):
        simulator.submit(
            replace(INTENT, environment_id=environment, quantity=Decimal(0)), QUOTE, NOW
        )
    assert simulator.balance == INITIAL


@pytest.mark.parametrize(
    ("policy", "intent", "reason"),
    [
        (replace(CONTROL, paused=True), INTENT, "paused"),
        (CONTROL, replace(INTENT, actor_id="unknown"), "unauthorized"),
        (CONTROL, replace(INTENT, account_id="different"), "unauthorized"),
        (CONTROL, replace(INTENT, expires_at=NOW), "intent_outside_validity"),
    ],
)
def test_control_rejections_preserve_balance(
    policy: ControlPolicy, intent: TradingIntent, reason: str
) -> None:
    simulator = PaperSimulator(policy, LIMITS, INITIAL)
    with pytest.raises(ValueError, match=f"control: {reason}"):
        simulator.submit(intent, QUOTE, NOW)
    assert simulator.balance == INITIAL


@pytest.mark.parametrize(
    ("limits", "balance", "intent", "quote", "reason"),
    [
        (
            replace(LIMITS, max_order_notional=Decimal(99)),
            INITIAL,
            INTENT,
            QUOTE,
            "order_limit",
        ),
        (
            replace(LIMITS, max_position_quantity=Decimal("0.005")),
            INITIAL,
            INTENT,
            QUOTE,
            "position_limit",
        ),
        (
            LIMITS,
            PaperBalance(Decimal(99), Decimal(0)),
            INTENT,
            QUOTE,
            "insufficient_cash",
        ),
        (LIMITS, INITIAL, replace(INTENT, side="SELL"), QUOTE, "insufficient_position"),
        (
            LIMITS,
            INITIAL,
            INTENT,
            replace(QUOTE, observed_at=NOW - timedelta(seconds=3)),
            "invalid_or_stale_quote",
        ),
        (
            LIMITS,
            INITIAL,
            replace(INTENT, quantity=Decimal("NaN")),
            QUOTE,
            "invalid_quantity_price_or_limit",
        ),
    ],
)
def test_risk_rejections_preserve_balance(
    limits: RiskLimits,
    balance: PaperBalance,
    intent: TradingIntent,
    quote: SyntheticQuote,
    reason: str,
) -> None:
    simulator = PaperSimulator(CONTROL, limits, balance)
    with pytest.raises(ValueError, match=f"risk: {reason}"):
        simulator.submit(intent, quote, NOW)
    assert simulator.balance == balance


def test_futures_short_position_limit_does_not_round_quantity() -> None:
    quantity = Decimal("0.010000000000000000000000000000001")
    limits = replace(LIMITS, max_position_quantity=Decimal("0.01"))
    with pytest.raises(ValueError, match="risk: position_limit"):
        assess_futures(
            replace(INTENT, side="SELL", quantity=quantity),
            replace(QUOTE, price=Decimal(1)),
            FuturesBalance(Decimal(1000)),
            limits,
            ExecutionCosts(),
            NOW,
            reduce_only=False,
        )
