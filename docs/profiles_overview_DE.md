# Profil-Überblick

> Der englische Primärtext ist `profiles_overview.md`. Diese Datei ist der deutsche Klon.

Der Profil-Ordner enthält werkzeugspezifische Beispielkonfigurationen für die Arbeit mit lokalen Modellen.
Die eigentlichen Konfigurationsdateien bleiben sprachneutral.

## Enthaltene Profile

### `profiles/ollama/`
Kurze Modellhinweise und Starter-Empfehlungen für lokale Ollama-Nutzung.

### `profiles/aider/`
Beispielkonfiguration für repo-fokussierte Terminal-Arbeit mit einem lokalen Coding-Modell.

### `profiles/continue/`
Beispielkonfiguration für editorbasierte Nutzung lokaler Modelle.

## Warum es keine `_DE`-Duplikate für Konfigurationsdateien gibt

Konfigurationsdateien sind in erster Linie technisch und sollten gemeinsam bleiben, damit kein Drift zwischen zwei Versionen entsteht.
Stattdessen ist die Erklärungsschicht zweisprachig, während die ausführbare Konfiguration Single-Source bleibt.
