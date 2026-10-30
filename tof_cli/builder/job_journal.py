"""Bounded, crash-safe local job journal inside the existing Builder sandbox.

This journal is control metadata, not a generated source artifact. It never
touches the selected read-only project or starts another service.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from tof_cli.builder.artifact_ops import _get_area, _resolve_sandbox
from tof_cli.builder.repo_bridge_ops import source_repo_report

MAX_RECORD_BYTES = 64_000
MAX_JOBS = 200
JOB_ID = re.compile(r"^[0-9a-f]{32}$")
RUNNING = frozenset({"queued", "inspecting", "planning", "generating", "cancelling", "resuming"})


class JournalError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobJournal:
    def __init__(self, env: dict[str, str]) -> None:
        source = source_repo_report(env)
        sandbox = _resolve_sandbox(env)
        if source["state"] != "ok" or sandbox is None:
            raise JournalError("Choose a valid read-only source and a separate sandbox first")
        source_root = Path(source["path"]).resolve()
        if not source_root.is_dir():
            raise JournalError("Source project is not a directory")
        workspace = _get_area(sandbox, "workspace")
        workspace.mkdir(parents=True, exist_ok=True)
        if workspace.is_symlink() or not workspace.resolve().is_relative_to(sandbox):
            raise JournalError("Unsafe workspace path")
        directory = workspace / ".builder_runs"
        if directory.is_symlink():
            raise JournalError("Unsafe job journal path")
        directory.mkdir(mode=0o700, exist_ok=True)
        if not directory.resolve().is_relative_to(workspace.resolve()):
            raise JournalError("Job journal is outside the sandbox")
        self.directory = directory
        identity = f"{source_root}|{sandbox}"
        self.scope = hashlib.sha256(identity.encode("utf-8")).hexdigest()

    def _path(self, job_id: str) -> Path:
        if not isinstance(job_id, str) or not JOB_ID.fullmatch(job_id):
            raise JournalError("Invalid job identifier")
        return self.directory / (job_id + ".json")

    def _read(self, path: Path) -> dict[str, object]:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_RECORD_BYTES:
            raise JournalError("Job record is missing or unsafe")
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            raise JournalError("Job record could not be read") from exc
        if not isinstance(record, dict) or record.get("scope") != self.scope:
            raise JournalError("Job belongs to a different project workspace")
        return record

    def get(self, job_id: str) -> dict[str, object]:
        record = self._read(self._path(job_id))
        result = dict(record)
        if result.get("status") in RUNNING:
            # The in-memory manager can distinguish a live job from a stale
            # journal after a restart. Never resume writes automatically.
            result["resume_policy"] = "check_active_worker"
        return result

    def recent(self, limit: int = 12) -> list[dict[str, object]]:
        files = sorted(
            (p for p in self.directory.glob("*.json") if JOB_ID.fullmatch(p.stem) and not p.is_symlink()),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        records = []
        for path in files[: min(limit, 20)]:
            try:
                records.append(self._read(path))
            except JournalError:
                continue
        return records

    def create(self, goal: str, model: str, task: str) -> dict[str, object]:
        if len(list(self.directory.glob("*.json"))) >= MAX_JOBS:
            raise JournalError("Job history is full; archive old journal entries before creating more")
        stamp = _now()
        record: dict[str, object] = {
            "id": uuid.uuid4().hex,
            "scope": self.scope,
            "goal": goal,
            "model": model,
            "task": task,
            "status": "queued",
            "current_step": "Preparing your request",
            "steps": [],
            "plan": None,
            "context_hash": "",
            "source_hashes": {},
            "output_hashes": {},
            "syntax_checks": {},
            "files": [],
            "resume_count": 0,
            "summary": "",
            "error": "",
            "created_at": stamp,
            "updated_at": stamp,
        }
        path = self._path(str(record["id"]))
        serialized = json.dumps(record, ensure_ascii=False).encode("utf-8")
        with path.open("xb") as handle:
            handle.write(serialized)
        try:
            path.chmod(0o600)
        except OSError:
            pass
        return record

    def update(self, job_id: str, **fields: object) -> dict[str, object]:
        record = self._read(self._path(job_id))
        allowed = {"status", "current_step", "steps", "plan", "context_hash",
                   "source_hashes", "output_hashes", "syntax_checks", "files", "summary", "error", "resume_count"}
        if set(fields) - allowed:
            raise JournalError("Attempt to modify protected journal fields")
        record.update(fields)
        record["updated_at"] = _now()
        payload = json.dumps(record, ensure_ascii=False).encode("utf-8")
        if len(payload) > MAX_RECORD_BYTES:
            raise JournalError("Job record is too large")
        path = self._path(job_id)
        # No in-place partial writes; completed job records remain inspectable.
        fd, temp_name = tempfile.mkstemp(prefix=".job-", dir=str(self.directory))
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            if path.is_symlink():
                raise JournalError("Journal entry became a symlink")
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        return record
