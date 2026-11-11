"""Read-only endpoints for the local diagnostic API."""

import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from importlib.metadata import version
from typing import Literal

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from infrastructure.database.readiness import (
    DatabaseState,
    MigrationState,
    check_database,
)
from infrastructure.security.config import runtime_environment
from infrastructure.telemetry import log_event, request_correlation_id, tracer


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    runtime_environment()
    yield


class HealthResponse(BaseModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    status: Literal["ok"] = "ok"


class ReadinessChecks(BaseModel):
    database: DatabaseState
    migrations: MigrationState


class ReadinessResponse(BaseModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    status: Literal["ready", "not_ready"]
    checks: ReadinessChecks


class SystemInfoResponse(BaseModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    service: Literal["deep-trade-system"] = "deep-trade-system"
    version: str
    live_enabled: Literal[False] = False


APP_VERSION = version("deep-trade-system")
app = FastAPI(
    title="Trade System Diagnostic API",
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)


logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_request(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    correlation_id = request_correlation_id(request.headers.get("X-Correlation-ID"))
    with tracer.start_as_current_span(
        "diagnostic.request", record_exception=False, set_status_on_exception=False
    ):
        try:
            response = await call_next(request)
        except Exception as error:
            log_event(
                logger,
                "diagnostic_failed",
                level=logging.ERROR,
                correlation_id=correlation_id,
                route=getattr(request.scope.get("route"), "name", "unmatched"),
                status_code=500,
                error_type=type(error).__name__,
            )
            response = JSONResponse(
                {"detail": "Internal server error"}, status_code=500
            )
        else:
            log_event(
                logger,
                "diagnostic_request",
                correlation_id=correlation_id,
                route=getattr(request.scope.get("route"), "name", "unmatched"),
                status_code=response.status_code,
            )

    response.headers["X-Correlation-ID"] = correlation_id
    return response


@app.get("/health")
def health() -> HealthResponse:
    return HealthResponse()


@app.get("/readiness", responses={503: {"model": ReadinessResponse}})
def readiness(response: Response) -> ReadinessResponse:
    database, migrations = check_database()
    checks = ReadinessChecks(database=database, migrations=migrations)
    if database == "ok" and migrations == "current":
        return ReadinessResponse(status="ready", checks=checks)

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(status="not_ready", checks=checks)


@app.get("/info")
def info() -> SystemInfoResponse:
    return SystemInfoResponse(version=APP_VERSION)
