# Web-GUiX-Freeze v0.2

## Scope

Dieser Freeze deckt nur den gestuften Web-GUiX-Setup- und Handoff-Pfad ab:

- frischer Clone des Repositories
- `bash scripts/up_guix.sh`
- Setup-Seite auf `http://127.0.0.1:3011`
- host-aware Setup-Erkennung über Host-Snapshot
- Speichern von Quellpfad, Modell und Beschleunigung
- Runtime-Handoff zu `open-webui`
- grünes `bash scripts/check_guix.sh`

## Acceptance-Basis

Die eingefrorene Basis gilt als erfüllt, wenn alle folgenden Punkte zutreffen:

1. `setup-web` startet und ist auf `3011` erreichbar
2. die Setup-Seite akzeptiert einen gültigen Host-Pfad
3. die Host-Erkennung in der Web-Setup-Fläche basiert auf dem Host-Snapshot statt auf containerlokalem Capability-Raten
4. die Runtime startet, nachdem das Setup gespeichert wurde
5. `repo-bridge-v2` wird gesund
6. `open-webui` wird erreichbar und gesund
7. der Handoff geht sauber zu Open WebUI weiter
8. `bash scripts/check_guix.sh` wird grün

## Explizit nicht Teil dieses Freeze

Dieser Freeze behauptet **noch nicht**:

- vollständige Open-WebUI-Tool-Server-Validierung
- vollständige Write-E2E-Validierung über die Chat-Oberfläche
- weitergehende Release-Aussagen außerhalb von Setup- und Handoff-Pfad

## Hinweise aus dem eingefrorenen Lauf

- der erste Kaltstart kann länger dauern, weil Open WebUI Embedding-/Runtime-Assets nachlädt
- während dieses Kaltstarts kann ein früher Health-Check noch fehlschlagen, bevor der Endzustand healthy erreicht ist
- das bricht den Freeze nicht, solange der Stack am Ende sauber auf healthy konvergiert und der Setup-Handoff danach funktioniert

## Zweck

Dieser Freeze soll das aktuell stabile Verhalten des Web-GUiX-Onboarding-Pfads festhalten, bevor der nächste Feature-Zyklus beginnt.
