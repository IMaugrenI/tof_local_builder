from __future__ import annotations

import webbrowser


def open_url(url: str) -> bool:
    try:
        return bool(webbrowser.open(url, new=2))
    except Exception:
        return False
