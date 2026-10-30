from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException


MODULE_PATH = Path(__file__).resolve().parents[1] / "services" / "repo_bridge" / "app" / "main.py"
SPEC = importlib.util.spec_from_file_location("tof_local_builder_repo_bridge_main", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)


@pytest.fixture()
def sandbox_roots(tmp_path, monkeypatch):
    source = tmp_path / "source"
    sandbox = tmp_path / "sandbox"
    workspace = sandbox / "workspace"
    output = sandbox / "output"
    outside = tmp_path / "outside"
    for item in (source, workspace, output, outside):
        item.mkdir(parents=True, exist_ok=True)

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


@pytest.mark.parametrize(
    "relative_path",
    ["/tmp/absolute.txt", "C:/Windows/system.ini", "C:relative.txt", "../escape", r"..\\escape"],
)
def test_ambiguous_or_absolute_write_paths_are_rejected(sandbox_roots, relative_path):
    with pytest.raises(HTTPException) as exc:
        bridge.resolve_write_path("output", relative_path)
    assert exc.value.status_code == 400


@pytest.mark.parametrize("relative_path", ["/etc/passwd", "C:/Windows", "../outside"])
def test_tree_paths_reject_absolute_and_parent_segments(sandbox_roots, relative_path):
    with pytest.raises(HTTPException) as exc:
        bridge.resolve_tree_path("source", relative_path)
    assert exc.value.status_code == 400


def test_tree_root_remains_browsable(sandbox_roots):
    source, _, _, _ = sandbox_roots
    path, relative = bridge.resolve_tree_path("source", "")
    assert path == source.resolve()
    assert relative == ""


def test_source_and_sandbox_must_not_overlap(sandbox_roots, monkeypatch):
    source, _, _, _ = sandbox_roots
    monkeypatch.setattr(bridge, "SANDBOX_ROOT", (source / "sandbox").resolve())
    with pytest.raises(HTTPException) as exc:
        bridge.resolve_write_path("output", "note.md")
    assert exc.value.status_code == 503


def test_symlink_alias_inside_workspace_is_rejected(sandbox_roots):
    _, workspace, _, _ = sandbox_roots
    target = workspace / "real"
    target.mkdir()
    alias = workspace / "alias"
    try:
        alias.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("Symlinks are unavailable")
    with pytest.raises(HTTPException) as exc:
        bridge.resolve_write_path("workspace", "alias/generated.md")
    assert exc.value.status_code == 400


def test_non_overwriting_bridge_writer_preserves_existing_artifact(sandbox_roots):
    _, workspace, _, _ = sandbox_roots
    target = workspace / "draft.md"
    target.write_text("original", encoding="utf-8")
    with pytest.raises(HTTPException) as exc:
        bridge.write_internal(SimpleNamespace(
            target_root="workspace", relative_path="draft.md",
            content="new", overwrite=False,
        ))
    assert exc.value.status_code == 409
    assert target.read_text(encoding="utf-8") == "original"
