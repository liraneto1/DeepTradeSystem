"""Read-only endpoints for the local diagnostic API."""

from importlib.metadata import version
from typing import Literal

from fastapi import FastAPI, Response, status
from pydantic import BaseModel

from infrastructure.database.readiness import (
    DatabaseState,
    MigrationState,
    check_database,
)


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
    docs_url=None,
    redoc_url=None,
)


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
