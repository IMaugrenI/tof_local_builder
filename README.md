# tof_local_builder

<p align="center">
  <img src="https://raw.githubusercontent.com/IMaugrenI/IMaugrenI/main/assets/banner/tof_local_builder_banner_v4_fixed.png" alt="tof_local_builder banner" width="100%" />
</p>

**Build with local AI while keeping source and output under control.**

Local Builder provides a workspace for AI-assisted implementation with **read-only mounted source material** and **separate sandboxed output**. The aim is useful generation with reviewable boundaries, not uncontrolled changes to an existing project.

**Get started:** [First run](START_HERE.md) · [German README](README_DE.md) · [ToF Systems overview](https://github.com/IMaugrenI/tof-showcase)

**Who it serves:** builders, self-hosters, and small local teams that want a local model-backed workflow and a clear place to review generated work. The repo is the independent **Generate** tool, not a full knowledge-management system or an automatically connected multi-tool suite.

**Workflow:** choose the local model and workspace → inspect the read-only source → work in Open WebUI → review output in the sandbox. Setup and control interfaces have separate responsibilities, as documented below.

## New in the B1 development branch

The existing browser control surface now includes a **read-only review panel** for generated files in `sandbox/workspace` and `sandbox/output`. It lists relative paths, file sizes and timestamps and permits bounded previews of small UTF-8 text files. Symlinks, paths outside the sandbox, and overlapping source/sandbox roots are rejected. Nothing is automatically copied, committed or pushed to the original project.

The normal `up` command no longer runs a blanket `docker compose down --remove-orphans` first. Readiness now checks the configured source path, sandbox, and selected model as well as local service endpoints.

These features are on the [B1 development pull request](https://github.com/IMaugrenI/tof_local_builder/pull/34). Passing GitHub CI checks prove code-level checks only; they are not a statement that a target machine was tested.

## B2: compare generated changes before adopting them

The existing local control UI now offers **Compare to source** alongside sandbox file previews. Small UTF-8 text files under `sandbox/workspace` or `sandbox/output` are compared with the file at the **same relative path** in the selected read-only project. The panel distinguishes new, identical, modified, unavailable, and too-large source files and shows a bounded unified diff.

Comparison is **read-only**. There is no automatic application, commit, or push to the original repository. Oversized, binary, unsafe, or out-of-root paths are rejected.

## B3 — Guided task and model choice

The existing local control UI now includes a **task-first planning panel**. Task types and model suggestions come from the existing `model_catalog/builder_catalog.json`. Only models detected as locally installed through Ollama are available for selection.

The panel produces a **copyable prompt** to use in Open WebUI. Users select the model in Open WebUI and decide whether to adopt generated files after read-only review. This planning step does not download models, execute tasks, or write into the selected source project.

## B4 — One-step task handoff

The existing task panel now offers **Copy & open workspace**. It copies the prepared task prompt and opens the configured local Open WebUI only after the copy succeeds. You select the model and submit the prompt yourself in Open WebUI. No task is executed automatically, and no changes are copied back to source.

Browser links for Open WebUI, the project bridge and Ollama now follow the repository's existing `.env` port settings instead of assuming fixed ports. Invalid port settings are rejected rather than redirecting to an arbitrary address.

## B5 — Track reviewed generated files

The existing sandbox review screen now includes a **per-file reviewed/not reviewed checklist**, a pending-only filter, and a visible reviewed count. A text file can be marked reviewed only after its preview or complete source comparison was opened. The review mark is stored locally in the browser and bound to that exact file content and the selected source/sandbox paths: changing a generated file invalidates the old mark. Oversized/binary files cannot be marked reviewed using the short-text viewer.

This is a **manual review aid, not an approval to apply a patch**. No original project files are modified, and the UI does not commit, copy or push generated results.

## B6 — Task-oriented local model suggestions and project overview

The existing task panel now **prefers an installed model suitable for the selected task**, according to the existing model catalog and its profile order. Users retain manual choice; no model installation or configuration change is triggered.

A **read-only project summary** displays the selected source and sandbox state plus a bounded list of up to 24 visible, first-level source entries. It never recursively reads project content and excludes hidden entries from this summary. The original repository and Compose workflows stay unchanged.

## B7 – Guided status and next steps

The existing control page now prioritizes missing prerequisites: source project, separate sandbox, Ollama, selected model, repository bridge and WebUI. Each non-ready component receives a human-readable next step and a button for a relevant existing command (`setup`, `up`, or `doctor`). Nothing is repaired automatically. Original project files, API contracts and the current Compose startup path are unchanged.

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
A German quickstart mirror is available in `docs/00_beginner_quickstart_DE.md`.

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
- [`tof-showcase`](https://github.com/IMaugrenI/tof-showcase) — public architecture entry point
- [`tof-v7-public-frame`](https://github.com/IMaugrenI/tof-v7-public-frame) — reduced V7 boundary frame
