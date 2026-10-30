# Native Autonomous Builder – Architektur- und Ausbauplan

Status: Architekturentwurf / Betreiberentscheidung vom 2026-10-30. Kein Laufzeit- oder Abnahmenachweis.
Branch: `development/native-autonomous-builder`
Geltungsbereich: `IMaugrenI/tof_local_builder`.

## Produktentscheidung
- Open WebUI vollständig aus dem zukünftigen Standardprodukt entfernen; keine Pflichtabhängigkeit, keine zweite Chatoberfläche.
- Eine integrierte Builder-Oberfläche für Chat, Projekt, Auftrag, Fortschritt, Review und Freigabe.
- Möglichst autonome Bedienung ohne laufende Docker-/Terminal-Administration durch Benutzer.
- Originalquelle bleibt standardmäßig read-only; erzeugte Dateien nur in den vorhandenen Sandbox-Bereichen.
- Entscheidungen mit erhöhten Rechten, fremden Daten oder erheblicher Tragweite benötigen explizite Freigabe.
- Bestehende Repository-Struktur, `python run.py` und Docker-Compose-Startweg beibehalten. Keine parallele Infrastruktur.

## Nachgewiesener Ist-Zustand (main, GitHub-Quelllektüre)
- `run.py` ruft `tof_cli.cli.main` auf; `tof_cli/commands/` stellt Setup, Up, Check, Status, Doctor, Down, UI bereit.
- `compose.yml` betreibt Ollama, Repo Bridge und Open WebUI; `compose.host_bridge.yml` hat ebenfalls Open WebUI.
- `tof_cli/ui/app.py`: Python-basierte lokale Steueroberfläche; Aktionshandler und Statusdarstellung.
- `tof_cli/builder/task_ops.py`: aufgabenbezogene Modellauswahl und Promptvorbereitung; Übergabe in Open WebUI bislang manuell, keine Ausführung.
- `tof_cli/builder/model_ops.py`: listet Ollama-Modelle, stellt Standardmodell bereit; kein eigener Chat-/Tool-Loop nachgewiesen.
- `services/repo_bridge/app/main.py`: FastAPI mit source/workspace/output; read-only Quellbereich und eingeschränkte Sandbox-Schreiboperationen.
- `tof_cli/builder/artifact_ops.py`: Inventar, Vorschau, Diff, Review-gebundener manueller Handoff; kein automatisches Zurückschreiben.
- `tof_cli/ui/guidance.py`: lesende Statushilfe, keine automatische Reparatur.
- `docs/00_product/PRODUCT_CONSTITUTION_V1.md` enthält bisher Open-WebUI- und Light/Grounded-Ziele, die vor Implementierung bewusst auf die neue Betreiberentscheidung angepasst werden müssen.
- Weitere Komponenten, Tests, Betriebseigenschaften und externe Schnittstellen sind vor Änderungen von der lokalen KI vollständig zu inventarisieren; GitHub-Quelllektüre ist keine Runtime-Abnahme.

## Zielarchitektur (logische Module, nicht notwendigerweise neue Dienste)
1. Native UI: vorhandene `tof_cli/ui/` ausbauen, Chat/Projektansicht/Taskstatus/Review integrieren.
2. Model gateway: Ollama direkt anbinden (Streaming, Timeouts, Modellrollen, kontrollierte Toolaufrufe); existierende Modellverwaltung wiederverwenden.
3. Task engine: Auftrag -> Architektur-/Kontextaufnahme -> Plan -> begrenzte Werkzeugaktionen -> Ergebnis -> Review, mit durablem Journal und sicherem Resume.
4. Workspace engine: Repo Bridge / Sandbox / Artefaktvergleich nutzen; Quellcode-Schreibgrenze niemals still aufheben.
5. Runtime manager: vorhandene Setup/Up/Check/Doctor-Kommandos orches­trieren; sichere Recovery begrenzen, irreversible Aktionen nur nach Zustimmung.
6. External adapters: optional vorhandene Schnittstellen von Knowledge/Organizer nutzen; deren Code und Zuständigkeiten nicht kopieren.

