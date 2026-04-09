from __future__ import annotations

import argparse

from tof_cli.builder.repo_bridge_ops import sandbox_report, source_repo_report, tool_server_url
from tof_cli.core.env_ops import ensure_env_file, read_env
from tof_cli.core.path_ops import DEFAULT_SETUP_DIRS, ensure_directories
from tof_cli.core.platform_profile import detect_platform


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("setup", help="prepare local env and directories")
    parser.set_defaults(handler=handle)


def handle(_args: argparse.Namespace) -> int:
    env_path, created = ensure_env_file()
    env = read_env()
    ensure_directories(DEFAULT_SETUP_DIRS)
    source = source_repo_report(env)
    sandbox = sandbox_report(env)
    platform_info = detect_platform()

    print("setup complete")
    print(f"- env_path: {env_path}")
    print(f"- env_created: {'yes' if created else 'no'}")
    print(f"- platform: {platform_info.system} {platform_info.release} / {platform_info.machine}")
    print("- prepared_dirs:")
    for path in DEFAULT_SETUP_DIRS:
        print(f"  - {path}")
    print(f"- source_repo_path: {source['path']}")
    print(f"- source_repo_state: {source['state']}")
    print(f"- sandbox_path: {sandbox['path']}")
    print(f"- sandbox_state: {sandbox['state']}")
    print(f"- tool_server_url: {tool_server_url(env)}")
    if source["state"] != "ok":
        print("WARN: SOURCE_REPO_PATH is not ready yet.")
    return 0
