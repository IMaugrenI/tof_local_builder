"""Focused isolated agent tests: path policy, scoped journals, bounded execution.

No real LLM, Docker, source writes or Git operations are involved.
"""
from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from tof_cli.builder.agent_bridge import AgentBridge, BridgeError, safe_relative_file
from tof_cli.builder.agent_ops import AgentManager, BuildCancelled, BuildError, _plan_from_model, build_in_sandbox
from tof_cli.builder.job_journal import JobJournal, JournalError


class FakeBridge:
    def __init__(self) -> None:
        self.writes: list[tuple[str, str]] = []
        self.saved: dict[str, str] = {}
        self.source_overrides: dict[str, str] = {}
        self.verified = False

    def tree(self, directory: str = "") -> list[dict[str, object]]:
        if directory == "":
            return [
                {"name": "README.md", "path": "README.md", "type": "file"},
                {"name": "src", "path": "src", "type": "dir"},
            ]
        return [{"name": "demo.py", "path": "src/demo.py", "type": "file"}]

    def source_text(self, path: str, max_bytes: int = 6000) -> str | None:
        if path in self.source_overrides:
            return self.source_overrides[path]
        if path == "README.md":
            return "Read-only demo project"
        if path == "src/demo.py":
            return "def answer():\n    return 1\n"
        return None

    def verify_roots(self) -> None:
        self.verified = True

    def output_text(self, path: str) -> str | None:
        return self.saved.get(path)

    def write_output(self, path: str, content: str) -> None:
        if path in self.saved:
            raise BridgeError("Existing draft cannot be replaced")
        self.saved[path] = content
        self.writes.append((path, content))


