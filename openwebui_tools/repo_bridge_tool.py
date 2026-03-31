from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        REPO_BRIDGE_BASE_URL: str = Field(
            default=os.getenv("REPO_BRIDGE_BASE_URL", "http://repo-bridge:8099"),
            description="Base URL of the local repo_bridge service",
        )
        DEFAULT_MAX_BYTES: int = Field(
            default=200000,
            description="Default byte limit for repo_read requests",
        )

    def __init__(self):
        self.valves = self.Valves()

    def _get_json(self, path: str, params: dict | None = None) -> dict:
        url = self.valves.REPO_BRIDGE_BASE_URL.rstrip("/") + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = response.read().decode("utf-8", errors="replace")
        return json.loads(payload)

    def _post_json(self, path: str, payload: dict) -> dict:
        url = self.valves.REPO_BRIDGE_BASE_URL.rstrip("/") + path
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8", errors="replace")
        return json.loads(raw)

    async def repo_tree(self, path: str = "") -> str:
        """List files and folders inside the mounted source repository. Use an empty path for the source root."""
        data = self._get_json("/tree", {"path": path})
        entries = data.get("entries", [])
        listing = "\n".join(f"- {entry}" for entry in entries)
        current_path = data.get("path", path or ".")
        return f"Source tree at `{current_path}`:\n\n{listing}"

    async def repo_read(self, path: str, max_bytes: int | None = None) -> str:
        """Read a file from the mounted source repository. This is read-only and never writes into the source repo."""
        byte_limit = max_bytes or self.valves.DEFAULT_MAX_BYTES
        data = self._get_json("/read", {"path": path, "max_bytes": byte_limit})
        kind = data.get("kind", "unknown")
        size = data.get("size", "unknown")
        content = data.get("content", "")
        return f"Read `{path}` from source repo\n- kind: {kind}\n- size: {size}\n\n{content}"

    async def sandbox_write(
        self,
        target_root: str,
        relative_path: str,
        content: str,
        overwrite: bool = False,
    ) -> str:
        """Write content into the builder sandbox only. target_root must be `workspace` or `output`."""
        if target_root not in {"workspace", "output"}:
            return "target_root must be `workspace` or `output`."
        data = self._post_json(
            "/write",
            {
                "target_root": target_root,
                "relative_path": relative_path,
                "content": content,
                "overwrite": overwrite,
            },
        )
        written_path = data.get("written_path", relative_path)
        return f"Sandbox write successful: `{written_path}`"
