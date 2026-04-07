# Legacy to New Mapping v1

## Purpose

This map explains how current builder-era files should yield to the new cleaner structure over time.

## Current builder-era truth

- `scripts/setup.sh`
- `scripts/start.sh`
- `scripts/up.sh`
- `scripts/check.sh`
- `scripts/compose_wrapper.sh`
- `compose.yml`
- `compose.host_bridge.yml`
- `services/repo_bridge/`
- multiple wizard-related files in `scripts/`

## New target truth

### Start and repair surface
- `scripts/bootstrap.sh`
- `scripts/start_light.sh`
- `scripts/start_grounded.sh`
- `scripts/check_light.sh`
- `scripts/check_grounded.sh`
- `scripts/repair.sh`

### Runtime surface
- `runtime/compose.light.yml`
- `runtime/compose.grounded.yml`

### Service boundaries
- `services/host_reader/`
- `services/sandbox_writer/`
- `services/tool_gateway/`

### Product logic and orchestration
- `app/wizard/`
- `app/tools/`
- `app/orchestration/`

### Engine space
- `engines/tof_local_knowledge/`

## Migration intent

### setup.sh
Should yield to `bootstrap.sh` over time.

### up.sh and start.sh
Should yield to `start_light.sh` and `start_grounded.sh` over time.

### check.sh
Should yield to `check_light.sh` and `check_grounded.sh` over time.

### compose.yml and compose.host_bridge.yml
Should yield to `runtime/compose.light.yml` and `runtime/compose.grounded.yml` over time.

### repo_bridge as one mixed surface
Should yield to separate host reader, sandbox writer, and gateway-facing layers over time.

### multiple wizard layers
Should yield to one official wizard surface backed by internal helper modules.
