from pathlib import Path

import pytest
from fastapi import HTTPException

from services.repo_bridge.app import main as bridge


@pytest.fixture()
def sandbox_roots(tmp_path, monkeypatch):
    source = tmp_path / "source"
    sandbox = tmp_path / "sandbox"
    workspace = sandbox / "workspace"
    output = sandbox / "output"
    outside = tmp_path / "outside"
    for path in (source, workspace, output, outside):
        path.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(bridge, "SOURCE_ROOT", source.resolve())
    monkeypatch.setattr(bridge, "SANDBOX_ROOT", sandbox.resolve())
    monkeypatch.setattr(bridge, "WORKSPACE_ROOT", workspace.resolve())
    monkeypatch.setattr(bridge, "OUTPUT_ROOT", output.resolve())
    return source, workspace, output, outside


def test_write_path_stays_inside_workspace(sandbox_roots):
    _, workspace, _, _ = sandbox_roots
    base, target = bridge.resolve_write_path("workspace", "notes/result.md")
    assert base == workspace.resolve()
    assert target == (workspace / "notes/result.md").resolve()


def test_parent_escape_is_rejected(sandbox_roots):
    with pytest.raises(HTTPException):
        bridge.resolve_write_path("workspace", "../../outside.txt")


def test_symlink_escape_is_rejected(sandbox_roots):
    _, workspace, _, outside = sandbox_roots
    link = workspace / "linked"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks are unavailable in this environment")

    with pytest.raises(HTTPException):
        bridge.resolve_write_path("workspace", "linked/escape.txt")


def test_source_root_is_not_writable(sandbox_roots):
    with pytest.raises(HTTPException):
        bridge.resolve_write_path("source", "should-not-write.txt")
