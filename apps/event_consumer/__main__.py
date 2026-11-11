"""Run the local idempotent event consumer."""

import argparse
import logging
import time

from sqlalchemy import create_engine

from infrastructure.database.config import local_database_url
from infrastructure.events.consumer import consume_once
from infrastructure.events.diagnostic_projection import apply_diagnostic_event
from infrastructure.telemetry import run_worker


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--once", action="store_true", help="Consume up to one delivery and exit"
    )
    args = parser.parse_args()

    engine = create_engine(
        local_database_url(), connect_args={"connect_timeout": 5}, hide_parameters=True
    )
    try:
        if args.once:
            consume_once(engine, apply_diagnostic_event)
            return

        while True:
            if not consume_once(engine, apply_diagnostic_event):
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_worker(main, logging.getLogger("apps.event_consumer"))
