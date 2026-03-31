# Read-only-Quelle + beschreibbare Sandbox (V2)

Dieser V2-Modus hält den Builder klein und sauber:

- Quell-Repo wird nur lesend gemountet
- Builder-Sandbox wird schreibend gemountet
- echte Repo-Änderungen werden später geprüft und bewusst übernommen

## Zweck

Nutze diesen Modus, wenn der lokale Builder ein fremdes Repo oder einen lokalen Quellbestand lesen soll, ohne in diese Quelle hineinzuschreiben.

Das Schreibziel bleibt in der Builder-Sandbox:

- `sandbox/workspace/`
- `sandbox/output/`
- `sandbox/examples/`

## Laufzeitpfade im Container

- Quell-Repo: `/workspace/source_repo_ro`
- Builder-Sandbox: `/workspace/builder_sandbox`
- Arbeitsentwürfe: `/workspace/builder_sandbox/workspace`
- Übergabe-Output: `/workspace/builder_sandbox/output`
- Beispiele: `/workspace/builder_sandbox/examples`

## Start

1. V2-Env-Beispiel kopieren:

```bash
cp .env.readonly-sandbox.example .env
```

2. Absoluten Quellpfad in `.env` setzen:

```bash
SOURCE_REPO_PATH=/absoluter/pfad/zur/repo/oder/quelle
```

3. V2 starten:

```bash
docker compose -f compose.v2.readonly-sandbox.yml up -d
```

4. Dienste prüfen:

```bash
bash scripts/healthcheck.sh
```

5. WebUI öffnen:

- `http://localhost:3000`

## Regeln

- den gemounteten Quellpfad nie als Schreibziel behandeln
- Entwürfe und Ergebnisse nur in der Sandbox vorbereiten
- geprüfte Resultate später bewusst verschieben
- Beobachtung von Interpretation trennen
- konkrete Dateipfade bevorzugen

## Empfohlene Nutzung

Bitte das Modell darum:

- die gemountete Quell-Repo zusammenzufassen
- Grenzen und Drift zu benennen
- eine Markdown-Datei, ein Shell-Skript oder ein Python-Skript für die Sandbox zu entwerfen
- ein Übergabe-Artefakt für menschliches Review oder für Codex/Claude vorzubereiten

## Wichtiger Hinweis

Der aktuelle Baseline-Stack bleibt ein leichter lokaler Workspace.
Diese V2-Struktur ergänzt eine saubere Trennung von Quelle und Sandbox, macht Open WebUI aber nicht automatisch zu einem vollständig autonomen Dateischreib-Worker.

Lies das als sicheren Builder-Rahmen für lokales Lesen, Entwerfen und geprüfte Übergabe.
