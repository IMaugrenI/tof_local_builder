# Beginner quickstart

This guide is for people who want the shortest safe path.

## Fastest safe path

### Linux

```bash
bash scripts/start_here.sh
```

### Windows PowerShell

```powershell
pwsh ./scripts/start_here.ps1
```

### macOS

```bash
./scripts/start_here.command
```

## What happens (clear chain)

The start-here path always does:

1. setup (first-run wizard if needed)
2. start the stack
3. check health

## What opens and what you use

- Wizard = first setup only
- Local UI = control surface
- Open WebUI = your actual workspace

## What success looks like

You should see:

- running stack
- reachable WebUI
- working builder environment

## Everyday use

```bash
python run.py up
python run.py status
python run.py check
python run.py down
```

## If something fails

```bash
python run.py doctor
```
