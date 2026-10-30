"""Launch or reuse the existing Builder control UI (no competing runtime).

Only the existing python run.py ui entrypoint is started. No Docker or source
filesystem actions are carried out here.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from tof_cli.core.env_ops import REPO_ROOT

UI_DEFAULT_PORT = 8795


def ui_port(env: dict[str, str]) -> int:
    try:
        port = int(env.get("BUILDER_UI_PORT", str(UI_DEFAULT_PORT)))
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid BUILDER_UI_PORT") from exc
    if not 1 <= port <= 65535:
        raise ValueError("Invalid BUILDER_UI_PORT")
    return port


def ui_url(env: dict[str, str]) -> str:
    return f"http://127.0.0.1:{ui_port(env)}"


def _is_builder_ui(url: str) -> bool:
    try:
        with urllib.request.urlopen(url + "/api/identity", timeout=0.8) as response:
            data = json.loads(response.read(1024))
        return isinstance(data, dict) and data.get("app") == "tof_local_builder" and data.get("ui") == "control"
    except (OSError, ValueError, TimeoutError):
        return False


def builder_ui_running(env: dict[str, str]) -> bool:
    """Whether the configured port already serves this Builder, not another app."""
    return _is_builder_ui(ui_url(env))


def ensure_builder_ui(env: dict[str, str]) -> tuple[bool, str]:
    """Start the local UI on demand, never silently replace another process."""
    url = ui_url(env)
    if _is_builder_ui(url):
        return True, url
    # Distinguish a foreign process from an unused port.
    from socket import AF_INET, SOCK_STREAM, socket

    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        if sock.connect_ex(("127.0.0.1", ui_port(env))) == 0:
            return False, "Builder UI port is occupied by another service"
    command = [sys.executable, str(REPO_ROOT / "run.py"), "ui", "--port", str(ui_port(env)), "--no-browser"]
    try:
        subprocess.Popen(
            command,
            cwd=Path(REPO_ROOT),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            start_new_session=True,
        )
    except OSError as exc:
        return False, f"Could not start Builder UI: {exc}"
    for _ in range(30):
        if _is_builder_ui(url):
            return True, url
        time.sleep(0.15)
    return False, "Builder UI did not become reachable"
