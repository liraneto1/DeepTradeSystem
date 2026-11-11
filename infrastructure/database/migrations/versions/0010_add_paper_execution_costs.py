"""Store the price reference and execution costs for each PAPER fill."""

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None
SCHEMA = "trade_system"


def upgrade() -> None:
    op.add_column(
        "paper_fill", sa.Column("reference_price", sa.Numeric()), schema=SCHEMA
    )
    op.execute("UPDATE trade_system.paper_fill SET reference_price = price")
    op.alter_column("paper_fill", "reference_price", nullable=False, schema=SCHEMA)
    for field in ("fee", "fee_bps", "slippage_bps"):
        op.add_column(
            "paper_fill",
            sa.Column(field, sa.Numeric(), nullable=False, server_default="0"),
            schema=SCHEMA,
        )
    op.create_check_constraint(
        "paper_fill_cost_bounds",
        "paper_fill",
        "reference_price > 0 AND fee >= 0 AND fee <= notional "
        "AND fee_bps >= 0 AND fee_bps <= 10000 "
        "AND slippage_bps >= 0 AND slippage_bps < 10000",
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_constraint(
        "paper_fill_cost_bounds", "paper_fill", type_="check", schema=SCHEMA
    )
    for field in ("fee", "fee_bps", "slippage_bps", "reference_price"):
        op.drop_column("paper_fill", field, schema=SCHEMA)
