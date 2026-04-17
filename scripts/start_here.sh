#!/usr/bin/env bash
set -euo pipefail
bash scripts/setup.sh
bash scripts/up.sh
bash scripts/check.sh
