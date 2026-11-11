import pytest

from infrastructure.database.config import local_database_url
from infrastructure.security.config import ConfigurationError, runtime_environment


@pytest.fixture(autouse=True)
def valid_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRADE_SYSTEM_ENVIRONMENT", "PAPER")
    monkeypatch.setenv("LIVE_ENABLED", "false")


@pytest.mark.parametrize(
    ("variable", "value"),
    [
        ("TRADE_SYSTEM_ENVIRONMENT", None),
        ("TRADE_SYSTEM_ENVIRONMENT", ""),
        ("TRADE_SYSTEM_ENVIRONMENT", "LIVE"),
        ("TRADE_SYSTEM_ENVIRONMENT", "paper"),
        ("TRADE_SYSTEM_ENVIRONMENT", "PAPER "),
        ("LIVE_ENABLED", None),
        ("LIVE_ENABLED", ""),
        ("LIVE_ENABLED", "true"),
        ("LIVE_ENABLED", "0"),
    ],
)
def test_runtime_rejects_missing_or_invalid_policy(
    monkeypatch: pytest.MonkeyPatch, variable: str, value: str | None
) -> None:
    if value is None:
        monkeypatch.delenv(variable)
    else:
        monkeypatch.setenv(variable, value)

    with pytest.raises(ConfigurationError, match=variable):
        runtime_environment()


@pytest.mark.parametrize("environment", ["TRAINING", "PAPER"])
def test_allowed_environments(
    monkeypatch: pytest.MonkeyPatch, environment: str
) -> None:
    monkeypatch.setenv("TRADE_SYSTEM_ENVIRONMENT", environment)
    assert runtime_environment() == environment


@pytest.mark.parametrize("password", [None, "", "  "])
def test_database_rejects_missing_or_blank_password(
    monkeypatch: pytest.MonkeyPatch, password: str | None
) -> None:
    if password is None:
        monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    else:
        monkeypatch.setenv("POSTGRES_PASSWORD", password)

    with pytest.raises(ConfigurationError, match="POSTGRES_PASSWORD"):
        local_database_url()


@pytest.mark.parametrize(
    "port", ["", "bad-port", "0", "65536", "-1", " 55432", "9" * 5000]
)
def test_database_rejects_invalid_ports(
    monkeypatch: pytest.MonkeyPatch, port: str
) -> None:
    monkeypatch.setenv("POSTGRES_PASSWORD", "synthetic-test-value")
    monkeypatch.setenv("POSTGRES_PORT", port)

    with pytest.raises(ConfigurationError) as error:
        local_database_url()
    assert str(error.value) == "POSTGRES_PORT must be an integer between 1 and 65535."


def test_database_url_is_local_and_masks_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "synthetic-test-value"
    monkeypatch.setenv("POSTGRES_PASSWORD", secret)
    monkeypatch.delenv("POSTGRES_PORT", raising=False)
    monkeypatch.setenv("PGHOST", "remote.example")
    monkeypatch.setenv("PGHOSTADDR", "192.0.2.1")

    url = local_database_url()
    assert url.host == "127.0.0.1"
    assert url.query["hostaddr"] == "127.0.0.1"
    assert url.port == 55432
    assert url.password == secret
    assert secret not in str(url)
    assert secret not in repr(url)
