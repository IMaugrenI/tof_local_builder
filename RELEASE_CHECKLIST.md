# Release checklist

Use this before calling a public release good enough for normal users.

## Basic repo checks

- README still matches the real start path
- `INSTALL_AND_FIRST_TEST.md` still matches the real start path
- `docs/00_beginner_quickstart.md` still matches the browser UI
- no private or local test data is committed

## Smoke path

- fresh local clone works
- `scripts/start_here.*` works on the intended platform
- stack starts
- browser UI opens
- readiness cards reflect reality
- WebUI opens
- repo bridge responds
- Ollama responds when expected

## User-facing truth

- the next-step hint still matches reality
- WebUI is clearly the main path when ready
- diagnostics are understandable enough for a normal user

## Final rule

If a normal first-time user still needs to guess whether the stack is ready or where to go next, the release is not ready enough.
