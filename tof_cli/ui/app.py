from __future__ import annotations

import io
import json
import urllib.error
import urllib.request
import webbrowser
from contextlib import redirect_stdout
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable
from urllib.parse import urlparse

from tof_cli.commands import check, doctor, down, setup, status, up


@dataclass(frozen=True)
class ActionSpec:
    label: str
    handler: Callable[..., int]
    kwargs: dict[str, object]
    safe_level: str


ACTIONS = {
    "setup": ActionSpec("Prepare local setup", setup.handle, {}, "SAFE"),
    "up": ActionSpec("Start builder stack", up.handle, {"skip_wizard": False, "skip_model_ensure": False}, "SAFE"),
    "check": ActionSpec("Check services", check.handle, {}, "SAFE"),
    "status": ActionSpec("Show runtime status", status.handle, {}, "SAFE"),
    "doctor": ActionSpec("Run doctor", doctor.handle, {}, "SAFE"),
    "down": ActionSpec("Stop stack", down.handle, {"remove_orphans": False}, "SAFE"),
}

LINKS = {
    "openwebui": {"label": "Open WebUI", "url": "http://127.0.0.1:3000"},
    "repo_bridge_health": {"label": "Open repo bridge health", "url": "http://127.0.0.1:8099/health"},
    "ollama": {"label": "Open Ollama endpoint", "url": "http://127.0.0.1:11434"},
}

READINESS_TARGETS = {
    "webui": {"label": "WebUI", "url": "http://127.0.0.1:3000"},
    "repo_bridge": {"label": "Repo bridge", "url": "http://127.0.0.1:8099/health"},
    "ollama": {"label": "Ollama", "url": "http://127.0.0.1:11434"},
}


