# tof_local_builder

A small local-first builder stack for repo work, audits, drift checks, and code assistance without cloud token pressure.

## Goal

`tof_local_builder` is a lightweight local workspace for:
- running local coding models with Ollama
- using a chat UI with Open WebUI
- keeping reusable prompts and profiles for repo work
- staying simple, inspectable, and easy to rebuild

## Principles

- local-first
- small and understandable
- replaceable parts
- Docker-based start
- explicit config

## Included

- `compose.yml` for Ollama + Open WebUI
- reusable prompts for repo audits and drift checks
- starter profiles for Ollama, Aider, and Continue
- setup notes for Ubuntu

## Quick start

```bash
cp .env.example .env
bash scripts/bootstrap.sh
bash scripts/healthcheck.sh
```

Then open:
- Open WebUI: `http://localhost:3000`
- Ollama API: `http://localhost:11434`

## Suggested first models

- `qwen2.5-coder:7b`
- `qwen2.5-coder:14b`
- `deepseek-coder-v2:16b`
- `llama3.1:8b`

## Repo layout

```text
tof_local_builder/
├── README.md
├── .gitignore
├── .env.example
├── compose.yml
├── docs/
│   ├── architecture.md
│   ├── setup_ubuntu.md
│   └── usage.md
├── prompts/
│   ├── repo_audit.md
│   ├── drift_check.md
│   └── codex_style_tasks.md
├── profiles/
│   ├── ollama/
│   │   └── models.md
│   ├── aider/
│   │   └── aider.conf.yml
│   └── continue/
│       └── config.example.json
└── scripts/
    ├── bootstrap.sh
    └── healthcheck.sh
```
