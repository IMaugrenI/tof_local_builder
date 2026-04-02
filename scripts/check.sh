#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

bash scripts/healthcheck.sh || true

echo
echo "default model:"
if curl -fsS "http://localhost:${OLLAMA_PORT:-11434}/api/tags" | grep -Fq "\"name\":\"${DEFAULT_OLLAMA_MODEL:-qwen2.5:0.5b}\""; then
  echo "OK: ${DEFAULT_OLLAMA_MODEL:-qwen2.5:0.5b}"
else
  echo "WARN: ${DEFAULT_OLLAMA_MODEL:-qwen2.5:0.5b} not found yet"
fi

echo
echo "repo_bridge health:"
curl -fsS "http://localhost:${REPO_BRIDGE_PORT:-8099}/health" && echo

echo
echo "repo_bridge openapi:"
curl -fsS "http://localhost:${REPO_BRIDGE_PORT:-8099}/openapi.json" | head -c 200 && echo

echo
echo "tool server base URL for Open WebUI:"
echo "http://127.0.0.1:8099"
