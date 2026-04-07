# host_repo_bridge

Simple host-native tool server for `tof_local_builder`.

## Why this exists

This variant removes the container path confusion for reading local material.

Reader behavior:

- paste one absolute local path
- read exactly that file or directory
- recurse through subdirectories when requested

Writer behavior:

- stays limited to `sandbox/workspace` and `sandbox/output`

## Start

```bash
bash scripts/up_host_bridge.sh
```

Open WebUI stays at `http://localhost:3000`.

Use this tool server URL inside Open WebUI:

```text
http://host.docker.internal:8099
```

Direct local bridge URL on the host:

```text
http://127.0.0.1:8099
```
