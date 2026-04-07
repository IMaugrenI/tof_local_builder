# Host repo bridge start

This path is for the simple local reader case.

What changes:

- the reader takes one absolute local path
- it reads exactly that file or directory on the host
- recursion is controlled by the request
- the writer still stays limited to `sandbox/workspace` and `sandbox/output`

Files added for this path:

- `services/repo_bridge/host_main.py`
- `compose.host_bridge.yml`
- `scripts/start_host_repo_bridge.sh`

Suggested use:

1. Start the host bridge with `bash scripts/start_host_repo_bridge.sh`
2. Start Ollama and Open WebUI with the host-bridge compose file
3. In Open WebUI use the tool server URL `http://host.docker.internal:8099`
4. For direct local checks on the host use `http://127.0.0.1:8099`

Reader endpoints:

- `POST /reader/scan`
- `POST /reader/read_file`
- `POST /reader/find`
- `POST /reader/search`

Writer endpoints:

- `POST /writer/mkdir`
- `POST /writer/write`
- `POST /writer/doit`
