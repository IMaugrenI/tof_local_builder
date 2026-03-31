#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  cp env.repo-bridge.example .env
fi

mkdir -p data/ollama data/open-webui sandbox/workspace sandbox/output sandbox/examples

echo "Edit SOURCE_REPO_PATH in .env before starting V3."
echo "Then run: docker compose -f compose.v3.repo-bridge.yml up -d --build"
