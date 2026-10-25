# Release checklist

Use this before calling a public release good enough for normal users.

## B8/K8: prepare candidate package only (not acceptance)

A source distribution candidate can be built manually without adding a new
application startup route:

```bash
python scripts/build_source_candidate.py --output-dir dist
```

Or use the **Source distribution candidate** GitHub Actions workflow, started
manually (`workflow_dispatch`). It uploads a ZIP made from the committed Git
tree plus `CHECKSUMS.sha256`. The candidate includes existing Windows, Linux,
and macOS start scripts and bilingual offline guides at
`docs/RELEASE_PACKAGE_DE.md` and `docs/RELEASE_PACKAGE.md`.

**This is packaging, not a public GitHub Release.** Do not tag or publish the
candidate as a stable release before the agreed joint repository acceptance.
The existing first-run/runtime, platform and security items below are still
open acceptance evidence, not satisfied by packaging CI.

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
