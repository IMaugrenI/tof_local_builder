# tof_local_builder

**Lokaler KI-Builder mit klaren Grenzen: read-only Quelle, Sandbox-Ausgabe**

Ein lokaler Bauarbeitsraum für KI-gestützte Umsetzung unter menschlicher Architekturführung.

> Die englische Hauptfassung liegt in `README.md`.

## Einfachster Einstieg

### Linux

```bash
bash scripts/start_here.sh
```

### Windows PowerShell

```powershell
pwsh ./scripts/start_here.ps1
```

### macOS

```bash
./scripts/start_here.command
```

Das führt aus:

1. setup
2. start
3. check

Ein Einsteiger-Guide liegt in `docs/00_beginner_quickstart.md`.
Ein deutscher Klon liegt in `docs/00_beginner_quickstart_DE.md`.

## Rollen im System (wichtig)

Dieses Repo hat drei unterschiedliche Ebenen:

1. **Wizard (Erstsetup)**
   - läuft beim ersten Start
   - legt Modell, Pfad und Profil fest

2. **Lokale Control-UI**
   - startet über `python run.py ui`
   - dient zur Steuerung und Übersicht

3. **Open WebUI (Arbeitsfläche)**
   - hier findet die eigentliche Arbeit statt

Die Runtime-Wahrheit bleibt:

```bash
python run.py ...
```

## Erfolgszustand

Ein erfolgreicher Start bedeutet:

- Stack läuft
- Setup ist abgeschlossen
- WebUI ist erreichbar
- Output bleibt sauber in der Sandbox

## Alltagspfad

```bash
python run.py up
python run.py status
python run.py check
python run.py down
```

## Kernidee

- Quelle bleibt read-only
- Ausgabe bleibt getrennt
- Aufbau bleibt kontrolliert

## Verwandte Repos

- tof_local_knowledge
- tof_showcase
- tof_v7_public_frame
