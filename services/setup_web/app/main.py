from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

sys.path.insert(0, "/app/scripts")

from builder_bootstrap import (  # type: ignore
    MODEL_OPTIONS,
    apply_setup_values,
    detect_host,
    is_placeholder_source,
    merge_env,
    parse_env_file,
    recommended_acceleration_options,
    write_env_file,
)

APP_TITLE = "tof_local_builder_setup_web"
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://127.0.0.1:3000")
ENV_FILE_PATH = Path(os.getenv("ENV_FILE_PATH", "/workspace/repo/.env")).resolve()

app = FastAPI(title=APP_TITLE, version="0.1.1")


class SaveSetupRequest(BaseModel):
    source_repo_path: str
    default_model: str
    acceleration: str
    open_browser: bool = True


def load_env() -> tuple[dict[str, str], list[str]]:
    env, order = parse_env_file(ENV_FILE_PATH)
    return merge_env(env), order


def web_setup_saved(env: dict[str, str]) -> bool:
    source = (env.get("SOURCE_REPO_PATH") or "").strip()
    if env.get("BUILDER_SETUP_DONE") != "1":
        return False
    if is_placeholder_source(source):
        return False
    if not env.get("HOST_UID") or not env.get("HOST_GID"):
        return False
    return True


def normalize_web_source_path(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        return ""
    if candidate.startswith("~"):
        return candidate
    if candidate.startswith("/"):
        return str(Path(candidate).resolve())
    return candidate


@app.get("/health")
def health() -> dict[str, object]:
    env, _ = load_env()
    return {
        "status": "ok",
        "configured": web_setup_saved(env),
        "env_file": str(ENV_FILE_PATH),
        "openwebui_url": OPENWEBUI_URL,
    }


@app.get("/api/state")
def api_state() -> dict[str, object]:
    env, _ = load_env()
    info = detect_host()
    return {
        "configured": web_setup_saved(env),
        "env_file": str(ENV_FILE_PATH),
        "openwebui_url": OPENWEBUI_URL,
        "host": info,
        "model_options": MODEL_OPTIONS,
        "acceleration_options": recommended_acceleration_options(info),
        "current": {
            "source_repo_path": env.get("SOURCE_REPO_PATH", ""),
            "default_model": env.get("DEFAULT_OLLAMA_MODEL", info["recommended_model"]),
            "acceleration": env.get("BUILDER_ACCELERATION", info["recommended_acceleration"]),
            "open_browser": env.get("BUILDER_OPEN_BROWSER", "1") == "1",
        },
    }


@app.post("/api/save")
def api_save(payload: SaveSetupRequest) -> dict[str, object]:
    env, order = load_env()
    info = detect_host()
    normalized_source = normalize_web_source_path(payload.source_repo_path)
    if not normalized_source or is_placeholder_source(normalized_source):
        raise HTTPException(status_code=400, detail="SOURCE_REPO_PATH is missing or invalid.")
    allowed_acceleration = recommended_acceleration_options(info)
    if payload.acceleration not in allowed_acceleration:
        raise HTTPException(status_code=400, detail="Acceleration option is invalid for this host.")
    default_model = payload.default_model.strip()
    if not default_model:
        raise HTTPException(status_code=400, detail="DEFAULT_OLLAMA_MODEL must not be empty.")
    merged = apply_setup_values(
        env,
        source_repo_path=normalized_source,
        default_model=default_model,
        acceleration=payload.acceleration,
        open_browser=payload.open_browser,
    )
    write_env_file(ENV_FILE_PATH, merged, order)
    return {
        "status": "ok",
        "configured": web_setup_saved(merged),
        "openwebui_url": OPENWEBUI_URL,
        "saved": {
            "SOURCE_REPO_PATH": merged["SOURCE_REPO_PATH"],
            "DEFAULT_OLLAMA_MODEL": merged["DEFAULT_OLLAMA_MODEL"],
            "BUILDER_ACCELERATION": merged["BUILDER_ACCELERATION"],
            "BUILDER_OPEN_BROWSER": merged["BUILDER_OPEN_BROWSER"],
            "BUILDER_SETUP_DONE": merged["BUILDER_SETUP_DONE"],
        },
    }


INDEX_HTML = """<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <title>ToF Local Builder – GUiX Setup</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b0f14;
      --panel: #111822;
      --panel-2: #17212e;
      --text: #e6edf3;
      --muted: #9fb0c0;
      --line: #29415d;
      --accent: #1793d1;
      --ok: #3fb950;
      --warn: #d29922;
      --err: #f85149;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      background: linear-gradient(180deg, #0b0f14 0%, #0d131b 100%);
      color: var(--text);
    }
    .shell {
      width: min(1000px, calc(100vw - 32px));
      margin: 24px auto;
      display: grid;
      gap: 16px;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.28);
    }
    h1, h2, h3 { margin: 0 0 12px; }
    h1 { font-size: 28px; }
    h2 { font-size: 18px; }
    p, li { color: var(--muted); line-height: 1.5; }
    .grid-2 {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }
    .grid-3 {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }
    label {
      display: block;
      font-size: 14px;
      margin-bottom: 8px;
      color: var(--text);
      font-weight: 600;
    }
    .hint {
      color: var(--muted);
      font-size: 13px;
      margin-top: 6px;
    }
    input[type="text"], select {
      width: 100%;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: var(--panel-2);
      color: var(--text);
      outline: none;
    }
    input[type="checkbox"] {
      transform: translateY(1px);
      margin-right: 8px;
    }
    .button-row {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      align-items: center;
    }
    button, .button-link {
      border: 0;
      border-radius: 12px;
      padding: 12px 16px;
      background: var(--accent);
      color: white;
      font-weight: 700;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    button.secondary, .button-link.secondary {
      background: #233246;
      color: var(--text);
    }
    .status-pill {
      display: inline-flex;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      background: #1f2a38;
      color: var(--text);
    }
    .status-ok { background: rgba(63, 185, 80, 0.15); color: #7ee787; }
    .status-warn { background: rgba(210, 153, 34, 0.15); color: #e3b341; }
    .status-err { background: rgba(248, 81, 73, 0.15); color: #ff7b72; }
    .mono {
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
    }
    .kv {
      display: grid;
      grid-template-columns: 180px 1fr;
      gap: 8px 12px;
      align-items: start;
    }
    .kv div:nth-child(odd) {
      color: var(--text);
      font-weight: 600;
    }
    .banner {
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: #0f1722;
      color: var(--muted);
    }
    .success {
      border-color: rgba(63, 185, 80, 0.3);
      background: rgba(63, 185, 80, 0.08);
      color: #9ee2a2;
    }
    .error {
      border-color: rgba(248, 81, 73, 0.3);
      background: rgba(248, 81, 73, 0.08);
      color: #ffb1ac;
    }
    .small {
      font-size: 12px;
      color: var(--muted);
    }
    @media (max-width: 760px) {
      .grid-2, .grid-3, .kv { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="card">
      <div class="button-row" style="justify-content: space-between;">
        <div>
          <h1>ToF Local Builder – GUiX Setup</h1>
          <p>Lokaler Web-First-Wizard vor der Hauptoberfläche. / Local web-first wizard before the main surface.</p>
        </div>
        <div id="configured-pill" class="status-pill status-warn">Setup offen / Setup pending</div>
      </div>
    </section>

    <section class="card">
      <h2>Was passiert hier? / What happens here?</h2>
      <div class="grid-2">
        <div>
          <p>1. Du trägst den Quellpfad ein.</p>
          <p>2. Du wählst Modell und Beschleunigung.</p>
          <p>3. Der Wizard speichert die lokale <span class="mono">.env</span>.</p>
          <p>4. Danach startet der Hauptstack weiter und die Seite leitet auf Open WebUI um.</p>
        </div>
        <div>
          <p>1. Enter the source path.</p>
          <p>2. Choose model and acceleration.</p>
          <p>3. The wizard writes the local <span class="mono">.env</span>.</p>
          <p>4. Then the main stack continues and the page redirects to Open WebUI.</p>
        </div>
      </div>
    </section>

    <section class="card">
      <h2>Host-Erkennung / Host detection</h2>
      <div id="host-grid" class="grid-3"></div>
    </section>

    <section class="card">
      <h2>Einrichtung / Setup</h2>
      <form id="setup-form">
        <div style="margin-bottom: 16px;">
          <label for="source_repo_path">Quellpfad / Source path</label>
          <input id="source_repo_path" name="source_repo_path" type="text" placeholder="/absolute/path/to/source/repo" />
          <div class="hint">Read-only Quelle für die Builder-Leseseite. / Read-only source for the builder read side.</div>
        </div>

        <div class="grid-2">
          <div>
            <label for="default_model">Standardmodell / Default model</label>
            <select id="default_model" name="default_model"></select>
          </div>
          <div>
            <label for="acceleration">Beschleunigung / Acceleration</label>
            <select id="acceleration" name="acceleration"></select>
          </div>
        </div>

        <div style="margin-top: 16px;">
          <label>
            <input id="open_browser" name="open_browser" type="checkbox" />
            Browser nach Stack-Start automatisch öffnen / Open browser automatically after stack start
          </label>
        </div>

        <div id="message" class="banner" style="margin-top: 16px;">
          Noch nicht gespeichert. / Not saved yet.
        </div>

        <div class="button-row" style="margin-top: 16px;">
          <button type="submit">Speichern und weiter / Save and continue</button>
          <a id="openwebui-link" class="button-link secondary" href="#" target="_blank" rel="noreferrer">Open WebUI</a>
        </div>
      </form>
    </section>

    <section class="card">
      <h2>Aktuelle Werte / Current values</h2>
      <div id="current-values" class="kv mono"></div>
      <p class="small">Wenn der Startpfad noch nicht fertig ist, bleibt diese Seite offen, speichert aber schon sauber die Builder-Konfiguration. / If the main stack is not ready yet, this page stays available while still saving the builder configuration cleanly.</p>
    </section>
  </main>

  <script>
    const stateUrl = "/api/state";
    const saveUrl = "/api/save";
    const hostGrid = document.getElementById("host-grid");
    const currentValues = document.getElementById("current-values");
    const form = document.getElementById("setup-form");
    const message = document.getElementById("message");
    const configuredPill = document.getElementById("configured-pill");
    const sourceInput = document.getElementById("source_repo_path");
    const modelSelect = document.getElementById("default_model");
    const accelerationSelect = document.getElementById("acceleration");
    const browserCheckbox = document.getElementById("open_browser");
    const openWebUiLink = document.getElementById("openwebui-link");
    let latestOpenWebUiUrl = "http://127.0.0.1:3000";

    function boolText(value) {
      return value ? "ja / yes" : "nein / no";
    }

    function renderHost(info) {
      const rows = [
        ["OS", `${info.system} ${info.release}`],
        ["Architektur / Architecture", info.machine],
        ["CPU-Kerne / CPU cores", String(info.cpu_cores)],
        ["RAM", info.ram_gb === null ? "unbekannt / unknown" : `${info.ram_gb} GiB`],
        ["Docker installiert / installed", boolText(info.docker_available)],
        ["Docker erreichbar / reachable", boolText(info.docker_reachable)],
        ["/dev/dri", boolText(info.has_dri)],
        ["Render-Node", boolText(info.has_render_node)],
        ["NVIDIA", boolText(info.has_nvidia)],
        ["Empfohlen / Recommended accel", info.recommended_acceleration],
        ["Empfohlenes Modell / Recommended model", info.recommended_model],
      ];
      hostGrid.innerHTML = rows.map(([k, v]) => `
        <div class="banner">
          <div class="small">${k}</div>
          <div class="mono">${v}</div>
        </div>
      `).join("");
    }

    function renderCurrent(current, configured) {
      const rows = [
        ["SOURCE_REPO_PATH", current.source_repo_path || "-"],
        ["DEFAULT_OLLAMA_MODEL", current.default_model || "-"],
        ["BUILDER_ACCELERATION", current.acceleration || "-"],
        ["BUILDER_OPEN_BROWSER", current.open_browser ? "1" : "0"],
        ["BUILDER_SETUP_DONE", configured ? "1" : "0"],
      ];
      currentValues.innerHTML = rows.map(([k, v]) => `<div>${k}</div><div>${v}</div>`).join("");
    }

    function renderOptions(select, values, selectedValue) {
      select.innerHTML = values.map((value) => `<option value="${value}">${value}</option>`).join("");
      if (selectedValue && values.includes(selectedValue)) {
        select.value = selectedValue;
      }
    }

    function renderConfigured(configured) {
      configuredPill.textContent = configured ? "Setup fertig / Setup done" : "Setup offen / Setup pending";
      configuredPill.className = configured ? "status-pill status-ok" : "status-pill status-warn";
    }

    function setMessage(text, kind = "normal") {
      message.textContent = text;
      message.className = "banner";
      if (kind === "success") {
        message.classList.add("success");
      } else if (kind === "error") {
        message.classList.add("error");
      }
    }

    async function loadState() {
      const response = await fetch(stateUrl);
      if (!response.ok) {
        throw new Error("State fetch failed");
      }
      const data = await response.json();
      latestOpenWebUiUrl = data.openwebui_url;
      openWebUiLink.href = latestOpenWebUiUrl;
      renderConfigured(data.configured);
      renderHost(data.host);
      renderOptions(modelSelect, data.model_options, data.current.default_model);
      renderOptions(accelerationSelect, data.acceleration_options, data.current.acceleration);
      sourceInput.value = data.current.source_repo_path || "";
      browserCheckbox.checked = Boolean(data.current.open_browser);
      renderCurrent(data.current, data.configured);
      if (data.configured) {
        setMessage("Setup bereits gespeichert. Die Hauptoberfläche liegt unter " + latestOpenWebUiUrl, "success");
      }
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      setMessage("Speichere lokale Builder-Konfiguration ... / Saving local builder configuration ...");
      const payload = {
        source_repo_path: sourceInput.value,
        default_model: modelSelect.value,
        acceleration: accelerationSelect.value,
        open_browser: browserCheckbox.checked,
      };
      const response = await fetch(saveUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        setMessage(data.detail || "Speichern fehlgeschlagen / Save failed", "error");
        return;
      }
      renderConfigured(true);
      renderCurrent(
        {
          source_repo_path: data.saved.SOURCE_REPO_PATH,
          default_model: data.saved.DEFAULT_OLLAMA_MODEL,
          acceleration: data.saved.BUILDER_ACCELERATION,
          open_browser: data.saved.BUILDER_OPEN_BROWSER === "1",
        },
        true,
      );
      setMessage("Setup gespeichert. Der Builder startet jetzt weiter. Weiterleitung auf Open WebUI in 8 Sekunden ... / Setup saved. The builder now continues. Redirecting to Open WebUI in 8 seconds ...", "success");
      setTimeout(() => {
        window.location.href = latestOpenWebUiUrl;
      }, 8000);
    });

    loadState().catch(() => {
      setMessage("Setup-Status konnte nicht geladen werden. / Could not load setup state.", "error");
    });
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML)
