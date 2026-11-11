"""Check the local PostgreSQL connection and Alembic revision."""

from pathlib import Path
from typing import Literal

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from alembic.util import CommandError
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool

from infrastructure.database.config import local_database_url
from infrastructure.security.config import ConfigurationError

DatabaseState = Literal["ok", "unavailable"]
MigrationState = Literal["current", "pending", "unknown"]

ALEMBIC_CONFIG = Path(__file__).resolve().parents[2] / "alembic.ini"


def check_database() -> tuple[DatabaseState, MigrationState]:
    try:
        url = local_database_url()
    except ConfigurationError:
        return "unavailable", "unknown"

    engine = create_engine(
        url,
        poolclass=NullPool,
        connect_args={"connect_timeout": 2, "options": "-c statement_timeout=2000"},
        hide_parameters=True,
    )
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            migration_context = MigrationContext.configure(
                connection, opts={"version_table_schema": "public"}
            )
            try:
                current_heads = set(migration_context.get_current_heads())
            except SQLAlchemyError:
                return "ok", "unknown"
    except SQLAlchemyError:
        return "unavailable", "unknown"
    finally:
        engine.dispose()

    try:
        expected_heads = set(
            ScriptDirectory.from_config(Config(str(ALEMBIC_CONFIG))).get_heads()
        )
    except CommandError:
        return "ok", "unknown"

    if current_heads == expected_heads and expected_heads:
        return "ok", "current"
    return "ok", "pending"
