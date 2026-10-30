# tof_local_builder

<p align="center">
  <img src="https://raw.githubusercontent.com/IMaugrenI/IMaugrenI/main/assets/banner/tof_local_builder_banner_v4_fixed.png" alt="tof_local_builder banner" width="100%" />
</p>

**Mit lokaler KI entwickeln und Quellmaterial sowie Ergebnisse kontrolliert getrennt halten.**

Local Builder bietet einen Arbeitsbereich für KI-gestützte Implementierung mit **schreibgeschützt eingebundenen Quellen** und **separater Sandbox-Ausgabe**. Ziel sind nutzbare, überprüfbare Ergebnisse statt unkontrollierter Änderungen an bestehenden Projekten.

**Einstieg:** [Schnellstart](START_HERE_DE.md) · [English README](README.md) · [ToF Systems Übersicht](https://github.com/IMaugrenI/tof-showcase)

**Quellpaket-Kandidat (B8/K8):** Die vorhandenen Windows-/Linux-/macOS-Starter lassen sich über den manuellen GitHub-Workflow **Source distribution candidate** oder `python scripts/build_source_candidate.py --output-dir dist` aus einem Git-Commit bündeln. Enthalten sind eine [Offline-Anleitung](docs/RELEASE_PACKAGE_DE.md) und eine SHA-256-Prüfsumme. **Noch kein freigegebenes Produkt-Release und kein nativer Installer; die Abnahme erfolgt erst nach dem Ausbau.**

**Für wen:** Entwickler, Self-Hoster und kleine lokale Teams, die lokal unterstützte KI-Arbeit mit klaren Prüfgrenzen möchten. Das Repository ist das eigenständige **Generate**-Werkzeug, kein vollständiges Wissensmanagement und keine automatisch verbundene Tool-Suite.

**Ablauf:** Projekt wählen → lokale KI im Builder ansprechen → Ergebnisse prüfen. Kein Open WebUI.


## Aktueller Entwicklungsstand auf main (30.10.2026)

**Open WebUI ist nicht mehr Bestandteil der Compose-Runtime.** Die vorhandene Builder-Control-UI enthält jetzt einen direkt mit Ollama verbundenen, begrenzten Assistenten. Der KI-Dialog unterstützt weiterhin Fragen und Planung. Zusätzlich kann **„Generate sandbox draft“** auf ausdrücklichen Benutzerwunsch einen begrenzten Bauauftrag ausführen: Repository-Überblick lesen, Bauplan erstellen und höchstens sechs Textdateien unter sandbox/output erzeugen. Nach einer Unterbrechung kann der Benutzer den Auftrag ausdrücklich fortsetzen, wenn Bauplan, Projektkontext, Quell- und Entwurfsdateien noch zum gespeicherten Stand passen. Vor dem Speichern werden Python-, JSON- und TOML-Entwürfe ohne Ausführung auf Syntax geprüft. Ein erkannter Syntaxfehler führt zu höchstens einem automatischen Korrekturversuch. Für andere Dateitypen wird keine Syntaxprüfung behauptet. Originaldateien, Shell und Git bleiben unberührt. Source bleibt read-only, Ausgabe bleibt in der Sandbox. Die Zielsystem-Abnahme steht aus.

**Start:** `python run.py setup` (beim ersten Mal), `python run.py up`, `python run.py check`. `up` startet die bestehende Builder-Oberfläche lokal unter `http://127.0.0.1:8795` (konfigurierbar über `BUILDER_UI_PORT`), sofern nicht bereits gestartet.

Optional ist eine ausdrücklich bestätigte, lesende Suche in einem separat gestarteten ToF Local Knowledge möglich. Die Oberfläche zeigt höchstens fünf indizierte, **ungeprüfte** Textstellen; diese werden nicht automatisch an das Builder-LLM oder einen Bauauftrag weitergereicht. Der Case Organizer bleibt ohne freigegebenen Austauschvertrag getrennt.

Die historischen Open-WebUI-Beschreibungen unten dokumentieren frühere Ausbauschritte und sind **nicht mehr** der aktuelle Nutzungsweg. Vorhandene Open-WebUI-Daten werden bei einem Upgrade nicht automatisch gelöscht. Ein bereits laufender alter Container wird nicht automatisch gestoppt.

[Neue Produktverfassung](docs/00_product/PRODUCT_CONSTITUTION_V2.md) · [Ausbauplan](docs/WEBUI_FREE_BUILDER_EXPANSION.md)

## Historische Bauabschnitte (B1–B9; vorheriger Open-WebUI-Stand)

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

## B9 – geprüfte Ergebnisse manuell übernehmen

Die vorhandene Sandbox-Prüfung kann jetzt für zuvor als geprüft markierte **kleine Textdateien** einen vollständigen Übergabeinhalt kopieren. Bei geänderten Dateien ist das ein Unified-Diff, bei neuen Dateien der vollständige Text. Ein identischer Stand erzeugt keinen Übergabeinhalt.

Die Markierung ist an **Quell- und Ausgabestand** gebunden. Wenn die Originaldatei oder das generierte Ergebnis zwischen Prüfung und Kopieren verändert wurde, verweigert die Funktion die Übergabe und verlangt erneute Sichtung. Binäre und zu große Dateien oder abgeschnittene Diffs werden nicht automatisch übernommen.

**Sicherheitsgrenze:** Die Originalquelle bleibt weiterhin schreibgeschützt; es gibt keine automatische Dateiübernahme, kein automatisches Commit und keinen Push. Der Benutzer entscheidet in seinem Editor bewusst über die Anwendung.


## Jetzt verwenden

Die `run.py`-CLI, die vorhandenen Linux-/Windows-/macOS-Starter und das Repository-Compose-System bleiben erhalten.

```bash
python run.py setup
python run.py up
python run.py check
```

Danach arbeitet der Benutzer in der **eigenen Builder-Oberfläche**. Der Chat liest zur Orientierung höchstens einen begrenzten README-Ausschnitt und erzeugt eine Antwort. Die separate Funktion „Generate sandbox draft“ kann nach Benutzerauftrag höchstens sechs neue, prüfbare Textdateien in der Sandbox erzeugen. Die vorhandenen Sandbox-Vorschau-, Vergleichs- und Review-Funktionen bleiben für alle generierten Artefakte verfügbar.

**Betriebsgrenze:** kein automatischer Quell-Commit, kein Push, keine automatische Übernahme. Kein freigegebenes Release; auf dem Zielrechner noch nicht abgenommen.

Mehr: [Schnellstart](START_HERE_DE.md) · [Produktverfassung v2](docs/00_product/PRODUCT_CONSTITUTION_V2.md).
