# tof_local_builder

> English is the primary text in this repository. A German clone is available in `README_DE.md`.

Local GUI-first builder for one-machine or small local company use.

## At a glance

- runs local models through Ollama
- exposes a browser GUI through Open WebUI
- reads a mounted source path as read-only
- writes reviewed artifacts only into a local sandbox
- keeps source and writable output clearly separated
- first start ensures a small default Ollama model is present
- first start opens a small local setup wizard and then hands over to the web surface
- stays CPU-safe by default; optional acceleration modes can be enabled later when the host supports them

## What this repo is for

This repository is meant for controlled local builder workflows:

- local prompt and editor-based experimentation
- read-only access to a mounted source repo or source path
- reviewed writes into a sandbox instead of the source
- GUI-first local interaction through Open WebUI

## Product boundary

- source repo stays read-only
- writes stay limited to `sandbox/workspace` and `sandbox/output`
- no direct writes into the source repo
- this is a builder stack, not a general-purpose knowledge system

## Runtime components

- `ollama` = local model runtime
- `open-webui` = browser GUI
- `repo-bridge` = controlled read/write boundary for source and sandbox
- `wizard.py` = one-time local setup guide before the web handoff

## Quick start

1. prepare local setup:

```bash
bash scripts/setup.sh
```

2. start the stack:

```bash
bash scripts/up.sh
```

3. check health:

```bash
bash scripts/check.sh
```

4. first-run flow:

- a small local setup wizard appears if the builder is not configured yet
- once the setup is saved, the normal builder start continues
- after startup the flow hands over to `http://localhost:3000`

5. in Open WebUI go to:

- `Tool Server Management`

6. paste the base URL:

- `http://127.0.0.1:8099`

## First-run defaults

- the first `up.sh` run ensures `DEFAULT_OLLAMA_MODEL` is available
- the default model is `qwen2.5:0.5b`
- stronger hardware can switch to a larger Ollama model later by changing `.env`
- `BUILDER_ACCELERATION=cpu` keeps the stack on the portable baseline by default; later you can switch to `auto` or `intel` in `.env` if you want to test hardware acceleration
- the wizard can be reopened with `python3 scripts/wizard.py --force`

## Operator commands

Use the small public command surface for normal operation:

```bash
bash scripts/setup.sh
bash scripts/up.sh
bash scripts/check.sh
bash scripts/logs.sh
bash scripts/down.sh
```

More details:

- [`docs/commands.md`](docs/commands.md)
- [`docs/commands_DE.md`](docs/commands_DE.md)

## Required `.env` values

```env
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
BUILDER_SANDBOX_PATH=./sandbox
HOST_UID=1000
HOST_GID=1000
ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DEFAULT_OLLAMA_MODEL=qwen2.5:0.5b
BUILDER_ACCELERATION=cpu
BUILDER_OPEN_BROWSER=1
BUILDER_SETUP_DONE=0
```

## Files that matter

- `compose.yml`
- `compose.intel.yml`
- `.env.example`
- `scripts/setup.sh`
- `scripts/up.sh`
- `scripts/check.sh`
- `scripts/down.sh`
- `scripts/ensure_model.sh`
- `scripts/compose_wrapper.sh`
- `scripts/builder_bootstrap.py`
- `scripts/wizard.py`
- `docs/quickstart.md`
- `docs/commands.md`
- `services/repo_bridge/`
- `sandbox/`

## Related public repos

- [`tof-showcase`](https://github.com/IMaugrenI/tof-showcase) — public architectural frame
- [`tof_local_knowledge`](https://github.com/IMaugrenI/tof_local_knowledge) — on-prem local knowledge system
