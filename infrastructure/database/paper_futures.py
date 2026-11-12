"""Persist and reconcile synthetic USDⓈ-M PAPER fills."""

from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, DecimalException
from typing import cast

from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Connection, Engine, RowMapping

from infrastructure.database.paper_ledger import market_state_reference, require_paper
from trade_system.control.paper import ControlPolicy, Side, TradingIntent, authorize
from trade_system.risk.execution_costs import ExecutionCosts
from trade_system.risk.futures import (
    FundingObservation,
    FundingSettlement,
    FuturesBalance,
    FuturesFill,
    LiquidationCutoffError,
    LiquidationMark,
    LiquidationSettlement,
    apply_fill,
    assess_futures,
    settle_funding,
    settle_liquidation,
)
from trade_system.risk.paper import RiskLimits, SyntheticQuote

LOCK = text("""
SELECT opening_cash, balance FROM trade_system.paper_futures_account
WHERE account_id = :account FOR UPDATE
""")


def balance_json(balance: FuturesBalance) -> dict[str, str]:
    return {key: str(value) for key, value in asdict(balance).items()}


def decode_balance(value: dict[str, str]) -> FuturesBalance:
    return FuturesBalance(**{key: Decimal(amount) for key, amount in value.items()})


def fill_json(fill: FuturesFill) -> dict[str, object]:
    return {
        "price": str(fill.price),
        "notional": str(fill.notional),
        "fee": str(fill.fee),
        "realized_pnl": str(fill.realized_pnl),
        "after": balance_json(fill.after),
    }


def decode_fill(value: dict[str, object]) -> FuturesFill:
    return FuturesFill(
        Decimal(cast(str, value["price"])),
        Decimal(cast(str, value["notional"])),
        Decimal(cast(str, value["fee"])),
        Decimal(cast(str, value["realized_pnl"])),
        decode_balance(cast(dict[str, str], value["after"])),
    )


def locked_account(connection: Connection, account: str) -> RowMapping:
    row = connection.execute(LOCK, {"account": account}).mappings().one_or_none()
    if row is None:
        raise ValueError("control: paper_futures_account_missing")
    return row


def update_balance(
    connection: Connection, account_id: str, balance: FuturesBalance
) -> None:
    connection.execute(
        text("""
        UPDATE trade_system.paper_futures_account SET balance = :balance
        WHERE account_id = :account
        """).bindparams(bindparam("balance", type_=JSONB)),
        {"account": account_id, "balance": balance_json(balance)},
    )


def funding_observation(row: RowMapping) -> FundingObservation:
    return FundingObservation(
        row["funding_at"],
        row["available_at"],
        row["mark_price"],
        row["rate"],
        row["reference"],
    )


def latest_funding_at(engine: Engine, account_id: str) -> datetime | None:
    require_paper()
    with engine.connect() as connection:
        locked_account(connection, account_id)
        result: datetime | None = connection.execute(
            text("""
            SELECT max(funding_at) FROM trade_system.paper_futures_funding
            WHERE account_id = :account
            """),
            {"account": account_id},
        ).scalar_one()
        return result


