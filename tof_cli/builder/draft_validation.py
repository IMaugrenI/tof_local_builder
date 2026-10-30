"""Static, non-executing checks for small generated sandbox text files.

Validation is deliberately narrower than a test run: only parse supported
formats. Unsupported formats are visibly marked unchecked, never called valid.
"""
from __future__ import annotations

import ast
import json
import tomllib
from pathlib import PurePosixPath


class DraftSyntaxError(ValueError):
    """The generated text did not pass a supported static parser."""


def check_draft(relative_file: str, content: str) -> str:
    """Return a precise check label; never import or execute generated code."""
    if not isinstance(content, str) or not content.strip():
        raise DraftSyntaxError("Generated text is empty")
    if "\x00" in content:
        raise DraftSyntaxError("Generated text contains a NUL byte")
    extension = PurePosixPath(relative_file).suffix.casefold()
    try:
        if extension == ".py":
            ast.parse(content, filename=relative_file)
            return "python_syntax_ok"
        if extension == ".json":
            json.loads(content)
            return "json_syntax_ok"
        if extension == ".toml":
            tomllib.loads(content)
            return "toml_syntax_ok"
    except (SyntaxError, ValueError) as exc:
        description = getattr(exc, "msg", str(exc))
        raise DraftSyntaxError(f"{extension} syntax check failed: {description}") from exc
    return "not_checked"  # Do not imply CSS, JS, Markdown, etc. were validated.
