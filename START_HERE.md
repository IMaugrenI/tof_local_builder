# START HERE

This repository now has one intended product path for normal use.

## Goal

Open WebUI chat should work against a local read-only source path and only write reviewed artifacts into the local sandbox.

## The only normal path

1. Edit `.env`
2. Run:

```bash
bash scripts/start.sh
```

3. Check:

```bash
bash scripts/check.sh
```

4. Open:

- `http://localhost:3000`

5. In Open WebUI go to:

- `Tool-Server verwalten`

6. Paste this URL:

- `http://127.0.0.1:8099/openapi.json`

## Required `.env` values

```env
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
BUILDER_SANDBOX_PATH=./sandbox
HOST_UID=1000
HOST_GID=1000
ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Boundary

- source repo stays read-only
- writes stay limited to sandbox `workspace` and `output`
- no direct writes into the source repo

## Notes

Older experimental files may still exist in the repository, but the intended product entry is:

- `scripts/start.sh`
- `scripts/check.sh`
- `docs/web_tool_mode_quickstart.md`
