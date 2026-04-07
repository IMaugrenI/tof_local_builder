# Start Grounded Runbook v1

## Purpose

This is the clean grounded-mode operational entry path.

## Intended runtime pieces

- everything from light mode
- knowledge engine services
- Postgres-backed evidence runtime
- grounded search and QA paths

## Recommended human entry command

```bash
bash scripts/start_grounded.sh
```

## Intended behavior

1. ensure config and runtime folders exist
2. ensure the host-native reader is available
3. start the grounded runtime compose stack from `runtime/compose.grounded.yml`
4. expose the correct tool server and grounded service URLs
5. allow the builder-facing orchestration layer to route grounded questions to the knowledge engine

## Product rule

The user should still experience one builder product surface.
Grounded mode must not become a second visible product identity.
