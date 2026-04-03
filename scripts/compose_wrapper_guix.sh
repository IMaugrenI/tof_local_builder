#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BUILDER_ACCELERATION="${BUILDER_ACCELERATION:-auto}"
BUILDER_COMPOSE_FILES=(-f compose.guix.yml)
BUILDER_COMPOSE_MODE="cpu"

case "$BUILDER_ACCELERATION" in
  auto)
    ;;
  intel)
    if [ -e /dev/dri/renderD128 ]; then
      BUILDER_COMPOSE_FILES+=(-f compose.intel.yml)
      BUILDER_COMPOSE_MODE="intel"
    else
      echo "WARN: BUILDER_ACCELERATION=intel requested but /dev/dri/renderD128 was not found. Falling back to CPU." >&2
    fi
    ;;
  cpu)
    ;;
  *)
    echo "Unknown BUILDER_ACCELERATION='$BUILDER_ACCELERATION'. Expected: auto, cpu, or intel." >&2
    return 1 2>/dev/null || exit 1
    ;;
esac

compose_guix_cmd() {
  docker compose "${BUILDER_COMPOSE_FILES[@]}" "$@"
}
