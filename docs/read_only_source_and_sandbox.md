# Read-only source + writable sandbox (V2)

This V2 mode keeps the builder simple and safe:

- source repository is mounted read-only
- builder sandbox is mounted read-write
- real repo changes are reviewed and moved later

## Purpose

Use this mode when you want the local builder to inspect an external repository or document source without writing into that source.

The write target stays inside the builder sandbox:

- `sandbox/workspace/`
- `sandbox/output/`
- `sandbox/examples/`

## Runtime paths inside the container

- source repo: `/workspace/source_repo_ro`
- builder sandbox: `/workspace/builder_sandbox`
- workspace drafts: `/workspace/builder_sandbox/workspace`
- output handoff: `/workspace/builder_sandbox/output`
- examples: `/workspace/builder_sandbox/examples`

## Start

1. Copy the V2 env example:

```bash
cp .env.readonly-sandbox.example .env
```

2. Set the absolute source repo path in `.env`:

```bash
SOURCE_REPO_PATH=/absolute/path/to/the/repo/or/source
```

3. Start V2:

```bash
docker compose -f compose.v2.readonly-sandbox.yml up -d
```

4. Check the services:

```bash
bash scripts/healthcheck.sh
```

5. Open WebUI:

- `http://localhost:3000`

## Rules

- never treat the mounted source path as writable
- prepare drafts and outputs in the sandbox only
- move reviewed results later
- separate observation from interpretation
- prefer concrete file paths

## Suggested use

Ask the model to:

- summarize the mounted source repo
- identify boundaries and drift
- draft a markdown note, shell script, or python file for the sandbox
- prepare a handoff artifact for a human, Codex, or Claude review

## Important note

The current baseline stack is still a lightweight local workspace.
This V2 layout adds a clean source/sandbox separation, but it does not by itself turn Open WebUI into a fully autonomous file-writing worker.

Treat this as a safe builder frame for local reading, drafting, and reviewed handoff.
