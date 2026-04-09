from __future__ import annotations

import argparse

from tof_cli.builder.model_ops import ollama_tags
from tof_cli.builder.repo_bridge_ops import tool_server_url
from tof_cli.core.env_ops import ensure_env_file, read_env
from tof_cli.core.health_ops import check_url, print_health_result


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("check", help="check builder health endpoints")
    parser.set_defaults(handler=handle)


def handle(_args: argparse.Namespace) -> int:
    ensure_env_file()
    env = read_env()
    failures = 0

    targets = [
        ("ollama", f"http://localhost:{env.get('OLLAMA_PORT', '11434')}/api/tags"),
        ("open_webui", f"http://localhost:{env.get('OPENWEBUI_PORT', '3000')}"),
        ("repo_bridge", f"{tool_server_url(env)}/health"),
        ("repo_bridge_openapi", f"{tool_server_url(env)}/openapi.json"),
    ]

    for label, url in targets:
        ok, detail = check_url(url)
        print_health_result(label, ok, detail)
        if not ok:
            failures += 1

    default_model = env.get("DEFAULT_OLLAMA_MODEL", "qwen2.5:0.5b")
    try:
        tags = ollama_tags(env.get("OLLAMA_PORT", "11434"))
        if default_model in tags:
            print(f"[OK] default_model: present ({default_model})")
        else:
            print(f"[FAIL] default_model: missing ({default_model})")
            failures += 1
    except Exception as exc:
        print(f"[FAIL] default_model: error ({exc})")
        failures += 1

    print(f"healthcheck finished: failures={failures}")
    return 0 if failures == 0 else 1
