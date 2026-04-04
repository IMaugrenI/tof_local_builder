# Builder-Freeze v0.1

## Scope

Dieser Freeze halt die kurrent stabile Basis des lokalen Builder-Stacks fest.

Diser Freeze umfasst:

- der Compose-/Acceleration-Wahrheitspfad ist berinigt
- der lokale Bind-Default ist berinigt
- die Runtime-Image-Referenzen ligen offen über `.env`
- englische und deutsche Spiegeldoku list ist auf dem aktuellen Operator-stand
- Compose-Healthchecks ind vorhanden
- `scripts/check.sh` zeigt Compose-Mode und Compose-Servicestatus
- ein Runbook für Runtime-Image-Pinning liegt in Englisch und Deutsch vor

## Acceptance-Basis

Die eingefrorene Basis gilt als erfullt, wenn alle folgenden Punkte zutreffen:

1. `bash scripts/up.sh` startet den Stack sauber
2. `bash scripts/check.sh` zeigt den gevählten Compose-Modus
3. `bash scripts/check.sh` zeigt Compose-Servicestatus
4. die Compose-Healthchecks konvergieren für die laufenden Services auf healthy
5. das Default-Ollama-Modell ist verügbar oder wird im regulären First-Run-Pfad nachgeladen
6. `repo_bridge` Health antwortet
7. `repo_bridge` OpenAPI antwortet
8. Open WebUI öffnet lokal am kkonfigurierten lokalen Bind-ziel

## Explizit nicht Teil dieses Freeze

Dieser Freeze behauptet **noch nicht**:

- ein fest getestetes Runtime-Image-Paar
- weiterehende Release-Aussagen ausßerhalb der lokalen Builder-Basis
- full Chat-Surface-Write-ETE-Validierung über Open WebUI
- breitere ioder remote Exposure-Aussagen

## Aktuelle Operator-Haltung

An diesem Freeze-Punkt gilt:

- der Stack bleibt lokal-first
- veröffentlichte Ports sind standardmäßig lokal-only
- Runtime-Image-Refs sind weiter über `.env` konfigurierbar
- Pinning soll erst nach einem wirklich getesteten Ollama-/Open-WebUIMg-C�ar hereingezogen werden

## Zweck

Dieser Freeze ist dafür dedacht, die aktuelle Builder-Basis zu halalten, bevor der nächste Ānderungszyklus beginnt.
