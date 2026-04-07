from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_VERSION = "0.3.1"
ROOT_NAME = Literal["source", "workspace", "output"]
WRITE_ROOT_NAME = Literal["workspace", "output"]

app = FastAPI(
    title="repo_bridge",
    version=APP_VERSION,
    description=(
        "Controlled local builder bridge. "
        "English and German summaries are included to make the tool surface easier to understand. "
        "Source stays read-only. Writes stay limited to the sandbox."
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
SOURCE_HOST_PATH = (os.getenv("SOURCE_HOST_PATH", "") or "").strip() or None
SANDBOX_HOST_PATH = (os.getenv("SANDBOX_HOST_PATH", "") or "").strip() or None

MAX_FIND_RESULTS = 200
MAX_SEARCH_RESULTS = 50
MAX_SEARCH_FILES = 500
DEFAULT_MAX_BYTES = 200_000


class WriteRequest(BaseModel):
    target_root: WRITE_ROOT_NAME = Field(
        default="output",
        description="Writable sandbox root. 'output' or 'workspace'. / Schreibbares Sandbox-Ziel: 'output' oder 'workspace'.",
    )
    relative_path: str = Field(
        min_length=1,
        description="Relative file path inside the writable sandbox root. / Relativer Dateipfad innerhalb des schreibbaren Sandbox-Ziels.",
    )
    content: str = Field(
        description="Text content to write. / Textinhalt, der geschrieben wird."
    )
    overwrite: bool = Field(
        default=False,
        description="Allow overwriting an existing file. / Überschreiben einer vorhandenen Datei erlauben.",
    )


class DirectoryRequest(BaseModel):
    target_root: WRITE_ROOT_NAME = Field(
        default="workspace",
        description="Writable sandbox root. 'output' or 'workspace'. / Schreibbares Sandbox-Ziel: 'output' oder 'workspace'.",
    )
    relative_path: str = Field(
        min_length=1,
        description="Relative directory path inside the writable sandbox root. / Relativer Ordnerpfad innerhalb des schreibbaren Sandbox-Ziels.",
    )
    exist_ok: bool = Field(
        default=True,
        description="Do not fail when the directory already exists. / Kein Fehler, wenn der Ordner bereits existiert.",
    )


class DoRequest(BaseModel):
    action: Literal["write", "mkdir"] = Field(
        description="Simple guided action. 'write' creates a text file, 'mkdir' creates a directory. / Einfache geführte Aktion. 'write' erstellt eine Textdatei, 'mkdir' erstellt einen Ordner."
    )
    target_root: WRITE_ROOT_NAME = Field(
        default="output",
        description="Writable sandbox root. 'output' or 'workspace'. / Schreibbares Sandbox-Ziel: 'output' oder 'workspace'.",
    )
    relative_path: str = Field(
        min_length=1,
        description="Relative file or directory path inside the writable sandbox root. / Relativer Datei- oder Ordnerpfad innerhalb des schreibbaren Sandbox-Ziels.",
    )
    content: str | None = Field(
        default=None,
        description="Required for action='write'. / Erforderlich für action='write'.",
    )
    overwrite: bool = Field(
        default=False,
        description="Only used for action='write'. / Wird nur für action='write' genutzt.",
    )
    exist_ok: bool = Field(
        default=True,
        description="Only used for action='mkdir'. / Wird nur für action='mkdir' genutzt.",
    )


def within(base: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(base)
        return True
    except ValueError:
        return False


def available_roots() -> dict[str, Path]:
    return {
        "source": SOURCE_ROOT,
        "workspace": WORKSPACE_ROOT,
        "output": OUTPUT_ROOT,
    }


def _join_host_path(base: str | None, child: str) -> str | None:
    if not base:
        return None
    return str(Path(base) / child)


def path_view() -> dict[str, object]:
    return {
        "read_root_name": "source",
        "write_root_names": ["workspace", "output"],
        "host_paths": {
            "source": SOURCE_HOST_PATH,
            "sandbox": SANDBOX_HOST_PATH,
            "workspace": _join_host_path(SANDBOX_HOST_PATH, "workspace"),
            "output": _join_host_path(SANDBOX_HOST_PATH, "output"),
        },
        "container_paths": {
            "source": str(SOURCE_ROOT),
            "sandbox": str(SANDBOX_ROOT),
            "workspace": str(WORKSPACE_ROOT),
            "output": str(OUTPUT_ROOT),
        },
    }


def resolve_root(root_name: ROOT_NAME | str) -> Path:
    roots = available_roots()
    root = roots.get(str(root_name))
    if root is None:
        allowed = ", ".join(sorted(roots))
        raise HTTPException(status_code=400, detail=f"Unknown root '{root_name}'. Allowed roots: {allowed}")
    return root


def clean_relative_path(value: str) -> str:
    candidate = (value or "").strip()
    if not candidate:
        raise HTTPException(status_code=400, detail="relative_path must not be empty")
    candidate = candidate.replace("\\", "/")
    if candidate in {".", "/"}:
        raise HTTPException(status_code=400, detail="relative_path must point to a file or directory below the root")
    return candidate.lstrip("/")


def resolve_read_path(root_name: ROOT_NAME | str, rel_path: str) -> Path:
    base = resolve_root(root_name)
    candidate = (base / clean_relative_path(rel_path)).resolve()
    if not within(base, candidate):
        raise HTTPException(status_code=400, detail="Path escapes selected root")
    return candidate


def resolve_tree_path(root_name: ROOT_NAME | str, rel_path: str = "") -> tuple[Path, str]:
    base = resolve_root(root_name)
    normalized = (rel_path or "").strip().lstrip("/")
    candidate = (base / normalized).resolve() if normalized else base
    if not within(base, candidate):
        raise HTTPException(status_code=400, detail="Path escapes selected root")
    return candidate, normalized


def resolve_write_path(root_name: WRITE_ROOT_NAME | str, rel_path: str) -> tuple[Path, Path]:
    base = resolve_root(root_name)
    if base == SOURCE_ROOT:
        raise HTTPException(status_code=400, detail="Writes into source are not allowed")
    candidate = (base / clean_relative_path(rel_path)).resolve()
    if not within(base, candidate):
        raise HTTPException(status_code=400, detail="Path escapes writable sandbox root")
    return base, candidate


def relative_string(base: Path, candidate: Path) -> str:
    return candidate.relative_to(base).as_posix()


def build_tree_entry(base: Path, child: Path) -> dict[str, str | int]:
    entry_type = "dir" if child.is_dir() else "file"
    return {
        "name": child.name,
        "path": relative_string(base, child),
        "type": entry_type,
        "size": child.stat().st_size if child.is_file() else 0,
    }


def mkdir_internal(req: DirectoryRequest) -> dict[str, str]:
    base, target = resolve_write_path(req.target_root, req.relative_path)
    if target.exists() and target.is_file():
        raise HTTPException(status_code=409, detail="Target exists as a file")
    target.mkdir(parents=True, exist_ok=req.exist_ok)
    return {
        "status": "ok",
        "action": "mkdir",
        "target_root": req.target_root,
        "relative_path": relative_string(base, target),
        "written_path": str(target),
    }


def write_internal(req: WriteRequest) -> dict[str, str]:
    base, target = resolve_write_path(req.target_root, req.relative_path)
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
        "relative_path": relative_string(base, target),
        "written_path": str(target),
    }


@app.get("/health", summary="Health / Gesundheit")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "version": APP_VERSION,
        "roots": {
            "source": str(SOURCE_ROOT),
            "workspace": str(WORKSPACE_ROOT),
            "output": str(OUTPUT_ROOT),
        },
        "path_view": path_view(),
    }


@app.get("/api/config", summary="Tool server config / Tool-Server-Konfiguration")
def api_config() -> dict[str, object]:
    return {
        "name": "repo_bridge",
        "title": "ToF Local Builder Repo Bridge",
        "version": APP_VERSION,
        "language_support": ["en", "de"],
        "capabilities": ["roots", "tree", "read", "find", "search", "mkdir", "write", "doit"],
        "notes": {
            "en": "Source is read-only and selected through SOURCE_REPO_PATH. Writes are limited to sandbox/workspace and sandbox/output.",
            "de": "Source ist read-only und wird über SOURCE_REPO_PATH ausgewählt. Schreibzugriffe sind auf sandbox/workspace und sandbox/output begrenzt.",
        },
    }


@app.get("/roots", summary="List roots / Wurzeln anzeigen")
def roots() -> dict[str, object]:
    return {
        "source_root": str(SOURCE_ROOT),
        "workspace_root": str(WORKSPACE_ROOT),
        "output_root": str(OUTPUT_ROOT),
        "source_host_path": SOURCE_HOST_PATH,
        "sandbox_host_path": SANDBOX_HOST_PATH,
        "workspace_host_path": _join_host_path(SANDBOX_HOST_PATH, "workspace"),
        "output_host_path": _join_host_path(SANDBOX_HOST_PATH, "output"),
        "source_container_path": str(SOURCE_ROOT),
        "workspace_container_path": str(WORKSPACE_ROOT),
        "output_container_path": str(OUTPUT_ROOT),
        "read_root_name": "source",
        "write_root_names": ["workspace", "output"],
    }


@app.get("/tree", summary="List directory tree / Verzeichnis anzeigen")
def tree(
    root: ROOT_NAME = Query(default="source", description="Root to inspect. / Zu prüfende Wurzel."),
    path: str = Query(default="", description="Relative directory path inside the selected root. / Relativer Ordnerpfad innerhalb der gewählten Wurzel."),
) -> dict[str, object]:
    target, normalized = resolve_tree_path(root, path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="Selected path not found")
    base = resolve_root(root)
    if target.is_file():
        return {
            "root": root,
            "path": normalized or ".",
            "kind": "file",
            "entries": [build_tree_entry(base, target)],
        }

    entries = [build_tree_entry(base, child) for child in sorted(target.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))]
    return {
        "root": root,
        "path": normalized or ".",
        "kind": "directory",
        "entries": entries,
    }


