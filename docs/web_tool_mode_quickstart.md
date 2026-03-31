# Web tool mode quickstart

This is the simplest intended mode for direct Open WebUI chat access to a local source path.

## 1. Edit `.env`

Set at least:

```env
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
BUILDER_SANDBOX_PATH=./sandbox
HOST_UID=1000
HOST_GID=1000
ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 2. Start everything with one command

```bash
bash scripts/start_web_tool_mode.sh
```

## 3. If you want a quick check

```bash
bash scripts/check_web_tool_mode.sh
```

## 4. In Open WebUI

Go to:

- `Tool-Server verwalten`

Paste this URL:

- `http://127.0.0.1:8099/openapi.json`

## 5. First chat tests

- list files in the source root
- read `MANIFEST.md`
- write a note into `output/test/chat_note.md`

## Boundary

- source repo stays read-only
- writes stay limited to sandbox `workspace` and `output`
- no direct writes into the source repo
