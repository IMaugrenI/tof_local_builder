# Target Repo Structure v1

## Goal

The repository should feel like one clean product while keeping internal responsibilities separated.

## Target tree

```text
tof_local_builder/
  app/
    orchestration/
    tools/
    ui/
    wizard/
  config/
    defaults/
    profiles/
  docs/
    00_product/
    01_architecture/
    02_runtime/
    03_tools/
    04_runbooks/
    05_migration/
  engines/
    tof_local_knowledge/
  runtime/
    compose.light.yml
    compose.grounded.yml
  scripts/
    bootstrap.sh
    start_light.sh
    start_grounded.sh
    check_light.sh
    check_grounded.sh
    repair.sh
  services/
    host_reader/
    sandbox_writer/
    tool_gateway/
  sandbox/
    workspace/
    output/
  .runtime/
```

## Top-level interpretation

### app/
Builder-facing orchestration, wizard logic, UI-facing contracts, and tool-facing glue.

### config/
Persistent product settings, defaults, mode profiles, and later user-written config.

### docs/
Clean public and internal project guidance in one place.

### engines/
Heavy internal engines that should not become the visible product face.
The knowledge engine belongs here.

### runtime/
Official compose and runtime entry files.
Only these files should define product-facing runtime truth.

### scripts/
Short operational entrypoints for humans.
No giant monolithic all-in-one script should remain the only truth.

### services/
Small service boundaries for reader, writer, tool gateway, and later related runtime helpers.

## Non-goals

This target structure is not intended to erase all legacy files in one step.
Instead it provides the new official shape that legacy paths can gradually yield to.