@app.get("/read", summary="Read file / Datei lesen")
def read(
    root: ROOT_NAME = Query(default="source", description="Root to read from. / Wurzel, aus der gelesen wird."),
    path: str = Query(..., description="Relative file path. / Relativer Dateipfad."),
    max_bytes: int = Query(default=DEFAULT_MAX_BYTES, ge=1, le=2_000_000, description="Maximum number of bytes to read. / Maximale Zahl gelesener Bytes."),
) -> dict[str, object]:
    target = resolve_read_path(root, path)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    raw = target.read_bytes()[:max_bytes]
    try:
        content = raw.decode("utf-8")
        kind = "text"
    except UnicodeDecodeError:
        content = raw.hex()
        kind = "binary_hex"
    return {
        "root": root,
        "path": target.relative_to(resolve_root(root)).as_posix(),
        "kind": kind,
        "size": target.stat().st_size,
        "content": content,
    }


@app.get("/find", summary="Find names / Namen finden")
def find(
    root: ROOT_NAME = Query(default="source", description="Root to search in. / Wurzel, in der gesucht wird."),
    query: str = Query(..., min_length=1, description="Case-insensitive substring for file and directory names. / Groß-Kleinschreibung-unabhängige Teilzeichenfolge für Datei- und Ordnernamen."),
    path: str = Query(default="", description="Relative start directory inside the selected root. / Relativer Startordner innerhalb der gewählten Wurzel."),
    max_results: int = Query(default=50, ge=1, le=MAX_FIND_RESULTS, description="Maximum number of results. / Maximale Anzahl an Treffern."),
    include_files: bool = Query(default=True, description="Include file names. / Dateinamen einbeziehen."),
    include_dirs: bool = Query(default=True, description="Include directory names. / Ordnernamen einbeziehen."),
) -> dict[str, object]:
    target, normalized = resolve_tree_path(root, path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="Selected path not found")
    if not target.is_dir():
        raise HTTPException(status_code=400, detail="find requires a directory path")

    needle = query.casefold()
    base = resolve_root(root)
    results: list[dict[str, str]] = []

    for child in sorted(target.rglob("*")):
        is_dir = child.is_dir()
        if is_dir and not include_dirs:
            continue
        if child.is_file() and not include_files:
            continue
        if needle not in child.name.casefold():
            continue
        results.append(
            {
                "path": relative_string(base, child),
                "name": child.name,
                "type": "dir" if is_dir else "file",
            }
        )
        if len(results) >= max_results:
            break

    return {
        "root": root,
        "path": normalized or ".",
        "query": query,
        "count": len(results),
        "results": results,
    }


