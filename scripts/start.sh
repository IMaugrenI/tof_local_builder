#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

source scripts/compose_wrapper.sh

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

python3 scripts/wizard.py --ensure

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

set -a
source .env
set +a

mkdir -p data/ollama data/open-webui sandbox/workspace sandbox/output sandbox/examples

compose_cmd down --remove-orphans || true
compose_cmd up -d --build

echo "Waiting for services..."
bash scripts/ensure_model.sh || true

bash scripts/check.sh || true

echo
echo "Acceleration mode: ${BUILDER_COMPOSE_MODE}"
echo "Default Ollama model: ${DEFAULT_OLLAMA_MODEL:-qwen2.5:0.5b}"
echo "Open WebUI: http://localhost:3000"
echo "Tool server base URL to paste into Open WebUI > Tool Server Management:"
echo "http://127.0.0.1:8099"

if [ "${BUILDER_OPEN_BROWSER:-1}" = "1" ]; then
  python3 scripts/wizard.py --open-webui >/dev/null 2>&1 || true
fi
