# Architektur

`tof_local_builder` ist ein kleiner lokaler Stack für codefokussierte Arbeit ohne starke Abhängigkeit von Cloud-Tokenbudgets.

## Grundbausteine

### 1. Ollama
Startet lokale Modelle und stellt eine API auf Port `11434` bereit.

### 2. Open WebUI
Stellt eine Browser-Oberfläche bereit und spricht mit der lokalen Ollama-Instanz.

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

## Sprachregel

Englische Dateien sind Primärtexte.
Deutsche `_DE`-Dateien sind direkte Text-Klone.
