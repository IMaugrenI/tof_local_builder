from __future__ import annotations

import json
import urllib.request

from tof_cli.core.docker_ops import run_docker


def ollama_tags(ollama_port: str) -> list[str]:
    url = f"http://127.0.0.1:{ollama_port}/api/tags"
    with urllib.request.urlopen(url, timeout=2.0) as response:
        payload = json.loads(response.read().decode("utf-8", errors="replace"))
    models = payload.get("models", [])
    tags: list[str] = []
    for model in models:
        if isinstance(model, dict):
            name = str(model.get("name", "")).strip()
            if name:
                tags.append(name)
    return tags


def ensure_default_model(model_name: str, ollama_port: str) -> tuple[bool, str]:
    if not model_name:
        return True, "DEFAULT_OLLAMA_MODEL is empty; skipped."
    try:
        tags = ollama_tags(ollama_port)
    except Exception as exc:
        return True, f"Ollama not ready yet; skipped default model pull ({exc})."
    if model_name in tags:
        return True, f"Default model already present: {model_name}"
    result = run_docker(["exec", "-i", "tof_local_builder_ollama", "ollama", "pull", model_name], capture_output=True, check=False)
    if result.returncode == 0:
        return True, f"Pulled default model: {model_name}"
    detail = (result.stderr or result.stdout or "").strip()
    return False, f"Failed to pull default model: {model_name} ({detail})"
