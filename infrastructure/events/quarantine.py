"""Serialize dispatch, quarantine, and human-authorized resumption by aggregate."""

import json
from collections.abc import Mapping

from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from infrastructure.security.config import require_event_environment

FIELDS = ("environment_id", "account_id", "aggregate_type", "aggregate_id")
MATCH = """
    environment_id = :environment_id
    AND account_id IS NOT DISTINCT FROM :account_id
    AND aggregate_type = :aggregate_type AND aggregate_id = :aggregate_id
"""


def aggregate_scope(envelope: Mapping[str, object]) -> dict[str, object]:
    return {key: envelope.get(key) for key in FIELDS}


def lock_scope(
    db: Connection, scope: Mapping[str, object], *, wait: bool = True
) -> bool:
    key = json.dumps([scope[name] for name in FIELDS], separators=(",", ":"))
    function = "pg_advisory_xact_lock" if wait else "pg_try_advisory_xact_lock"
    result: object = db.execute(
        text(f"SELECT {function}(hashtextextended(:key, 1738))"), {"key": key}
    ).scalar_one()
    return wait or result is True


def quarantine(db: Connection, envelope: Mapping[str, object], reason: str) -> None:
    scope = aggregate_scope(envelope)
    lock_scope(db, scope)
    db.execute(
        text("""
        INSERT INTO trade_system.outbox_quarantine
        (environment_id, account_id, aggregate_type, aggregate_id, event_id, reason)
        VALUES (:environment_id, :account_id, :aggregate_type, :aggregate_id,
                :event_id, :reason)
        """),
        {**scope, "event_id": envelope["event_id"], "reason": reason},
    )


def is_quarantined(db: Connection, scope: Mapping[str, object]) -> bool:
    active: bool = db.execute(
        text(f"""
        SELECT EXISTS (SELECT 1 FROM trade_system.outbox_quarantine
        WHERE {MATCH} AND released_at IS NULL)
        """),
        scope,
    ).scalar_one()
    return active


def release_quarantine(
    engine: Engine,
    aggregate: Mapping[str, object],
    *,
    decision_reference: str,
) -> int:
    scope = aggregate_scope(aggregate)
    require_event_environment(scope["environment_id"])
    if not decision_reference.strip():
        raise ValueError("outbox_quarantine: decision_required")

    with engine.begin() as db:
        db.execute(
            text("SELECT trade_system.authorize_outbox_operation(:role)"),
            {"role": "outbox_resume_authorizer"},
        )
        lock_scope(db, scope)
        if not is_quarantined(db, scope):
            return 0
        # Use the durable consumer marker for every previously published event.
        query = text(f"""
            SELECT version, published, consumed FROM (
                SELECT CAST(envelope->>'aggregate_version' AS numeric) AS version,
                       published_at IS NOT NULL AS published,
                       processed.event_id IS NOT NULL AS consumed,
                       envelope->>'environment_id' AS environment_id,
                       envelope->>'account_id' AS account_id,
                       envelope->>'aggregate_type' AS aggregate_type,
                       envelope->>'aggregate_id' AS aggregate_id
                FROM trade_system.outbox AS event
                LEFT JOIN trade_system.processed_event AS processed USING (event_id)
            ) AS history WHERE {MATCH} ORDER BY version
            """)
        rows = db.execute(query, scope).all()
        pending_seen = False
        if not rows:
            raise ValueError("outbox_quarantine: incomplete_chain")
        for expected, (version, published, consumed) in enumerate(rows, start=1):
            if version != expected:
                raise ValueError("outbox_quarantine: incomplete_chain")
            if published and (pending_seen or not consumed):
                raise ValueError("outbox_quarantine: unreconciled_effect")
            pending_seen = pending_seen or not published

        matching_receipts: bool = db.execute(
            text(f"""
            SELECT NOT EXISTS (
                SELECT 1 FROM trade_system.outbox_retention_receipt
                WHERE {MATCH} AND NOT EXISTS (
                    SELECT 1 FROM trade_system.outbox AS restored
                    WHERE restored.event_id = outbox_retention_receipt.event_id
                      AND encode(sha256(convert_to(restored.envelope::text, 'UTF8')),
                                 'hex') = outbox_retention_receipt.envelope_sha256
                )
            )
            """),
            scope,
        ).scalar_one()
        if not matching_receipts:
            raise ValueError("outbox_quarantine: retention_repair_mismatch")

        db.execute(
            text(f"""
            UPDATE trade_system.outbox SET failed_at = NULL,
                available_at = clock_timestamp()
            WHERE event_id IN (
                SELECT event_id FROM trade_system.outbox_quarantine
                WHERE {MATCH} AND released_at IS NULL AND reason = 'retained'
            ) AND published_at IS NULL AND failed_at IS NOT NULL
            """),
            scope,
        )
        count: int = db.execute(
            text(f"""
            WITH released AS (
                UPDATE trade_system.outbox_quarantine
                SET released_at = clock_timestamp(), decision_reference = :decision
                WHERE {MATCH} AND released_at IS NULL RETURNING id
            )
            SELECT count(*) FROM released
            """),
            {**scope, "decision": decision_reference},
        ).scalar_one()
        return count
