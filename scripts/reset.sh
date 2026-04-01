#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "WARNING: reset.sh is destructive."
echo "It stops the stack, removes local service data, and clears sandbox workspace/output."

docker compose down -v --remove-orphans || true
rm -rf data/ollama data/open-webui sandbox/workspace sandbox/output
mkdir -p data/ollama data/open-webui sandbox/workspace sandbox/output sandbox/examples

echo "Builder reset finished."
