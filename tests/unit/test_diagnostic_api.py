import json
import logging
import socket
from importlib.metadata import version

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from infrastructure.security.config import ConfigurationError


@pytest.fixture(autouse=True)
def valid_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRADE_SYSTEM_ENVIRONMENT", "PAPER")
    monkeypatch.setenv("LIVE_ENABLED", "false")


def test_health_and_info_work_without_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    monkeypatch.delenv("POSTGRES_PORT", raising=False)

    with TestClient(app) as client:
        health = client.get("/health")
        info = client.get("/info")
        readiness = client.get("/readiness")

    assert health.status_code == 200
    assert health.json() == {"schema_version": "1.0.0", "status": "ok"}
    assert info.status_code == 200
    assert info.json() == {
        "schema_version": "1.0.0",
        "service": "deep-trade-system",
        "version": version("deep-trade-system"),
        "live_enabled": False,
    }
    assert readiness.status_code == 503
    assert readiness.json() == {
        "schema_version": "1.0.0",
        "status": "not_ready",
        "checks": {"database": "unavailable", "migrations": "unknown"},
    }


def test_readiness_handles_connection_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    # Reserve an unused local port without listening for connections.
    with socket.socket() as reserved_port:
        reserved_port.bind(("127.0.0.1", 0))
        monkeypatch.setenv("POSTGRES_PORT", str(reserved_port.getsockname()[1]))
        monkeypatch.setenv("POSTGRES_PASSWORD", "synthetic-test-value")
        with TestClient(app) as client:
            response = client.get("/readiness")

    assert response.status_code == 503
    assert response.json()["checks"] == {
        "database": "unavailable",
        "migrations": "unknown",
    }
    assert "synthetic-test-value" not in response.text


def test_openapi_declares_diagnostic_endpoints() -> None:
    with TestClient(app) as client:
        response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert set(paths) == {"/health", "/readiness", "/info"}
    assert set(paths["/readiness"]["get"]["responses"]) == {"200", "503"}


@pytest.mark.parametrize(
    ("variable", "value"),
    [
        ("LIVE_ENABLED", "true"),
        ("TRADE_SYSTEM_ENVIRONMENT", "LIVE"),
        ("LIVE_ENABLED", None),
    ],
)
def test_api_blocks_invalid_runtime(
    monkeypatch: pytest.MonkeyPatch, variable: str, value: str | None
) -> None:
    if value is None:
        monkeypatch.delenv(variable)
    else:
        monkeypatch.setenv(variable, value)

    with pytest.raises(ConfigurationError, match=variable), TestClient(app):
        pytest.fail("The API started with invalid configuration.")


def test_request_log_correlates_and_omits_secrets(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    secret = "synthetic-secret-for-log-test"
    monkeypatch.setenv("POSTGRES_PASSWORD", secret)
    with (
        TestClient(app) as client,
        caplog.at_level(logging.INFO, logger="apps.api.main"),
    ):
        accepted = client.get(
            f"/health?token={secret}",
            headers={
                "X-Correlation-ID": "corr_example",
                "Authorization": f"Bearer {secret}",
            },
        )
        replaced = client.get("/health", headers={"X-Correlation-ID": secret})
        generated = client.get("/health")
    assert accepted.headers["X-Correlation-ID"] == "corr_example"
    assert replaced.headers["X-Correlation-ID"] != secret
    assert len(generated.headers["X-Correlation-ID"]) == 32
    records = [
        json.loads(record.getMessage())
        for record in caplog.records
        if record.name == "apps.api.main"
    ]
    assert [record["correlation_id"] for record in records] == [
        accepted.headers["X-Correlation-ID"],
        replaced.headers["X-Correlation-ID"],
        generated.headers["X-Correlation-ID"],
    ]
    assert records[0]["route"] == "health"
    assert records[0]["status_code"] == 200
    assert len(records[0]["trace_id"]) == 32
    assert len(records[0]["span_id"]) == 16
    assert secret not in caplog.text
    assert "Authorization" not in caplog.text
    assert "token=" not in caplog.text


def test_api_failure_logs_type_without_exception_message(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def fail() -> None:
        raise RuntimeError("synthetic private exception detail")

    monkeypatch.setattr("apps.api.main.check_database", fail)
    with TestClient(app) as client:
        response = client.get(
            "/readiness", headers={"X-Correlation-ID": "corr_failure"}
        )
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert response.headers["X-Correlation-ID"] == "corr_failure"
    record = json.loads(caplog.records[-1].getMessage())
    assert record["event"] == "diagnostic_failed"
    assert record["error_type"] == "RuntimeError"
    assert record["correlation_id"] == "corr_failure"
    assert "synthetic private exception detail" not in caplog.text
