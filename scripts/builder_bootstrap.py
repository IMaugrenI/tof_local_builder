#!/usr/bin/env python3
from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

ENV_DEFAULTS = {
    "TZ": "Europe/Berlin",
    "OLLAMA_PORT": "11434",
    "OPENWEBUI_PORT": "3000",
    "REPO_BRIDGE_PORT": "8099",
    "BUILDER_BIND_HOST": "127.0.0.1",
    "OLLAMA_IMAGE": "ollama/ollama:latest",
    "OPENWEBUI_IMAGE": "ghcr.io/open-webui/open-webui:main",
    "OLLAMA_MODELS_PATH": "./data/ollama",
    "OPENWEBUI_DATA_PATH": "./data/open-webui",
    "OLLAMA_KEEP_ALIVE": "5m",
    "SOURCE_REPO_PATH": "/absolute/path/to/the/source/repo",
    "BUILDER_SANDBOX_PATH": "./sandbox",
    "HOST_UID": "1000",
    "HOST_GID": "1000",
    "ALLOW_ORIGINS": "http://localhost:3000,http://127.0.0.1:3000",
    "DEFAULT_OLLAMA_MODEL": "qwen2.5:0.5b",
    "BUILDER_ACCELERATION": "cpu",
    "BUILDER_OPEN_BROWSER": "1",
    "BUILDER_SETUP_DONE": "0",
}

ENV_KEY_ORDER = [
    "TZ",
    "OLLAMA_PORT",
    "OPENWEBUI_PORT",
    "REPO_BRIDGE_PORT",
    "BUILDER_BIND_HOST",
    "OLLAMA_IMAGE",
    "OPENWEBUI_IMAGE",
    "OLLAMA_MODELS_PATH",
    "OPENWEBUI_DATA_PATH",
    "OLLAMA_KEEP_ALIVE",
    "SOURCE_REPO_PATH",
    "BUILDER_SANDBOX_PATH",
    "HOST_UID",
    "HOST_GID",
    "ALLOW_ORIGINS",
    "DEFAULT_OLLAMA_MODEL",
    "BUILDER_ACCELERATION",
    "BUILDER_OPEN_BROWSER",
    "BUILDER_SETUP_DONE",
]

PLACEHOLDER_SOURCE = "/absolute/path/to/the/source/repo"
MODEL_OPTIONS = [
    "qwen2.5:0.5b",
    "qwen2.5:1.5b",
    "qwen2.5:3b",
    "llama3.2:1b",
    "llama3.2:3b",
    "gemma2:2b",
    "qwen2.5-coder:0.5b",
    "qwen2.5-coder:1.5b",
    "qwen2.5-coder:3b",
    "custom",
]


def parse_env_file(path: Path) -> Tuple[Dict[str, str], List[str]]:
    env: Dict[str, str] = {}
    order: List[str] = []
    if not path.exists():
        return env, order

    pattern = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            continue
        key, value = match.group(1), match.group(2)
        value = value.strip().strip('"').strip("'")
        env[key] = value
        if key not in order:
            order.append(key)
    return env, order


def merge_env(existing: Dict[str, str]) -> Dict[str, str]:
    merged = dict(existing)
    for key, value in ENV_DEFAULTS.items():
        merged.setdefault(key, value)
    return merged


def write_env_file(path: Path, env: Dict[str, str], existing_order: List[str] | None = None) -> None:
    existing_order = existing_order or []
    keys: List[str] = []
    for key in ENV_KEY_ORDER + existing_order + sorted(env.keys()):
        if key not in keys:
            keys.append(key)
    lines = [f"{key}={env[key]}" for key in keys if key in env and env[key] is not None]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def get_root_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def get_default_env_path() -> Path:
    return get_root_dir() / ".env"


def _ram_gb() -> float | None:
    try:
        if hasattr(os, "sysconf") and "SC_PAGE_SIZE" in os.sysconf_names and "SC_PHYS_PAGES" in os.sysconf_names:
            page_size = os.sysconf("SC_PAGE_SIZE")
            phys_pages = os.sysconf("SC_PHYS_PAGES")
            return round((page_size * phys_pages) / (1024 ** 3), 1)
    except (ValueError, OSError):
        pass

    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        match = re.search(r"^MemTotal:\s+(\d+)\s+kB$", meminfo.read_text(encoding="utf-8"), re.MULTILINE)
        if match:
            return round((int(match.group(1)) * 1024) / (1024 ** 3), 1)
    return None


