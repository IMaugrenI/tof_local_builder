"""Opt-in, project-scoped local conversation snapshots.

Nothing is persisted automatically. Users explicitly choose Save / Restore /
Delete inside the existing Builder UI. The selected source remains read-only.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from tof_cli.builder.job_journal import JobJournal

MAX_CONVERSATION_TURNS = 10
MAX_TURN_CHARS = 4_000
MAX_CONVERSATION_CHARS = 9_000
MAX_SESSION_BYTES = 20_000


class ConversationError(ValueError):
    pass


def validate_conversation(messages: object) -> list[dict[str, str]]:
    if not isinstance(messages, list) or len(messages) > MAX_CONVERSATION_TURNS:
        raise ConversationError("Conversation exceeds the ten-message limit")
    cleaned = []
    total = 0
    for entry in messages:
        if not isinstance(entry, dict) or set(entry) != {"role", "content"}:
            raise ConversationError("Conversation entry must contain only role and text")
        role, content = entry["role"], entry["content"]
        if role not in ("user", "assistant") or not isinstance(content, str):
            raise ConversationError("Conversation contains an invalid role or entry")
        if not content.strip() or len(content) > MAX_TURN_CHARS:
            raise ConversationError("Conversation entry is empty or too long")
        total += len(content)
        cleaned.append({"role": role, "content": content})
    if total > MAX_CONVERSATION_CHARS:
        raise ConversationError("Conversation exceeds the local snapshot limit")
    return cleaned


class ConversationStore:
    def __init__(self, env: dict[str, str]) -> None:
        journal = JobJournal(env)
        self.scope = journal.scope
        self.path = journal.directory / ("conversation-" + self.scope[:24] + ".json")

    def load(self) -> dict[str, object]:
        if self.path.is_symlink():
            raise ConversationError("Unsafe local conversation path")
        if not self.path.exists():
            return {"saved": False, "messages": [], "read_only_source": True}
        if not self.path.is_file() or self.path.stat().st_size > MAX_SESSION_BYTES:
            raise ConversationError("Saved conversation is not a safe, bounded file")
        try:
            record = json.loads(self.path.read_text(encoding="utf-8"))
        except (UnicodeError, ValueError, OSError) as exc:
            raise ConversationError("Could not read local conversation snapshot") from exc
        if not isinstance(record, dict) or record.get("scope") != self.scope:
            raise ConversationError("Saved conversation belongs to another project")
        return {
            "saved": True,
            "messages": validate_conversation(record.get("messages")),
            "saved_at": record.get("saved_at"),
            "read_only_source": True,
        }

    def save(self, messages: object) -> dict[str, object]:
        cleaned = validate_conversation(messages)
        if not cleaned:
            raise ConversationError("No conversation to save yet")
        if self.path.is_symlink():
            raise ConversationError("Unsafe local conversation path")
        stamp = datetime.now(timezone.utc).isoformat()
        payload = json.dumps({
            "scope": self.scope, "saved_at": stamp, "messages": cleaned,
        }, ensure_ascii=False).encode("utf-8")
        if len(payload) > MAX_SESSION_BYTES:
            raise ConversationError("Saved conversation would exceed the size limit")
        fd, tmp = tempfile.mkstemp(prefix=".conversation-", dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            if self.path.is_symlink():
                raise ConversationError("Unsafe local conversation path")
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        return {"saved": True, "messages": len(cleaned), "saved_at": stamp}

    def delete(self) -> dict[str, object]:
        if self.path.is_symlink():
            raise ConversationError("Unsafe local conversation path")
        try:
            self.path.unlink(missing_ok=True)
        except OSError as exc:
            raise ConversationError("Could not delete local conversation snapshot") from exc
        return {"saved": False, "messages": 0}
