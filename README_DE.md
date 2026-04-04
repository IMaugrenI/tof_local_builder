# tof_local_builder

> Deutsch ist die Spiegelversion dieses Repositories. Der englische Primärtext liegt in `README.md`.
> Die Design-Begründung liegt in `WHY_DE.md`. Der englische Primärtext dazu liegt in `WHY.md`.

Lokaler GUI-first Builder für Einzelplatz- oder kleine lokale Firmen-Setups.

## Kurzüberblick

- nutzt lokale Modelle über Ollama
- stellt eine Browser-GUI über Open WebUI bereit
- liest einen gemounteten Quellpfad read-only
- schreibt geprüfte Artefakte nur in eine lokale Sandbox
- hält Quellraum und schreibbaren Ausgaberaum sauber getrennt
- der erste Start stellt automatisch ein kleines Default-Modell bereit
- der erste Start öffnet einen kleinen lokalen Setup-Wizard und übergibt danach an die Web-Oberfläche
- bleibt standardmäßig CPU-sicher; optionale Beschleunigungsmodi können später aktiviert werden, wenn der Host sie sauber trägt

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
- `wizard.py` = einmalige lokale Setup-Hilfe vor der Übergabe an die Web-Oberfläche

## Repo-Bridge-Werkzeugfläche

Die Bridge ist bewusst in kleine klare Operationen geschnitten, damit die Tool-Ebene leichter verständlich bleibt:

- `roots` = verfügbare Wurzeln anzeigen
- `tree` = Verzeichnis auflisten
- `read` = Datei lesen
- `find` = Datei- und Ordnernamen finden
- `search` = Textinhalt in Dateien suchen
- `mkdir` = Sandbox-Ordner anlegen
- `write` = Textdatei in die Sandbox schreiben
- `doit` = kleiner geführter Wrapper für `mkdir` und `write`

Mehr Details und Beispiele:

- [`docs/repo_bridge_DE.md`](docs/repo_bridge_DE.md)
- [`docs/repo_bridge.md`](docs/repo_bridge.md)

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

4. First-Run-Fluss:

- ein kleiner lokaler Setup-Wizard erscheint, wenn der Builder noch nicht eingerichtet ist
- sobald das Setup gespeichert ist, läuft der normale Builder-Start weiter
- nach dem Start geht es weiter zu `http://localhost:3000`

5. in Open WebUI zu folgendem Bereich gehen:

- `Tool Server Management`

6. dort die Basis-URL einfügen:

- `http://127.0.0.1:8099`

## First-Run-Standards

- der erste `up.sh`-Lauf stellt sicher, dass `DEFAULT_OLLAMA_MODEL` vorhanden ist
- das Standardmodell ist `qwen2.5:0.5b`
- stärkere Hardware kann später über `.env` auf größere Ollama-Modelle wechseln
- `BUILDER_ACCELERATION=cpu` hält den Stack zunächst auf einer portablen Basis; später kann in `.env` bewusst auf `auto` oder `intel` gewechselt werden, wenn man Hardware-Beschleunigung testen will
- der Wizard kann mit `python3 scripts/wizard.py --force` erneut geöffnet werden
- der GUI-Wizard ist bilingual (`de/en`) und schließt sich nach dem Speichern selbst

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
- [`docs/commands.md`](docs/commands.md)

## Erforderliche `.env`-Werte

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
- `scripts/builder_bootstrap.py`
- `scripts/wizard.py`
- `docs/quickstart_DE.md`
- `docs/commands_DE.md`
- `docs/repo_bridge_DE.md`
- `services/repo_bridge/`
- `sandbox/`

## Verwandte öffentliche Repositories

- [`tof-showcase`](https://github.com/IMaugrenI/tof-showcase) — öffentlicher Architekturrahmen
- [`tof_local_knowledge`](https://github.com/IMaugrenI/tof_local_knowledge) — on-prem lokales Wissenssystem
