import json
import logging
import os
import socket
import subprocess
import sys
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
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
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import IntegrityError

from apps.api.main import app
from apps.market_data.continuous import ingest
from apps.market_data.paper import submit_market_intent
from infrastructure.database.config import local_database_url
from infrastructure.database.market_history import CANDLE, SOURCE, persist_history
from infrastructure.database.market_stream import OBSERVATION, StreamStore
from infrastructure.database.paper_ledger import PaperLedger, market_state_reference
from infrastructure.events.consumer import PROCESSED_EVENT, consume_once
from infrastructure.events.diagnostic_projection import (
    DIAGNOSTIC_COUNT,
    apply_diagnostic_event,
)
from infrastructure.events.dispatcher import MAX_ATTEMPTS, dispatch_once
from infrastructure.events.local_delivery import DELIVERY, LocalPublisher
from infrastructure.events.outbox import OUTBOX, append_event
from infrastructure.security.config import ConfigurationError
from trade_system.control.paper import ControlPolicy, TradingIntent
from trade_system.market_data.binance_archive import collect_day
from trade_system.market_data.binance_stream import Observation
from trade_system.risk.paper import PaperBalance, RiskLimits, SyntheticQuote

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
            == "0009"
        )

    command.downgrade(config, "0008")
    with engine.connect() as connection:
        assert "market_state" not in {
            column["name"]
            for column in inspect(connection).get_columns(
                "paper_fill", schema="trade_system"
            )
        }

    command.downgrade(config, "0007")
    with engine.connect() as connection:
        inspector = inspect(connection)
        assert not inspector.has_table("paper_fill", schema="trade_system")
        assert not inspector.has_table("paper_account", schema="trade_system")

    command.downgrade(config, "0006")
    with engine.connect() as connection:
        assert not inspect(connection).has_table(
            "market_candle_observation", schema="trade_system"
        )

    command.downgrade(config, "0005")
    with engine.connect() as connection:
        inspector = inspect(connection)
        assert not inspector.has_table("market_candle", schema="trade_system")
        assert not inspector.has_table("market_history_source", schema="trade_system")

    command.downgrade(config, "0004")
    with engine.connect() as connection:
        constraints = inspect(connection).get_check_constraints(
            "event_delivery", schema="trade_system"
        )
        assert all(
            check["name"] != "event_delivery_environment_allowed"
            for check in constraints
        )

    command.downgrade(config, "0003")
    with engine.connect() as connection:
        inspector = inspect(connection)
        assert inspector.has_table("event_delivery", schema="trade_system")
        assert "consumed_at" not in {
            column["name"]
            for column in inspector.get_columns("event_delivery", schema="trade_system")
        }
        assert not inspector.has_table("processed_event", schema="trade_system")
        assert not inspector.has_table("diagnostic_event_count", schema="trade_system")

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


