# Productization roadmap

## Goal

Turn `tof_local_builder` from a strong local builder stack repository into a local end-user product with a browser-led control path.

## Product target

A user should be able to:

1. download the project
2. run the starter path
3. open a browser control surface
4. prepare setup safely
5. start the builder stack
6. verify runtime health
7. open the main builder workspace
8. continue build work without needing to manage raw runtime steps manually

## Phase 1 — browser control front door

Status: started.

Target:

- local browser control UI
- setup button
- start-stack button
- check button
- status button
- doctor button
- stop button
- clear next-step guidance

## Phase 2 — builder runtime visibility

Target:

- visible WebUI link
- visible tool-server link
- visible runtime status in plain language
- visible model readiness state
- friendlier explanation of what is ready and what is missing

## Phase 3 — guided builder workflow

Target:

- easier wizard visibility
- clearer workspace/source/sandbox explanation
- simple open-workspace button
- simple open-WebUI button
- browser-led handoff into the actual builder workflow

## Phase 4 — cross-platform polish

Target:

- same control path on Windows, Linux, and macOS
- friendlier Docker readiness messages
- clearer browser success state
- release-ready starter paths

## Phase 5 — release mode

Target:

- GitHub releases
- simple download package
- starter files per operating system
- short offline user guide inside the release package

## Definition of done for product V1

- normal users can control setup and startup from the browser
- normal users can see whether the builder stack is actually ready
- normal users can reach the main workspace without reading deep repo internals
- the default path stays local-first
- the same basic path works across the three main supported operating systems
