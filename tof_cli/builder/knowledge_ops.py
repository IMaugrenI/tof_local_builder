"""Optional, explicitly invoked read-only search in ToF Local Knowledge.

This adapter uses the existing Knowledge search API contract. It does not
start Knowledge, access its database, ingest documents, call an LLM, or share
results with a Builder prompt. No automatic discovery of private documents.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

DEFAULT_KNOWLEDGE_PORT = "8105"
MAX_QUERY_CHARS = 500
MAX_RESPONSE_BYTES = 64_000
MAX_HITS = 5


class KnowledgeError(ValueError):
    pass


def _port(env: dict[str, str]) -> int:
    raw = env.get("BUILDER_KNOWLEDGE_SEARCH_PORT", DEFAULT_KNOWLEDGE_PORT)
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise KnowledgeError("Invalid local Knowledge search port") from exc
    if not 1 <= value <= 65535:
        raise KnowledgeError("Invalid local Knowledge search port")
    return value


def _get_json(request: urllib.request.Request, timeout: float) -> dict[str, object]:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read(MAX_RESPONSE_BYTES + 1)
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise KnowledgeError("Local Knowledge is unavailable; start it separately to use optional document search") from exc
    if len(payload) > MAX_RESPONSE_BYTES:
        raise KnowledgeError("Knowledge response is too large")
    try:
        obj = json.loads(payload)
    except (UnicodeError, ValueError) as exc:
        raise KnowledgeError("Knowledge returned unreadable data") from exc
    if not isinstance(obj, dict):
        raise KnowledgeError("Unexpected Knowledge response")
    return obj


def search_knowledge(query: str, env: dict[str, str], *, limit: int = MAX_HITS) -> dict[str, object]:
    """Send a deliberate query to a loopback-only search endpoint.

    Search hits are marked unverified and returned to the UI only. The caller
    must never silently inject them into an LLM conversation or a build plan.
    """
    if not isinstance(query, str) or not query.strip() or len(query) > MAX_QUERY_CHARS:
        raise KnowledgeError("Enter a Knowledge search query of 1–500 characters")
    if not isinstance(limit, int) or not 1 <= limit <= MAX_HITS:
        raise KnowledgeError("Knowledge search limit is invalid")

    base = f"http://127.0.0.1:{_port(env)}"
    health = _get_json(urllib.request.Request(base + "/health"), timeout=2)
    if health.get("status") != "ok" or health.get("service") != "search_api":
        raise KnowledgeError("Configured port does not identify a healthy Knowledge search service")

    body = json.dumps({
        "query": query.strip(),
        "source_scope": [],
        "limit": limit,
        "semantic": False,
    }).encode("utf-8")
    response = _get_json(urllib.request.Request(
        base + "/search", data=body,
        headers={"Content-Type": "application/json"}, method="POST",
    ), timeout=8)
    hits = response.get("hits")
    if not isinstance(hits, list):
        raise KnowledgeError("Knowledge search result is missing its evidence list")
    cleaned = []
    for item in hits[:limit]:
        if not isinstance(item, dict):
            continue
        label = item.get("citation_label")
        path = item.get("relative_path")
        excerpt = item.get("preview_text")
        identifier = item.get("segment_id")
        if not all(isinstance(value, str) for value in (label, path, excerpt, identifier)):
            continue
        if any(len(value) > max_length for value, max_length in (
            (label, 180), (path, 300), (excerpt, 500), (identifier, 130),
        )):
            continue
        page = item.get("page_no")
        cleaned.append({
            "citation_label": label,
            "relative_path": path,
            "preview_text": excerpt[:400],
            "segment_id": identifier,
            "page_no": page if isinstance(page, int) and page >= 0 else None,
            "trust": "unverified_indexed_excerpt",
        })
    return {
        "provider": "tof_local_knowledge",
        "query": query.strip(),
        "hits": cleaned,
        "count": len(cleaned),
        "read_only": True,
        "shared_with_model": False,
        "warning": "Search excerpts are indexed references, not verified truth or Builder instructions.",
    }
