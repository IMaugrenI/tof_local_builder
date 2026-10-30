"""The Builder owns its local interface and never delegates to Open WebUI."""
from __future__ import annotations

from pathlib import Path

from tof_cli.ui import app


def test_native_links_use_only_existing_configured_ports():
    links = app._configured_links({
        "OPENWEBUI_PORT": "3111",  # an old config key is ignored
        "REPO_BRIDGE_PORT": "8112",
        "OLLAMA_PORT": "11440",
    })
    assert "openwebui" not in links
    assert links["repo_bridge_health"]["url"] == "http://127.0.0.1:8112/health"
    assert links["ollama"]["url"] == "http://127.0.0.1:11440"


def test_invalid_bridge_port_never_opens_arbitrary_location(monkeypatch):
    monkeypatch.setattr(app, "read_env", lambda: {"REPO_BRIDGE_PORT": "8099/unsafe"})
    opened = []
    monkeypatch.setattr(app.webbrowser, "open", lambda url: opened.append(url))
    result = app._open_link("repo_bridge_health")
    assert result["error"] == "invalid_local_port"
    assert not opened


def test_native_ui_contains_task_and_sandbox_build_controls():
    assert "async function sendTask()" in app.HTML
    assert "async function startSandboxBuild()" in app.HTML
    assert "async function cancelSandboxBuild()" in app.HTML
    assert "async function resumeSandboxBuild()" in app.HTML
    assert "async function inspectArchitecture()" in app.HTML
    assert "async function searchLocalKnowledge()" in app.HTML
    assert "async function saveLocalConversation()" in app.HTML
    assert "async function restoreLocalConversation()" in app.HTML
    assert "async function deleteLocalConversation()" in app.HTML
    assert "/api/conversation/save" in app.HTML
    assert "/api/knowledge/search" in app.HTML
    assert "/api/project/inspect" in app.HTML
    assert "Static syntax checks (not a test run)" in app.HTML
    assert "/api/build/resume" in app.HTML
    assert "/api/build" in app.HTML
    assert "Open WebUI" not in app.HTML


def test_compose_runtime_has_no_openwebui_service():
    root = Path(__file__).resolve().parents[1]
    for filename in ("compose.yml", "compose.host_bridge.yml"):
        content = (root / filename).read_text(encoding="utf-8")
        assert "open-webui:" not in content
