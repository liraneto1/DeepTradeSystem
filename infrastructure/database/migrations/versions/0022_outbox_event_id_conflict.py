"""Record changed envelopes that reuse an existing Outbox event ID."""

import sqlalchemy as sa
from alembic import op

revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE trade_system.outbox_quarantine
        DROP CONSTRAINT outbox_quarantine_reason_check,
        ADD CONSTRAINT outbox_quarantine_reason_check CHECK (
            reason IN ('version_conflict', 'retained', 'missing',
                       'retention_removed', 'event_id_conflict')
        )
    """)
    op.execute("""
        CREATE TABLE trade_system.outbox_event_id_conflict (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            event_id text NOT NULL,
            original_sha256 text NOT NULL,
            claimed_sha256 text NOT NULL,
            claimed_environment_id text NOT NULL,
            claimed_correlation_id text NOT NULL,
            detected_at timestamptz NOT NULL DEFAULT clock_timestamp()
        )
    """)


def downgrade() -> None:
    if (
        op.get_bind()
        .execute(
            sa.text("""
        SELECT EXISTS (SELECT 1 FROM trade_system.outbox_event_id_conflict)
            OR EXISTS (SELECT 1 FROM trade_system.outbox_quarantine
                       WHERE reason = 'event_id_conflict')
        """)
        )
        .scalar_one()
    ):
        raise RuntimeError("Cannot downgrade with recorded Outbox ID conflicts.")
    op.drop_table("outbox_event_id_conflict", schema="trade_system")
    op.execute("""
        ALTER TABLE trade_system.outbox_quarantine
        DROP CONSTRAINT outbox_quarantine_reason_check,
        ADD CONSTRAINT outbox_quarantine_reason_check CHECK (
            reason IN ('version_conflict', 'retained', 'missing', 'retention_removed')
        )
    """)