def apply_funding(
    engine: Engine, account_id: str, observation: FundingObservation, *, as_of: datetime
) -> FundingSettlement:
    require_paper()
    observation.validate(as_of)
    keys = {"account": account_id, "funding_at": observation.funding_at}
    with engine.begin() as connection:
        account = locked_account(connection, account_id)
        previous = (
            connection.execute(
                text("""
            SELECT * FROM trade_system.paper_futures_funding
            WHERE account_id = :account AND funding_at = :funding_at
            """),
                keys,
            )
            .mappings()
            .one_or_none()
        )
        if previous is not None:
            if observation != funding_observation(previous):
                raise ValueError("funding: conflicting_observation")
            if as_of < previous["applied_at"]:
                raise ValueError("funding: invalid_cutoff")
            return FundingSettlement(
                previous["cash_delta"], decode_balance(previous["balance_after"])
            )

        out_of_order: bool = connection.execute(
            text("""
            SELECT EXISTS (
                SELECT 1 FROM trade_system.paper_futures_fill
                WHERE account_id = :account AND filled_at >= :funding_at
                UNION ALL
                SELECT 1 FROM trade_system.paper_futures_liquidation
                WHERE account_id = :account AND applied_at >= :funding_at
                UNION ALL
                SELECT 1 FROM trade_system.paper_futures_funding
                WHERE account_id = :account
                  AND (funding_at > :funding_at OR applied_at > :as_of)
            )
            """),
            {**keys, "as_of": as_of},
        ).scalar_one()
        if out_of_order:
            raise ValueError("funding: out_of_order")

        try:
            settlement = settle_funding(decode_balance(account["balance"]), observation)
        except DecimalException as error:
            raise ValueError("funding: arithmetic_out_of_range") from error
        connection.execute(
            text("""
            INSERT INTO trade_system.paper_futures_funding
            (account_id, funding_at, available_at, applied_at, mark_price, rate,
             reference, cash_delta, balance_after)
            VALUES (:account, :funding_at, :available_at, :applied_at, :mark_price,
                    :rate, :reference, :cash_delta, :balance_after)
            """).bindparams(bindparam("balance_after", type_=JSONB)),
            {
                **keys,
                "available_at": observation.available_at,
                "applied_at": as_of,
                "mark_price": observation.mark_price,
                "rate": observation.rate,
                "reference": observation.reference,
                "cash_delta": settlement.cash_delta,
                "balance_after": balance_json(settlement.after),
            },
        )
        update_balance(connection, account_id, settlement.after)
        return settlement


def liquidation_mark(row: RowMapping) -> LiquidationMark:
    return LiquidationMark(
        row["observed_at"], row["available_at"], row["mark_price"], row["reference"]
    )


def decode_liquidation(row: RowMapping) -> LiquidationSettlement:
    return LiquidationSettlement(
        row["isolated_equity"],
        row["maintenance_margin"],
        row["released_margin"],
        decode_balance(row["balance_after"]),
    )


def evaluate_liquidation(
    engine: Engine,
    account_id: str,
    mark: LiquidationMark,
    *,
    maintenance_rate: Decimal,
    as_of: datetime,
    max_age: timedelta,
    recollected: bool = False,
) -> LiquidationSettlement | None:
    require_paper()
    mark.validate(as_of, max_age)
    keys = {"account": account_id, "observed_at": mark.observed_at}
    with engine.begin() as connection:
        account = locked_account(connection, account_id)
        previous = (
            connection.execute(
                text("""
            SELECT * FROM trade_system.paper_futures_liquidation
            WHERE account_id = :account AND observed_at = :observed_at
            """),
                keys,
            )
            .mappings()
            .one_or_none()
        )
        if previous is not None:
            original = liquidation_mark(previous)
            same_mark = (
                mark.price == original.price and mark.reference == original.reference
                if recollected
                else mark == original
            )
            if (
                not same_mark
                or not maintenance_rate.is_finite()
                or maintenance_rate != previous["maintenance_rate"]
                or max_age != previous["max_age"]
            ):
                raise ValueError("liquidation: conflicting_observation")
            if as_of < previous["applied_at"]:
                raise ValueError("liquidation: invalid_cutoff")
            return None if recollected else decode_liquidation(previous)

        out_of_order: bool = connection.execute(
            text("""
            SELECT EXISTS (
                SELECT 1 FROM trade_system.paper_futures_fill
                WHERE account_id = :account AND filled_at > :observed_at
                UNION ALL
                SELECT 1 FROM trade_system.paper_futures_funding
                WHERE account_id = :account AND applied_at > :observed_at
                UNION ALL
                SELECT 1 FROM trade_system.paper_futures_liquidation
                WHERE account_id = :account AND applied_at > :observed_at
            )
            """),
            keys,
        ).scalar_one()
        if out_of_order:
            raise LiquidationCutoffError("liquidation: out_of_order")
        try:
            settlement = settle_liquidation(
                decode_balance(account["balance"]), mark, maintenance_rate
            )
        except DecimalException as error:
            raise ValueError("liquidation: arithmetic_out_of_range") from error
        if settlement is None:
            return None

        connection.execute(
            text("""
            INSERT INTO trade_system.paper_futures_liquidation
            (account_id, observed_at, available_at, applied_at, mark_price,
             reference, maintenance_rate, max_age, isolated_equity,
             maintenance_margin, released_margin, balance_after)
            VALUES (:account, :observed_at, :available_at, :applied_at, :mark_price,
                    :reference, :maintenance_rate, :max_age, :isolated_equity,
                    :maintenance_margin, :released_margin, :balance_after)
            """).bindparams(bindparam("balance_after", type_=JSONB)),
            {
                **keys,
                "available_at": mark.available_at,
                "applied_at": as_of,
                "mark_price": mark.price,
                "reference": mark.reference,
                "maintenance_rate": maintenance_rate,
                "max_age": max_age,
                "isolated_equity": settlement.isolated_equity,
                "maintenance_margin": settlement.maintenance_margin,
                "released_margin": settlement.released_margin,
                "balance_after": balance_json(settlement.after),
            },
        )
        update_balance(connection, account_id, settlement.after)
        return settlement


