# host_reader

## Role

The host reader is the official product read boundary.

It reads from one user-selected local source path on the host machine.
It may inspect folders, read files, find names, and search text.

## Product rules

- read only from the selected source path
- no silent write-back into the source path
- compact outputs for small LLMs should be preferred
- raw outputs may still exist for debugging

## Relationship to current state

The current `services/repo_bridge/host_main.py` path is the practical bridge into this future service space.
