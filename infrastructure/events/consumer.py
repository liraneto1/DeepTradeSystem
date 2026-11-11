"""Consume local deliveries with transactional deduplication."""

import json
import logging
import typing
from collections.abc import Callable, Mapping

from sqlalchemy import Column, MetaData, Table, Text, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection, Engine

from infrastructure.events.local_delivery import DELIVERY

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


def consume_once(engine: Engine, handle_event: EventHandler) -> bool:
    """Acknowledge one delivery and apply its database effect at most once."""
    with engine.begin() as connection:
        row = connection.execute(NEXT_DELIVERY).one_or_none()
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

        if inserted is not None:
            handle_event(connection, envelope)

        connection.execute(
            DELIVERY.update()
            .where(DELIVERY.c.delivery_id == delivery_id)
            .values(consumed_at=func.clock_timestamp())
        )

    logger.info(
        "%s",
        json.dumps(
            {
                "event": "delivery_consumed"
                if inserted is not None
                else "delivery_duplicate",
                "delivery_id": delivery_id,
                "event_id": event_id,
                "correlation_id": envelope.get("correlation_id"),
                "environment_id": envelope.get("environment_id"),
            }
        ),
    )
    return True
