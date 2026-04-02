#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

source scripts/compose_wrapper.sh

compose_cmd pull --ignore-pull-failures || true

echo
echo "Pull finished."
echo "Run 'bash scripts/up.sh' to rebuild local services if needed."
