# Start here

This is the shortest supported path for a first-time user.

> German version: [START_HERE_DE.md](START_HERE_DE.md)

## What you are starting

`tof_local_builder` is a local AI-assisted build workspace. The normal path gives you:

- a first-run setup wizard
- local models through Ollama
- Open WebUI as the main browser workspace
- a selected source repository mounted read-only
- writable output only inside the builder sandbox

The normal start does **not** write back into the selected source repository.

## Requirements

Before the first start, have:

- Python 3.11+
- Docker with Docker Compose
- enough local disk space for the selected Ollama model

Linux is the primary supported platform. Windows and macOS launchers exist, but Linux remains the deepest-supported path.

## First start

### Linux

```bash
git clone https://github.com/IMaugrenI/tof_local_builder.git
cd tof_local_builder
bash scripts/start_here.sh
```

### Windows PowerShell

```powershell
git clone https://github.com/IMaugrenI/tof_local_builder.git
cd tof_local_builder
pwsh ./scripts/start_here.ps1
```

### macOS

```bash
git clone https://github.com/IMaugrenI/tof_local_builder.git
cd tof_local_builder
./scripts/start_here.command
```

The start-here path runs setup, starts the stack, and checks health.

## What opens

There are three surfaces:

1. **First-run wizard** — configuration during initial setup.
2. **Local control UI** — optional control/diagnostic surface.
3. **Open WebUI** — the main place where you work with the builder.

If you only want to use the product, Open WebUI is the important one after setup.

## How to know it worked

Run:

```bash
python run.py check
```

A good first run means:

- Docker services are up
- Open WebUI is reachable
- the repo bridge is reachable
- the selected local model is available
- source and sandbox paths are configured

## Everyday commands

```bash
python run.py up
python run.py status
python run.py check
python run.py ui
python run.py down
```

Use `doctor` if something is unclear:

```bash
python run.py doctor
```

## Where files go

- **Source:** selected by you and mounted read-only in the normal mode.
- **Workspace:** `sandbox/workspace/`
- **Output:** `sandbox/output/`

Generated work should stay in the sandbox until you review and move it yourself.

## Advanced host-reader mode

There is an optional host-native reader for trusted local use:

```bash
bash scripts/start_host_repo_bridge.sh
```

This mode can read absolute local paths that the current host user can access. It is intentionally more powerful than the normal source-root model.

Read [STANDARD_START_HOST_READER.md](STANDARD_START_HOST_READER.md) before using it. Keep it local and do not expose the bridge to a LAN or the internet.

## Stop

Normal stack:

```bash
python run.py down
```

## If you want more detail

- [Beginner quickstart](docs/00_beginner_quickstart.md)
- [Commands](docs/commands.md)
- [Repo bridge](docs/repo_bridge.md)
- [Product constitution](docs/00_product/PRODUCT_CONSTITUTION_V1.md)
