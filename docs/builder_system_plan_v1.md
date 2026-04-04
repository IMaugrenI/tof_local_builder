# Builder system plan v1

## Purpose

This document defines the next public product cut for `tof_local_builder` after the current freeze baseline.

The goal is **not** to turn the builder into a general local AI bundle.
The goal is to turn the builder into a clearer public product for local work with a guided model choice.

## Product reading

`tof_local_builder` is the local builder product for:

- chat and writing
- repo reading and small code assistance
- text analysis and summarizing
- controlled local work through Open WebUI and the repo bridge
- optional stronger local profiles on better hardware

The builder is **not** the knowledge system.
Knowledge, embeddings, retrieval, and broader RAG storage remain outside the builder product cut.

## Why this plan exists

The current wizard model selection is still a flat shared list.
That is acceptable for a first curated expansion, but not yet the final product shape.

The builder should ask for the **task**, not force the user to understand Ollama tags first.

## Public product boundary

Inside the builder product:

- general chat and writing models
- code helper models
- text analysis and summarizing models
- optional stronger 3B profiles
- optional future vision profile
- manual `custom` fallback

Outside the builder product:

- embeddings
- retrieval-only models
- knowledge indexing and document stores
- broader RAG pipelines
- company knowledge system logic

## Builder model packs v1

The first public pack cut should be based on the current curated builder model space.

### General / CPU-light

Use when the user wants the lightest practical local experience.

- `qwen2.5:0.5b`
- `llama3.2:1b`

### General / CPU-balanced

Use when the user wants a better all-round local assistant but still wants a CPU-friendly default range.

- `qwen2.5:1.5b`
- `gemma2:2b`

### General / Optional 3B

Use only as an explicit stronger profile, not as the default builder path.

- `qwen2.5:3b`
- `llama3.2:3b`

### Code / CPU-light

Use when the user mainly wants light code help, snippets, and small fixes.

- `qwen2.5-coder:0.5b`

### Code / CPU-balanced

Use when the user wants more useful repo and code assistance without moving to the stronger tier.

- `qwen2.5-coder:1.5b`

### Code / Optional 3B

Use only as an explicit stronger coding profile.

- `qwen2.5-coder:3b`

### Manual fallback

- `custom`

## Builder questions in the wizard

The next wizard step should move from a flat model list to a guided task flow.

### Step 1 — What do you need the builder for?

- Chat and writing
- Code and repo help
- Analysis and summaries
- I am not sure yet

### Step 2 — How light should the setup stay?

- very light
- balanced
- stronger optional profile

### Step 3 — Builder recommendation

The wizard should then show:

- one recommended model
- a small number of alternatives
- a short reason in plain language

Example:

- Task: code and repo help
- Hardware preference: balanced
- Recommendation: `qwen2.5-coder:1.5b`
- Alternatives: `qwen2.5-coder:0.5b`, `qwen2.5-coder:3b`

## Internal repo structure target

The builder should move toward a small model catalog instead of one long hardcoded list.

```text
model_catalog/
  builder_catalog.json
  catalog.schema.json
  general/
    cpu_light.json
    cpu_balanced.json
    optional_3b.json
  code/
    cpu_light.json
    cpu_balanced.json
    optional_3b.json
  analysis/
    cpu_light.json
    cpu_balanced.json
```

## Data shape target

Each model entry should carry more meaning than just the raw tag.

Suggested fields:

- `tag`
- `group`
- `profile`
- `task_labels`
- `recommended`
- `default_candidate`
- `notes`
- `visible_in_wizard`
- `experimental`

## Migration path

### Phase 1

Merge the curated wizard model expansion.

### Phase 2

Introduce the builder model catalog files while preserving compatibility with the current setup flow.

### Phase 3

Change the wizard from:

- direct model selection

to:

- task choice
- profile choice
- recommended model output

### Phase 4

Keep an advanced escape hatch:

- show all compatible builder models
- manual `custom` tag entry

## Product language

The public builder should speak in product language first.

Good language:

- chat and writing
- code and repo help
- analysis and summaries
- light profile
- balanced profile
- stronger optional profile

Avoid as the first public surface:

- long raw Ollama tag lists
- knowledge or retrieval jargon
- embedding-focused choices in the normal builder path

## Explicit non-goals for v1

This plan does **not** yet introduce:

- a knowledge subsystem inside the builder
- embedding packs inside the standard builder wizard
- a full all-model browser
- auto-benchmarking or host-score based model ranking
- a second product mixed into the builder repo

## Acceptance for builder plan v1

This plan is considered implemented when all of the following are true:

1. the builder public docs describe the task-first model cut
2. the repo contains a clear target path for grouped model packs
3. the wizard no longer has to stay permanently tied to one flat list
4. the builder remains CPU-first by default
5. stronger 3B models stay optional rather than becoming the new default

## Summary

The builder should evolve from a local stack with a flat model picker into a guided local builder product.

The core move is simple:

- from model tags first
- to task and profile first

That keeps the builder public, understandable, CPU-friendly, and expandable without mixing it into the knowledge product.
