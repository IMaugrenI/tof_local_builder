#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

set -a
source .env
set +a

RUNTIME_DIR="$ROOT_DIR/.runtime/host_repo_bridge"
VENV_DIR="$RUNTIME_DIR/venv"
PID_FILE="$RUNTIME_DIR/bridge.pid"
LOG_FILE="$RUNTIME_DIR/bridge.log"

BRIDGE_HOST="${BUILDER_BIND_HOST:-127.0.0.1}"
BRIDGE_PORT="${REPO_BRIDGE_PORT:-8099}"
SANDBOX_VALUE="${BUILDER_SANDBOX_PATH:-./sandbox}"

ABS_SANDBOX_PATH="$(python3 - "$ROOT_DIR" "$SANDBOX_VALUE" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
value = Path(sys.argv[2]).expanduser()
if not value.is_absolute():
    value = (root / value).resolve()
else:
    value = value.resolve()
print(value)
PY
)"

mkdir -p "$RUNTIME_DIR" "$ABS_SANDBOX_PATH/workspace" "$ABS_SANDBOX_PATH/output" "$ABS_SANDBOX_PATH/examples"

if [ -f "$PID_FILE" ]; then
  OLD_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "${OLD_PID:-}" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Host repo bridge already running on PID $OLD_PID"
    echo "Local URL: http://127.0.0.1:${BRIDGE_PORT}"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
  python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/pip" install --disable-pip-version-check --no-input -r "$ROOT_DIR/services/host_repo_bridge/requirements.txt" >/dev/null

export SANDBOX_ROOT="$ABS_SANDBOX_PATH"
export ALLOW_ORIGINS="${ALLOW_ORIGINS:-http://localhost:3000,http://127.0.0.1:3000}"

(
  cd "$ROOT_DIR/services/host_repo_bridge"
  nohup "$VENV_DIR/bin/python" -m uvicorn app.main:app --host "$BRIDGE_HOST" --port "$BRIDGE_PORT" >"$LOG_FILE" 2>&1 &
  echo $! >"$PID_FILE"
)

sleep 1

NEW_PID="$(cat "$PID_FILE")"
if ! kill -0 "$NEW_PID" 2>/dev/null; then
  echo "Host repo bridge failed to start. Log:"
  cat "$LOG_FILE"
  exit 1
fi

echo "Host repo bridge started."
echo "Local URL: http://127.0.0.1:${BRIDGE_PORT}"
echo "Open WebUI tool server URL: http://host.docker.internal:${BRIDGE_PORT}"
