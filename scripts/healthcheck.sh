#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

retry_url() {
  local label="$1"
  local url="$2"
  local attempts="${3:-30}"
  local delay_seconds="${4:-2}"

  echo "Checking ${label}..."
  for _ in $(seq 1 "${attempts}"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "OK: ${label}"
      return 0
    fi
    sleep "${delay_seconds}"
  done

  echo "WARN: ${label} not ready yet"
  return 1
}

status=0

retry_url "Ollama" "http://localhost:${OLLAMA_PORT:-11434}/api/tags" || status=1
retry_url "Open WebUI" "http://localhost:${OPENWEBUI_PORT:-3000}" || status=1
retry_url "repo_bridge" "http://localhost:${REPO_BRIDGE_PORT:-8099}/health" || status=1

echo "Healthcheck finished."
exit "${status}"
