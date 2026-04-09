from __future__ import annotations

from pathlib import Path

from tof_cli.core.path_ops import normalize_path, path_state


def source_repo_report(env: dict[str, str]) -> dict[str, str]:
    raw = env.get("SOURCE_REPO_PATH", "").strip()
    if not raw or raw == "/absolute/path/to/the/source/repo":
        return {"path": raw, "state": "missing_config"}
    path = normalize_path(raw)
    return {"path": str(path), "state": path_state(path)}


def sandbox_report(env: dict[str, str]) -> dict[str, str]:
    raw = env.get("BUILDER_SANDBOX_PATH", "./sandbox").strip() or "./sandbox"
    path = normalize_path(raw)
    return {"path": str(path), "state": path_state(path)}


def tool_server_url(env: dict[str, str]) -> str:
    return f"http://127.0.0.1:{env.get('REPO_BRIDGE_PORT', '8099')}"
