"""Alembic environment for the local PostgreSQL instance."""

from alembic import context
from sqlalchemy import create_engine, pool

from infrastructure.database.config import local_database_url

url = local_database_url()

if context.is_offline_mode():
    context.configure(url=url, literal_binds=True, version_table_schema="public")
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(url, poolclass=pool.NullPool)
    try:
        with engine.connect() as connection:
            context.configure(connection=connection, version_table_schema="public")
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()
