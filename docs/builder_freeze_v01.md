# Builder freeze v0.1

## Scope

This freeze captures the current stable baseline of the local builder stack.

Covered in this freeze:

- compose acceleration truth path is aligned
- local-only bind default is aligned
- runtime image refs are exposed through `.env`
- English and German mirror docs are aligned for the current operator surface
- compose healthchecks are present
- `scripts/check.sh` shows compose mode and compose service status
- runtime image pinning guidance exists in English and German

## Acceptance baseline

The frozen baseline is considered met when all of the following are true:

1. `bash scripts/up.sh` starts the stack cleanly
2. `bash scripts/check.sh` shows the selected compose mode
3. `bash scripts/check.sh` shows compose service status
4. compose healthchecks converge to healthy for the running services
5. the default Ollama model is available or is pulled during the normal first-run path
6. `repo_bridge` health responds
7. `repo_bridge` OpenAPI responds
8. Open WebUI opens locally on the configured local bind target

## Explicitly out of scope

This freeze does **not** yet claim:

- a pinned tested runtime image pair
- broader release guarantees outside the local builder baseline
- full chat-surface write E2E validation through Open WebUI
- broader multi-host or remote exposure guarantees

## Current operator posture

At this freeze point:

- the stack is still local-first
- published ports are local-only by default
- runtime image refs remain configurable through `.env`
- pinning should happen only after a tested Ollama and Open WebUI pair is verified

## Intent

This freeze exists to preserve the current builder baseline before the next change cycle.
