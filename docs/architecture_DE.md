# Architektur

> Der englische Primärtext ist `architecture.md`. Diese Datei ist der deutsche Klon.

## Zweck

`tof_local_builder` ist ein kleiner lokaler Stack für codefokussierte Arbeit ohne starke Abhängigkeit von Cloud-Tokenbudgets.

## Grundbausteine

### 1. Ollama
Startet lokale Modelle und stellt eine API auf Port `11434` bereit.

### 2. Open WebUI
Stellt eine Browser-GUI bereit und spricht mit der lokalen Ollama-Instanz.

### 3. Prompt-Bibliothek
Enthält wiederverwendbare Arbeitsmuster wie Repo-Audits, Drift-Prüfung und Umsetzungsaufgaben.

### 4. Editor-Profile
Starter-Konfiguration für Tools, die mit lokalen Modellen arbeiten können.

## Fluss

```text
Nutzer
  -> Open WebUI / Aider / Continue
  -> Ollama
  -> lokales Modell
  -> Antwort / Patch / Audit-Ausgabe
```

## Warum diese Form

- leicht auf einem Rechner startbar
- leicht nachvollziehbar
- leicht austauschbar
- wenige bewegliche Teile

## Spätere Erweiterung

Mögliche nächste Schichten:

- lokale Embeddings + RAG
- Repo-Watcher
- Patch-/Review-Worker
- lokaler Dokumenten-Ingest
- optionaler GPU-Host-Split
