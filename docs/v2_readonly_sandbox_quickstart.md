# V2 quickstart

This quickstart uses the additive V2 files in this repository.

## Files

- `env.readonly-sandbox.example`
- `compose.v2.readonly-sandbox.full.yml`
- `scripts/bootstrap_v2_readonly_sandbox.sh`
- `prompts/source_to_sandbox_task.md`

## Start

```bash
bash scripts/bootstrap_v2_readonly_sandbox.sh
nano .env
```

Set:

```bash
SOURCE_REPO_PATH=/absolute/path/to/the/source/repo
```

Then start:

```bash
docker compose -f compose.v2.readonly-sandbox.full.yml up -d
bash scripts/healthcheck.sh
```

## Runtime separation

- source: `/workspace/source_repo_ro`
- sandbox workspace: `/workspace/builder_sandbox/workspace`
- sandbox output: `/workspace/builder_sandbox/output`
- sandbox examples: `/workspace/builder_sandbox/examples`

## Intent

Use this mode when the builder should read a local source but keep all drafts and handoff artifacts inside its own sandbox.
