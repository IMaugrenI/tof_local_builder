# Schnellstart

## 1. `.env` anlegen

`.env.example` nach `.env` kopieren und mindestens Folgendes setzen:

```env
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
BUILDER_SANDBOX_PATH=./sandbox
HOST_UID=1000
HOST_GID=1000
ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DEFAULT_OLLAMA_MODEL=qwen2.5:0.5b
BUILDER_ACCELERATION=cpu
BUILDER_OPEN_BROWSER=1
BUILDER_SETUP_DONE=0
```

## 2. Produkt starten

```bash
bash scripts/up.sh
```

## 3. Produkt prüfen

```bash
bash scripts/check.sh
```

## 4. Erste Tool-Tests

- `roots`
- `tree` mit `root=source`
- `read` mit `root=source` und `path=README.md`
- `mkdir` mit `target_root=output` und `relative_path=test`
- `write` mit `target_root=output` und `relative_path=test/chat_note.md`

## 5. Wizard später erneut öffnen

```bash
python3 scripts/wizard.py --force
```
