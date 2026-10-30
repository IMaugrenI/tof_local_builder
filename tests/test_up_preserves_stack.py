"""A normal Builder start preserves existing Compose services and reuses the native UI."""
from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace

from tof_cli.commands import up


def configure_fake_runtime(monkeypatch, *, returncode=0):
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
    monkeypatch.setattr(
        up, "run_docker_compose",
        lambda args, **kwargs: calls.append(args) or SimpleNamespace(returncode=returncode),
    )
    return calls


def test_up_uses_existing_compose_stack_without_down(monkeypatch):
    calls = configure_fake_runtime(monkeypatch)
    ui_calls = []
    monkeypatch.setattr(
        up, "ensure_builder_ui",
        lambda env: ui_calls.append(env) or (True, "http://127.0.0.1:8795"),
    )
    args = argparse.Namespace(skip_wizard=True, skip_model_ensure=True)
    assert up.handle(args) == 0
    assert up.handle(args) == 0
    assert calls == [
        ["-f", "compose.yml", "up", "-d", "--build"],
        ["-f", "compose.yml", "up", "-d", "--build"],
    ]
    assert len(ui_calls) == 2
    assert not any("down" in command for command in calls)


def test_failed_compose_up_never_stops_running_services(monkeypatch):
    calls = configure_fake_runtime(monkeypatch, returncode=17)
    monkeypatch.setattr(up, "ensure_builder_ui", lambda env: (True, "http://127.0.0.1:8795"))
    assert up.handle(argparse.Namespace(skip_wizard=True, skip_model_ensure=True)) == 17
    assert len(calls) == 1
    assert "down" not in calls[0]
