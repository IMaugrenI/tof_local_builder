from __future__ import annotations

import argparse

from tof_cli.builder.model_ops import ensure_default_model
from tof_cli.builder.repo_bridge_ops import tool_server_url
from tof_cli.builder.wizard_ops import ensure_wizard
from tof_cli.core.compose_profile import builder_compose_profile
from tof_cli.core.docker_ops import compose_file_args, docker_exists, docker_reachable, run_docker_compose
from tof_cli.core.env_ops import ensure_env_file, read_env
from tof_cli.core.path_ops import DEFAULT_SETUP_DIRS, ensure_directories
from tof_cli.core.platform_profile import detect_platform


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("up", help="start the builder stack with docker compose")
    parser.add_argument("--skip-wizard", action="store_true", help="do not run the first-run wizard")
    parser.add_argument("--skip-model-ensure", action="store_true", help="do not ensure the default Ollama model")
    parser.set_defaults(handler=handle)


def handle(args: argparse.Namespace) -> int:
    ensure_env_file()
    ensure_directories(DEFAULT_SETUP_DIRS)

    if not args.skip_wizard:
        wizard_rc = ensure_wizard(force=False)
        if wizard_rc != 0:
            print(f"FAIL: setup wizard exited with code {wizard_rc}")
            return int(wizard_rc)

    env = read_env()
    platform_info = detect_platform()
    compose_profile = builder_compose_profile(env, platform_info)

    if not docker_exists():
        print("FAIL: docker is not installed or not on PATH.")
        return 1
    if not docker_reachable():
        print("FAIL: docker is installed but not reachable.")
        return 1

    down_args = compose_file_args(compose_profile.files) + ["down", "--remove-orphans"]
    run_docker_compose(down_args, capture_output=False, check=False)

    up_args = compose_file_args(compose_profile.files) + ["up", "-d", "--build"]
    result = run_docker_compose(up_args, capture_output=False, check=False)
    if result.returncode != 0:
        print(f"FAIL: docker compose exited with code {result.returncode}")
        return int(result.returncode)

    if not args.skip_model_ensure:
        ok, detail = ensure_default_model(env.get("DEFAULT_OLLAMA_MODEL", "qwen2.5:0.5b"), env.get("OLLAMA_PORT", "11434"))
        print(detail)
        if not ok:
            return 1

    print("stack started")
    print(f"- compose_files: {[str(path) for path in compose_profile.files]}")
    print(f"- compose_mode: {compose_profile.mode}")
    print(f"- open_webui: http://localhost:{env.get('OPENWEBUI_PORT', '3000')}")
    print(f"- tool_server_url: {tool_server_url(env)}")
    return 0
