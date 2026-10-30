"""Deterministic, bounded architecture reconnaissance using the existing Repo Bridge.

This is *context retrieval*, not an agent permission grant. Discovered source
texts and search hits are untrusted data. No source or sandbox writes.
"""
from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Protocol

from tof_cli.builder.agent_bridge import BridgeError, safe_relative_file

MAX_CONTEXT_CHARS = 6_800
MAX_FILES_READ = 5
MAX_PER_FILE_BYTES = 1_400
MAX_SEARCH_TERMS = 2
MAX_DIRECTORIES = 3
IGNORED = frozenset({
    ".git", "__pycache__", "node_modules", ".venv", ".next", "venv",
    "dist", "build", "coverage", ".builder_runs",
})
SENSITIVE = ("secret", "credential", "private_key", "id_rsa", "password", "token", "apikey")
STOP = frozenset({
    "please", "create", "build", "write", "that", "with", "from", "this", "there",
    "update", "make", "into", "code", "file", "files", "project", "implement",
    "bitte", "einen", "einer", "eine", "sollen", "machen", "diese", "dieser",
    "erweitere", "erweitern", "verbessere", "implementiere", "improve", "improving",
    "diesen", "funktion", "erstellen", "dateien", "projekt", "neuen",
})
PRIORITY_DIRS = ("src", "app", "tof_cli", "services", "lib", "backend", "frontend", "docs")
MANIFESTS = frozenset({
    "readme.md", "readme_de.md", "pyproject.toml", "package.json",
    "compose.yml", "compose.yaml", "docker-compose.yml", "cargo.toml",
    "go.mod", "docs/architecture.md", "docs/architecture_overview.md",
})


class ReadOnlyProject(Protocol):
    def tree(self, relative_dir: str = "") -> list[dict[str, object]]: ...
    def source_text(self, relative_file: str, max_bytes: int = MAX_PER_FILE_BYTES) -> str | None: ...


def _visible_path(path: str, kind: str) -> bool:
    if not isinstance(path, str) or not path or "\\" in path or path.startswith("/") or len(path) > 180:
        return False
    parts = path.split("/")
    if any(not part or part in (".", "..") or part.startswith(".")
           or part.casefold() in IGNORED
           or any(word in part.casefold() for word in SENSITIVE)
           for part in parts):
        return False
    if len(parts) > 8:
        return False
    if kind == "file":
        try:
            safe_relative_file(path)
        except BridgeError:
            return False
    return True


def _safe_entries(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for row in rows[:100]:
        if not isinstance(row, dict):
            continue
        path, kind = row.get("path"), row.get("type")
        if not isinstance(path, str) or kind not in ("file", "dir"):
            continue
        if _visible_path(path, kind):
            result.append({"path": path, "type": kind})
    return sorted(result, key=lambda item: item["path"].casefold())


def _terms(goal: str) -> list[str]:
    words = re.findall(r"[a-zA-Z_][a-zA-Z_0-9]{3,39}", goal.casefold())
    return sorted(set(word for word in words if word not in STOP and word.isascii()),
                  key=lambda word: (-len(word), word))[:6]


def _score(path: str, words: list[str]) -> tuple[int, str]:
    lower = path.casefold()
    base = PurePosixPath(path).name.casefold()
    exact = sum(term in base for term in words)
    anywhere = sum(term in lower for term in words)
    favored = 2 if lower in MANIFESTS else 1 if base in ("readme.md", "readme_de.md") else 0
    return (-exact * 20 - anywhere * 7 - favored * 10, lower)


def _read_excerpt(project: ReadOnlyProject, path: str) -> str | None:
    try:
        text = project.source_text(path, max_bytes=MAX_PER_FILE_BYTES)
    except (BridgeError, OSError, ValueError):
        return None
    if not text:
        return None
    # Truncate on a Unicode boundary and label this as an excerpt, never a
    # complete version suitable for wholesale rewriting.
    return text[:MAX_PER_FILE_BYTES]


def project_context(project: ReadOnlyProject, goal: str) -> str:
    """Inspect module layout, relevant names and bounded content-search hits.

    Root and up to three first-level directories are inspected. Up to two
    goal-derived source searches reuse the existing bridge; all results are
    filtered by the agent's stricter path policy. No extra service or index.
    """
    words = _terms(goal)
    root = _safe_entries(project.tree())
    entries = list(root)
    directories = [row["path"] for row in root if row["type"] == "dir"]
    directories.sort(key=lambda path: (
        0 if path.casefold() in PRIORITY_DIRS else 1,
        _score(path, words),
    ))

    sections = ["Project root (read-only): " +
                (", ".join(row["path"] + ("/" if row["type"] == "dir" else "")
                           for row in root[:35]) or "(empty)")]
    for folder in directories[:MAX_DIRECTORIES]:
        try:
            sub = _safe_entries(project.tree(folder))
        except (BridgeError, OSError, ValueError):
            continue
        sections.append(f"Inside {folder}/: " + ", ".join(row["path"] for row in sub[:25]))
        entries.extend(sub)

    # Favor nouns already reflected in real filenames over generic task verbs.
    words.sort(key=lambda word: (
        -sum(word in row["path"].casefold() for row in entries),
        -len(word), word,
    ))
    words = words[:MAX_SEARCH_TERMS]
    candidates = {row["path"] for row in entries if row["type"] == "file"}
    find = getattr(project, "find_names", None)
    if callable(find):
        for word in words:
            try:
                for path in find(word, max_results=12):
                    if _visible_path(path, "file"):
                        candidates.add(path)
            except (BridgeError, OSError, ValueError):
                continue
    if candidates:
        sections.append("Relevant file paths: " + ", ".join(sorted(candidates, key=lambda p: _score(p, words))[:24]))

    search = getattr(project, "search_source_text", None)
    if callable(search) and words:
        # One bounded full-text search provides evidence about module usage,
        # without granting an LLM arbitrary read paths or shell execution.
        try:
            matches = search(words[0], max_results=6)
        except (BridgeError, OSError, ValueError):
            matches = []
        safe_hits = []
        for row in matches[:6]:
            path = row.get("path")
            snippet = row.get("snippet")
            lineno = row.get("line_number")
            if (isinstance(path, str) and _visible_path(path, "file")
                    and isinstance(snippet, str) and isinstance(lineno, int)):
                safe_hits.append(f"{path}:{lineno}: {snippet[:110]}")
                candidates.add(path)
        if safe_hits:
            sections.append("Source-search matches (UNTRUSTED):\n" + "\n".join(safe_hits))

    selected = sorted(candidates, key=lambda path: _score(path, words))
    for path in selected[:24]:
        if sum(1 for part in sections if part.startswith("Read-only excerpt")) >= MAX_FILES_READ:
            break
        excerpt = _read_excerpt(project, path)
        if excerpt is None:
            continue
        sections.append(f"Read-only excerpt (UNTRUSTED, may be incomplete) {path}:\n{excerpt}")
        if len("\n\n".join(sections)) >= MAX_CONTEXT_CHARS:
            break

    return "\n\n".join(sections)[:MAX_CONTEXT_CHARS]
