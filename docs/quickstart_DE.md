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
BUILDER_ACCELERATION=auto
BUILDER_OPEN_BROWSER=1
BUILDER_SETUP_DONE=0
```

## 2. Produkt starten

```bash
bash scripts/start.sh
```

Der erste Start stellt sicher, dass das Default-Ollama-Modell vorhanden ist. Wenn der Builder noch nicht eingerichtet ist, öffnet sich zuerst ein kleiner lokaler Setup-Wizard und übergibt danach an die Web-Oberfläche.

## 3. Produkt prüfen

```bash
bash scripts/check.sh
```

## 4. GUI öffnen

- `http://localhost:3000`

## 5. In Open WebUI

Gehe zu:

- `Tool Server Management`

Füge dort die Basis-URL ein:

- `http://127.0.0.1:8099`

## 6. Erste Chat-Tests

- Root der Quelle auflisten
- `README.md` lesen
- eine Notiz nach `output/test/chat_note.md` schreiben

## 7. Wizard später erneut öffnen, wenn nötig

```bash
python3 scripts/wizard.py --force
```
