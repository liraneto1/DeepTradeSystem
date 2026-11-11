"""Transactional persistence and reconciliation for synthetic PAPER fills."""

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, DecimalException, Inexact, localcontext
from hashlib import sha256

from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Connection, Engine, RowMapping

from infrastructure.security.config import ConfigurationError, runtime_environment
from trade_system.control.paper import ControlPolicy, TradingIntent, authorize
from trade_system.execution.paper import PaperFill
from trade_system.risk.paper import PaperBalance, RiskLimits, SyntheticQuote, assess

LOCK_ACCOUNT = text("""
SELECT opening_cash, opening_quantity, cash, quantity
FROM trade_system.paper_account WHERE account_id = :account FOR UPDATE
""")
FILL_FIELDS = """
intent_id, correlation_id, quote_reference, filled_at, price, quantity, notional,
cash_after, quantity_after
"""
INSERT_FILL = text("""
INSERT INTO trade_system.paper_fill
(account_id, intent_id, intent, side, correlation_id, quote_reference, filled_at,
 price, quantity, notional, cash_after, quantity_after, market_state)
VALUES (:account, :intent_id, :intent, :side, :correlation, :quote, :at,
        :price, :quantity, :notional, :cash_after, :quantity_after, :market_state)
""").bindparams(
    bindparam("intent", type_=JSONB),
    bindparam("market_state", type_=JSONB(none_as_null=True)),
)


@dataclass(frozen=True)
class Reconciliation:
    fills: int
    expected: PaperBalance
    stored: PaperBalance
    first_divergent_fill: str | None

    @property
    def consistent(self) -> bool:
        return self.first_divergent_fill is None and self.expected == self.stored


def market_state_reference(state: dict[str, object]) -> str:
    digest = sha256(json.dumps(state, sort_keys=True, separators=(",", ":")).encode())
    return f"market-state:sha256:{digest.hexdigest()}"


def require_paper() -> None:
    if runtime_environment() != "PAPER":
        raise ConfigurationError("The synthetic ledger requires the PAPER runtime.")


def account_row(connection: Connection, account: str) -> RowMapping:
    row = (
        connection.execute(LOCK_ACCOUNT, {"account": account}).mappings().one_or_none()
    )
    if row is None:
        raise ValueError("control: paper_account_missing")
    return row


def fill_from_row(row: RowMapping) -> PaperFill:
    return PaperFill(
        row["intent_id"],
        row["correlation_id"],
        row["quote_reference"],
        row["filled_at"].astimezone(UTC),
        row["price"],
        row["quantity"],
        row["notional"],
        PaperBalance(row["cash_after"], row["quantity_after"]),
    )


