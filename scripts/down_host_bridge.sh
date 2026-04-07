#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

docker compose -f compose.host_bridge.yml down --remove-orphans
bash scripts/stop_host_repo_bridge.sh
