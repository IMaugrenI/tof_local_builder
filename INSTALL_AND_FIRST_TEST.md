# Install and first test

This file is the shortest practical path for a fresh local download.

## 1. Get the repository

Clone it or download it from GitHub, then enter the repository folder.

```bash
git clone https://github.com/IMaugrenI/tof_local_builder.git
cd tof_local_builder
```

## 2. Use the easiest start path

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

## 3. What should happen

The repository should:

1. prepare local setup
2. start the builder stack
3. check the main services

## 4. First real browser test

You can also open the local browser control path:

```bash
python run.py ui
```

Then do this:

1. confirm the readiness cards update
2. open WebUI
3. confirm the repo bridge health endpoint is reachable
4. confirm the Ollama endpoint is reachable when expected

## 5. What counts as success

A good first test means:

- the stack comes up locally
- the browser UI opens
- readiness cards reflect reality
- WebUI is reachable
- the repo bridge is reachable
- the builder path is understandable without reading deep internal docs

## 6. If something fails

Run:

```bash
python run.py doctor
python run.py status
python run.py check
```

Then fix the first failing item before doing anything else.

## 7. Best first local test style

Start with a small harmless local source directory.

Confirm the front door, WebUI, and readiness state first before doing deeper work.
