# tof_local_builder

> English is the primary text in this repository. A German clone is available in `README_DE.md`.

Kleiner lokaler Builder-Stack für Repo-Arbeit, Drift-Prüfung und Code-Unterstützung ohne starken Cloud- oder Token-Druck.

Dieses Repository ist für lokale, nachvollziehbare Arbeit mit Coding-Modellen gedacht.

## Zweck

`tof_local_builder` ist ein leichtes lokales Arbeitsrepo für:

- lokale Coding-Modelle mit Ollama
- eine Browser-GUI mit Open WebUI
- wiederverwendbare Prompts und Profile für Repo-Arbeit
- einen einfachen, gut neu aufsetzbaren Start

## Kernidee

Der Builder selbst ist kein magischer Selbstverbesserer.
Er ist zunächst ein lokaler Arbeitsraum und Werkzeugträger.

Er kann besser werden durch:

- bessere Prompts
- bessere Profile
- bessere Arbeitsabläufe
- optional spätere Retrieval-, Memory- oder Fine-Tuning-Schichten

Aber das ist nicht automatisch eingebaut.

## Enthalten

- `compose.yml` für Ollama + Open WebUI
- wiederverwendbare Prompts für Repo-Audits und Drift-Prüfung
- Starter-Profile für Ollama, Aider und Continue
- Setup-Hinweise für Ubuntu

## Schnellstart

```bash
cp .env.example .env
bash scripts/bootstrap.sh
bash scripts/healthcheck.sh
```

Danach öffnen:
- Open WebUI: `http://localhost:3000`
- Ollama API: `http://localhost:11434`
