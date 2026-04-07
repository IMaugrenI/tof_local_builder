# Product Constitution v1

## Product identity

`tof_local_builder` is the visible local product.

The product must feel like one clean local application:
- one download
- one visible start path
- one visible wizard
- one visible workspace concept
- one visible chat surface

Internal engines may exist, but they must stay behind the builder surface.

## User promise

A user downloads the system, starts it, selects a source path and an output path, chooses recommended local models, waits for setup to finish, and then uses natural language in Open WebUI.

The user should not need to understand compose details, root mapping, internal API names, or multiple repo identities.

## Source and output rule

There are two central path truths:

1. Read path
   - selected by the user
   - acts as the active local source space
   - all direct reading and later knowledge ingestion must stay tied to this source

2. Write path
   - selected by the user or defaulted into the product sandbox
   - all generated files, notes, markdown outputs, and derived artifacts must land here

The system must never silently write back into the selected source path.

## Mode rule

The product has two official runtime modes:

1. Light mode
   - local builder workflow
   - low hardware pressure
   - direct host reader
   - sandbox writer
   - local models through Ollama
   - Open WebUI as the chat surface

2. Grounded mode
   - everything from light mode
   - plus knowledge indexing, extraction, search, and grounded QA
   - evidence-first outputs with explicit uncertainty

Light mode is the first-class default.
Grounded mode is optional and must remain clearly marked as heavier.

## Model slots

The wizard and runtime must treat model roles as separate slots:
- chat
- coding
- analysis
- task/background
- optional grounded wording or QA wording

The system must not assume one model is ideal for every role.

## Tool language rule

Internal tool structure may remain strict, but visible tool behavior must feel human-readable.

Prefer visible actions like:
- view folder
- read file
- find in folder
- search in text
- write file
- create folder

Small LLMs must be able to use the tools successfully.
That means compact outputs, shallow structures, and low interpretation burden.

## Wizard rule

There is one official first-run wizard.
It should:
- detect hardware
- explain recommendations
- set read and write paths
- set model slots
- choose light or grounded mode
- save configuration
- start installation/bootstrap
- open Open WebUI after success

Multiple parallel wizard truths are not allowed as a product direction.

## Knowledge rule

Knowledge is an internal engine, not the visible product face.
The builder remains the visible surface.

If the knowledge engine is integrated into this repo, it must remain logically separated and live behind the builder-facing orchestration layer.

## Repair rule

The product must expose a repair path.
Users must be able to:
- re-check runtime
- re-check tool connectivity
- re-check paths
- re-check model availability
- repair setup without manually reconstructing internals

## Platform rule

Linux is the first supported platform.
Windows and macOS are later targets.
The target architecture must keep this expansion possible without rethinking the product identity.
