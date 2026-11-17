"""Persist local Outbox alert transitions and run the approved sampling schedule."""

import argparse
import json
import sqlite3
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import create_engine

from infrastructure.database.config import local_database_url
from infrastructure.events.outbox_metrics import collect_outbox_metrics
from infrastructure.security.config import runtime_environment

INTERVAL_SECONDS = 30
WINDOW_SECONDS = 300


class AlertState(BaseModel):
    failures: int = 0
    healthy: int = 0
    last_success: float | None = None
    last_observation: float | None = None
    unavailable: bool = False
    warning_samples: int = 0
    critical_samples: int = 0
    normal_samples: int = 0
    age_level: Literal["normal", "warning", "critical"] = "normal"
    incidents: list[str] = Field(default_factory=list)


class Transition(BaseModel):
    condition: str
    action: str
    severity: str
    incident_id: str | None = None
    scope: dict[str, str | None] = Field(default_factory=dict)


def evaluate(
    state: AlertState, sample: dict[str, object], now: float, started_at: float
) -> list[Transition]:
    """Evaluate one observation; incident closure is recorded by human action."""
    if state.last_observation is not None and now <= state.last_observation:
        raise ValueError("monitor: observation_time_must_advance")
    state.last_observation = now
    events: list[Transition] = []
    stale = (
        now - (state.last_success if state.last_success is not None else started_at)
        >= 60
    )
    if sample["status"] != "ok":
        state.failures += 1
        state.healthy = 0
        # A missing sample breaks consecutive confirmations of age and recovery.
        state.warning_samples = state.critical_samples = state.normal_samples = 0
        if not state.unavailable and (state.failures >= 2 or stale):
            state.unavailable = True
            events.append(
                Transition(condition="collection", action="open", severity="critical")
            )
        return events

    if stale and not state.unavailable:
        state.healthy = 0
        state.unavailable = True
        events.append(
            Transition(condition="collection", action="open", severity="critical")
        )
    state.failures = 0
    state.healthy += 1
    state.last_success = now
    if state.unavailable and state.healthy >= 2:
        state.unavailable = False
        events.append(
            Transition(condition="collection", action="recover", severity="normal")
        )

    # Pydantic validates the nested metric values before using them below.
    metrics = Observation.model_validate(sample)
    age = metrics.backlog.conditions["eligible"].oldest_age_seconds
    warning = age is not None and age > 300
    critical = age is not None and age > 900
    state.warning_samples = state.warning_samples + 1 if warning else 0
    state.critical_samples = state.critical_samples + 1 if critical else 0
    state.normal_samples = 0 if warning else state.normal_samples + 1
    level: Literal["normal", "warning", "critical"] = state.age_level
    if state.critical_samples >= 2:
        level = "critical"
    elif state.warning_samples >= 2:
        level = "warning"
    elif state.normal_samples >= 2:
        level = "normal"
    if level != state.age_level:
        events.append(
            Transition(
                condition="eligible_age",
                action="recover" if level == "normal" else "change",
                severity=level,
            )
        )
        state.age_level = level

    for incident in metrics.incidents:
        if incident.id not in state.incidents:
            state.incidents.append(incident.id)
            events.append(
                Transition(
                    condition="quarantine",
                    action="open",
                    severity="critical",
                    incident_id=incident.id,
                    scope={
                        "reason": incident.reason,
                        "aggregate_type": incident.aggregate_type,
                        "aggregate_id": incident.aggregate_id,
                        "account_id": incident.account_id,
                    },
                )
            )
    return events


class Condition(BaseModel):
    count: int = Field(ge=0)
    oldest_age_seconds: float | None = Field(default=None, ge=0)


class Backlog(BaseModel):
    conditions: dict[str, Condition]


class Incident(BaseModel):
    id: str
    reason: str
    aggregate_type: str
    aggregate_id: str
    account_id: str | None = None


class Observation(BaseModel):
    backlog: Backlog
    incidents: list[Incident]


def record_sample(
    path: Path, environment: str, sample: dict[str, object], now: float
) -> list[Transition]:
    """Serialize evaluators and atomically persist state and transition history."""
    if (
        environment not in ("TRAINING", "PAPER")
        or sample.get("environment") != environment
    ):
        raise ValueError("monitor: environment_mismatch")
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path, timeout=10, isolation_level=None) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS monitor_state "
            "(environment TEXT PRIMARY KEY, started_at REAL NOT NULL, "
            "state TEXT NOT NULL)"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS monitor_transition "
            "(id INTEGER PRIMARY KEY, environment TEXT NOT NULL, "
            "observed_at REAL NOT NULL, transition TEXT NOT NULL)"
        )
        db.execute("BEGIN IMMEDIATE")
        try:
            row = db.execute(
                "SELECT started_at, state FROM monitor_state WHERE environment = ?",
                (environment,),
            ).fetchone()
            started_at = float(row[0]) if row else now
            state = AlertState.model_validate_json(row[1]) if row else AlertState()
            events = evaluate(state, sample, now, started_at)
            db.execute(
                "INSERT INTO monitor_state VALUES (?, ?, ?) "
                "ON CONFLICT(environment) DO UPDATE SET state = excluded.state",
                (environment, started_at, state.model_dump_json()),
            )
            db.executemany(
                "INSERT INTO monitor_transition(environment, observed_at, transition) "
                "VALUES (?, ?, ?)",
                [(environment, now, event.model_dump_json()) for event in events],
            )
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise
    return events


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-file", type=Path, required=True)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    environment = runtime_environment()
    engine = create_engine(
        local_database_url(), hide_parameters=True, connect_args={"connect_timeout": 5}
    )
    try:
        while True:
            tick = time.monotonic()
            sample = collect_outbox_metrics(
                engine, window=timedelta(seconds=WINDOW_SECONDS), include_incidents=True
            )
            now = datetime.now(UTC)
            transitions = record_sample(
                args.state_file, environment, sample, now.timestamp()
            )
            print(
                json.dumps(
                    {
                        "observed_at": now.isoformat(),
                        "environment": environment,
                        "status": sample["status"],
                        "transitions": [item.model_dump() for item in transitions],
                    }
                ),
                flush=True,
            )
            if args.once:
                return
            time.sleep(max(0, INTERVAL_SECONDS - (time.monotonic() - tick)))
    except KeyboardInterrupt:
        pass
    finally:
        engine.dispose()


if __name__ == "__main__":
    run()
