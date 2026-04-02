# tof_local_builder

> Deutsch ist die Spiegelversion dieses Repositories. Der englische Primärtext liegt in `README.md`.

Lokaler GUI-first Builder für Einzelplatz- oder kleine lokale Firmen-Setups.

## Kurzüberblick

- nutzt lokale Modelle über Ollama
- stellt eine Browser-GUI über Open WebUI bereit
- liest einen gemounteten Quellpfad read-only
- schreibt geprüfte Artefakte nur in eine lokale Sandbox
- hält Quellraum und schreibbaren Ausgaberaum sauber getrennt
- der erste Start stellt automatisch ein kleines Default-Modell bereit
- bleibt standardmäßig CPU-sicher und aktiviert auf Linux automatisch den Intel-Render-Node-Pfad, wenn er vorhanden ist

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

1. lokale Vorbereitung ausführen:

```bash
bash scripts/setup.sh
```

2. den Stack starten:

```bash
bash scripts/up.sh
```

3. Health prüfen:

```bash
bash scripts/check.sh
```

4. öffnen:

- `http://localhost:3000`

5. in Open WebUI zu folgendem Bereich gehen:

- `Tool Server Management`

6. dort die Basis-URL einfügen:

- `http://127.0.0.1:8099`

## First-Run-Standards

- der erste `up.sh`-Lauf stellt sicher, dass `DEFAULT_OLLAMA_MODEL` vorhanden ist
- das Standardmodell ist `qwen2.5:0.5b`
- stärkere Hardware kann später über `.env` auf größere Ollama-Modelle wechseln
- `BUILDER_ACCELERATION=auto` hält den Stack CPU-sicher und ergänzt automatisch den Intel-`/dev/dri`-Override, wenn auf Linux ein Render-Node vorhanden ist

## Befehle für den Betrieb

Nutze für den normalen Betrieb diese kleine Befehlsoberfläche:

```bash
bash scripts/setup.sh
bash scripts/up.sh
bash scripts/check.sh
bash scripts/logs.sh
bash scripts/down.sh
```

Mehr Details:

- [`docs/commands_DE.md`](docs/commands_DE.md)

## Erforderliche `.env`-Werte

```env
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
BUILDER_SANDBOX_PATH=./sandbox
HOST_UID=1000
HOST_GID=1000
ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DEFAULT_OLLAMA_MODEL=qwen2.5:0.5b
BUILDER_ACCELERATION=auto
```

## Wichtige Dateien

- `compose.yml`
- `compose.intel.yml`
- `.env.example`
- `scripts/setup.sh`
- `scripts/up.sh`
- `scripts/check.sh`
- `scripts/down.sh`
- `scripts/ensure_model.sh`
- `scripts/compose_wrapper.sh`
- `docs/quickstart_DE.md`
- `docs/commands_DE.md`
- `services/repo_bridge/`
- `sandbox/`

## Verwandte öffentliche Repositories

- [`tof-showcase`](https://github.com/IMaugrenI/tof-showcase) — öffentlicher Architekturrahmen
- [`tof_local_knowledge`](https://github.com/IMaugrenI/tof_local_knowledge) — on-prem lokales Wissenssystem
