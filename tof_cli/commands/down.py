from __future__ import annotations

import argparse

from tof_cli.core.compose_profile import builder_compose_profile
from tof_cli.core.docker_ops import compose_file_args, docker_exists, docker_reachable, run_docker_compose
from tof_cli.core.env_ops import ensure_env_file, read_env
from tof_cli.core.platform_profile import detect_platform


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("down", help="stop the builder stack")
    parser.add_argument("--remove-orphans", action="store_true", help="remove orphan containers")
    parser.set_defaults(handler=handle)


def handle(args: argparse.Namespace) -> int:
    ensure_env_file()
    env = read_env()
    platform_info = detect_platform()
    compose_profile = builder_compose_profile(env, platform_info)

    if not docker_exists():
        print("FAIL: docker is not installed or not on PATH.")
        return 1
    if not docker_reachable():
        print("FAIL: docker is installed but not reachable.")
        return 1

    compose_args = compose_file_args(compose_profile.files) + ["down"]
    if args.remove_orphans:
        compose_args.append("--remove-orphans")

    result = run_docker_compose(compose_args, capture_output=False, check=False)
    if result.returncode != 0:
        print(f"FAIL: docker compose exited with code {result.returncode}")
        return int(result.returncode)
    print("stack stopped")
    return 0
