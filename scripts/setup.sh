#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

mkdir -p data/ollama data/open-webui sandbox/workspace sandbox/output sandbox/examples

echo
echo "Builder setup prepared."
echo "Check or set these values in .env before starting:"
echo "- SOURCE_REPO_PATH"
echo "- HOST_UID"
echo "- HOST_GID"
echo
echo "Next steps:"
echo "bash scripts/up.sh"
echo "bash scripts/check.sh"
