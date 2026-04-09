#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
CMD="$(basename "$0" .command)"
python3 run.py "$CMD" "$@"
