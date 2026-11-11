"""Persist an event in the caller's database transaction."""

from collections.abc import Mapping

from sqlalchemy import Column, DateTime, MetaData, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Connection

OUTBOX = Table(
    "outbox",
    MetaData(),
    Column("event_id", Text(), primary_key=True),
    Column("envelope", JSONB(), nullable=False),
    Column("enqueued_at", DateTime(timezone=True), nullable=False),
    schema="trade_system",
)


def append_event(connection: Connection, envelope: Mapping[str, object]) -> None:
    """Insert a validated EventEnvelope v1 using the state write's transaction."""
    if not connection.in_transaction():
        raise RuntimeError(
            "An active database transaction is required to append an event."
        )

    connection.execute(
        OUTBOX.insert().values(event_id=envelope["event_id"], envelope=dict(envelope))
    )
