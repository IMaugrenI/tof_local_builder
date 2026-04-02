# Why this repository exists

> English is the primary text in this repository. A German clone is available in `WHY_DE.md`.

## Problem

Many local AI builder setups are either too loose or too risky.
They write back into source material too easily, mix experimentation with real project state, and assume users are comfortable starting from a terminal-heavy workflow.

## Chosen approach

This repository uses a local GUI-first builder model with three deliberate decisions:

1. the source path stays read-only
2. reviewed output goes only into a sandbox
3. the first experience is guided through a small setup wizard and then a browser UI

## Why this approach

I wanted a builder workflow that is useful for real local work without normalizing unsafe direct writes into the source.
The read-only source boundary forces separation between "what already exists" and "what is being tried".
The sandbox makes experimentation cheap while keeping the original project stable.

I also chose a GUI-first entry because many local users and small teams need a visible working surface before they need a deeper operator path.
The wizard exists to reduce first-run friction and to make the setup state explicit instead of hidden.

The default runtime stays CPU-safe on purpose.
A portable baseline is more valuable here than assuming stronger hardware from day one.

## Why not the obvious alternative

I did not want:

- direct writes into the mounted source repo
- a terminal-only first impression
- a hardware-hungry default setup
- a builder stack that behaves like a knowledge system

Those choices would have made the stack look more powerful at first glance, but less disciplined and less portable.

## Trade-off

This design is slower and more constrained than a looser setup.
The user has to accept an extra boundary and an extra review step.
That is intentional.

## What I would improve next

If I extended this further, I would make the design reasoning even more visible in the repo itself:
why the repo-bridge exists, why the sandbox is mandatory, and where the builder boundary stops.
