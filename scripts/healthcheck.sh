#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

CMD="$(basename "$0" .sh)"
case "$CMD" in
  start) TARGET="up" ;;
  healthcheck) TARGET="check" ;;
  *) echo "Deprecated legacy helper: use python3 run.py <command>" >&2; exit 1 ;;
esac

python3 run.py "$TARGET" "$@"
