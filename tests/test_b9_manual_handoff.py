"""Final Builder workflow: verified read-only handoff after review."""
from __future__ import annotations

import pytest

from tof_cli.builder import artifact_ops
from tof_cli.ui import app


@pytest.fixture
def roots(tmp_path):
    src = tmp_path / "source"
    sandbox = tmp_path / "sandbox"
    src.mkdir()
    (sandbox / "workspace").mkdir(parents=True)
    (sandbox / "output").mkdir()
    return src, sandbox, {"SOURCE_REPO_PATH": str(src), "BUILDER_SANDBOX_PATH": str(sandbox)}


def token(env, area="output", path="page.py"):
    return next(item["review_token"] for item in artifact_ops.artifact_inventory(env)["items"]
                if item["area"] == area and item["path"] == path)


def test_modified_file_handoff_is_complete_diff_and_source_stays_untouched(roots):
    src, sandbox, env = roots
    (src / "page.py").write_text("value = 1\n", encoding="utf-8")
    (sandbox / "output" / "page.py").write_text("value = 2\n", encoding="utf-8")
    handoff = artifact_ops.artifact_handoff(env, "output", "page.py", token(env))
    assert handoff["kind"] == "unified_diff"
    assert "-value = 1" in handoff["content"]
    assert "+value = 2" in handoff["content"]
    assert handoff["requires_manual_adoption"] is True
    assert handoff["read_only"] is True
    assert (src / "page.py").read_text(encoding="utf-8") == "value = 1\n"


def test_new_file_can_only_be_copied_as_small_text(roots):
    _, sandbox, env = roots
    (sandbox / "output" / "page.py").write_text("new file", encoding="utf-8")
    result = artifact_ops.artifact_handoff(env, "output", "page.py", token(env))
    assert result["kind"] == "new_file_text"
    assert result["content"] == "new file"


def test_changed_content_invalidates_review_token(roots):
    src, sandbox, env = roots
    (src / "page.py").write_text("old", encoding="utf-8")
    generated = sandbox / "output" / "page.py"
    generated.write_text("first", encoding="utf-8")
    expected = token(env)
    generated.write_text("second", encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        artifact_ops.artifact_handoff(env, "output", "page.py", expected)


def test_unbounded_and_unsafe_files_cannot_be_handed_off(roots):
    src, sandbox, env = roots
    (sandbox / "output" / "page.py").write_text("generated", encoding="utf-8")
    expected = token(env)
    for path in ["../page.py", "/tmp/page.py", "binary.png"]:
        with pytest.raises(ValueError):
            artifact_ops.artifact_handoff(env, "output", path, expected)
    (src / "page.py").write_text("a" * (artifact_ops.MAX_PREVIEW_BYTES + 1),
                                encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        artifact_ops.artifact_handoff(env, "output", "page.py", expected)


def test_ui_does_not_apply_generated_files():
    assert "Copy reviewed handoff" in app.HTML
    assert "reviewedTokens.has(token)" in app.HTML
    assert "navigator.clipboard.writeText(data.content)" in app.HTML
    assert "Original source unchanged." in app.HTML


def test_source_edit_invalidates_review_approval(roots):
    source, sandbox, env = roots
    original = source / "page.py"
    original.write_text("old", encoding="utf-8")
    (sandbox / "output" / "page.py").write_text("generated", encoding="utf-8")
    previous = token(env)
    original.write_text("modified after review", encoding="utf-8")
    assert token(env) != previous
    with pytest.raises(ValueError, match="changed"):
        artifact_ops.artifact_handoff(env, "output", "page.py", previous)


def test_binary_utf8_payload_disallowed_even_when_file_suffix_is_text(roots):
    _, sandbox, env = roots
    (sandbox / "output" / "page.py").write_bytes(bytes([104, 101, 108, 108, 111, 0, 119, 111, 114, 108, 100]))
    with pytest.raises(ValueError, match="Binary"):
        artifact_ops.artifact_handoff(env, "output", "page.py", token(env))
