"""Publish one committed outbox event per transaction."""

import logging
import typing
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta

from sqlalchemy import Numeric, cast, func, select, text
from sqlalchemy.engine import Engine

from infrastructure.events.gap_escalation import (
    DEFAULT_GAP_AFTER_SECONDS,
    escalate_gaps,
)
from infrastructure.events.outbox import OUTBOX
from infrastructure.events.quarantine import (
    aggregate_scope,
    is_quarantined,
    lock_scope,
    quarantine,
)
from infrastructure.security.config import runtime_environment
from infrastructure.telemetry import log_event, tracer

logger = logging.getLogger(__name__)
MAX_ATTEMPTS = 5

Publisher = Callable[[Mapping[str, object]], None]

predecessor = OUTBOX.alias("predecessor")
version = cast(OUTBOX.c.envelope["aggregate_version"].astext, Numeric)
predecessor_version = cast(predecessor.c.envelope["aggregate_version"].astext, Numeric)
same_aggregate = (
    select(predecessor.c.event_id)
    .where(
        predecessor.c.envelope["environment_id"].astext
        == OUTBOX.c.envelope["environment_id"].astext,
        predecessor.c.envelope["account_id"].astext.is_not_distinct_from(
            OUTBOX.c.envelope["account_id"].astext
        ),
        predecessor.c.envelope["aggregate_type"].astext
        == OUTBOX.c.envelope["aggregate_type"].astext,
        predecessor.c.envelope["aggregate_id"].astext
        == OUTBOX.c.envelope["aggregate_id"].astext,
    )
    .correlate(OUTBOX)
)
earlier_pending = same_aggregate.where(
    predecessor_version < version, predecessor.c.published_at.is_(None)
).exists()
previous_published = same_aggregate.where(
    predecessor_version == version - 1, predecessor.c.published_at.is_not(None)
).exists()
quarantine_scope = text("""
    EXISTS (
        SELECT 1 FROM trade_system.outbox_quarantine AS q
        WHERE q.released_at IS NULL
          AND q.environment_id = outbox.envelope->>'environment_id'
          AND q.account_id IS NOT DISTINCT FROM (outbox.envelope->>'account_id')
          AND q.aggregate_type = outbox.envelope->>'aggregate_type'
          AND q.aggregate_id = outbox.envelope->>'aggregate_id'
    )
""")
ordering_blocked = (
    earlier_pending | ((version != 1) & ~previous_published) | quarantine_scope
)
NEXT_EVENT = (
    select(OUTBOX.c.event_id, OUTBOX.c.envelope, OUTBOX.c.attempts)
    .where(
        OUTBOX.c.published_at.is_(None),
        OUTBOX.c.failed_at.is_(None),
        OUTBOX.c.available_at <= func.now(),
        ~ordering_blocked,
    )
    .order_by(OUTBOX.c.available_at, OUTBOX.c.enqueued_at, OUTBOX.c.event_id)
    .limit(1)
    .with_for_update(of=OUTBOX, skip_locked=True)
)


@tracer.start_as_current_span(
    "outbox.dispatch", record_exception=False, set_status_on_exception=False
)
def dispatch_once(
    engine: Engine,
    publish: Publisher,
    *,
    gap_after: timedelta | None = timedelta(seconds=DEFAULT_GAP_AFTER_SECONDS),
) -> bool:
    """Attempt one event using a publisher that confirms durable acceptance."""
    environment = runtime_environment()
    query = NEXT_EVENT.where(OUTBOX.c.envelope["environment_id"].astext == environment)
    with engine.begin() as connection:
        escalate_gaps(connection, environment=environment, gap_after=gap_after)
        row = connection.execute(query).one_or_none()
        if row is None:
            return False

        event_id, envelope, previous_attempts = typing.cast(
            tuple[str, dict[str, object], int], tuple(row)
        )
        scope = aggregate_scope(envelope)
        if not lock_scope(connection, scope, wait=False) or is_quarantined(
            connection, scope
        ):
            return False
        attempt = previous_attempts + 1
        update = (
            OUTBOX.update()
            .where(OUTBOX.c.event_id == event_id)
            .values(attempts=attempt)
        )
        details = {
            "event_id": event_id,
            "correlation_id": envelope["correlation_id"],
            "causation_id": envelope["causation_id"],
            "environment_id": envelope["environment_id"],
            "attempt": attempt,
        }

        try:
            publish(envelope)
        except Exception as error:
            recorded_at: datetime = connection.execute(
                select(func.clock_timestamp())
            ).scalar_one()
            details["error_type"] = type(error).__name__
            if attempt >= MAX_ATTEMPTS:
                update = update.values(failed_at=recorded_at)
                outcome = "outbox_failed"
                quarantine(connection, envelope, "retained")
            else:
                delay = 2 ** (attempt - 1)
                update = update.values(
                    available_at=recorded_at + timedelta(seconds=delay)
                )
                details["retry_delay_seconds"] = delay
                outcome = "outbox_retry_scheduled"
        else:
            recorded_at = connection.execute(
                select(func.clock_timestamp())
            ).scalar_one()
            update = update.values(published_at=recorded_at)
            outcome = "outbox_published"

        connection.execute(update)
        connection.execute(
            text("""
            INSERT INTO trade_system.outbox_attempt
            (event_id, attempt, environment_id, recorded_at, outcome)
            VALUES (:event_id, :attempt, :environment_id, :recorded_at, :outcome)
            """),
            {
                "event_id": event_id,
                "attempt": attempt,
                "environment_id": environment,
                "recorded_at": recorded_at,
                "outcome": outcome,
            },
        )

    level = logging.INFO if outcome == "outbox_published" else logging.WARNING
    log_event(logger, outcome, level=level, **details)
    return True
