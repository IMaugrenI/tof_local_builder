# Schnellstart

## 1. `.env` anlegen

`.env.example` nach `.env` kopieren und mindestens Folgendes setzen:

```env
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
BUILDER_SANDBOX_PATH=./sandbox
BUILDER_BIND_HOST=127.0.0.1
OLLAMA_IMAGE=ollama/ollama:latest
OPENWEBUI_IMAGE=ghcr.io/open-webui/open-webui:main
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

## 4. GUI öffnen

- `http://localhost:3000`

Standardmäßig bleiben veröffentlichte Ports über `BUILDER_BIND_HOST` an `127.0.0.1` gebunden.

## 5. In Open WebUI

Gehe zu:

- `Tool Server Management`

Füge dort diese Basis-URL ein:

- `http://127.0.0.1:8099`

## 6. Wizard später erneut öffnen

```bash
python3 scripts/wizard.py --force
```
