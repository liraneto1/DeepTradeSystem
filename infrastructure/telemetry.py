"""Local spans and allowlisted JSON logging for I00."""

import json
import logging
import os
import re
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

tracer = TracerProvider().get_tracer("trade_system")

IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
TEXT_FIELDS = (
    "correlation_id",
    "event_id",
    "causation_id",
    "environment_id",
    "error_type",
    "route",
)
NUMBER_FIELDS = ("attempt", "retry_delay_seconds", "delivery_id", "status_code")


def safe_identifier(value: object) -> str | None:
    secret = os.environ.get("POSTGRES_PASSWORD")
    if (
        isinstance(value, str)
        and IDENTIFIER.fullmatch(value)
        and (not secret or secret not in value)
    ):
        return value
    return None


def request_correlation_id(header: str | None) -> str:
    return safe_identifier(header) or uuid4().hex


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def run_worker(main: Callable[[], None], logger: logging.Logger) -> None:
    configure_logging()
    try:
        main()
    except Exception as error:
        log_event(
            logger,
            "worker_failed",
            level=logging.ERROR,
            error_type=type(error).__name__,
        )
        raise SystemExit(1) from None


def log_event(
    logger: logging.Logger, event: str, *, level: int = logging.INFO, **fields: object
) -> None:
    record: dict[str, str | int] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "level": logging.getLevelName(level),
        "component": logger.name,
        "event": event,
    }
    for key in TEXT_FIELDS:
        value = safe_identifier(fields.get(key))
        if value is not None:
            record[key] = value
    for key in NUMBER_FIELDS:
        number = fields.get(key)
        if type(number) is int:
            record[key] = number

    span = trace.get_current_span()
    context = span.get_span_context()
    if context.is_valid:
        record["trace_id"] = f"{context.trace_id:032x}"
        record["span_id"] = f"{context.span_id:016x}"
        span.set_attribute("trade_system.event", event)
        if "correlation_id" in record:
            span.set_attribute("trade_system.correlation_id", record["correlation_id"])

    logger.log(level, "%s", json.dumps(record))
