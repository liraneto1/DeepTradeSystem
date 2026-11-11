"""Persist synthetic Spot fills and balances for PAPER accounts."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None
SCHEMA = "trade_system"


def upgrade() -> None:
    op.create_table(
        "paper_account",
        sa.Column("account_id", sa.Text(), primary_key=True),
        *(
            sa.Column(name, sa.Numeric(), nullable=False)
            for name in ("opening_cash", "opening_quantity", "cash", "quantity")
        ),
        sa.CheckConstraint(
            "opening_cash >= 0 AND opening_quantity >= 0 "
            "AND cash >= 0 AND quantity >= 0",
            name="paper_account_nonnegative",
        ),
        schema=SCHEMA,
    )
    op.create_table(
        "paper_fill",
        sa.Column("sequence_id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column(
            "account_id",
            sa.Text(),
            sa.ForeignKey(f"{SCHEMA}.paper_account.account_id"),
            nullable=False,
        ),
        sa.Column("intent_id", sa.Text(), nullable=False),
        sa.Column("intent", JSONB(), nullable=False),
        sa.Column("side", sa.Text(), nullable=False),
        sa.Column("correlation_id", sa.Text(), nullable=False),
        sa.Column("quote_reference", sa.Text(), nullable=False),
        sa.Column("filled_at", sa.DateTime(timezone=True), nullable=False),
        *(
            sa.Column(name, sa.Numeric(), nullable=False)
            for name in (
                "price",
                "quantity",
                "notional",
                "cash_after",
                "quantity_after",
            )
        ),
        sa.UniqueConstraint(
            "account_id", "intent_id", name="paper_fill_account_intent"
        ),
        sa.CheckConstraint("side IN ('BUY', 'SELL')", name="paper_fill_valid_side"),
        sa.CheckConstraint(
            "price > 0 AND quantity > 0 AND notional > 0 "
            "AND cash_after >= 0 AND quantity_after >= 0",
            name="paper_fill_amounts",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "paper_fill_account_sequence",
        "paper_fill",
        ["account_id", "sequence_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("paper_fill", schema=SCHEMA)
    op.drop_table("paper_account", schema=SCHEMA)
