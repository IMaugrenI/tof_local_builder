# tof_local_builder

> Die englischen Dateien sind die Primärtexte in diesem Repository. Die deutschen `_DE`-Dateien sind direkte Text-Klone zum leichteren Lesen.

Lokaler GUI-first-Builder für den Einsatz auf einem einzelnen Rechner.

## Was dieses Repo tut

- startet lokale Modelle über Ollama
- stellt eine Browser-GUI über Open WebUI bereit
- liest einen gemounteten Quellpfad nur read-only
- schreibt überprüfte Artefakte nur in eine lokale Sandbox

## Produktgrenze

- die Quell-Repo bleibt read-only
- Schreiben bleibt auf `sandbox/workspace` und `sandbox/output` begrenzt
- kein direktes Schreiben in die Quell-Repo

## Normale Nutzung

1. `.env.example` nach `.env` kopieren
2. `SOURCE_REPO_PATH`, `HOST_UID` und `HOST_GID` setzen
3. ausführen:

```bash
bash scripts/start.sh
```

4. prüfen:

```bash
bash scripts/check.sh
```

5. öffnen:

- `http://localhost:3000`

6. in Open WebUI zu Folgendem gehen:

- `Tool-Server verwalten`

7. dort einfügen:

- `http://127.0.0.1:8099/openapi.json`

## Erforderliche `.env`-Werte

```env
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
BUILDER_SANDBOX_PATH=./sandbox
HOST_UID=1000
HOST_GID=1000
ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Wichtige Dateien

### Kern
- `compose.yml`
- `.env.example`
- `scripts/start.sh`
- `scripts/check.sh`

### Doku
- `README.md`
- `README_DE.md`
- `docs/quickstart.md`
- `docs/quickstart_DE.md`
- `sandbox/README.md`
- `sandbox/README_DE.md`

### Laufzeitteile
- `services/repo_bridge/`
- `sandbox/`
