"""Regression checks for the approved local monitor transitions."""

import json
import sqlite3
from pathlib import Path

import pytest

from apps.event_dispatcher.monitor import AlertState, evaluate, record_sample


def sample(
    age: float | None = None, *, status: str = "ok", incident: str | None = None
) -> dict[str, object]:
    return {
        "status": status,
        "environment": "PAPER",
        "backlog": {
            "conditions": {
                "eligible": {"count": int(age is not None), "oldest_age_seconds": age},
                "blocked": {"count": 1, "oldest_age_seconds": 5000},
                "waiting": {"count": 1, "oldest_age_seconds": 5000},
            }
        },
        "incidents": (
            [
                {
                    "id": incident,
                    "reason": "retained",
                    "aggregate_type": "test",
                    "aggregate_id": "one",
                    "account_id": None,
                }
            ]
            if incident
            else []
        ),
    }


def test_failures_and_two_sample_recovery() -> None:
    state = AlertState()
    assert evaluate(state, sample(status="unavailable"), 0, 0) == []
    assert evaluate(state, sample(status="unavailable"), 30, 0)[0].action == "open"
    assert evaluate(state, sample(), 60, 0) == []
    assert evaluate(state, sample(), 90, 0)[0].action == "recover"


def test_silence_is_detected_on_resumption() -> None:
    state = AlertState()
    evaluate(state, sample(), 0, 0)
    events = evaluate(state, sample(), 60, 0)
    assert [(e.condition, e.action) for e in events] == [("collection", "open")]
    assert evaluate(state, sample(), 90, 0)[0].action == "recover"


def test_age_escalation_and_recovery_exclude_waiting() -> None:
    state = AlertState()
    assert evaluate(state, sample(300), 0, 0) == []
    assert evaluate(state, sample(301), 30, 0) == []
    assert evaluate(state, sample(301), 60, 0)[0].severity == "warning"
    assert evaluate(state, sample(901), 90, 0) == []
    assert evaluate(state, sample(901), 120, 0)[0].severity == "critical"
    assert evaluate(state, sample(), 150, 0) == []
    assert evaluate(state, sample(), 180, 0)[0].severity == "normal"


def test_collection_failure_breaks_age_confirmation() -> None:
    state = AlertState()
    evaluate(state, sample(1000), 0, 0)
    evaluate(state, sample(status="unavailable"), 30, 0)
    assert evaluate(state, sample(1000), 45, 0) == []
    assert evaluate(state, sample(1000), 50, 0)[0].severity == "critical"


def test_incident_is_durable_and_deduplicated(tmp_path: Path) -> None:
    path = tmp_path / "monitor.sqlite"
    events = record_sample(path, "PAPER", sample(incident="42"), 0)
    assert events[0].scope["aggregate_id"] == "one"
    assert record_sample(path, "PAPER", sample(incident="42"), 30) == []
    assert record_sample(path, "PAPER", sample(), 60) == []
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT count(*) FROM monitor_transition").fetchone() == (1,)


def test_restart_preserves_confirmation(tmp_path: Path) -> None:
    path = tmp_path / "monitor.sqlite"
    assert record_sample(path, "PAPER", sample(500), 0) == []
    assert record_sample(path, "PAPER", sample(500), 30)[0].severity == "warning"


@pytest.mark.parametrize("environment", ["LIVE", "TRAINING"])
def test_environment_mismatch_is_rejected(tmp_path: Path, environment: str) -> None:
    with pytest.raises(ValueError, match="environment_mismatch"):
        record_sample(tmp_path / "monitor.sqlite", environment, sample(), 0)


def test_stale_observation_rolls_back(tmp_path: Path) -> None:
    path = tmp_path / "monitor.sqlite"
    record_sample(path, "PAPER", sample(), 30)
    with pytest.raises(ValueError, match="observation_time"):
        record_sample(path, "PAPER", sample(1000), 20)
    with sqlite3.connect(path) as db:
        data = db.execute("SELECT state FROM monitor_state").fetchone()[0]
        assert json.loads(data)["last_observation"] == 30


def test_scheduler_uses_approved_interval_and_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from apps.event_dispatcher import monitor

    class Engine:
        disposed = False

        def dispose(self) -> None:
            self.disposed = True

    engine = Engine()
    windows = []
    sleeps = []

    def collect(*args: object, **kwargs: object) -> dict[str, object]:
        windows.append(kwargs["window"])
        assert kwargs["include_incidents"] is True
        return sample()

    def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        raise KeyboardInterrupt

    ticks = iter([100.0, 102.0])
    monkeypatch.setattr(
        "sys.argv", ["monitor", "--state-file", str(tmp_path / "state")]
    )
    monkeypatch.setattr(monitor, "runtime_environment", lambda: "PAPER")
    monkeypatch.setattr(monitor, "local_database_url", lambda: "unused")
    monkeypatch.setattr(monitor, "create_engine", lambda *a, **k: engine)
    monkeypatch.setattr(monitor, "collect_outbox_metrics", collect)
    monkeypatch.setattr(
        "apps.event_dispatcher.monitor.time.monotonic", lambda: next(ticks)
    )
    monkeypatch.setattr("apps.event_dispatcher.monitor.time.sleep", sleep)
    monitor.run()
    from datetime import timedelta

    assert windows[0] == timedelta(seconds=300)
    assert sleeps == [28.0]
    assert engine.disposed
    assert json.loads(capsys.readouterr().out)["status"] == "ok"
