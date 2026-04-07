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

mkdir -p data/ollama data/open-webui sandbox/workspace sandbox/output sandbox/examples

bash scripts/start_host_repo_bridge.sh

docker compose -f compose.host_bridge.yml down --remove-orphans >/dev/null 2>&1 || true
docker compose -f compose.host_bridge.yml up -d

echo
echo "Open WebUI: http://localhost:${OPENWEBUI_PORT:-3000}"
echo "Local host repo bridge: http://127.0.0.1:${REPO_BRIDGE_PORT:-8099}"
echo "Open WebUI tool server URL: http://host.docker.internal:${REPO_BRIDGE_PORT:-8099}"
