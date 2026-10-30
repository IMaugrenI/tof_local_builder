"""Narrow client for the existing containerized read-only-source/sandbox bridge.

All requests use an explicit loopback port. The root handshake prevents a
running bridge from quietly pointing at a different project after config edits.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath, PureWindowsPath

from tof_cli.builder.repo_bridge_ops import sandbox_report, source_repo_report

MAX_REPLY_BYTES = 160_000
MAX_WRITE_CHARS = 16_000
ALLOWED_SUFFIXES = frozenset({
    ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml",
    ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".sql",
    ".sh", ".go", ".rs", ".java", ".c", ".cpp", ".h", ".hpp",
    ".rb", ".php", ".vue",
})
RESERVED_PARTS = frozenset({
    ".git", ".builder_runs", "node_modules", "__pycache__", ".venv",
    "secrets", "private", "credentials", "keys", "tokens",
})


class BridgeError(ValueError):
    pass


class SourceNotFound(BridgeError):
    pass


def safe_relative_file(raw: str) -> str:
    """Never accept host paths, hidden dot-paths, secrets or path traversal."""
    if not isinstance(raw, str) or not raw or len(raw) > 180:
        raise BridgeError("Generated file requires a short relative path")
    if "\\" in raw or raw.startswith("/") or PureWindowsPath(raw).drive:
        raise BridgeError("Absolute and Windows paths are not allowed")
    if any(ord(char) < 32 for char in raw):
        raise BridgeError("Control characters in generated path are forbidden")
    parts = raw.split("/")
    if not 1 <= len(parts) <= 8:
        raise BridgeError("Generated path exceeds the allowed depth")
    for part in parts:
        lowered = part.lower()
        if not part or part in (".", "..") or part.startswith(".") or len(part) > 64:
            raise BridgeError("Unsafe path component")
        if any(char in part for char in ':*?"<>|'):
            raise BridgeError("Unsafe path characters")
        if lowered in RESERVED_PARTS or any(term in lowered for term in ("secret", "credential", "private_key", "id_rsa", "token")):
            raise BridgeError("Sensitive path names cannot be generated automatically")
        if lowered.split(".")[0] in ("con", "prn", "nul", "aux", "com1", "lpt1"):
            raise BridgeError("Reserved file name")
    if PurePosixPath(raw).suffix.lower() not in ALLOWED_SUFFIXES:
        raise BridgeError("Automatic generation supports known text file types only")
    return raw


class AgentBridge:
    def __init__(self, env: dict[str, str]) -> None:
        source = source_repo_report(env)
        sandbox = sandbox_report(env)
        if source["state"] != "ok" or sandbox["state"] != "ok":
            raise BridgeError("Choose a readable project and a separate sandbox")
        self.source = Path(source["path"]).resolve()
        self.sandbox = Path(sandbox["path"]).resolve()
        if self.source == self.sandbox or self.source in self.sandbox.parents or self.sandbox in self.source.parents:
            raise BridgeError("Source and sandbox must be separated")
        try:
            port = int(env.get("REPO_BRIDGE_PORT", "8099"))
        except (TypeError, ValueError) as exc:
            raise BridgeError("Invalid repository bridge port") from exc
        if not 1 <= port <= 65535:
            raise BridgeError("Invalid repository bridge port")
        self.base = f"http://127.0.0.1:{port}"
        self.verify_roots()

    def _request(self, endpoint: str, *, params: dict[str, object] | None = None,
                 payload: dict[str, object] | None = None) -> dict[str, object]:
        if endpoint not in ("/roots", "/tree", "/read", "/write"):
            raise BridgeError("Operation is not permitted by the agent")
        url = self.base + endpoint
        if params:
            url += "?" + urllib.parse.urlencode(params)
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "application/json"} if payload is not None else {},
            method="POST" if payload is not None else "GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=8.0) as response:
                raw = response.read(MAX_REPLY_BYTES + 1)
        except urllib.error.HTTPError as exc:
            if endpoint == "/read" and exc.code == 404:
                raise SourceNotFound("Source file does not exist") from exc
            if endpoint == "/write" and exc.code == 409:
                raise BridgeError("Generated sandbox file already exists; review it before starting a new build") from exc
            raise BridgeError(f"Repository bridge rejected {endpoint} (HTTP {exc.code})") from exc
        except (OSError, TimeoutError) as exc:
            raise BridgeError("Repository bridge is not reachable; check the Builder runtime") from exc
        if len(raw) > MAX_REPLY_BYTES:
            raise BridgeError("Repository bridge response is too large")
        try:
            result = json.loads(raw)
        except (UnicodeError, ValueError) as exc:
            raise BridgeError("Repository bridge returned unreadable data") from exc
        if not isinstance(result, dict):
            raise BridgeError("Unexpected repository bridge response")
        return result

    def verify_roots(self) -> None:
        roots = self._request("/roots")
        try:
            actual_source = Path(str(roots["source_host_path"])).resolve()
            actual_sandbox = Path(str(roots["sandbox_host_path"])).resolve()
        except (KeyError, TypeError, ValueError) as exc:
            raise BridgeError("Repository bridge does not report its source and sandbox") from exc
        if actual_source != self.source or actual_sandbox != self.sandbox:
            raise BridgeError("Repository bridge points to another project. Restart only after reviewing the configuration.")

    def tree(self, relative_dir: str = "") -> list[dict[str, object]]:
        # The bridge itself validates root and containment; only the source is inspected.
        params = {"root": "source", "path": relative_dir}
        result = self._request("/tree", params=params)
        if result.get("kind") != "directory" or not isinstance(result.get("entries"), list):
            raise BridgeError("Could not read the selected repository directory")
        return [item for item in result["entries"][:100] if isinstance(item, dict)]

    def source_text(self, relative_file: str, max_bytes: int = 6_000) -> str | None:
        safe_relative_file(relative_file)
        try:
            result = self._request("/read", params={
                "root": "source", "path": relative_file, "max_bytes": max_bytes,
            })
        except SourceNotFound:
            return None
        if result.get("kind") != "text" or not isinstance(result.get("content"), str):
            raise BridgeError("Source file is not valid UTF-8 text")
        if not isinstance(result.get("size"), int) or result["size"] > max_bytes:
            raise BridgeError("Source file is too large for safe complete-file generation")
        return result["content"]

    def output_text(self, relative_file: str) -> str | None:
        """Read a saved draft through the existing bridge, never directly from host."""
        path = safe_relative_file(relative_file)
        self.verify_roots()
        try:
            result = self._request("/read", params={
                "root": "output", "path": path, "max_bytes": MAX_WRITE_CHARS * 4,
            })
        except SourceNotFound:
            return None
        if result.get("kind") != "text" or not isinstance(result.get("content"), str):
            raise BridgeError("Saved draft is not UTF-8 text")
        size = result.get("size")
        if not isinstance(size, int) or size > MAX_WRITE_CHARS * 4:
            raise BridgeError("Saved draft is too large to safely verify")
        return result["content"]

    def write_output(self, relative_file: str, content: str) -> None:
        path = safe_relative_file(relative_file)
        if not isinstance(content, str) or not content.strip() or len(content) > MAX_WRITE_CHARS:
            raise BridgeError("Generated file is empty or larger than the safe text limit")
        self.verify_roots()
        result = self._request("/write", payload={
            "target_root": "output", "relative_path": path,
            "content": content, "overwrite": False,
        })
        if result.get("status") != "ok" or result.get("target_root") != "output" or result.get("relative_path") != path:
            raise BridgeError("Repository bridge did not confirm the expected sandbox write")
