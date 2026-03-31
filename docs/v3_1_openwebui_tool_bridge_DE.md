# V3.1 Open-WebUI-Tool-Bridge

## Ziel

V3 hat die echte lokale Repo-Bridge eingefuehrt.
V3.1 ergaenzt die fehlende Chat-Schicht:

- eine fertig vorbereitete Open-WebUI-Tool-Datei zum Einfuegen
- einen Compose-Modus, der repo_bridge und Open WebUI zusammen haelt
- Host-UID/GID-Mapping fuer Sandbox-Schreibrechte

## Was das ermoeglicht

Im Open-WebUI-Chat kannst du nach dem Hinzufuegen und Aktivieren des Tools direkt Dinge sagen wie:

- Dateien in einem Quellpfad auflisten
- eine Quelldatei lesen
- einen geprueften Entwurf nach `sandbox/workspace` oder `sandbox/output` schreiben

## Dateien

- `compose.v3.1.openwebui-tool.yml`
- `env.openwebui-tool.example`
- `scripts/bootstrap_v3_1_openwebui_tool.sh`
- `openwebui_tools/repo_bridge_tool.py`

## Start

```bash
bash scripts/bootstrap_v3_1_openwebui_tool.sh
nano .env
```

Mindestens setzen:

```bash
SOURCE_REPO_PATH=/absoluter/pfad/zur/quell-repo
HOST_UID=<deine host uid>
HOST_GID=<deine host gid>
```

Dann:

```bash
docker compose down --remove-orphans
docker compose -f compose.v3.1.openwebui-tool.yml up -d --build
bash scripts/healthcheck.sh
bash scripts/test_repo_bridge.sh
```

## Tool in Open WebUI hinzufuegen

1. Open WebUI oeffnen.
2. In den Bereich Tools in Admin- oder Workspace-Einstellungen gehen.
3. Neues Tool anlegen.
4. Den Inhalt von `openwebui_tools/repo_bridge_tool.py` einfuegen.
5. Tool speichern.
6. Tool fuer den gewuenschten Chat oder das gewuenschte Modell aktivieren.

## Empfohlene erste Chat-Tests

- `Nutze repo_tree auf dem Root-Pfad.`
- `Nutze repo_read auf MANIFEST.md.`
- `Schreibe eine Markdown-Notiz nach output/test/chat_notiz.md.`

## Grenze

- die Quell-Repo bleibt read-only
- Schreiben bleibt auf Sandbox `workspace` oder `output` begrenzt
- kein direktes Schreiben in die Quell-Repo
