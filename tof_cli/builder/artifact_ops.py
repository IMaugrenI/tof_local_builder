"""Read-only review inventory for generated Builder sandbox artifacts.

This module does not alter, import, stage or commit project files.
"""
from __future__ import annotations

import difflib
import hashlib
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


def _review_token(
    source: dict[str, str], sandbox: Path, area: str, relative: str,
    generated: bytes,
) -> str | None:
    """Bind the mark to BOTH generated content and the current original."""
    source_identity = source["path"] if source["state"] == "ok" else "unconfigured"
    source_hash = "unconfigured"
    if source["state"] == "ok":
        root = Path(source["path"]).resolve()
        candidate = root.joinpath(*PurePosixPath(relative).parts)
        if candidate.is_symlink() or not candidate.resolve().is_relative_to(root):
            return None
        if candidate.exists():
            if not candidate.is_file() or candidate.stat().st_size > MAX_PREVIEW_BYTES:
                return None
            source_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
        else:
            source_hash = "new_file"
    fingerprint = hashlib.sha256(generated).hexdigest()
    identity = f"{source_identity}|{sandbox}|{area}|{relative}|{fingerprint}|{source_hash}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def artifact_inventory(env: dict[str, str], *, limit: int = MAX_ITEMS) -> dict[str, object]:
    sandbox = _resolve_sandbox(env)
    if sandbox is None:
        return {"status": "unavailable", "items": [], "reason": "Missing or overlapping sandbox/source paths"}
    items: list[dict[str, object]] = []
    source = source_repo_report(env)
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
            previewable = path.suffix.lower() in PREVIEW_SUFFIXES and stat.st_size <= MAX_PREVIEW_BYTES
            review_token = None
            if previewable:
                review_token = _review_token(source, sandbox, area, relative, path.read_bytes())
            items.append({
                "area": area,
                "path": relative,
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                "previewable": previewable,
                "review_token": review_token,
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


MAX_DIFF_LINES = 350


def artifact_diff(env: dict[str, str], area: str, relative_path: str) -> dict[str, object]:
    """Compare generated text with the *same relative path* in the read-only source.

    The preview constraints also apply to diffs. There are no file writes,
    commits, automatic applies, or arbitrary host paths in this operation.
    """
    # Enforce all output-path, extension, size, encoding and symlink guards.
    candidate = artifact_preview(env, area, relative_path)
    source = source_repo_report(env)
    if source["state"] != "ok":
        return {"status": "source_unavailable", "area": area, "path": relative_path}

    root = Path(source["path"]).resolve()
    # PurePosixPath normalizes '..' and '.', but artifact_preview has already
    # rejected them in the original input before we form this source path.
    parts = PurePosixPath(relative_path).parts
    original = root.joinpath(*parts)
    if original.is_symlink() or not original.resolve().is_relative_to(root):
        raise ValueError("Source file is outside the selected project")
    if not original.exists():
        return {"status": "new_file", "area": area, "path": relative_path}
    if not original.is_file():
        raise ValueError("Original path is not a regular file")
    if original.stat().st_size > MAX_PREVIEW_BYTES:
        return {"status": "source_too_large", "area": area, "path": relative_path}
    try:
        source_text = original.read_text(encoding="utf-8")
    except (UnicodeError, OSError) as exc:
        raise ValueError("Source is not a readable UTF-8 text file") from exc
    if chr(0) in source_text or chr(0) in candidate["content"]:
        raise ValueError("Binary text is not eligible for comparison")
    diff_lines = list(difflib.unified_diff(
        source_text.splitlines(keepends=True),
        candidate["content"].splitlines(keepends=True),
        fromfile=f"source/{relative_path}",
        tofile=f"{area}/{relative_path}",
    ))
    return {
        "status": "identical" if not diff_lines else "changed",
        "area": area,
        "path": relative_path,
        "diff": "".join(diff_lines[:MAX_DIFF_LINES]),
        "truncated": len(diff_lines) > MAX_DIFF_LINES,
        "read_only": True,
    }


def artifact_handoff(
    env: dict[str, str], area: str, relative_path: str, expected_token: str,
) -> dict[str, object]:
    """Provide a complete, review-bound text handoff; NEVER edit the source.

    The token binds the exact candidate bytes, source root and sandbox root.
    It is a staleness check, *not* an authorization credential. The browser
    controls the reviewed state, while the operator still applies work manually.
    """
    if not isinstance(expected_token, str) or len(expected_token) != 64:
        raise ValueError("Missing or invalid review token")
    if any(ch not in "0123456789abcdef" for ch in expected_token):
        raise ValueError("Invalid review token")
    generated = artifact_preview(env, area, relative_path)
    sandbox = _resolve_sandbox(env)
    source = source_repo_report(env)
    if sandbox is None or source["state"] != "ok":
        raise ValueError("Source and separate sandbox must be configured")
    if chr(0) in generated["content"]:
        raise ValueError("Binary text cannot be handed off")
    source_path = Path(source["path"]).resolve()
    current_token = _review_token(
        source, sandbox, area, relative_path, generated["content"].encode("utf-8")
    )
    if current_token != expected_token:
        raise ValueError("Generated file changed; repeat preview and review")
    comparison = artifact_diff(env, area, relative_path)
    if comparison["status"] == "changed":
        if comparison["truncated"]:
            raise ValueError("Diff is truncated; inspect the complete file manually")
        transfer = comparison["diff"]
        kind = "unified_diff"
    elif comparison["status"] == "new_file":
        # No original file exists; the generated content is complete and bounded.
        transfer = generated["content"]
        kind = "new_file_text"
    elif comparison["status"] == "identical":
        transfer = ""
        kind = "no_changes"
    else:
        raise ValueError("The source cannot be safely compared for handoff")
    if _review_token(source, sandbox, area, relative_path,
                     generated["content"].encode("utf-8")) != expected_token:
        raise ValueError("Source changed during comparison; review again")
    return {
        "status": "ready", "kind": kind, "area": area, "path": relative_path,
        "content": transfer, "review_token": expected_token,
        "source": str(source_path), "read_only": True,
        "requires_manual_adoption": True,
    }
