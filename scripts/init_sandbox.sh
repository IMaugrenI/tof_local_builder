#!/usr/bin/env bash
set -euo pipefail

mkdir -p sandbox/workspace sandbox/output sandbox/examples

echo "Sandbox initialized."
echo "Write-enabled target for experiments: sandbox/workspace"
echo "Suggested review/output area:          sandbox/output"
echo "Example file included:                  sandbox/examples/coinflip.pu"
