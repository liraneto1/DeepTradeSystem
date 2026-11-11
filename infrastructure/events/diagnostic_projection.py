"""Apply the local synthetic event effect."""

from collections.abc import Mapping

from sqlalchemy import BigInteger, Column, MetaData, Table, Text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection

DIAGNOSTIC_COUNT = Table(
    "diagnostic_event_count",
    MetaData(),
    Column("environment_id", Text(), primary_key=True),
    Column("event_count", BigInteger(), nullable=False),
    schema="trade_system",
)


def apply_diagnostic_event(
    connection: Connection, envelope: Mapping[str, object]
) -> None:
    environment = envelope.get("environment_id")
    if (
        environment not in ("TRAINING", "PAPER")
        or envelope.get("event_type") != "diagnostics.synthetic.created"
        or envelope.get("schema_version") != "1.0.0"
    ):
        raise ValueError("Unsupported diagnostic event.")

    connection.execute(
        insert(DIAGNOSTIC_COUNT)
        .values(environment_id=environment, event_count=1)
        .on_conflict_do_update(
            index_elements=[DIAGNOSTIC_COUNT.c.environment_id],
            set_={"event_count": DIAGNOSTIC_COUNT.c.event_count + 1},
        )
    )
