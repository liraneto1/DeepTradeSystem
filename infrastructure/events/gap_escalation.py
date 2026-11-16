"""Escalate missing predecessors and retain evidence of authorized removal."""

from collections.abc import Mapping
from datetime import timedelta

from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from infrastructure.events.quarantine import aggregate_scope, is_quarantined, lock_scope
from infrastructure.security.config import runtime_environment

DEFAULT_GAP_AFTER_SECONDS = 3600
RETENTION_MINIMUM_AGE = timedelta(days=30)

GAPS = """
    SELECT e.envelope, (e.envelope->>'aggregate_version')::numeric - 1 AS expected,
           EXISTS (
               SELECT 1 FROM trade_system.outbox_retention_receipt AS receipt
               WHERE receipt.environment_id = e.envelope->>'environment_id'
                 AND receipt.account_id IS NOT DISTINCT FROM e.envelope->>'account_id'
                 AND receipt.aggregate_type = e.envelope->>'aggregate_type'
                 AND receipt.aggregate_id = e.envelope->>'aggregate_id'
                 AND receipt.aggregate_version =
                     (e.envelope->>'aggregate_version')::numeric - 1
           ) AS was_removed,
           statement_timestamp() - e.enqueued_at AS age
    FROM trade_system.outbox AS e
    WHERE e.envelope->>'environment_id' = :environment
      AND e.published_at IS NULL AND e.failed_at IS NULL
      AND (e.envelope->>'aggregate_version')::numeric > 1
      AND NOT EXISTS (
          SELECT 1 FROM trade_system.outbox AS predecessor
          WHERE predecessor.envelope->>'environment_id' = e.envelope->>'environment_id'
            AND predecessor.envelope->>'account_id'
                IS NOT DISTINCT FROM e.envelope->>'account_id'
            AND predecessor.envelope->>'aggregate_type' = e.envelope->>'aggregate_type'
            AND predecessor.envelope->>'aggregate_id' = e.envelope->>'aggregate_id'
            AND (predecessor.envelope->>'aggregate_version')::numeric =
                (e.envelope->>'aggregate_version')::numeric - 1
      )
"""


def escalate_gaps(
    db: Connection, *, environment: str, gap_after: timedelta | None
) -> None:
    if gap_after is not None and gap_after <= timedelta(0):
        raise ValueError("outbox_gap: invalid_threshold")
    params = {"environment": environment}
    candidates = (
        db.execute(
            text(f"""
        SELECT * FROM ({GAPS}) AS gaps
        WHERE was_removed OR age >= :gap_after
        ORDER BY expected, envelope->>'event_id'
        """),
            {**params, "gap_after": gap_after},
        )
        .mappings()
        .all()
    )
    for candidate in candidates:
        envelope = candidate["envelope"]
        scope = aggregate_scope(envelope)
        if not lock_scope(db, scope, wait=False) or is_quarantined(db, scope):
            continue
        current = (
            db.execute(
                text(f"""
            SELECT * FROM ({GAPS}) AS gaps WHERE envelope->>'event_id' = :event_id
            """),
                {**params, "event_id": envelope["event_id"]},
            )
            .mappings()
            .one_or_none()
        )
        if current is None:
            continue
        removed = current["was_removed"]
        if not removed and (gap_after is None or current["age"] < gap_after):
            continue
        db.execute(
            text("""
            INSERT INTO trade_system.outbox_quarantine
            (environment_id, account_id, aggregate_type, aggregate_id, event_id,
             reason, expected_version)
            VALUES (:environment_id, :account_id, :aggregate_type, :aggregate_id,
                    :event_id, :reason, :expected)
            """),
            {
                **scope,
                "event_id": envelope["event_id"],
                "expected": current["expected"],
                "reason": "retention_removed" if removed else "missing",
            },
        )


def remove_published_event(
    engine: Engine, event_id: str, *, decision_reference: str
) -> bool:
    """Remove one reconciled event and commit its retention receipt atomically."""
    environment = runtime_environment()
    if not decision_reference.strip():
        raise ValueError("outbox_retention: decision_required")
    with engine.begin() as db:
        db.execute(
            text("SELECT trade_system.authorize_outbox_operation(:role)"),
            {"role": "outbox_retention_authorizer"},
        )
        envelope: Mapping[str, object] | None = db.execute(
            text("""
            SELECT envelope FROM trade_system.outbox
            WHERE event_id = :event_id AND envelope->>'environment_id' = :environment
            """),
            {"event_id": event_id, "environment": environment},
        ).scalar_one_or_none()
        if envelope is None:
            return False
        scope = aggregate_scope(envelope)
        lock_scope(db, scope)
        if is_quarantined(db, scope):
            raise ValueError("outbox_retention: quarantined")
        removed = db.execute(
            text("""
            DELETE FROM trade_system.outbox AS event
            WHERE event_id = :event_id AND published_at IS NOT NULL
              AND envelope->>'environment_id' = :environment_id
              AND published_at <= statement_timestamp() - :minimum_age
              AND NOT EXISTS (
                  SELECT 1 FROM trade_system.outbox AS successor
                  WHERE successor.envelope->>'environment_id' = :environment_id
                    AND successor.envelope->>'account_id'
                        IS NOT DISTINCT FROM :account_id
                    AND successor.envelope->>'aggregate_type' = :aggregate_type
                    AND successor.envelope->>'aggregate_id' = :aggregate_id
                    AND (successor.envelope->>'aggregate_version')::numeric >
                        (event.envelope->>'aggregate_version')::numeric
              )
              AND EXISTS (
                  SELECT 1 FROM trade_system.processed_event
                  WHERE event_id = event.event_id
              )
            RETURNING encode(sha256(convert_to(envelope::text, 'UTF8')), 'hex'),
                      attempts
            """),
            {**scope, "event_id": event_id, "minimum_age": RETENTION_MINIMUM_AGE},
        ).one_or_none()
        if removed is None:
            raise ValueError("outbox_retention: ineligible_event")
        db.execute(
            text("""
            INSERT INTO trade_system.outbox_retention_receipt
            (event_id, environment_id, account_id, aggregate_type, aggregate_id,
             aggregate_version, decision_reference, envelope_sha256, attempts)
            VALUES (:event_id, :environment_id, :account_id, :aggregate_type,
                    :aggregate_id, :version, :decision, :digest, :attempts)
            """),
            {
                **scope,
                "event_id": event_id,
                "version": envelope["aggregate_version"],
                "decision": decision_reference,
                "digest": removed[0],
                "attempts": removed[1],
            },
        )
        return True
