"""Actionable read-only readiness guidance for the existing Builder control UI.

This module only interprets status observations. It never runs recovery actions,
installs models, restarts Compose, or changes the selected project.
"""
from __future__ import annotations

ISSUE_ORDER = ("source", "sandbox", "ollama", "default_model", "repo_bridge", "webui")
HELP = {
    "source": (
        "Select an existing project folder in setup. The project stays read-only.",
        "setup",
    ),
    "sandbox": (
        "Configure a separate writable sandbox folder in setup. It must not overlap the source.",
        "setup",
    ),
    "ollama": (
        "The local model service is not reachable. Start the existing workspace, then check again.",
        "up",
    ),
    "default_model": (
        "The selected model is not available. Check installed models or choose one through the existing setup.",
        "setup",
    ),
    "repo_bridge": (
        "The project connection is not reachable. Check its status and use Find problems for details.",
        "doctor",
    ),
    "webui": (
        "The AI workspace page is not reachable. Start the existing workspace, then check again.",
        "up",
    ),
}


def explain_readiness(items: list[dict[str, object]]) -> dict[str, object]:
    """Give each existing status a next step; select one priority without mutating state."""
    by_name = {str(item.get("name", "")): item for item in items}
    checks: list[dict[str, object]] = []
    for name in ISSUE_ORDER:
        if name not in by_name:
            continue
        item = by_name[name]
        state = str(item.get("state", "unknown"))
        if state == "ready":
            continue
        hint, action = HELP[name]
        if state.startswith("http_"):
            hint += " The endpoint responded but did not report a healthy state."
        checks.append({
            "name": name, "label": str(item.get("label", name)),
            "state": state, "next_step": hint, "suggested_action": action,
        })
    priority = checks[0] if checks else None
    all_ready = bool(items) and all(item.get("state") == "ready" for item in items)
    if all_ready:
        message = "Everything is ready. Open your workspace and continue working with your project."
    elif priority:
        message = priority["next_step"]
    else:
        message = "Status information is incomplete. Choose Find problems to inspect the existing installation."
    return {
        "status": "ready" if all_ready else "attention",
        "next_step": message,
        "priority": priority,
        "checks": checks,
        "read_only": True,
    }
