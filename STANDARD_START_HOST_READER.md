# Standard start: host reader

This is the recommended default start path for the local builder when the reader should use a pasted absolute local path from the host machine.

## Why this is the default

The containerized repo bridge keeps the read side tied to container roots.
The host reader path removes that friction:

- copy one absolute local path from the file manager
- paste that path into the reader request
- read exactly that host file or directory
- recurse through the folder when needed
- keep writing limited to `sandbox/workspace` and `sandbox/output`

## Start

1. Start the host-native bridge:

```bash
bash scripts/start_host_repo_bridge.sh
```

2. Start Ollama and Open WebUI with the host-bridge compose file:

```bash
docker compose -f compose.host_bridge.yml up -d
```

3. In Open WebUI use this tool server URL:

```text
http://host.docker.internal:8099
```

4. For local checks on the host machine use:

```text
http://127.0.0.1:8099
```

## Reader endpoints

- `POST /reader/scan`
- `POST /reader/read_file`
- `POST /reader/find`
- `POST /reader/search`

## Reader rule

Pass one absolute local path directly.
No container root translation.
No `source/workspace/output` read model.

## Writer endpoints

- `POST /writer/mkdir`
- `POST /writer/write`
- `POST /writer/doit`

## Writer rule

Writes stay limited to `sandbox/workspace` and `sandbox/output`.
