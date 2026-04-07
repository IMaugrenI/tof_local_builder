# Phased Repair Plan v1

This document translates the clean-repo rebuild into executable phases.

## Phase 1
Establish the product constitution and target repo structure.

## Phase 2
Reduce builder sprawl by creating one new official start surface and one new official wizard direction.

## Phase 3
Keep the host-native reader as the default read path and the sandbox writer as the default write path.

## Phase 4
Introduce compact human-friendly tool shapes for small LLMs while preserving raw endpoints for debugging.

## Phase 5
Define light and grounded modes as official runtime truths.

## Phase 6
Add clean runtime entry files and scripts for both modes.

## Phase 7
Prepare the repo for integrating the knowledge engine under `engines/`.

## Phase 8
Connect the knowledge engine only through the builder-facing orchestration layer, not as a second visible product face.

## Phase 9
Create repair and health-check flows that do not force users to rediscover internals.

## Phase 10
Mark the new structure as the official future truth and gradually demote legacy paths.

## Practical interpretation for this branch

This branch starts the rebuild by adding:
- the product constitution
- the target repo structure
- the mode definition
- the migration map
- the new runtime files
- the new script surface
- the service placeholders for host reader, sandbox writer, and tool gateway

The branch does not claim that every legacy file is already removed.
Instead it introduces the new official direction inside the repo so the cleanup can proceed in a controlled way.
