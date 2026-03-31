#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  cp env.toolserver-cors.example .env
  echo "Created .env from env.toolserver-cors.example"
fi

if ! grep -q '^SOURCE_REPO_PATH=' .env; then
  echo "Missing SOURCE_REPO_PATH in .env"
  exit 1
fi

if ! grep -q '^HOST_UID=' .env; then
  echo "Missing HOST_UID in .env"
  exit 1
fi

if ! grep -q '^HOST_GID=' .env; then
  echo "Missing HOST_GID in .env"
  exit 1
fi

mkdir -p data/ollama data/open-webui sandbox/workspace sandbox/output sandbox/examples

docker compose down --remove-orphans || true
docker compose -f compose.toolserver-cors.yml up -d --build

echo "Waiting for services..."
sleep 5

bash scripts/healthcheck.sh || true
curl -fsS http://localhost:8099/health && echo
curl -fsS http://localhost:8099/openapi.json > /dev/null && echo "repo_bridge openapi: OK"

echo
echo "Open WebUI: http://localhost:3000"
echo "Tool server URL to paste into Open WebUI > Tool-Server verwalten:"
echo "http://127.0.0.1:8099/openapi.json"
