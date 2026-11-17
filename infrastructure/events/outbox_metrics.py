"""Collect environment-scoped Outbox metrics from one PostgreSQL snapshot."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import cast

from sqlalchemy import case, func, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from infrastructure.events.dispatcher import ordering_blocked
from infrastructure.events.outbox import OUTBOX
from infrastructure.security.config import runtime_environment

CONDITIONS = ("retained", "blocked", "waiting", "eligible")


def collect_outbox_metrics(
    engine: Engine, *, window: timedelta, include_incidents: bool = False
) -> dict[str, object]:
    environment = runtime_environment()
    if window <= timedelta(0):
        raise ValueError("outbox_metrics: invalid_window")
    scoped = OUTBOX.c.envelope["environment_id"].astext == environment
    try:
        with (
            engine.connect().execution_options(isolation_level="REPEATABLE READ") as db,
            db.begin(),
        ):
            db.execute(text("SET TRANSACTION READ ONLY"))
            sampled_at: datetime = db.execute(
                select(func.statement_timestamp())
            ).scalar_one()
            sampled_at = sampled_at.astimezone(UTC)
            since = sampled_at - window
            condition = case(
                (OUTBOX.c.failed_at.is_not(None), "retained"),
                (ordering_blocked, "blocked"),
                (OUTBOX.c.available_at > sampled_at, "waiting"),
                else_="eligible",
            )
            seconds = func.extract("epoch", sampled_at - func.min(OUTBOX.c.enqueued_at))
            counts = dict.fromkeys(CONDITIONS, 0)
            ages: dict[str, float] = {}
            for row in db.execute(
                select(condition, func.count(), seconds)
                .where(scoped, OUTBOX.c.published_at.is_(None))
                .group_by(condition)
            ):
                key, count, age = cast(tuple[str, int, Decimal], tuple(row))
                counts[key] = count
                ages[key] = float(age)

            delay = func.extract("epoch", OUTBOX.c.published_at - OUTBOX.c.enqueued_at)
            published = (
                db.execute(
                    select(
                        func.count().label("count"),
                        func.min(delay).label("min_seconds"),
                        func.percentile_cont(0.5)
                        .within_group(delay)
                        .label("p50_seconds"),
                        func.percentile_cont(0.95)
                        .within_group(delay)
                        .label("p95_seconds"),
                        func.max(delay).label("max_seconds"),
                    ).where(
                        scoped,
                        OUTBOX.c.published_at >= since,
                        OUTBOX.c.published_at < sampled_at,
                    )
                )
                .mappings()
                .one()
            )
            transitions = (
                db.execute(
                    text("""
                SELECT count(*) AS attempts,
                       count(*) FILTER (WHERE outcome = 'outbox_retry_scheduled')
                           AS retries,
                       count(*) FILTER (WHERE outcome = 'outbox_failed')
                           AS terminal_failures
                FROM trade_system.outbox_attempt
                WHERE environment_id = :environment AND recorded_at >= :since
                  AND recorded_at < :sampled_at
                """),
                    {
                        "environment": environment,
                        "since": since,
                        "sampled_at": sampled_at,
                    },
                )
                .mappings()
                .one()
            )
            incidents = []
            if include_incidents:
                incidents = [
                    dict(row)
                    for row in db.execute(
                        text("""
                        SELECT id::text AS id, reason, aggregate_type,
                               aggregate_id, account_id
                        FROM trade_system.outbox_quarantine
                        WHERE environment_id = :environment AND released_at IS NULL
                        ORDER BY id
                        """),
                        {"environment": environment},
                    ).mappings()
                ]
            return {
                "status": "ok",
                "environment": environment,
                "sampled_at": sampled_at.isoformat(),
                "window_start": since.isoformat(),
                "backlog": {
                    "total": sum(counts.values()),
                    "oldest_age_seconds": max(ages.values(), default=None),
                    "conditions": {
                        key: {"count": count, "oldest_age_seconds": ages.get(key)}
                        for key, count in counts.items()
                    },
                },
                "publication_delay": {
                    key: (
                        float(value) if value is not None and key != "count" else value
                    )
                    for key, value in published.items()
                },
                "transitions": dict(transitions),
                **({"incidents": incidents} if include_incidents else {}),
            }
    except SQLAlchemyError:
        return {"status": "unavailable", "environment": environment}