@dataclass(frozen=True)
class FuturesReconciliation:
    fills: int
    expected: FuturesBalance
    stored: FuturesBalance
    first_divergent_fill: str | None
    funding_entries: int = 0
    first_divergent_funding_at: datetime | None = None
    liquidations: int = 0
    first_divergent_liquidation_at: datetime | None = None

    @property
    def consistent(self) -> bool:
        return (
            self.first_divergent_fill is None
            and self.first_divergent_funding_at is None
            and self.first_divergent_liquidation_at is None
            and self.expected == self.stored
        )


class PaperFuturesLedger:
    def __init__(
        self,
        engine: Engine,
        control: ControlPolicy,
        limits: RiskLimits,
        *,
        costs: ExecutionCosts = ExecutionCosts(),
    ) -> None:
        self.engine = engine
        self.control = control
        self.limits = limits
        self.costs = costs

    def open_account(self, cash: Decimal) -> None:
        require_paper()
        if not self.control.account_id.strip() or not cash.is_finite() or cash < 0:
            raise ValueError("risk: invalid_opening_balance")
        with self.engine.begin() as connection:
            connection.execute(
                text("""
                INSERT INTO trade_system.paper_futures_account
                (account_id, opening_cash, balance)
                VALUES (:account, :cash, :balance)
                """).bindparams(bindparam("balance", type_=JSONB)),
                {
                    "account": self.control.account_id,
                    "cash": cash,
                    "balance": balance_json(FuturesBalance(cash)),
                },
            )

    def submit(
        self,
        intent: TradingIntent,
        quote: SyntheticQuote,
        now: datetime,
        *,
        reduce_only: bool,
    ) -> FuturesFill:
        return self.submit_with_quote_provider(
            intent, now, lambda: (quote, None), reduce_only=reduce_only
        )

    def submit_with_quote_provider(
        self,
        intent: TradingIntent,
        now: datetime,
        quote_provider: Callable[[], tuple[SyntheticQuote, dict[str, object] | None]],
        *,
        reduce_only: bool,
        pricing_close_at: str | None = None,
    ) -> FuturesFill:
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
            "reduce_only": reduce_only,
        }
        if pricing_close_at is not None:
            identity["pricing_close_at"] = pricing_close_at
        keys = {"account": intent.account_id, "intent_id": intent.intent_id}
        with self.engine.begin() as connection:
            account = locked_account(connection, intent.account_id)
            previous = (
                connection.execute(
                    text("""
                SELECT intent, quantity, fill FROM trade_system.paper_futures_fill
                WHERE account_id = :account AND intent_id = :intent_id
                """),
                    keys,
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
                return decode_fill(previous["fill"])

            latest_funding: datetime | None = connection.execute(
                text("""
                SELECT max(applied_at) FROM trade_system.paper_futures_funding
                WHERE account_id = :account
                """),
                keys,
            ).scalar_one()
            if latest_funding is not None and now < latest_funding:
                raise ValueError("funding: fill_precedes_settlement")

            latest_liquidation: datetime | None = connection.execute(
                text("""
                SELECT max(applied_at) FROM trade_system.paper_futures_liquidation
                WHERE account_id = :account
                """),
                keys,
            ).scalar_one()
            if latest_liquidation is not None and now < latest_liquidation:
                raise ValueError("liquidation: fill_precedes_settlement")

            quote, market_state = quote_provider()
            if (pricing_close_at is None) != (market_state is None) or (
                market_state is not None
                and quote.reference != market_state_reference(market_state)
            ):
                raise ValueError("market_state: invalid_quote_evidence")

            try:
                fill = assess_futures(
                    intent,
                    quote,
                    decode_balance(account["balance"]),
                    self.limits,
                    self.costs,
                    now,
                    reduce_only=reduce_only,
                )
            except DecimalException as error:
                raise ValueError("risk: arithmetic_out_of_range") from error
            connection.execute(
                text("""
                INSERT INTO trade_system.paper_futures_fill
                (account_id, intent_id, intent, quantity, reference_price, fee_bps,
                 slippage_bps, quote_reference, filled_at, fill, market_state)
                VALUES (:account, :intent_id, :intent, :quantity, :reference_price,
                        :fee_bps,
                        :slippage_bps, :quote_reference, :filled_at, :fill,
                        :market_state)
                """).bindparams(
                    bindparam("intent", type_=JSONB),
                    bindparam("fill", type_=JSONB),
                    bindparam("market_state", type_=JSONB(none_as_null=True)),
                ),
                {
                    **keys,
                    "intent": identity,
                    "quantity": intent.quantity,
                    "reference_price": quote.price,
                    "fee_bps": self.costs.fee_bps,
                    "slippage_bps": self.costs.slippage_bps,
                    "quote_reference": quote.reference,
                    "filled_at": now.astimezone(UTC),
                    "fill": fill_json(fill),
                    "market_state": market_state,
                },
            )
            update_balance(connection, intent.account_id, fill.after)
            return fill

    def apply_funding(
        self, observation: FundingObservation, *, as_of: datetime
    ) -> FundingSettlement:
        return apply_funding(
            self.engine, self.control.account_id, observation, as_of=as_of
        )

    def liquidate_if_needed(
        self, mark: LiquidationMark, *, maintenance_rate: Decimal, as_of: datetime
    ) -> LiquidationSettlement | None:
        return evaluate_liquidation(
            self.engine,
            self.control.account_id,
            mark,
            maintenance_rate=maintenance_rate,
            as_of=as_of,
            max_age=self.limits.max_quote_age,
        )

    def reconcile(self) -> FuturesReconciliation:
        require_paper()
        account_id = self.control.account_id
        with self.engine.begin() as connection:
            account = locked_account(connection, account_id)
            expected = FuturesBalance(account["opening_cash"])
            stored = decode_balance(account["balance"])
            rows = (
                connection.execute(
                    text("""
                SELECT sequence_id, filled_at, intent_id, intent, quantity,
                       reference_price, fee_bps, slippage_bps, fill,
                       quote_reference, market_state
                FROM trade_system.paper_futures_fill
                WHERE account_id = :account ORDER BY sequence_id
                """),
                    {"account": account_id},
                )
                .mappings()
                .all()
            )
            funding = (
                connection.execute(
                    text("""
                SELECT * FROM trade_system.paper_futures_funding
                WHERE account_id = :account ORDER BY sequence_id
                """),
                    {"account": account_id},
                )
                .mappings()
                .all()
            )
            liquidations = (
                connection.execute(
                    text("""
                SELECT * FROM trade_system.paper_futures_liquidation
                WHERE account_id = :account
                """),
                    {"account": account_id},
                )
                .mappings()
                .all()
            )
            divergent_liquidation: datetime | None = None
            divergent: str | None = None
            divergent_funding: datetime | None = None
            latest_fill: datetime | None = None
            latest_funding_at: datetime | None = None
            latest_applied_at: datetime | None = None
            for row in sorted(
                [*rows, *funding, *liquidations], key=lambda entry: entry["sequence_id"]
            ):
                if "observed_at" in row:
                    mark = liquidation_mark(row)
                    try:
                        mark.validate(row["applied_at"], row["max_age"])
                        if (
                            latest_fill is not None and mark.observed_at < latest_fill
                        ) or (
                            latest_applied_at is not None
                            and mark.observed_at < latest_applied_at
                        ):
                            raise ValueError("liquidation: out_of_order")
                        liquidation = settle_liquidation(
                            expected, mark, row["maintenance_rate"]
                        )
                        if liquidation is None:
                            raise ValueError("liquidation: threshold_not_met")
                    except (ValueError, DecimalException):
                        divergent_liquidation = (
                            divergent_liquidation or mark.observed_at
                        )
                        break
                    expected = liquidation.after
                    latest_applied_at = row["applied_at"]
                    latest_fill = latest_applied_at
                    if liquidation != decode_liquidation(row):
                        divergent_liquidation = (
                            divergent_liquidation or mark.observed_at
                        )
                    continue
                if "funding_at" in row:
                    observation = funding_observation(row)
                    applied_at = row["applied_at"]
                    try:
                        observation.validate(applied_at)
                        if (
                            (
                                latest_fill is not None
                                and observation.funding_at <= latest_fill
                            )
                            or (
                                latest_funding_at is not None
                                and observation.funding_at <= latest_funding_at
                            )
                            or (
                                latest_applied_at is not None
                                and applied_at < latest_applied_at
                            )
                        ):
                            raise ValueError("funding: out_of_order")
                        settlement = settle_funding(expected, observation)
                    except (ValueError, DecimalException):
                        divergent_funding = observation.funding_at
                        break
                    expected = settlement.after
                    latest_funding_at = observation.funding_at
                    latest_applied_at = applied_at
                    if divergent_funding is None and (
                        settlement.cash_delta != row["cash_delta"]
                        or expected != decode_balance(row["balance_after"])
                    ):
                        divergent_funding = observation.funding_at
                    continue
                filled_at = row["filled_at"]
                latest_fill = (
                    filled_at if latest_fill is None else max(latest_fill, filled_at)
                )
                if latest_applied_at is not None and filled_at < latest_applied_at:
                    divergent = divergent or row["intent_id"]
                intent = row["intent"]
                market_state = row["market_state"]
                if divergent is None and (
                    ("pricing_close_at" in intent) != (market_state is not None)
                    or (
                        market_state is not None
                        and market_state_reference(market_state)
                        != row["quote_reference"]
                    )
                ):
                    divergent = row["intent_id"]
                try:
                    recomputed = apply_fill(
                        expected,
                        cast(Side, intent["side"]),
                        row["quantity"],
                        row["reference_price"],
                        ExecutionCosts(row["fee_bps"], row["slippage_bps"]),
                        reduce_only=intent["reduce_only"],
                    )
                except (ValueError, DecimalException):
                    divergent = divergent or row["intent_id"]
                    break
                expected = recomputed.after
                if divergent is None and recomputed != decode_fill(row["fill"]):
                    divergent = row["intent_id"]
            return FuturesReconciliation(
                len(rows),
                expected,
                stored,
                divergent,
                len(funding),
                divergent_funding,
                len(liquidations),
                divergent_liquidation,
            )
