"""Persist aggregate-level dispatch quarantines and release decisions."""

from alembic import op

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE trade_system.outbox_quarantine (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            environment_id text NOT NULL
                CHECK (environment_id IN ('PAPER', 'TRAINING')),
            account_id text,
            aggregate_type text NOT NULL,
            aggregate_id text NOT NULL,
            event_id text NOT NULL,
            reason text NOT NULL CHECK (reason IN ('version_conflict', 'retained')),
            detected_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            released_at timestamptz,
            decision_reference text,
            CHECK ((released_at IS NULL) = (decision_reference IS NULL))
        )
    """)
    op.execute("""
        CREATE INDEX outbox_active_quarantine_scope ON trade_system.outbox_quarantine
        (environment_id, account_id, aggregate_type, aggregate_id)
        WHERE released_at IS NULL
    """)
    op.execute("""
        INSERT INTO trade_system.outbox_quarantine
            (environment_id, account_id, aggregate_type, aggregate_id, event_id,
             reason, detected_at)
        SELECT environment_id, account_id, aggregate_type, aggregate_id, event_id,
               'version_conflict', detected_at
        FROM trade_system.outbox_version_conflict
        UNION ALL
        SELECT envelope->>'environment_id', envelope->>'account_id',
               envelope->>'aggregate_type', envelope->>'aggregate_id', event_id,
               'retained', failed_at
        FROM trade_system.outbox WHERE failed_at IS NOT NULL AND published_at IS NULL
          AND envelope->>'environment_id' IN ('PAPER', 'TRAINING')
    """)


def downgrade() -> None:
    op.drop_table("outbox_quarantine", schema="trade_system")
