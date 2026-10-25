from __future__ import annotations

from tof_cli.builder import task_ops
from tof_cli.ui import app


def test_preferred_models_respect_existing_task_catalog():
    installed = {"qwen2.5:0.5b", "qwen2.5-coder:1.5b", "qwen2.5-coder:0.5b"}
    code = task_ops.preferred_installed_models("code", installed)
    assert code == ["qwen2.5-coder:0.5b", "qwen2.5-coder:1.5b"]
    assert "qwen2.5:0.5b" not in code
    assert task_ops.preferred_installed_models("analysis", installed) == ["qwen2.5:0.5b"]


def test_task_guide_contains_preferred_installed_models(monkeypatch, tmp_path):
    source = tmp_path / "source"
    sandbox = tmp_path / "sandbox"
    source.mkdir()
    sandbox.mkdir()
    (source / "README.md").write_text("# Sample", encoding="utf-8")
    (source / "pkg").mkdir()
    (source / ".private").write_text("not listed", encoding="utf-8")
    monkeypatch.setattr(task_ops, "ollama_tags", lambda _: [
        "qwen2.5:0.5b", "qwen2.5-coder:0.5b"
    ])
    guide = task_ops.task_guide({
        "SOURCE_REPO_PATH": str(source), "BUILDER_SANDBOX_PATH": str(sandbox),
    })
    assert guide["preferred_models"]["code"] == ["qwen2.5-coder:0.5b"]
    assert guide["preferred_models"]["analysis"] == ["qwen2.5:0.5b"]
    project = guide["project"]
    assert project["source_name"] == "source"
    assert project["read_only"] is True
    assert {"name": "README.md", "kind": "file"} in project["top_level"]
    assert not any(row["name"] == ".private" for row in project["top_level"])


def test_project_snapshot_rejects_overlapping_paths(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "nested").mkdir()
    report = task_ops.project_snapshot({
        "SOURCE_REPO_PATH": str(source),
        "BUILDER_SANDBOX_PATH": str(source / "nested"),
    })
    assert report["source_state"] == "overlapping_paths"
    assert report["top_level"] == []


def test_snapshot_is_bounded_to_first_level(tmp_path):
    source = tmp_path / "repo"
    source.mkdir()
    for number in range(28):
        (source / f"file{number}.txt").write_text(str(number), encoding="utf-8")
    report = task_ops.project_snapshot({"SOURCE_REPO_PATH": str(source)})
    assert len(report["top_level"]) <= 24
    assert report["truncated"] is True


def test_ui_reuses_task_guide_without_model_installation():
    assert "renderProjectContext" in app.HTML
    assert "guide.preferred_models" in app.HTML
    assert "Suggested for this task" in app.HTML
    assert "Copy &amp; open workspace" in app.HTML
