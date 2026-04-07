# Knowledge Subtree Plan v1

## Goal

Integrate `tof_local_knowledge` into this repository without turning it into a second visible product face.

## Recommended Git strategy

Use `git subtree`, not a raw copy and not a submodule.

## Target location

```text
engines/tof_local_knowledge/
```

## Why subtree

- one repository clone for the user
- no submodule init flow for first testers
- cleaner long-term update path than raw copy-paste
- internal logical separation can still stay intact

## Product rule

The builder remains the visible surface.
The knowledge engine remains an internal engine space used by grounded mode.

## Suggested future command shape

These commands are not executed in this branch yet. They describe the intended future integration flow.

```bash
git remote add tof_local_knowledge https://github.com/IMaugrenI/tof_local_knowledge.git
git fetch tof_local_knowledge main
git subtree add --prefix=engines/tof_local_knowledge tof_local_knowledge main --squash
```
