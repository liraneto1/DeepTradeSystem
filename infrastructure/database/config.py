"""Connection settings for the local PostgreSQL instance."""

import os

from sqlalchemy import URL


def local_database_url() -> URL:
    password = os.environ.get("POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError("Set POSTGRES_PASSWORD for the local PostgreSQL instance.")

    return URL.create(
        "postgresql+psycopg",
        username="trade_system",
        password=password,
        host="127.0.0.1",
        port=int(os.environ.get("POSTGRES_PORT", "55432")),
        database="trade_system",
    )
