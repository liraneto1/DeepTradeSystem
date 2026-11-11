"""Store public continuous ingestion provenance and checkpoints."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None
SCHEMA = "trade_system"


def upgrade() -> None:
    for name in ("archive_sha256", "csv_sha256"):
        op.alter_column("market_history_source", name, nullable=True, schema=SCHEMA)
    op.create_check_constraint(
        "market_history_source_hash_pair",
        "market_history_source",
        "(archive_sha256 IS NULL) = (csv_sha256 IS NULL)",
        schema=SCHEMA,
    )
    keys = ("market", "symbol", "interval", "open_time_utc")
    op.create_table(
        "market_candle_observation",
        *(sa.Column(name, sa.Text(), primary_key=True) for name in keys[:3]),
        sa.Column("open_time_utc", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("source_kind", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "available_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("payload", JSONB(), nullable=False),
        sa.CheckConstraint(
            "source_kind IN ('websocket', 'rest')",
            name="market_candle_observation_source_kind",
        ),
        sa.ForeignKeyConstraint(
            list(keys),
            [f"{SCHEMA}.market_candle.{name}" for name in keys],
            name="market_candle_observation_fk",
        ),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("market_candle_observation", schema=SCHEMA)
    op.execute(
        "DELETE FROM trade_system.market_candle c "
        "USING trade_system.market_history_source s "
        "WHERE (c.market, c.symbol, c.interval, c.day_utc) = "
        "(s.market, s.symbol, s.interval, s.day_utc) AND s.archive_sha256 IS NULL"
    )
    op.execute(
        "DELETE FROM trade_system.market_history_source WHERE archive_sha256 IS NULL"
    )
    op.drop_constraint(
        "market_history_source_hash_pair",
        "market_history_source",
        type_="check",
        schema=SCHEMA,
    )
    for name in ("archive_sha256", "csv_sha256"):
        op.alter_column("market_history_source", name, nullable=False, schema=SCHEMA)
