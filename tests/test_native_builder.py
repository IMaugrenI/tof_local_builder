"""Focused native Builder checks; do not require Docker or a running model."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tof_cli.builder.ollama_chat import ChatReply
from tof_cli.builder.task_runner import run_task_once
from tof_cli.ui.launcher import ui_port, ui_url


class NativeBuilderTests(unittest.TestCase):
    def test_ui_port_validation(self) -> None:
        self.assertEqual(ui_port({}), 8795)
        self.assertEqual(ui_url({"BUILDER_UI_PORT": "9012"}), "http://127.0.0.1:9012")
        for invalid in ("abc", "0", "65536", "-1"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                ui_port({"BUILDER_UI_PORT": invalid})

    def test_task_plans_only_and_never_writes_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            source.mkdir()
            (source / "README.md").write_text("Demo source", encoding="utf-8")
            fake_prepared = {"source": str(source), "prompt": "Task: analyze the project"}
            with patch("tof_cli.builder.task_runner.read_env", return_value={"OLLAMA_PORT": "11434"}), \
                 patch("tof_cli.builder.task_runner.prepare_task", return_value=fake_prepared) as prepare, \
                 patch("tof_cli.builder.task_runner.chat_once", return_value=ChatReply("local-model", "Suggested steps")) as chat:
                response = run_task_once(task="repo_help", model="local-model", goal="Explain the project")
            self.assertEqual(response["content"], "Suggested steps")
            self.assertEqual(response["files_modified"], False)
            self.assertEqual(response["execution_mode"], "read_only_assistance")
            self.assertEqual((source / "README.md").read_text(encoding="utf-8"), "Demo source")
            self.assertIn("Demo source", chat.call_args.kwargs["prompt"])
            self.assertIn("no tools are available", chat.call_args.kwargs["prompt"])
            prepare.assert_called_once()

    def test_invalid_goal_is_rejected_before_model_access(self) -> None:
        with patch("tof_cli.builder.task_runner.prepare_task") as prepare:
            with self.assertRaises(ValueError):
                run_task_once(task="code", model="test", goal="")
            prepare.assert_not_called()


if __name__ == "__main__":
    unittest.main()
