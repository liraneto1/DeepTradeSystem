"""Start the diagnostic API on loopback with application-level request logging."""

import uvicorn

from apps.api.main import app
from infrastructure.telemetry import configure_logging


def main() -> None:
    configure_logging()
    uvicorn.run(app, host="127.0.0.1", port=8000, access_log=False, proxy_headers=False)


if __name__ == "__main__":
    main()
