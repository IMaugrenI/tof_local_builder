# Web GUiX freeze v0.2

## Scope

This freeze covers only the staged web GUiX setup and handoff path:

- fresh clone of the repository
- `bash scripts/up_guix.sh`
- setup page at `http://127.0.0.1:3011`
- host-aware setup detection via host snapshot
- save of source path, model and acceleration
- runtime handoff to `open-webui`
- green `bash scripts/check_guix.sh`

## Acceptance baseline

The frozen baseline is considered met when all of the following are true:

1. `setup-web` starts and is reachable on `3011`
2. the setup page accepts a valid host path
3. host detection in the web setup is based on the host snapshot instead of container-local capability guessing
4. the runtime starts after the setup is saved
5. `repo-bridge-v2` becomes healthy
6. `open-webui` becomes reachable and healthy
7. the handoff continues cleanly to Open WebUI
8. `bash scripts/check_guix.sh` turns green

## Explicitly out of scope

This freeze does **not** yet claim:

- full Open WebUI tool-server validation
- full write E2E validation through the chat surface
- broader release guarantees outside the setup and handoff path

## Notes from the frozen run

- first boot may take longer because Open WebUI can download embedding/runtime assets on the cold path
- during that cold start, an early health check can still fail before the final healthy state appears
- this does not break the freeze as long as the stack converges to healthy and the setup handoff succeeds afterwards

## Intent

This freeze is meant to preserve the current stable behavior of the web GUiX onboarding path before the next feature cycle starts.
