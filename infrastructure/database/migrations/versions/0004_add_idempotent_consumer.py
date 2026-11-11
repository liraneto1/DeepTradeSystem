"""Add persistent deduplication and the synthetic diagnostic projection."""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

SCHEMA = "trade_system"


def upgrade() -> None:
    op.add_column(
        "event_delivery",
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        schema=SCHEMA,
    )
    op.create_index(
        "event_delivery_pending_idx",
        "event_delivery",
        ["delivery_id"],
        schema=SCHEMA,
        postgresql_where=sa.text("consumed_at IS NULL"),
    )
    op.create_table(
        "processed_event",
        sa.Column("event_id", sa.Text(), primary_key=True),
        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema=SCHEMA,
    )
    op.create_table(
        "diagnostic_event_count",
        sa.Column("environment_id", sa.Text(), primary_key=True),
        sa.Column("event_count", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "environment_id IN ('TRAINING', 'PAPER')",
            name="diagnostic_environment_allowed",
        ),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("diagnostic_event_count", schema=SCHEMA)
    op.drop_table("processed_event", schema=SCHEMA)
    op.drop_index(
        "event_delivery_pending_idx", table_name="event_delivery", schema=SCHEMA
    )
    op.drop_column("event_delivery", "consumed_at", schema=SCHEMA)
