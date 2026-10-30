# Product Constitution v2 — Native Builder Experience

Supersedes [v1](PRODUCT_CONSTITUTION_V1.md) for new development. Operator decision: 2026-10-30. Development state, not a certified release.

## Product identity and simplicity

`tof_local_builder` is one standalone local application. Users start it, describe development work, and review consequential results. The interface must hide routine technical work; users are not expected to administer containers, ports, model APIs, or shell commands.

- One supported Python CLI + repository-defined Docker Compose startup path.
- One existing first-run wizard; one native Builder workspace UI.
- Open WebUI is **not** part of the product or runtime.
- Continue reusing the existing `tof_cli/` and `services/repo_bridge/` components.
- No second backend stack or product repo created to replace the UI.

## Local models and work

Ollama serves installed local LLMs. The Builder UI talks to Ollama via a bounded local adapter. Tool execution must not follow directly from untrusted model output: planning, command selection, capability checks, execution and results must be distinct steps.

Work should evolve from read-only advice to supervised, bounded task execution. Each proposed operation must specify its target, side effects, permissions, and result. The user reviews consequential decisions; routine authorized technical work may be automated.

The integrated chat endpoint is planning-only. The separate user-triggered sandbox build runs a finite inspect → plan → generate workflow with explicit limits and a job journal. It writes reviewable text drafts only under sandbox/output using the existing Repo Bridge. It is **not** unrestricted autonomous development; shell tests, Git commits and source application are not automated. Never claim source files have been modified or tests run merely because a model produced text.

## Source and sandbox

Selected source is read-only. Generated output may be written only within the separately configured sandbox. Compare/preview/review workflows remain mandatory for manual adoption. No implicit apply, commit, push, delete, or privileged host command.

Existing path traversal, symlink and root separation guarantees remain binding. Unknown or unsafe actions fail closed.

## Runtime and recovery

The Builder shall automatically inspect readiness, start its own allowed services, select suitable installed local models and show understandable next steps. Operations requiring elevated privileges, installations, external connections, changes to running systems or other safety decisions require explicit operator consent.

The current Python `run.py` CLI and Compose stack remain authoritative. Avoid destructive restarts. Existing Open WebUI volumes remain untouched during transition; orphan containers require a separate operator decision.

Persist planned tasks; allow explicit continuation only after validating project binding, saved plan, original source/context hashes and previously generated draft hashes. Never silently resume or repeat side effects. If a journal write was interrupted after a sandbox draft was created, the unexpected draft must block replay and be reviewed manually. Cancelling stops before the next file operation, not mid-model-call.

## Integration boundaries

Knowledge and Organizer remain independent products. The optional Knowledge adapter uses the separately hosted local search API on loopback; each search requires a deliberate user request and privacy confirmation. It returns bounded indexed excerpt references to the UI only, not to the model, job journal or generated file context. A separate Organizer integration remains disabled until its data-sharing contract and consent boundaries are explicitly defined. Retrieved knowledge is context, not trusted instructions.

## Release evidence

Code-level tests on GitHub are development evidence only. DOM performs target-system acceptance, including actual runtime, model availability and user workflow, before GO/NO-GO.
