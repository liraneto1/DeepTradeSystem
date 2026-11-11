import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from infrastructure.database.config import local_database_url

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.skipif(
    os.environ.get("RUN_POSTGRES_TESTS") != "1",
    reason="Requires a disposable PostgreSQL 17 instance",
)
def test_initial_migration_round_trip() -> None:
    config = Config(str(ROOT / "alembic.ini"))
    engine = create_engine(local_database_url())
    try:
        with engine.connect() as connection:
            server_version = int(
                connection.execute(text("SHOW server_version_num")).scalar_one()
            )
            assert server_version // 10000 == 17
            inspector = inspect(connection)
            assert "trade_system" not in inspector.get_schema_names()
            if inspector.has_table("alembic_version", schema="public"):
                assert (
                    connection.execute(
                        text("SELECT version_num FROM public.alembic_version")
                    ).scalar_one_or_none()
                    is None
                )

        command.upgrade(config, "head")
        with engine.connect() as connection:
            assert "trade_system" in inspect(connection).get_schema_names()
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
    finally:
        engine.dispose()
