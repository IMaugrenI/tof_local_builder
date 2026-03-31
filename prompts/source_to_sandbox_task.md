# Source to sandbox task prompt

You are working in a local builder with a read-only source mount and a writable sandbox.

## Runtime paths

- source repo: `/workspace/source_repo_ro`
- sandbox workspace: `/workspace/builder_sandbox/workspace`
- sandbox output: `/workspace/builder_sandbox/output`
- sandbox examples: `/workspace/builder_sandbox/examples`

## Task

Read the source carefully and prepare a reviewed handoff artifact for the sandbox.

## Rules

- never claim that you wrote into the source repo
- treat the source repo as read-only
- draft outputs for the sandbox only
- separate observation from interpretation
- prefer concrete file paths
- mark uncertainty clearly
- do not invent files that are not present

## Requested output shape

1. short goal summary
2. source files inspected
3. draft artifact path inside sandbox
4. exact draft content
5. risks or open edges
6. next useful handoff step

## Typical artifact targets

- `/workspace/builder_sandbox/workspace/*.md`
- `/workspace/builder_sandbox/workspace/*.py`
- `/workspace/builder_sandbox/workspace/*.sh`
- `/workspace/builder_sandbox/output/*`
