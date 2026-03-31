#!/usr/bin/env bash
set -euo pipefail

echo "Checking Ollama..."
curl -fsS http://localhost:11434/api/tags >/dev/null && echo "OK: Ollama"

echo "Checking Open WebUI..."
curl -fsS http://localhost:3000 >/dev/null && echo "OK: Open WebUI"

echo "Healthcheck finished."
