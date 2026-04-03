#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

status=0

check_required() {
  local name="$1"
  local url="$2"
  if curl -fsS "$url" >/dev/null 2>&1; then
    echo "[ok] ${name} -> ${url}"
  else
    echo "[fail] ${name} -> ${url}"
    status=1
  fi
}

check_optional() {
  local name="$1"
  local url="$2"
  if curl -fsS "$url" >/dev/null 2>&1; then
    echo "[ok] ${name} -> ${url}"
  else
    echo "[warn] ${name} not running -> ${url}"
  fi
}

check_optional "setup-web" "http://127.0.0.1:${SETUP_UI_PORT:-3011}/health"
check_required "repo-bridge-v2" "http://127.0.0.1:${REPO_BRIDGE_PORT:-8099}/health"
check_required "open-webui" "http://127.0.0.1:${OPENWEBUI_PORT:-3000}"

exit "$status"
