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
from apps.market_data.funding import collect_funding
from apps.market_data.liquidation import poll_mark
from apps.market_data.paper import submit_futures_market_intent, submit_market_intent
from infrastructure.database.config import local_database_url
from infrastructure.database.market_history import CANDLE, SOURCE, persist_history
from infrastructure.database.market_stream import OBSERVATION, StreamStore
from infrastructure.database.paper_futures import PaperFuturesLedger
from infrastructure.database.paper_ledger import PaperLedger, market_state_reference
from infrastructure.database.paper_mark_history import (
    IncompleteMarkHistory,
    read_mark_history,
    recover_mark_history,
)
from infrastructure.events.consumer import PROCESSED_EVENT, consume_once
from infrastructure.events.diagnostic_projection import (
    DIAGNOSTIC_COUNT,
    apply_diagnostic_event,
)
from infrastructure.events.dispatcher import MAX_ATTEMPTS, dispatch_once
from infrastructure.events.local_delivery import DELIVERY, LocalPublisher
from infrastructure.events.outbox import OUTBOX, append_event
from infrastructure.security.config import ConfigurationError
from trade_system.control.paper import ControlPolicy, Side, TradingIntent
from trade_system.market_data.binance_archive import collect_day
from trade_system.market_data.binance_mark import MarkCandle
from trade_system.market_data.binance_stream import Observation
from trade_system.risk.execution_costs import ExecutionCosts
from trade_system.risk.futures import (
    FundingObservation,
    FuturesBalance,
    LiquidationMark,
)
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
            == "0015"
        )

    command.downgrade(config, "0014")
    with engine.connect() as connection:
        assert not inspect(connection).has_table(
            "paper_mark_candle", schema="trade_system"
        )
    command.downgrade(config, "0013")
    with engine.connect() as connection:
        assert not inspect(connection).has_table(
            "paper_futures_liquidation", schema="trade_system"
        )
    command.downgrade(config, "0012")
    with engine.connect() as connection:
        assert not inspect(connection).has_table(
            "paper_futures_funding", schema="trade_system"
        )
    command.downgrade(config, "0011")
    with engine.connect() as connection:
        columns = inspect(connection).get_columns(
            "paper_futures_fill", schema="trade_system"
        )
        assert "market_state" not in {column["name"] for column in columns}

    command.downgrade(config, "0010")
    with engine.connect() as connection:
        assert not inspect(connection).has_table(
            "paper_futures_fill", schema="trade_system"
        )

    command.downgrade(config, "0009")
    with engine.connect() as connection:
        columns = inspect(connection).get_columns("paper_fill", schema="trade_system")
        assert "fee" not in {column["name"] for column in columns}

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
from infrastructure.database.paper_futures import PaperFuturesLedger
from infrastructure.database.paper_ledger import PaperLedger, market_state_reference
from trade_system.control.paper import ControlPolicy, TradingIntent
from trade_system.risk.execution_costs import ExecutionCosts
from trade_system.risk.futures import FuturesBalance
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


