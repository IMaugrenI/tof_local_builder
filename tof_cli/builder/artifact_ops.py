"""Read-only review inventory for generated Builder sandbox artifacts.

This module does not alter, import, stage or commit project files.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from tof_cli.builder.repo_bridge_ops import sandbox_report, source_repo_report

ALLOWED_AREAS = ("workspace", "output")
MAX_ITEMS = 100
MAX_PREVIEW_BYTES = 32_768
PREVIEW_SUFFIXES = frozenset({
    ".txt", ".md", ".markdown", ".py", ".json", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".csv", ".html", ".css", ".js", ".ts", ".sh",
})


def _resolve_sandbox(env: dict[str, str]) -> Path | None:
    report = sandbox_report(env)
    if report["state"] != "ok":
        return None
    sandbox = Path(report["path"]).resolve()
    source = source_repo_report(env)
    if source["state"] == "ok":
        source_path = Path(source["path"]).resolve()
        if sandbox == source_path or sandbox in source_path.parents or source_path in sandbox.parents:
            return None
    return sandbox


def _get_area(sandbox: Path, area: str) -> Path:
    if area not in ALLOWED_AREAS:
        raise ValueError("Only workspace and output can be inspected")
    base = sandbox / area
    if base.is_symlink() or (base.exists() and base.resolve() != base):
        raise ValueError("Sandbox area must not be a symlink")
    return base


def artifact_inventory(env: dict[str, str], *, limit: int = MAX_ITEMS) -> dict[str, object]:
    sandbox = _resolve_sandbox(env)
    if sandbox is None:
        return {"status": "unavailable", "items": [], "reason": "Missing or overlapping sandbox/source paths"}
    items: list[dict[str, object]] = []
    total = 0
    for area in ALLOWED_AREAS:
        try:
            base = _get_area(sandbox, area)
        except ValueError:
            return {"status": "unavailable", "items": [], "reason": "Unsafe sandbox area"}
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_symlink() or not path.is_file():
                continue
            # Resolved containment additionally protects against symlinked ancestors.
            try:
                relative = path.resolve().relative_to(base.resolve()).as_posix()
            except ValueError:
                continue
            total += 1
            if len(items) >= min(MAX_ITEMS, max(1, limit)):
                continue
            stat = path.stat()
            items.append({
                "area": area,
                "path": relative,
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                "previewable": path.suffix.lower() in PREVIEW_SUFFIXES and stat.st_size <= MAX_PREVIEW_BYTES,
            })
    items.sort(key=lambda item: (item["modified_at"], item["area"], item["path"]), reverse=True)
    return {
        "status": "ok",
        "items": items,
        "total": total,
        "truncated": total > len(items),
        "source_is_read_only": True,
    }


def artifact_preview(env: dict[str, str], area: str, relative_path: str) -> dict[str, object]:
    sandbox = _resolve_sandbox(env)
    if sandbox is None:
        raise ValueError("Sandbox path is unavailable or overlaps source")
    base = _get_area(sandbox, area)
    path = PurePosixPath(relative_path)
    if not relative_path or relative_path.startswith("/") or path.is_absolute() or any(
        part in {".", ".."} for part in path.parts
    ) or "\\" in relative_path:
        raise ValueError("Invalid relative artifact path")
    target = base.joinpath(*path.parts)
    if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(base.resolve()):
        raise ValueError("Artifact path is unavailable or outside sandbox")
    if target.suffix.lower() not in PREVIEW_SUFFIXES or target.stat().st_size > MAX_PREVIEW_BYTES:
        raise ValueError("Only small known text files can be previewed")
    try:
        text = target.read_text(encoding="utf-8")
    except UnicodeError as exc:
        raise ValueError("Artifact is not a UTF-8 text file") from exc
    return {"area": area, "path": relative_path, "content": text, "read_only": True}
