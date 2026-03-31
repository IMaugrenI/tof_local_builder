# tof_local_builder

Local GUI-first builder for one-machine company use.

## What it does

- runs local models through Ollama
- exposes a browser GUI through Open WebUI
- reads a mounted source path as read-only
- writes reviewed artifacts only into a local sandbox

## Product boundary

- source repo stays read-only
- writes stay limited to `sandbox/workspace` and `sandbox/output`
- no direct writes into the source repo

## Normal use

1. copy `.env.example` to `.env`
2. set `SOURCE_REPO_PATH`, `HOST_UID`, and `HOST_GID`
3. run:

```bash
bash scripts/start.sh
```

4. check:

```bash
bash scripts/check.sh
```

5. open:

- `http://localhost:3000`

6. in Open WebUI go to:

- `Tool-Server verwalten`

7. paste:

- `http://127.0.0.1:8099/openapi.json`

## Required `.env` values

```env
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
BUILDER_SANDBOX_PATH=./sandbox
HOST_UID=1000
HOST_GID=1000
ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Files that matter

- `compose.yml`
- `.env.example`
- `scripts/start.sh`
- `scripts/check.sh`
- `docs/quickstart.md`
- `services/repo_bridge/`
- `sandbox/`
