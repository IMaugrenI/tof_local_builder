"""Focused B4 tests for configured browser handoff and no silent fallback."""
from __future__ import annotations

from tof_cli.ui import app


def test_workspace_link_uses_existing_configured_ports():
    links = app._configured_links({
        "OPENWEBUI_PORT": "3111",
        "REPO_BRIDGE_PORT": "8112",
        "OLLAMA_PORT": "11440",
    })
    assert links["openwebui"]["url"] == "http://127.0.0.1:3111"
    assert links["repo_bridge_health"]["url"] == "http://127.0.0.1:8112/health"
    assert links["ollama"]["url"] == "http://127.0.0.1:11440"


def test_invalid_port_never_opened_or_replaced_with_arbitrary_location(monkeypatch):
    monkeypatch.setattr(app, "read_env", lambda: {"OPENWEBUI_PORT": "3000/other"})
    opened = []
    monkeypatch.setattr(app.webbrowser, "open", lambda url: opened.append(url))
    result = app._open_link("openwebui")
    assert result["error"] == "invalid_local_port"
    assert not opened


def test_handoff_opens_local_configured_webui_only(monkeypatch):
    monkeypatch.setattr(app, "read_env", lambda: {"OPENWEBUI_PORT": "3333"})
    opened = []
    monkeypatch.setattr(app.webbrowser, "open", lambda url: opened.append(url))
    result = app._open_link("openwebui")
    assert opened == ["http://127.0.0.1:3333"]
    assert result["opened"] == opened[0]


def test_task_handoff_requires_successful_copy_in_existing_page():
    assert "async function copyAndOpenTask()" in app.HTML
    assert "if (await copyTask())" in app.HTML
    assert "onclick=\"copyAndOpenTask()\"" in app.HTML
