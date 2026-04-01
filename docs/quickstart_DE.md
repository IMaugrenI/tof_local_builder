# Schnellstart

## 1. `.env` anlegen

`.env.example` nach `.env` kopieren und mindestens Folgendes setzen:

```env
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
BUILDER_SANDBOX_PATH=./sandbox
HOST_UID=1000
HOST_GID=1000
ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 2. Produkt starten

```bash
bash scripts/start.sh
```

## 3. Produkt prüfen

```bash
bash scripts/check.sh
```

## 4. GUI öffnen

- `http://localhost:3000`

## 5. In Open WebUI

Gehe zu:

- `Tool-Server verwalten`

Füge dort ein:

- `http://127.0.0.1:8099/openapi.json`

## 6. Erste Chat-Tests

- Root der Quelle auflisten
- `MANIFEST.md` lesen
- eine Notiz nach `output/test/chat_note.md` schreiben
