"""Persist Market State evidence with simulated USD-M Futures fills."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "paper_futures_fill",
        sa.Column("market_state", JSONB(), nullable=True),
        schema="trade_system",
    )


def downgrade() -> None:
    op.drop_column("paper_futures_fill", "market_state", schema="trade_system")
