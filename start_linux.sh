#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"
export PYTHONUTF8=1

python_is_compatible() {
    local executable="$1"
    [[ -n "$executable" ]] || return 1
    command -v "$executable" >/dev/null 2>&1 || [[ -x "$executable" ]] || return 1
    "$executable" -X utf8 -c 'import sys, venv; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] <= (3, 13) else 1)' \
        >/dev/null 2>&1
}

find_python() {
    local candidate
    for candidate in "${PYTHON_BIN:-}" python3.12 python3.13 python3.11 python3 python; do
        if python_is_compatible "$candidate"; then
            command -v "$candidate" 2>/dev/null || printf '%s\n' "$candidate"
            return 0
        fi
    done
    return 1
}

sudo_prefix=()
prepare_privileges() {
    if [[ "$(id -u)" -eq 0 ]]; then
        sudo_prefix=()
    elif command -v sudo >/dev/null 2>&1; then
        sudo -v
        sudo_prefix=(sudo)
    else
        echo 'Root privileges or sudo are required to install Python system packages.' >&2
        exit 1
    fi
}

install_python() {
    prepare_privileges
    if command -v apt-get >/dev/null 2>&1; then
        "${sudo_prefix[@]}" apt-get update
        if apt-cache show python3.12 >/dev/null 2>&1; then
            "${sudo_prefix[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y \
                python3.12 python3.12-venv python3-pip git curl ca-certificates
        else
            "${sudo_prefix[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y \
                python3 python3-venv python3-pip git curl ca-certificates
        fi
    elif command -v dnf >/dev/null 2>&1; then
        "${sudo_prefix[@]}" dnf install -y python3 python3-pip python3-devel git curl ca-certificates
    elif command -v zypper >/dev/null 2>&1; then
        "${sudo_prefix[@]}" zypper --non-interactive install python3 python3-pip python3-devel git curl ca-certificates
    elif command -v pacman >/dev/null 2>&1; then
        "${sudo_prefix[@]}" pacman -Sy --needed --noconfirm python python-pip git curl ca-certificates
    else
        echo 'No supported package manager was found. Install Python 3.11-3.13 with the venv module.' >&2
        exit 1
    fi
}

if [[ "$(uname -s)" != "Linux" ]]; then
    echo 'This launcher supports Linux only. Use start_windows.bat on Windows.' >&2
    exit 1
fi

BOOTSTRAP_PYTHON="$(find_python || true)"
if [[ -z "$BOOTSTRAP_PYTHON" ]]; then
    echo 'A compatible Python runtime was not found. Installing system prerequisites...'
    install_python
    BOOTSTRAP_PYTHON="$(find_python || true)"
fi
if [[ -z "$BOOTSTRAP_PYTHON" ]]; then
    echo 'Python was installed, but Python 3.11-3.13 with venv is still unavailable.' >&2
    echo 'Use Ubuntu 24.04+ or install Python 3.12, then run this file again.' >&2
    exit 1
fi

export PYTHON_BIN="$BOOTSTRAP_PYTHON"
echo "Bootstrap Python: $BOOTSTRAP_PYTHON"

if [[ $# -eq 0 ]]; then
    exec "$BOOTSTRAP_PYTHON" -X utf8 scripts/terminal_wizard.py
fi

exec "$BOOTSTRAP_PYTHON" -X utf8 scripts/bootstrap_multibackend.py "$@"
