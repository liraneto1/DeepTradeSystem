import json
import logging
import os
from collections.abc import Iterator, Mapping
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import (
    Column,
    MetaData,
    Table,
    Text,
    create_engine,
    func,
    inspect,
    select,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from infrastructure.database.config import local_database_url
from infrastructure.events.dispatcher import MAX_ATTEMPTS, dispatch_once
from infrastructure.events.local_delivery import DELIVERY, LocalPublisher
from infrastructure.events.outbox import OUTBOX, append_event

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_POSTGRES_TESTS") != "1",
    reason="Requires a disposable PostgreSQL 17 instance",
)
TEST_STATE = Table(
    "outbox_test_state",
    MetaData(),
    Column("state_id", Text(), primary_key=True),
    schema="trade_system",
)


@pytest.fixture
def postgres() -> Iterator[tuple[Config, Engine]]:
    config = Config(str(ROOT / "alembic.ini"))
    engine = create_engine(local_database_url())
    try:
        with engine.connect() as connection:
            version = int(
                connection.execute(text("SHOW server_version_num")).scalar_one()
            )
            assert version // 10000 == 17
            inspector = inspect(connection)
            assert "trade_system" not in inspector.get_schema_names()
            if inspector.has_table("alembic_version", schema="public"):
                assert (
                    connection.execute(
                        text("SELECT version_num FROM public.alembic_version")
                    ).scalar_one_or_none()
                    is None
                )
        yield config, engine
    finally:
        engine.dispose()


def test_migrations_round_trip(postgres: tuple[Config, Engine]) -> None:
    config, engine = postgres
    command.upgrade(config, "head")
    with engine.connect() as connection:
        assert inspect(connection).has_table("outbox", schema="trade_system")
        assert (
            connection.execute(
                text("SELECT version_num FROM public.alembic_version")
            ).scalar_one()
            == "0003"
        )

    command.downgrade(config, "0002")
    with engine.connect() as connection:
        inspector = inspect(connection)
        assert not inspector.has_table("event_delivery", schema="trade_system")
        assert {
            column["name"]
            for column in inspector.get_columns("outbox", schema="trade_system")
        } == {"event_id", "envelope", "enqueued_at"}

    command.downgrade(config, "0001")
    with engine.connect() as connection:
        inspector = inspect(connection)
        assert "trade_system" in inspector.get_schema_names()
        assert not inspector.has_table("outbox", schema="trade_system")
        assert (
            connection.execute(
                text("SELECT version_num FROM public.alembic_version")
            ).scalar_one()
            == "0001"
        )

    command.downgrade(config, "base")
    with engine.connect() as connection:
        assert "trade_system" not in inspect(connection).get_schema_names()
        assert (
            connection.execute(
                text("SELECT version_num FROM public.alembic_version")
            ).scalar_one_or_none()
            is None
        )


@pytest.fixture
def outbox_database(postgres: tuple[Config, Engine]) -> Iterator[Engine]:
    config, engine = postgres
    command.upgrade(config, "head")
    try:
        TEST_STATE.create(engine)
        try:
            yield engine
        finally:
            TEST_STATE.drop(engine)
    finally:
        command.downgrade(config, "base")


@pytest.fixture
def event() -> dict[str, object]:
    path = ROOT / "contracts" / "examples" / "event-envelope.example.json"
    envelope: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
    return envelope


def test_outbox_commits_with_state(
    outbox_database: Engine, event: dict[str, object]
) -> None:
    with outbox_database.begin() as connection:
        connection.execute(TEST_STATE.insert().values(state_id="synthetic-state"))
        append_event(connection, event)
        with outbox_database.connect() as reader:
            assert (
                reader.execute(select(TEST_STATE.c.state_id)).scalar_one_or_none()
                is None
            )
            assert (
                reader.execute(select(OUTBOX.c.envelope)).scalar_one_or_none() is None
            )

    with outbox_database.connect() as reader:
        assert (
            reader.execute(select(TEST_STATE.c.state_id)).scalar_one()
            == "synthetic-state"
        )
        assert reader.execute(select(OUTBOX.c.envelope)).scalar_one() == event


def test_outbox_rolls_back_with_state(
    outbox_database: Engine, event: dict[str, object]
) -> None:
    with (
        pytest.raises(RuntimeError, match="simulated failure"),
        outbox_database.begin() as conn,
    ):
        conn.execute(TEST_STATE.insert().values(state_id="synthetic-state"))
        append_event(conn, event)
        raise RuntimeError("simulated failure")

    with outbox_database.connect() as reader:
        assert (
            reader.execute(select(TEST_STATE.c.state_id)).scalar_one_or_none() is None
        )
        assert reader.execute(select(OUTBOX.c.envelope)).scalar_one_or_none() is None


