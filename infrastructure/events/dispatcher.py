"""Publish one committed outbox event per transaction."""

import logging
import typing
from collections.abc import Callable, Mapping
from datetime import timedelta

from sqlalchemy import Numeric, cast, func, select
from sqlalchemy.engine import Engine

from infrastructure.events.outbox import OUTBOX
from infrastructure.security.config import runtime_environment
from infrastructure.telemetry import log_event, tracer

logger = logging.getLogger(__name__)
MAX_ATTEMPTS = 5

Publisher = Callable[[Mapping[str, object]], None]

earlier = OUTBOX.alias("earlier")
earlier_pending = (
    select(earlier.c.event_id)
    .where(
        earlier.c.published_at.is_(None),
        earlier.c.envelope["environment_id"].astext
        == OUTBOX.c.envelope["environment_id"].astext,
        earlier.c.envelope["account_id"].astext.is_not_distinct_from(
            OUTBOX.c.envelope["account_id"].astext
        ),
        earlier.c.envelope["aggregate_type"].astext
        == OUTBOX.c.envelope["aggregate_type"].astext,
        earlier.c.envelope["aggregate_id"].astext
        == OUTBOX.c.envelope["aggregate_id"].astext,
        cast(earlier.c.envelope["aggregate_version"].astext, Numeric)
        < cast(OUTBOX.c.envelope["aggregate_version"].astext, Numeric),
    )
    .correlate(OUTBOX)
    .exists()
)
NEXT_EVENT = (
    select(OUTBOX.c.event_id, OUTBOX.c.envelope, OUTBOX.c.attempts)
    .where(
        OUTBOX.c.published_at.is_(None),
        OUTBOX.c.failed_at.is_(None),
        OUTBOX.c.available_at <= func.now(),
        ~earlier_pending,
    )
    .order_by(OUTBOX.c.available_at, OUTBOX.c.enqueued_at, OUTBOX.c.event_id)
    .limit(1)
    .with_for_update(of=OUTBOX, skip_locked=True)
)


@tracer.start_as_current_span(
    "outbox.dispatch", record_exception=False, set_status_on_exception=False
)
def dispatch_once(engine: Engine, publish: Publisher) -> bool:
    """Attempt one event using a publisher that confirms durable acceptance."""
    environment = runtime_environment()
    query = NEXT_EVENT.where(OUTBOX.c.envelope["environment_id"].astext == environment)
    with engine.begin() as connection:
        row = connection.execute(query).one_or_none()
        if row is None:
            return False

        event_id, envelope, previous_attempts = typing.cast(
            tuple[str, dict[str, object], int], tuple(row)
        )
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
            details["error_type"] = type(error).__name__
            if attempt >= MAX_ATTEMPTS:
                update = update.values(failed_at=func.clock_timestamp())
                outcome = "outbox_failed"
            else:
                delay = 2 ** (attempt - 1)
                update = update.values(
                    available_at=func.clock_timestamp() + timedelta(seconds=delay)
                )
                details["retry_delay_seconds"] = delay
                outcome = "outbox_retry_scheduled"
        else:
            update = update.values(published_at=func.clock_timestamp())
            outcome = "outbox_published"

        connection.execute(update)

    level = logging.INFO if outcome == "outbox_published" else logging.WARNING
    log_event(logger, outcome, level=level, **details)
    return True
