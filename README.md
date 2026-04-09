# tof_local_builder

> English is the primary text in this repository. A German clone is available in `README_DE.md`.

Local AI builder for controlled work on one machine or in a small local team.

I built this repo to keep source access read-only, output sandboxed, and the workflow easy to start.

## Why this repo is shaped this way

`tof_local_builder` is my strongest public proof because it shows how I turn architecture, build discipline, and clear separation into a concrete runnable form.

The source stays read-only because I want to understand the source cleanly before anything is changed or processed further.

Output goes into a sandbox because results should stay separate, reviewable, and free from silent mixing.

The runtime is Python-first because the flow should stay clear, direct, and understandable.

## Start here

Primary runtime entrypoint:

```bash
python run.py setup
python run.py up
python run.py check
```

Additional runtime commands:

```bash
python run.py status
python run.py doctor
python run.py down
```

## Cross-platform wrappers

The supported runtime truth is `python run.py ...`.

Supported convenience wrappers:

- Linux: `scripts/setup.sh`, `scripts/up.sh`, `scripts/check.sh`, `scripts/down.sh`, `scripts/status.sh`, `scripts/doctor.sh`
- Windows PowerShell: `scripts/setup.ps1`, `scripts/up.ps1`, `scripts/check.ps1`, `scripts/down.ps1`, `scripts/status.ps1`, `scripts/doctor.ps1`
- macOS command launchers: `scripts/setup.command`, `scripts/up.command`, `scripts/check.command`, `scripts/down.command`, `scripts/status.command`, `scripts/doctor.command`

Examples:

```bash
./scripts/setup.sh
pwsh ./scripts/setup.ps1
./scripts/setup.command
```

After startup, open `http://localhost:3000` and connect the tool server at `http://127.0.0.1:8099`.

## What you should understand quickly

This repo is not a random AI playground. It is a controlled build layer that shows how I structure systems seriously, with boundaries, review paths, and disciplined runtime behavior.

## What this repo does

1. runs local models through Ollama
2. exposes a browser GUI through Open WebUI
3. reads a mounted source path as read-only
4. writes reviewed artifacts only into a local sandbox
5. uses a first-run wizard to guide setup and model choice
6. stays CPU-safe by default, with optional later acceleration

## Boundary

1. the source repo stays read-only
2. writes stay limited to `sandbox/workspace` and `sandbox/output`
3. this is a builder stack, not a general knowledge system
4. local use comes first

## Key runtime parts

- `run.py`
- `tof_cli/`
- `compose.yml`
- `.env.example`
- `docs/13_python_cli_runtime.md`
- `services/repo_bridge/`
- `scripts/wizard.py`

## Related public repos

- [`tof_local_knowledge`](https://github.com/IMaugrenI/tof_local_knowledge) — local document indexing and grounded answers
- [`tof_showcase`](https://github.com/IMaugrenI/tof-showcase) — public architecture entry point
- [`tof_v7_public_frame`](https://github.com/IMaugrenI/tof-v7-public-frame) — reduced V7 boundary frame
