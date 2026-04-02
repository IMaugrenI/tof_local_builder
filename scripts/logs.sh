#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

source scripts/compose_wrapper.sh

if [ "$#" -gt 0 ]; then
  compose_cmd logs -f "$@"
else
  compose_cmd logs -f
fi
