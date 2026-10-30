# tof_local_builder

<p align="center">
  <img src="https://raw.githubusercontent.com/IMaugrenI/IMaugrenI/main/assets/banner/tof_local_builder_banner_v4_fixed.png" alt="tof_local_builder banner" width="100%" />
</p>

**Build with local AI while keeping source and output under control.**

Local Builder provides a workspace for AI-assisted implementation with **read-only mounted source material** and **separate sandboxed output**. The aim is useful generation with reviewable boundaries, not uncontrolled changes to an existing project.

**Get started:** [First run](START_HERE.md) · [German README](README_DE.md) · [ToF Systems overview](https://github.com/IMaugrenI/tof-showcase)

**Source distribution candidate (B8/K8):** Existing Windows/Linux/macOS starters can now be packaged from a committed Git snapshot using the manual **Source distribution candidate** workflow or `python scripts/build_source_candidate.py --output-dir dist`. The ZIP includes [offline instructions](docs/RELEASE_PACKAGE.md) and a SHA-256 checksum. **Not an approved release or native installer; target-system acceptance comes after development.**

**Who it serves:** builders, self-hosters, and small local teams that want a local model-backed workflow and a clear place to review generated work. The repo is the independent **Generate** tool, not a full knowledge-management system or an automatically connected multi-tool suite.

**Workflow:** choose a project → use the local AI directly in Builder → review results. No Open WebUI.


## Current main development state (2026-10-30)

**Open WebUI is no longer a Compose runtime service.** The existing Builder control UI now hosts a bounded assistant connected directly to Ollama. The native UI supports **read-only dialogue** and a separate **Generate sandbox draft** workflow. That workflow inspects bounded source context, makes a plan and drafts up to six text files under sandbox/output; it never runs shell commands or changes the selected source. If interrupted, the operator can explicitly continue after Builder verifies the plan, source fingerprints and saved drafts. Python, JSON and TOML drafts receive a static, non-executing syntax check before saving, with at most one local-model repair attempt. Other file types are marked unchecked. Original source stays read-only, sandbox review remains in place. Target-system acceptance is pending.

**Start:** `python run.py setup` (first run), `python run.py up`, `python run.py check`. `up` starts or reuses the native Builder UI at `http://127.0.0.1:8795` (configurable via `BUILDER_UI_PORT`).

The native Builder chat also offers explicit **Save locally**, **Restore saved** and **Delete saved** controls. Conversations are not persisted automatically, and snapshots are scoped to the selected project in the existing sandbox metadata area.

An optional, consent-gated local Knowledge search is available for users who separately run ToF Local Knowledge. It shows up to five indexed excerpt references in the Builder UI. Retrieved document text is **never automatically injected into an LLM or build plan**. The Case Organizer remains isolated until an explicit safe data contract exists.

The historical Open-WebUI feature notes below are **not** the current workflow. Previous Open WebUI data is not deleted automatically; an already running old container is not stopped without an operator decision.

[Updated product constitution](docs/00_product/PRODUCT_CONSTITUTION_V2.md) · [Build plan](docs/WEBUI_FREE_BUILDER_EXPANSION.md)

## Historical milestones (B1–B9; prior Open WebUI workflow)

## B1 foundation (integrated into main)

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

## B9 – Reviewed manual source handoff

The existing generated-file review flow can now **copy complete changes for intentional manual adoption** after a file was inspected and marked reviewed. For small modified text files it provides a full unified diff, for new files it provides the complete text; identical files have nothing to transfer. The review token tracks both the source and generated file contents, so a stale review is rejected. Truncated or oversized files cannot use this shortcut.

**The original source stays read-only.** This function never applies, commits, stages or pushes output. The operator reviews and applies any change in their own editor.


## Use the current Builder

The `run.py` CLI, existing Linux/Windows/macOS launchers and repository-defined Compose path remain the supported runtime.

```bash
python run.py setup
python run.py up
python run.py check
```

The user now works in the **native Builder UI**. The chat reads a bounded README excerpt for orientation and returns an answer. A separate, user-initiated sandbox build can draft up to six reviewable text files using the existing Repo Bridge. Existing sandbox preview, compare and review remain mandatory before manually adopting any generated artifact.

**Boundary:** no automatic source commit, push or adoption. Not an approved public release; target-system validation remains pending.

More: [First run](START_HERE.md) · [Product constitution v2](docs/00_product/PRODUCT_CONSTITUTION_V2.md).
