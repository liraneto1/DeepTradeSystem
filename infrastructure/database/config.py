"""Connection settings for the local PostgreSQL instance."""

import os

from sqlalchemy import URL

from infrastructure.security.config import ConfigurationError, runtime_environment


def local_database_url() -> URL:
    return _database_url("trade_system", "POSTGRES_PASSWORD")


def dispatcher_database_url() -> URL:
    runtime_environment()
    username = os.environ.get("OUTBOX_DISPATCHER_DB_USER", "")
    if not username.strip():
        raise ConfigurationError("OUTBOX_DISPATCHER_DB_USER must be set and nonblank.")
    return _database_url(username, "OUTBOX_DISPATCHER_DB_PASSWORD")


def _database_url(username: str, password_variable: str) -> URL:
    runtime_environment()
    password = os.environ.get(password_variable)
    if not password or not password.strip():
        raise ConfigurationError(f"{password_variable} must be set and nonblank.")

    port = os.environ.get("POSTGRES_PORT", "55432")
    if not (
        1 <= len(port) <= 5
        and port.isascii()
        and port.isdecimal()
        and 1 <= int(port) <= 65535
    ):
        raise ConfigurationError(
            "POSTGRES_PORT must be an integer between 1 and 65535."
        )

    return URL.create(
        "postgresql+psycopg",
        username=username,
        password=password,
        host="127.0.0.1",
        port=int(port),
        database="trade_system",
        query={"hostaddr": "127.0.0.1"},
    )
