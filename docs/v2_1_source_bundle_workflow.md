# V2.1 source bundle workflow

## What this adds

V2 established the safe runtime separation:

- read-only source repo
- writable builder sandbox

V2.1 adds the first practical bridge for Open WebUI usage:

- build a readable source bundle from the mounted source
- place the bundle in `sandbox/output/source_bundle/`
- upload that generated bundle into Open WebUI for local analysis and drafting

## Why this exists

A mount alone makes files available to the container, but it does not automatically make Open WebUI browse and understand the source tree.

This workflow creates a controlled handoff artifact for the WebUI.

## Step by step

1. Start V2.
2. Verify mounts:

```bash
bash scripts/test_v2_mounts.sh
```

3. Build a source bundle:

```bash
bash scripts/build_source_bundle.sh
```

4. Optional smaller bundle:

```bash
bash scripts/build_source_bundle.sh --name repo_small --max-files 80 --max-bytes 120000
```

5. Open the generated files in:

- `sandbox/output/source_bundle/`

6. Upload the `*_bundle.md` file into Open WebUI.

7. Ask the model to summarize, audit, or draft follow-up files for the sandbox.

## Generated artifacts

- `*_manifest.txt`
- `*_tree.txt`
- `*_bundle.md`

## Intended use

- repo audits
- drift checks
- architecture reviews
- markdown draft generation
- shell script drafting
- python helper drafting

## Important boundary

This workflow is intentionally conservative.
It does not write into the source repo.
It creates reviewable artifacts inside the builder sandbox first.
