# Beginner quickstart

This guide is for people who want the shortest safe path.

## What this repo is

`tof_local_builder` gives you a local AI build workspace on your own machine.

You do **not** need to understand the whole repo first.

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

## What happens

The start-here path does three things in order:

1. prepares local folders and `.env` defaults
2. starts the local builder stack
3. checks whether the main services answered correctly

## What success looks like

You should end up with:

- the local stack running
- a browser-accessible WebUI
- a working local builder environment

## If something fails

Run:

```bash
python run.py doctor
```

Then read the printed checks and fix the first failing item.

## Normal everyday commands after first startup

```bash
python run.py status
python run.py check
python run.py down
```
