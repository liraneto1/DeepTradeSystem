"""Store recovered BTCUSDT mark-price candles."""

import sqlalchemy as sa
from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "paper_mark_candle",
        sa.Column("opened_at", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("opening", sa.Numeric(), nullable=False),
        sa.Column("high", sa.Numeric(), nullable=False),
        sa.Column("low", sa.Numeric(), nullable=False),
        sa.Column("closing", sa.Numeric(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.CheckConstraint("closed_at = opened_at + interval '1 minute'"),
        sa.CheckConstraint("closed_at <= available_at"),
        schema="trade_system",
    )


def downgrade() -> None:
    op.drop_table("paper_mark_candle", schema="trade_system")
