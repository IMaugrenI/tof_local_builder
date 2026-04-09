from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tof_cli.core.env_ops import REPO_ROOT
from tof_cli.core.platform_profile import PlatformProfile


@dataclass(frozen=True)
class ComposeProfile:
    files: list[Path]
    mode: str


def builder_compose_profile(env: dict[str, str], platform_info: PlatformProfile) -> ComposeProfile:
    mode = env.get("BUILDER_ACCELERATION", "cpu").strip().lower() or "cpu"
    files = [REPO_ROOT / "compose.yml"]
    intel_overlay = REPO_ROOT / "deploy" / "compose" / "compose.intel.yml"

    if mode == "intel":
        if platform_info.system == "linux" and platform_info.has_render_node:
            return ComposeProfile(files=files + [intel_overlay], mode="intel")
        return ComposeProfile(files=files, mode="cpu")

    if mode == "auto":
        if platform_info.system == "linux" and platform_info.has_render_node:
            return ComposeProfile(files=files + [intel_overlay], mode="intel")
        return ComposeProfile(files=files, mode="cpu")

    return ComposeProfile(files=files, mode="cpu")
