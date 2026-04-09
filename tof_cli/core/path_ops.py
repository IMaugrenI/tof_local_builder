from __future__ import annotations

from pathlib import Path

from tof_cli.core.env_ops import REPO_ROOT

DEFAULT_SETUP_DIRS = [
    REPO_ROOT / "data" / "ollama",
    REPO_ROOT / "data" / "open-webui",
    REPO_ROOT / "sandbox" / "workspace",
    REPO_ROOT / "sandbox" / "output",
    REPO_ROOT / "sandbox" / "examples",
]


def ensure_directories(paths: list[Path]) -> list[Path]:
    created: list[Path] = []
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
        created.append(path)
    return created


def normalize_path(raw: str) -> Path:
    return Path(raw).expanduser().resolve()


def path_state(path: Path) -> str:
    if path.exists() and path.is_dir():
        return "ok"
    if path.exists():
        return "exists_not_dir"
    return "missing"
