# tof_local_builder

> English is the primary text in this repository. A German clone is available in `README_DE.md`.

Small local builder stack for repo work, audits, drift checks, and code assistance without strong cloud or token pressure.

This repository is meant as a local, inspectable workspace for coding models and repo-focused work.

## Purpose

`tof_local_builder` is a lightweight local workspace for:

- running local coding models with Ollama
- using a browser GUI with Open WebUI
- keeping reusable prompts and profiles for repo work
- starting with a small, understandable Docker stack

## Core idea

The builder itself is not a self-improving system.
It is first a local workspace and tool carrier.

It can become more useful through:

- better prompts
- better profiles
- better workflows
- later retrieval, memory, or fine-tuning layers

But that is not automatic in the current baseline.

## Included

- `compose.yml` for Ollama + Open WebUI
- reusable prompts for repo audits and drift checks
- starter profiles for Ollama, Aider, and Continue
- Ubuntu setup notes
- English primary docs plus German `_DE` clones

## Quick start

```bash
cp .env.example .env
bash scripts/bootstrap.sh
bash scripts/healthcheck.sh
```

Then open:

- Open WebUI: `http://localhost:3000`
- Ollama API: `http://localhost:11434`

## Structure

- English primary:
  - `README.md`
  - `docs/architecture.md`
  - `docs/setup_ubuntu.md`
  - `docs/usage.md`
  - `docs/profiles_overview.md`
  - `prompts/repo_audit.md`
  - `prompts/drift_check.md`
  - `prompts/codex_style_tasks.md`

- German clones:
  - `README_DE.md`
  - `docs/architecture_DE.md`
  - `docs/setup_ubuntu_DE.md`
  - `docs/usage_DE.md`
  - `docs/profiles_overview_DE.md`
  - `prompts/repo_audit_DE.md`
  - `prompts/drift_check_DE.md`
  - `prompts/codex_style_tasks_DE.md`

## Profiles

The profile directory stays language-neutral for the actual config files.
A short bilingual overview is documented here:

- English: `docs/profiles_overview.md`
- German: `docs/profiles_overview_DE.md`

Technical files such as `compose.yml`, `.env.example`, scripts, and tool profile configs stay shared.
