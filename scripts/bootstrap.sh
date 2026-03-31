#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  cp .env.example .env
fi

mkdir -p data/ollama data/open-webui

docker compose pull
docker compose up -d

echo "tof_local_builder started."
echo "Open WebUI: http://localhost:3000"
echo "Ollama API:  http://localhost:11434"
