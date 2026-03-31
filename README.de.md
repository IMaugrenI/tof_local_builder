# tof_local_builder

Ein kleiner lokaler Builder-Stack für Repo-Arbeit, Audits, Drift-Prüfung und Code-Unterstützung ohne starken Cloud- oder Token-Druck.

## Ziel

`tof_local_builder` ist ein leichtes lokales Arbeitsrepo für:
- lokale Coding-Modelle mit Ollama
- eine Browser-GUI mit Open WebUI
- wiederverwendbare Prompts und Profile für Repo-Arbeit
- einen einfachen, nachvollziehbaren und gut neu aufsetzbaren Start

## Prinzipien

- lokal zuerst
- klein und verständlich
- austauschbare Bausteine
- Docker-basierter Start
- klare Konfiguration

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

## Sprachstruktur

- Englisch: `README.md`, `docs/en/`
- Deutsch: `README.de.md`, `docs/de/`

## Hinweis

Die technischen Dateien wie `compose.yml`, `.env.example`, Skripte und Profile bleiben sprachneutral.
