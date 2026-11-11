"""Reject new event records outside the I00 environments."""

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

SCHEMA = "trade_system"


def upgrade() -> None:
    for table in ("outbox", "event_delivery"):
        op.create_check_constraint(
            f"{table}_environment_allowed",
            table,
            "(envelope ->> 'environment_id' IN ('TRAINING', 'PAPER')) IS TRUE",
            schema=SCHEMA,
            postgresql_not_valid=True,
        )


def downgrade() -> None:
    for table in ("outbox", "event_delivery"):
        op.drop_constraint(
            f"{table}_environment_allowed", table, schema=SCHEMA, type_="check"
        )
