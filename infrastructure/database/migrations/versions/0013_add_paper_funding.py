"""Store simulated BTCUSDT funding in the Futures ledger sequence."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None
SCHEMA = "trade_system"


def upgrade() -> None:
    op.create_table(
        "paper_futures_funding",
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
        sa.Column("funding_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("mark_price", sa.Numeric(), nullable=False),
        sa.Column("rate", sa.Numeric(), nullable=False),
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("cash_delta", sa.Numeric(), nullable=False),
        sa.Column("balance_after", JSONB(), nullable=False),
        sa.UniqueConstraint("account_id", "funding_at"),
        sa.CheckConstraint("funding_at <= available_at AND available_at <= applied_at"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    connection = op.get_bind()
    if connection.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM trade_system.paper_futures_funding)")
    ).scalar_one():
        raise RuntimeError("Cannot downgrade a Futures ledger with funding entries.")
    op.drop_table("paper_futures_funding", schema=SCHEMA)
