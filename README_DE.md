# tof_local_builder

<p align="center">
  <img src="https://raw.githubusercontent.com/IMaugrenI/IMaugrenI/main/assets/banner/tof_local_builder_banner_v4_fixed.png" alt="tof_local_builder banner" width="100%" />
</p>

**Mit lokaler KI entwickeln und Quellmaterial sowie Ergebnisse kontrolliert getrennt halten.**

Local Builder bietet einen Arbeitsbereich für KI-gestützte Implementierung mit **schreibgeschützt eingebundenen Quellen** und **separater Sandbox-Ausgabe**. Ziel sind nutzbare, überprüfbare Ergebnisse statt unkontrollierter Änderungen an bestehenden Projekten.

**Einstieg:** [Schnellstart](START_HERE_DE.md) · [English README](README.md) · [ToF Systems Übersicht](https://github.com/IMaugrenI/tof-showcase)

**Quellpaket-Kandidat (B8/K8):** Die vorhandenen Windows-/Linux-/macOS-Starter lassen sich über den manuellen GitHub-Workflow **Source distribution candidate** oder `python scripts/build_source_candidate.py --output-dir dist` aus einem Git-Commit bündeln. Enthalten sind eine [Offline-Anleitung](docs/RELEASE_PACKAGE_DE.md) und eine SHA-256-Prüfsumme. **Noch kein freigegebenes Produkt-Release und kein nativer Installer; die Abnahme erfolgt erst nach dem Ausbau.**

**Für wen:** Entwickler, Self-Hoster und kleine lokale Teams, die lokal unterstützte KI-Arbeit mit klaren Prüfgrenzen möchten. Das Repository ist das eigenständige **Generate**-Werkzeug, kein vollständiges Wissensmanagement und keine automatisch verbundene Tool-Suite.

**Ablauf:** lokales Modell und Arbeitsraum wählen → schreibgeschützte Quelle sichten → in Open WebUI arbeiten → Ergebnisse in der Sandbox prüfen. Setup-, Steuer- und Arbeitsoberfläche besitzen dabei getrennte Rollen, die unten erläutert werden.

## B1-Grundlage (in main integriert)

Die vorhandene Browser-Steuerung hat jetzt eine **schreibgeschützte Ergebnisübersicht** für `sandbox/workspace` und `sandbox/output`. Sie zeigt relative Dateipfade, Größen und Änderungszeiten; kleine UTF-8-Textdateien können begrenzt angesehen werden. Symlinks, Pfade außerhalb der Sandbox und überlappende Quell-/Sandbox-Wurzeln werden abgewiesen. Dateien werden nicht automatisch ins Quellprojekt übernommen, committed oder gepusht.

Der normale Befehl `up` führt nicht mehr zunächst pauschal `docker compose down --remove-orphans` aus. Die Statusanzeige berücksichtigt nun auch den Quellpfad, die Sandbox und das gewählte Modell neben den lokalen Dienstendpunkten.

Diese Änderungen befinden sich im [B1-Entwicklungs-PR](https://github.com/IMaugrenI/tof_local_builder/pull/34). Grüne GitHub-CI-Prüfungen sind nur Codetests, keine Aussage über einen geprüften Zielrechner.

## Ausbau B2: Änderungen vor der Übernahme vergleichen

Die bestehende lokale Steueroberfläche bietet neben der Sandbox-Dateiübersicht nun **„Compare to source“**. Dabei werden ausschließlich kleine UTF-8-Textdateien aus `sandbox/workspace` oder `sandbox/output` mit einer Datei **unter demselben relativen Pfad** im gewählten, schreibgeschützten Quellprojekt verglichen. Angezeigt werden hinzugefügte und entfernte Zeilen sowie die Zustände „neu“, „identisch“, „geändert“ oder „Quelle zu groß/nicht verfügbar“.

Die Vorschau ist begrenzt und ausschließlich lesend; es gibt **keine automatische Übernahme, keinen Commit und keinen Push** in das Quellprojekt. Bei großen, binären oder über Pfadgrenzen hinausführenden Dateien verweigert das System den Vergleich.

## Ausbau B3 — Geführte Aufgabenwahl

Die bestehende lokale Browser-Steuerung bietet nun eine **Aufgaben- und Modellwahl**. Aufgabenprofile stammen aus dem vorhandenen `model_catalog/builder_catalog.json`. Als ausführbare Auswahl werden ausschließlich lokal bei Ollama erkannte Modelle angezeigt; geeignete Profile werden kenntlich gemacht.

Aus einer kurzen Aufgabenbeschreibung wird eine **kopierbare Arbeitsanweisung** erstellt. Die eigentliche Arbeit findet weiterhin in Open WebUI statt und das Modell wird dort bewusst gewählt. Die Aufgabenwahl lädt keine Modelle herunter, startet keine Aufträge automatisch und schreibt nicht in das Quellprojekt. Voraussetzung sind die bestehenden, getrennten Quell-/Sandbox-Pfade.

## Ausbau B4 — Aufgabenübergabe mit einem Klick

Die vorhandene Aufgabenoberfläche bietet **„Copy & open workspace“**. Damit wird eine bereits vorbereitete Arbeitsanweisung kopiert und die konfigurierte lokale Open WebUI geöffnet — ausschließlich, wenn das Kopieren erfolgreich war. Modellwahl und Auftragsstart erfolgen weiterhin bewusst in Open WebUI. Es gibt keine automatische Ausführung und keine Rückschreibungen in das Quellprojekt.

Die Links zu Open WebUI, Projekt-Bridge und Ollama berücksichtigen jetzt die vorhandenen `.env`-Ports statt fest vorgegebener Adressen. Ungültige Portwerte werden nicht stillschweigend umgedeutet.

## Ausbau B5 — Erzeugte Dateien nachvollziehbar sichten

In der vorhandenen Sandbox-Ansicht gibt es jetzt einen **Prüfstatus je Textdatei**, eine Filterung offener Prüfungen und einen Fortschrittszähler. Eine Datei kann erst nach erfolgreicher Vorschau oder vollständigem Vergleich als geprüft markiert werden. Diese Markierung wird ausschließlich im lokalen Browser gespeichert und an den konkreten Dateiinhalt sowie die gewählten Quell-/Sandbox-Pfade gebunden. Ändert sich der Inhalt, gilt die frühere Markierung nicht mehr. Große oder binäre Dateien können nicht über die begrenzte Textansicht abgehakt werden.

Die Markierung ist eine **Sichtungshilfe, keine Freigabe zur automatischen Übernahme**. Dateien des Originalprojekts werden nicht verändert, committed oder gepusht.

## Ausbau B6 — Passendere KI-Modelle und Projektüberblick

Die vorhandene Aufgabenoberfläche schlägt für den gewählten Aufgabentyp jetzt **bevorzugt ein bereits installiertes, im bestehenden Modellkatalog passendes Modell** vor. Die Auswahl kann weiterhin manuell geändert werden; es gibt keine automatische Modellinstallation oder Änderung der Ollama-Konfiguration.

Daneben zeigt die Oberfläche eine **schreibgeschützte Projektübersicht**: den gewählten Quellordner, die Sandbox, ihre Zustände und höchstens 24 sichtbare Einträge der ersten Verzeichnisebene. Es erfolgt kein rekursives Einlesen von Projektdateien und kein Zugriff auf versteckte Einträge in dieser Übersicht. Bestehende Repository- und Compose-Strukturen bleiben unverändert.

## B7 – Verständliche Status- und Fehlerführung

Die bestehende Steueroberfläche ordnet fehlende Voraussetzungen jetzt nach Priorität: Quellprojekt, getrennte Sandbox, Ollama, gewähltes Modell, Projekt-Bridge und Open WebUI. Sie erläutert konkrete nächste Schritte und bietet einen bewusst auszulösenden passenden vorhandenen Befehl (`setup`, `up` oder `doctor`). Bestehende Statusfelder, Arbeitsabläufe und Quellenrechte bleiben erhalten. Es werden keine Reparaturen automatisch ausgeführt.

## Was dieses Repo macht

1. führt lokale Modelle über Ollama aus
2. stellt eine Browser-GUI über Open WebUI bereit
3. liest einen gemounteten Quellpfad read-only
4. schreibt geprüfte Artefakte nur in eine lokale Sandbox
5. nutzt einen First-Run-Wizard für Setup und Modellwahl
6. bleibt standardmäßig CPU-sicher, mit optionaler späterer Beschleunigung

## Einfachster Einstieg

Wenn du den kürzesten sicheren Weg willst, starte hier:

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
2. startup
3. health check

Ein Einsteiger-Guide liegt in `docs/00_beginner_quickstart.md`.
Ein deutscher Spiegel liegt in `docs/00_beginner_quickstart_DE.md`.

## Rollenmodell: was sich öffnet, was steuert, wo du wirklich arbeitest

Dieses Repo hat drei unterschiedliche browserseitige Ebenen, und sie sollten nicht verwechselt werden:

1. **First-run Wizard**
   - läuft beim ersten Setup, solange die Konfiguration noch unvollständig ist
   - hilft bei Task-Typ, Performance-Profil, Standardmodell und Quellpfad
   - schreibt das lokale Setup einmal und übergibt dann

2. **Lokale Control-UI**
   - startet über `python run.py ui`
   - dient als lokale Steueroberfläche
   - hilft dir, die Hauptseiten zu erreichen und den Stack zu kontrollieren

3. **Open WebUI**
   - ist die eigentliche Arbeitsfläche nach dem Start
   - hier findet normale Builder-Arbeit tatsächlich statt

Die Runtime-Wahrheit bleibt:

```bash
python run.py ...
```

Die Wrapper bleiben dünne Komfortstarter um denselben Befehlsweg.

## Warum dieses Repo so geformt ist

`tof_local_builder` ist mein stärkstes öffentliches Beispiel, weil es zeigt, wie ich Struktur, Grenzen und Build-Disziplin in eine konkrete lauffähige Form überführe.

Die Quelle bleibt read-only, weil ich will, dass die Quelle sauber verstanden wird, bevor etwas verändert oder weiterverarbeitet wird.

Die Ausgabe geht in eine Sandbox, weil Ergebnisse getrennt, prüfbar und frei von stiller Vermischung bleiben sollen.

Die Runtime ist Python-first, weil der Ablauf klar, direkt und verständlich bleiben soll.

## Meine Rolle in diesem Repo

Meine Rolle hier ist:

- Architektur und Grenzdefinition
- Workflow-Design und Runtime-Form
- Review und Korrektur erzeugter Ausgaben
- öffentliches Framing und Scope-Reduktion
- KI-gestützte Umsetzung unter meiner Führung

## Einstieg

Primärer Runtime-Einstieg:

```bash
python run.py setup
python run.py up
python run.py check
```

Weitere Runtime-Befehle:

```bash
python run.py status
python run.py doctor
python run.py down
python run.py ui
```

## Plattform-Wrapper

Die unterstützte Runtime-Wahrheit ist `python run.py ...`.

Unterstützte Komfortstarter:

- Linux: `scripts/setup.sh`, `scripts/up.sh`, `scripts/check.sh`, `scripts/down.sh`, `scripts/status.sh`, `scripts/doctor.sh`, `scripts/start_here.sh`
- Windows PowerShell: `scripts/setup.ps1`, `scripts/up.ps1`, `scripts/check.ps1`, `scripts/down.ps1`, `scripts/status.ps1`, `scripts/doctor.ps1`, `scripts/start_here.ps1`
- macOS-Command-Starter: `scripts/setup.command`, `scripts/up.command`, `scripts/check.command`, `scripts/down.command`, `scripts/status.command`, `scripts/doctor.command`, `scripts/start_here.command`

Beispiele:

```bash
./scripts/start_here.sh
pwsh ./scripts/start_here.ps1
./scripts/start_here.command
```

## Erfolgszustand

Ein erfolgreicher erster Start bedeutet:

- der lokale Builder-Stack läuft
- das First-Run-Setup wurde bereits geschrieben
- die browserseitige WebUI öffnet sich korrekt
- der Tool-Server ist erreichbar
- Ausgabe bleibt innerhalb der Sandbox-Pfade

## Normaler Alltagspfad

Nach dem ersten Setup ist der normale tägliche Pfad:

1. den Stack starten
2. bei Bedarf die lokale Control-UI öffnen oder prüfen
3. in Open WebUI als eigentlicher Arbeitsfläche weiterarbeiten
4. `status` oder `check` für Bestätigung nutzen
5. den Stack mit `down` stoppen

Tägliche Befehle:

```bash
python run.py up
python run.py status
python run.py check
python run.py down
```

## Rolle in der öffentlichen Produktlinie

Erzeugen (kontrollierte Erstellung)

### Funktioniert allein
Ja.

### Kann kombiniert werden mit
- `tof_local_knowledge` für evidenzgebundene Eingaben
- `local_case_organizer` für die Strukturierung geprüfter Ausgaben

### Nicht gedacht für
- generierte Ergebnisse als Wahrheit in Knowledge zurückzuschreiben
- als verschmolzenes Super-Tool mit den anderen Produkten zu enden

## Was dieses Repo zeigt

1. Architektur vor Umsetzung
2. explizite Grenzen zwischen Quelle, Runtime und Ausgabe
3. KI-gestützte Build-Arbeit unter menschlicher Führung
4. praktische lokale Systemdenke statt vager KI-Rhetorik
5. Dokumentations- und Runtime-Disziplin

## Grenze

1. das Quell-Repo bleibt read-only
2. Schreibvorgänge bleiben auf `sandbox/workspace` und `sandbox/output` begrenzt
3. das ist ein Builder-Stack, kein allgemeines Wissenssystem
4. lokale Nutzung kommt zuerst

## Zentrale Runtime-Teile

- `run.py`
- `tof_cli/`
- `compose.yml`
- `.env.example`
- `docs/13_python_cli_runtime.md`
- `services/repo_bridge/`
- `scripts/wizard.py`

## Verwandte öffentliche Repos

- [`tof_local_knowledge`](https://github.com/IMaugrenI/tof_local_knowledge) — lokales Wissenssystem mit Evidenzsuche und grounded Answers
- [`tof-showcase`](https://github.com/IMaugrenI/tof-showcase) — öffentlicher Architektur-Einstieg
- [`tof-v7-public-frame`](https://github.com/IMaugrenI/tof-v7-public-frame) — reduzierter V7-Grenzrahmen
