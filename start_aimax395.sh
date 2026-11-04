#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PYTHON_BIN="${PYTHON_BIN:-python3}"
if grep -qi microsoft /proc/sys/kernel/osrelease /proc/version 2>/dev/null; then
  export VENV_DIR="${VENV_DIR:-$PROJECT_ROOT/.venv-aimax395-wsl}"
  export HSA_ENABLE_DXG_DETECTION="${HSA_ENABLE_DXG_DETECTION:-1}"
  export NCCL_PROTO="${NCCL_PROTO:-LL128,Simple}"
else
  export VENV_DIR="${VENV_DIR:-$PROJECT_ROOT/.venv-aimax395}"
fi
export LLAMAFACTORY_LIGER_PROBE_TIMEOUT="${LLAMAFACTORY_LIGER_PROBE_TIMEOUT:-600}"
export LLAMAFACTORY_DEFAULT_COMPUTE_TYPE="${LLAMAFACTORY_DEFAULT_COMPUTE_TYPE:-fp16}"

exec bash "$PROJECT_ROOT/start_webui.sh" \
  --backend rocm \
  --rocm-profile aimax395 \
  "$@"
