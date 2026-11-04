#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

export PYTHONUTF8=1
if [[ -n "${PYTHON_BIN:-}" ]]; then
    BOOTSTRAP_PYTHON="$PYTHON_BIN"
elif [[ "$(uname -s)" != Linux && -x "$PROJECT_ROOT/.venv/Scripts/python.exe" ]]; then
    BOOTSTRAP_PYTHON="$PROJECT_ROOT/.venv/Scripts/python.exe"
elif [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
    BOOTSTRAP_PYTHON="$PROJECT_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    BOOTSTRAP_PYTHON=python3
else
    BOOTSTRAP_PYTHON=python
fi
exec "$BOOTSTRAP_PYTHON" -X utf8 scripts/bootstrap_webui.py "$@"
