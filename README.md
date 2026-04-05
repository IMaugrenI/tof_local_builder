# tof_local_builder

> English is the primary text in this repository. A German clone is available in `README_DE.md`.

Local AI builder for controlled work on one machine or in a small local team.

I built this repo to keep source access read_only, output sandboxed, and the workflow easy to start.

## start_here

```bash
bash scripts/setup.sh
bash scripts/up.sh
bash scripts/check.sh
```

After startup, open `http://localhost:3000` and connect the tool server at `http://127.0.0.1:8099`.

## what_this_repo_does

1. runs local models through Ollama
2. exposes a browser GUI through Open WebUI
3. reads a mounted source path as read_only
4. writes reviewed artifacts only into a local sandbox
5. uses a first_run wizard to guide setup and model choice
6. stays CPU_safe by default, with optional later acceleration

## what_this_shows

1. hands_on Linux and Docker work
2. clear source_vs_output boundaries
3. product_minded local workflow design
4. practical repo and documentation discipline
5. controlled experimentation without direct source writes

## boundary

1. the source repo stays read_only
2. writes stay limited to `sandbox/workspace` and `sandbox/output`
3. this is a builder stack, not a general knowledge system
4. local use comes first

## key_runtime_parts

- `ollama` = local model runtime
- `open-webui` = browser GUI
- `repo-bridge` = controlled read_write boundary for source and sandbox
- `wizard.py` = one_time local setup guide before web handoff

## key_files

- `compose.yml`
- `.env.example`
- `scripts/setup.sh`
- `scripts/up.sh`
- `scripts/check.sh`
- `scripts/down.sh`
- `scripts/wizard.py`
- `docs/product/START_HERE.md`
- `docs/product/WHY.md`
- `docs/repo_bridge.md`
- `services/repo_bridge/`

## related_public_repos

- [`tof_local_knowledge`](https://github.com/IMaugrenI/tof_local_knowledge) — local document indexing and grounded answers
- [`tof_showcase`](https://github.com/IMaugrenI/tof-showcase) — public architecture entry point
- [`tof_v7_public_frame`](https://github.com/IMaugrenI/tof-v7-public-frame) — reduced V7 boundary frame