@app.get("/search", summary="Search text content / Textinhalt suchen")
def search(
    root: ROOT_NAME = Query(default="source", description="Root to search in. / Wurzel, in der gesucht wird."),
    query: str = Query(..., min_length=1, description="Case-insensitive text query. / Groß-Kleinschreibung-unabhängige Textsuche."),
    path: str = Query(default="", description="Relative start directory inside the selected root. / Relativer Startordner innerhalb der gewählten Wurzel."),
    max_results: int = Query(default=20, ge=1, le=MAX_SEARCH_RESULTS, description="Maximum number of matches returned. / Maximale Anzahl zurückgegebener Treffer."),
    max_file_bytes: int = Query(default=DEFAULT_MAX_BYTES, ge=1, le=2_000_000, description="Maximum bytes read per file. / Maximale pro Datei gelesene Bytes."),
) -> dict[str, object]:
    target, normalized = resolve_tree_path(root, path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="Selected path not found")
    if not target.is_dir():
        raise HTTPException(status_code=400, detail="search requires a directory path")

    needle = query.casefold()
    base = resolve_root(root)
    results: list[dict[str, object]] = []
    files_scanned = 0

    for child in sorted(target.rglob("*")):
        if not child.is_file():
            continue
        files_scanned += 1
        if files_scanned > MAX_SEARCH_FILES:
            break
        try:
            raw = child.read_bytes()[:max_file_bytes]
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
                    "path": relative_string(base, child),
                    "line_number": line_number,
                    "snippet": snippet,
                }
            )
            if len(results) >= max_results:
                return {
                    "root": root,
                    "path": normalized or ".",
                    "query": query,
                    "count": len(results),
                    "files_scanned": files_scanned,
                    "results": results,
                }

    return {
        "root": root,
        "path": normalized or ".",
        "query": query,
        "count": len(results),
        "files_scanned": files_scanned,
        "results": results,
    }


@app.post("/mkdir", summary="Create directory / Ordner erstellen")
def mkdir(req: DirectoryRequest) -> dict[str, str]:
    return mkdir_internal(req)


@app.post("/write", summary="Write text file / Textdatei schreiben")
def write(req: WriteRequest) -> dict[str, str]:
    return write_internal(req)


@app.post("/doit", summary="Simple guided action / Einfache geführte Aktion")
def doit(req: DoRequest) -> dict[str, str]:
    if req.action == "mkdir":
        return mkdir_internal(
            DirectoryRequest(
                target_root=req.target_root,
                relative_path=req.relative_path,
                exist_ok=req.exist_ok,
            )
        )
    if req.content is None:
        raise HTTPException(status_code=400, detail="content is required for action='write'")
    return write_internal(
        WriteRequest(
            target_root=req.target_root,
            relative_path=req.relative_path,
            content=req.content,
            overwrite=req.overwrite,
        )
    )
