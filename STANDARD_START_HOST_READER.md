# Optional advanced mode: host reader

This is an optional advanced path for cases where the reader must use a pasted absolute local path from the host machine. The normal beginner/default start remains `scripts/start_here.*`, which uses the containerized repo bridge and its selected read-only source root.

## Why this mode exists

The containerized repo bridge keeps the read side tied to container roots.
The host reader path removes that friction, but it is intentionally more powerful because it can read any absolute path that the local user running the bridge can access:

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

**Security note:** this mode is not constrained to the source path selected by the normal builder wizard. Use it only on a trusted local machine, keep the bridge bound to `127.0.0.1`, and do not expose it to a LAN or the internet.

## Writer endpoints

- `POST /writer/mkdir`
- `POST /writer/write`
- `POST /writer/doit`

## Writer rule

Writes stay limited to `sandbox/workspace` and `sandbox/output`.
