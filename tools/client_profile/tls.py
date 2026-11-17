"""Check hostname/trust validation using only the disposable PostgreSQL server."""

import json
import os
from pathlib import Path

import psycopg

args = {
    "host": "localhost",
    "hostaddr": "127.0.0.1",
    "port": 55432,
    "user": "trade_system",
    "dbname": "trade_system",
    "password": os.environ["POSTGRES_PASSWORD"],
    "connect_timeout": 5,
    "sslrootcert": "/results/test-server-public.crt",
    "sslmode": "verify-full",
}
results = []
with psycopg.connect(**args) as connection:
    row = connection.execute(
        "SELECT ssl, version, cipher FROM pg_stat_ssl WHERE pid=pg_backend_pid()"
    ).fetchone()
    assert row and row[0] is True
    assert connection.execute("SELECT 1").fetchone() == (1,)
    results.append({"case": "trusted_hostname", "result": "PASS", "ssl": row})
for case, change in [
    ("wrong_hostname", {"host": "wrong.invalid"}),
    ("missing_trust", {"sslrootcert": "/does-not-exist.crt"}),
]:
    try:
        with psycopg.connect(**(args | change)):
            pass
    except psycopg.OperationalError as error:
        results.append(
            {
                "case": case,
                "result": "PASS_REJECTED",
                "error": str(error).replace(args["password"], "[REDACTED]"),
            }
        )
    else:
        raise AssertionError(case + " should fail")
Path("/results/tls.json").write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
