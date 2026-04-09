# tof_local_builder

> English is the primary text in this repository. A German clone is available in `README_DE.md`.

Local AI builder for controlled work on one machine or in a small local team.

I built this repo to keep source access read_only, output sandboxed, and the workflow easy to start.

## start_here

Primary runtime entrypoint:

```bash
python run.py setup
python run.py up
python run.py check
```

Additional runtime commands:

```bash
python run.py status
python run.py doctor
python run.py down
```

## cross_platform_wrappers

The supported runtime truth is `python run.py ...`.

Supported convenience wrappers:

- Linux: `scripts/setup.sh`, `scripts/up.sh`, `scripts/check.sh`, `scripts/down.sh`, `scripts/status.sh`, `scripts/doctor.sh`
- Windows PowerShell: `scripts/setup.ps1`, `scripts/up.ps1`, `scripts/check.ps1`, `scripts/down.ps1`, `scripts/status.ps1`, `scripts/doctor.ps1`
- macOS command launchers: `scripts/setup.command`, `scripts/up.command`, `scripts/check.command`, `scripts/down.command`, `scripts/status.command`, `scripts/doctor.command`

Examples:

```bash
./scripts/setup.sh
pwsh ./scripts/setup.ps1
./scripts/setup.command
```

After startup, open `http://localhost:3000` and connect the tool server at `http://127.0.0.1:8099`.

## what_this_repo_does

1. runs local models through Ollama
2. exposes a browser GUI through Open WebUI
3. reads a mounted source path as read_only
4. writes reviewed artifacts only into a local sandbox
5. uses a first_run wizard to guide setup and model choice
6. stays CPU_safe by default, with optional later acceleration

## boundary

1. the source repo stays read_only
2. writes stay limited to `sandbox/workspace` and `sandbox/output`
3. this is a builder stack, not a general knowledge system
4. local use comes first

## key_runtime_parts

- `run.py`
- `tof_cli/`
- `compose.yml`
- `.env.example`
- `docs/13_python_cli_runtime.md`
- `services/repo_bridge/`
- `scripts/wizard.py`

## related_public_repos

- [`tof_local_knowledge`](https://github.com/IMaugrenI/tof_local_knowledge) — local document indexing and grounded answers
- [`tof_showcase`](https://github.com/IMaugrenI/tof-showcase) — public architecture entry point
- [`tof_v7_public_frame`](https://github.com/IMaugrenI/tof-v7-public-frame) — reduced V7 boundary frame
