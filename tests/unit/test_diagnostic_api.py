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
