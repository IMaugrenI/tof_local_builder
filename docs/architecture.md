# Architecture

## Intent

`tof_local_builder` is a small local stack for code-focused work without depending on cloud token budgets.

## Baseline components

### 1. Ollama
Runs local models and exposes an API on port `11434`.

### 2. Open WebUI
Provides a browser UI that talks to the local Ollama instance.

### 3. Prompt library
Stores repeatable work patterns such as repo audits, drift checks, and implementation tasks.

### 4. Editor profiles
Starter configuration for tools that can talk to local models.

## Flow

```text
User
  -> Open WebUI / Aider / Continue
  -> Ollama
  -> local model
  -> answer / patch / audit output
```

## Why this shape

- easy to run on one machine
- easy to inspect
- easy to replace pieces later
- minimal moving parts

## Future expansion

Possible next layers:
- local embeddings + RAG
- repo watcher
- patch/review worker
- local document ingest
- optional GPU host split
