# tof_local_builder

> Die englische Hauptfassung liegt in `README.md`.

Lokaler KI-Builder für kontrolliertes Arbeiten auf einem einzelnen Rechner oder in einem kleinen lokalen Team.

Dieses Repository ist ein öffentlicher Beleg für KI-gestützte Aufbauarbeit unter menschlicher Architekturführung.

Ich stelle dieses Repo nicht als klassischen Beweis für manuell Zeile für Zeile geschriebenen Code dar. Ich stelle es als Beleg dafür dar, dass aus Architektur, Grenzziehung, Orchestrierung und Review in einem KI-gestützten Workflow eine konkrete lauffähige Form entstehen kann.

## Warum dieses Repo so gebaut ist

`tof_local_builder` ist mein stärkstes öffentliches Beispiel, weil man daran direkt sieht, wie ich Struktur, Grenzen und Bauruhe in eine konkrete lauffähige Form bringe.

Die Quelle bleibt read-only, weil ich die Quelle zuerst sauber verstehen will, bevor irgendetwas verändert oder weiterverarbeitet wird.

Ergebnisse gehen in eine Sandbox, weil sie getrennt, prüfbar und ohne stille Vermischung entstehen sollen.

Die Runtime ist Python-first, weil der Ablauf klar, direkt und nachvollziehbar bleiben soll.

## Meine Rolle in diesem Repo

Meine Rolle hier ist:

- Architektur und Grenzdefinition
- Workflow-Design und Runtime-Form
- Review und Korrektur erzeugter Ausgaben
- öffentliche Rahmung und bewusste Reduktion des Scopes
- KI-gestützte Umsetzung unter meiner Führung

Die konkrete Repo-Oberfläche ist stark KI-gestützt entstanden. Mein Anteil liegt in der Struktur dahinter: warum die Quelle read-only bleibt, warum Ausgaben in einer Sandbox landen, warum der Startpfad eng gehalten wird und was als zulässiger öffentlicher Beleg gilt.

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
```

## Plattform-Wrapper

Die unterstützte Runtime-Wahrheit ist `python run.py ...`.

Unterstützte Komfortstarter:

- Linux: `scripts/setup.sh`, `scripts/up.sh`, `scripts/check.sh`, `scripts/down.sh`, `scripts/status.sh`, `scripts/doctor.sh`
- Windows PowerShell: `scripts/setup.ps1`, `scripts/up.ps1`, `scripts/check.ps1`, `scripts/down.ps1`, `scripts/status.ps1`, `scripts/doctor.ps1`
- macOS Command-Starter: `scripts/setup.command`, `scripts/up.command`, `scripts/check.command`, `scripts/down.command`, `scripts/status.command`, `scripts/doctor.command`

Beispiele:

```bash
./scripts/setup.sh
pwsh ./scripts/setup.ps1
./scripts/setup.command
```

Nach dem Start öffne `http://localhost:3000` und verbinde den Tool-Server unter `http://127.0.0.1:8099`.

## Was man schnell verstehen sollte

Dieses Repo ist kein beliebiger KI-Spielplatz. Es ist eine kontrollierte Bauschicht, an der sichtbar wird, dass auch KI-gestützte Umsetzung begrenzt, prüfbar und technisch ehrlich gehalten werden kann.

## Was dieses Repo macht

1. führt lokale Modelle über Ollama aus
2. stellt eine Browser-Oberfläche über Open WebUI bereit
3. liest einen eingebundenen Quellpfad read-only
4. schreibt geprüfte Artefakte nur in eine lokale Sandbox
5. nutzt einen First-Run-Wizard für Setup und Modellwahl
6. bleibt standardmäßig CPU-schonend, mit optionaler späterer Beschleunigung

## Was dieses Repo zeigt

1. Architektur vor Umsetzung
2. explizite Grenzen zwischen Quelle, Runtime und Ausgabe
3. KI-gestützte Aufbauarbeit unter menschlicher Führung
4. praktische Lokalsystem-Denke statt vager KI-Rhetorik
5. Dokumentations- und Runtime-Disziplin

## Grenze

1. das Quellrepo bleibt read-only
2. Schreibvorgänge bleiben auf `sandbox/workspace` und `sandbox/output` begrenzt
3. das ist ein Builder-Stack und kein allgemeines Wissenssystem
4. lokaler Einsatz steht im Vordergrund

## Zentrale Runtime-Teile

- `run.py`
- `tof_cli/`
- `compose.yml`
- `.env.example`
- `docs/13_python_cli_runtime.md`
- `services/repo_bridge/`
- `scripts/wizard.py`

## Verwandte öffentliche Repos

- [`tof_local_knowledge`](https://github.com/IMaugrenI/tof_local_knowledge) — lokale Dokumenten-Indexierung und belegte Antworten
- [`tof_showcase`](https://github.com/IMaugrenI/tof-showcase) — öffentlicher Architektur-Einstieg
- [`tof_v7_public_frame`](https://github.com/IMaugrenI/tof-v7-public-frame) — reduzierter V7-Grenzrahmen
