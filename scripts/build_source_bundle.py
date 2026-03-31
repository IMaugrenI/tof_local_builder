#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path
from typing import Iterable

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".idea",
    ".vscode",
}

ALLOWED_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".sh",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".sql",
    ".env",
    ".conf",
}

LANG_BY_SUFFIX = {
    ".md": "markdown",
    ".txt": "text",
    ".py": "python",
    ".sh": "bash",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".json": "json",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".sql": "sql",
    ".env": "bash",
    ".conf": "text",
}


def read_env_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def resolve_paths(repo_root: Path) -> tuple[Path, Path]:
    env = read_env_file(repo_root / ".env")
    source_repo = env.get("SOURCE_REPO_PATH")
    if not source_repo:
        raise SystemExit("SOURCE_REPO_PATH is missing in .env")
    sandbox_value = env.get("BUILDER_SANDBOX_PATH", "./sandbox")
    source_path = Path(source_repo).expanduser().resolve()
    sandbox_path = Path(sandbox_value).expanduser()
    if not sandbox_path.is_absolute():
        sandbox_path = (repo_root / sandbox_path).resolve()
    return source_path, sandbox_path


def iter_files(root: Path, max_bytes: int, max_files: int) -> list[Path]:
    selected: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_dir() and path.name in EXCLUDED_DIRS:
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > max_bytes:
            continue
        selected.append(path)
        if len(selected) >= max_files:
            break
    return selected


def build_tree_lines(root: Path, files: Iterable[Path]) -> list[str]:
    lines = []
    for file_path in files:
        rel = file_path.relative_to(root)
        lines.append(str(rel))
    return lines


def language_for(path: Path) -> str:
    return LANG_BY_SUFFIX.get(path.suffix.lower(), "text")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a source bundle for Open WebUI review")
    parser.add_argument("--name", default="source_snapshot", help="Bundle name prefix")
    parser.add_argument("--max-bytes", type=int, default=200_000, help="Maximum size per included file")
    parser.add_argument("--max-files", type=int, default=200, help="Maximum number of files to include")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    source_root, sandbox_root = resolve_paths(repo_root)

    output_dir = sandbox_root / "output" / "source_bundle"
    output_dir.mkdir(parents=True, exist_ok=True)

    files = iter_files(source_root, max_bytes=args.max_bytes, max_files=args.max_files)
    if not files:
        raise SystemExit("No eligible files found. Check SOURCE_REPO_PATH and file filters.")

    generated_at = dt.datetime.now(dt.timezone.utc).isoformat()
    tree_lines = build_tree_lines(source_root, files)

    manifest_path = output_dir / f"{args.name}_manifest.txt"
    tree_path = output_dir / f"{args.name}_tree.txt"
    bundle_path = output_dir / f"{args.name}_bundle.md"

    manifest_path.write_text(
        "\n".join(
            [
                f"generated_at={generated_at}",
                f"source_root={source_root}",
                f"file_count={len(files)}",
                f"max_bytes={args.max_bytes}",
                f"max_files={args.max_files}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    tree_path.write_text("\n".join(tree_lines) + "\n", encoding="utf-8")

    bundle_parts = [
        "# Source snapshot bundle",
        "",
        f"Generated at: `{generated_at}`",
        f"Source root: `{source_root}`",
        f"Included file count: `{len(files)}`",
        "",
        "## Included paths",
        "",
    ]
    bundle_parts.extend(f"- `{line}`" for line in tree_lines)
    bundle_parts.append("")
    bundle_parts.append("## File contents")
    bundle_parts.append("")

    for path in files:
        rel = path.relative_to(source_root)
        bundle_parts.append(f"### `{rel}`")
        bundle_parts.append("")
        bundle_parts.append(f"Path: `{rel}`")
        bundle_parts.append("")
        bundle_parts.append(f"```{language_for(path)}")
        try:
            bundle_parts.append(path.read_text(encoding="utf-8", errors="replace"))
        except OSError as exc:
            bundle_parts.append(f"<unreadable: {exc}>")
        bundle_parts.append("```")
        bundle_parts.append("")

    bundle_path.write_text("\n".join(bundle_parts), encoding="utf-8")

    print(f"Wrote: {manifest_path}")
    print(f"Wrote: {tree_path}")
    print(f"Wrote: {bundle_path}")


if __name__ == "__main__":
    main()
