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

## Alternative browser-first path

If you want a simpler browser control path:

```bash
python run.py ui
```

## What happens

The start-here path does three things in order:

1. prepares local folders and `.env` defaults
2. starts the local builder stack
3. checks whether the main services answered correctly

The browser UI gives you:

- stack control buttons
- direct links to the main local pages
- a simple local entry point into the builder environment

## What success looks like

You should end up with:

- the local stack running
- a browser-accessible WebUI
- a working local builder environment
- a browser page where you can open the main local services directly

## Simple normal path

- start the stack
- open the browser UI
- open WebUI
- verify repo bridge or Ollama if needed
- continue in the actual builder workspace

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
