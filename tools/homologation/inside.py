"""Container-only checks without a Docker socket or outbound network."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

RESULTS = Path("/results")


def connect_options() -> dict[str, Any]:
    return dict(
        host="localhost",
        hostaddr="127.0.0.1",
        port=5432,
        user="trade_system",
        dbname="trade_system",
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
    )


def verify_source() -> None:
    expected = json.loads(Path("/hml/source-manifest.json").read_text())
    for name, checksum in expected.items():
        data = (Path("/workspace") / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != checksum:
            raise RuntimeError("Source identity mismatch: " + name)


def run_tests(group: str) -> None:
    verify_source()
    commands = {
        "base": [
            "pytest",
            "-k",
            "not test_concurrent_duplicate_consumer_workers",
            "--junitxml=/results/base.xml",
        ],
        "concurrency": [
            "pytest",
            "tests/integration/test_postgres_migrations.py",
            "-k",
            "test_concurrent_duplicate_consumer_workers",
            "--junitxml=/results/concurrency.xml",
        ],
        "monitor": [
            "pytest",
            "tests/unit/test_outbox_monitor.py",
            "--junitxml=/results/monitor.xml",
        ],
    }
    if group == "base":
        for command in [
            [
                "ruff",
                "check",
                "src",
                "infrastructure",
                "apps",
                "tests",
                "tools/client_profile",
            ],
            [
                "ruff",
                "format",
                "--check",
                "src",
                "infrastructure",
                "apps",
                "tests",
                "tools/client_profile",
            ],
            ["mypy", "--cache-dir", "/tmp/hml-mypy-cache"],
        ]:
            subprocess.run(command, check=True, timeout=180)
    subprocess.run(
        commands[group] + ["-o", "cache_dir=/tmp/hml-pytest-cache"],
        check=True,
        timeout=900,
    )


def tls() -> None:
    import psycopg

    args = connect_options() | {
        "sslrootcert": "/results/test-server-public.crt",
        "sslmode": "verify-full",
    }
    results = []
    with psycopg.connect(**args) as connection:
        row = connection.execute(
            "SELECT ssl, version, cipher FROM pg_stat_ssl WHERE pid=pg_backend_pid()"
        ).fetchone()
        assert row and row[0] is True
        results.append({"case": "trusted_hostname", "result": "PASS"})
    for case, change in [
        ("wrong_hostname", {"host": "wrong.invalid"}),
        ("missing_trust", {"sslrootcert": "/does-not-exist.crt"}),
    ]:
        try:
            with psycopg.connect(**(args | change)):
                pass
        except psycopg.OperationalError:
            results.append({"case": case, "result": "PASS_REJECTED"})
        else:
            raise RuntimeError("TLS negative case accepted: " + case)
    (RESULTS / "tls.json").write_text(json.dumps(results, indent=2))


def auth() -> None:
    import psycopg

    with psycopg.connect(**connect_options()) as connection:
        assert connection.execute("SELECT 1").fetchone() == (1,)
    try:
        with psycopg.connect(**(connect_options() | {"password": ""})):
            pass
    except psycopg.OperationalError:
        pass
    else:
        raise RuntimeError("Passwordless TCP connection accepted")
    (RESULTS / "auth.json").write_text(
        '{"authenticated":true,"passwordless_rejected":true}\n'
    )


def persistence(write: bool) -> None:
    from decimal import Decimal

    import psycopg

    with psycopg.connect(**connect_options()) as connection:
        if write:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS hml_persistence "
                "(id integer primary key, amount numeric(20,8), ts timestamptz)"
            )
            connection.execute(
                "INSERT INTO hml_persistence VALUES (1, 123.45000001, "
                "'2026-11-18T00:00:00Z') ON CONFLICT (id) DO NOTHING"
            )
        row = connection.execute(
            "SELECT amount, ts AT TIME ZONE 'UTC' FROM hml_persistence WHERE id=1"
        ).fetchone()
        assert row and row[0] == Decimal("123.45000001")
        assert row[1].isoformat() == "2026-11-18T00:00:00"
    (
        RESULTS / ("persistence-before.json" if write else "persistence-after.json")
    ).write_text('{"decimal_exact":true,"utc_preserved":true}\n')


def inventory() -> None:
    subprocess.run(
        [
            "python",
            "/workspace/tools/client_profile/inventory.py",
            "/results/test-inventory",
        ],
        check=True,
        timeout=60,
    )


def runtime_inventory() -> None:
    subprocess.run(
        ["python", "/tools/inventory.py", "/results/runtime-inventory"],
        check=True,
        timeout=60,
    )


if __name__ == "__main__":
    os.umask(
        0o022
    )  # results readable by the host operator; secrets are never written here
    if os.environ.get("TRADE_SYSTEM_ENVIRONMENT") != "PAPER":
        raise RuntimeError("PAPER only")
    if os.environ.get("LIVE_ENABLED") != "false":
        raise RuntimeError("LIVE must be disabled")
    os.environ["POSTGRES_PASSWORD"] = (
        Path("/run/secrets/postgres_password").read_text().strip()
    )
    command = sys.argv[1]
    try:
        if command in {"base", "concurrency", "monitor"}:
            run_tests(command)
        elif command == "tls":
            tls()
        elif command == "auth":
            auth()
        elif command in {"persist-write", "persist-read"}:
            persistence(command == "persist-write")
        elif command == "inventory":
            inventory()
        elif command == "runtime-inventory":
            runtime_inventory()
        else:
            raise RuntimeError("Unknown command")
    except Exception as error:
        # Avoid emitting database URLs, passwords or subprocess arguments.
        print("Functional check failed: " + type(error).__name__, file=sys.stderr)
        sys.exit(1)
