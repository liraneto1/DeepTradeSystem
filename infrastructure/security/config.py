"""Validate the I00 runtime policy without exposing configuration values."""

import os
from typing import Literal, cast

RuntimeEnvironment = Literal["TRAINING", "PAPER"]


class ConfigurationError(RuntimeError):
    """The process configuration is missing or outside the allowed local policy."""


def runtime_environment() -> RuntimeEnvironment:
    if os.environ.get("LIVE_ENABLED") != "false":
        raise ConfigurationError("LIVE_ENABLED must be explicitly set to false.")

    environment = os.environ.get("TRADE_SYSTEM_ENVIRONMENT")
    if environment not in ("TRAINING", "PAPER"):
        raise ConfigurationError("TRADE_SYSTEM_ENVIRONMENT must be TRAINING or PAPER.")

    return cast(RuntimeEnvironment, environment)


def require_event_environment(environment: object) -> None:
    if environment != runtime_environment():
        raise ValueError("The event environment must match the runtime environment.")
