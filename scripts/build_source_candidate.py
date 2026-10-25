"""Build a committed-source *candidate*, not a release or native installer.

Packages the existing CLI, Compose and platform-specific start scripts without
starting any service. Requires Git and Python 3.11+, both development tools.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

PRODUCT = "tof_local_builder"
COMPOSE = "compose.yml"
ROOT = Path(__file__).resolve().parents[1]
REQUIRED = frozenset({
    ".env.example", "run.py", COMPOSE,
    "scripts/start_here.sh", "scripts/start_here.ps1",
    "scripts/start_here.command", "START_HERE_DE.md", "START_HERE.md",
    "LICENSE", "docs/RELEASE_PACKAGE_DE.md", "docs/RELEASE_PACKAGE.md",
})
FORBIDDEN_PARTS = frozenset({
    ".git", "__pycache__", ".venv", "node_modules", "local_sources",
    ".runtime", "storage", "logs", "tmp", "exports",
})
FORBIDDEN_SUFFIXES = (".pem", ".p12", ".pfx", ".key", ".sqlite", ".sqlite3", ".db")


def validate_tree_entries(tree_bytes: bytes) -> list[str]:
    """Reject unexpected source files before making any distribution archive."""
    paths: list[str] = []
    for item in tree_bytes.split(b"\0"):
        if not item:
            continue
        try:
            meta, name = item.split(b"\t", 1)
            mode = meta.split(b" ", 1)[0]
            filename = name.decode("utf-8")
        except (ValueError, UnicodeError) as exc:
            raise ValueError("invalid_git_tree_entry") from exc
        rel = PurePosixPath(filename)
        parts = rel.parts
        if (mode not in {b"100644", b"100755"} or not parts
                or rel.is_absolute() or any(part in {".", ".."} for part in parts)
                or "\\" in filename):
            raise ValueError(f"unsafe_or_nonregular_entry:{filename}")
        base = parts[-1].lower()
        if (any(part in FORBIDDEN_PARTS for part in parts)
                or any(part.startswith(".env") and part != ".env.example" for part in parts)
                or base.endswith(FORBIDDEN_SUFFIXES)
                or base in {"credentials.json", "secrets.json", "id_rsa"}
                or parts[0] in {"data", "dist"}):
            raise ValueError(f"sensitive_or_generated_entry:{filename}")
        paths.append(filename)
    missing = REQUIRED.difference(paths)
    if missing:
        raise ValueError("missing_package_files:" + ",".join(sorted(missing)))
    return paths


def build_candidate(output_dir: Path) -> tuple[Path, Path]:
    """Archive a fixed Git commit only; uncommitted workspace files stay out."""
    commit = subprocess.check_output(
        ["git", "rev-parse", "--verify", "HEAD"], cwd=ROOT, text=True,
    ).strip()
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("invalid_commit_sha")
    tree = subprocess.check_output(
        ["git", "ls-tree", "-r", "-z", commit], cwd=ROOT,
    )
    validate_tree_entries(tree)

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    name = f"{PRODUCT}-source-candidate-{commit[:12]}.zip"
    archive = output_dir / name
    subprocess.run([
        "git", "archive", "--format=zip",
        f"--prefix={PRODUCT}/", f"--output={archive}", commit,
    ], cwd=ROOT, check=True)
    with zipfile.ZipFile(archive) as reader:
        if reader.testzip() is not None:
            raise ValueError("package_integrity_check_failed")
        packaged = set(reader.namelist())
        for required in REQUIRED:
            if f"{PRODUCT}/{required}" not in packaged:
                raise ValueError(f"archive_missing:{required}")
    sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = output_dir / "CHECKSUMS.sha256"
    checksum.write_text(f"{sha}  {name}\n", encoding="utf-8")
    return archive, checksum


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a source-only distribution candidate")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    zip_path, sha_path = build_candidate(args.output_dir)
    print(f"Source candidate: {zip_path}\nSHA-256: {sha_path}")
