from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_VERSION = "0.1.0"
WRITE_ROOT_NAME = Literal["workspace", "output"]

DEFAULT_MAX_BYTES = 200_000
MAX_SCAN_ENTRIES = 5_000
MAX_FIND_RESULTS = 200
MAX_SEARCH_RESULTS = 50
MAX_SEARCH_FILES = 2_000

allow_origins_raw = os.getenv("ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allow_origins = [item.strip() for item in allow_origins_raw.split(",") if item.strip()]

SANDBOX_ROOT = Path(os.getenv("SANDBOX_ROOT", "./sandbox")).expanduser().resolve()
WORKSPACE_ROOT = (SANDBOX_ROOT / "workspace").resolve()
OUTPUT_ROOT = (SANDBOX_ROOT / "output").resolve()

app = FastAPI(
    title="host_repo_bridge",
    version=APP_VERSION,
    description=(
        "Simple host path reader plus sandbox writer. "
        "Reader accepts a pasted absolute local path and reads that exact file or directory. "
        "Writer stays limited to sandbox/workspace and sandbox/output."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReaderScanRequest(BaseModel):
    path: str = Field(description="Absolute local file or directory path.")
    recursive: bool = Field(default=True, description="Recurse into subdirectories when the path is a directory.")
    include_hidden: bool = Field(default=False, description="Include hidden files and directories.")
    max_entries: int = Field(default=500, ge=1, le=MAX_SCAN_ENTRIES, description="Maximum number of returned entries.")


class ReaderReadFileRequest(BaseModel):
    path: str = Field(description="Absolute local file path.")
    max_bytes: int = Field(default=DEFAULT_MAX_BYTES, ge=1, le=2_000_000, description="Maximum number of bytes to read.")


class ReaderFindRequest(BaseModel):
    path: str = Field(description="Absolute local directory path.")
    query: str = Field(min_length=1, description="Case-insensitive substring for file and directory names.")
    include_hidden: bool = Field(default=False, description="Include hidden files and directories.")
    max_results: int = Field(default=50, ge=1, le=MAX_FIND_RESULTS, description="Maximum number of returned matches.")


class ReaderSearchRequest(BaseModel):
    path: str = Field(description="Absolute local directory path.")
    query: str = Field(min_length=1, description="Case-insensitive text query.")
    include_hidden: bool = Field(default=False, description="Include hidden files and directories.")
    max_results: int = Field(default=20, ge=1, le=MAX_SEARCH_RESULTS, description="Maximum number of returned matches.")
    max_file_bytes: int = Field(default=DEFAULT_MAX_BYTES, ge=1, le=2_000_000, description="Maximum bytes read per file.")


class WriterMkdirRequest(BaseModel):
    target_root: WRITE_ROOT_NAME = Field(default="workspace", description="Writable sandbox root: workspace or output.")
    relative_path: str = Field(min_length=1, description="Relative directory path inside the selected sandbox root.")
    exist_ok: bool = Field(default=True, description="Do not fail when the directory already exists.")


class WriterWriteRequest(BaseModel):
    target_root: WRITE_ROOT_NAME = Field(default="output", description="Writable sandbox root: workspace or output.")
    relative_path: str = Field(min_length=1, description="Relative file path inside the selected sandbox root.")
    content: str = Field(description="Text content to write.")
    overwrite: bool = Field(default=False, description="Allow overwriting an existing file.")


class WriterDoRequest(BaseModel):
    action: Literal["write", "mkdir"] = Field(description="write creates a text file, mkdir creates a directory.")
    target_root: WRITE_ROOT_NAME = Field(default="output", description="Writable sandbox root: workspace or output.")
    relative_path: str = Field(min_length=1, description="Relative file or directory path inside the selected sandbox root.")
    content: str | None = Field(default=None, description="Required when action='write'.")
    overwrite: bool = Field(default=False, description="Only used for action='write'.")
    exist_ok: bool = Field(default=True, description="Only used for action='mkdir'.")


def ensure_writer_roots() -> None:
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)


def clean_relative_path(value: str) -> str:
    candidate = (value or "").strip()
    if not candidate:
        raise HTTPException(status_code=400, detail="relative_path must not be empty")
    candidate = candidate.replace("\\", "/")
    if candidate in {".", "/"}:
        raise HTTPException(status_code=400, detail="relative_path must point below the selected sandbox root")
    return candidate.lstrip("/")


def within(base: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(base)
        return True
    except ValueError:
        return False


def resolve_writer_root(root_name: WRITE_ROOT_NAME | str) -> Path:
    if root_name == "workspace":
        return WORKSPACE_ROOT
    if root_name == "output":
        return OUTPUT_ROOT
    raise HTTPException(status_code=400, detail="Unknown writer root. Allowed roots: workspace, output")


def resolve_writer_path(root_name: WRITE_ROOT_NAME | str, rel_path: str) -> tuple[Path, Path]:
    base = resolve_writer_root(root_name)
    candidate = (base / clean_relative_path(rel_path)).resolve()
    if not within(base, candidate):
        raise HTTPException(status_code=400, detail="Path escapes selected sandbox root")
    return base, candidate


def resolve_reader_path(path_value: str) -> Path:
    raw = (path_value or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="path must not be empty")
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        raise HTTPException(status_code=400, detail="path must be an absolute local path")
    resolved = candidate.resolve()
    if not resolved.exists():
        raise HTTPException(status_code=404, detail="path not found")
    return resolved


def relative_from(base: Path, child: Path) -> str:
    if base == child:
        return "."
    return child.relative_to(base).as_posix()


def is_hidden_path(path: Path, base: Path) -> bool:
    try:
        relative = path.relative_to(base)
    except ValueError:
        relative = path
    return any(part.startswith(".") for part in relative.parts if part not in {"."})


def detect_content_kind(path: Path) -> str:
    if path.is_dir():
        return "directory"
    try:
        raw = path.read_bytes()[:2048]
    except OSError:
        return "unreadable"
    if b"\x00" in raw:
        return "binary"
    try:
        raw.decode("utf-8")
        return "text"
    except UnicodeDecodeError:
        return "binary"


def iter_scan_targets(base: Path, recursive: bool, include_hidden: bool):
    if base.is_file():
        yield base
        return

    iterator = base.rglob("*") if recursive else base.iterdir()
    count = 0
    for child in sorted(iterator, key=lambda item: (not item.is_dir(), item.as_posix().lower())):
        if not include_hidden and is_hidden_path(child, base):
            continue
        count += 1
        if count > MAX_SCAN_ENTRIES:
            break
        yield child


def build_scan_entry(base: Path, child: Path) -> dict[str, object]:
    entry_type = "dir" if child.is_dir() else "file"
    payload: dict[str, object] = {
        "path": str(child),
        "relative_path": relative_from(base, child),
        "type": entry_type,
        "size": child.stat().st_size if child.is_file() else 0,
    }
    if child.is_file():
        payload["content_kind"] = detect_content_kind(child)
    return payload


def build_find_result(base: Path, child: Path) -> dict[str, str]:
    return {
        "path": str(child),
        "relative_path": relative_from(base, child),
        "name": child.name,
        "type": "dir" if child.is_dir() else "file",
    }


def read_textish_file(path: Path, max_bytes: int) -> tuple[str, str]:
    raw = path.read_bytes()[:max_bytes]
    try:
        return raw.decode("utf-8"), "text"
    except UnicodeDecodeError:
        return raw.hex(), "binary_hex"


@app.get("/health", summary="Health / Gesundheit")
def health() -> dict[str, object]:
    ensure_writer_roots()
    return {
        "status": "ok",
        "version": APP_VERSION,
        "reader_mode": "direct_host_path",
        "writer_roots": {
            "workspace": str(WORKSPACE_ROOT),
            "output": str(OUTPUT_ROOT),
        },
    }


@app.get("/roots", summary="Writer roots / Writer-Wurzeln")
def roots() -> dict[str, object]:
    ensure_writer_roots()
    return {
        "reader_mode": "direct_host_path",
        "reader_rule": "Pass an absolute local path directly to the reader endpoints.",
        "workspace_root": str(WORKSPACE_ROOT),
        "output_root": str(OUTPUT_ROOT),
        "write_root_names": ["workspace", "output"],
    }


@app.post("/reader/scan", summary="Scan local path recursively / Lokalen Pfad rekursiv scannen")
def reader_scan(req: ReaderScanRequest) -> dict[str, object]:
    base = resolve_reader_path(req.path)
    entries: list[dict[str, object]] = []
    for child in iter_scan_targets(base, req.recursive, req.include_hidden):
        entries.append(build_scan_entry(base, child))
        if len(entries) >= req.max_entries:
            break
    return {
        "status": "ok",
        "requested_path": req.path,
        "resolved_path": str(base),
        "kind": "file" if base.is_file() else "directory",
        "recursive": req.recursive,
        "count": len(entries),
        "entries": entries,
    }


@app.post("/reader/read_file", summary="Read a local file / Lokale Datei lesen")
def reader_read_file(req: ReaderReadFileRequest) -> dict[str, object]:
    target = resolve_reader_path(req.path)
    if not target.is_file():
        raise HTTPException(status_code=400, detail="path must point to a file")
    content, kind = read_textish_file(target, req.max_bytes)
    return {
        "status": "ok",
        "requested_path": req.path,
        "resolved_path": str(target),
        "kind": kind,
        "size": target.stat().st_size,
        "content": content,
    }


@app.post("/reader/find", summary="Find names below a local path / Namen unter lokalem Pfad finden")
def reader_find(req: ReaderFindRequest) -> dict[str, object]:
    base = resolve_reader_path(req.path)
    if not base.is_dir():
        raise HTTPException(status_code=400, detail="path must point to a directory")
    needle = req.query.casefold()
    results: list[dict[str, str]] = []
    for child in sorted(base.rglob("*"), key=lambda item: (not item.is_dir(), item.as_posix().lower())):
        if not req.include_hidden and is_hidden_path(child, base):
            continue
        if needle not in child.name.casefold():
            continue
        results.append(build_find_result(base, child))
        if len(results) >= req.max_results:
            break
    return {
        "status": "ok",
        "requested_path": req.path,
        "resolved_path": str(base),
        "query": req.query,
        "count": len(results),
        "results": results,
    }


@app.post("/reader/search", summary="Search text below a local path / Text unter lokalem Pfad suchen")
def reader_search(req: ReaderSearchRequest) -> dict[str, object]:
    base = resolve_reader_path(req.path)
    if not base.is_dir():
        raise HTTPException(status_code=400, detail="path must point to a directory")
    needle = req.query.casefold()
    results: list[dict[str, object]] = []
    files_scanned = 0

    for child in sorted(base.rglob("*"), key=lambda item: item.as_posix().lower()):
        if not child.is_file():
            continue
        if not req.include_hidden and is_hidden_path(child, base):
            continue
        files_scanned += 1
        if files_scanned > MAX_SEARCH_FILES:
            break
        try:
            raw = child.read_bytes()[:req.max_file_bytes]
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            if needle not in line.casefold():
                continue
            snippet = line.strip()
            if len(snippet) > 240:
                snippet = snippet[:237] + "..."
            results.append(
                {
                    "path": str(child),
                    "relative_path": relative_from(base, child),
                    "line_number": line_number,
                    "snippet": snippet,
                }
            )
            if len(results) >= req.max_results:
                return {
                    "status": "ok",
                    "requested_path": req.path,
                    "resolved_path": str(base),
                    "query": req.query,
                    "count": len(results),
                    "files_scanned": files_scanned,
                    "results": results,
                }

    return {
        "status": "ok",
        "requested_path": req.path,
        "resolved_path": str(base),
        "query": req.query,
        "count": len(results),
        "files_scanned": files_scanned,
        "results": results,
    }


@app.post("/writer/mkdir", summary="Create sandbox directory / Sandbox-Ordner erstellen")
def writer_mkdir(req: WriterMkdirRequest) -> dict[str, str]:
    ensure_writer_roots()
    base, target = resolve_writer_path(req.target_root, req.relative_path)
    if target.exists() and target.is_file():
        raise HTTPException(status_code=409, detail="Target exists as a file")
    target.mkdir(parents=True, exist_ok=req.exist_ok)
    return {
        "status": "ok",
        "action": "mkdir",
        "target_root": req.target_root,
        "relative_path": target.relative_to(base).as_posix(),
        "written_path": str(target),
    }


@app.post("/writer/write", summary="Write sandbox text file / Sandbox-Textdatei schreiben")
def writer_write(req: WriterWriteRequest) -> dict[str, str]:
    ensure_writer_roots()
    base, target = resolve_writer_path(req.target_root, req.relative_path)
    if target.exists():
        if target.is_dir():
            raise HTTPException(status_code=400, detail="Target path points to an existing directory")
        if not req.overwrite:
            raise HTTPException(status_code=409, detail="Target exists")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(req.content, encoding="utf-8")
    return {
        "status": "ok",
        "action": "write",
        "target_root": req.target_root,
        "relative_path": target.relative_to(base).as_posix(),
        "written_path": str(target),
    }


@app.post("/writer/doit", summary="Guided sandbox action / Geführte Sandbox-Aktion")
def writer_doit(req: WriterDoRequest) -> dict[str, str]:
    if req.action == "mkdir":
        return writer_mkdir(
            WriterMkdirRequest(
                target_root=req.target_root,
                relative_path=req.relative_path,
                exist_ok=req.exist_ok,
            )
        )
    if req.content is None:
        raise HTTPException(status_code=400, detail="content is required for action='write'")
    return writer_write(
        WriterWriteRequest(
            target_root=req.target_root,
            relative_path=req.relative_path,
            content=req.content,
            overwrite=req.overwrite,
        )
    )
