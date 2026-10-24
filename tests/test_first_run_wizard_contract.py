from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "builder_bootstrap.py"
SPEC = importlib.util.spec_from_file_location("tof_local_builder_bootstrap", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)


def test_placeholder_source_requires_first_run_wizard():
    env = {
        "BUILDER_SETUP_DONE": "0",
        "SOURCE_REPO_PATH": "/absolute/path/to/the/source/repo",
        "HOST_UID": "1000",
        "HOST_GID": "1000",
    }
    assert bootstrap.needs_first_run_wizard(env) is True
    assert bootstrap.source_path_valid(env["SOURCE_REPO_PATH"]) is False


def test_existing_source_can_complete_setup(tmp_path):
    env = {
        "BUILDER_SETUP_DONE": "0",
        "SOURCE_REPO_PATH": "/absolute/path/to/the/source/repo",
        "HOST_UID": "1000",
        "HOST_GID": "1000",
    }
    configured = bootstrap.apply_setup_values(
        env,
        source_repo_path=str(tmp_path),
        default_model="qwen2.5:0.5b",
        acceleration="cpu",
        open_browser=True,
    )
    assert configured["BUILDER_SETUP_DONE"] == "1"
    assert Path(configured["SOURCE_REPO_PATH"]) == tmp_path.resolve()
    assert configured["BUILDER_OPEN_BROWSER"] == "1"
