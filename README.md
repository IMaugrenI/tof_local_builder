# tof_local_builder

**A controlled local AI builder with read-only source and sandboxed output**

A local build workspace for AI-assisted implementation under human architectural control — with explicit source boundaries and isolated output paths.

> English is the primary text in this repository. A German clone is available in `README_DE.md`.

Local AI builder for controlled work on one machine or in a small local team.

## What this repo does

1. runs local models through Ollama
2. exposes a browser GUI through Open WebUI
3. reads a mounted source path as read-only
4. writes reviewed artifacts only into a local sandbox
5. uses a first-run wizard to guide setup and model choice
6. stays CPU-safe by default, with optional later acceleration

## Use this repo in the simplest way

If you want the shortest safe path, start here:

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

That path runs:

1. setup
2. startup
3. health check

A beginner guide is available in `docs/00_beginner_quickstart.md`.
A German quickstart clone is available in `docs/00_beginner_quickstart_DE.md`.

## Role model: what opens, what controls, where you actually work

This repo has three different browser-facing layers, and they should not be mixed up:

1. **First-run wizard**
   - runs during first setup when configuration is still incomplete
   - helps choose task type, performance profile, default model, and source path
   - writes the local setup once, then hands over

2. **Local control UI**
   - starts through `python run.py ui`
   - acts as a local control surface
   - helps you reach the main local pages and control the stack

3. **Open WebUI**
   - this is the main working surface after startup
   - this is where normal builder work actually happens

The runtime truth stays:

```bash
python run.py ...
```

The wrappers stay thin convenience launchers around that same command path.

## Why this repo is shaped this way

`tof_local_builder` is my strongest public example because it shows how I turn structure, boundaries, and build discipline into a concrete runnable form.

The source stays read-only because I want the source to be understood cleanly before anything is changed or processed further.

Output goes into a sandbox because results should stay separate, reviewable, and free from silent mixing.

The runtime is Python-first because the flow should stay clear, direct, and understandable.

## My role in this repo

My role here is:

- architecture and boundary definition
- workflow design and runtime shape
- review and correction of generated output
- public framing and scope reduction
- AI-assisted implementation under my direction

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
python run.py ui
```

## Cross-platform wrappers

The supported runtime truth is `python run.py ...`.

Supported convenience wrappers:

- Linux: `scripts/setup.sh`, `scripts/up.sh`, `scripts/check.sh`, `scripts/down.sh`, `scripts/status.sh`, `scripts/doctor.sh`, `scripts/start_here.sh`
- Windows PowerShell: `scripts/setup.ps1`, `scripts/up.ps1`, `scripts/check.ps1`, `scripts/down.ps1`, `scripts/status.ps1`, `scripts/doctor.ps1`, `scripts/start_here.ps1`
- macOS command launchers: `scripts/setup.command`, `scripts/up.command`, `scripts/check.command`, `scripts/down.command`, `scripts/status.command`, `scripts/doctor.command`, `scripts/start_here.command`

Examples:

```bash
./scripts/start_here.sh
pwsh ./scripts/start_here.ps1
./scripts/start_here.command
```

## What success looks like

A successful first run means:

- the local builder stack is running
- the first-run setup has already been written
- the browser-accessible WebUI opens correctly
- the tool server is reachable
- output stays inside the sandbox paths

## Normal everyday path

After first setup, the normal daily path is:

1. start the stack
2. open or verify the local control UI if needed
3. continue in Open WebUI as the real working surface
4. use `status` or `check` when you want confirmation
5. stop the stack with `down`

Daily commands:

```bash
python run.py up
python run.py status
python run.py check
python run.py down
```

## Role in the public product line

Generate (controlled creation)

### Works standalone
Yes.

### Can be combined with
- `tof_local_knowledge` for evidence-grounded input
- `local_case_organizer` for structuring reviewed outputs

### Not intended for
- feeding generated results back into knowledge as truth
- becoming a merged super-tool with the other products

## What this repo shows

1. architecture before implementation
2. explicit boundaries between source, runtime, and output
3. AI-assisted build work under human direction
4. practical local-system thinking instead of vague AI talk
5. documentation and runtime discipline

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
