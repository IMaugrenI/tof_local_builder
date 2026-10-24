# Hier starten

Das ist der kürzeste unterstützte Einstieg für neue Nutzer.

> English version: [START_HERE.md](START_HERE.md)

## Was du startest

`tof_local_builder` ist ein lokaler KI-gestützter Arbeitsraum für kontrollierte Umsetzung. Der normale Weg gibt dir:

- einen First-Run-Wizard
- lokale Modelle über Ollama
- Open WebUI als Hauptarbeitsfläche im Browser
- ein ausgewähltes Quell-Repository, das read-only eingebunden wird
- schreibbare Ausgabe nur innerhalb der Builder-Sandbox

Der normale Start schreibt **nicht** in dein ausgewähltes Quell-Repository zurück.

## Voraussetzungen

Vor dem ersten Start brauchst du:

- Python 3.11+ (unter Windows über `py` oder `python` erreichbar)
- Docker mit Docker Compose
- genügend lokalen Speicherplatz für das gewählte Ollama-Modell

Linux ist die primär unterstützte Plattform. Für Windows und macOS gibt es Launcher, Linux bleibt aber der tiefste unterstützte Pfad.

## Erster Start

### Linux

```bash
git clone https://github.com/IMaugrenI/tof_local_builder.git
cd tof_local_builder
bash scripts/start_here.sh
```

### Windows PowerShell

```powershell
git clone https://github.com/IMaugrenI/tof_local_builder.git
cd tof_local_builder
pwsh ./scripts/start_here.ps1
```

### macOS

```bash
git clone https://github.com/IMaugrenI/tof_local_builder.git
cd tof_local_builder
./scripts/start_here.command
```

Der Start-hier-Pfad führt Setup aus, öffnet bei unvollständiger Konfiguration den First-Run-Wizard, startet den Stack, öffnet bei `BUILDER_OPEN_BROWSER=1` Open WebUI und führt anschließend den Health-Check aus.

## Was sich öffnet

Es gibt drei Oberflächen:

1. **First-Run-Wizard** — Konfiguration beim ersten Setup.
2. **Lokale Control-UI** — optionale Steuer- und Diagnoseoberfläche.
3. **Open WebUI** — die eigentliche Arbeitsfläche.

Wenn du das Produkt nur benutzen willst, ist nach dem Setup vor allem Open WebUI relevant.

## Woran du erkennst, dass alles läuft

```bash
python run.py check
```

Ein guter Erststart bedeutet:

- Docker-Dienste laufen
- Open WebUI ist erreichbar
- Repo Bridge ist erreichbar
- das gewählte lokale Modell ist verfügbar
- Quell- und Sandbox-Pfade sind gesetzt

## Befehle im Alltag

```bash
python run.py up
python run.py status
python run.py check
python run.py ui
python run.py down
```

Bei Problemen:

```bash
python run.py doctor
```

## Wohin Dateien geschrieben werden

- **Quelle:** von dir gewählt und im normalen Modus read-only eingebunden.
- **Workspace:** `sandbox/workspace/`
- **Output:** `sandbox/output/`

Erzeugte Arbeit bleibt in der Sandbox, bis du sie selbst prüfst und weitergibst.

## Optionaler Host-Reader für Fortgeschrittene

Für vertrauenswürdige lokale Nutzung gibt es zusätzlich:

```bash
bash scripts/start_host_repo_bridge.sh
```

Dieser Modus kann absolute lokale Pfade lesen, auf die dein Host-Benutzer Zugriff hat. Er ist bewusst mächtiger als der normale Source-Root-Modus.

Lies vorher [STANDARD_START_HOST_READER.md](STANDARD_START_HOST_READER.md). Nicht ins LAN oder Internet exponieren.

## Stoppen

```bash
python run.py down
```

## Mehr Details

- [Einsteiger-Quickstart](docs/00_beginner_quickstart_DE.md)
- [Befehle](docs/commands_DE.md)
- [Repo Bridge](docs/repo_bridge.md)
- [Product Constitution](docs/00_product/PRODUCT_CONSTITUTION_V1.md)
