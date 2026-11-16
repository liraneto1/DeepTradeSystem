"""Print one local Outbox metrics sample as JSON."""

import argparse
import json
from datetime import timedelta

from sqlalchemy import create_engine

from infrastructure.database.config import local_database_url
from infrastructure.events.outbox_metrics import collect_outbox_metrics
from infrastructure.security.config import runtime_environment


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window-seconds", type=int, required=True)
    args = parser.parse_args()
    if args.window_seconds <= 0:
        parser.error("--window-seconds must be positive")
    runtime_environment()
    engine = create_engine(
        local_database_url(), hide_parameters=True, connect_args={"connect_timeout": 5}
    )
    try:
        window = timedelta(seconds=args.window_seconds)
        sample = collect_outbox_metrics(engine, window=window)
        print(json.dumps(sample))
        if sample["status"] == "unavailable":
            raise SystemExit(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
