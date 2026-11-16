"""Track removed predecessors and classify escalated gaps."""

import sqlalchemy as sa
from alembic import op

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE trade_system.outbox_quarantine
        ADD COLUMN expected_version numeric,
        DROP CONSTRAINT outbox_quarantine_reason_check,
        ADD CONSTRAINT outbox_quarantine_reason_check CHECK (
            reason IN ('version_conflict', 'retained', 'missing', 'retention_removed')
        )
    """)
    op.execute("""
        CREATE TABLE trade_system.outbox_retention_receipt (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            event_id text NOT NULL,
            envelope_sha256 text NOT NULL,
            attempts integer NOT NULL CHECK (attempts >= 0),
            environment_id text NOT NULL
                CHECK (environment_id IN ('PAPER', 'TRAINING')),
            account_id text,
            aggregate_type text NOT NULL,
            aggregate_id text NOT NULL,
            aggregate_version numeric NOT NULL,
            removed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            decision_reference text NOT NULL
        )
    """)
    op.execute("""
        CREATE INDEX outbox_retention_scope ON trade_system.outbox_retention_receipt
        (environment_id, account_id, aggregate_type, aggregate_id, aggregate_version)
    """)


def downgrade() -> None:
    if (
        op.get_bind()
        .execute(
            sa.text("""
        SELECT EXISTS (SELECT 1 FROM trade_system.outbox_retention_receipt)
            OR EXISTS (SELECT 1 FROM trade_system.outbox_quarantine
                       WHERE reason IN ('missing', 'retention_removed'))
        """)
        )
        .scalar_one()
    ):
        raise RuntimeError("Cannot downgrade with recorded Outbox gaps or removals.")
    op.execute("""
        ALTER TABLE trade_system.outbox_quarantine
        DROP COLUMN expected_version,
        DROP CONSTRAINT outbox_quarantine_reason_check,
        ADD CONSTRAINT outbox_quarantine_reason_check CHECK (
            reason IN ('version_conflict', 'retained')
        )
    """)
    op.drop_table("outbox_retention_receipt", schema="trade_system")
