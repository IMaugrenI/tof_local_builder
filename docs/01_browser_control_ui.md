# Browser control UI

`tof_local_builder` now includes a simple local browser control UI.

## Start it

```bash
python run.py ui
```

By default this starts a local server on `127.0.0.1:8795` and opens the browser.

## What it is for

This UI is a simple front door for normal users who do not want to begin with raw terminal commands.

It currently exposes large buttons for:

- prepare local setup
- start builder stack
- check services
- show runtime status
- run doctor
- stop stack

It also exposes direct local links for:

- Open WebUI
- repo bridge health
- Ollama endpoint

## What it is not

This is not the full builder workspace itself.

It is a safe local control surface for the main runtime steps and a jump-off point into the real local builder environment.

## Suggested user path

1. prepare local setup
2. start builder stack
3. check services
4. open WebUI
5. use the repo bridge or Ollama links only when needed for diagnosis or advanced checks
