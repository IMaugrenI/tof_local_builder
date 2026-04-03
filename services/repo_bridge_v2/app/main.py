from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="repo_bridge_v2",
    version="0.3.0",
    description=(
        "Controlled read/search/find/write bridge with explicit root separation. "
        "Bilingual aliases are provided for DE/EN usage."
    ),
)

allow_origins_raw = os.getenv("ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allow_origins = [item.strip() for item in allow_origins_raw.split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SOURCE_ROOT = Path(os.getenv("SOURCE_ROOT", "/workspace/source_repo_ro")).resolve()
SANDBOX_ROOT = Path(os.getenv("SANDBOX_ROOT", "/workspace/builder_sandbox")).resolve()
WORKSPACE_ROOT = (SANDBOX_ROOT / "workspace").resolve()
OUTPUT_ROOT = (SANDBOX_ROOT / "output").resolve()

ROOTS = {
    "source": SOURCE_ROOT,
    "workspace": WORKSPACE_ROOT,
    "output": OUTPUT_ROOT,
}
ROOT_ALIASES = {
    "source": "source",
    "quelle": "source",
    "workspace": "workspace",
    "arbeitsbereich": "workspace",
    "output": "output",
    "ausgabe": "output",
}


class WriteRequest(BaseModel):
    target_root: str = Field(default="output", description="output|workspace or ausgabe|arbeitsbereich")
    relative_path: str = Field(..., description="relative file path inside the selected writable root")
    content: str
    overwrite: bool = False


class MkdirRequest(BaseModel):
    target_root: str = Field(default="workspace", description="workspace|output or arbeitsbereich|ausgabe")
    relative_path: str = Field(..., description="relative folder path inside the selected writable root")


def normalize_root_name(root_name: str, *, writable_only: bool = False) -> str:
    key = (root_name or "source").strip().lower()
    normalized = ROOT_ALIASES.get(key)
    if not normalized:
        raise HTTPException(status_code=400, detail="Unknown root. Use source/workspace/output or quelle/arbeitsbereich/ausgabe.")
    if writable_only and normalized == "source":
        raise HTTPException(status_code=400, detail="Source root is read-only.")
    return normalized


def within(base: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(base)
        return True
    except ValueError:
        return False


def resolve_root(root_name: str, *, writable_only: bool = False) -> tuple[str, Path]:
    normalized = normalize_root_name(root_name, writable_only=writable_only)
    return normalized, ROOTS[normalized]


def resolve_candidate(root_name: str, rel_path: str = "", *, writable_only: bool = False) -> tuple[str, Path, Path]:
    normalized, base = resolve_root(root_name, writable_only=writable_only)
    safe_rel = (rel_path or "").strip()
    candidate = (base / safe_rel).resolve() if safe_rel else base
    if not within(base, candidate):
        raise HTTPException(status_code=400, detail="Path escapes selected root.")
    return normalized, base, candidate


def rel_to(base: Path, value: Path) -> str:
    if value == base:
        return "."
    return value.relative_to(base).as_posix()


def is_probably_text(path: Path, max_bytes: int = 200000) -> tuple[bool, str]:
    raw = path.read_bytes()[:max_bytes]
    try:
        return True, raw.decode("utf-8")
    except UnicodeDecodeError:
        return False, raw.hex()


def iter_files(base: Path, start: Path) -> Iterable[Path]:
    if start.is_file():
        yield start
        return
    for candidate in sorted(start.rglob("*")):
        if candidate.is_file():
            yield candidate


@app.get("/health", tags=["system"])
@app.get("/gesundheit", include_in_schema=False)
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "roots": {
            "source": str(SOURCE_ROOT),
            "workspace": str(WORKSPACE_ROOT),
            "output": str(OUTPUT_ROOT),
        },
    }


@app.get("/roots", tags=["reader"])
@app.get("/wurzeln", include_in_schema=False)
def roots() -> dict[str, object]:
    return {
        "source_root": str(SOURCE_ROOT),
        "workspace_root": str(WORKSPACE_ROOT),
        "output_root": str(OUTPUT_ROOT),
        "aliases": ROOT_ALIASES,
    }


@app.get("/tree", tags=["reader"])
@app.get("/baum", include_in_schema=False)
def tree(root: str = "source", path: str = "") -> dict[str, object]:
    normalized, base, candidate = resolve_candidate(root, path)
    if not candidate.exists():
        raise HTTPException(status_code=404, detail="Selected path was not found.")
    if candidate.is_file():
        return {
            "root": normalized,
            "path": rel_to(base, candidate),
            "entries": [
                {
                    "name": candidate.name,
                    "type": "file",
                    "size": candidate.stat().st_size,
                }
            ],
        }
    entries: list[dict[str, object]] = []
    for child in sorted(candidate.iterdir()):
        entries.append(
            {
                "name": child.name,
                "type": "dir" if child.is_dir() else "file",
                "size": None if child.is_dir() else child.stat().st_size,
            }
        )
    return {
        "root": normalized,
        "path": rel_to(base, candidate),
        "entries": entries,
    }


@app.get("/stat", tags=["reader"])
@app.get("/status", include_in_schema=False)
def stat(root: str = "source", path: str = "") -> dict[str, object]:
    normalized, base, candidate = resolve_candidate(root, path)
    if not candidate.exists():
        raise HTTPException(status_code=404, detail="Selected path was not found.")
    return {
        "root": normalized,
        "path": rel_to(base, candidate),
        "name": candidate.name if candidate != base else ".",
        "type": "dir" if candidate.is_dir() else "file",
        "size": None if candidate.is_dir() else candidate.stat().st_size,
        "exists": True,
    }


@app.get("/read", tags=["reader"])
@app.get("/lesen", include_in_schema=False)
def read(root: str = "source", path: str = "", max_bytes: int = 200000) -> dict[str, object]:
    normalized, base, candidate = resolve_candidate(root, path)
    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Selected file was not found.")
    is_text, content = is_probably_text(candidate, max_bytes=max_bytes)
    return {
        "root": normalized,
        "path": rel_to(base, candidate),
        "kind": "text" if is_text else "binary_hex",
        "size": candidate.stat().st_size,
        "content": content,
    }


@app.get("/find", tags=["search"])
@app.get("/finden", include_in_schema=False)
def find(root: str = "source", path: str = "", query: str = "", limit: int = 50) -> dict[str, object]:
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")
    normalized, base, candidate = resolve_candidate(root, path)
    if not candidate.exists():
        raise HTTPException(status_code=404, detail="Selected path was not found.")
    query_lower = query.strip().lower()
    matches: list[dict[str, object]] = []
    iterable = [candidate] if candidate.is_file() else sorted(candidate.rglob("*"))
    for item in iterable:
        if query_lower in item.name.lower():
            matches.append(
                {
                    "path": rel_to(base, item),
                    "type": "dir" if item.is_dir() else "file",
                }
            )
            if len(matches) >= max(1, min(limit, 200)):
                break
    return {
        "root": normalized,
        "path": rel_to(base, candidate),
        "query": query,
        "matches": matches,
    }


@app.get("/search", tags=["search"])
@app.get("/suche", include_in_schema=False)
def search(root: str = "source", path: str = "", query: str = "", limit: int = 50, max_file_bytes: int = 200000) -> dict[str, object]:
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")
    normalized, base, candidate = resolve_candidate(root, path)
    if not candidate.exists():
        raise HTTPException(status_code=404, detail="Selected path was not found.")
    query_lower = query.lower()
    matches: list[dict[str, object]] = []
    for file_path in iter_files(base, candidate):
        if file_path.stat().st_size > max_file_bytes:
            continue
        is_text, content = is_probably_text(file_path, max_bytes=max_file_bytes)
        if not is_text:
            continue
        for line_number, line in enumerate(content.splitlines(), start=1):
            if query_lower in line.lower():
                matches.append(
                    {
                        "path": rel_to(base, file_path),
                        "line_number": line_number,
                        "excerpt": line[:240],
                    }
                )
                if len(matches) >= max(1, min(limit, 200)):
                    return {
                        "root": normalized,
                        "path": rel_to(base, candidate),
                        "query": query,
                        "matches": matches,
                    }
    return {
        "root": normalized,
        "path": rel_to(base, candidate),
        "query": query,
        "matches": matches,
    }


@app.post("/mkdir", tags=["writer"])
@app.post("/ordner", include_in_schema=False)
def mkdir(req: MkdirRequest) -> dict[str, object]:
    normalized, base, candidate = resolve_candidate(req.target_root, req.relative_path, writable_only=True)
    if not req.relative_path.strip():
        raise HTTPException(status_code=400, detail="relative_path must not be empty.")
    candidate.mkdir(parents=True, exist_ok=True)
    return {
        "status": "ok",
        "root": normalized,
        "path": rel_to(base, candidate),
        "created_path": str(candidate),
    }


@app.post("/write", tags=["writer"])
@app.post("/schreiben", include_in_schema=False)
def write(req: WriteRequest) -> dict[str, object]:
    normalized, base, candidate = resolve_candidate(req.target_root, req.relative_path, writable_only=True)
    if not req.relative_path.strip():
        raise HTTPException(status_code=400, detail="relative_path must not be empty.")
    if candidate.exists() and candidate.is_dir():
        raise HTTPException(status_code=400, detail="Target path points to a directory.")
    if candidate.exists() and not req.overwrite:
        raise HTTPException(status_code=409, detail="Target exists.")
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text(req.content, encoding="utf-8")
    return {
        "status": "ok",
        "root": normalized,
        "path": rel_to(base, candidate),
        "written_path": str(candidate),
        "bytes_written": len(req.content.encode("utf-8")),
    }
