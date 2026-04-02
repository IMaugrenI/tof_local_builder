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

echo
echo "Builder setup prepared."
echo "Check or set these values in .env before starting if you want to override the defaults:"
echo "- SOURCE_REPO_PATH"
echo "- HOST_UID"
echo "- HOST_GID"
echo "- DEFAULT_OLLAMA_MODEL (default: ${DEFAULT_OLLAMA_MODEL:-qwen2.5:0.5b})"
echo "- BUILDER_ACCELERATION (default: ${BUILDER_ACCELERATION:-auto})"
echo "- BUILDER_OPEN_BROWSER (default: ${BUILDER_OPEN_BROWSER:-1})"
echo
echo "Notes:"
echo "- The first start opens a small local setup wizard if the builder is not configured yet."
echo "- The first start also ensures a small default Ollama model is available."
echo "- Tool server base URL for Open WebUI: http://127.0.0.1:8099"
echo
echo "Next steps:"
echo "bash scripts/up.sh"
echo "bash scripts/check.sh"
