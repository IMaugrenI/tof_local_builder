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

Platform-specific convenience wrappers are available as thin launchers:

- Linux shell wrappers: `scripts/*.sh`
- Windows PowerShell wrappers: `scripts/*.ps1`
- macOS command launchers: `scripts/*.command`

## goal

- one operational runtime entrypoint
- cross-platform start logic in Python
- compose remains the runtime truth
- shell scripts can become thin wrappers later

## current migration state

- `run.py` is available now
- `tof_cli/` contains the new command and core runtime modules
- legacy shell entry scripts remain as thin wrappers for compatibility
- builder-specific Python bridges exist for wizard, repo bridge and default model handling
- `scripts/compose_wrapper.sh` is deprecated and no longer part of the supported runtime path
- `scripts/ensure_model.sh` is deprecated and no longer part of the supported runtime path
- Windows and macOS wrapper sets are available for the primary commands

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
