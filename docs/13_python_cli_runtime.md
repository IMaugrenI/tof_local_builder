# Python CLI runtime

This repo now has a Python-first runtime entrypoint.

## primary entrypoint

```bash
python run.py setup
python run.py up
python run.py check
python run.py status
python run.py doctor
python run.py down
```

## wrapper availability

The runtime truth is `python run.py ...`.

Supported convenience wrappers are limited to these files:

- Linux shell wrappers: `scripts/setup.sh`, `scripts/up.sh`, `scripts/check.sh`, `scripts/down.sh`, `scripts/status.sh`, `scripts/doctor.sh`
- Windows PowerShell wrappers: `scripts/setup.ps1`, `scripts/up.ps1`, `scripts/check.ps1`, `scripts/down.ps1`, `scripts/status.ps1`, `scripts/doctor.ps1`
- macOS command launchers: `scripts/setup.command`, `scripts/up.command`, `scripts/check.command`, `scripts/down.command`, `scripts/status.command`, `scripts/doctor.command`

## goal

- one operational runtime entrypoint
- cross-platform start logic in Python
- compose remains the runtime truth
- shell scripts can become thin wrappers later

## current migration state

- `run.py` is available now
- `tof_cli/` contains the new command and core runtime modules
- builder-specific Python bridges exist for wizard, repo bridge and default model handling
- `scripts/compose_wrapper.sh` is deprecated and no longer part of the supported runtime path
- `scripts/ensure_model.sh` is deprecated and no longer part of the supported runtime path
- older helper scripts are not part of the supported runtime surface

## command summary

### setup

- creates `.env` from `.env.example` if missing
- prepares local runtime directories
- reports source repo and sandbox state

### up

- optionally runs the existing first-run wizard through Python
- resolves the compose runtime profile
- starts the stack with Docker Compose
- optionally ensures the default Ollama model

### check

- checks Ollama, Open WebUI and repo bridge HTTP health endpoints
- checks the default model presence

### status

- prints platform details
- prints compose file/mode state
- runs `docker compose ps`

### doctor

- verifies Docker presence and reachability
- checks source path and sandbox readiness
- scans configured ports
- reports platform-specific acceleration hints

### down

- stops the compose stack
