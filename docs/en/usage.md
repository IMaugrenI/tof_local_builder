# Usage

## Typical use cases

- inspect a repo locally
- detect architecture drift
- write implementation prompts
- use coding assistance without heavy cloud dependence

## Basic flow

1. Start the stack.
2. Pull one local model.
3. Open Open WebUI.
4. reuse or adapt prompts from `prompts/`.
5. Use editor integrations when needed.

## Suggested pattern

- chat UI for planning and audits
- editor integration for code changes
- prompt library for repeatable tasks

## First useful prompt

Ask the model to:
- summarize the repo structure
- point out unclear boundaries
- mark drift between docs and code
- propose the next smallest clean step