def seed_paper_market_state(
    engine: Engine, market: str, close_at: datetime, ready_at: datetime
) -> None:
    for interval, minutes in (("1m", 1), ("5m", 5), ("15m", 15), ("1h", 60)):
        step = timedelta(minutes=minutes)
        cutoff = close_at.replace(minute=close_at.minute // minutes * minutes)
        stream = StreamStore(engine, market, interval)
        stream.persist(
            [
                observed(cutoff - index * step, step, "websocket")
                for index in range(21, 0, -1)
            ]
        )

    with engine.begin() as connection:
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


def test_paper_market_state_obeys_decision_cutoff_and_preserves_evidence(
    outbox_database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    close_at = datetime(2025, 11, 10, 22, 35, tzinfo=UTC)
    ready_at = close_at + timedelta(seconds=3)
    execution_at = close_at + timedelta(seconds=4)
    seed_paper_market_state(outbox_database, "spot", close_at, ready_at)

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


def test_paper_costed_fills_replay_and_reconcile(outbox_database: Engine) -> None:
    baseline = paper_ledger(outbox_database)
    costs = ExecutionCosts(fee_bps=Decimal(10), slippage_bps=Decimal(100))
    ledger = PaperLedger(
        outbox_database, baseline.control, baseline.limits, costs=costs
    )
    ledger.open_account(PaperBalance(Decimal(1000), Decimal(0)))
    now = datetime(2025, 11, 10, tzinfo=UTC)
    buy = TradingIntent(
        "costed-buy",
        "cost-correlation",
        "paper-test",
        "actor-test",
        "PAPER",
        "BTCUSDT",
        "BUY",
        Decimal("0.01"),
        now,
        now + timedelta(seconds=5),
    )
    quote = SyntheticQuote("cost-quote", "BTCUSDT", Decimal(10000), now)
    bought = ledger.submit(buy, quote, now)
    assert bought.reference_price == Decimal(10000)
    assert bought.price == Decimal(10100)
    assert bought.notional == Decimal(101)
    assert bought.fee == Decimal("0.101")
    assert bought.balance_after == PaperBalance(Decimal("898.899"), Decimal("0.01"))

    restarted = PaperLedger(outbox_database, ledger.control, ledger.limits)
    assert restarted.submit(buy, quote, now) == bought

    sold = ledger.submit(replace(buy, intent_id="costed-sell", side="SELL"), quote, now)
    assert sold.price == Decimal(9900)
    assert sold.notional == Decimal(99)
    assert sold.fee == Decimal("0.099")
    report = restarted.reconcile()
    assert report.consistent and report.fills == 2
    assert report.expected == PaperBalance(Decimal("997.800"), Decimal(0))

    with outbox_database.begin() as connection:
        connection.execute(
            text(
                "UPDATE trade_system.paper_fill SET fee = fee + 0.001 "
                "WHERE intent_id = 'costed-buy'"
            )
        )
    assert restarted.reconcile().first_divergent_fill == "costed-buy"


def test_paper_risk_uses_slipped_notional_and_fee(outbox_database: Engine) -> None:
    baseline = paper_ledger(outbox_database)
    costs = ExecutionCosts(fee_bps=Decimal(10), slippage_bps=Decimal(100))
    ledger = PaperLedger(
        outbox_database, baseline.control, baseline.limits, costs=costs
    )
    opening = PaperBalance(Decimal("101.05"), Decimal(0))
    ledger.open_account(opening)
    now = datetime(2025, 11, 10, tzinfo=UTC)
    intent = TradingIntent(
        "costed-buy",
        "cost-correlation",
        "paper-test",
        "actor-test",
        "PAPER",
        "BTCUSDT",
        "BUY",
        Decimal("0.01"),
        now,
        now + timedelta(seconds=5),
    )
    quote = SyntheticQuote("cost-quote", "BTCUSDT", Decimal(10000), now)
    limited = PaperLedger(
        outbox_database,
        ledger.control,
        replace(ledger.limits, max_order_notional=Decimal("100.50")),
        costs=costs,
    )
    with pytest.raises(ValueError, match="risk: order_limit"):
        limited.submit(intent, quote, now)
    with pytest.raises(ValueError, match="risk: insufficient_cash"):
        ledger.submit(intent, quote, now)
    report = ledger.reconcile()
    assert report.consistent and report.fills == 0 and report.stored == opening


def test_futures_long_and_short_fills_reconcile(outbox_database: Engine) -> None:
    baseline = paper_ledger(outbox_database)
    costs = ExecutionCosts(fee_bps=Decimal(10), slippage_bps=Decimal(100))
    ledger = PaperFuturesLedger(
        outbox_database, baseline.control, baseline.limits, costs=costs
    )
    ledger.open_account(Decimal(1000))
    now = datetime(2025, 11, 10, tzinfo=UTC)
    intent = TradingIntent(
        "long-open",
        "futures-correlation",
        "paper-test",
        "actor-test",
        "PAPER",
        "BTCUSDT",
        "BUY",
        Decimal("0.01"),
        now,
        now + timedelta(seconds=5),
    )
    quote = SyntheticQuote("futures-reference", "BTCUSDT", Decimal(10000), now)
    opened = ledger.submit(intent, quote, now, reduce_only=False)
    assert opened.after == FuturesBalance(
        Decimal("898.899"), Decimal("0.01"), Decimal(10100), Decimal(101)
    )

    restarted = PaperFuturesLedger(outbox_database, ledger.control, ledger.limits)
    assert restarted.submit(intent, quote, now, reduce_only=False) == opened
    with pytest.raises(ValueError, match="conflicting_intent_id"):
        restarted.submit(intent, quote, now, reduce_only=True)
    with pytest.raises(ValueError, match="full_reduce_only_required"):
        ledger.submit(
            replace(
                intent, intent_id="partial", side="SELL", quantity=Decimal("0.005")
            ),
            quote,
            now,
            reduce_only=True,
        )

    closed = ledger.submit(
        replace(intent, intent_id="long-close", side="SELL"),
        replace(quote, price=Decimal(11000)),
        now,
        reduce_only=True,
    )
    assert closed.realized_pnl == Decimal("7.9") and closed.fee == Decimal("0.1089")
    assert closed.after == FuturesBalance(
        Decimal("1007.6901"), realized_pnl=Decimal("7.9")
    )

    short = ledger.submit(
        replace(intent, intent_id="short-open", side="SELL"),
        quote,
        now,
        reduce_only=False,
    )
    assert short.after.quantity == Decimal("-0.01")
    assert short.after.margin == Decimal(99)
    with pytest.raises(ValueError, match="isolated_margin_exhausted"):
        ledger.submit(
            replace(intent, intent_id="short-exhausted"),
            replace(quote, price=Decimal(22000)),
            now,
            reduce_only=True,
        )
    covered = ledger.submit(
        replace(intent, intent_id="short-close"),
        replace(quote, price=Decimal(9000)),
        now,
        reduce_only=True,
    )
    assert covered.realized_pnl == Decimal("8.1") and covered.fee == Decimal("0.0909")
    report = restarted.reconcile()
    assert report.consistent and report.fills == 4
    assert report.expected == FuturesBalance(
        Decimal("1015.6002"), realized_pnl=Decimal(16)
    )
    assert covered.after == report.expected

    with outbox_database.begin() as connection:
        connection.execute(
            text("""
            UPDATE trade_system.paper_futures_fill
            SET fill = fill || '{"fee":"0"}'::jsonb WHERE intent_id = 'short-close'
        """)
        )
    assert restarted.reconcile().first_divergent_fill == "short-close"


def test_futures_blocks_live_and_insufficient_collateral(
    outbox_database: Engine,
) -> None:
    baseline = paper_ledger(outbox_database)
    ledger = PaperFuturesLedger(outbox_database, baseline.control, baseline.limits)
    ledger.open_account(Decimal(99))
    now = datetime(2025, 11, 10, tzinfo=UTC)
    intent = TradingIntent(
        "futures-blocked",
        "futures-correlation",
        "paper-test",
        "actor-test",
        "PAPER",
        "BTCUSDT",
        "SELL",
        Decimal("0.01"),
        now,
        now + timedelta(seconds=5),
    )
    quote = SyntheticQuote("futures-reference", "BTCUSDT", Decimal(10000), now)
    with pytest.raises(ValueError, match="control: paper_required"):
        ledger.submit(
            replace(intent, environment_id="LIVE"), quote, now, reduce_only=False
        )
    with pytest.raises(ValueError, match="insufficient_futures_collateral"):
        ledger.submit(intent, quote, now, reduce_only=False)
    report = ledger.reconcile()
    assert (
        report.consistent
        and report.fills == 0
        and report.stored == FuturesBalance(Decimal(99))
    )


def test_futures_market_state_cutoff_and_reconciliation(
    outbox_database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    close_at = datetime(2025, 11, 10, 22, 35, tzinfo=UTC)
    ready_at = close_at + timedelta(seconds=3)
    now = close_at + timedelta(seconds=4)
    seed_paper_market_state(outbox_database, "futures-um", close_at, ready_at)
    ledger = PaperFuturesLedger(
        outbox_database,
        ControlPolicy("paper-test", frozenset({"actor-test"}), paused=False),
        RiskLimits(Decimal("200"), Decimal("0.02"), timedelta(seconds=5)),
    )
    opening = FuturesBalance(Decimal("1000"))
    ledger.open_account(opening.cash)
    intent = TradingIntent(
        "futures-state-open",
        "futures-state-correlation",
        "paper-test",
        "actor-test",
        "PAPER",
        "BTCUSDT",
        "SELL",
        Decimal("0.01"),
        close_at + timedelta(seconds=2),
        close_at + timedelta(seconds=30),
    )

    with pytest.raises(ValueError, match="5m:"):
        submit_futures_market_intent(
            ledger, intent, close_at=close_at, now=now, reduce_only=False
        )
    with pytest.raises(ValueError, match="close_at <= as_of"):
        submit_futures_market_intent(
            ledger,
            intent,
            close_at=close_at + timedelta(minutes=5),
            now=now,
            reduce_only=False,
        )
    intent = replace(intent, issued_at=ready_at)
    with pytest.raises(ValueError, match="risk: invalid_or_stale_quote"):
        submit_futures_market_intent(
            ledger,
            intent,
            close_at=close_at,
            now=close_at + timedelta(seconds=6),
            reduce_only=False,
        )
    report = ledger.reconcile()
    assert report.consistent and report.fills == 0 and report.stored == opening

    opened = submit_futures_market_intent(
        ledger, intent, close_at=close_at, now=now, reduce_only=False
    )
    assert opened.price == Decimal("2.5")
    assert opened.after == FuturesBalance(
        Decimal("999.975"), Decimal("-0.01"), Decimal("2.5"), Decimal("0.025")
    )
    closed = submit_futures_market_intent(
        ledger,
        replace(intent, intent_id="futures-state-close", side="BUY"),
        close_at=close_at,
        now=now,
        reduce_only=True,
    )
    assert closed.price == Decimal("2.5") and closed.after == opening
    with outbox_database.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT market_state, quote_reference "
                "FROM trade_system.paper_futures_fill"
            )
        ).all()
    assert len(rows) == 2
    for evidence, reference in rows:
        assert isinstance(evidence, dict)
        assert evidence["market"] == "futures-um"
        assert evidence["close_at"] == close_at.isoformat()
        assert evidence["as_of"] == ready_at.isoformat()
        assert set(evidence["intervals"]) == {"1m", "5m", "15m", "1h"}
        assert (
            sum(len(window["lineage"]) for window in evidence["intervals"].values())
            == 84
        )
        assert reference == market_state_reference(evidence)

    def forbidden_read(*args: object, **kwargs: object) -> None:
        pytest.fail("Market State was read before Control or during replay.")

    monkeypatch.setattr("apps.market_data.paper.read_state", forbidden_read)
    restarted = PaperFuturesLedger(outbox_database, ledger.control, ledger.limits)
    assert (
        submit_futures_market_intent(
            restarted, intent, close_at=close_at, now=now, reduce_only=False
        )
        == opened
    )
    with pytest.raises(ValueError, match="conflicting_intent_id"):
        submit_futures_market_intent(
            restarted,
            intent,
            close_at=close_at - timedelta(minutes=5),
            now=now,
            reduce_only=False,
        )
    with pytest.raises(ValueError, match="control: paper_required"):
        submit_futures_market_intent(
            restarted,
            replace(intent, environment_id="LIVE"),
            close_at=close_at,
            now=now,
            reduce_only=False,
        )
    report = restarted.reconcile()
    assert report.consistent and report.fills == 2 and report.stored == opening
    with outbox_database.begin() as connection:
        connection.execute(
            text(
                "UPDATE trade_system.paper_futures_fill SET market_state = NULL "
                "WHERE intent_id = :intent_id"
            ),
            {"intent_id": intent.intent_id},
        )
    assert restarted.reconcile().first_divergent_fill == intent.intent_id


@pytest.mark.parametrize(("side", "delta"), [("BUY", "-0.02"), ("SELL", "0.02")])
def test_futures_funding_cutoff_replay_and_reconciliation(
    outbox_database: Engine, monkeypatch: pytest.MonkeyPatch, side: Side, delta: str
) -> None:
    baseline = paper_ledger(outbox_database)
    ledger = PaperFuturesLedger(outbox_database, baseline.control, baseline.limits)
    ledger.open_account(Decimal(1000))
    opened_at = datetime(2025, 11, 10, 15, 59, 59, tzinfo=UTC)
    funding_at = opened_at + timedelta(seconds=1)
    available_at = funding_at + timedelta(seconds=2)
    intent = TradingIntent(
        "funding-open",
        "funding-correlation",
        "paper-test",
        "actor-test",
        "PAPER",
        "BTCUSDT",
        side,
        Decimal("0.01"),
        opened_at,
        opened_at + timedelta(minutes=1),
    )
    quote = SyntheticQuote("funding-fixture", "BTCUSDT", Decimal(10000), opened_at)
    opened = ledger.submit(intent, quote, opened_at, reduce_only=False)
    event = FundingObservation(
        funding_at, available_at, Decimal(20000), Decimal("0.0001"), "fixture:funding"
    )

    try:
        for cutoff in (opened_at, funding_at, available_at.replace(tzinfo=None)):
            with pytest.raises(ValueError, match="funding: invalid_cutoff"):
                ledger.apply_funding(event, as_of=cutoff)
        with pytest.raises(ValueError, match="funding: out_of_order"):
            ledger.apply_funding(
                replace(event, funding_at=opened_at), as_of=available_at
            )
        with pytest.raises(ValueError, match="funding: invalid_observation"):
            ledger.apply_funding(
                replace(event, rate=Decimal("NaN")), as_of=available_at
            )
        assert ledger.reconcile().stored == opened.after
        assert ledger.reconcile().funding_entries == 0

        settled = ledger.apply_funding(event, as_of=available_at)
        assert settled.cash_delta == Decimal(delta)
        assert settled.after == replace(
            opened.after, cash=Decimal(900) + Decimal(delta)
        )
        restarted = PaperFuturesLedger(outbox_database, ledger.control, ledger.limits)
        with pytest.raises(ValueError, match="funding: conflicting_observation"):
            restarted.apply_funding(replace(event, rate=Decimal(0)), as_of=available_at)
        closing = replace(
            intent, intent_id="funding-close", side="SELL" if side == "BUY" else "BUY"
        )
        with pytest.raises(ValueError, match="funding: fill_precedes_settlement"):
            restarted.submit(closing, quote, funding_at, reduce_only=True)
        closed = restarted.submit(
            closing,
            replace(quote, observed_at=available_at),
            available_at,
            reduce_only=True,
        )
        assert closed.after == FuturesBalance(Decimal(1000) + Decimal(delta))
        assert restarted.apply_funding(event, as_of=available_at) == settled

        flat_at = available_at + timedelta(seconds=1)
        flat_event = replace(event, funding_at=flat_at, available_at=flat_at)
        assert restarted.apply_funding(flat_event, as_of=flat_at).cash_delta == 0
        report = restarted.reconcile()
        assert report.consistent and report.fills == 2 and report.funding_entries == 2
        assert report.stored == closed.after

        with monkeypatch.context() as scope:
            scope.setenv("TRADE_SYSTEM_ENVIRONMENT", "TRAINING")
            with pytest.raises(ConfigurationError, match="requires the PAPER"):
                restarted.apply_funding(flat_event, as_of=flat_at)

        with outbox_database.begin() as connection:
            connection.execute(
                text(
                    "UPDATE trade_system.paper_futures_funding SET cash_delta = 0 "
                    "WHERE funding_at = :funding_at"
                ),
                {"funding_at": funding_at},
            )
        report = restarted.reconcile()
        assert not report.consistent and report.first_divergent_funding_at == funding_at
    finally:
        # The disposable fixture downgrades to base; discard its funding entries first.
        with outbox_database.begin() as connection:
            connection.execute(text("DELETE FROM trade_system.paper_futures_funding"))


def test_funding_collector_resumes_after_partial_run(outbox_database: Engine) -> None:
    baseline = paper_ledger(outbox_database)
    ledger = PaperFuturesLedger(outbox_database, baseline.control, baseline.limits)
    ledger.open_account(Decimal(1000))
    opened_at = datetime(2025, 11, 10, 15, 59, 59, tzinfo=UTC)
    first_at = opened_at + timedelta(seconds=1)
    second_at = first_at + timedelta(hours=8)
    received = second_at + timedelta(seconds=1)
    start = int(first_at.timestamp() * 1000)
    next_start = int(second_at.timestamp() * 1000)
    end = int(received.timestamp() * 1000)
    intent = TradingIntent(
        "collected-funding-open",
        "funding-correlation",
        "paper-test",
        "actor-test",
        "PAPER",
        "BTCUSDT",
        "BUY",
        Decimal("0.01"),
        opened_at,
        opened_at + timedelta(minutes=1),
    )
    ledger.submit(
        intent,
        SyntheticQuote("fixture", "BTCUSDT", Decimal(10000), opened_at),
        opened_at,
        reduce_only=False,
    )
    first = FundingObservation(
        first_at, received, Decimal(20000), Decimal("0.0001"), "fixture:first"
    )
    second = replace(first, funding_at=second_at, reference="fixture:second")

    def interrupted(lower: int, upper: int) -> list[FundingObservation]:
        assert upper == end
        if lower == start:
            return [first]
        assert lower == start + 1
        raise ConnectionError("fixture: response interrupted")

    def recovered(lower: int, upper: int) -> list[FundingObservation]:
        assert upper == end
        if lower == start + 1:
            return [second]
        assert lower == next_start + 1
        return []

    try:
        with pytest.raises(ValueError, match="observation_outside_window"):
            collect_funding(
                outbox_database,
                intent.account_id,
                start=first_at,
                fetch=lambda _a, _b: [
                    first,
                    replace(
                        second,
                        funding_at=received + timedelta(seconds=1),
                        available_at=received + timedelta(seconds=1),
                    ),
                ],
                now=iter((received, received + timedelta(seconds=1))).__next__,
            )
        with pytest.raises(ValueError, match="funding: invalid_cutoff"):
            collect_funding(
                outbox_database,
                intent.account_id,
                start=first_at,
                fetch=lambda _a, _b: [
                    replace(first, available_at=received + timedelta(seconds=1))
                ],
                now=lambda: received,
            )
        assert ledger.reconcile().funding_entries == 0
        with pytest.raises(ConnectionError, match="response interrupted"):
            collect_funding(
                outbox_database,
                intent.account_id,
                start=first_at,
                fetch=interrupted,
                now=lambda: received,
            )
        assert ledger.reconcile().funding_entries == 1

        restarted_engine = create_engine(outbox_database.url)
        try:
            assert (
                collect_funding(
                    restarted_engine,
                    intent.account_id,
                    start=first_at,
                    fetch=recovered,
                    now=lambda: received,
                )
                == 1
            )
            assert (
                collect_funding(
                    restarted_engine,
                    intent.account_id,
                    start=first_at,
                    fetch=recovered,
                    now=lambda: received,
                )
                == 0
            )
        finally:
            restarted_engine.dispose()
        report = ledger.reconcile()
        assert report.consistent and report.funding_entries == 2
        assert report.stored.cash == Decimal("899.96")
    finally:
        with outbox_database.begin() as connection:
            connection.execute(text("DELETE FROM trade_system.paper_futures_funding"))


@pytest.mark.parametrize(
    ("price", "equity", "maintenance", "released"),
    [("16000", "40", "40", "40"), ("21000", "-10", "52.5", "0")],
)
def test_futures_liquidation_margin_cutoff_and_reconciliation(
    outbox_database: Engine, price: str, equity: str, maintenance: str, released: str
) -> None:
    baseline = paper_ledger(outbox_database)
    ledger = PaperFuturesLedger(outbox_database, baseline.control, baseline.limits)
    ledger.open_account(Decimal(1000))
    opened_at = datetime(2025, 11, 10, 16, 0, tzinfo=UTC)
    funding_at = opened_at + timedelta(seconds=1)
    marked_at = opened_at + timedelta(seconds=2)
    available_at = marked_at + timedelta(seconds=1)
    intent = TradingIntent(
        "liquidation-open",
        "liquidation-correlation",
        "paper-test",
        "actor-test",
        "PAPER",
        "BTCUSDT",
        "SELL",
        Decimal("0.01"),
        opened_at,
        opened_at + timedelta(minutes=1),
    )
    quote = SyntheticQuote("fixture:entry", "BTCUSDT", Decimal(10000), opened_at)
    ledger.submit(intent, quote, opened_at, reduce_only=False)
    funding = FundingObservation(
        funding_at, funding_at, Decimal(10000), Decimal("0.0001"), "fixture:funding"
    )
    mark = LiquidationMark(marked_at, available_at, Decimal(price), "fixture:mark")
    rate = Decimal("0.25")
    try:
        ledger.apply_funding(funding, as_of=funding_at)
        with pytest.raises(ValueError, match="liquidation: out_of_order"):
            ledger.liquidate_if_needed(
                replace(mark, observed_at=opened_at, available_at=marked_at),
                maintenance_rate=rate,
                as_of=marked_at,
            )
        for cutoff in (marked_at, available_at + timedelta(seconds=2)):
            with pytest.raises(ValueError, match="liquidation: invalid_cutoff"):
                ledger.liquidate_if_needed(mark, maintenance_rate=rate, as_of=cutoff)
        assert (
            ledger.liquidate_if_needed(
                replace(mark, price=Decimal("15999")),
                maintenance_rate=rate,
                as_of=available_at,
            )
            is None
        )
        assert ledger.reconcile().liquidations == 0

        settlement = ledger.liquidate_if_needed(
            mark, maintenance_rate=rate, as_of=available_at
        )
        assert settlement is not None
        assert settlement.isolated_equity == Decimal(equity)
        assert settlement.maintenance_margin == Decimal(maintenance)
        assert settlement.released_margin == Decimal(released)
        assert settlement.after == FuturesBalance(
            Decimal("900.01") + Decimal(released),
            realized_pnl=Decimal(released) - Decimal(100),
        )
        restarted = PaperFuturesLedger(outbox_database, ledger.control, ledger.limits)
        assert (
            restarted.liquidate_if_needed(
                mark, maintenance_rate=rate, as_of=available_at
            )
            == settlement
        )
        with pytest.raises(ValueError, match="liquidation: conflicting_observation"):
            restarted.liquidate_if_needed(
                mark, maintenance_rate=Decimal("0.20"), as_of=available_at
            )
        with pytest.raises(ValueError, match="funding: out_of_order"):
            restarted.apply_funding(
                replace(funding, funding_at=marked_at, available_at=available_at),
                as_of=available_at,
            )
        with pytest.raises(ValueError, match="liquidation: fill_precedes_settlement"):
            restarted.submit(
                replace(intent, intent_id="backdated-fill"),
                quote,
                marked_at,
                reduce_only=False,
            )
        report = restarted.reconcile()
        assert report.consistent and report.liquidations == 1
        assert report.funding_entries == 1 and report.fills == 1
        assert report.stored == settlement.after

        with outbox_database.begin() as connection:
            connection.execute(
                text(
                    "UPDATE trade_system.paper_futures_liquidation "
                    "SET maintenance_margin = 0"
                )
            )
        assert restarted.reconcile().first_divergent_liquidation_at == marked_at
    finally:
        with outbox_database.begin() as connection:
            connection.execute(
                text("DELETE FROM trade_system.paper_futures_liquidation")
            )
            connection.execute(text("DELETE FROM trade_system.paper_futures_funding"))


def test_liquidation_worker_reobserves_mark_after_restart(
    outbox_database: Engine,
) -> None:
    baseline = paper_ledger(outbox_database)
    ledger = PaperFuturesLedger(outbox_database, baseline.control, baseline.limits)
    ledger.open_account(Decimal(1000))
    opened_at = datetime(2025, 11, 10, 16, 0, tzinfo=UTC)
    observed_at = opened_at + timedelta(seconds=1)
    received_at = observed_at + timedelta(seconds=1)
    replay_at = received_at + timedelta(milliseconds=100)
    intent = TradingIntent(
        "mark-worker-open",
        "mark-correlation",
        "paper-test",
        "actor-test",
        "PAPER",
        "BTCUSDT",
        "SELL",
        Decimal("0.01"),
        opened_at,
        opened_at + timedelta(minutes=1),
    )
    ledger.submit(
        intent,
        SyntheticQuote("fixture", "BTCUSDT", Decimal(10000), opened_at),
        opened_at,
        reduce_only=False,
    )
    mark = LiquidationMark(observed_at, received_at, Decimal(16000), "fixture:mark")
    rate = Decimal("0.25")
    max_age = timedelta(seconds=5)

    try:
        for cutoff in (opened_at, observed_at, observed_at + timedelta(seconds=6)):
            with pytest.raises(ValueError, match="liquidation: invalid_cutoff"):
                poll_mark(
                    outbox_database,
                    intent.account_id,
                    maintenance_rate=rate,
                    max_age=max_age,
                    fetch=lambda: mark,
                    now=lambda: cutoff,
                )
        assert ledger.reconcile().liquidations == 0
        assert poll_mark(
            outbox_database,
            intent.account_id,
            maintenance_rate=rate,
            max_age=max_age,
            fetch=lambda: mark,
            now=lambda: received_at,
        )
        restarted = create_engine(outbox_database.url)
        try:
            assert not poll_mark(
                restarted,
                intent.account_id,
                maintenance_rate=rate,
                max_age=max_age,
                fetch=lambda: replace(mark, available_at=replay_at),
                now=lambda: replay_at,
            )
            with pytest.raises(
                ValueError, match="liquidation: conflicting_observation"
            ):
                poll_mark(
                    restarted,
                    intent.account_id,
                    maintenance_rate=rate,
                    max_age=max_age,
                    now=lambda: replay_at,
                    fetch=lambda: replace(
                        mark, price=Decimal(16001), available_at=replay_at
                    ),
                )
        finally:
            restarted.dispose()
        report = ledger.reconcile()
        assert report.consistent and report.liquidations == 1
        assert report.stored == FuturesBalance(Decimal(940), realized_pnl=Decimal(-60))
        with outbox_database.connect() as connection:
            assert (
                connection.execute(
                    text(
                        "SELECT available_at "
                        "FROM trade_system.paper_futures_liquidation"
                    )
                ).scalar_one()
                == received_at
            )
    finally:
        with outbox_database.begin() as connection:
            connection.execute(
                text("DELETE FROM trade_system.paper_futures_liquidation")
            )


def test_mark_history_recovers_from_first_missing_minute(
    outbox_database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("infrastructure.database.paper_mark_history.PAGE_SIZE", 1)
    start = datetime(2025, 11, 10, 16, 0, tzinfo=UTC)
    second = start + timedelta(minutes=1)
    end = second + timedelta(minutes=1)
    now = end + timedelta(seconds=5)

    def candle(opened: datetime) -> MarkCandle:
        return MarkCandle(
            opened,
            opened + timedelta(minutes=1),
            now,
            Decimal(100),
            Decimal(110),
            Decimal(90),
            Decimal(105),
            "fixture:mark",
        )

    def interrupted(begin: datetime, stop: datetime) -> list[MarkCandle]:
        assert stop <= end
        return [candle(begin)] if begin == start else []

    with pytest.raises(IncompleteMarkHistory):
        recover_mark_history(
            outbox_database,
            start,
            fetch=interrupted,
            now=lambda: now,
        )
    assert read_mark_history(outbox_database, start, end, as_of=end) == []
    assert read_mark_history(outbox_database, start, end, as_of=now) == [candle(start)]

    def resumed(begin: datetime, stop: datetime) -> list[MarkCandle]:
        assert (begin, stop) == (second, end)
        return [candle(second)]

    restarted = create_engine(outbox_database.url)
    try:
        with pytest.raises(ValueError, match="invalid_availability"):
            recover_mark_history(
                restarted,
                start,
                now=lambda: now,
                fetch=lambda _a, _b: [
                    replace(candle(second), available_at=now + timedelta(seconds=1))
                ],
            )
        assert (
            recover_mark_history(restarted, start, fetch=resumed, now=lambda: now)
            == end
        )
        assert (
            recover_mark_history(restarted, start, fetch=resumed, now=lambda: now)
            == end
        )
        assert read_mark_history(restarted, start, end, as_of=now) == [
            candle(start),
            candle(second),
        ]
        assert read_mark_history(restarted, start, second, as_of=now) == [candle(start)]
    finally:
        restarted.dispose()