## Zusammenhängende Baupakete
### Paket A – Native Oberfläche ohne Open WebUI
- Ist-Pfade, UI-Aktionen, Startpfade, Compose-Varianten, Wizard, Umgebungsvariablen und Dokumentation vollständig kartieren.
- Direkten lokalen Ollama-Modell-/Chatpfad einschließlich Streaming und Sitzungen in vorhandene Python-Architektur integrieren.
- Bestehende Control UI zum einzigen Arbeitsbereich ausbauen, Aufgaben-/Kontext-/Reviewfunktionen erhalten.
- Open-WebUI-Referenzen und -Services in allen aktiven Start-/Prüfpfaden erst entfernen, wenn Ersatz funktionsfähig ist.
- Minimaler Nachweis: Start-/Endpoint-Prüfung, Streaming, Sandbox-Read/Write-Grenzen, keine Open-WebUI-Abhängigkeit.

### Paket B – Autonomer Entwicklungskern
- Taskstatus, Bauplan, Fortschritt, Halt/Fortsetzen und persistente Übergaben.
- Projektanalyse vor Änderungen, begrenzte Dateisuchen, kontrollierte Codegenerierung in Sandbox.
- Toolberechtigungen und Aktionsklassen: automatisch / Zustimmung / verboten.
- Review und Übernahme bleiben explizit; keine stillen Änderungen am Quellrepository.
- Gezielte Nachweise für Toolgrenzen, Zustandsübergänge, Crash-/Resume-Pfade.

### Paket C – Benutzerfreundliche Selbstverwaltung
- Ein sichtbarer Startweg, geführte Erstkonfiguration, automatische sichere Prüfung und Reparatur der *eigenen* Laufzeit.
- Fehler als verständliche Handlungsvorschläge; keine unbemerkten Installationen, Diensteingriffe in fremde Systeme oder Datenverluste.
- Bestehenden Compose-/CLI-Pfad wiederverwenden.
- Gezielte Nachweise für fehlende Modelle, gestörten Dienst und Recovery.

### Paket D – Optionale Anbindungen
- Ist-Schnittstellen und Sicherheitsgrenzen von `tof_local_knowledge` und `local_case_organizer` vor Implementierung prüfen.
- Read-only/evidence-first Knowledge-Kontext und begrenzte Organizer-Übergaben nur mit klaren Datenverträgen.
- Keine unbestätigten generierten Inhalte zu Knowledge-Wahrheiten erheben; keine implizite Freigabe/Weitergabe.

### Paket E – Meilensteinabnahme
- DEV-Code-/isolierte Tests von DOM-Runtime-Nachweisen unterscheiden.
- Bestehende Belege übernehmen, fehlende Nachweise zielgerichtet erbringen.
- P0/P1 vor abhängigem Weiterbau beheben; P2 dokumentieren.
- DOM entscheidet GO/NO-GO und Merge nach realem Zielsystemnachweis.

## Auftrag an lokale KI (erste Implementierungsübergabe)
1. Zuerst *vollständige* Architektur-/Abhängigkeitsinventur von Builder-Repository, UI, sämtlichen Compose-Modi und Tests.
2. Abgleich mit diesem Plan sowie verbindlichen ToF-Blueprints, ohne Annahmen über nicht geprüfte Schnittstellen.
3. Umsetzung Paket A in zusammenhängenden, sauber getrennten Commits direkt im vorhandenen Repository und Branch.
4. Keine neuen Repositories/konkurrierenden Startwege; vorhandene Bibliotheken und Module bevorzugen.
5. Nur notwendige gezielte Tests, Ergebnisse und verbleibende Risiken dokumentieren.
6. Keine Erstellung von DOM-Review-Bündeln durch die lokale KI; DOM führt die Runtime-Abnahme und bündelt Review-Unterlagen.

## Offene Architekturfragen, vor abhängigem Ausbau im Code zu klären
- Session-/Journal-Speicher und Schema im bestehenden Projekt.
- Oberflächen-Authentisierung und CSRF/Origin-Schutz bei lokalen mutierenden Endpoints.
- Exakter Ollama-Transport und Modellrollen; Abbruch-/Timeout-Verhalten.
- Sicherheitsgrenzen und Risiken im optionalen Host-Reader-Modus.
- Maschinenübergreifende Erstinstallation: Docker-Präsenz/Rechte, GPU/CPU, Offline-Betrieb.
- Vertragliche Schnittstellen von Knowledge/Organizer; nicht aufgrund README-Kompatibilitätsaussagen als bereits integriert behandeln.

## Freigaberegel
Dieser Plan erlaubt Architektur-/Implementierungsarbeit auf dem Entwicklungsbranch; er ist kein automatischer Auftrag zum Merge, zur Produktionseinführung oder zur Änderung des Nutzer-Quellrepositories.
