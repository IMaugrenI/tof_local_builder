from __future__ import annotations

import pytest

from tof_cli.builder import task_ops


def test_catalog_coding_models_reuse_existing_catalog():
    tags = [entry["tag"] for entry in task_ops._suggestions("code")]
    assert "qwen2.5-coder:0.5b" in tags
    assert "qwen2.5:0.5b" not in tags


def test_unknown_task_is_rejected():
    with pytest.raises(ValueError):
        task_ops._suggestions("untrusted")


def test_task_options_report_installed_not_only_recommended(monkeypatch):
    monkeypatch.setattr(task_ops, "ollama_tags", lambda _: ["qwen2.5-coder:0.5b"])
    result = task_ops.task_options("code", {"OLLAMA_PORT": "11434"})
    assert result["installed_models"] == ["qwen2.5-coder:0.5b"]
    assert any(row["installed"] for row in result["models"])


def test_prepare_task_is_read_only_and_needs_installed_model(monkeypatch, tmp_path):
    source = tmp_path / "source"
    sandbox = tmp_path / "sandbox"
    source.mkdir()
    sandbox.mkdir()
    monkeypatch.setattr(task_ops, "ollama_tags", lambda _: ["qwen2.5-coder:0.5b"])
    monkeypatch.setattr(task_ops, "source_repo_report",
                        lambda env: {"state": "ok", "path": str(source)})
    monkeypatch.setattr(task_ops, "sandbox_report",
                        lambda env: {"state": "ok", "path": str(sandbox)})

    result = task_ops.prepare_task(
        "code", "qwen2.5-coder:0.5b", "Review the README",
        {"OLLAMA_PORT": "11434"},
    )
    assert result["writes_performed"] is False
    assert result["model_changed"] is False
    assert "Do not edit" in result["prompt"]
    with pytest.raises(ValueError):
        task_ops.prepare_task("code", "not-installed", "Do something", {})


def test_source_sandbox_overlap_is_rejected(monkeypatch, tmp_path):
    monkeypatch.setattr(task_ops, "ollama_tags", lambda _: ["local:1b"])
    monkeypatch.setattr(task_ops, "source_repo_report",
                        lambda env: {"state": "ok", "path": str(tmp_path)})
    monkeypatch.setattr(task_ops, "sandbox_report",
                        lambda env: {"state": "ok", "path": str(tmp_path / "out")})
    with pytest.raises(ValueError):
        task_ops.prepare_task("analysis", "local:1b", "Check something", {})