def _docker_reachable() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        result = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return result.returncode == 0
    except OSError:
        return False


def detect_host() -> Dict[str, object]:
    system = platform.system().lower()
    has_render_node = Path("/dev/dri/renderD128").exists()
    has_dri = Path("/dev/dri").exists()
    has_nvidia = shutil.which("nvidia-smi") is not None
    recommended_acceleration = "cpu"
    ram_gb = _ram_gb()
    return {
        "system": system,
        "release": platform.release(),
        "machine": platform.machine().lower(),
        "cpu_cores": os.cpu_count() or 1,
        "ram_gb": ram_gb,
        "docker_available": shutil.which("docker") is not None,
        "docker_reachable": _docker_reachable(),
        "has_dri": has_dri,
        "has_render_node": has_render_node,
        "has_nvidia": has_nvidia,
        "recommended_acceleration": recommended_acceleration,
        "recommended_model": ENV_DEFAULTS["DEFAULT_OLLAMA_MODEL"],
        "supports_gui": bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY") or system in {"windows", "darwin"}),
    }


def host_summary_lines(info: Dict[str, object]) -> List[str]:
    ram_text = f"{info['ram_gb']} GiB" if info.get("ram_gb") is not None else "unknown"
    return [
        f"OS: {info['system']} {info['release']}",
        f"Architektur: {info['machine']}",
        f"CPU-Kerne: {info['cpu_cores']}",
        f"RAM: {ram_text}",
        f"Docker installiert: {'ja' if info['docker_available'] else 'nein'}",
        f"Docker erreichbar: {'ja' if info['docker_reachable'] else 'nein'}",
        f"/dev/dri vorhanden: {'ja' if info['has_dri'] else 'nein'}",
        f"Render-Node vorhanden: {'ja' if info['has_render_node'] else 'nein'}",
        f"NVIDIA erkannt: {'ja' if info['has_nvidia'] else 'nein'}",
        f"Empfohlene Beschleunigung: {info['recommended_acceleration']}",
        f"Empfohlenes Standardmodell: {info['recommended_model']}",
    ]


def recommended_acceleration_options(info: Dict[str, object]) -> List[str]:
    options = ["cpu", "auto"]
    if info.get("system") == "linux" and info.get("has_render_node"):
        options.append("intel")
    return options


def get_host_ids(existing: Dict[str, str]) -> Tuple[str, str]:
    uid = existing.get("HOST_UID") or ENV_DEFAULTS["HOST_UID"]
    gid = existing.get("HOST_GID") or ENV_DEFAULTS["HOST_GID"]
    if hasattr(os, "getuid"):
        uid = str(os.getuid())
    if hasattr(os, "getgid"):
        gid = str(os.getgid())
    return uid, gid


def normalize_source_path(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        return candidate
    return str(Path(candidate).expanduser().resolve())


def is_placeholder_source(value: str | None) -> bool:
    if not value:
        return True
    candidate = value.strip()
    return not candidate or candidate == PLACEHOLDER_SOURCE


def source_path_valid(value: str | None) -> bool:
    if is_placeholder_source(value):
        return False
    try:
        return Path(str(value)).expanduser().exists()
    except OSError:
        return False


def needs_first_run_wizard(env: Dict[str, str]) -> bool:
    if env.get("BUILDER_SETUP_DONE") != "1":
        return True
    if is_placeholder_source(env.get("SOURCE_REPO_PATH")):
        return True
    if not source_path_valid(env.get("SOURCE_REPO_PATH")):
        return True
    if not env.get("HOST_UID") or not env.get("HOST_GID"):
        return True
    return False


def apply_setup_values(
    env: Dict[str, str],
    *,
    source_repo_path: str,
    default_model: str,
    acceleration: str,
    open_browser: bool,
) -> Dict[str, str]:
    merged = merge_env(env)
    uid, gid = get_host_ids(merged)
    merged["SOURCE_REPO_PATH"] = normalize_source_path(source_repo_path)
    merged["HOST_UID"] = uid
    merged["HOST_GID"] = gid
    merged["DEFAULT_OLLAMA_MODEL"] = default_model
    merged["BUILDER_ACCELERATION"] = acceleration
    merged["BUILDER_OPEN_BROWSER"] = "1" if open_browser else "0"
    merged["BUILDER_SETUP_DONE"] = "1"
    return merged
