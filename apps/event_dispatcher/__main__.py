"""Run the local outbox dispatcher."""

import argparse
import logging
import time

from sqlalchemy import create_engine

from infrastructure.database.config import local_database_url
from infrastructure.events.dispatcher import dispatch_once
from infrastructure.events.local_delivery import LocalPublisher


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--once", action="store_true", help="Attempt at most one event and exit"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    engine = create_engine(
        local_database_url(), connect_args={"connect_timeout": 5}, hide_parameters=True
    )
    publish = LocalPublisher(engine)
    try:
        if args.once:
            dispatch_once(engine, publish)
            return

        while True:
            if not dispatch_once(engine, publish):
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
