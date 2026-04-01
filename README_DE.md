# tof_local_builder

> Deutsch ist die Spiegelversion dieses Repositories. Der englische Primärtext liegt in `README.md`.

Lokaler GUI-first Builder für Einzelplatz- oder kleine lokale Firmen-Setups.

## Kurzüberblick

- nutzt lokale Modelle über Ollama
- stellt eine Browser-GUI über Open WebUI bereit
- liest einen gemounteten Quellpfad read-only
- schreibt geprüfte Artefakte nur in eine lokale Sandbox
- hält Quellraum und schreibbaren Ausgaberaum sauber getrennt

## Wofür dieses Repo da ist

Dieses Repository ist für kontrollierte lokale Builder-Workflows gedacht:

- lokale Prompt- und editorbasierte Experimente
- read-only Zugriff auf ein gemountetes Source-Repo oder einen Source-Pfad
- geprüfte Writes in eine Sandbox statt in die Quelle
- GUI-first lokale Interaktion über Open WebUI

## Produktgrenze

- Source-Repo bleibt read-only
- Writes bleiben auf `sandbox/workspace` und `sandbox/output` begrenzt
- keine direkten Schreibzugriffe in das Source-Repo
- das hier ist ein Builder-Stack, kein allgemeines Wissenssystem

## Runtime-Komponenten

- `ollama` = lokaler Modellträger
- `open-webui` = Browser-GUI
- `repo-bridge` = kontrollierte Lese-/Schreibgrenze für Quelle und Sandbox

## Schnellstart

1. `.env.example` nach `.env` kopieren
2. `SOURCE_REPO_PATH`, `HOST_UID` und `HOST_GID` setzen
3. starten:

```bash
bash scripts/start.sh
```

4. prüfen:

```bash
bash scripts/check.sh
```

5. öffnen:

- `http://localhost:3000`

6. in Open WebUI zu folgendem Bereich gehen:

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

- `compose.yml`
- `.env.example`
- `scripts/start.sh`
- `scripts/check.sh`
- `docs/quickstart.md`
- `services/repo_bridge/`
- `sandbox/`

## Verwandte öffentliche Repositories

- [`tof-showcase`](https://github.com/IMaugrenI/tof-showcase) — öffentlicher Architekturrahmen
- [`tof_local_knowledge`](https://github.com/IMaugrenI/tof_local_knowledge) — on-prem lokales Wissenssystem
