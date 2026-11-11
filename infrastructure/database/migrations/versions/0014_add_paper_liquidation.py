"""Persist simulated BTCUSDT liquidations in the shared Futures sequence."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None
SCHEMA = "trade_system"


def upgrade() -> None:
    op.create_table(
        "paper_futures_liquidation",
        sa.Column(
            "sequence_id",
            sa.BigInteger(),
            server_default=sa.text(
                "nextval(pg_get_serial_sequence("
                "'trade_system.paper_futures_fill', 'sequence_id'))"
            ),
            primary_key=True,
        ),
        sa.Column(
            "account_id",
            sa.Text(),
            sa.ForeignKey(f"{SCHEMA}.paper_futures_account.account_id"),
            nullable=False,
        ),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("mark_price", sa.Numeric(), nullable=False),
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("maintenance_rate", sa.Numeric(), nullable=False),
        sa.Column("max_age", sa.Interval(), nullable=False),
        sa.Column("isolated_equity", sa.Numeric(), nullable=False),
        sa.Column("maintenance_margin", sa.Numeric(), nullable=False),
        sa.Column("released_margin", sa.Numeric(), nullable=False),
        sa.Column("balance_after", JSONB(), nullable=False),
        sa.UniqueConstraint("account_id", "observed_at"),
        sa.CheckConstraint(
            "observed_at <= available_at AND available_at <= applied_at"
        ),
        schema=SCHEMA,
    )


def downgrade() -> None:
    if (
        op.get_bind()
        .execute(
            sa.text(
                "SELECT EXISTS (SELECT 1 FROM trade_system.paper_futures_liquidation)"
            )
        )
        .scalar_one()
    ):
        raise RuntimeError("Cannot downgrade a Futures ledger with liquidations.")
    op.drop_table("paper_futures_liquidation", schema=SCHEMA)
