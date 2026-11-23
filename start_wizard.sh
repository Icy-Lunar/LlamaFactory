#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"
export PYTHONUTF8=1

if [[ -n "${PYTHON_BIN:-}" ]]; then
    BOOTSTRAP_PYTHON="$PYTHON_BIN"
elif command -v python3 >/dev/null 2>&1; then
    BOOTSTRAP_PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    BOOTSTRAP_PYTHON=python
else
    exec bash "$PROJECT_ROOT/start_linux.sh"
fi

exec "$BOOTSTRAP_PYTHON" -X utf8 scripts/terminal_wizard.py "$@"
