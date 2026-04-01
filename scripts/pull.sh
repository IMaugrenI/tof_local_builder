#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

docker compose pull --ignore-pull-failures || true

echo
echo "Pull finished."
echo "Run 'bash scripts/up.sh' to rebuild local services if needed."
