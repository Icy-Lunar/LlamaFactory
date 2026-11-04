#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"
export PYTHONUTF8=1

if [[ -n "${PYTHON_BIN:-}" ]]; then
    BOOTSTRAP_PYTHON="$PYTHON_BIN"
elif command -v python3.12 >/dev/null 2>&1; then
    BOOTSTRAP_PYTHON=python3.12
elif command -v python3 >/dev/null 2>&1; then
    BOOTSTRAP_PYTHON=python3
else
    echo "Python 3.11 or newer is required." >&2
    exit 1
fi

if [[ $# -eq 0 ]]; then
    exec "$BOOTSTRAP_PYTHON" -X utf8 scripts/terminal_wizard.py
fi

exec "$BOOTSTRAP_PYTHON" -X utf8 scripts/bootstrap_multibackend.py "$@"
