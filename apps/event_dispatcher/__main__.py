"""Run the local outbox dispatcher."""

import argparse
import logging
import time
from datetime import timedelta

from sqlalchemy import create_engine, text

from infrastructure.database.config import dispatcher_database_url
from infrastructure.events.dispatcher import dispatch_once
from infrastructure.events.gap_escalation import DEFAULT_GAP_AFTER_SECONDS
from infrastructure.events.local_delivery import LocalPublisher
from infrastructure.security.config import ConfigurationError
from infrastructure.telemetry import run_worker


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--once", action="store_true", help="Attempt at most one event and exit"
    )
    parser.add_argument(
        "--gap-after-seconds",
        type=int,
        default=DEFAULT_GAP_AFTER_SECONDS,
        help="Escalate missing predecessors after this wait (default: %(default)s)",
    )
    args = parser.parse_args()
    if args.gap_after_seconds <= 0:
        parser.error("--gap-after-seconds must be positive")
    gap_after = timedelta(seconds=args.gap_after_seconds)

    engine = create_engine(
        dispatcher_database_url(),
        connect_args={"connect_timeout": 5},
        hide_parameters=True,
    )
    publish = LocalPublisher(engine)
    try:
        with engine.connect() as connection:
            authorized: bool = connection.execute(
                text("""
                SELECT NOT (rolsuper OR rolcreatedb OR rolcreaterole
                            OR rolreplication OR rolbypassrls)
                   AND pg_has_role(session_user, 'outbox_dispatcher_worker', 'USAGE')
                   AND NOT pg_has_role(
                       session_user, 'outbox_retention_authorizer', 'MEMBER'
                   )
                   AND NOT pg_has_role(
                       session_user, 'outbox_resume_authorizer', 'MEMBER'
                   )
                   AND NOT has_table_privilege(
                       session_user, 'trade_system.outbox', 'DELETE, TRUNCATE'
                   )
                   AND NOT has_column_privilege(
                       session_user, 'trade_system.outbox_quarantine',
                       'released_at', 'UPDATE'
                   )
                FROM pg_roles WHERE rolname = session_user
                """)
            ).scalar_one()
        if not authorized:
            raise ConfigurationError(
                "The dispatcher requires a restricted database login."
            )
        if args.once:
            dispatch_once(engine, publish, gap_after=gap_after)
            return

        while True:
            if not dispatch_once(engine, publish, gap_after=gap_after):
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_worker(main, logging.getLogger("apps.event_dispatcher"))
