from __future__ import annotations

import json
import os
import sys
import urllib.request
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
OPENWEBUI_BROWSER_URL = os.getenv("OPENWEBUI_BROWSER_URL", "http://127.0.0.1:3000")
OPENWEBUI_READY_URL = os.getenv("OPENWEBUI_READY_URL", "http://open-webui:8080")
ENV_FILE_PATH = Path(os.getenv("ENV_FILE_PATH", "/workspace/repo/.env")).resolve()
HOST_SNAPSHOT_PATH = Path(os.getenv("HOST_SNAPSHOT_PATH", "/workspace/repo/.runtime/host_snapshot.json")).resolve()

app = FastAPI(title=APP_TITLE, version="0.1.3")


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


def load_host_info() -> dict[str, object]:
    info: dict[str, object] | None = None
    warning: str | None = None
    source = "host_snapshot"
    if HOST_SNAPSHOT_PATH.exists():
        try:
            raw = json.loads(HOST_SNAPSHOT_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                info = dict(raw)
            else:
                warning = "Host snapshot is invalid."
        except (OSError, json.JSONDecodeError):
            warning = "Host snapshot could not be read."
    if info is None:
        info = detect_host()
        source = "container_fallback"
        if warning is None:
            warning = "Falling back to container-local detection. Host capabilities may be incomplete."
    info.setdefault("recommended_model", MODEL_OPTIONS[0])
    info.setdefault("recommended_acceleration", "cpu")
    options = info.get("acceleration_options")
    if not isinstance(options, list) or not options:
        info["acceleration_options"] = recommended_acceleration_options(info)
    else:
        info["acceleration_options"] = [str(item) for item in options]
    info["model_options"] = list(MODEL_OPTIONS)
    info["host_info_source"] = source
    if warning:
        info["host_info_warning"] = warning
    return info


def openwebui_ready() -> bool:
    try:
        request = urllib.request.Request(OPENWEBUI_READY_URL, method="GET")
        with urllib.request.urlopen(request, timeout=1.5) as response:
            return int(getattr(response, "status", 200)) < 500
    except Exception:
        return False


@app.get("/health")
def health() -> dict[str, object]:
    env, _ = load_env()
    host = load_host_info()
    return {
        "status": "ok",
        "configured": web_setup_saved(env),
        "env_file": str(ENV_FILE_PATH),
        "host_snapshot_path": str(HOST_SNAPSHOT_PATH),
        "openwebui_url": OPENWEBUI_BROWSER_URL,
        "openwebui_ready_url": OPENWEBUI_READY_URL,
        "openwebui_ready": openwebui_ready(),
        "host_info_source": host.get("host_info_source"),
    }


@app.get("/api/state")
def api_state() -> dict[str, object]:
    env, _ = load_env()
    info = load_host_info()
    return {
        "configured": web_setup_saved(env),
        "env_file": str(ENV_FILE_PATH),
        "host_snapshot_path": str(HOST_SNAPSHOT_PATH),
        "openwebui_url": OPENWEBUI_BROWSER_URL,
        "openwebui_ready_url": OPENWEBUI_READY_URL,
        "openwebui_ready": openwebui_ready(),
        "host": info,
        "model_options": list(MODEL_OPTIONS),
        "acceleration_options": info["acceleration_options"],
        "current": {
            "source_repo_path": env.get("SOURCE_REPO_PATH", ""),
            "default_model": env.get("DEFAULT_OLLAMA_MODEL", str(info["recommended_model"])),
            "acceleration": env.get("BUILDER_ACCELERATION", str(info["recommended_acceleration"])),
            "open_browser": env.get("BUILDER_OPEN_BROWSER", "1") == "1",
        },
    }


@app.get("/api/openwebui-ready")
def api_openwebui_ready() -> dict[str, object]:
    return {
        "status": "ok",
        "openwebui_url": OPENWEBUI_BROWSER_URL,
        "openwebui_ready_url": OPENWEBUI_READY_URL,
        "ready": openwebui_ready(),
    }


@app.post("/api/save")
def api_save(payload: SaveSetupRequest) -> dict[str, object]:
    env, order = load_env()
    info = load_host_info()
    normalized_source = normalize_web_source_path(payload.source_repo_path)
    if not normalized_source or is_placeholder_source(normalized_source):
        raise HTTPException(status_code=400, detail="SOURCE_REPO_PATH is missing or invalid.")
    allowed_acceleration = [str(item) for item in info["acceleration_options"]]
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
        "openwebui_url": OPENWEBUI_BROWSER_URL,
        "openwebui_ready": openwebui_ready(),
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
    h1, h2 { margin: 0 0 12px; }
    h1 { font-size: 28px; }
    h2 { font-size: 18px; }
    p { color: var(--muted); line-height: 1.5; }
    .grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
    .grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
    label { display: block; font-size: 14px; margin-bottom: 8px; color: var(--text); font-weight: 600; }
    .hint { color: var(--muted); font-size: 13px; margin-top: 6px; }
    input[type="text"], select {
      width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid var(--line);
      background: var(--panel-2); color: var(--text); outline: none;
    }
    input[type="checkbox"] { transform: translateY(1px); margin-right: 8px; }
    .button-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
    button, .button-link {
      border: 0; border-radius: 12px; padding: 12px 16px; background: var(--accent);
      color: white; font-weight: 700; cursor: pointer; text-decoration: none;
      display: inline-flex; align-items: center; justify-content: center;
    }
    button.secondary, .button-link.secondary { background: #233246; color: var(--text); }
    .status-pill {
      display: inline-flex; padding: 6px 10px; border-radius: 999px; font-size: 12px;
      font-weight: 700; background: #1f2a38; color: var(--text);
    }
    .status-ok { background: rgba(63, 185, 80, 0.15); color: #7ee787; }
    .status-warn { background: rgba(210, 153, 34, 0.15); color: #e3b341; }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; }
    .kv { display: grid; grid-template-columns: 220px 1fr; gap: 8px 12px; align-items: start; }
    .kv div:nth-child(odd) { color: var(--text); font-weight: 600; }
    .banner {
      padding: 12px 14px; border-radius: 12px; border: 1px solid var(--line);
      background: #0f1722; color: var(--muted);
    }
    .success { border-color: rgba(63, 185, 80, 0.3); background: rgba(63, 185, 80, 0.08); color: #9ee2a2; }
    .error { border-color: rgba(248, 81, 73, 0.3); background: rgba(248, 81, 73, 0.08); color: #ffb1ac; }
    .warning { border-color: rgba(210, 153, 34, 0.3); background: rgba(210, 153, 34, 0.08); color: #e3b341; }
    .small { font-size: 12px; color: var(--muted); }
    @media (max-width: 760px) { .grid-2, .grid-3, .kv { grid-template-columns: 1fr; } }
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
          <p>4. Danach wartet diese Seite, bis Open WebUI wirklich bereit ist, und wechselt dann im selben Tab weiter.</p>
        </div>
        <div>
          <p>1. Enter the source path.</p>
          <p>2. Choose model and acceleration.</p>
          <p>3. The wizard writes the local <span class="mono">.env</span>.</p>
          <p>4. Afterwards this page waits until Open WebUI is actually ready and then continues in the same tab.</p>
        </div>
      </div>
    </section>

    <section class="card">
      <h2>Host-Erkennung / Host detection</h2>
      <div id="host-note" class="banner" style="display:none; margin-bottom: 12px;"></div>
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
    const openWebUiReadyUrl = "/api/openwebui-ready";
    const hostGrid = document.getElementById("host-grid");
    const hostNote = document.getElementById("host-note");
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
        ["Quelle / Source", info.host_info_source || "-"],
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
      if (info.host_info_warning) {
        hostNote.textContent = info.host_info_warning;
        hostNote.className = "banner warning";
        hostNote.style.display = "block";
      } else {
        hostNote.style.display = "none";
      }
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
      } else if (kind === "warning") {
        message.classList.add("warning");
      }
    }

    async function waitForOpenWebUiReady() {
      for (let attempt = 0; attempt < 180; attempt += 1) {
        try {
          const response = await fetch(openWebUiReadyUrl, { cache: "no-store" });
          if (response.ok) {
            const data = await response.json();
            if (data.ready) {
              setMessage("Open WebUI ist bereit. Weiterleitung... / Open WebUI is ready. Redirecting...", "success");
              window.location.replace(latestOpenWebUiUrl);
              return;
            }
          }
        } catch (_error) {
        }
        setMessage("Setup gespeichert. Runtime startet noch. Warte auf Open WebUI... / Setup saved. Runtime is still starting. Waiting for Open WebUI...", "success");
        await new Promise((resolve) => window.setTimeout(resolve, 1500));
      }
      setMessage(`Setup gespeichert, aber Open WebUI ist noch nicht bereit. Bitte später manuell öffnen: ${latestOpenWebUiUrl}`, "warning");
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
      if (data.configured && data.openwebui_ready) {
        setMessage("Setup bereits gespeichert. Open WebUI ist bereit unter " + latestOpenWebUiUrl, "success");
      } else if (data.configured) {
        setMessage("Setup bereits gespeichert. Open WebUI startet eventuell noch unter " + latestOpenWebUiUrl, "success");
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
      latestOpenWebUiUrl = data.openwebui_url || latestOpenWebUiUrl;
      openWebUiLink.href = latestOpenWebUiUrl;
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
      if (payload.open_browser) {
        await waitForOpenWebUiReady();
      } else {
        setMessage("Setup gespeichert. Open WebUI wird nicht automatisch geöffnet. / Setup saved. Open WebUI will not open automatically.", "success");
      }
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
