"""Consume local deliveries with transactional deduplication."""

import logging
import typing
from collections.abc import Callable, Mapping

from sqlalchemy import Column, MetaData, Table, Text, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection, Engine

from infrastructure.events.local_delivery import DELIVERY
from infrastructure.security.config import runtime_environment
from infrastructure.telemetry import log_event, tracer

logger = logging.getLogger(__name__)

EventHandler = Callable[[Connection, Mapping[str, object]], None]

PROCESSED_EVENT = Table(
    "processed_event",
    MetaData(),
    Column("event_id", Text(), primary_key=True),
    schema="trade_system",
)

NEXT_DELIVERY = (
    select(DELIVERY.c.delivery_id, DELIVERY.c.envelope)
    .where(DELIVERY.c.consumed_at.is_(None))
    .order_by(DELIVERY.c.delivery_id)
    .limit(1)
    .with_for_update()
)


@tracer.start_as_current_span(
    "delivery.consume", record_exception=False, set_status_on_exception=False
)
def consume_once(engine: Engine, handle_event: EventHandler) -> bool:
    """Acknowledge one delivery and apply its database effect at most once."""
    environment = runtime_environment()
    query = NEXT_DELIVERY.where(
        DELIVERY.c.envelope["environment_id"].astext == environment
    )
    with engine.begin() as connection:
        row = connection.execute(query).one_or_none()
        if row is None:
            return False

        delivery_id, envelope = typing.cast(tuple[int, dict[str, object]], tuple(row))
        event_id = envelope.get("event_id")
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError("The delivery requires a nonblank event_id.")

        inserted = connection.execute(
            insert(PROCESSED_EVENT)
            .values(event_id=event_id)
            .on_conflict_do_nothing(index_elements=[PROCESSED_EVENT.c.event_id])
            .returning(PROCESSED_EVENT.c.event_id)
        ).scalar_one_or_none()

        details = {
            "delivery_id": delivery_id,
            "event_id": event_id,
            "correlation_id": envelope.get("correlation_id"),
            "causation_id": envelope.get("causation_id"),
            "environment_id": environment,
        }
        if inserted is not None:
            try:
                handle_event(connection, envelope)
            except Exception as error:
                log_event(
                    logger,
                    "delivery_failed",
                    level=logging.ERROR,
                    error_type=type(error).__name__,
                    **details,
                )
                raise

        connection.execute(
            DELIVERY.update()
            .where(DELIVERY.c.delivery_id == delivery_id)
            .values(consumed_at=func.clock_timestamp())
        )

    outcome = "delivery_consumed" if inserted is not None else "delivery_duplicate"
    log_event(logger, outcome, level=logging.INFO, **details)
    return True
