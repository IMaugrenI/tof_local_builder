#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  cp env.readonly-sandbox.example .env
fi

mkdir -p data/ollama data/open-webui sandbox/workspace sandbox/output sandbox/examples

echo "Edit SOURCE_REPO_PATH in .env before starting V2."
echo "Then run: docker compose -f compose.v2.readonly-sandbox.full.yml up -d"
