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

## goal

- one operational runtime entrypoint
- cross-platform start logic in Python
- compose remains the runtime truth
- shell scripts can become thin wrappers later

## current migration state

- `run.py` is available now
- `tof_cli/` contains the new command and core runtime modules
- legacy shell scripts still remain for backward compatibility during transition
- builder-specific Python bridges exist for wizard, repo bridge and default model handling

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
