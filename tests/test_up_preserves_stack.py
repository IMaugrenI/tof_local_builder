from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace

from tof_cli.commands import up


def test_up_uses_existing_compose_stack_without_down(monkeypatch):
    """A normal start must not stop an existing workspace first."""
    calls = []
    monkeypatch.setattr(up, "ensure_env_file", lambda: None)
    monkeypatch.setattr(up, "ensure_directories", lambda paths: None)
    monkeypatch.setattr(up, "read_env", lambda: {"BUILDER_OPEN_BROWSER": "0"})
    monkeypatch.setattr(up, "detect_platform", lambda: SimpleNamespace())
    monkeypatch.setattr(
        up, "builder_compose_profile",
        lambda env, platform: SimpleNamespace(files=[Path("compose.yml")], mode="cpu"),
    )
    monkeypatch.setattr(up, "docker_exists", lambda: True)
    monkeypatch.setattr(up, "docker_reachable", lambda: True)
    monkeypatch.setattr(up, "compose_file_args", lambda files: ["-f", str(files[0])])

    def fake_compose(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(up, "run_docker_compose", fake_compose)
    args = argparse.Namespace(skip_wizard=True, skip_model_ensure=True)

    assert up.handle(args) == 0
    assert calls == [["-f", "compose.yml", "up", "-d", "--build"]]
    assert up.handle(args) == 0
    assert calls == [
        ["-f", "compose.yml", "up", "-d", "--build"],
        ["-f", "compose.yml", "up", "-d", "--build"],
    ]


def test_failed_up_returns_failure_without_stop(monkeypatch):
    calls = []
    monkeypatch.setattr(up, "ensure_env_file", lambda: None)
    monkeypatch.setattr(up, "ensure_directories", lambda paths: None)
    monkeypatch.setattr(up, "read_env", lambda: {})
    monkeypatch.setattr(up, "detect_platform", lambda: SimpleNamespace())
    monkeypatch.setattr(
        up, "builder_compose_profile",
        lambda env, platform: SimpleNamespace(files=[Path("compose.yml")], mode="cpu"),
    )
    monkeypatch.setattr(up, "docker_exists", lambda: True)
    monkeypatch.setattr(up, "docker_reachable", lambda: True)
    monkeypatch.setattr(up, "compose_file_args", lambda files: ["-f", str(files[0])])

    def fake_compose(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=17)

    monkeypatch.setattr(up, "run_docker_compose", fake_compose)
    assert up.handle(argparse.Namespace(skip_wizard=True, skip_model_ensure=True)) == 17
    assert len(calls) == 1
    assert "down" not in calls[0]
