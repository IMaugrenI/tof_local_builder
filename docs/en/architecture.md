# Architecture

## Purpose

`tof_local_builder` is a small local stack for code-focused work without heavy dependence on cloud token budgets.

## Core parts

### 1. Ollama
Runs local models and exposes an API on port `11434`.

### 2. Open WebUI
Provides a browser UI and talks to the local Ollama instance.

### 3. Prompt library
Stores reusable work patterns such as repo audits, drift checks, and implementation tasks.

### 4. Editor profiles
Starter configuration for tools that can work with local models.

## Flow

```text
User
  -> Open WebUI / Aider / Continue
  -> Ollama
  -> local model
  -> answer / patch / audit output
```

## Why this shape

- easy to start on one machine
- easy to inspect
- easy to replace later
- few moving parts

## Languages

- English: `docs/en/`
- German: `docs/de/`

## Later expansion

Possible next layers:
- local embeddings + RAG
- repo watcher
- patch/review worker
- local document ingest
- optional GPU host split
