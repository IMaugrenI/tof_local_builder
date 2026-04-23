# tof_local_builder

<p align="center">
  <img src="https://raw.githubusercontent.com/IMaugrenI/IMaugrenI/main/assets/banner/tof_local_builder_banner_v4_fixed.png" alt="tof_local_builder banner" width="100%" />
</p>

> Die englische Hauptfassung liegt in `README.md`.

**Lokaler KI-Builder mit klaren Grenzen: read-only Quelle, Sandbox-Ausgabe**

Ein lokaler Bauarbeitsraum für KI-gestützte Umsetzung unter menschlicher Architekturführung — mit expliziten Quellgrenzen und isolierten Ausgabepfaden.

Lokaler KI-Builder für kontrollierte Arbeit auf einer Maschine oder in einem kleinen lokalen Team.

## Was dieses Repo ist

Dieses Repository ist das öffentliche **Generate**-Repo in der Produktlinie.

## Für wen es gedacht ist

Dieses Repo ist für Builder, Self-Hoster und kleine lokale Teams, die kontrollierte KI-gestützte Umsetzung mit klaren Quellgrenzen und prüfbarer Ausgabe wollen.

## Was es nicht ist

Dieses Repo ist kein allgemeines Wissenssystem, kein versteckter Cloud-Dienst und kein verschmolzenes Super-Tool.

## Wohin du als Nächstes gehen kannst

- `tof-showcase` — öffentlicher Architektur- und Produktlinien-Überblick
- `tof_local_knowledge` — evidenzgebundene Eingaben vor der Generierung
- `local_case_organizer` — geprüfte Ausgaben nach dem Builder strukturieren

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
