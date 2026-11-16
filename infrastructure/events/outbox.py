"""Persist an event in the caller's database transaction."""

from collections.abc import Mapping

from sqlalchemy import Column, DateTime, Integer, MetaData, Table, Text, bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError

from infrastructure.events.quarantine import quarantine
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


def record_version_conflict(
    connection: Connection, envelope: Mapping[str, object]
) -> None:
    with connection.engine.begin() as audit:
        quarantine(audit, envelope, "version_conflict")
        audit.execute(
            text("""
            INSERT INTO trade_system.outbox_version_conflict
            (event_id, environment_id, account_id, aggregate_type,
             aggregate_id, aggregate_version, correlation_id)
            VALUES (:event_id, :environment_id, :account_id, :aggregate_type,
                    :aggregate_id, :aggregate_version, :correlation_id)
            """),
            {
                "event_id": envelope["event_id"],
                "environment_id": envelope["environment_id"],
                "account_id": envelope.get("account_id"),
                "aggregate_type": envelope["aggregate_type"],
                "aggregate_id": envelope["aggregate_id"],
                "aggregate_version": envelope["aggregate_version"],
                "correlation_id": envelope["correlation_id"],
            },
        )


def record_id_conflict(
    connection: Connection,
    original: Mapping[str, object],
    envelope: Mapping[str, object],
    original_sha256: str,
    claimed_sha256: str,
) -> None:
    with connection.engine.begin() as audit:
        quarantine(audit, original, "event_id_conflict")
        audit.execute(
            text("""
            INSERT INTO trade_system.outbox_event_id_conflict
            (event_id, original_sha256, claimed_sha256,
             claimed_environment_id, claimed_correlation_id)
            VALUES (:event_id, :original, :claimed, :environment, :correlation)
            """),
            {
                "event_id": envelope["event_id"],
                "original": original_sha256,
                "claimed": claimed_sha256,
                "environment": envelope["environment_id"],
                "correlation": envelope["correlation_id"],
            },
        )


def append_event(connection: Connection, envelope: Mapping[str, object]) -> None:
    """Insert a validated EventEnvelope v1 using the state write's transaction."""
    require_event_environment(envelope.get("environment_id"))
    if not connection.in_transaction():
        raise RuntimeError(
            "An active database transaction is required to append an event."
        )

    parameters = {"event_id": envelope["event_id"], "claimed": dict(envelope)}
    receipt = (
        connection.execute(
            text("""
        SELECT *, encode(sha256(convert_to(CAST(:claimed AS jsonb)::text, 'UTF8')),
                         'hex') AS claimed_digest
        FROM trade_system.outbox_retention_receipt
        WHERE event_id = :event_id ORDER BY id DESC LIMIT 1
        """).bindparams(bindparam("claimed", type_=JSONB)),
            parameters,
        )
        .mappings()
        .one_or_none()
    )
    if receipt is not None and receipt["envelope_sha256"] != receipt["claimed_digest"]:
        original = dict(receipt)
        connection.rollback()
        record_id_conflict(
            connection,
            original,
            envelope,
            receipt["envelope_sha256"],
            receipt["claimed_digest"],
        )
        raise ValueError("outbox: retained_event_id_conflict")

    try:
        with connection.begin_nested():
            connection.execute(
                OUTBOX.insert().values(
                    event_id=envelope["event_id"],
                    envelope=dict(envelope),
                    attempts=receipt["attempts"] if receipt is not None else 0,
                )
            )
    except IntegrityError as error:
        constraint = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
        original_row = None
        if constraint in ("outbox_pkey", "outbox_aggregate_version_unique"):
            original_row = (
                connection.execute(
                    text("""
                SELECT envelope, envelope = CAST(:claimed AS jsonb) AS equivalent,
                       encode(sha256(convert_to(envelope::text, 'UTF8')), 'hex')
                           AS original_digest,
                       encode(sha256(convert_to(CAST(:claimed AS jsonb)::text, 'UTF8')),
                              'hex') AS claimed_digest
                FROM trade_system.outbox WHERE event_id = :event_id
                """).bindparams(bindparam("claimed", type_=JSONB)),
                    parameters,
                )
                .mappings()
                .one_or_none()
            )

        # Roll back the state write even when the caller catches this exception.
        connection.rollback()
        if original_row is not None:
            if not original_row["equivalent"]:
                record_id_conflict(
                    connection,
                    original_row["envelope"],
                    envelope,
                    original_row["original_digest"],
                    original_row["claimed_digest"],
                )
        elif constraint == "outbox_aggregate_version_unique":
            record_version_conflict(connection, envelope)
        raise
