#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

BUILDER_ACCELERATION="${BUILDER_ACCELERATION:-cpu}"
BUILDER_COMPOSE_FILES=(-f compose.yml)
BUILDER_COMPOSE_MODE="cpu"

has_intel_render_node() {
  [ "$(uname -s)" = "Linux" ] && [ -e /dev/dri/renderD128 ]
}

case "$BUILDER_ACCELERATION" in
  auto)
    if has_intel_render_node; then
      BUILDER_COMPOSE_FILES+=(-f compose.intel.yml)
      BUILDER_COMPOSE_MODE="intel"
    else
      BUILDER_COMPOSE_MODE="cpu"
    fi
    ;;
  intel)
    if has_intel_render_node; then
      BUILDER_COMPOSE_FILES+=(-f compose.intel.yml)
      BUILDER_COMPOSE_MODE="intel"
    else
      echo "WARN: BUILDER_ACCELERATION=intel requested but /dev/dri/renderD128 was not found. Falling back to CPU." >&2
      BUILDER_COMPOSE_MODE="cpu"
    fi
    ;;
  cpu)
    BUILDER_COMPOSE_MODE="cpu"
    ;;
  *)
    echo "Unknown BUILDER_ACCELERATION='$BUILDER_ACCELERATION'. Expected: auto, cpu, or intel." >&2
    return 1 2>/dev/null || exit 1
    ;;
esac

export BUILDER_COMPOSE_MODE

compose_cmd() {
  docker compose "${BUILDER_COMPOSE_FILES[@]}" "$@"
}
