"""Optional Knowledge integration: privacy, loopback, and evidence limits."""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from tof_cli.builder.knowledge_ops import KnowledgeError, search_knowledge


class Response:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, limit):
        return self.payload[:limit]


def test_knowledge_requires_explicit_query_and_uses_loopback_only():
    hits = {
        "hits": [{"citation_label": "doc#1", "relative_path": "guides/local.md",
                  "preview_text": "Unverified excerpt", "segment_id": "seg-123",
                  "page_no": 2, "score": 0.9}],
    }
    with patch("tof_cli.builder.knowledge_ops.urllib.request.urlopen",
               side_effect=[Response({"status": "ok", "service": "search_api"}), Response(hits)]) as transport:
        result = search_knowledge("local guidelines", {})
    assert result["read_only"] is True
    assert result["shared_with_model"] is False
    assert result["hits"][0]["trust"] == "unverified_indexed_excerpt"
    assert result["count"] == 1
    health_req = transport.call_args_list[0].args[0]
    search_req = transport.call_args_list[1].args[0]
    assert health_req.full_url == "http://127.0.0.1:8105/health"
    assert search_req.full_url == "http://127.0.0.1:8105/search"
    body = json.loads(search_req.data)
    assert body["query"] == "local guidelines"
    assert body["source_scope"] == []
    assert body["limit"] == 5
    assert body["semantic"] is False


@pytest.mark.parametrize("port", ["0", "-1", "65536", "not-a-port"])
def test_invalid_knowledge_port_fails_before_network(port):
    with patch("tof_cli.builder.knowledge_ops.urllib.request.urlopen") as transport:
        with pytest.raises(KnowledgeError):
            search_knowledge("source", {"BUILDER_KNOWLEDGE_SEARCH_PORT": port})
        transport.assert_not_called()


def test_rejected_health_identity_never_submits_document_query():
    with patch("tof_cli.builder.knowledge_ops.urllib.request.urlopen",
               return_value=Response({"status": "ok", "service": "some_other_service"})) as transport:
        with pytest.raises(KnowledgeError, match="identify"):
            search_knowledge("source", {})
        assert transport.call_count == 1


@pytest.mark.parametrize("query", ["", "x" * 501, None, 22])
def test_invalid_query_fails_without_touching_private_documents(query):
    with patch("tof_cli.builder.knowledge_ops.urllib.request.urlopen") as transport:
        with pytest.raises(KnowledgeError):
            search_knowledge(query, {})
        transport.assert_not_called()


def test_malformed_and_oversize_indexed_results_cannot_escape_bounds():
    hits = [
        {"citation_label": "doc", "relative_path": "large.md",
         "preview_text": "private" * 200, "segment_id": "seg-1"},
        {"citation_label": "doc", "relative_path": "normal.md",
         "preview_text": "small excerpt", "segment_id": "seg-2"},
    ]
    with patch("tof_cli.builder.knowledge_ops.urllib.request.urlopen",
               side_effect=[Response({"status": "ok", "service": "search_api"}),
                            Response({"hits": hits})]):
        result = search_knowledge("something", {})
    assert len(result["hits"]) == 1
    assert result["hits"][0]["segment_id"] == "seg-2"
