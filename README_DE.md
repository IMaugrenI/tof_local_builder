# tof_local_builder

> Die englischen Dateien sind die Primärtexte in diesem Repository. Ein deutscher Klon liegt in `README_DE.md`.

Kleiner lokaler Builder-Stack für Repo-Arbeit, Audits, Drift-Prüfung und Code-Unterstützung ohne starken Cloud- oder Token-Druck.

Dieses Repository ist als lokaler, nachvollziehbarer Arbeitsraum für Coding-Modelle und repo-bezogene Arbeit gedacht.

## Zweck

`tof_local_builder` ist ein leichtes lokales Arbeitsrepo für:

- lokale Coding-Modelle mit Ollama
- eine Browser-GUI mit Open WebUI
- wiederverwendbare Prompts und Profile für Repo-Arbeit
- einen kleinen, verständlichen Docker-Start

## Kernidee

Der Builder selbst ist kein selbstverbesserndes System.
Er ist zuerst ein lokaler Arbeitsraum und Werkzeugträger.

Er kann nützlicher werden durch:

- bessere Prompts
- bessere Profile
- bessere Arbeitsabläufe
- spätere Retrieval-, Memory- oder Fine-Tuning-Schichten

Das ist im aktuellen Grundstand aber nicht automatisch eingebaut.

## Enthalten

- `compose.yml` für Ollama + Open WebUI
- wiederverwendbare Prompts für Repo-Audits und Drift-Prüfung
- Starter-Profile für Ollama, Aider und Continue
- Ubuntu-Setup-Hinweise
- englische Primärdokumente plus deutsche `_DE`-Klone

## Schnellstart

```bash
cp .env.example .env
bash scripts/bootstrap.sh
bash scripts/healthcheck.sh
```

Danach öffnen:

- Open WebUI: `http://localhost:3000`
- Ollama API: `http://localhost:11434`

## Struktur

- Englische Primärtexte:
  - `README.md`
  - `docs/architecture.md`
  - `docs/setup_ubuntu.md`
  - `docs/usage.md`
  - `docs/profiles_overview.md`
  - `prompts/repo_audit.md`
  - `prompts/drift_check.md`
  - `prompts/codex_style_tasks.md`

- Deutsche Klone:
  - `README_DE.md`
  - `docs/architecture_DE.md`
  - `docs/setup_ubuntu_DE.md`
  - `docs/usage_DE.md`
  - `docs/profiles_overview_DE.md`
  - `prompts/repo_audit_DE.md`
  - `prompts/drift_check_DE.md`
  - `prompts/codex_style_tasks_DE.md`

## Profile

Der Profil-Ordner bleibt bei den eigentlichen Konfigurationsdateien sprachneutral.
Ein kurzer zweisprachiger Überblick liegt hier:

- Englisch: `docs/profiles_overview.md`
- Deutsch: `docs/profiles_overview_DE.md`

Sprachneutrale Technikdateien wie `compose.yml`, `.env.example`, Skripte und Profil-Konfigurationen bleiben gemeinsam.
