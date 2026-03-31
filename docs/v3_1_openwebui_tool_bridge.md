# V3.1 Open WebUI tool bridge

## Goal

V3 gave the stack a real local repo bridge.
V3.1 adds the missing chat-facing layer:

- a ready-to-paste Open WebUI tool file
- a compose mode that keeps repo_bridge and Open WebUI together
- host UID/GID mapping for sandbox writes

## What this enables

Inside the Open WebUI chat, after the tool is added and enabled, you can ask for actions like:

- list files in a source path
- read a source file
- write a reviewed draft into `sandbox/workspace` or `sandbox/output`

## Files

- `compose.v3.1.openwebui-tool.yml`
- `env.openwebui-tool.example`
- `scripts/bootstrap_v3_1_openwebui_tool.sh`
- `openwebui_tools/repo_bridge_tool.py`

## Start

```bash
bash scripts/bootstrap_v3_1_openwebui_tool.sh
nano .env
```

Set at least:

```bash
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
HOST_UID=<your host uid>
HOST_GID=<your host gid>
```

Then:

```bash
docker compose down --remove-orphans
docker compose -f compose.v3.1.openwebui-tool.yml up -d --build
bash scripts/healthcheck.sh
bash scripts/test_repo_bridge.sh
```

## Add the tool in Open WebUI

1. Open Open WebUI.
2. Go to the Tools area in the admin or workspace settings.
3. Create a new tool.
4. Paste the contents of `openwebui_tools/repo_bridge_tool.py`.
5. Save the tool.
6. Enable the tool for the chat or model you want to use.

## Suggested first chat tests

- `Use repo_tree on the root path.`
- `Use repo_read on MANIFEST.md.`
- `Write a markdown note to output/test/chat_note.md.`

## Boundary

- source repo remains read-only
- writes stay limited to sandbox `workspace` or `output`
- no direct writes into the source repo
