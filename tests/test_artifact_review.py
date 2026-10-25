from __future__ import annotations

from pathlib import Path

import pytest

from tof_cli.builder import artifact_ops


@pytest.fixture
def configured_paths(tmp_path):
    source = tmp_path / "source"
    sandbox = tmp_path / "sandbox"
    source.mkdir()
    (sandbox / "workspace").mkdir(parents=True)
    (sandbox / "output").mkdir()
    return source, sandbox, {
        "SOURCE_REPO_PATH": str(source),
        "BUILDER_SANDBOX_PATH": str(sandbox),
    }


def test_inventory_lists_only_generated_sandbox_files(configured_paths):
    source, sandbox, env = configured_paths
    (source / "secret.txt").write_text("private", encoding="utf-8")
    (sandbox / "output" / "result.md").write_text("generated", encoding="utf-8")
    (sandbox / "workspace" / "code.py").write_text("print('ok')", encoding="utf-8")
    report = artifact_ops.artifact_inventory(env)
    assert report["status"] == "ok"
    assert sorted((entry["area"], entry["path"]) for entry in report["items"]) == [
        ("output", "result.md"), ("workspace", "code.py")
    ]
    assert all(entry["previewable"] for entry in report["items"])
    assert artifact_ops.artifact_preview(env, "output", "result.md")["content"] == "generated"


@pytest.mark.parametrize("area,path", [
    ("source", "secret.txt"), ("output", "../source/secret.txt"),
    ("output", "/etc/passwd"), ("output", r"C:\\Windows\\win.ini"),
    ("output", ""), ("output", "binary.png"),
])
def test_preview_rejects_invalid_or_non_text_paths(configured_paths, area, path):
    _, _, env = configured_paths
    with pytest.raises(ValueError):
        artifact_ops.artifact_preview(env, area, path)


def test_symlinks_outside_sandbox_are_not_visible(configured_paths, tmp_path):
    _, sandbox, env = configured_paths
    outside = tmp_path / "outside.txt"
    outside.write_text("private", encoding="utf-8")
    link = sandbox / "output" / "outside.md"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("Symlinks not available")
    assert artifact_ops.artifact_inventory(env)["items"] == []
    with pytest.raises(ValueError):
        artifact_ops.artifact_preview(env, "output", "outside.md")


def test_source_and_sandbox_overlap_fail_closed(configured_paths):
    source, _, env = configured_paths
    env["BUILDER_SANDBOX_PATH"] = str(source)
    assert artifact_ops.artifact_inventory(env)["status"] == "unavailable"
    with pytest.raises(ValueError):
        artifact_ops.artifact_preview(env, "output", "foo.md")


def test_preview_rejects_large_file(configured_paths):
    _, sandbox, env = configured_paths
    (sandbox / "output" / "large.md").write_text(
        "a" * (artifact_ops.MAX_PREVIEW_BYTES + 1), encoding="utf-8"
    )
    listing = artifact_ops.artifact_inventory(env)
    assert listing["items"][0]["previewable"] is False
    with pytest.raises(ValueError):
        artifact_ops.artifact_preview(env, "output", "large.md")
