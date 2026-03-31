#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  cp env.openwebui-tool.example .env
fi

mkdir -p data/ollama data/open-webui sandbox/workspace sandbox/output sandbox/examples

echo "Edit SOURCE_REPO_PATH, HOST_UID and HOST_GID in .env before starting V3.1."
echo "Hint: HOST_UID=$(id -u) and HOST_GID=$(id -g) on the host."
echo "Then run: docker compose -f compose.v3.1.openwebui-tool.yml up -d --build"
