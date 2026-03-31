#!/usr/bin/env bash
set -euo pipefail

docker exec -it tof_local_builder_openwebui sh -lc 'test -d /workspace/source_repo_ro && echo SOURCE_OK; test -d /workspace/builder_sandbox/workspace && echo WORKSPACE_OK; test -d /workspace/builder_sandbox/output && echo OUTPUT_OK; test -d /workspace/builder_sandbox/examples && echo EXAMPLES_OK'
