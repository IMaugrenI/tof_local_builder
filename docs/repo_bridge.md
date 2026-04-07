# Repo Bridge

The repo bridge is the controlled boundary between the read-only source and the writable sandbox.

## Root model

The bridge separates two different spaces:

1. **Read space**
   - selected through `SOURCE_REPO_PATH` on the host
   - mounted read-only into the container as `/workspace/source_repo_ro`
   - exposed in the API as the logical root name `source`

2. **Write space**
   - stays inside the builder sandbox on the host
   - mounted into the container as `/workspace/builder_sandbox`
   - exposed in the API as the logical root names `workspace` and `output`

## Roots

- `source`
- `workspace`
- `output`

## Operations

- `roots` shows the available roots
- `tree` lists one directory
- `read` reads one file
- `find` finds file and directory names
- `search` searches text content inside files
- `mkdir` creates a sandbox directory
- `write` writes a text file into the sandbox
- `doit` is a small guided wrapper for `mkdir` and `write`

## Read and write rule

Use the root name and a relative path separately.

- Read from `source`
- Write only to `workspace` or `output`
- Do not pass host absolute paths to `read`, `tree`, `find`, or `search`

Example:

```json
{
  "target_root": "output",
  "relative_path": "test/chat_note.md",
  "content": "Bridge test ok",
  "overwrite": true
}
```

## Host path visibility

`/roots` and `/health` also expose the selected host path and the internal container path view so that the active read space stays transparent.
