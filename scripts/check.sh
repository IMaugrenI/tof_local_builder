#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

bash scripts/healthcheck.sh || true

echo
echo "repo_bridge health:"
curl -fsS http://localhost:8099/health && echo

echo
echo "repo_bridge openapi:"
curl -fsS http://localhost:8099/openapi.json | head -c 200 && echo
