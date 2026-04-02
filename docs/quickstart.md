# Quickstart

## 1. Create your `.env`

Copy `.env.example` to `.env` and set at least:

```env
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
BUILDER_SANDBOX_PATH=./sandbox
HOST_UID=1000
HOST_GID=1000
ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DEFAULT_OLLAMA_MODEL=qwen2.5:0.5b
BUILDER_ACCELERATION=auto
BUILDER_OPEN_BROWSER=1
BUILDER_SETUP_DONE=0
```

## 2. Start the product

```bash
bash scripts/start.sh
```

The first startup ensures the default Ollama model is present. If the builder is not configured yet, a small local setup wizard opens first and then hands over to the web surface.

## 3. Check the product

```bash
bash scripts/check.sh
```

## 4. Open the GUI

- `http://localhost:3000`

## 5. In Open WebUI

Go to:

- `Tool Server Management`

Paste the base URL:

- `http://127.0.0.1:8099`

## 6. First chat tests

- list the source root
- read `README.md`
- write a note into `output/test/chat_note.md`

## 7. Reopen the setup wizard later if needed

```bash
python3 scripts/wizard.py --force
```
