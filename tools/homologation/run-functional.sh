#!/usr/bin/env bash
# TS-PLAN-HML-002: explicit action only; never source this script.
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -B "$script_dir/runner.py" run "$@"

