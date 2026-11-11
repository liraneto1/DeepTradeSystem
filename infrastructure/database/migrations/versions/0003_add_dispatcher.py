"""Add dispatcher state and the local delivery queue."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

SCHEMA = "trade_system"


def upgrade() -> None:
    for column in (
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "available_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("failed_at", sa.DateTime(timezone=True)),
    ):
        op.add_column("outbox", column, schema=SCHEMA)
    op.create_index(
        "outbox_ready_idx",
        "outbox",
        ["available_at", "enqueued_at", "event_id"],
        schema=SCHEMA,
        postgresql_where=sa.text("published_at IS NULL AND failed_at IS NULL"),
    )
    op.create_table(
        "event_delivery",
        sa.Column("delivery_id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("envelope", JSONB(), nullable=False),
        sa.Column(
            "delivered_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("event_delivery", schema=SCHEMA)
    op.drop_index("outbox_ready_idx", table_name="outbox", schema=SCHEMA)
    for column in ("failed_at", "published_at", "available_at", "attempts"):
        op.drop_column("outbox", column, schema=SCHEMA)
