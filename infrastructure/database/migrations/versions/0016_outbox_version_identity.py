"""Enforce one event per aggregate version and retain rejected claims."""

import sqlalchemy as sa
from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing collisions require reconciliation before installing the index.
    op.execute("""
        CREATE UNIQUE INDEX outbox_aggregate_version_unique ON trade_system.outbox (
            (envelope->>'environment_id'),
            (envelope->>'account_id'),
            (envelope->>'aggregate_type'),
            (envelope->>'aggregate_id'),
            ((envelope->>'aggregate_version')::numeric)
        ) NULLS NOT DISTINCT
    """)
    op.create_table(
        "outbox_version_conflict",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("event_id", sa.Text(), nullable=False),
        sa.Column("environment_id", sa.Text(), nullable=False),
        sa.Column("account_id", sa.Text()),
        sa.Column("aggregate_type", sa.Text(), nullable=False),
        sa.Column("aggregate_id", sa.Text(), nullable=False),
        sa.Column("aggregate_version", sa.Numeric(), nullable=False),
        sa.Column("correlation_id", sa.Text(), nullable=False),
        sa.Column(
            "detected_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("clock_timestamp()"),
            nullable=False,
        ),
        schema="trade_system",
    )


def downgrade() -> None:
    op.drop_table("outbox_version_conflict", schema="trade_system")
    op.drop_index("outbox_aggregate_version_unique", schema="trade_system")