class PaperLedger:
    def __init__(
        self, engine: Engine, control: ControlPolicy, limits: RiskLimits
    ) -> None:
        self.engine = engine
        self.control = control
        self.limits = limits

    def open_account(self, opening: PaperBalance) -> None:
        require_paper()
        if not self.control.account_id.strip() or any(
            not value.is_finite() or value < 0
            for value in (opening.cash, opening.quantity)
        ):
            raise ValueError("risk: invalid_opening_balance")
        with self.engine.begin() as connection:
            connection.execute(
                text("""
                INSERT INTO trade_system.paper_account
                (account_id, opening_cash, opening_quantity, cash, quantity)
                VALUES (:account, :cash, :quantity, :cash, :quantity)
                """),
                {
                    "account": self.control.account_id,
                    "cash": opening.cash,
                    "quantity": opening.quantity,
                },
            )

    def submit(
        self, intent: TradingIntent, quote: SyntheticQuote, now: datetime
    ) -> PaperFill:
        return self.submit_with_quote_provider(intent, now, lambda: (quote, None))

    def submit_with_quote_provider(
        self,
        intent: TradingIntent,
        now: datetime,
        price: Callable[[], tuple[SyntheticQuote, dict[str, object] | None]],
        *,
        pricing_close_at: str | None = None,
    ) -> PaperFill:
        require_paper()
        authorize(intent, self.control, now)
        identity = {
            "actor_id": intent.actor_id,
            "environment_id": intent.environment_id,
            "symbol": intent.symbol,
            "side": intent.side,
            "correlation_id": intent.correlation_id,
            "issued_at": intent.issued_at.astimezone(UTC).isoformat(),
            "expires_at": intent.expires_at.astimezone(UTC).isoformat(),
        }
        if pricing_close_at is not None:
            identity["pricing_close_at"] = pricing_close_at
        with self.engine.begin() as connection:
            row = account_row(connection, intent.account_id)
            previous = (
                connection.execute(
                    text(
                        f"SELECT {FILL_FIELDS}, intent FROM trade_system.paper_fill "
                        "WHERE account_id = :account AND intent_id = :intent_id"
                    ),
                    {"account": intent.account_id, "intent_id": intent.intent_id},
                )
                .mappings()
                .one_or_none()
            )
            if previous is not None:
                if (
                    not intent.quantity.is_finite()
                    or previous["quantity"] != intent.quantity
                    or previous["intent"] != identity
                ):
                    raise ValueError("control: conflicting_intent_id")
                return fill_from_row(previous)

            quote, market_state = price()
            if (market_state is None) != (pricing_close_at is None):
                raise ValueError("market_state: evidence_mismatch")
            if market_state is not None and quote.reference != market_state_reference(
                market_state
            ):
                raise ValueError("market_state: reference_mismatch")
            balance = PaperBalance(row["cash"], row["quantity"])
            try:
                notional, after = assess(intent, quote, balance, self.limits, now)
            except DecimalException as error:
                raise ValueError("risk: arithmetic_out_of_range") from error
            filled_at = now.astimezone(UTC)
            connection.execute(
                INSERT_FILL,
                {
                    "account": intent.account_id,
                    "intent_id": intent.intent_id,
                    "intent": identity,
                    "side": intent.side,
                    "correlation": intent.correlation_id,
                    "quote": quote.reference,
                    "at": filled_at,
                    "price": quote.price,
                    "quantity": intent.quantity,
                    "notional": notional,
                    "cash_after": after.cash,
                    "quantity_after": after.quantity,
                    "market_state": market_state,
                },
            )
            connection.execute(
                text(
                    "UPDATE trade_system.paper_account SET "
                    "cash = :cash, quantity = :quantity "
                    "WHERE account_id = :account"
                ),
                {
                    "account": intent.account_id,
                    "cash": after.cash,
                    "quantity": after.quantity,
                },
            )
            return PaperFill(
                intent.intent_id,
                intent.correlation_id,
                quote.reference,
                filled_at,
                quote.price,
                intent.quantity,
                notional,
                after,
            )

    def reconcile(self) -> Reconciliation:
        require_paper()
        account = self.control.account_id
        with self.engine.begin() as connection, localcontext() as context:
            context.prec = 50
            context.traps[Inexact] = True
            row = account_row(connection, account)
            expected = PaperBalance(row["opening_cash"], row["opening_quantity"])
            stored = PaperBalance(row["cash"], row["quantity"])
            fills = (
                connection.execute(
                    text(
                        f"SELECT {FILL_FIELDS}, side, market_state, intent "
                        "FROM trade_system.paper_fill "
                        "WHERE account_id = :account ORDER BY sequence_id"
                    ),
                    {"account": account},
                )
                .mappings()
                .all()
            )
            divergent: str | None = None
            for row in fills:
                fill = fill_from_row(row)
                notional = fill.price * fill.quantity
                quantity: Decimal = (
                    fill.quantity if row["side"] == "BUY" else -fill.quantity
                )
                cash_delta = -notional if row["side"] == "BUY" else notional
                expected = PaperBalance(
                    expected.cash + cash_delta, expected.quantity + quantity
                )
                market_state = row["market_state"]
                expects_state = "pricing_close_at" in row["intent"]
                evidence_mismatch = ((market_state is not None) != expects_state) or (
                    market_state is not None
                    and market_state_reference(market_state) != fill.quote_reference
                )
                if divergent is None and (
                    evidence_mismatch
                    or fill.notional != notional
                    or fill.balance_after != expected
                ):
                    divergent = fill.intent_id
            return Reconciliation(len(fills), expected, stored, divergent)
