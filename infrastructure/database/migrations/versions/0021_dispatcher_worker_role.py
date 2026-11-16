"""Grant a dedicated dispatcher role the permissions needed to publish."""

from alembic import op

revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_roles WHERE rolname = 'outbox_dispatcher_worker'
            ) THEN
                CREATE ROLE outbox_dispatcher_worker NOLOGIN;
            END IF;
        END
        $$;
        GRANT USAGE ON SCHEMA trade_system
            TO outbox_dispatcher_worker;
        GRANT SELECT ON trade_system.outbox, trade_system.outbox_retention_receipt
            TO outbox_dispatcher_worker;
        GRANT SELECT (environment_id, account_id, aggregate_type,
                      aggregate_id, released_at)
            ON trade_system.outbox_quarantine
            TO outbox_dispatcher_worker;
        GRANT UPDATE (attempts, available_at, published_at, failed_at)
            ON trade_system.outbox
            TO outbox_dispatcher_worker;
        GRANT INSERT ON trade_system.outbox_attempt
            TO outbox_dispatcher_worker;
        GRANT INSERT (envelope) ON trade_system.event_delivery
            TO outbox_dispatcher_worker;
        GRANT INSERT (environment_id, account_id, aggregate_type,
                      aggregate_id, event_id, reason, expected_version)
            ON trade_system.outbox_quarantine
            TO outbox_dispatcher_worker
    """)


def downgrade() -> None:
    op.execute("""
        REVOKE USAGE ON SCHEMA trade_system
            FROM outbox_dispatcher_worker;
        REVOKE SELECT ON trade_system.outbox, trade_system.outbox_retention_receipt
            FROM outbox_dispatcher_worker;
        REVOKE SELECT (environment_id, account_id, aggregate_type,
                      aggregate_id, released_at)
            ON trade_system.outbox_quarantine
            FROM outbox_dispatcher_worker;
        REVOKE UPDATE (attempts, available_at, published_at, failed_at)
            ON trade_system.outbox
            FROM outbox_dispatcher_worker;
        REVOKE INSERT ON trade_system.outbox_attempt
            FROM outbox_dispatcher_worker;
        REVOKE INSERT (envelope) ON trade_system.event_delivery
            FROM outbox_dispatcher_worker;
        REVOKE INSERT (environment_id, account_id, aggregate_type,
                      aggregate_id, event_id, reason, expected_version)
            ON trade_system.outbox_quarantine
            FROM outbox_dispatcher_worker
    """)
    # The role is cluster-wide and login assignments may be shared by other databases.
