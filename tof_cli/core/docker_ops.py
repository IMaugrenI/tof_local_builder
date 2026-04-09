from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from tof_cli.core.env_ops import REPO_ROOT


def docker_exists() -> bool:
    return shutil.which("docker") is not None


def docker_reachable() -> bool:
    if not docker_exists():
        return False
    try:
        result = subprocess.run(
            ["docker", "info"],
            cwd=REPO_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return result.returncode == 0
    except OSError:
        return False


def run_docker_compose(args: list[str], *, capture_output: bool = False, check: bool = False) -> subprocess.CompletedProcess[str]:
    command = ["docker", "compose", *args]
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=capture_output,
        check=check,
    )


def run_docker(args: list[str], *, capture_output: bool = False, check: bool = False) -> subprocess.CompletedProcess[str]:
    command = ["docker", *args]
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=capture_output,
        check=check,
    )


def compose_file_args(files: list[Path]) -> list[str]:
    args: list[str] = []
    for file in files:
        args.extend(["-f", str(file)])
    return args