def test_duplicate_deliveries_apply_one_effect_across_restarts(
    outbox_database: Engine, event: dict[str, object]
) -> None:
    publish = LocalPublisher(outbox_database)
    publish(event)
    publish(event)

    for outcome in ("delivery_consumed", "delivery_duplicate"):
        result = subprocess.run(
            [sys.executable, "-m", "apps.event_consumer", "--once"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert json.loads(result.stderr)["event"] == outcome

    assert not consume_once(outbox_database, apply_diagnostic_event)
    with outbox_database.connect() as connection:
        assert (
            connection.execute(select(DIAGNOSTIC_COUNT.c.event_count)).scalar_one() == 1
        )
        assert (
            connection.execute(select(PROCESSED_EVENT.c.event_id)).scalar_one()
            == event["event_id"]
        )
        acknowledgements: list[object] = list(
            connection.scalars(select(DELIVERY.c.consumed_at))
        )
        assert len(acknowledgements) == 2
        assert all(timestamp is not None for timestamp in acknowledgements)


def test_consumer_rolls_back_effect_and_deduplication(
    outbox_database: Engine, event: dict[str, object]
) -> None:
    publish = LocalPublisher(outbox_database)
    publish(event)

    def fail_after_effect(
        connection: Connection, envelope: Mapping[str, object]
    ) -> None:
        apply_diagnostic_event(connection, envelope)
        raise RuntimeError("simulated failure after effect")

    with pytest.raises(RuntimeError, match="simulated failure after effect"):
        consume_once(outbox_database, fail_after_effect)

    with outbox_database.connect() as connection:
        assert (
            connection.execute(
                select(DIAGNOSTIC_COUNT.c.event_count)
            ).scalar_one_or_none()
            is None
        )
        assert (
            connection.execute(select(PROCESSED_EVENT.c.event_id)).scalar_one_or_none()
            is None
        )
        assert connection.execute(select(DELIVERY.c.consumed_at)).scalar_one() is None

    assert consume_once(outbox_database, apply_diagnostic_event)
    assert not consume_once(outbox_database, apply_diagnostic_event)
    with outbox_database.connect() as connection:
        assert (
            connection.execute(select(DIAGNOSTIC_COUNT.c.event_count)).scalar_one() == 1
        )
        assert (
            connection.execute(select(PROCESSED_EVENT.c.event_id)).scalar_one()
            == event["event_id"]
        )
        assert (
            connection.execute(select(DELIVERY.c.consumed_at)).scalar_one() is not None
        )


def test_api_readiness_requires_current_migrations(
    postgres: tuple[Config, Engine],
) -> None:
    config, _ = postgres
    with TestClient(app) as client:
        pending = client.get("/readiness")
        assert pending.status_code == 503
        assert pending.json()["checks"] == {"database": "ok", "migrations": "pending"}
        assert client.get("/health").status_code == 200

        command.upgrade(config, "head")
        try:
            ready = client.get("/readiness")
            assert ready.status_code == 200
            assert ready.json() == {
                "schema_version": "1.0.0",
                "status": "ready",
                "checks": {"database": "ok", "migrations": "current"},
            }

            command.downgrade(config, "0003")
            stale = client.get("/readiness")
            assert stale.status_code == 503
            assert stale.json()["checks"] == {"database": "ok", "migrations": "pending"}
        finally:
            command.downgrade(config, "base")


def test_workers_process_only_their_environment(
    outbox_database: Engine, event: dict[str, object], monkeypatch: pytest.MonkeyPatch
) -> None:
    training = {**event, "event_id": "evt_training", "environment_id": "TRAINING"}
    publish = LocalPublisher(outbox_database)

    with outbox_database.begin() as connection:
        append_event(connection, event)
        with pytest.raises(ValueError, match="environment"):
            append_event(connection, training)
    with pytest.raises(ValueError, match="environment"):
        publish(training)

    with monkeypatch.context() as training_policy:
        training_policy.setenv("TRADE_SYSTEM_ENVIRONMENT", "TRAINING")
        with outbox_database.begin() as connection:
            append_event(connection, training)
        assert dispatch_once(outbox_database, publish)
        assert not dispatch_once(outbox_database, publish)

    assert dispatch_once(outbox_database, publish)
    assert not dispatch_once(outbox_database, publish)
    assert consume_once(outbox_database, apply_diagnostic_event)
    assert not consume_once(outbox_database, apply_diagnostic_event)
    with outbox_database.connect() as connection:
        assert (
            connection.execute(select(PROCESSED_EVENT.c.event_id)).scalar_one()
            == event["event_id"]
        )
        assert (
            connection.execute(select(DIAGNOSTIC_COUNT.c.environment_id)).scalar_one()
            == "PAPER"
        )

    monkeypatch.setenv("TRADE_SYSTEM_ENVIRONMENT", "TRAINING")
    assert consume_once(outbox_database, apply_diagnostic_event)
    assert not consume_once(outbox_database, apply_diagnostic_event)
    with outbox_database.connect() as connection:
        counts = connection.execute(
            select(
                DIAGNOSTIC_COUNT.c.environment_id, DIAGNOSTIC_COUNT.c.event_count
            ).order_by(DIAGNOSTIC_COUNT.c.environment_id)
        ).all()
        assert counts == [("PAPER", 1), ("TRAINING", 1)]


def test_postgres_rejects_live_events(
    outbox_database: Engine, event: dict[str, object]
) -> None:
    live = {**event, "environment_id": "LIVE"}
    with pytest.raises(IntegrityError), outbox_database.begin() as connection:
        connection.execute(
            OUTBOX.insert().values(event_id=live["event_id"], envelope=live)
        )
    with pytest.raises(IntegrityError), outbox_database.begin() as connection:
        connection.execute(DELIVERY.insert().values(envelope=live))


def test_correlation_traces_api_dispatcher_and_consumer(
    outbox_database: Engine, event: dict[str, object], caplog: pytest.LogCaptureFixture
) -> None:
    event = {**event, "payload": {"token": "synthetic-private-payload"}}
    with outbox_database.begin() as connection:
        append_event(connection, event)

    with caplog.at_level(logging.INFO), TestClient(app) as client:
        response = client.get("/health", headers={"X-Correlation-ID": "corr_example"})
        assert dispatch_once(outbox_database, LocalPublisher(outbox_database))
        assert consume_once(outbox_database, apply_diagnostic_event)
    assert response.headers["X-Correlation-ID"] == event["correlation_id"]
    components = {
        "apps.api.main",
        "infrastructure.events.dispatcher",
        "infrastructure.events.consumer",
    }
    records = [
        json.loads(record.getMessage())
        for record in caplog.records
        if record.name in components
    ]
    assert [record["event"] for record in records] == [
        "diagnostic_request",
        "outbox_published",
        "delivery_consumed",
    ]
    for record in records:
        assert record["correlation_id"] == event["correlation_id"]
        assert len(record["trace_id"]) == 32
        assert len(record["span_id"]) == 16
        assert record["timestamp"].endswith("+00:00")
    for record in records[1:]:
        assert record["event_id"] == event["event_id"]
        assert record["causation_id"] == event["causation_id"]
    assert "synthetic-private-payload" not in caplog.text


def test_out_of_order_arrival_waits_for_missing_version(
    outbox_database: Engine, event: dict[str, object]
) -> None:
    later = {**event, "event_id": "evt_later", "aggregate_version": 2}
    unrelated = {**event, "event_id": "evt_unrelated", "aggregate_id": "unrelated"}
    publish = LocalPublisher(outbox_database)
    with outbox_database.begin() as connection:
        append_event(connection, later)
        append_event(connection, unrelated)

    assert dispatch_once(outbox_database, publish)
    assert not dispatch_once(outbox_database, publish)
    with outbox_database.connect() as connection:
        assert connection.scalars(select(DELIVERY.c.envelope)).all() == [unrelated]
        waiting = connection.execute(
            select(OUTBOX.c.attempts, OUTBOX.c.published_at).where(
                OUTBOX.c.event_id == later["event_id"]
            )
        ).one()
        assert waiting.attempts == 0
        assert waiting.published_at is None

    with outbox_database.begin() as connection:
        append_event(connection, event)

    assert dispatch_once(outbox_database, publish)
    assert dispatch_once(outbox_database, publish)
    assert not dispatch_once(outbox_database, publish)
    with outbox_database.connect() as connection:
        assert connection.scalars(
            select(DELIVERY.c.envelope).order_by(DELIVERY.c.delivery_id)
        ).all() == [unrelated, event, later]


def test_dispatcher_retry_recovers_after_publisher_unavailability(
    outbox_database: Engine, event: dict[str, object]
) -> None:
    with outbox_database.begin() as connection:
        append_event(connection, event)

    def unavailable(_: Mapping[str, object]) -> None:
        raise ConnectionError("synthetic publisher outage")

    assert dispatch_once(outbox_database, unavailable)
    publish = LocalPublisher(outbox_database)
    assert not dispatch_once(outbox_database, publish)

    with outbox_database.begin() as connection:
        assert (
            connection.execute(select(DELIVERY.c.delivery_id)).scalar_one_or_none()
            is None
        )
        scheduled = connection.execute(
            select(OUTBOX.c.attempts, OUTBOX.c.available_at > func.now())
        ).one()
        assert scheduled == (1, True)
        # Advance the pending retry deterministically without sleeping.
        connection.execute(OUTBOX.update().values(available_at=func.now()))

    assert dispatch_once(outbox_database, publish)
    assert not dispatch_once(outbox_database, publish)
    with outbox_database.connect() as connection:
        assert connection.scalars(select(DELIVERY.c.envelope)).all() == [event]
        recovered = connection.execute(
            select(OUTBOX.c.attempts, OUTBOX.c.published_at, OUTBOX.c.failed_at)
        ).one()
        assert recovered.attempts == 2
        assert recovered.published_at is not None
        assert recovered.failed_at is None


def test_workers_restart_after_database_connection_failure(
    outbox_database: Engine, event: dict[str, object]
) -> None:
    with outbox_database.begin() as connection:
        append_event(connection, event)

    def run_worker(
        module: str, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", module, "--once"],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )

    with socket.socket() as reserved_port:
        reserved_port.bind(("127.0.0.1", 0))
        unreachable = {
            **os.environ,
            "POSTGRES_PORT": str(reserved_port.getsockname()[1]),
        }

        dispatcher = run_worker("apps.event_dispatcher", unreachable)
        assert dispatcher.returncode == 1
        assert json.loads(dispatcher.stderr)["event"] == "worker_failed"
        with outbox_database.connect() as connection:
            assert connection.execute(select(OUTBOX.c.attempts)).scalar_one() == 0
            assert (
                connection.execute(select(DELIVERY.c.delivery_id)).scalar_one_or_none()
                is None
            )

        dispatcher = run_worker("apps.event_dispatcher")
        assert dispatcher.returncode == 0
        assert json.loads(dispatcher.stderr)["event"] == "outbox_published"

        consumer = run_worker("apps.event_consumer", unreachable)
        assert consumer.returncode == 1
        assert json.loads(consumer.stderr)["event"] == "worker_failed"
        with outbox_database.connect() as connection:
            assert (
                connection.execute(select(DELIVERY.c.consumed_at)).scalar_one() is None
            )
            assert (
                connection.execute(
                    select(PROCESSED_EVENT.c.event_id)
                ).scalar_one_or_none()
                is None
            )

    consumer = run_worker("apps.event_consumer")
    assert consumer.returncode == 0
    assert json.loads(consumer.stderr)["event"] == "delivery_consumed"
    with outbox_database.connect() as connection:
        assert (
            connection.execute(select(DELIVERY.c.consumed_at)).scalar_one() is not None
        )
        assert (
            connection.execute(select(DIAGNOSTIC_COUNT.c.event_count)).scalar_one() == 1
        )
        assert (
            connection.execute(select(PROCESSED_EVENT.c.event_id)).scalar_one()
            == event["event_id"]
        )


def history_snapshot(
    output: Path, day: date, market: str, *, opening: str = "2.00000001"
) -> Path:
    scale = 1_000_000 if market == "spot" else 1000
    start = int(datetime(day.year, day.month, day.day, tzinfo=UTC).timestamp()) * scale
    step = 3600 * scale
    stem = f"BTCUSDT-1h-{day.isoformat()}"
    csv = "\n".join(
        f"{tick},{opening},3,1,2.5,5,{tick + step - 1},10,3,4,8,0"
        for tick in range(start, start + step * 24, step)
    )
    zipped = BytesIO()
    with ZipFile(zipped, "w") as archive:
        archive.writestr(stem + ".csv", csv)
    raw = zipped.getvalue()

    def fetch(url: str) -> bytes:
        if url.endswith(".CHECKSUM"):
            return f"{sha256(raw).hexdigest()}  {stem}.zip\n".encode()
        return raw

    return collect_day(
        market=market, day=day, interval="1h", output=output, fetch=fetch
    )


def test_market_history_persists_lineage_and_reimports_idempotently(
    outbox_database: Engine, tmp_path: Path
) -> None:
    days = (date(2025, 11, 9), date(2025, 11, 10))
    for market in ("spot", "futures-um"):
        snapshots = [history_snapshot(tmp_path, day, market) for day in days]
        assert persist_history(outbox_database, snapshots) == (48, 0)
        assert persist_history(outbox_database, snapshots) == (0, 2)

    with outbox_database.connect() as connection:
        assert (
            connection.execute(select(func.count()).select_from(CANDLE)).scalar_one()
            == 96
        )
        assert (
            connection.execute(select(func.count()).select_from(SOURCE)).scalar_one()
            == 4
        )
        sample = connection.execute(
            select(CANDLE.c.open, SOURCE.c.manifest, SOURCE.c.archive_sha256)
            .join_from(
                CANDLE,
                SOURCE,
                (CANDLE.c.market == SOURCE.c.market)
                & (CANDLE.c.symbol == SOURCE.c.symbol)
                & (CANDLE.c.interval == SOURCE.c.interval)
                & (CANDLE.c.day_utc == SOURCE.c.day_utc),
            )
            .where(CANDLE.c.market == "spot")
            .order_by(CANDLE.c.open_time_utc)
            .limit(1)
        ).one()
        assert sample.open == Decimal("2.00000001")
        assert sample.manifest["date_utc"] == "2025-11-09"
        assert sample.archive_sha256 == sample.manifest["sha256"]["source.zip"]


def test_market_history_rejects_gaps_and_changed_files(
    outbox_database: Engine, tmp_path: Path
) -> None:
    early = history_snapshot(tmp_path, date(2025, 11, 8), "spot")
    later = history_snapshot(tmp_path, date(2025, 11, 10), "spot")
    with pytest.raises(ValueError, match="contiguous UTC days"):
        persist_history(outbox_database, [early, later])
    later.with_name("candles.csv").write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        persist_history(outbox_database, [later])

    with outbox_database.connect() as connection:
        assert (
            connection.execute(select(func.count()).select_from(SOURCE)).scalar_one()
            == 0
        )
        assert (
            connection.execute(select(func.count()).select_from(CANDLE)).scalar_one()
            == 0
        )


def test_market_history_rolls_back_window_on_source_revision(
    outbox_database: Engine, tmp_path: Path
) -> None:
    day = date(2025, 11, 10)
    original = history_snapshot(tmp_path, day, "spot")
    earlier = history_snapshot(tmp_path, date(2025, 11, 9), "spot")
    changed = history_snapshot(tmp_path, day, "spot", opening="2.20")
    assert persist_history(outbox_database, [original]) == (24, 0)
    with pytest.raises(ValueError, match="Source changed"):
        persist_history(outbox_database, [earlier, changed])
    with outbox_database.connect() as connection:
        assert connection.execute(select(SOURCE.c.day_utc)).scalar_one() == day
        assert (
            connection.execute(select(func.count()).select_from(CANDLE)).scalar_one()
            == 24
        )


def observed(opened: datetime, step: timedelta, kind: str) -> Observation:
    values = tuple(
        Decimal(value) for value in ("2.00000001", "3", "1", "2.5", "5", "10", "4", "8")
    )
    return Observation(
        opened,
        opened + step,
        values,
        3,
        kind,
        "https://example.invalid",
        opened + step,
        {"fixture": True},
    )


@pytest.mark.parametrize("market", ["spot", "futures-um"])
def test_stream_reconnect_recovers_postgres_gap_and_resumes(
    outbox_database: Engine, market: str
) -> None:
    start = datetime(2025, 11, 10, tzinfo=UTC)
    step = timedelta(minutes=5)
    clock = start + step
    sleeps: list[float] = []
    store = StreamStore(outbox_database, market, "5m")

    class Feed:
        def __init__(self) -> None:
            self.step = step
            self.connections = 0

        @contextmanager
        def stream(self) -> Iterator[Iterator[Observation | None]]:
            self.connections += 1

            def messages() -> Iterator[Observation | None]:
                yield None
                if self.connections == 1:
                    yield observed(start + step, step, "websocket")
                    raise ConnectionError("synthetic disconnect")
                yield observed(start + 3 * step, step, "websocket")
                yield observed(start + 4 * step, step, "websocket")
                raise KeyboardInterrupt

            yield messages()

        def backfill(self, first: datetime, end: datetime) -> list[Observation]:
            count = (end - first) // step
            if self.connections == 2:
                count -= 1
            return [observed(first + i * step, step, "rest") for i in range(count)]

    def advance(seconds: float) -> None:
        nonlocal clock
        sleeps.append(seconds)
        if len(sleeps) == 1:
            clock = start + 4 * step
        else:
            assert store.latest() == start + step

    feed = Feed()
    with pytest.raises(KeyboardInterrupt):
        ingest(feed, store, now=lambda: clock, sleep=advance)
    assert sleeps == [1, 2]
    assert feed.connections == 3

    class RestartedFeed(Feed):
        @contextmanager
        def stream(self) -> Iterator[Iterator[Observation | None]]:
            yield iter([observed(start + 6 * step, step, "websocket")])

    ingest(
        RestartedFeed(),
        StreamStore(outbox_database, market, "5m"),
        once=True,
        now=lambda: start + 6 * step,
    )
    with outbox_database.connect() as connection:
        rows = connection.execute(
            select(OBSERVATION.c.open_time_utc, OBSERVATION.c.source_kind).order_by(
                OBSERVATION.c.open_time_utc
            )
        ).all()
        assert [row.open_time_utc for row in rows] == [
            start + i * step for i in range(7)
        ]
        assert [row.source_kind for row in rows] == [
            "rest",
            "websocket",
            "rest",
            "rest",
            "websocket",
            "rest",
            "websocket",
        ]
        assert (
            connection.execute(select(func.count()).select_from(CANDLE)).scalar_one()
            == 7
        )


def test_archive_reconciles_with_existing_stream_candle(
    outbox_database: Engine, tmp_path: Path
) -> None:
    start = datetime(2025, 11, 10, tzinfo=UTC)
    first = observed(start, timedelta(hours=1), "websocket")
    store = StreamStore(outbox_database, "spot", "1h")
    store.persist([first])
    snapshot = history_snapshot(tmp_path, start.date(), "spot")
    assert persist_history(outbox_database, [snapshot]) == (23, 0)
    assert persist_history(outbox_database, [snapshot]) == (0, 1)
    with outbox_database.connect() as connection:
        assert (
            connection.execute(select(func.count()).select_from(CANDLE)).scalar_one()
            == 24
        )
        assert (
            connection.execute(select(SOURCE.c.archive_sha256)).scalar_one() is not None
        )
        assert (
            connection.execute(select(OBSERVATION.c.source_kind)).scalar_one()
            == "websocket"
        )


def paper_ledger(engine: Engine) -> PaperLedger:
    return PaperLedger(
        engine,
        ControlPolicy("paper-test", frozenset({"actor-test"}), paused=False),
        RiskLimits(Decimal("200"), Decimal("0.02"), timedelta(seconds=2)),
    )


def test_paper_fill_survives_process_restart_and_reconciles(
    outbox_database: Engine,
) -> None:
    ledger = paper_ledger(outbox_database)
    ledger.open_account(PaperBalance(Decimal("1000"), Decimal(0)))
    script = """
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from infrastructure.database.config import local_database_url
from infrastructure.database.paper_ledger import PaperLedger, market_state_reference
from trade_system.control.paper import ControlPolicy, TradingIntent
from trade_system.risk.paper import RiskLimits, SyntheticQuote

now = datetime(2025, 11, 10, tzinfo=UTC)
engine = create_engine(local_database_url(), hide_parameters=True)
try:
    ledger = PaperLedger(
        engine, ControlPolicy("paper-test", frozenset({"actor-test"}), paused=False),
        RiskLimits(Decimal("200"), Decimal("0.02"), timedelta(seconds=2)),
    )
    intent = TradingIntent(
        "paper-intent", "paper-correlation", "paper-test", "actor-test",
        "PAPER", "BTCUSDT", "BUY", Decimal("0.01"), now, now + timedelta(seconds=5),
    )
    quote = SyntheticQuote("synthetic-quote", "BTCUSDT", Decimal("10000.12345678"), now)
    fill = ledger.submit(intent, quote, now)
    print(fill.intent_id, fill.correlation_id, fill.notional, fill.balance_after.cash)
finally:
    engine.dispose()
"""
    outputs = [
        subprocess.run(
            [sys.executable, "-c", script],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        ).stdout.strip()
        for _ in range(2)
    ]
    assert (
        outputs == ["paper-intent paper-correlation 100.0012345678 899.9987654322"] * 2
    )
    reconciliation = ledger.reconcile()
    assert reconciliation.consistent
    assert reconciliation.fills == 1
    assert reconciliation.expected == PaperBalance(
        Decimal("899.9987654322"), Decimal("0.01")
    )
    with outbox_database.begin() as connection:
        connection.execute(
            text("UPDATE trade_system.paper_fill SET cash_after = cash_after + 1")
        )
        connection.execute(
            text("UPDATE trade_system.paper_account SET cash = cash + 1")
        )
    report = ledger.reconcile()
    assert not report.consistent
    assert report.first_divergent_fill == "paper-intent"
    assert report.stored.cash - report.expected.cash == Decimal(1)


def test_paper_fill_and_balance_roll_back_together(outbox_database: Engine) -> None:
    ledger = paper_ledger(outbox_database)
    opening = PaperBalance(Decimal(1000), Decimal(0))
    ledger.open_account(opening)
    with outbox_database.begin() as connection:
        connection.execute(
            text("ALTER TABLE trade_system.paper_account ADD CHECK (cash >= 1000)")
        )

    now = datetime(2025, 11, 10, tzinfo=UTC)
    intent = TradingIntent(
        "paper-intent",
        "paper-correlation",
        "paper-test",
        "actor-test",
        "PAPER",
        "BTCUSDT",
        "BUY",
        Decimal("0.01"),
        now,
        now + timedelta(seconds=5),
    )
    quote = SyntheticQuote("synthetic-quote", "BTCUSDT", Decimal(10000), now)
    with pytest.raises(IntegrityError):
        ledger.submit(intent, quote, now)
    report = ledger.reconcile()
    assert report.consistent and report.fills == 0 and report.stored == opening


def test_paper_ledger_blocks_live(
    outbox_database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    ledger = paper_ledger(outbox_database)
    monkeypatch.setenv("TRADE_SYSTEM_ENVIRONMENT", "LIVE")
    with pytest.raises(ConfigurationError):
        ledger.open_account(PaperBalance(Decimal(1000), Decimal(0)))
    with outbox_database.connect() as connection:
        assert (
            connection.execute(
                text("SELECT count(*) FROM trade_system.paper_account")
            ).scalar_one()
            == 0
        )


def test_paper_market_state_obeys_decision_cutoff_and_preserves_evidence(
    outbox_database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    close_at = datetime(2025, 11, 10, 22, 35, tzinfo=UTC)
    ready_at = close_at + timedelta(seconds=3)
    execution_at = close_at + timedelta(seconds=4)
    for interval, minutes in (("1m", 1), ("5m", 5), ("15m", 15), ("1h", 60)):
        step = timedelta(minutes=minutes)
        cutoff = close_at.replace(minute=close_at.minute // minutes * minutes)
        stream = StreamStore(outbox_database, "spot", interval)
        stream.persist(
            [
                observed(cutoff - index * step, step, "websocket")
                for index in range(21, 0, -1)
            ]
        )

    with outbox_database.begin() as connection:
        connection.execute(
            OBSERVATION.update().values(
                available_at=close_at + timedelta(seconds=1),
                received_at=close_at + timedelta(seconds=1),
            )
        )
        connection.execute(
            OBSERVATION.update()
            .where(
                OBSERVATION.c.interval == "5m",
                OBSERVATION.c.open_time_utc == close_at - timedelta(minutes=5),
            )
            .values(available_at=ready_at, received_at=ready_at)
        )

    ledger = PaperLedger(
        outbox_database,
        ControlPolicy("paper-test", frozenset({"actor-test"}), paused=False),
        RiskLimits(Decimal("200"), Decimal("0.02"), timedelta(seconds=5)),
    )
    opening = PaperBalance(Decimal("1000"), Decimal(0))
    ledger.open_account(opening)
    intent = TradingIntent(
        "market-intent",
        "market-correlation",
        "paper-test",
        "actor-test",
        "PAPER",
        "BTCUSDT",
        "BUY",
        Decimal("0.01"),
        close_at + timedelta(seconds=2),
        close_at + timedelta(seconds=30),
    )

    with pytest.raises(ValueError, match="5m:"):
        submit_market_intent(ledger, intent, close_at=close_at, now=execution_at)
    with pytest.raises(ValueError, match="close_at <= as_of"):
        submit_market_intent(
            ledger, intent, close_at=close_at + timedelta(minutes=5), now=execution_at
        )
    assert ledger.reconcile().stored == opening and ledger.reconcile().fills == 0

    intent = replace(intent, issued_at=execution_at)
    with pytest.raises(ValueError, match="risk: invalid_or_stale_quote"):
        submit_market_intent(
            ledger, intent, close_at=close_at, now=close_at + timedelta(seconds=6)
        )
    fill = submit_market_intent(ledger, intent, close_at=close_at, now=execution_at)
    assert fill.price == Decimal("2.5") and fill.notional == Decimal("0.025")
    assert fill.balance_after == PaperBalance(Decimal("999.975"), Decimal("0.01"))
    with outbox_database.connect() as connection:
        evidence: dict[str, object] = connection.execute(
            text("SELECT market_state FROM trade_system.paper_fill")
        ).scalar_one()
        assert evidence["close_at"] == close_at.isoformat()
        assert evidence["as_of"] == execution_at.isoformat()
        intervals = evidence["intervals"]
        assert isinstance(intervals, dict)
        assert sum(len(window["lineage"]) for window in intervals.values()) == 84
        assert fill.quote_reference == market_state_reference(evidence)

    def forbidden_read(*args: object, **kwargs: object) -> None:
        pytest.fail("Market State was read before Control or during replay.")

    monkeypatch.setattr("apps.market_data.paper.read_state", forbidden_read)
    restarted = PaperLedger(outbox_database, ledger.control, ledger.limits)
    assert (
        submit_market_intent(restarted, intent, close_at=close_at, now=execution_at)
        == fill
    )
    with pytest.raises(ValueError, match="conflicting_intent_id"):
        submit_market_intent(
            restarted,
            intent,
            close_at=close_at - timedelta(minutes=5),
            now=execution_at,
        )
    with pytest.raises(ValueError, match="control: paper_required"):
        submit_market_intent(
            restarted,
            replace(intent, environment_id="LIVE"),
            close_at=close_at,
            now=execution_at,
        )
    assert restarted.reconcile().consistent and restarted.reconcile().fills == 1
    with outbox_database.begin() as connection:
        connection.execute(
            text(
                """UPDATE trade_system.paper_fill
               SET market_state = market_state
               || '{"schema_version":"tampered"}'::jsonb"""
            )
        )
    assert restarted.reconcile().first_divergent_fill == intent.intent_id
    with outbox_database.begin() as connection:
        connection.execute(
            text("UPDATE trade_system.paper_fill SET market_state = NULL")
        )
    assert restarted.reconcile().first_divergent_fill == intent.intent_id
