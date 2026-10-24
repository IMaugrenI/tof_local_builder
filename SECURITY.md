# Security

`tof_local_builder` is local-first, but it can read source code and write generated artifacts. Treat local paths and generated output as sensitive.

## Normal mode

The supported beginner/default path uses the containerized repo bridge:

- the selected source is mounted read-only
- writes are restricted to `sandbox/workspace` and `sandbox/output`
- browser-facing services bind to `127.0.0.1` by default

Do not change the bind host to a LAN/public address unless you understand the exposure.

## Advanced host-reader mode

The optional host reader accepts absolute local paths and can read files/directories available to the host user running it.

That means:

- it is more powerful than the normal selected-source model
- it should only be used on a trusted local machine
- it should remain bound to `127.0.0.1`
- it must not be exposed directly to the internet
- do not point it at secrets or unrelated private directories unless you explicitly intend to read them

## Secrets and public reports

Do not commit or publish:

- `.env`
- API keys or tokens
- private source repositories
- private local paths if they reveal sensitive information
- generated output containing secrets
- Open WebUI data directories
- Ollama model/runtime data

For security-sensitive findings, use GitHub private vulnerability reporting where available rather than a public issue.
