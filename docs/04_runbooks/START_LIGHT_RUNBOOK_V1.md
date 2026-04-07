# Start Light Runbook v1

## Purpose

This is the clean light-mode operational entry path.

## Intended runtime pieces

- host-native reader
- sandbox writer
- Ollama
- Open WebUI
- no knowledge database required

## Recommended human entry command

```bash
bash scripts/start_light.sh
```

## Intended behavior

1. ensure config and runtime folders exist
2. ensure the host-native reader is available
3. start the light runtime compose stack from `runtime/compose.light.yml`
4. expose the correct tool server URL for Open WebUI
5. open or point the user to Open WebUI

## Tool expectation

The user should only need to work with a selected source path and a selected output path.
Internal root naming should not leak into the product UX.
