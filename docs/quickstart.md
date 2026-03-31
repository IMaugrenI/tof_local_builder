# Quickstart

## 1. Create your `.env`

Copy `.env.example` to `.env` and set at least:

```env
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
BUILDER_SANDBOX_PATH=./sandbox
HOST_UID=1000
HOST_GID=1000
ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 2. Start the product

```bash
bash scripts/start.sh
```

## 3. Check the product

```bash
bash scripts/check.sh
```

## 4. Open the GUI

- `http://localhost:3000`

## 5. In Open WebUI

Go to:

- `Tool-Server verwalten`

Paste:

- `http://127.0.0.1:8099/openapi.json`

## 6. First chat tests

- list the source root
- read `MANIFEST.md`
- write a note into `output/test/chat_note.md`
