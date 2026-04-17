# Commands

> English is the primary text in this document. A German mirror is available in `commands_DE.md`.

This repository exposes a small public operator path so local startup and shutdown stay easy to understand.

## Fastest beginner path

If you want the shortest safe path:

```bash
bash scripts/start_here.sh
```

Equivalent entry points:

- PowerShell: `pwsh ./scripts/start_here.ps1`
- macOS: `./scripts/start_here.command`

That path runs setup, startup, and health check in the expected order.

## Standard command flow

```bash
bash scripts/setup.sh
bash scripts/up.sh
bash scripts/check.sh
bash scripts/logs.sh
bash scripts/down.sh
```

## Commands

- `bash scripts/start_here.sh` — beginner path that runs setup, up, and check in sequence
- `bash scripts/setup.sh` — prepare `.env` and local directories
- `bash scripts/up.sh` — start the stack through the public wrapper, open the first-run setup wizard when needed, auto-detect Intel `/dev/dri` on Linux, and ensure the default Ollama model exists
- `bash scripts/check.sh` — run health checks for the live stack and show the expected tool-server base URL
- `bash scripts/logs.sh` — follow compose logs
- `bash scripts/pull.sh` — pull upstream images where available
- `bash scripts/down.sh` — stop the stack cleanly without deleting data
- `bash scripts/restart.sh` — restart through the public wrappers
- `bash scripts/reset.sh` — destructive reset for local service data and sandbox work/output
- `python3 scripts/wizard.py --force` — reopen the local setup wizard intentionally

## Safety markers

- SAFE: `start_here`, `setup`, `check`, `status`, `doctor`, `down`
- ADVANCED: `logs`, `pull`, `restart`, `wizard --force`
- DESTRUCTIVE: `reset`

## Notes

- `up.sh` wraps the existing `start.sh`
- `check.sh` remains the main health entry point
- `down.sh` is non-destructive by default
- `reset.sh` is the destructive path and should be used deliberately
- `DEFAULT_OLLAMA_MODEL` defaults to `qwen2.5:0.5b`
- `BUILDER_ACCELERATION` accepts `auto`, `cpu`, or `intel`
- `BUILDER_OPEN_BROWSER=1` opens the local WebUI after startup when possible
