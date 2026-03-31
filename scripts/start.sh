#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
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
docker compose up -d --build

echo "Waiting for services..."
sleep 8

bash scripts/check.sh || true

echo
echo "Open WebUI: http://localhost:3000"
echo "Tool server URL to paste into Open WebUI > Tool-Server verwalten:"
echo "http://127.0.0.1:8099/openapi.json"
