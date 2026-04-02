#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

DEFAULT_MODEL="${DEFAULT_OLLAMA_MODEL:-qwen2.5:0.5b}"
OLLAMA_URL="http://127.0.0.1:${OLLAMA_PORT:-11434}"

if [ -z "$DEFAULT_MODEL" ]; then
  echo "DEFAULT_OLLAMA_MODEL is empty. Skipping default model check."
  exit 0
fi

echo "Ensuring default Ollama model is available: ${DEFAULT_MODEL}"

for _ in $(seq 1 30); do
  if curl -fsS "${OLLAMA_URL}/api/tags" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

if ! curl -fsS "${OLLAMA_URL}/api/tags" >/dev/null 2>&1; then
  echo "WARN: Ollama is not ready yet. Skipping default model pull."
  exit 0
fi

if docker exec -i tof_local_builder_ollama ollama list 2>/dev/null | awk 'NR > 1 {print $1}' | grep -Fxq "${DEFAULT_MODEL}"; then
  echo "Default Ollama model already present: ${DEFAULT_MODEL}"
  exit 0
fi

echo "Pulling default Ollama model: ${DEFAULT_MODEL}"
docker exec -i tof_local_builder_ollama ollama pull "${DEFAULT_MODEL}"
