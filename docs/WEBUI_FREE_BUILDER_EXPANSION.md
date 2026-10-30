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
| Laufzeit | `compose.yml`: Ollama und Repo Bridge, ohne Open WebUI | Vorhandenen Compose-Startweg beibehalten |
| Steuerung | `tof_cli/ui/app.py`, Port 8795 | Bestehende Oberfläche erweitern |
| LLM | `model_ops.py` und direkter begrenzter `ollama_chat.py`-Adapter | Sichere Modellsteuerung erweitern |
| Quellzugriff | `services/repo_bridge/app/main.py`: source read-only | Grenzen beibehalten |
| Sandbox/Review | `tof_cli/builder/artifact_ops.py` | Weiterverwenden |
| Aufgaben | Native Chat- und Sandbox-Bauaufträge mit `agent_ops.py` und Journal | Umfangreiche Entwicklungswerkzeuge kontrolliert ausbauen |
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
- DOM hat den direkten Ausbau auf `main` ausdrücklich genehmigt. Diese Entwicklungscommits sind **keine Release-Freigabe**; die Zielsystem-Abnahme und GO/NO-GO bleiben erforderlich.
- Keine automatischen Repository-Commits, Pushes oder Quelländerungen durch generierte Modellantworten.
- Bei Konflikten zur älteren Produktdokumentation gilt diese explizite neue Betreiberentscheidung; betroffene Dokumente werden bei der Umstellung konsistent aktualisiert.

## Aktueller Ausbaustatus

- [x] Architektur-Einstiegspunkte gelesen und WebUI-Kopplungen identifiziert.
- [x] Entwicklungsbranch erstellt.
- [x] P1 Direkter, begrenzter Ollama-Modelladapter und gezielte Tests im Repository (noch nicht runtime-geprüft).
- [x] P2 Erste integrierte KI-Aufgabenoberfläche und lokaler API-Endpunkt (read-only, noch keine Toolausführung).
- [x] P3 Open-WebUI-Service aus Compose/Startpfad entfernt; eigene UI wird über bestehende CLI gestartet.
- [x] P4 (Teilpaket): Architekturübersicht, streng begrenzte JSON-Baupläne und höchstens 3 nicht-überschreibende Sandbox-Textentwürfe über die vorhandene Repo Bridge.
- [x] P4 (Teilpaket): Aufgabenjournal, Fortschritt, Verlauf, Benutzerabbruch und sichere Unterbrechungsanzeige (keine automatische Wiederholung nach Neustart).
- [x] P4 (Teilpaket): Explizite Wiederaufnahme nach Unterbrechung mit Prüfung des gespeicherten Bauplans, Projektkontexts, der Quell-Fingerabdrücke und bereits erzeugter Entwürfe.
- [ ] P4 offen: verbesserte Entwicklungstools, sichere isolierte Testausführung und umfassendere Entwicklungsautonomie.
- [x] P5 (Teilpaket): Eigene Builder-Oberfläche wird bereits vor Docker-/Modellprüfung geöffnet, damit Fehler über die Oberfläche sichtbar bleiben.
- [x] Ressourcenbegrenzung: höchstens ein aktiver Bauauftrag und kein paralleler Chat während einer Bauausführung.
- [ ] P5–P6 offen: weitergehende sichere Selbstreparatur, optionale Knowledge-/Organizer-Schnittstellen.
- [x] Gezielte Testdateien für Agent-Pfade, Journal, Abbruch, WebUI-freie Oberfläche und Repo-Bridge-Schreibschutz hinzugefügt.
- [ ] GitHub-CI für den letzten Stand auswerten; DEV-/Runtime-Nachweise getrennt halten.
- [ ] Zielsystem-Test / GO-NO-GO.

## Begrenzte autonome Bauausführung (aktuelle Schnittstelle)

- **Start:** `POST /api/build` mit Task, installiertem Modell und Benutzerziel; ausdrücklich ausgelöste Aktion in der bestehenden Builder-Oberfläche.
- **Fortschritt:** `GET /api/build?id=<id>` und `GET /api/builds`.
- **Abbruch:** `POST /api/build/cancel`; laufende Modellantworten können nicht hart unterbrochen werden, vor dem nächsten Dateischritt wird der Abbruch berücksichtigt.
- **Ablauf:** Read-only Repo-Bridge-Überblick → validierter JSON-Bauplan → höchstens drei vollständige Textdateientwürfe → ausschließliche nicht-überschreibende Repo-Bridge-Schreibvorgänge in `sandbox/output`.
- **Journal:** `sandbox/workspace/.builder_runs/` enthält projektgebundene Status-Metadaten. Diese werden nicht als erzeugte Quellartefakte inventarisiert.
- **Nach Neustart:** unterbrochener Auftrag wird angezeigt; `POST /api/build/resume` beziehungsweise „Continue safely“ ist nur nach ausdrücklicher Benutzeraktion möglich. Vorher werden gespeicherte Baupläne, Quell- und Ausgabe-Fingerabdrücke sowie der aktuelle Repo-Bridge-Projektbezug kontrolliert. Bereits gültige Entwürfe werden übersprungen; ein vorhandener nicht erfasster Entwurf blockiert den Auftrag (kein Überschreiben). Für Altaufträge mit erzeugten Dateien, aber ohne gespeicherten Bauplan, ist keine automatische Wiederaufnahme erlaubt.
- **Freigabe:** Vor einer manuellen Übernahme in das Originalprojekt gelten unverändert Vorschau, Vergleich und Review.

Die automatische Ausführung von Shell-Befehlen, Build-Skripten, Tests, Git-Operationen und die Änderung der Quelle sind weiterhin **nicht Bestandteil** dieser Ausbaustufe.
