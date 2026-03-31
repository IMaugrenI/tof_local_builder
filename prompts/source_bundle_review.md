# Source bundle review prompt

You are reviewing a generated source bundle from a local read-only source repository.

## Input assumption

The uploaded file is a generated `*_bundle.md` artifact from `sandbox/output/source_bundle/`.

## Task

Produce:
1. a short repository summary
2. the main subsystems or areas
3. unclear boundaries or drift
4. the next smallest clean step
5. one concrete artifact that should be drafted for the sandbox

## Rules

- treat the uploaded bundle as the current source view
- do not invent files that are not included
- separate observation from interpretation
- mark uncertainty clearly
- when drafting follow-up work, target the sandbox rather than the source repo
