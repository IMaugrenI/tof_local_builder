# GUiX quickstart

## Ziel / Goal

Dieser Pfad startet zuerst eine kleine lokale Setup-Webseite und leitet danach auf Open WebUI weiter.

This path starts a small local setup website first and then hands over to Open WebUI.

## Start

```bash
bash scripts/up_guix.sh
```

## Ablauf / Flow

1. Falls `.env` fehlt, wird sie aus `.env.example` erzeugt.
2. Falls der Builder noch nicht fertig eingerichtet ist, startet `setup-web` auf `http://127.0.0.1:3011`.
3. Dort speicherst du Quellpfad, Modell und Beschleunigung.
4. Danach fährt der Hauptstack hoch:
   - `ollama`
   - `repo-bridge-v2`
   - `open-webui`
5. Anschließend geht es auf `http://127.0.0.1:3000` weiter.

## Health check

```bash
bash scripts/check_guix.sh
```

## Logs

```bash
bash scripts/logs_guix.sh
```

## Stoppen / Stop

```bash
bash scripts/down_guix.sh
```

## Tool-Server in Open WebUI

In `Tool Server Management` diese Base-URL eintragen:

```text
http://127.0.0.1:8099
```

## Repo bridge v2

Die neue Bridge trennt sauber:

- `roots` / `wurzeln`
- `tree` / `baum`
- `read` / `lesen`
- `stat` / `status`
- `find` / `finden`
- `search` / `suche`
- `mkdir` / `ordner`
- `write` / `schreiben`
- `health` / `gesundheit`

Schreibzugriffe bleiben auf `workspace` und `output` begrenzt.