def test_duplicate_event_rolls_back_new_state(
    outbox_database: Engine, event: dict[str, object]
) -> None:
    with outbox_database.begin() as connection:
        append_event(connection, event)

    with pytest.raises(IntegrityError), outbox_database.begin() as connection:
        connection.execute(TEST_STATE.insert().values(state_id="duplicate-attempt"))
        append_event(connection, event)

    with outbox_database.connect() as reader:
        assert (
            reader.execute(select(TEST_STATE.c.state_id)).scalar_one_or_none() is None
        )
        assert reader.execute(select(OUTBOX.c.envelope)).scalar_one() == event


def test_dispatcher_orders_pending_versions_and_skips_locked_rows(
    outbox_database: Engine, event: dict[str, object]
) -> None:
    next_version = {**event, "event_id": "evt_next", "aggregate_version": 2}
    other_aggregate = {**event, "event_id": "evt_other", "aggregate_id": "other"}
    publish = LocalPublisher(outbox_database)
    with outbox_database.begin() as connection:
        append_event(connection, next_version)
        append_event(connection, event)
        append_event(connection, other_aggregate)

    def publish_with_concurrent_worker(envelope: Mapping[str, object]) -> None:
        assert envelope == event
        assert dispatch_once(outbox_database, publish)
        assert not dispatch_once(outbox_database, publish)
        publish(envelope)

    assert dispatch_once(outbox_database, publish_with_concurrent_worker)
    assert dispatch_once(outbox_database, publish)
    assert not dispatch_once(outbox_database, publish)
    with outbox_database.connect() as connection:
        assert connection.scalars(
            select(DELIVERY.c.envelope).order_by(DELIVERY.c.delivery_id)
        ).all() == [other_aggregate, event, next_version]


def test_dispatcher_retries_then_retains_failed_event(
    outbox_database: Engine, event: dict[str, object], caplog: pytest.LogCaptureFixture
) -> None:
    with outbox_database.begin() as connection:
        append_event(connection, event)
        append_event(
            connection, {**event, "event_id": "evt_next", "aggregate_version": 2}
        )

    def unavailable(_: Mapping[str, object]) -> None:
        raise RuntimeError("private publisher error")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        assert dispatch_once(outbox_database, unavailable)
        assert not dispatch_once(outbox_database, unavailable)
        with outbox_database.begin() as connection:
            row = connection.execute(
                select(
                    OUTBOX.c.attempts,
                    OUTBOX.c.failed_at,
                    OUTBOX.c.available_at > func.now(),
                ).where(OUTBOX.c.event_id == event["event_id"])
            ).one()
            assert row.attempts == attempt
            if attempt < MAX_ATTEMPTS:
                assert row.failed_at is None
                assert row[2]
                connection.execute(
                    OUTBOX.update()
                    .where(OUTBOX.c.event_id == event["event_id"])
                    .values(available_at=func.now())
                )
            else:
                assert row.failed_at is not None

    logs = [
        json.loads(record.getMessage())
        for record in caplog.records
        if record.name == "infrastructure.events.dispatcher"
    ]
    assert [record["retry_delay_seconds"] for record in logs[:-1]] == [1, 2, 4, 8]
    assert logs[-1]["event"] == "outbox_failed"
    assert logs[-1]["correlation_id"] == event["correlation_id"]
    assert "private publisher error" not in caplog.text


def test_dispatcher_republishes_after_interruption(
    outbox_database: Engine, event: dict[str, object], caplog: pytest.LogCaptureFixture
) -> None:
    with outbox_database.begin() as connection:
        append_event(connection, event)
    publish = LocalPublisher(outbox_database)

    def interrupted(envelope: Mapping[str, object]) -> None:
        publish(envelope)
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        dispatch_once(outbox_database, interrupted)

    with caplog.at_level(logging.INFO, logger="infrastructure.events.dispatcher"):
        assert dispatch_once(outbox_database, publish)
    assert "outbox_published" in caplog.text
    assert not dispatch_once(outbox_database, publish)
    with outbox_database.connect() as connection:
        assert connection.scalars(select(DELIVERY.c.envelope)).all() == [event, event]
