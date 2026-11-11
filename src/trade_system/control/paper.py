"""Authority checks for synthetic PAPER intents."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Literal

Side = Literal["BUY", "SELL"]


@dataclass(frozen=True)
class TradingIntent:
    intent_id: str
    correlation_id: str
    account_id: str
    actor_id: str
    environment_id: str
    symbol: str
    side: Side
    quantity: Decimal
    issued_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class ControlPolicy:
    account_id: str
    allowed_actors: frozenset[str]
    paused: bool = True


def authorize(intent: TradingIntent, policy: ControlPolicy, now: datetime) -> None:
    if intent.environment_id != "PAPER":
        raise ValueError("control: paper_required")
    if policy.paused:
        raise ValueError("control: paused")
    if (
        not policy.account_id.strip()
        or intent.account_id != policy.account_id
        or not intent.actor_id.strip()
        or intent.actor_id not in policy.allowed_actors
    ):
        raise ValueError("control: unauthorized")
    if (
        intent.symbol != "BTCUSDT"
        or intent.side not in ("BUY", "SELL")
        or not intent.intent_id.strip()
        or not intent.correlation_id.strip()
    ):
        raise ValueError("control: invalid_intent")
    if any(
        value.utcoffset() is None
        for value in (now, intent.issued_at, intent.expires_at)
    ):
        raise ValueError("control: timezone_required")
    if not intent.issued_at <= now < intent.expires_at:
        raise ValueError("control: intent_outside_validity")
