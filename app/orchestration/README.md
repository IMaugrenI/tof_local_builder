# orchestration

## Role

This space owns the builder-facing control flow.

It decides which internal capability should handle a user request:
- direct folder view
- direct file read
- direct text search
- sandbox writing
- optional grounded search
- optional grounded QA

## Product rule

Users should speak naturally.
The orchestration layer translates that intent into the right internal tool path.

## Non-goal

This space should not become a second wizard, a second UI, or a dumping ground for every runtime concern.