class AgentTests(unittest.TestCase):
    def test_generated_path_rejects_escape_and_suspicious_names(self) -> None:
        for unsafe in ("../x.py", "/tmp/x.py", "C:\\x.py", ".env",
                       ".git/config.py", "src/token.py", "a//b.py",
                       "src/private_key.py", "config.exe"):
            with self.subTest(unsafe=unsafe), self.assertRaises(BridgeError):
                safe_relative_file(unsafe)
        self.assertEqual(safe_relative_file("src/example.py"), "src/example.py")

    def test_plan_rejects_duplicate_files_and_external_paths(self) -> None:
        invalid = [
            {"summary": "x", "steps": ["do"], "files": [{"path": "../bad.py", "description": "x"}]},
            {"summary": "x", "steps": ["do"], "files": [
                {"path": "src/a.py", "description": "a"},
                {"path": "src/A.py", "description": "b"}]},
            {"summary": "x", "steps": [], "files": []},
        ]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises((BridgeError, BuildError)):
                _plan_from_model(json.dumps(value))

    def test_job_journal_is_scoped_and_writes_only_to_workspace_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, sandbox = Path(tmp) / "source", Path(tmp) / "sandbox"
            source.mkdir()
            sandbox.mkdir()
            env = {"SOURCE_REPO_PATH": str(source), "BUILDER_SANDBOX_PATH": str(sandbox)}
            journal = JobJournal(env)
            record = journal.create("Build demo", "test-model", "code")
            latest = journal.update(record["id"], status="planning", steps=["plan"])
            self.assertEqual(latest["status"], "planning")
            self.assertEqual(journal.get(record["id"])["goal"], "Build demo")
            self.assertEqual(len(journal.recent()), 1)
            self.assertFalse(list(source.rglob("*")))
            self.assertEqual(len(list((sandbox / "workspace" / ".builder_runs").glob("*.json"))), 1)
            other = Path(tmp) / "different_source"
            other.mkdir()
            with self.assertRaises(JournalError):
                JobJournal({"SOURCE_REPO_PATH": str(other), "BUILDER_SANDBOX_PATH": str(sandbox)}).get(record["id"])

    def test_bridge_rejects_stale_runtime_mounts(self) -> None:
        bridge = AgentBridge.__new__(AgentBridge)
        bridge.source = Path("/project/source").resolve()
        bridge.sandbox = Path("/project/sandbox").resolve()
        with patch.object(bridge, "_request", return_value={
            "source_host_path": "/different/source", "sandbox_host_path": "/project/sandbox",
        }):
            with self.assertRaises(BridgeError):
                bridge.verify_roots()

    def test_agent_generates_reviewable_draft_without_source_write(self) -> None:
        class FakeJournal:
            record = {"model": "local", "goal": "Revise demo"}

            def get(self, job_id):
                return self.record

            def update(self, job_id, **fields):
                self.record.update(fields)
                return self.record

        bridge, journal = FakeBridge(), FakeJournal()
        replies = iter([
            json.dumps({"summary": "Update demo", "steps": ["inspect", "revise"],
                        "files": [{"path": "src/demo.py", "description": "Improve answer"}]}),
            json.dumps({"path": "src/demo.py", "content": "def answer():\n    return 2\n"}),
        ])
        with patch("tof_cli.builder.agent_ops._model_reply", side_effect=lambda *_: next(replies)):
            build_in_sandbox(journal, bridge, "job", {"OLLAMA_PORT": "11434"}, threading.Event())
        self.assertEqual(journal.record["status"], "completed")
        self.assertTrue(bridge.verified)
        self.assertEqual(bridge.writes, [("src/demo.py", "def answer():\n    return 2\n")])

    def test_interrupted_job_resumes_without_overwriting_verified_draft(self) -> None:
        """An explicitly resumed job skips the first draft after hash validation."""
        class FakeJournal:
            def __init__(self):
                self.record = {"model": "local", "goal": "Improve example", "plan": None, "files": []}

            def get(self, job_id):
                return dict(self.record)

            def update(self, job_id, **fields):
                self.record.update(fields)
                return dict(self.record)

        journal = FakeJournal()
        bridge = FakeBridge()
        plan = json.dumps({"summary": "Improve both files", "steps": ["inspect", "write"],
                           "files": [{"path": "src/demo.py", "description": "Improve demo"},
                                     {"path": "src/new.py", "description": "Add helper"}]})
        replies = iter([plan, json.dumps({"path": "src/demo.py", "content": "result = 2\n"})])
        with patch("tof_cli.builder.agent_ops._model_reply", side_effect=lambda *_: next(replies)):
            # Simulate a worker process dying on the second generation request.
            with self.assertRaises(StopIteration):
                build_in_sandbox(journal, bridge, "run", {}, threading.Event())
        self.assertEqual(bridge.writes, [("src/demo.py", "result = 2\n")])
        self.assertEqual(journal.record["status"], "generating")

        # A new worker receives the persisted plan; only the unfinished file
        # needs an LLM response. The old file must not be rewritten.
        with patch("tof_cli.builder.agent_ops._model_reply", return_value=json.dumps({
            "path": "src/new.py", "content": "helper = True\n",
        })) as model:
            build_in_sandbox(journal, bridge, "run", {}, threading.Event())
            self.assertEqual(model.call_count, 1)
        self.assertEqual(journal.record["status"], "completed")
        self.assertEqual(bridge.writes, [("src/demo.py", "result = 2\n"),
                                         ("src/new.py", "helper = True\n")])

    def test_resume_rejects_modified_previous_output(self) -> None:
        from tof_cli.builder.agent_ops import _digest, _project_snapshot

        bridge = FakeBridge()
        bridge.saved["src/demo.py"] = "changed by user"
        plan = {"summary": "Edit", "steps": ["one"],
                "files": [{"path": "src/demo.py", "description": "Revise"}]}
        journal_record = {
            "model": "local", "goal": "Revise demo", "plan": plan,
            "files": ["src/demo.py"], "output_hashes": {"src/demo.py": _digest("original")},
            "source_hashes": {"src/demo.py": _digest(bridge.source_text("src/demo.py"))},
            "context_hash": _digest(_project_snapshot(bridge, "Revise demo")),
        }

        class FakeJournal:
            def get(self, job_id):
                return dict(journal_record)

            def update(self, job_id, **fields):
                journal_record.update(fields)
                return dict(journal_record)

        with patch("tof_cli.builder.agent_ops._model_reply") as model:
            with self.assertRaises(BuildError):
                build_in_sandbox(FakeJournal(), bridge, "job", {}, threading.Event())
            model.assert_not_called()
        self.assertEqual(bridge.writes, [])

    def test_resume_blocks_unjournaled_file_without_replacing_it(self) -> None:
        from tof_cli.builder.agent_ops import _digest, _project_snapshot

        bridge = FakeBridge()
        bridge.saved["src/demo.py"] = "untracked draft"
        plan = {"summary": "Edit", "steps": ["one"],
                "files": [{"path": "src/demo.py", "description": "Revise"}]}
        record = {
            "model": "local", "goal": "Revise demo", "plan": plan,
            "files": [], "output_hashes": {},
            "source_hashes": {"src/demo.py": _digest(bridge.source_text("src/demo.py"))},
            "context_hash": _digest(_project_snapshot(bridge, "Revise demo")),
        }

        class FakeJournal:
            def get(self, job_id):
                return dict(record)

            def update(self, job_id, **fields):
                record.update(fields)
                return dict(record)

        with patch("tof_cli.builder.agent_ops._model_reply") as model:
            with self.assertRaises(BuildError):
                build_in_sandbox(FakeJournal(), bridge, "job", {}, threading.Event())
            model.assert_not_called()
        self.assertEqual(bridge.saved["src/demo.py"], "untracked draft")

    def test_resume_blocks_changed_source_even_if_saved_outputs_unchanged(self) -> None:
        from tof_cli.builder.agent_ops import _digest, _project_snapshot

        bridge = FakeBridge()
        plan = {"summary": "Edit", "steps": ["one"],
                "files": [{"path": "src/demo.py", "description": "Revise"}]}
        record = {
            "model": "local", "goal": "Revise demo", "plan": plan,
            "files": [], "output_hashes": {},
            "source_hashes": {"src/demo.py": _digest(bridge.source_text("src/demo.py"))},
            "context_hash": _digest(_project_snapshot(bridge, "Revise demo")),
        }

        class FakeJournal:
            def get(self, job_id):
                return dict(record)

            def update(self, job_id, **fields):
                record.update(fields)
                return dict(record)

        bridge.source_overrides["src/demo.py"] = "def answer():\n    return 5\n"
        with patch("tof_cli.builder.agent_ops._model_reply") as model:
            with self.assertRaises(BuildError):
                build_in_sandbox(FakeJournal(), bridge, "job", {}, threading.Event())
            model.assert_not_called()
        self.assertEqual(bridge.writes, [])

    def test_cancelled_job_never_calls_model_or_writes(self) -> None:
        class FakeJournal:
            def get(self, job_id):
                return {"model": "local", "goal": "Build"}

            def update(self, job_id, **fields):
                return fields

        cancel = threading.Event()
        cancel.set()
        bridge = FakeBridge()
        with patch("tof_cli.builder.agent_ops._model_reply") as model:
            with self.assertRaises(BuildCancelled):
                build_in_sandbox(FakeJournal(), bridge, "job", {}, cancel)
            model.assert_not_called()
        self.assertEqual(bridge.writes, [])


    def test_build_uses_shared_local_model_gate(self) -> None:
        gate = threading.BoundedSemaphore(1)
        gate.acquire()
        try:
            manager = AgentManager(model_gate=gate)
            with self.assertRaises(BuildError):
                manager.start(task="code", model="local", goal="Build something")
        finally:
            gate.release()


if __name__ == "__main__":
    unittest.main()
