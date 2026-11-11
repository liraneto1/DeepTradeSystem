"""Connection settings for the local PostgreSQL instance."""

import os

from sqlalchemy import URL

from infrastructure.security.config import ConfigurationError, runtime_environment


def local_database_url() -> URL:
    runtime_environment()
    password = os.environ.get("POSTGRES_PASSWORD")
    if not password or not password.strip():
        raise ConfigurationError("POSTGRES_PASSWORD must be set and nonblank.")

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
        username="trade_system",
        password=password,
        host="127.0.0.1",
        port=int(port),
        database="trade_system",
        query={"hostaddr": "127.0.0.1"},
    )
