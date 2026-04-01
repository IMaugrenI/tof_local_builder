# Befehle

> Deutsch ist die Spiegelversion dieses Dokuments. Der englische Primärtext liegt in `commands.md`.

Dieses Repository zeigt einen kleinen öffentlichen Operator-Pfad, damit lokales Starten und Beenden leicht verständlich bleibt.

## Standard-Befehlsfluss

```bash
bash scripts/setup.sh
bash scripts/up.sh
bash scripts/check.sh
bash scripts/logs.sh
bash scripts/down.sh
```

## Befehle

- `bash scripts/setup.sh` — `.env` und lokale Verzeichnisse vorbereiten
- `bash scripts/up.sh` — den Stack über den öffentlichen Wrapper starten
- `bash scripts/check.sh` — Health-Prüfungen für den laufenden Stack ausführen
- `bash scripts/logs.sh` — Compose-Logs verfolgen
- `bash scripts/pull.sh` — vorhandene Upstream-Images aktualisieren
- `bash scripts/down.sh` — den Stack sauber stoppen, ohne Daten zu löschen
- `bash scripts/restart.sh` — den Stack über die öffentlichen Wrapper neu starten
- `bash scripts/reset.sh` — destruktiver Reset für lokale Servicedaten und Sandbox-Work/Output

## Hinweise

- `up.sh` kapselt das bestehende `start.sh`
- `check.sh` bleibt der zentrale Health-Einstiegspunkt
- `down.sh` ist standardmäßig nicht destruktiv
- `reset.sh` ist der destruktive Pfad und sollte bewusst verwendet werden
