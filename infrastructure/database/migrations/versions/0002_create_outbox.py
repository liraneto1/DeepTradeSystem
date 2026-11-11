"""Create the transactional outbox."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "outbox",
        sa.Column("event_id", sa.Text(), primary_key=True),
        sa.Column("envelope", JSONB(), nullable=False),
        sa.Column(
            "enqueued_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "((jsonb_typeof(envelope -> 'event_id') = 'string') "
            "AND (envelope ->> 'event_id' = event_id)) IS TRUE",
            name="outbox_event_id_matches_envelope",
        ),
        schema="trade_system",
    )


def downgrade() -> None:
    op.drop_table("outbox", schema="trade_system")
