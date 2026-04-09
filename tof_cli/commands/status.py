from __future__ import annotations

import argparse

from tof_cli.builder.repo_bridge_ops import sandbox_report, source_repo_report, tool_server_url
from tof_cli.core.compose_profile import builder_compose_profile
from tof_cli.core.docker_ops import compose_file_args, docker_exists, docker_reachable, run_docker_compose
from tof_cli.core.env_ops import ensure_env_file, read_env
from tof_cli.core.platform_profile import detect_platform


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("status", help="show platform and compose status")
    parser.set_defaults(handler=handle)


def handle(_args: argparse.Namespace) -> int:
    env_path, _ = ensure_env_file()
    env = read_env()
    platform_info = detect_platform()
    compose_profile = builder_compose_profile(env, platform_info)
    source = source_repo_report(env)
    sandbox = sandbox_report(env)

    print("runtime status")
    print(f"- env_path: {env_path}")
    print(f"- platform: {platform_info.system} {platform_info.release} / {platform_info.machine}")
    print(f"- cpu_cores: {platform_info.cpu_cores}")
    print(f"- has_dri: {platform_info.has_dri}")
    print(f"- has_render_node: {platform_info.has_render_node}")
    print(f"- supports_gui: {platform_info.supports_gui}")
    print(f"- compose_files: {[str(path) for path in compose_profile.files]}")
    print(f"- compose_mode: {compose_profile.mode}")
    print(f"- source_repo_path: {source['path']}")
    print(f"- source_repo_state: {source['state']}")
    print(f"- sandbox_path: {sandbox['path']}")
    print(f"- sandbox_state: {sandbox['state']}")
    print(f"- tool_server_url: {tool_server_url(env)}")

    if not docker_exists():
        print("- docker: missing")
        return 1
    if not docker_reachable():
        print("- docker: installed but not reachable")
        return 1

    compose_args = compose_file_args(compose_profile.files) + ["ps"]
    result = run_docker_compose(compose_args, capture_output=True, check=False)
    print("- compose_ps:")
    output = result.stdout.strip() if result.stdout else "(no output)"
    print(output)
    return 0 if result.returncode == 0 else int(result.returncode)
