# Runtime image pinning

This repository already exposes the runtime image refs through `.env`:

```env
OLLAMA_IMAGE=ollama/ollama:latest
OPENWEBUI_IMAGE=ghcr.io/open-webui/open-webui:main
```

## Purpose

The goal is to move from floating runtime refs to a deliberately tested pair of explicit tags.

## Safe workflow

1. choose a candidate Ollama tag and a candidate Open WebUI tag
2. set both tags in a local `.env`
3. run:

```bash
bash scripts/up.sh
bash scripts/check.sh
```

4. confirm all of the following:
   - compose status is healthy
   - the default model is available
   - `repo_bridge` health is green
   - `repo_bridge` OpenAPI responds
   - Open WebUI opens cleanly
5. only then promote the tested pair into the operator baseline you want to keep

## Why this matters

Blindly pinning one image without validating the pair can create avoidable drift between the model runtime, the web surface, and the operator path.

## Recommended rule

- `latest` and `main` are fine for exploration
- explicit tags are better for a repeatable baseline
- only pin tags that were actually tested together

## Promotion example

```env
OLLAMA_IMAGE=ollama/ollama:<tested-tag>
OPENWEBUI_IMAGE=ghcr.io/open-webui/open-webui:<tested-tag>
```

Replace `<tested-tag>` only after you have a verified pair.
