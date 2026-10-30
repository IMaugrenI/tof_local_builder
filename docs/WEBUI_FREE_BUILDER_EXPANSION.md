# ToF Local Builder — WebUI-freier Ausbauplan

Status: **in Entwicklung auf `main`** (DOM-Entscheidung vom 30.10.2026). Dies ist eine Zielarchitektur, kein Runtime-Abnahmenachweis.

## Betreiberentscheidung (DOM)

- Keine Open-WebUI-Abhängigkeit in der Zielversion.
- Die vorhandene Builder-Control-UI wird zur einzigen sichtbaren Arbeitsoberfläche.
- Lokale Modelle bleiben über Ollama angebunden.
- Möglichst eigenständiges Setup, Runtime-Verwaltung, Aufgabenbearbeitung und sichere Wiederaufnahme; Alltagsbenutzer sollen keine Admin-Arbeit erledigen müssen.
- Das Original-Repository bleibt ohne ausdrückliche neue Freigabe **read-only**. Generierte Dateien bleiben in der Sandbox.
- Keine parallele Repository-, Start- oder Containerstruktur. Bestehende Python-CLI und Compose-Wahrheit bleiben erhalten.

## Nachgewiesener Ist-Zustand (Quellcode `main`)

| Bereich | Bestehend | Konsequenz |
| --- | --- | --- |
| Start | `run.py` → `tof_cli/cli.py` → Python-Commands | Wiederverwenden |
| Laufzeit | `compose.yml`: ollama, repo-bridge, open-webui | WebUI später aus Compose entfernen |
| Steuerung | `tof_cli/ui/app.py`, Port 8795 | Bestehende Oberfläche erweitern |
| LLM | `tof_cli/builder/model_ops.py` (Ollama Tags/Modell-Pull) | Sichere Ollama Chat API ergänzen |
| Quellzugriff | `services/repo_bridge/app/main.py`: source read-only | Grenzen beibehalten |
| Sandbox/Review | `tof_cli/builder/artifact_ops.py` | Weiterverwenden |
| Aufgaben | `tof_cli/builder/task_ops.py`: Prompt/Handoff zu Open WebUI | Durch direkte Auftragsausführung ersetzen |
| Setup | `scripts/wizard.py`, `tof_cli/commands/setup.py` | Eine vorhandene Wizard-Wahrheit behalten |

## Baupakete und Abhängigkeiten

### P1 — Eigene Modellkommunikation (Grundlage)

- Direkter Ollama Chat-Adapter in `tof_cli/builder/`, ohne externes Framework.
- Modellname wird aus installierten lokalen Modellen validiert; Längen- und Timeoutgrenzen.
- Keine Toolausführung oder Schreibrechte durch bloße Modellantworten.
- Gezielte isolierte Tests für Eingabevalidierung und Fehlerpfade.

### P2 — Eine Builder-Arbeitsoberfläche

- Chat/Entwicklungsauftrag im bestehenden `tof_cli/ui/app.py`; kein zweiter Webserver.
- Eigener lokaler API-Endpunkt für Modellsitzungen, später Streaming.
- Sichtbare Auftragshistorie, Status und Fehler in verständlicher Sprache.
- `task_ops.py` auf interne Übergabe statt Copy-to-WebUI umstellen.
- CSRF-/Origin-/Bind-Schutz für lokale steuernde Endpunkte überprüfen; keine öffentliche Netzfreigabe.

### P3 — WebUI aus der Runtime entfernen

- `compose.yml`: Open WebUI entfällt, Ollama und Repo Bridge bleiben.
- `up`, `check`, `doctor`, `ui`, Wizard und Modellwahl vollständig auf eigene Oberfläche umstellen.
- `.env.example`, Browserlinks und plattformspezifische Startwrapper bereinigen.
- Existierende Daten von Open WebUI nicht automatisch löschen; Migrationshinweise geben.
- Kein zusätzlicher Compose-Startweg.

### P4 — Autonomer Entwicklungsauftrag

- Architektur- und Pfadprüfung vor jeder Aktion.
- Nachvollziehbarer Aufgabenplan: Status, Teilschritte, Ergebnisse, Unterbrechungen.
- Erlaubte Toolaufrufe explizit kontrollieren; Repo Bridge nur im bisherigen Rechtebereich.
- Sandbox-Artefakte + bestehende Vergleiche/Review als verbindliche Übergabe.
- Zeit-/Ressourcenlimits und Abbruch; vor riskanten Schritten Operatorfreigabe.
- Wiederaufnahme idempotent gestalten, keine unbemerkten doppelten Schreibaktionen.

### P5 — Nutzerfreundliche Selbstverwaltung

- Hardware/Ports/Modelle/Runtime durch vorhandene CLI-Mechanismen prüfen.
- Sichere Routine-Reparaturen automatisieren; Installationen oder erhöhte Rechte nur mit Einwilligung.
- Oberfläche zeigt Fortschritt und nächste sinnvolle Handlung statt Terminalpflicht.
- Keine ungefragten Docker-Neustarts, wenn laufende Arbeit gefährdet wäre.

### P6 — Externe Wissens-/Orga-Anbindung

- Schnittstellen von `tof_local_knowledge` und `local_case_organizer` separat im Ist-Zustand prüfen.
- Kein gegenseitiger Schreibzugriff als implizite Voraussetzung; Dokumente aus Knowledge sind Kontext, keine Anweisungsautorität.
- Integration optional, ohne Produkte zusammenzukopieren oder eine zweite Runtime zu schaffen.

## Qualitäts- und Freigaberegeln

- Während des Ausbaus nur gezielte notwendige Tests; P0/P1 vor abhängigen Arbeiten beheben.
- DEV-Prüfungen und Zielsystem-Abnahme ausdrücklich trennen.
- Kein Merge nach `main` vor Betreiberentscheidung und Runtime-Nachweis.
- Keine automatischen Repository-Commits, Pushes oder Quelländerungen durch generierte Modellantworten.
- Bei Konflikten zur älteren Produktdokumentation gilt diese explizite neue Betreiberentscheidung; betroffene Dokumente werden bei der Umstellung konsistent aktualisiert.

## Aktueller Ausbaustatus

- [x] Architektur-Einstiegspunkte gelesen und WebUI-Kopplungen identifiziert.
- [x] Entwicklungsbranch erstellt.
- [x] P1 Direkter, begrenzter Ollama-Modelladapter und gezielte Tests im Repository (noch nicht runtime-geprüft).
- [x] P2 Erste integrierte KI-Aufgabenoberfläche und lokaler API-Endpunkt (read-only, noch keine Toolausführung).
- [x] P3 Open-WebUI-Service aus Compose/Startpfad entfernt; eigene UI wird über bestehende CLI gestartet.
- [ ] P4–P6 Autonome Toolausführung, Wiederaufnahme, Selbstverwaltung und Integrationen.
- [ ] Tests auf GitHub und DEV-Runtime nachziehen, bevor Aussagen zur Betriebsbereitschaft erfolgen.
- [ ] Zielsystem-Test / GO-NO-GO.
