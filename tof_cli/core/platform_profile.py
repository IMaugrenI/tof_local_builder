from __future__ import annotations

from dataclasses import asdict, dataclass
import os
import platform
from pathlib import Path


@dataclass(frozen=True)
class PlatformProfile:
    system: str
    release: str
    machine: str
    cpu_cores: int
    supports_host_ids: bool
    has_dri: bool
    has_render_node: bool
    has_nvidia: bool
    supports_gui: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def detect_platform() -> PlatformProfile:
    system = platform.system().lower()
    return PlatformProfile(
        system=system,
        release=platform.release(),
        machine=platform.machine().lower(),
        cpu_cores=os.cpu_count() or 1,
        supports_host_ids=(system == "linux"),
        has_dri=Path("/dev/dri").exists(),
        has_render_node=Path("/dev/dri/renderD128").exists(),
        has_nvidia=bool(os.environ.get("NVIDIA_VISIBLE_DEVICES")) or Path("/proc/driver/nvidia").exists(),
        supports_gui=bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY") or system in {"windows", "darwin"}),
    )
