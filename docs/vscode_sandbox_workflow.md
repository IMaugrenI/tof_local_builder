# VS Code sandbox workflow

This document describes the intended safe workflow for editor-based coding with `tof_local_builder`.

## Principle

Use VS Code as the working surface.
Use `tof_local_builder` as the local model and prompt base.
Use the sandbox as the only write-enabled workspace for early experiments.

## Why this split

- VS Code is the practical editor workspace
- `tof_local_builder` stays the local AI/tool base
- the sandbox keeps experiments away from real repos and active stacks

## Safe baseline

Do not point editor-based AI tooling at real production repos first.
Start inside:

- `sandbox/workspace/`

Generated outputs may also be collected in:

- `sandbox/output/`

## Example use

A model or editor tool may create:

- `sandbox/workspace/coinflip.pu`
- `sandbox/workspace/module_candidate.md`
- `sandbox/output/notes.txt`

## Rule

Sandbox first.
Real repo later.

Only after review should anything be copied into a real repo.
