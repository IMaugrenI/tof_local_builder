#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

source scripts/compose_wrapper_guix.sh

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

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

write_host_snapshot() {
  python3 - <<'PY'
import json
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from builder_bootstrap import MODEL_OPTIONS, detect_host, recommended_acceleration_options

root = Path(".").resolve()
snapshot = detect_host()
snapshot["acceleration_options"] = recommended_acceleration_options(snapshot)
snapshot["model_options"] = list(MODEL_OPTIONS)
snapshot["snapshot_source"] = "host"
path = root / ".runtime" / "host_snapshot.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
}

wait_for_url() {
  local url="$1"
  local label="$2"
  local attempts="${3:-60}"
  local sleep_seconds="${4:-2}"
  for _ in $(seq 1 "$attempts"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep "$sleep_seconds"
  done
  echo "[fail] ${label} not ready -> ${url}" >&2
  return 1
}

set -a
source .env
set +a

mkdir -p .runtime data/ollama data/open-webui sandbox/workspace sandbox/output sandbox/examples

if ! write_host_snapshot; then
  echo "[warn] host snapshot could not be written; setup-web may fall back to container-local detection" >&2
fi

wizard_needed=0
if needs_wizard; then
  wizard_needed=1
  compose_guix_cmd up -d --build setup-web
  SETUP_URL="http://127.0.0.1:${SETUP_UI_PORT:-3011}"
  wait_for_url "${SETUP_URL}/health" "setup-web" 60 1
  echo
  echo "GUiX setup page: ${SETUP_URL}"
  echo "Save the setup there once. Afterwards this script continues automatically."
  if [ "${BUILDER_OPEN_BROWSER:-1}" = "1" ]; then
    python3 - <<PY >/dev/null 2>&1 || true
import webbrowser
webbrowser.open("${SETUP_URL}", new=2)
PY
  fi
  until ! needs_wizard; do
    sleep 2
  done
  set -a
  source .env
  set +a
fi

compose_guix_cmd up -d --build ollama repo-bridge-v2 open-webui

echo "Waiting for services..."
wait_for_url "http://127.0.0.1:${REPO_BRIDGE_PORT:-8099}/health" "repo-bridge-v2" 45 2
wait_for_url "http://127.0.0.1:${OPENWEBUI_PORT:-3000}" "open-webui" 90 2

docker exec tof_local_builder_ollama ollama pull "${DEFAULT_OLLAMA_MODEL:-qwen2.5:0.5b}" >/dev/null 2>&1 || true

bash scripts/check_guix.sh || true

echo
echo "Acceleration mode: ${BUILDER_COMPOSE_MODE}"
echo "Default Ollama model: ${DEFAULT_OLLAMA_MODEL:-qwen2.5:0.5b}"
echo "Setup page: http://127.0.0.1:${SETUP_UI_PORT:-3011}"
echo "Open WebUI: http://127.0.0.1:${OPENWEBUI_PORT:-3000}"
echo "Repo bridge v2: http://127.0.0.1:${REPO_BRIDGE_PORT:-8099}"
echo
echo "Tool server base URL for Open WebUI > Tool Server Management:"
echo "http://127.0.0.1:${REPO_BRIDGE_PORT:-8099}"

if [ "${BUILDER_OPEN_BROWSER:-1}" = "1" ] && [ "$wizard_needed" -eq 0 ]; then
  python3 - <<PY >/dev/null 2>&1 || true
import webbrowser
webbrowser.open("http://127.0.0.1:${OPENWEBUI_PORT:-3000}", new=2)
PY
fi
