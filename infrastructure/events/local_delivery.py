"""Durable publication to the local PostgreSQL delivery queue."""

from collections.abc import Mapping

from sqlalchemy import BigInteger, Column, DateTime, MetaData, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine

DELIVERY = Table(
    "event_delivery",
    MetaData(),
    Column("delivery_id", BigInteger(), primary_key=True),
    Column("envelope", JSONB(), nullable=False),
    Column("consumed_at", DateTime(timezone=True)),
    schema="trade_system",
)


class LocalPublisher:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def __call__(self, envelope: Mapping[str, object]) -> None:
        with self.engine.begin() as connection:
            connection.execute(DELIVERY.insert().values(envelope=dict(envelope)))
