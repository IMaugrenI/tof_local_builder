"""Focused source-candidate checks; no Docker or target-system acceptance."""
from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "distribution_candidate", ROOT / "scripts/build_source_candidate.py"
)
assert spec and spec.loader
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


def tree_bytes(paths, mode=b"100644"):
    return b"".join(
        mode + b" blob " + b"a" * 40 + b"\t" + p.encode("utf-8") + b"\0"
        for p in paths
    )


def test_expected_platform_starters_and_offline_guides_required():
    assert {
        "scripts/start_here.ps1", "scripts/start_here.sh",
        "scripts/start_here.command", "docs/RELEASE_PACKAGE_DE.md",
        "docs/RELEASE_PACKAGE.md", "run.py",
    }.issubset(package.REQUIRED)
    with pytest.raises(ValueError, match="missing_package_files"):
        package.validate_tree_entries(tree_bytes(["run.py"]))


@pytest.mark.parametrize("unsafe", [
    ".env", "config/.env.local", "local_sources/private.txt",
    "storage/private.json", "dist/old.zip", "keys/client.pem",
    "docs/../../private", "secrets.json", "exports/data.csv",
])
def test_private_or_generated_paths_are_refused(unsafe):
    paths = sorted(package.REQUIRED | {unsafe})
    with pytest.raises(ValueError):
        package.validate_tree_entries(tree_bytes(paths))


def test_symlink_and_nonregular_git_entries_are_refused():
    for mode in [b"120000", b"160000"]:
        with pytest.raises(ValueError, match="unsafe_or_nonregular_entry"):
            package.validate_tree_entries(tree_bytes(sorted(package.REQUIRED), mode))


def test_committed_tree_builds_checksum_verified_source_zip(tmp_path):
    # This exercises the Git archive / zip / checksum path on a checked-out
    # source commit. It does not start Docker or claim runtime acceptance.
    zip_path, checksum = package.build_candidate(tmp_path / "candidate")
    assert zip_path.exists() and checksum.exists()
    expected_hash, expected_file = checksum.read_text(encoding="utf-8").strip().split("  ")
    assert expected_hash == hashlib.sha256(zip_path.read_bytes()).hexdigest()
    assert expected_file == zip_path.name
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        assert all(f"{package.PRODUCT}/{name}" in names for name in package.REQUIRED)
        assert not any(name.endswith("/.env") for name in names)
        assert archive.testzip() is None


def test_release_candidate_workflow_is_manual_only():
    workflow = (ROOT / ".github/workflows/source-candidate.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "scripts/build_source_candidate.py" in workflow
    assert "create-release" not in workflow
    assert "softprops/action-gh-release" not in workflow
