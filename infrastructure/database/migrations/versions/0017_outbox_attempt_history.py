"""Persist dispatcher outcomes for interval metrics."""

from alembic import op

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE trade_system.outbox_attempt (
            event_id text NOT NULL,
            attempt integer NOT NULL CHECK (attempt > 0),
            environment_id text NOT NULL
                CHECK (environment_id IN ('PAPER', 'TRAINING')),
            recorded_at timestamptz NOT NULL,
            outcome text NOT NULL CHECK (
                outcome IN ('outbox_published', 'outbox_retry_scheduled',
                            'outbox_failed')
            ),
            PRIMARY KEY (event_id, attempt)
        )
    """)
    op.create_index(
        "outbox_attempt_environment_time",
        "outbox_attempt",
        ["environment_id", "recorded_at"],
        schema="trade_system",
    )


def downgrade() -> None:
    op.drop_table("outbox_attempt", schema="trade_system")
