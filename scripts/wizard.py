#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from builder_bootstrap import (
    MODEL_OPTIONS,
    apply_setup_values,
    detect_host,
    get_default_env_path,
    host_summary_lines,
    merge_env,
    needs_first_run_wizard,
    normalize_source_path,
    parse_env_file,
    recommended_acceleration_options,
    source_path_valid,
    write_env_file,
)

WIZARD_HOST = "127.0.0.1"
WIZARD_DEFAULT_PORT = 8765
REDIRECT_DEFAULT_PORT = 8766
REDIRECT_TIMEOUT_SECONDS = 900


def _supports_browser(info: dict) -> bool:
    return bool(info.get("supports_gui"))


def _find_free_port(preferred: int) -> int:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((WIZARD_HOST, preferred))
            return preferred
        except OSError:
            sock.bind((WIZARD_HOST, 0))
            return int(sock.getsockname()[1])


def open_webui_browser() -> int:
    env_path = get_default_env_path()
    env, _ = parse_env_file(env_path)
    env = merge_env(env)
    if env.get("BUILDER_OPEN_BROWSER", "1") != "1":
        return 0
    url = f"http://localhost:{env.get('OPENWEBUI_PORT', '3000')}"
    try:
        webbrowser.open(url, new=2)
    except Exception:
        return 1
    return 0


def run_console_wizard(env_path: Path, env: dict, order: list[str], info: dict) -> int:
    current_source = env.get("SOURCE_REPO_PATH", "")
    current_model = env.get("DEFAULT_OLLAMA_MODEL", info["recommended_model"])
    current_acceleration = env.get("BUILDER_ACCELERATION", info["recommended_acceleration"])
    current_browser = env.get("BUILDER_OPEN_BROWSER", "1") == "1"

    print("\nToF Local Builder – Erstsetup / First setup\n")
    print("Dieser Wizard richtet den Builder einmal lokal ein und übergibt danach an die Web-Oberfläche.")
    print("This wizard configures the builder locally once and then hands over to the web UI.\n")
    print("Erkannter Host / Detected host:")
    for line in host_summary_lines(info):
        print(f"- {line}")
    print()

    while True:
        prompt = f"Quellpfad / Source path [{current_source}]: " if current_source else "Quellpfad / Source path: "
        value = input(prompt).strip() or current_source
        value = normalize_source_path(value)
        if source_path_valid(value):
            source_path = value
            break
        print("Pfad ungültig oder nicht vorhanden. Bitte einen existierenden Ordner angeben.\n")
        print("Path is invalid or missing. Please choose an existing directory.\n")

    print("\nModelloptionen / Model options:")
    for index, option in enumerate(MODEL_OPTIONS, start=1):
        print(f"  {index}. {option}")
    while True:
        choice = input(f"Standardmodell / Default model [{current_model}]: ").strip()
        if not choice:
            model = current_model
            break
        if choice.isdigit() and 1 <= int(choice) <= len(MODEL_OPTIONS):
            selected = MODEL_OPTIONS[int(choice) - 1]
            if selected == "custom":
                custom = input("Eigenen Modellnamen eingeben / Enter custom model name: ").strip()
                if custom:
                    model = custom
                    break
            else:
                model = selected
                break
        elif choice:
            model = choice
            break
        print("Ungültige Auswahl. / Invalid selection.\n")

    acceleration_options = recommended_acceleration_options(info)
    print("\nBeschleunigungsoptionen / Acceleration options:")
    for index, option in enumerate(acceleration_options, start=1):
        print(f"  {index}. {option}")
    while True:
        choice = input(f"Beschleunigung / Acceleration [{current_acceleration}]: ").strip()
        if not choice:
            acceleration = current_acceleration
            break
        if choice.isdigit() and 1 <= int(choice) <= len(acceleration_options):
            acceleration = acceleration_options[int(choice) - 1]
            break
        if choice in acceleration_options:
            acceleration = choice
            break
        print("Ungültige Auswahl. / Invalid selection.\n")

    browser_raw = input(
        f"Browser nach dem Start öffnen / Open browser after startup [{'J/Y' if current_browser else 'N'}]: "
    ).strip().lower()
    open_browser = current_browser if not browser_raw else browser_raw in {"j", "ja", "y", "yes", "1"}

    merged = apply_setup_values(
        env,
        source_repo_path=source_path,
        default_model=model,
        acceleration=acceleration,
        open_browser=open_browser,
    )
    write_env_file(env_path, merged, order)

    print("\nSetup gespeichert / Setup saved.")
    print(f"- SOURCE_REPO_PATH={merged['SOURCE_REPO_PATH']}")
    print(f"- DEFAULT_OLLAMA_MODEL={merged['DEFAULT_OLLAMA_MODEL']}")
    print(f"- BUILDER_ACCELERATION={merged['BUILDER_ACCELERATION']}")
    print(f"- BUILDER_OPEN_BROWSER={merged['BUILDER_OPEN_BROWSER']}")
    print()
    return 0


class RedirectBridgeServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], target_url: str, timeout_seconds: int) -> None:
        super().__init__(server_address, RedirectBridgeHandler)
        self.target_url = target_url
        self.expires_at = time.time() + timeout_seconds
        self._shutdown_started = False

    def maybe_shutdown(self, delay: float = 1.0) -> None:
        if self._shutdown_started:
            return
        self._shutdown_started = True

        def _worker() -> None:
            time.sleep(delay)
            self.shutdown()

        threading.Thread(target=_worker, daemon=True).start()

    def target_ready(self) -> bool:
        if time.time() >= self.expires_at:
            self.maybe_shutdown(delay=0.0)
            return False
        try:
            request = urllib.request.Request(self.target_url, method="GET")
            with urllib.request.urlopen(request, timeout=1.5) as response:
                return int(getattr(response, "status", 200)) < 500
        except Exception:
            return False


class RedirectBridgeHandler(BaseHTTPRequestHandler):
    server: RedirectBridgeServer

    def log_message(self, _format: str, *_args) -> None:
        return

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, body: str, status: int = 200) -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/status":
            ready = self.server.target_ready()
            if ready:
                self.server.maybe_shutdown()
            self._send_json({"ready": ready, "target_url": self.server.target_url})
            return
        if parsed.path == "/wait":
            target_label = html.escape(self.server.target_url)
            self._send_html(
                f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>ToF Builder startet / ToF Builder starting</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0b0f14;
      --panel: #11161d;
      --border: #243041;
      --text: #d8dee9;
      --muted: #93a1b5;
      --accent: #69a7ff;
      --ok: #7bd88f;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: linear-gradient(180deg, #0a0f14 0%, #0f151d 100%);
      color: var(--text);
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 24px;
    }}
    .card {{
      width: min(720px, 100%);
      background: rgba(17, 22, 29, 0.96);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 28px;
      box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
    }}
    h1 {{ margin: 0 0 10px; font-size: 1.5rem; }}
    p {{ line-height: 1.6; color: var(--muted); }}
    .pulse {{
      width: 12px;
      height: 12px;
      border-radius: 999px;
      background: var(--accent);
      box-shadow: 0 0 0 0 rgba(105, 167, 255, 0.8);
      animation: pulse 1.6s infinite;
      display: inline-block;
      margin-right: 10px;
    }}
    @keyframes pulse {{
      0% {{ box-shadow: 0 0 0 0 rgba(105, 167, 255, 0.65); }}
      70% {{ box-shadow: 0 0 0 16px rgba(105, 167, 255, 0); }}
      100% {{ box-shadow: 0 0 0 0 rgba(105, 167, 255, 0); }}
    }}
    .status {{
      margin-top: 18px;
      padding: 14px 16px;
      border-radius: 12px;
      background: rgba(11, 15, 20, 0.7);
      border: 1px solid var(--border);
      color: var(--text);
      font-weight: 600;
    }}
    a {{
      color: var(--accent);
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <main class="card">
    <h1><span class="pulse"></span>Setup gespeichert / Setup saved</h1>
    <p>
      Der Builder startet jetzt die Hauptoberfläche. Diese Seite prüft lokal weiter und leitet automatisch um,
      sobald Open WebUI erreichbar ist.
    </p>
    <p>
      The builder is now starting the main interface. This page keeps checking locally and redirects automatically
      as soon as Open WebUI becomes reachable.
    </p>
    <div id="status" class="status">Warte auf Open WebUI… / Waiting for Open WebUI…</div>
    <p>
      Ziel / Target: <a href="{target_label}">{target_label}</a>
    </p>
  </main>
  <script>
    const statusNode = document.getElementById("status");
    const poll = async () => {{
      try {{
        const response = await fetch("/status", {{ cache: "no-store" }});
        const data = await response.json();
        if (data.ready) {{
          statusNode.textContent = "Open WebUI ist bereit. Weiterleitung… / Open WebUI is ready. Redirecting…";
          window.location.replace(data.target_url);
          return;
        }}
        statusNode.textContent = "Stack startet noch… / Stack is still starting…";
      }} catch (_error) {{
        statusNode.textContent = "Prüfe lokale Oberfläche… / Checking local interface…";
      }}
      window.setTimeout(poll, 1200);
    }};
    poll();
  </script>
</body>
</html>"""
            )
            return
        self.send_error(404)


def run_redirect_bridge(port: int, target_url: str) -> int:
    server = RedirectBridgeServer((WIZARD_HOST, port), target_url, REDIRECT_TIMEOUT_SECONDS)
    try:
        server.serve_forever(poll_interval=0.2)
    finally:
        server.server_close()
    return 0


def spawn_redirect_bridge(target_url: str) -> str | None:
    port = _find_free_port(REDIRECT_DEFAULT_PORT)
    args = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--redirect-bridge",
        "--port",
        str(port),
        "--target-url",
        target_url,
    ]
    try:
        subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            start_new_session=True,
        )
    except Exception:
        return None

    status_url = f"http://{WIZARD_HOST}:{port}/status"
    for _ in range(20):
        try:
            with urllib.request.urlopen(status_url, timeout=0.2):
                return f"http://{WIZARD_HOST}:{port}/wait"
        except Exception:
            time.sleep(0.1)
    return f"http://{WIZARD_HOST}:{port}/wait"


class WizardState:
    def __init__(self, env_path: Path, env: dict, order: list[str], info: dict) -> None:
        self.env_path = env_path
        self.env = env
        self.order = order
        self.info = info
        self.saved_event = threading.Event()
        self.cancelled_event = threading.Event()

    @property
    def current_source(self) -> str:
        value = self.env.get("SOURCE_REPO_PATH", "")
        return value if source_path_valid(value) else ""

    @property
    def current_model(self) -> str:
        return self.env.get("DEFAULT_OLLAMA_MODEL", self.info["recommended_model"])

    @property
    def current_acceleration(self) -> str:
        acceleration = self.env.get("BUILDER_ACCELERATION", self.info["recommended_acceleration"])
        options = recommended_acceleration_options(self.info)
        return acceleration if acceleration in options else self.info["recommended_acceleration"]

    @property
    def current_browser(self) -> bool:
        return self.env.get("BUILDER_OPEN_BROWSER", "1") == "1"


class WizardServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], state: WizardState) -> None:
        super().__init__(server_address, WizardHandler)
        self.state = state


class WizardHandler(BaseHTTPRequestHandler):
    server: WizardServer

    def log_message(self, _format: str, *_args) -> None:
        return

    def _send_html(self, body: str, status: int = 200) -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _read_form(self) -> dict[str, str]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        parsed = urllib.parse.parse_qs(raw, keep_blank_values=True)
        return {key: values[-1] if values else "" for key, values in parsed.items()}

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self._send_html(self._wizard_html())
            return
        if parsed.path == "/cancel":
            self.server.state.cancelled_event.set()
            self._send_html(
                """<!doctype html>
<html lang="de"><head><meta charset="utf-8"><title>Wizard abgebrochen</title></head>
<body style="font-family:system-ui;padding:24px;background:#0b0f14;color:#d8dee9">
<h1>Wizard abgebrochen / Wizard cancelled</h1>
<p>Der Start wurde angehalten. Dieses Fenster kann geschlossen werden.</p>
<p>The startup was stopped. You can close this window.</p>
</body></html>"""
            )
            return
        self.send_error(404)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/submit":
            self.send_error(404)
            return

        form = self._read_form()
        state = self.server.state
        info = state.info

        source_path = normalize_source_path(form.get("source_repo_path", ""))
        if not source_path_valid(source_path):
            self._send_html(self._wizard_html(error="Bitte einen existierenden Quellordner wählen. / Please choose an existing source directory."), status=400)
            return

        model_choice = form.get("model", "").strip() or state.current_model
        custom_model = form.get("custom_model", "").strip()
        model = custom_model if model_choice == "custom" else model_choice
        if not model:
            self._send_html(self._wizard_html(error="Bitte ein Modell wählen. / Please choose a model."), status=400)
            return

        acceleration_options = recommended_acceleration_options(info)
        acceleration = form.get("acceleration", "").strip() or state.current_acceleration
        if acceleration not in acceleration_options:
            self._send_html(self._wizard_html(error="Ungültiger Beschleunigungsmodus. / Invalid acceleration mode."), status=400)
            return

        open_browser = form.get("open_browser") == "1"

        merged = apply_setup_values(
            state.env,
            source_repo_path=source_path,
            default_model=model,
            acceleration=acceleration,
            open_browser=open_browser,
        )
        write_env_file(state.env_path, merged, state.order)

        target_url = f"http://localhost:{merged.get('OPENWEBUI_PORT', '3000')}"
        wait_url = spawn_redirect_bridge(target_url) if open_browser else None

        if wait_url:
            self._redirect(wait_url)
        else:
            self._send_html(
                f"""<!doctype html>
<html lang="de">
<head><meta charset="utf-8"><title>Setup gespeichert</title></head>
<body style="font-family:system-ui;padding:24px;background:#0b0f14;color:#d8dee9">
<h1>Setup gespeichert / Setup saved</h1>
<p>Die Einrichtung wurde gespeichert. Der normale Builder-Start läuft jetzt weiter.</p>
<p>The setup was saved. The normal builder startup now continues.</p>
<p>Open WebUI wird nicht automatisch geöffnet. Ziel / Target:
<a href="{html.escape(target_url)}">{html.escape(target_url)}</a></p>
</body>
</html>"""
            )

        state.saved_event.set()

    def _wizard_html(self, error: str | None = None) -> str:
        state = self.server.state
        info = state.info
        acceleration_options = recommended_acceleration_options(info)
        current_model = state.current_model
        if current_model not in MODEL_OPTIONS:
            model_choice = "custom"
            custom_model = current_model
        else:
            model_choice = current_model
            custom_model = ""

        options_html = "".join(
            f'<option value="{html.escape(option)}"{" selected" if option == model_choice else ""}>{html.escape(option)}</option>'
            for option in MODEL_OPTIONS
        )
        acceleration_html = "".join(
            f'<option value="{html.escape(option)}"{" selected" if option == state.current_acceleration else ""}>{html.escape(option)}</option>'
            for option in acceleration_options
        )
        host_cards = "".join(
            f"<li>{html.escape(line)}</li>"
            for line in host_summary_lines(info)
        )
        error_html = (
            f'<div class="notice error">{html.escape(error)}</div>'
            if error
            else ""
        )
        checked = "checked" if state.current_browser else ""
        source_value = html.escape(state.current_source)
        custom_value = html.escape(custom_model)

        return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>ToF Local Builder – Setup</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0b0f14;
      --panel: rgba(17, 22, 29, 0.96);
      --panel-soft: rgba(13, 18, 25, 0.92);
      --border: #223042;
      --text: #d8dee9;
      --muted: #91a0b5;
      --accent: #6ea8fe;
      --accent-strong: #8ab8ff;
      --danger: #ff8f8f;
      --ok: #7bd88f;
      --shadow: 0 28px 90px rgba(0, 0, 0, 0.38);
      --radius: 18px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(110, 168, 254, 0.12), transparent 28%),
        radial-gradient(circle at bottom right, rgba(123, 216, 143, 0.08), transparent 22%),
        linear-gradient(180deg, #091018 0%, #0b0f14 100%);
      color: var(--text);
      min-height: 100vh;
      padding: 32px 20px 48px;
    }}
    .shell {{
      width: min(1040px, 100%);
      margin: 0 auto;
    }}
    .hero {{
      display: grid;
      gap: 24px;
      grid-template-columns: minmax(0, 1.05fr) minmax(320px, 0.95fr);
      align-items: start;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}
    .intro {{
      padding: 28px;
    }}
    .eyebrow {{
      display: inline-flex;
      gap: 8px;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid rgba(110, 168, 254, 0.26);
      background: rgba(110, 168, 254, 0.08);
      color: var(--accent-strong);
      font-size: 0.86rem;
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 16px 0 12px;
      font-size: clamp(1.9rem, 4vw, 3rem);
      line-height: 1.08;
    }}
    p {{
      margin: 0 0 14px;
      color: var(--muted);
      line-height: 1.66;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-top: 22px;
    }}
    .mini {{
      background: var(--panel-soft);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
    }}
    .mini h2 {{
      margin: 0 0 10px;
      font-size: 1rem;
    }}
    .mini ul {{
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
      line-height: 1.55;
    }}
    .form-panel {{
      padding: 28px;
    }}
    .form-title {{
      margin: 0 0 6px;
      font-size: 1.25rem;
    }}
    .notice {{
      margin-bottom: 16px;
      border-radius: 14px;
      padding: 13px 14px;
      border: 1px solid var(--border);
      background: rgba(11, 15, 20, 0.74);
      color: var(--text);
    }}
    .notice.error {{
      border-color: rgba(255, 143, 143, 0.36);
      background: rgba(255, 143, 143, 0.08);
      color: #ffd7d7;
    }}
    form {{
      display: grid;
      gap: 16px;
    }}
    label {{
      display: grid;
      gap: 8px;
      font-size: 0.94rem;
      color: var(--text);
    }}
    label span small {{
      display: block;
      color: var(--muted);
      font-size: 0.83rem;
      margin-top: 4px;
      font-weight: 400;
    }}
    input[type="text"], select {{
      width: 100%;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: rgba(8, 12, 18, 0.92);
      color: var(--text);
      padding: 13px 14px;
      font-size: 0.95rem;
      outline: none;
    }}
    input[type="text"]:focus, select:focus {{
      border-color: rgba(110, 168, 254, 0.7);
      box-shadow: 0 0 0 3px rgba(110, 168, 254, 0.14);
    }}
    .checkbox {{
      display: flex;
      gap: 12px;
      align-items: flex-start;
      background: var(--panel-soft);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
    }}
    .checkbox input {{
      margin-top: 2px;
    }}
    .actions {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 8px;
    }}
    button, .link-button {{
      appearance: none;
      border: 0;
      border-radius: 12px;
      padding: 13px 18px;
      font-size: 0.95rem;
      font-weight: 700;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }}
    button {{
      background: linear-gradient(180deg, #79b0ff 0%, #5f9fff 100%);
      color: #07111b;
      min-width: 220px;
    }}
    .link-button {{
      background: transparent;
      color: var(--muted);
      border: 1px solid var(--border);
    }}
    .host-list {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      gap: 10px;
    }}
    .host-list li {{
      background: var(--panel-soft);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 11px 13px;
      color: var(--muted);
    }}
    @media (max-width: 860px) {{
      .hero {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <div class="hero">
      <section class="panel intro">
        <div class="eyebrow">local setup · de / en</div>
        <h1>ToF Local Builder<br>Erstsetup / First setup</h1>
        <p>
          Diese kurze lokale Seite richtet den Builder einmal ein und übergibt danach an die Hauptoberfläche.
          Die Quelle bleibt read-only. Schreibpfade bleiben in der Sandbox.
        </p>
        <p>
          This short local page configures the builder once and then hands over to the main interface.
          The source remains read-only. Writable paths stay inside the sandbox.
        </p>
        <div class="grid">
          <article class="mini">
            <h2>Was hier gesetzt wird / What gets configured</h2>
            <ul>
              <li>Quellpfad / Source path</li>
              <li>Standardmodell / Default model</li>
              <li>Beschleunigungsmodus / Acceleration mode</li>
              <li>Browser-Weitergabe / Browser handoff</li>
            </ul>
          </article>
          <article class="mini">
            <h2>Ablauf / Flow</h2>
            <ul>
              <li>Setup speichern / Save setup</li>
              <li>Normaler Start läuft weiter / Normal startup continues</li>
              <li>Danach Übergabe an Open WebUI / Then handoff to Open WebUI</li>
            </ul>
          </article>
        </div>
      </section>

      <section class="panel form-panel">
        <h2 class="form-title">Lokale Einrichtung / Local configuration</h2>
        <p>Der Standard bleibt klein und einsteigerfreundlich. / The default stays small and beginner-friendly.</p>
        {error_html}
        <form method="post" action="/submit">
          <label>
            <span>Quellpfad / Source path
              <small>Existierender Ordner, read-only genutzt. / Existing directory, used read-only.</small>
            </span>
            <input type="text" name="source_repo_path" value="{source_value}" placeholder="/home/.../mein_repo" required>
          </label>

          <label>
            <span>Standardmodell / Default model</span>
            <select name="model" id="model">
              {options_html}
            </select>
          </label>

          <label>
            <span>Eigenes Modell / Custom model
              <small>Nur nötig, wenn oben „custom“ gewählt ist. / Only needed when “custom” is selected above.</small>
            </span>
            <input type="text" id="custom_model" name="custom_model" value="{custom_value}" placeholder="qwen2.5-coder:1.5b">
          </label>

          <label>
            <span>Beschleunigungsmodus / Acceleration mode</span>
            <select name="acceleration">
              {acceleration_html}
            </select>
          </label>

          <label class="checkbox">
            <input type="checkbox" name="open_browser" value="1" {checked}>
            <span>
              <strong>Nach dem Start automatisch an die Hauptoberfläche übergeben / Automatically hand off to the main interface after startup</strong>
            </span>
          </label>

          <div class="actions">
            <button type="submit">Speichern und weiter / Save and continue</button>
            <a class="link-button" href="/cancel">Abbrechen / Cancel</a>
          </div>
        </form>
      </section>
    </div>

    <section class="panel" style="margin-top:24px;padding:24px;">
      <h2 style="margin-top:0;">Erkannter Host / Detected host</h2>
      <ul class="host-list">
        {host_cards}
      </ul>
    </section>
  </div>
  <script>
    const modelSelect = document.getElementById("model");
    const customInput = document.getElementById("custom_model");
    const syncCustomState = () => {{
      const enabled = modelSelect.value === "custom";
      customInput.disabled = !enabled;
      if (!enabled) {{
        customInput.value = "";
      }}
    }};
    modelSelect.addEventListener("change", syncCustomState);
    syncCustomState();
  </script>
</body>
</html>"""


def run_web_wizard(env_path: Path, env: dict, order: list[str], info: dict) -> int:
    state = WizardState(env_path, env, order, info)
    port = _find_free_port(WIZARD_DEFAULT_PORT)
    server = WizardServer((WIZARD_HOST, port), state)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.2}, daemon=True)
    thread.start()

    url = f"http://{WIZARD_HOST}:{port}/"
    print(f"Opening setup wizard: {url}")
    opened = False
    try:
        opened = webbrowser.open(url, new=1)
    except Exception:
        opened = False
    if not opened:
        print("Browser konnte nicht automatisch geöffnet werden. / Browser could not be opened automatically.")
        print(f"Bitte lokal öffnen / Please open locally: {url}")

    try:
        while True:
            if state.saved_event.wait(timeout=0.2):
                return 0
            if state.cancelled_event.is_set():
                return 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2.0)


def ensure_wizard(force: bool = False) -> int:
    env_path = get_default_env_path()
    env, order = parse_env_file(env_path)
    env = merge_env(env)
    info = detect_host()
    if not force and not needs_first_run_wizard(env):
        return 0
    if _supports_browser(info):
        return run_web_wizard(env_path, env, order, info)
    return run_console_wizard(env_path, env, order, info)


def main() -> int:
    parser = argparse.ArgumentParser(description="ToF Local Builder setup wizard")
    parser.add_argument("--ensure", action="store_true", help="run the wizard only when setup is incomplete")
    parser.add_argument("--force", action="store_true", help="force the wizard to run")
    parser.add_argument("--open-webui", action="store_true", help="open the local WebUI in the default browser")
    parser.add_argument("--redirect-bridge", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--port", type=int, default=0, help=argparse.SUPPRESS)
    parser.add_argument("--target-url", default="", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.redirect_bridge:
        if not args.port or not args.target_url:
            return 2
        return run_redirect_bridge(args.port, args.target_url)
    if args.open_webui:
        return open_webui_browser()
    if args.force:
        return ensure_wizard(force=True)
    if args.ensure:
        return ensure_wizard(force=False)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