HTML = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>tof_local_builder</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; background: #f5f7fb; color: #18212f; }
    .wrap { max-width: 1080px; margin: 0 auto; padding: 24px; }
    .hero, .panel { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); }
    .panel { margin-top: 20px; }
    .lead { color: #4b5563; line-height: 1.5; }
    .note { color: #6b7280; font-size: 14px; }
    .actions, .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-top: 18px; }
    .card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; }
    .card .value { font-size: 20px; font-weight: 700; margin-top: 6px; }
    button { border: 0; border-radius: 12px; padding: 14px 16px; font-size: 15px; cursor: pointer; background: #1f6feb; color: white; }
    button.secondary { background: #0f766e; }
    button.ghost { background: #e5e7eb; color: #111827; }
    .status { margin-top: 18px; background: #ecfeff; border: 1px solid #a5f3fc; color: #164e63; border-radius: 14px; padding: 16px; }
    .log { margin-top: 18px; background: #111827; color: #d1fae5; border-radius: 14px; padding: 16px; min-height: 260px; }
    pre { margin: 0; white-space: pre-wrap; word-break: break-word; }
    h1 { margin-top: 0; }
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"hero\">
      <h1>tof_local_builder</h1>
      <p class=\"lead\">A simple local control surface for the builder stack. Use the buttons below to prepare the system, start the stack, check it, inspect readiness, open the main local pages, or stop it again.</p>
      <p class=\"note\">This is a local-only helper UI. It does not replace the main builder workspace itself.</p>
    </div>

    <div class=\"panel\">
      <h2>Readiness</h2>
      <div class=\"cards\" id=\"cards\"></div>
      <div class=\"status\" id=\"next-step\">Loading current guidance ...</div>
    </div>

    <div class=\"panel\">
      <h2>Main actions</h2>
      <div class=\"actions\">
        <button onclick=\"runAction('setup')\">1. Prepare local setup</button>
        <button class=\"secondary\" onclick=\"runAction('up')\">2. Start builder stack</button>
        <button onclick=\"runAction('check')\">3. Check services</button>
        <button class=\"ghost\" onclick=\"runAction('status')\">Show runtime status</button>
        <button class=\"ghost\" onclick=\"runAction('doctor')\">Run doctor</button>
        <button onclick=\"runAction('down')\">Stop stack</button>
      </div>
      <h3 style=\"margin-top:22px;\">Useful links</h3>
      <div class=\"actions\">
        <button class=\"ghost\" onclick=\"openLink('openwebui')\">Open WebUI</button>
        <button class=\"ghost\" onclick=\"openLink('repo_bridge_health')\">Open repo bridge health</button>
        <button class=\"ghost\" onclick=\"openLink('ollama')\">Open Ollama endpoint</button>
      </div>
      <div class=\"log\"><pre id=\"log\">Starting tof_local_builder UI...</pre></div>
    </div>
  </div>
  <script>
    function appendLog(text) {
      const log = document.getElementById('log');
      log.textContent = `[${new Date().toLocaleTimeString()}] ${text}\n\n` + log.textContent;
    }

    function renderCards(data) {
      const root = document.getElementById('cards');
      root.innerHTML = '';
      for (const item of data.items || []) {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `<div>${item.label}</div><div class=\"value\">${item.state}</div><div>${item.url}</div>`;
        root.appendChild(card);
      }
    }

    async function refreshSummary() {
      const response = await fetch('/api/summary');
      const data = await response.json();
      document.getElementById('next-step').textContent = data.next_step;
      renderCards(data.readiness || { items: [] });
      appendLog('Summary refreshed.');
    }

    async function runAction(action) {
      appendLog(`Running ${action} ...`);
      const response = await fetch(`/api/${action}`, { method: 'POST' });
      const data = await response.json();
      appendLog(JSON.stringify(data, null, 2));
      await refreshSummary();
    }

    async function openLink(name) {
      appendLog(`Opening ${name} ...`);
      const response = await fetch(`/api/open/${name}`, { method: 'POST' });
      const data = await response.json();
      appendLog(JSON.stringify(data, null, 2));
    }

    refreshSummary();
  </script>
</body>
</html>
"""


def _run_action(name: str) -> dict[str, object]:
    spec = ACTIONS[name]
    namespace = type("Args", (), spec.kwargs)()
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = spec.handler(namespace)
    output = buffer.getvalue().strip()
    return {
        "action": name,
        "label": spec.label,
        "safe_level": spec.safe_level,
        "exit_code": int(code or 0),
        "output": output,
    }



def _open_link(name: str) -> dict[str, object]:
    link = LINKS[name]
    webbrowser.open(link["url"])
    return {"opened": link["url"], "label": link["label"]}



def _probe_url(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            code = getattr(response, 'status', 200)
            return 'ready' if int(code) < 500 else f'http_{code}'
    except urllib.error.HTTPError as exc:
        return f'http_{exc.code}'
    except Exception:
        return 'not_reachable'



def _readiness_payload() -> dict[str, object]:
    items = []
    for key, target in READINESS_TARGETS.items():
        state = _probe_url(target['url'])
        items.append({'name': key, 'label': target['label'], 'url': target['url'], 'state': state})
    return {'items': items}



def _summary_payload() -> dict[str, object]:
    readiness = _readiness_payload()
    webui_ready = any(item['name'] == 'webui' and item['state'] == 'ready' for item in readiness['items'])
    next_step = (
        'WebUI is reachable. Open WebUI and continue the real builder work there.'
        if webui_ready
        else 'Recommended order: prepare local setup, start the builder stack, check services, then wait until WebUI becomes reachable.'
    )
    return {
        'next_step': next_step,
        'actions': [
            {'name': key, 'label': spec.label, 'safe_level': spec.safe_level}
            for key, spec in ACTIONS.items()
        ],
        'links': LINKS,
        'readiness': readiness,
    }



def _json_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, indent=2).encode('utf-8')



def run_ui(host: str = '127.0.0.1', port: int = 8795, open_browser: bool = True) -> int:
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, content_type: str, body: bytes) -> None:
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == '/':
                self._send(200, 'text/html; charset=utf-8', HTML.encode('utf-8'))
                return
            if parsed.path == '/api/summary':
                self._send(200, 'application/json; charset=utf-8', _json_bytes(_summary_payload()))
                return
            self._send(404, 'application/json; charset=utf-8', _json_bytes({'error': 'not found'}))

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            action = parsed.path.removeprefix('/api/')
            if action in ACTIONS:
                self._send(200, 'application/json; charset=utf-8', _json_bytes(_run_action(action)))
                return
            if action.startswith('open/'):
                name = action.removeprefix('open/')
                if name in LINKS:
                    self._send(200, 'application/json; charset=utf-8', _json_bytes(_open_link(name)))
                    return
            self._send(404, 'application/json; charset=utf-8', _json_bytes({'error': 'not found'}))

        def log_message(self, fmt: str, *args: object) -> None:  # noqa: A003
            return

    server = ThreadingHTTPServer((host, port), Handler)
    url = f'http://{host}:{port}'
    print(json.dumps({'ui_url': url, 'message': 'tof_local_builder UI is running'}, indent=2))
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
