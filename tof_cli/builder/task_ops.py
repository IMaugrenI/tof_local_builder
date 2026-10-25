"""Read-only task and model planning from the existing Builder catalog.

No installs, container control, source writes, or model switches happen here.
The generated prompt is copied manually into the existing Open WebUI.
"""
from __future__ import annotations

import json
from pathlib import Path

from tof_cli.builder.model_ops import ollama_tags
from tof_cli.builder.repo_bridge_ops import sandbox_report, source_repo_report
from tof_cli.core.env_ops import REPO_ROOT, read_env

CATALOG = REPO_ROOT / "model_catalog" / "builder_catalog.json"
TASK_LABELS = {
    "code": "Write or review code",
    "repo_help": "Understand a repository",
    "analysis": "Analyze a problem",
    "writing": "Draft documentation",
    "chat": "General assistance",
}
MAX_GOAL_LENGTH = 2000


def catalog_tasks() -> list[dict[str, str]]:
    return [{"key": key, "label": value} for key, value in TASK_LABELS.items()]


def _suggestions(task: str) -> list[dict[str, object]]:
    if task not in TASK_LABELS:
        raise ValueError("Unknown task type")
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    records: dict[str, dict[str, object]] = {}
    for group in data.get("groups", []):
        for profile in group.get("profiles", []):
            if task not in profile.get("task_labels", []):
                continue
            for model in profile.get("models", []):
                if not model.get("visible_in_wizard", False):
                    continue
                tag = str(model.get("tag", "")).strip()
                if tag and tag not in records:
                    records[tag] = {
                        "tag": tag, "profile": str(profile.get("label", "")),
                        "recommended": bool(model.get("recommended", False)),
                    }
    return list(records.values())


def task_options(task: str, env: dict[str, str] | None = None) -> dict[str, object]:
    values = env if env is not None else read_env()
    recommendations = _suggestions(task)
    try:
        installed = set(ollama_tags(values.get("OLLAMA_PORT", "11434")))
        reachable = True
    except (OSError, ValueError, TimeoutError):
        installed = set()
        reachable = False
    for model in recommendations:
        model["installed"] = model["tag"] in installed
    current = values.get("DEFAULT_OLLAMA_MODEL", "")
    return {
        "task": task, "tasks": catalog_tasks(), "models": recommendations,
        "installed_models": sorted(installed), "model_service_reachable": reachable,
        "configured_default": current, "action": "planning_only",
    }


def prepare_task(task: str, model: str, goal: str, env: dict[str, str] | None = None) -> dict[str, object]:
    values = env if env is not None else read_env()
    if not goal.strip() or len(goal) > MAX_GOAL_LENGTH:
        raise ValueError("Task description must be 1–2000 characters")
    options = task_options(task, values)
    if model not in options["installed_models"]:
        raise ValueError("Select an installed local model; no model download was started")
    source = source_repo_report(values)
    sandbox = sandbox_report(values)
    if source["state"] != "ok" or sandbox["state"] != "ok":
        raise ValueError("Configure existing source and sandbox paths before preparing a task")
    src = Path(source["path"]).resolve()
    dest = Path(sandbox["path"]).resolve()
    if src == dest or src in dest.parents or dest in src.parents:
        raise ValueError("Source and sandbox cannot overlap")
    # Goal is an instruction to the user-selected local model, never executed here.
    prompt = (
        f"Task: {TASK_LABELS[task]}\n"
        f"Goal:\n{goal.strip()}\n\n"
        "Work only with the selected read-only source project. "
        "Write any generated files exclusively under sandbox/workspace or sandbox/output. "
        "Do not edit, delete, commit, or push source files. "
        "State uncertainties and summarize files created for manual review. "
        "The operator decides whether to adopt any change."
    )
    return {
        "task": task, "model": model, "prompt": prompt,
        "source": source["path"], "sandbox": sandbox["path"],
        "writes_performed": False, "model_changed": False,
        "handoff": "Copy the prompt into Open WebUI and choose the installed model there.",
    }


def task_guide(env: dict[str, str] | None = None) -> dict[str, object]:
    """Collect all task choices and installed-model hints in one local read."""
    values = env if env is not None else read_env()
    try:
        installed = set(ollama_tags(values.get("OLLAMA_PORT", "11434")))
        reachable = True
    except (OSError, TimeoutError, ValueError):
        installed = set()
        reachable = False
    return {
        "tasks": catalog_tasks(),
        "recommendations": {key: [dict(row, installed=row["tag"] in installed)
                                 for row in _suggestions(key)] for key in TASK_LABELS},
        "installed_models": sorted(installed),
        "configured_default": values.get("DEFAULT_OLLAMA_MODEL", ""),
        "model_service_reachable": reachable,
        "handoff": "Select the chosen installed model manually in Open WebUI.",
    }
