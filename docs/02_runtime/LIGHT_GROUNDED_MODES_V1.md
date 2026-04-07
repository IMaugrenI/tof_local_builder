# Light and Grounded Modes v1

## Why modes exist

The product must support weak hardware and simple local use while still allowing a stronger grounded path when the user needs evidence-first workflows.

## Light mode

### Purpose
Fast local builder use with minimal pressure.

### Included parts
- Ollama
- Open WebUI
- host-native reader
- sandbox writer
- compact tool surface for small LLMs

### Intended use
- read from one selected local source path
- summarize files
- inspect folders
- generate markdown, notes, code snippets, or drafts into the output path
- work well on weaker machines

## Grounded mode

### Purpose
Everything from light mode plus a real local evidence engine.

### Included parts
- everything from light mode
- knowledge engine integration
- local ingest
- extraction
- search
- grounded QA
- Postgres-backed evidence storage

### Intended use
- scan and index the selected source path
- answer from grounded evidence instead of loose free-form guessing
- return visible uncertainty and citations when evidence is weak

## User-facing rule

The user should not need to understand the internal engine boundary.
The only visible difference should be a simple mode choice in the wizard and, later, in settings.

## Operational rule

Light mode is the default path.
Grounded mode remains clearly marked as heavier and optional.

## Path rule

Both modes use the same high-level path truth:
- read only from the selected source path
- write only to the selected output or sandbox path

Grounded mode may ingest from the selected source path, but must still never silently write back into that source path.
