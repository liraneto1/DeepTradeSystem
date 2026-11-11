"""Create the isolated synthetic USDⓈ-M PAPER ledger."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None
SCHEMA = "trade_system"


def upgrade() -> None:
    op.create_table(
        "paper_futures_account",
        sa.Column("account_id", sa.Text(), primary_key=True),
        sa.Column("opening_cash", sa.Numeric(), nullable=False),
        sa.Column("balance", JSONB(), nullable=False),
        sa.CheckConstraint("opening_cash >= 0", name="paper_futures_opening_cash"),
        schema=SCHEMA,
    )
    op.create_table(
        "paper_futures_fill",
        sa.Column("sequence_id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column(
            "account_id",
            sa.Text(),
            sa.ForeignKey(f"{SCHEMA}.paper_futures_account.account_id"),
            nullable=False,
        ),
        sa.Column("intent_id", sa.Text(), nullable=False),
        sa.Column("intent", JSONB(), nullable=False),
        sa.Column("quantity", sa.Numeric(), nullable=False),
        sa.Column("reference_price", sa.Numeric(), nullable=False),
        sa.Column("fee_bps", sa.Numeric(), nullable=False),
        sa.Column("slippage_bps", sa.Numeric(), nullable=False),
        sa.Column("quote_reference", sa.Text(), nullable=False),
        sa.Column("filled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fill", JSONB(), nullable=False),
        sa.UniqueConstraint(
            "account_id", "intent_id", name="paper_futures_account_intent"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "paper_futures_account_sequence",
        "paper_futures_fill",
        ["account_id", "sequence_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("paper_futures_fill", schema=SCHEMA)
    op.drop_table("paper_futures_account", schema=SCHEMA)
