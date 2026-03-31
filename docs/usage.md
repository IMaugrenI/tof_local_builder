# Usage

## Typical use cases

- inspect a repo locally
- review architecture drift
- write implementation prompts
- run coding assistance without cloud dependency

## Basic workflow

1. Start the stack.
2. Pull one local model.
3. Open WebUI.
4. Paste or adapt prompts from `prompts/`.
5. Use editor integrations when needed.

## Suggested pattern

- chat UI for planning and audits
- editor integration for code edits
- prompt library for repeatable tasks

## First useful prompt

Ask the model to:
- summarize repo structure
- detect unclear boundaries
- list drift between docs and code
- propose the next smallest clean step
