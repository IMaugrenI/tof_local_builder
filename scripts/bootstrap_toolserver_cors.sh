#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  cp env.toolserver-cors.example .env
fi

mkdir -p data/ollama data/open-webui sandbox/workspace sandbox/output sandbox/examples

echo "Edit SOURCE_REPO_PATH, HOST_UID and HOST_GID in .env before starting tool-server mode."
echo "Then run: docker compose -f compose.toolserver-cors.yml up -d --build"
