from pathlib import Path
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title='repo_bridge', version='0.2.0')

allow_origins_raw = os.getenv('ALLOW_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')
allow_origins = [item.strip() for item in allow_origins_raw.split(',') if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

SOURCE_ROOT = Path(os.getenv('SOURCE_ROOT', '/workspace/source_repo_ro')).resolve()
SANDBOX_ROOT = Path(os.getenv('SANDBOX_ROOT', '/workspace/builder_sandbox')).resolve()
WORKSPACE_ROOT = (SANDBOX_ROOT / 'workspace').resolve()
OUTPUT_ROOT = (SANDBOX_ROOT / 'output').resolve()

class WriteRequest(BaseModel):
    target_root: str = 'output'
    relative_path: str
    content: str
    overwrite: bool = False

def within(base: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(base)
        return True
    except ValueError:
        return False

def source_path(value: str) -> Path:
    candidate = (SOURCE_ROOT / value).resolve()
    if not within(SOURCE_ROOT, candidate):
        raise HTTPException(status_code=400, detail='Path escapes SOURCE_ROOT')
    return candidate

def write_path(root_name: str, rel_path: str) -> Path:
    base = OUTPUT_ROOT if root_name == 'output' else WORKSPACE_ROOT
    candidate = (base / rel_path).resolve()
    if not within(base, candidate):
        raise HTTPException(status_code=400, detail='Path escapes writable sandbox root')
    return candidate

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/roots')
def roots():
    return {
        'source_root': str(SOURCE_ROOT),
        'workspace_root': str(WORKSPACE_ROOT),
        'output_root': str(OUTPUT_ROOT),
    }

@app.get('/tree')
def tree(path: str = ''):
    root = source_path(path) if path else SOURCE_ROOT
    if not root.exists():
        raise HTTPException(status_code=404, detail='Source path not found')
    if root.is_file():
        return {'path': path, 'entries': [root.name]}
    entries = []
    for child in sorted(root.iterdir()):
        suffix = '/' if child.is_dir() else ''
        entries.append(child.name + suffix)
    return {'path': path or '.', 'entries': entries}

@app.get('/read')
def read(path: str, max_bytes: int = 200000):
    target = source_path(path)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail='Source file not found')
    raw = target.read_bytes()[:max_bytes]
    try:
        content = raw.decode('utf-8')
        kind = 'text'
    except UnicodeDecodeError:
        content = raw.hex()
        kind = 'binary_hex'
    return {
        'path': path,
        'kind': kind,
        'size': target.stat().st_size,
        'content': content,
    }

@app.post('/write')
def write(req: WriteRequest):
    target = write_path(req.target_root, req.relative_path)
    if target.exists() and not req.overwrite:
        raise HTTPException(status_code=409, detail='Target exists')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(req.content, encoding='utf-8')
    return {'status': 'ok', 'written_path': str(target)}
