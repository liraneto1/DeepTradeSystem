"""Add candles and their daily source manifests."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None
SCHEMA = "trade_system"


def upgrade() -> None:
    op.create_table(
        "market_history_source",
        sa.Column("market", sa.Text(), primary_key=True),
        sa.Column("symbol", sa.Text(), primary_key=True),
        sa.Column("interval", sa.Text(), primary_key=True),
        sa.Column("day_utc", sa.Date(), primary_key=True),
        sa.Column("archive_sha256", sa.String(64), nullable=False),
        sa.Column("csv_sha256", sa.String(64), nullable=False),
        sa.Column("manifest", JSONB(), nullable=False),
        schema=SCHEMA,
    )
    op.create_table(
        "market_candle",
        sa.Column("market", sa.Text(), primary_key=True),
        sa.Column("symbol", sa.Text(), primary_key=True),
        sa.Column("interval", sa.Text(), primary_key=True),
        sa.Column("open_time_utc", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("day_utc", sa.Date(), nullable=False),
        sa.Column(
            "close_time_exclusive_utc", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("open", sa.Numeric(), nullable=False),
        sa.Column("high", sa.Numeric(), nullable=False),
        sa.Column("low", sa.Numeric(), nullable=False),
        sa.Column("close", sa.Numeric(), nullable=False),
        sa.Column("volume", sa.Numeric(), nullable=False),
        sa.Column("quote_volume", sa.Numeric(), nullable=False),
        sa.Column("trade_count", sa.BigInteger(), nullable=False),
        sa.Column("taker_buy_volume", sa.Numeric(), nullable=False),
        sa.Column("taker_buy_quote_volume", sa.Numeric(), nullable=False),
        sa.ForeignKeyConstraint(
            ["market", "symbol", "interval", "day_utc"],
            [
                f"{SCHEMA}.market_history_source.{name}"
                for name in ("market", "symbol", "interval", "day_utc")
            ],
            name="market_candle_source_fk",
        ),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("market_candle", schema=SCHEMA)
    op.drop_table("market_history_source", schema=SCHEMA)
