"""Static generated-code validation; no code execution, Docker or Ollama."""
from __future__ import annotations

import json
import threading
from unittest.mock import patch

import pytest

from tof_cli.builder.agent_ops import BuildError, _validate_and_repair
from tof_cli.builder.draft_validation import DraftSyntaxError, check_draft


class InMemoryJournal:
    def __init__(self):
        self.steps = []

    def update(self, job_id, **fields):
        self.steps.append(fields)


@pytest.mark.parametrize(("path", "content", "expected"), [
    ("src/app.py", "answer = 42\n", "python_syntax_ok"),
    ("config/data.json", '{"answer":42}', "json_syntax_ok"),
    ("config/tool.toml", 'answer = 42\n', "toml_syntax_ok"),
    ("src/page.js", "let value = 42;", "not_checked"),
])
def test_static_check_does_not_claim_unsupported_languages(path, content, expected):
    assert check_draft(path, content) == expected


@pytest.mark.parametrize(("path", "content"), [
    ("src/bad.py", "def broken(:\n"),
    ("data/bad.json", '{"missing": }'),
    ("config/bad.toml", "answer = ["),
    ("src/bad.py", "x = '\x00'"),
])
def test_invalid_code_never_passes_a_static_check(path, content):
    with pytest.raises(DraftSyntaxError):
        check_draft(path, content)


def test_one_repair_is_accepted_only_for_matching_path_and_valid_syntax():
    corrected = json.dumps({"path": "src/app.py", "content": "answer = 43\n"})
    journal = InMemoryJournal()
    with patch("tof_cli.builder.agent_ops._model_reply", return_value=corrected) as model:
        text, result = _validate_and_repair(
            "local", "src/app.py", "def broken(:", {}, threading.Event(), journal, "job",
        )
    assert text == "answer = 43\n"
    assert result == "python_syntax_ok"
    assert model.call_count == 1
    assert len(journal.steps) == 1


@pytest.mark.parametrize("reply", [
    {"path": "../unexpected.py", "content": "answer = 43\n"},
    {"path": "src/app.py", "content": "def broken(:"},
])
def test_repair_fails_closed_on_wrong_path_or_still_invalid(reply):
    journal = InMemoryJournal()
    with patch("tof_cli.builder.agent_ops._model_reply", return_value=json.dumps(reply)) as model:
        with pytest.raises(BuildError):
            _validate_and_repair(
                "local", "src/app.py", "def broken(:", {}, threading.Event(), journal, "job",
            )
    assert model.call_count == 1


def test_valid_code_does_not_call_model():
    journal = InMemoryJournal()
    with patch("tof_cli.builder.agent_ops._model_reply") as model:
        text, result = _validate_and_repair(
            "local", "src/app.py", "answer = 42\n", {}, threading.Event(), journal, "job",
        )
    assert text == "answer = 42\n"
    assert result == "python_syntax_ok"
    model.assert_not_called()
    assert journal.steps == []
