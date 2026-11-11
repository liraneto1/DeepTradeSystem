"""Persist an event in the caller's database transaction."""

from collections.abc import Mapping

from sqlalchemy import Column, DateTime, Integer, MetaData, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Connection

from infrastructure.security.config import require_event_environment

OUTBOX = Table(
    "outbox",
    MetaData(),
    Column("event_id", Text(), primary_key=True),
    Column("envelope", JSONB(), nullable=False),
    Column("enqueued_at", DateTime(timezone=True), nullable=False),
    Column("attempts", Integer(), nullable=False),
    Column("available_at", DateTime(timezone=True), nullable=False),
    Column("published_at", DateTime(timezone=True)),
    Column("failed_at", DateTime(timezone=True)),
    schema="trade_system",
)


def append_event(connection: Connection, envelope: Mapping[str, object]) -> None:
    """Insert a validated EventEnvelope v1 using the state write's transaction."""
    require_event_environment(envelope.get("environment_id"))
    if not connection.in_transaction():
        raise RuntimeError(
            "An active database transaction is required to append an event."
        )

    connection.execute(
        OUTBOX.insert().values(event_id=envelope["event_id"], envelope=dict(envelope))
    )
