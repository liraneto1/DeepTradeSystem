"""Authorize and attribute manual Outbox operations to database identities."""

from alembic import op

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_roles WHERE rolname = 'outbox_retention_authorizer'
            ) THEN
                CREATE ROLE outbox_retention_authorizer NOLOGIN;
            END IF;
            IF NOT EXISTS (
                SELECT 1 FROM pg_roles WHERE rolname = 'outbox_resume_authorizer'
            ) THEN
                CREATE ROLE outbox_resume_authorizer NOLOGIN;
            END IF;
        END
        $$
    """)
    op.execute("""
        ALTER TABLE trade_system.outbox_retention_receipt ADD COLUMN removed_by name;
        ALTER TABLE trade_system.outbox_quarantine ADD COLUMN released_by name
    """)
    op.execute("""
        CREATE FUNCTION trade_system.authorize_outbox_operation(required_role text)
        RETURNS name LANGUAGE plpgsql STABLE SET search_path = pg_catalog AS $$
        BEGIN
            IF NOT EXISTS (
                WITH RECURSIVE memberships(role_oid) AS (
                    SELECT oid FROM pg_roles WHERE rolname = session_user
                    UNION
                    SELECT grant_row.roleid FROM pg_auth_members AS grant_row
                    JOIN memberships ON memberships.role_oid = grant_row.member
                    WHERE grant_row.inherit_option
                )
                SELECT 1 FROM memberships JOIN pg_roles
                    ON pg_roles.oid = memberships.role_oid
                WHERE pg_roles.rolname = required_role
            ) THEN
                RAISE EXCEPTION 'outbox: operation not authorized'
                    USING ERRCODE = '42501';
            END IF;
            RETURN session_user;
        END
        $$
    """)
    op.execute("""
        CREATE FUNCTION trade_system.guard_outbox_operation()
        RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                PERFORM trade_system.authorize_outbox_operation(
                    'outbox_retention_authorizer'
                );
                RETURN OLD;
            END IF;
            IF TG_TABLE_NAME = 'outbox_retention_receipt' THEN
                NEW.removed_by :=
                    trade_system.authorize_outbox_operation('outbox_retention_authorizer');
            ELSIF OLD.released_at IS DISTINCT FROM NEW.released_at
               OR OLD.decision_reference IS DISTINCT FROM NEW.decision_reference
               OR OLD.released_by IS DISTINCT FROM NEW.released_by THEN
                NEW.released_by :=
                    trade_system.authorize_outbox_operation('outbox_resume_authorizer');
            END IF;
            RETURN NEW;
        END
        $$
    """)
    op.execute("""
        CREATE TRIGGER outbox_guard_retention BEFORE DELETE ON trade_system.outbox
        FOR EACH ROW EXECUTE FUNCTION trade_system.guard_outbox_operation();
        CREATE TRIGGER outbox_attribute_retention BEFORE INSERT
        ON trade_system.outbox_retention_receipt
        FOR EACH ROW EXECUTE FUNCTION trade_system.guard_outbox_operation();
        CREATE TRIGGER outbox_guard_resume BEFORE UPDATE
        ON trade_system.outbox_quarantine
        FOR EACH ROW EXECUTE FUNCTION trade_system.guard_outbox_operation()
    """)
    op.execute("""
        GRANT USAGE ON SCHEMA trade_system TO
            outbox_retention_authorizer, outbox_resume_authorizer;
        GRANT SELECT ON trade_system.outbox, trade_system.processed_event,
            trade_system.outbox_quarantine, trade_system.outbox_retention_receipt TO
            outbox_retention_authorizer, outbox_resume_authorizer;
        GRANT DELETE ON trade_system.outbox TO outbox_retention_authorizer;
        GRANT INSERT ON trade_system.outbox_retention_receipt
            TO outbox_retention_authorizer;
        GRANT USAGE ON SEQUENCE trade_system.outbox_retention_receipt_id_seq
            TO outbox_retention_authorizer;
        GRANT UPDATE (failed_at, available_at) ON trade_system.outbox
            TO outbox_resume_authorizer;
        GRANT UPDATE (released_at, decision_reference)
            ON trade_system.outbox_quarantine TO outbox_resume_authorizer
    """)


def downgrade() -> None:
    op.execute("""
        REVOKE USAGE ON SCHEMA trade_system FROM
            outbox_retention_authorizer, outbox_resume_authorizer;
        REVOKE SELECT ON trade_system.outbox, trade_system.processed_event,
            trade_system.outbox_quarantine, trade_system.outbox_retention_receipt FROM
            outbox_retention_authorizer, outbox_resume_authorizer;
        REVOKE DELETE ON trade_system.outbox FROM outbox_retention_authorizer;
        REVOKE INSERT ON trade_system.outbox_retention_receipt
            FROM outbox_retention_authorizer;
        REVOKE USAGE ON SEQUENCE trade_system.outbox_retention_receipt_id_seq
            FROM outbox_retention_authorizer;
        REVOKE UPDATE (failed_at, available_at) ON trade_system.outbox
            FROM outbox_resume_authorizer;
        REVOKE UPDATE (released_at, decision_reference)
            ON trade_system.outbox_quarantine FROM outbox_resume_authorizer;
        DROP TRIGGER outbox_guard_resume ON trade_system.outbox_quarantine;
        DROP TRIGGER outbox_attribute_retention
            ON trade_system.outbox_retention_receipt;
        DROP TRIGGER outbox_guard_retention ON trade_system.outbox;
        DROP FUNCTION trade_system.guard_outbox_operation();
        DROP FUNCTION trade_system.authorize_outbox_operation(text);
        ALTER TABLE trade_system.outbox_retention_receipt DROP COLUMN removed_by;
        ALTER TABLE trade_system.outbox_quarantine DROP COLUMN released_by
    """)
    # Roles are cluster-wide and may be assigned or shared by other databases.
