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

needs_wizard() {
  python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from builder_bootstrap import merge_env, needs_first_run_wizard, parse_env_file

env, _ = parse_env_file(Path(".env"))
env = merge_env(env)
raise SystemExit(0 if needs_first_run_wizard(env) else 1)
PY
}

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

if needs_wizard; then
  check_required "setup-web" "http://127.0.0.1:${SETUP_UI_PORT:-3011}/health"
  check_optional "repo-bridge-v2" "http://127.0.0.1:${REPO_BRIDGE_PORT:-8099}/health"
  check_optional "open-webui" "http://127.0.0.1:${OPENWEBUI_PORT:-3000}"
else
  check_optional "setup-web" "http://127.0.0.1:${SETUP_UI_PORT:-3011}/health"
  check_required "repo-bridge-v2" "http://127.0.0.1:${REPO_BRIDGE_PORT:-8099}/health"
  check_required "open-webui" "http://127.0.0.1:${OPENWEBUI_PORT:-3000}"
fi

exit "$status"
