#!/usr/bin/env bash
set -euo pipefail

echo "Checking repo_bridge health..."
curl -fsS http://localhost:${REPO_BRIDGE_PORT:-8099}/health && echo

echo "Checking repo_bridge roots..."
curl -fsS http://localhost:${REPO_BRIDGE_PORT:-8099}/roots && echo
