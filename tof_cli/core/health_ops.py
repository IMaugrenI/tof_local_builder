from __future__ import annotations

import json
import urllib.error
import urllib.request


def check_url(url: str, timeout: float = 2.0) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            body = response.read(200).decode("utf-8", errors="replace")
            preview = body.strip().replace("\n", " ")
            if len(preview) > 120:
                preview = preview[:117] + "..."
            return status < 500, f"status={status} body={preview}"
    except urllib.error.HTTPError as exc:
        body = exc.read(200).decode("utf-8", errors="replace")
        preview = body.strip().replace("\n", " ")
        return False, f"status={exc.code} body={preview}"
    except Exception as exc:
        return False, f"error={exc}"


def print_health_result(label: str, ok: bool, detail: str) -> None:
    state = "OK" if ok else "FAIL"
    print(f"[{state}] {label}: {detail}")


def print_json(data: dict[str, object]) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))
