"""Attach immutable market-state evidence to PAPER fills."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "paper_fill", sa.Column("market_state", JSONB()), schema="trade_system"
    )


def downgrade() -> None:
    op.drop_column("paper_fill", "market_state", schema="trade_system")
