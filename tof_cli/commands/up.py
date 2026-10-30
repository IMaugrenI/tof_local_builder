from __future__ import annotations

import argparse

from tof_cli.builder.model_ops import ensure_default_model
from tof_cli.builder.repo_bridge_ops import tool_server_url
from tof_cli.builder.wizard_ops import ensure_wizard
from tof_cli.core.browser_ops import open_url
from tof_cli.ui.launcher import builder_ui_running, ensure_builder_ui
from tof_cli.core.compose_profile import builder_compose_profile
from tof_cli.core.docker_ops import compose_file_args, docker_exists, docker_reachable, run_docker_compose
from tof_cli.core.env_ops import ensure_env_file, env_bool, read_env
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

    # Open the existing Builder UI before checking Docker. This keeps
    # troubleshooting accessible even when the model runtime is unavailable.
    try:
        was_running = builder_ui_running(env)
        ui_ok, ui_address = ensure_builder_ui(env)
    except ValueError as exc:
        print(f"FAIL: invalid Builder UI configuration ({exc})")
        return 1
    if not ui_ok:
        print(f"FAIL: could not start Builder UI: {ui_address}")
        return 1
    if env_bool(env, "BUILDER_OPEN_BROWSER", default=True) and not was_running:
        if not open_url(ui_address):
            print(f"WARN: browser could not be opened. Open manually: {ui_address}")

    if not docker_exists():
        print("FAIL: docker is not installed or not on PATH.")
        return 1
    if not docker_reachable():
        print("FAIL: docker is installed but not reachable.")
        return 1

    # Compose up is repeatable and recreates only services whose configuration
    # or image changed. Do not tear down an already-running workspace first.
    # Stopping the workspace remains an explicit "down" operator action.
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
    print(f"- builder_ui: {ui_address}")
    print(f"- tool_server_url: {tool_server_url(env)}")

    return 0
