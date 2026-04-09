# tof_local_builder

> Die englische Hauptfassung liegt in `README.md`.

Lokaler KI_Builder fuer kontrolliertes Arbeiten auf einem einzelnen Rechner oder in einem kleinen lokalen Team.

Ich habe dieses Repo gebaut, damit Quellzugriff read_only bleibt, Ausgaben sauber in einer Sandbox landen und der Einstieg moeglichst einfach ist.

## start_here

Primaerer Runtime_Einstieg:

```bash
python run.py setup
python run.py up
python run.py check
```

Weitere Runtime_Befehle:

```bash
python run.py status
python run.py doctor
python run.py down
```

## plattform_wrapper

Die unterstuetzte Runtime_Wahrheit ist `python run.py ...`.

Komfortstarter existieren jetzt fuer mehrere Betriebssysteme:

- Linux: `scripts/*.sh`
- Windows PowerShell: `scripts/*.ps1`
- macOS Command_Starter: `scripts/*.command`

Beispiele:

```bash
./scripts/setup.sh
pwsh ./scripts/setup.ps1
./scripts/setup.command
```

Nach dem Start oeffne `http://localhost:3000` und verbinde den Tool_Server unter `http://127.0.0.1:8099`.

## was_dieses_repo_macht

1. es fuehrt lokale Modelle ueber Ollama aus
2. es stellt eine Browser_GUI ueber Open WebUI bereit
3. es liest einen eingebundenen Quellpfad read_only
4. es schreibt gepruefte Artefakte nur in eine lokale Sandbox
5. es nutzt einen first_run Wizard fuer Setup und Modellwahl
6. es bleibt standardmaessig CPU_schonend, mit optionaler spaeterer Beschleunigung

## grenze

1. das Quellrepo bleibt read_only
2. Schreibvorgaenge bleiben auf `sandbox/workspace` und `sandbox/output` begrenzt
3. das ist ein Builder_Stack und kein allgemeines Wissenssystem
4. lokaler Einsatz steht im Vordergrund

## zentrale_runtime_teile

- `run.py`
- `tof_cli/`
- `compose.yml`
- `.env.example`
- `docs/13_python_cli_runtime.md`
- `services/repo_bridge/`
- `scripts/wizard.py`

## wrapper_saetze

- Linux Shell_Wrapper: `scripts/*.sh`
- Windows PowerShell_Wrapper: `scripts/*.ps1`
- macOS Command_Starter: `scripts/*.command`

## verwandte_oeffentliche_repos

- [`tof_local_knowledge`](https://github.com/IMaugrenI/tof_local_knowledge) — lokale Dokumenten_Indexierung und belegte Antworten
- [`tof_showcase`](https://github.com/IMaugrenI/tof-showcase) — oeffentlicher Architektur_Einstieg
- [`tof_v7_public_frame`](https://github.com/IMaugrenI/tof-v7-public-frame) — reduzierter V7_Grenzrahmen
