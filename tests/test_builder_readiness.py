from __future__ import annotations

from tof_cli.ui import app


def test_readiness_requires_all_services_paths_and_model(monkeypatch):
    monkeypatch.setattr(app, "read_env", lambda: {
        "OPENWEBUI_PORT": "3005",
        "REPO_BRIDGE_PORT": "8109",
        "OLLAMA_PORT": "11440",
        "DEFAULT_OLLAMA_MODEL": "demo:1b",
    })
    monkeypatch.setattr(app, "_probe_url", lambda url: "ready")
    monkeypatch.setattr(app, "source_repo_report", lambda env: {"path": "/test/source", "state": "ok"})
    monkeypatch.setattr(app, "sandbox_report", lambda env: {"path": "/test/sandbox", "state": "ok"})
    monkeypatch.setattr(app, "ollama_tags", lambda port: ["demo:1b"])

    summary = app._summary_payload()
    assert len(summary["readiness"]["items"]) == 6
    assert all(i["state"] == "ready" for i in summary["readiness"]["items"])
    assert summary["next_step"].startswith("Everything is ready")


def test_webui_alone_does_not_mean_ready(monkeypatch):
    monkeypatch.setattr(app, "read_env", lambda: {"DEFAULT_OLLAMA_MODEL": "missing:1b"})
    monkeypatch.setattr(
        app, "_probe_url",
        lambda url: "ready" if ":3000" in url else "not_reachable",
    )
    monkeypatch.setattr(app, "source_repo_report", lambda env: {"path": "", "state": "missing_config"})
    monkeypatch.setattr(app, "sandbox_report", lambda env: {"path": "/test/sandbox", "state": "ok"})
    monkeypatch.setattr(app, "ollama_tags", lambda port: [])

    summary = app._summary_payload()
    assert "Everything is ready" not in summary["next_step"]
    items = {entry["name"]: entry["state"] for entry in summary["readiness"]["items"]}
    assert items["webui"] == "ready"
    assert items["source"] != "ready"
    assert items["default_model"] != "ready"
