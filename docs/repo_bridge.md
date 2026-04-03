# Repo Bridge

The repo bridge is the controlled boundary between the read-only source and the writable sandbox.

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

## Write rule

Use the root name and a relative path separately.

Example:

```json
{
  "target_root": "output",
  "relative_path": "test/chat_note.md",
  "content": "Bridge test ok",
  "overwrite": true
}
```
