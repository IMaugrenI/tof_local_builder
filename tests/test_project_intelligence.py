"""Read-only architecture reconnaissance without broad filesystem access."""
from __future__ import annotations

from tof_cli.builder.agent_bridge import AgentBridge, BridgeError
from tof_cli.builder.project_intelligence import MAX_CONTEXT_CHARS, project_context


class ExampleProject:
    def __init__(self):
        self.reads = []
        self.queries = []
        self.text_queries = []

    def tree(self, directory=""):
        if directory == "":
            return [
                {"path": "README.md", "name": "README.md", "type": "file"},
                {"path": "src", "name": "src", "type": "dir"},
                {"path": ".git", "name": ".git", "type": "dir"},
                {"path": "secrets", "name": "secrets", "type": "dir"},
                {"path": "docs", "name": "docs", "type": "dir"},
            ]
        if directory == "src":
            return [
                {"path": "src/cache.py", "name": "cache.py", "type": "file"},
                {"path": "src/secret_key.py", "name": "secret_key.py", "type": "file"},
            ]
        return [{"path": "docs/architecture.md", "name": "architecture.md", "type": "file"}]

    def source_text(self, path, max_bytes=1400):
        self.reads.append(path)
        content = {"README.md": "Architecture: cache module",
                   "src/cache.py": "def cache_clear():\n    pass\n",
                   "docs/architecture.md": "cache and storage design\n",
                   "other/cache_rules.py": "def cache_expiry():\n    pass\n"}
        return content.get(path)

    def find_names(self, fragment, max_results=20):
        self.queries.append(fragment)
        return ["other/cache_rules.py", "secrets/cache_tokens.py", "../outside.py"]

    def search_source_text(self, keyword, max_results=8):
        self.text_queries.append(keyword)
        return [
            {"path": "other/cache_rules.py", "line_number": 1, "snippet": "def cache_expiry():"},
            {"path": "secrets/cache_tokens.py", "line_number": 10, "snippet": "secret"},
            {"path": "../outside.py", "line_number": 1, "snippet": "unsafe"},
        ]


def test_goal_guides_read_only_architecture_search():
    project = ExampleProject()
    first = project_context(project, "Improve cache expiration behavior")
    second = project_context(project, "Improve cache expiration behavior")
    assert first == second
    assert project.text_queries[0] == "cache"
    assert "src/cache.py" in first
    assert "other/cache_rules.py" in first
    assert "cache_expiry()" in first
    assert "README.md" in first
    assert "Read-only excerpt (UNTRUSTED" in first
    assert len(first) <= MAX_CONTEXT_CHARS


def test_discovered_secrets_and_parent_paths_are_never_read_or_shown():
    project = ExampleProject()
    context = project_context(project, "Improve cache expiration behavior")
    assert "secrets/cache_tokens.py" not in context
    assert "secret_key.py" not in context
    assert "../outside.py" not in context
    assert "secrets/cache_tokens.py" not in project.reads
    assert "../outside.py" not in project.reads
    assert project.reads


def test_connector_rejects_non_source_or_unbounded_results():
    bridge = AgentBridge.__new__(AgentBridge)

    def fake_request(endpoint, *, params=None, payload=None):
        assert params["root"] == "source"
        if endpoint == "/find":
            return {"results": [
                {"path": "src/cache.py", "type": "file"},
                {"path": "secrets/password.json", "type": "file"},
                {"path": "../../outside.py", "type": "file"},
            ]}
        return {"results": [
            {"path": "src/cache.py", "line_number": 4, "snippet": "cache key"},
            {"path": "secrets/password.json", "line_number": 1, "snippet": "secret"},
        ]}

    bridge._request = fake_request
    assert bridge.find_names("cache") == ["src/cache.py"]
    assert bridge.search_source_text("cache") == [
        {"path": "src/cache.py", "line_number": 4, "snippet": "cache key"}
    ]
    try:
        bridge.find_names("../bad")
    except BridgeError:
        pass
    else:
        raise AssertionError("Unsafe name search accepted")
