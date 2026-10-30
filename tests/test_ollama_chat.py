"""Focused safety tests for the direct Ollama transport (no live Ollama needed)."""
from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from tof_cli.builder.ollama_chat import ModelChatError, chat_once


class FakeResponse:
    def __init__(self, data: bytes) -> None:
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size: int) -> bytes:
        return self.data[:size]


class OllamaChatTests(unittest.TestCase):
    def test_valid_chat_uses_local_loopback_and_does_not_execute_tools(self):
        raw = json.dumps({"message": {"role": "assistant", "content": "Sample output"}}).encode()
        with patch("tof_cli.builder.ollama_chat.urllib.request.urlopen", return_value=FakeResponse(raw)) as call:
            reply = chat_once(model="qwen2.5:0.5b", prompt="Make a plan", installed_models={"qwen2.5:0.5b"})
        self.assertEqual(reply.content, "Sample output")
        request = call.call_args.args[0]
        self.assertEqual(request.full_url, "http://127.0.0.1:11434/api/chat")
        payload = json.loads(request.data)
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["messages"][0]["role"], "user")

    def test_rejects_uninstalled_model_before_network_call(self):
        with patch("tof_cli.builder.ollama_chat.urllib.request.urlopen") as call:
            with self.assertRaises(ModelChatError):
                chat_once(model="not-installed", prompt="hello", installed_models={"installed"})
            call.assert_not_called()

    def test_rejects_invalid_port_and_unbounded_prompt(self):
        for port in ("abc", "0", "65536", "-1"):
            with self.subTest(port=port), self.assertRaises(ModelChatError):
                chat_once(model="local", prompt="hello", ollama_port=port)
        with self.assertRaises(ModelChatError):
            chat_once(model="local", prompt="x" * 12001)

    def test_rejects_oversize_response(self):
        with patch("tof_cli.builder.ollama_chat.urllib.request.urlopen", return_value=FakeResponse(b"x" * 512001)):
            with self.assertRaises(ModelChatError):
                chat_once(model="local", prompt="hello")

    def test_does_not_accept_malformed_response(self):
        with patch("tof_cli.builder.ollama_chat.urllib.request.urlopen", return_value=FakeResponse(b"{}")):
            with self.assertRaises(ModelChatError):
                chat_once(model="local", prompt="hello")


if __name__ == "__main__":
    unittest.main()
