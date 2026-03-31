# V3 repo bridge

## Purpose

V3 adds a small local bridge service so the stack can access a mounted source path directly instead of relying on uploaded source bundles only.

## Boundary

- source repo is read-only
- writes are restricted to builder sandbox subroots only
- no writes into the source repo

## Services

- Ollama
- Open WebUI
- repo_bridge

## Bridge endpoints

- `GET /health`
- `GET /roots`
- `GET /tree?path=`
- `GET /read?path=`
- `POST /write`

## Read model

The bridge reads from:

- `/workspace/source_repo_ro`

## Write model

The bridge only writes to:

- `/workspace/builder_sandbox/workspace`
- `/workspace/builder_sandbox/output`

## Start

```bash
bash scripts/bootstrap_v3_repo_bridge.sh
nano .env
```

Set:

```bash
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
```

Then:

```bash
docker compose -f compose.v3.repo-bridge.yml up -d --build
bash scripts/healthcheck.sh
bash scripts/test_repo_bridge.sh
```

## Practical note

This adds the real local path bridge that V2 intentionally did not include.
It still does not mean that Open WebUI magically browses the filesystem by itself.
What it gives you is a controlled local service that can read source paths and write reviewed artifacts into the sandbox.
