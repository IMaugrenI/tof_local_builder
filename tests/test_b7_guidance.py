"""B7: actionable, non-destructive guidance based on existing readiness checks."""
from __future__ import annotations

from tof_cli.ui import app
from tof_cli.ui.guidance import explain_readiness


def item(name, state):
    return {"name": name, "label": name, "state": state}


def test_all_ready_preserves_existing_success_contract():
    report = explain_readiness([item("source", "ready"), item("sandbox", "ready"),
                                item("ollama", "ready"), item("default_model", "ready"),
                                item("repo_bridge", "ready"), item("webui", "ready")])
    assert report["status"] == "ready"
    assert report["next_step"].startswith("Everything is ready")
    assert report["priority"] is None
    assert report["checks"] == []
    assert report["read_only"] is True


def test_source_and_sandbox_have_priority_over_services():
    report = explain_readiness([item("webui", "not_reachable"),
                                item("source", "not_reachable"),
                                item("sandbox", "not_reachable")])
    assert report["priority"]["name"] == "source"
    assert report["priority"]["suggested_action"] == "setup"
    assert [issue["name"] for issue in report["checks"]] == ["source", "sandbox", "webui"]


def test_missing_model_and_services_have_distinct_next_steps():
    model = explain_readiness([item("default_model", "not_reachable")])
    assert "model" in model["next_step"].lower()
    assert model["priority"]["suggested_action"] == "setup"
    engine = explain_readiness([item("ollama", "not_reachable"), item("webui", "not_reachable")])
    assert engine["priority"]["name"] == "ollama"
    assert engine["priority"]["suggested_action"] == "up"
    bridge = explain_readiness([item("repo_bridge", "http_503")])
    assert bridge["priority"]["suggested_action"] == "doctor"
    assert "endpoint" in bridge["next_step"].lower()


def test_empty_status_is_not_marked_successful():
    report = explain_readiness([])
    assert report["status"] == "attention"
    assert "incomplete" in report["next_step"]


def test_summary_exposes_guidance_with_legacy_fields(monkeypatch):
    monkeypatch.setattr(app, "_readiness_payload", lambda: {
        "items": [item("source", "not_reachable"), item("webui", "ready")]
    })
    monkeypatch.setattr(app, "task_guide", lambda: {"tasks": []})
    summary = app._summary_payload()
    assert "actions" in summary and "links" in summary
    assert summary["guidance"]["priority"]["name"] == "source"
    assert summary["next_step"] == summary["guidance"]["next_step"]
    assert "renderGuidance" in app.HTML
