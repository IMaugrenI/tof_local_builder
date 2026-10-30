"""Bounded, direct Ollama chat transport for the Builder's own UI.

No tool execution, source modification, downloads, or session persistence happens
in this module. It is a transport foundation, not an autonomous agent.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

MAX_PROMPT_CHARS = 12_000
MAX_REPLY_CHARS = 40_000
MAX_RESPONSE_BYTES = 512_000
MAX_HISTORY_TURNS = 10
MAX_HISTORY_CHARS = 12_000
DEFAULT_TIMEOUT_SECONDS = 90


class ModelChatError(RuntimeError):
    """User-actionable failure without exposing transport internals."""


@dataclass(frozen=True)
class ChatReply:
    model: str
    content: str


def _local_port(port: str) -> int:
    try:
        number = int(str(port))
    except (TypeError, ValueError) as exc:
        raise ModelChatError("Invalid local Ollama port") from exc
    if not 1 <= number <= 65535:
        raise ModelChatError("Invalid local Ollama port")
    return number


def _parse_reply(raw: bytes, chosen_model: str) -> ChatReply:
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ModelChatError("Model response exceeded the size limit")
    try:
        payload: Any = json.loads(raw)
    except (UnicodeError, ValueError) as exc:
        raise ModelChatError("Model returned an unreadable response") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("message"), dict):
        raise ModelChatError("Model returned an unexpected response")
    content = payload["message"].get("content")
    if not isinstance(content, str):
        raise ModelChatError("Model response contains no text")
    if len(content) > MAX_REPLY_CHARS:
        raise ModelChatError("Model reply is too long")
    return ChatReply(model=chosen_model, content=content)


def chat_once(
    *,
    model: str,
    prompt: str,
    ollama_port: str = "11434",
    installed_models: set[str] | None = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    history: list[dict[str, str]] | None = None,
    response_format: str | None = None,
) -> ChatReply:
    """Call the local Ollama chat API once, without executing its output.

    When installed_models is passed, the model must match an installed tag.
    The caller is responsible for retrieving those tags and for authorization
    of the UI request. Ollama stays on the loopback interface.
    """
    if not isinstance(model, str) or not model.strip() or len(model) > 160:
        raise ModelChatError("Select a valid local model")
    if installed_models is not None and model not in installed_models:
        raise ModelChatError("The selected model is not installed")
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > MAX_PROMPT_CHARS:
        raise ModelChatError("Enter a task between 1 and 12000 characters")
    if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 300:
        raise ModelChatError("Invalid model timeout")

    # Conversation context is only text. Never accept tool/command objects,
    # system roles, or arbitrarily large browser-provided histories.
    prior: list[dict[str, str]] = []
    if history is not None:
        if not isinstance(history, list) or len(history) > MAX_HISTORY_TURNS:
            raise ModelChatError("Conversation history is too long")
        total = 0
        for entry in history:
            if not isinstance(entry, dict) or entry.get("role") not in ("user", "assistant"):
                raise ModelChatError("Invalid conversation role")
            content = entry.get("content")
            if not isinstance(content, str) or not content.strip() or len(content) > 4000:
                raise ModelChatError("Invalid conversation entry")
            total += len(content)
            prior.append({"role": entry["role"], "content": content})
        if total > MAX_HISTORY_CHARS:
            raise ModelChatError("Conversation history exceeded the size limit")
    if response_format not in (None, "json"):
        raise ModelChatError("Unsupported response format")
    endpoint = f"http://127.0.0.1:{_local_port(ollama_port)}/api/chat"
    request_body = {
        "model": model,
        "messages": prior + [{"role": "user", "content": prompt.strip()}],
        "stream": False,
    }
    if response_format == "json":
        request_body["format"] = "json"
    body = json.dumps(request_body).encode("utf-8")
    request = urllib.request.Request(
        endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ModelChatError("Local model is unavailable; check Ollama status") from exc
    return _parse_reply(raw, model)
