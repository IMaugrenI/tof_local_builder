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
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ToF Local Builder</title>
  <style>
    :root {
      --bg: #0d0d0c;
      --bg-soft: #13120f;
      --surface: #181612;
      --surface-2: #211e18;
      --text: #f4f0e8;
      --muted: #aaa49a;
      --gold: #c69a52;
      --gold-bright: #e1b969;
      --gold-soft: rgba(198,154,82,.17);
      --border: rgba(244,240,232,.095);
      --border-strong: rgba(198,154,82,.34);
      --ok: #71c39b;
      --warn: #d8a85f;
      --off: #8e8a83;
      --danger: #cf7b72;
      --shadow: 0 24px 80px rgba(0,0,0,.32);
      --radius: 22px;
    }

    * { box-sizing: border-box; }

    html { color-scheme: dark; }

    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at 82% 6%, rgba(198,154,82,.08), transparent 28rem),
        radial-gradient(circle at 8% 42%, rgba(198,154,82,.03), transparent 34rem),
        linear-gradient(180deg, #0d0d0c 0%, #100f0d 55%, #0d0d0c 100%);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: .13;
      background-image:
        linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.014) 1px, transparent 1px);
      background-size: 72px 72px;
      mask-image: linear-gradient(180deg, #000 0, transparent 80%);
      z-index: -1;
    }

    button, summary { font: inherit; }
    button { appearance: none; }

    .skip-link {
      position: absolute;
      left: 16px;
      top: -64px;
      z-index: 10;
      background: var(--gold);
      color: #17120d;
      padding: 10px 14px;
      border-radius: 10px;
      font-weight: 700;
    }
    .skip-link:focus { top: 16px; }

    .shell {
      width: min(calc(100% - 40px), 1180px);
      margin: 0 auto;
      padding: 26px 0 54px;
    }

    .topbar {
      min-height: 68px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
      margin-bottom: 62px;
    }

    .brand {
      display: inline-flex;
      align-items: center;
      gap: 13px;
      min-width: 0;
    }

    .brand-mark {
      width: 38px;
      height: 38px;
      flex: 0 0 auto;
    }

    .brand-mark svg {
      width: 100%;
      height: 100%;
      display: block;
    }

    .brand-copy {
      display: flex;
      flex-direction: column;
      gap: 2px;
      min-width: 0;
    }

    .brand-name {
      font-size: .83rem;
      letter-spacing: .19em;
      font-weight: 800;
      white-space: nowrap;
    }

    .product-name {
      color: var(--muted);
      font-size: .78rem;
      letter-spacing: .08em;
      text-transform: uppercase;
    }

    .local-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 8px 12px;
      color: var(--muted);
      background: rgba(255,255,255,.018);
      font-size: .79rem;
      white-space: nowrap;
    }

    .local-pill::before {
      content: "";
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--gold);
      box-shadow: 0 0 16px rgba(198,154,82,.42);
    }

    main { display: block; }

    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1.06fr) minmax(340px, .94fr);
      gap: 58px;
      align-items: end;
      padding-bottom: 58px;
      border-bottom: 1px solid var(--border);
    }

    .eyebrow {
      margin: 0 0 16px;
      color: var(--gold);
      font-size: .76rem;
      letter-spacing: .18em;
      font-weight: 800;
    }

    h1, h2, h3, p { margin-top: 0; }

    h1 {
      max-width: 760px;
      margin-bottom: 22px;
      font-size: clamp(2.8rem, 6vw, 5.5rem);
      line-height: .98;
      letter-spacing: -.045em;
    }

    .lead {
      max-width: 690px;
      margin-bottom: 0;
      color: #c6bfb4;
      font-size: clamp(1.05rem, 1.7vw, 1.25rem);
      line-height: 1.7;
    }

    .hero-principles {
      display: grid;
      gap: 0;
      border-top: 1px solid var(--border);
    }

    .principle {
      display: grid;
      grid-template-columns: 38px 1fr;
      gap: 14px;
      padding: 15px 0;
      border-bottom: 1px solid var(--border);
      color: var(--muted);
      font-size: .9rem;
    }

    .principle span {
      color: var(--gold);
      font-size: .76rem;
      letter-spacing: .1em;
    }

    .workspace {
      padding: 54px 0 0;
    }

    .section-head {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 28px;
      margin-bottom: 20px;
    }

    .section-head h2 {
      margin: 0;
      font-size: clamp(1.9rem, 3vw, 2.8rem);
      letter-spacing: -.03em;
    }

    .system-state {
      display: inline-flex;
      align-items: center;
      gap: 9px;
      border: 1px solid var(--border-strong);
      border-radius: 999px;
      padding: 8px 12px;
      color: var(--gold-bright);
      background: rgba(198,154,82,.045);
      font-size: .82rem;
      white-space: nowrap;
    }

    .system-state::before {
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: currentColor;
      box-shadow: 0 0 14px currentColor;
      opacity: .8;
    }

    .system-state.ready { color: var(--ok); border-color: rgba(113,195,155,.32); background: rgba(113,195,155,.05); }
    .system-state.offline { color: var(--off); border-color: var(--border); background: rgba(255,255,255,.018); }
    .system-state.attention { color: var(--warn); border-color: rgba(216,168,95,.34); background: rgba(216,168,95,.05); }

    .focus-panel {
      position: relative;
      overflow: hidden;
      border: 1px solid var(--border-strong);
      border-radius: var(--radius);
      background:
        radial-gradient(circle at 86% 18%, rgba(198,154,82,.12), transparent 22rem),
        linear-gradient(180deg, rgba(255,255,255,.025), rgba(255,255,255,.012));
      box-shadow: var(--shadow);
      padding: 30px;
    }

    .focus-panel::before {
      content: "NEXT";
      position: absolute;
      right: 22px;
      top: 18px;
      color: rgba(225,185,105,.17);
      letter-spacing: .18em;
      font-size: .72rem;
      font-weight: 800;
    }

    .focus-label {
      margin: 0 0 8px;
      color: var(--gold);
      font-size: .75rem;
      letter-spacing: .14em;
      font-weight: 800;
      text-transform: uppercase;
    }

    .focus-panel h3 {
      margin: 0 0 10px;
      max-width: 760px;
      font-size: clamp(1.45rem, 2.5vw, 2.15rem);
      letter-spacing: -.025em;
    }

    .next-step {
      margin: 0;
      max-width: 820px;
      color: var(--muted);
      line-height: 1.65;
    }

    .focus-actions {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 24px;
    }

    .btn {
      min-height: 48px;
      border-radius: 12px;
      padding: 0 18px;
      border: 1px solid transparent;
      cursor: pointer;
      font-weight: 750;
      transition: transform .18s ease, border-color .18s ease, background .18s ease, color .18s ease, opacity .18s ease;
    }

    .btn:hover:not(:disabled) { transform: translateY(-1px); }
    .btn:disabled { cursor: wait; opacity: .55; }

    .btn-primary {
      background: var(--gold);
      color: #16120d;
    }

    .btn-primary:hover:not(:disabled),
    .btn-primary:focus-visible {
      background: var(--gold-bright);
    }

    .btn-secondary {
      color: var(--text);
      border-color: var(--border-strong);
      background: rgba(255,255,255,.015);
    }

    .btn-secondary:hover:not(:disabled),
    .btn-secondary:focus-visible {
      border-color: var(--gold);
      color: var(--gold-bright);
      background: rgba(198,154,82,.05);
    }

    .btn-quiet {
      color: var(--muted);
      border-color: var(--border);
      background: rgba(255,255,255,.012);
    }

    .btn-quiet:hover:not(:disabled),
    .btn-quiet:focus-visible {
      color: var(--text);
      border-color: var(--border-strong);
    }

    .btn-danger {
      color: #e4aaa4;
      border-color: rgba(207,123,114,.28);
      background: rgba(207,123,114,.035);
    }

    .btn-danger:hover:not(:disabled),
    .btn-danger:focus-visible {
      border-color: rgba(207,123,114,.55);
      background: rgba(207,123,114,.065);
    }

    button:focus-visible,
    summary:focus-visible {
      outline: 2px solid var(--gold-bright);
      outline-offset: 3px;
    }

    .readiness {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
      margin-top: 18px;
    }

    .service-card {
      min-width: 0;
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 18px;
      background: rgba(255,255,255,.014);
    }

    .service-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .service-name {
      font-size: .93rem;
      font-weight: 720;
    }

    .service-state {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      color: var(--muted);
      font-size: .78rem;
    }

    .service-state::before {
      content: "";
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--off);
    }

    .service-card.ready .service-state { color: var(--ok); }
    .service-card.ready .service-state::before { background: var(--ok); box-shadow: 0 0 12px rgba(113,195,155,.35); }
    .service-card.attention .service-state { color: var(--warn); }
    .service-card.attention .service-state::before { background: var(--warn); }
    .service-card.offline .service-state { color: var(--off); }

    .service-hint {
      margin: 10px 0 0;
      color: var(--muted);
      font-size: .82rem;
      overflow-wrap: anywhere;
    }

    .workflow {
      margin-top: 44px;
    }

    .workflow-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
      margin-top: 18px;
    }

    .step {
      border-top: 1px solid var(--border-strong);
      padding: 22px 0 4px;
    }

    .step-number {
      display: block;
      margin-bottom: 13px;
      color: var(--gold);
      font-size: .76rem;
      letter-spacing: .14em;
      font-weight: 800;
    }

    .step h3 {
      margin-bottom: 8px;
      font-size: 1.05rem;
    }

    .step p {
      min-height: 48px;
      margin-bottom: 18px;
      color: var(--muted);
      font-size: .9rem;
    }

    .details-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-top: 42px;
    }

    details {
      border: 1px solid var(--border);
      border-radius: 16px;
      background: rgba(255,255,255,.012);
      overflow: hidden;
    }

    summary {
      list-style: none;
      cursor: pointer;
      padding: 17px 18px;
      color: var(--text);
      font-weight: 720;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
    }

    summary::-webkit-details-marker { display: none; }
    summary::after {
      content: "+";
      color: var(--gold);
      font-size: 1.25rem;
      font-weight: 400;
    }
    details[open] summary::after { content: "−"; }

    .details-body {
      border-top: 1px solid var(--border);
      padding: 18px;
    }

    .advanced-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .log {
      margin-top: 12px;
      border-radius: 12px;
      padding: 15px;
      min-height: 150px;
      max-height: 340px;
      overflow: auto;
      background: #090a09;
      border: 1px solid rgba(255,255,255,.06);
      color: #c6d7c8;
      font: 12px/1.6 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    }

    pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .footer {
      display: flex;
      justify-content: space-between;
      gap: 20px;
      margin-top: 46px;
      padding-top: 18px;
      border-top: 1px solid var(--border);
      color: var(--muted);
      font-size: .79rem;
    }

    @media (max-width: 860px) {
      .topbar { margin-bottom: 42px; }
      .hero { grid-template-columns: 1fr; gap: 34px; }
      .readiness, .workflow-grid { grid-template-columns: 1fr; }
      .step p { min-height: 0; }
      .details-grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 560px) {
      .shell { width: min(calc(100% - 26px), 1180px); padding-top: 16px; }
      .topbar { align-items: flex-start; gap: 12px; }
      .product-name { white-space: normal; }
      .local-pill { display: none; }
      h1 { font-size: clamp(2.45rem, 13vw, 3.55rem); }
      .focus-panel { padding: 22px; }
      .section-head { align-items: flex-start; flex-direction: column; }
      .focus-actions, .advanced-actions { flex-direction: column; }
      .btn { width: 100%; }
      .footer { flex-direction: column; }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        scroll-behavior: auto !important;
        transition-duration: .001ms !important;
        animation-duration: .001ms !important;
        animation-iteration-count: 1 !important;
      }
    }
  </style>
</head>
<body>
  <a class="skip-link" href="#main">Skip to workspace</a>

  <div class="shell">
    <header class="topbar">
      <div class="brand" aria-label="ToF Systems Local Builder">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 64 64" fill="none">
            <g stroke="#e1b969" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round">
              <path d="M32 5.5C25.8 13.3 25.5 22.7 32 30.8C38.5 22.7 38.2 13.3 32 5.5Z"/>
              <path d="M31.6 30.1C23.1 20.8 12.4 22.4 5.8 31.8C13.4 40.5 23.7 41.2 31.8 32.5"/>
              <path d="M32.4 30.1C40.9 20.8 51.6 22.4 58.2 31.8C50.6 40.5 40.3 41.2 32.2 32.5"/>
              <path d="M32 33.2C25.7 41.4 26 50.8 32 58.5C38 50.8 38.3 41.4 32 33.2Z"/>
              <path d="M32 24.8L39.2 32L32 39.2L24.8 32L32 24.8Z"/>
              <path d="M19.7 29.1L15.2 33.2L23.2 39.1"/>
              <path d="M44.3 29.1L48.8 33.2L40.8 39.1"/>
            </g>
          </svg>
        </span>
        <span class="brand-copy">
          <span class="brand-name">TOF SYSTEMS</span>
          <span class="product-name">Local Builder</span>
        </span>
      </div>
      <span class="local-pill">Local only · 127.0.0.1</span>
    </header>

    <main id="main">
      <section class="hero">
        <div>
          <p class="eyebrow">CONTROLLED LOCAL AI WORKSPACE</p>
          <h1>Build locally. Keep control.</h1>
          <p class="lead">Work with local AI against a source you choose, while the normal builder path keeps that source read-only and writes generated work into a separate sandbox.</p>
        </div>

        <div class="hero-principles" aria-label="Builder principles">
          <div class="principle"><span>01</span><div>Source stays read-only in the normal workflow.</div></div>
          <div class="principle"><span>02</span><div>Generated work stays inside the builder sandbox.</div></div>
          <div class="principle"><span>03</span><div>You decide what leaves the local environment.</div></div>
        </div>
      </section>

      <section class="workspace" aria-labelledby="workspace-title">
        <div class="section-head">
          <div>
            <p class="eyebrow">WORKSPACE</p>
            <h2 id="workspace-title">Your next useful action.</h2>
          </div>
          <span class="system-state offline" id="system-state">Checking system</span>
        </div>

        <div class="focus-panel">
          <p class="focus-label">Recommended next step</p>
          <h3 id="focus-title">Checking local services…</h3>
          <p class="next-step" id="next-step" aria-live="polite">Loading current guidance…</p>
          <div class="focus-actions">
            <button class="btn btn-primary" id="primary-action" type="button" onclick="runPrimaryAction()">Start builder</button>
            <button class="btn btn-secondary" type="button" onclick="refreshSummary()">Refresh status</button>
          </div>
        </div>

        <div class="readiness" id="cards" aria-label="Local service readiness"></div>
      </section>

      <section class="workflow" aria-labelledby="workflow-title">
        <div class="section-head">
          <div>
            <p class="eyebrow">GUIDED FLOW</p>
            <h2 id="workflow-title">Three steps, then work.</h2>
          </div>
        </div>

        <div class="workflow-grid">
          <article class="step">
            <span class="step-number">01 · SETUP</span>
            <h3>Choose the local source.</h3>
            <p>Prepare paths, model settings and the guarded source/sandbox boundary.</p>
            <button class="btn btn-secondary" type="button" onclick="runAction('setup', this)">Prepare setup</button>
          </article>

          <article class="step">
            <span class="step-number">02 · START</span>
            <h3>Bring the workspace online.</h3>
            <p>Start the local builder stack and ensure the configured local model is available.</p>
            <button class="btn btn-secondary" type="button" onclick="runAction('up', this)">Start system</button>
          </article>

          <article class="step">
            <span class="step-number">03 · VERIFY</span>
            <h3>Confirm readiness.</h3>
            <p>Check the services before moving into the actual builder workspace.</p>
            <button class="btn btn-secondary" type="button" onclick="runAction('check', this)">Check services</button>
          </article>
        </div>
      </section>

      <section class="details-grid" aria-label="Advanced controls">
        <details>
          <summary>Diagnostics & system controls</summary>
          <div class="details-body">
            <div class="advanced-actions">
              <button class="btn btn-quiet" type="button" onclick="runAction('status', this)">Runtime status</button>
              <button class="btn btn-quiet" type="button" onclick="runAction('doctor', this)">Run doctor</button>
              <button class="btn btn-danger" type="button" onclick="runAction('down', this)">Stop stack</button>
            </div>
          </div>
        </details>

        <details>
          <summary>Advanced local endpoints</summary>
          <div class="details-body">
            <div class="advanced-actions">
              <button class="btn btn-quiet" type="button" onclick="openLink('repo_bridge_health', this)">Repo bridge health</button>
              <button class="btn btn-quiet" type="button" onclick="openLink('ollama', this)">Ollama endpoint</button>
            </div>
          </div>
        </details>
      </section>

      <details style="margin-top:16px;">
        <summary>Activity log</summary>
        <div class="details-body">
          <div class="log" aria-live="polite"><pre id="log">Local Builder control surface ready.</pre></div>
        </div>
      </details>
    </main>

    <footer class="footer">
      <span>ToF Systems · Local Builder</span>
      <span>Local-first · bounded source · sandboxed output</span>
    </footer>
  </div>

  <script>
    let currentSummary = null;

    function appendLog(text) {
      const log = document.getElementById('log');
      log.textContent = `[${new Date().toLocaleTimeString()}] ${text}\n\n` + log.textContent;
    }

    function friendlyState(state) {
      if (state === 'ready') return 'Ready';
      if (state === 'not_reachable') return 'Offline';
      if (String(state).startsWith('http_')) return 'Attention';
      return String(state).replaceAll('_', ' ');
    }

    function stateClass(state) {
      if (state === 'ready') return 'ready';
      if (state === 'not_reachable') return 'offline';
      return 'attention';
    }

    function renderCards(data) {
      const root = document.getElementById('cards');
      root.innerHTML = '';
      for (const item of data.items || []) {
        const card = document.createElement('article');
        card.className = `service-card ${stateClass(item.state)}`;

        const top = document.createElement('div');
        top.className = 'service-top';

        const name = document.createElement('span');
        name.className = 'service-name';
        name.textContent = item.label;

        const state = document.createElement('span');
        state.className = 'service-state';
        state.textContent = friendlyState(item.state);

        const hint = document.createElement('p');
        hint.className = 'service-hint';
        hint.textContent = item.state === 'ready'
          ? 'Available on this machine.'
          : 'Not currently reachable on this machine.';

        top.append(name, state);
        card.append(top, hint);
        root.appendChild(card);
      }
    }

    function applySummary(data) {
      currentSummary = data;
      const items = (data.readiness || {}).items || [];
      const webui = items.find(item => item.name === 'webui');
      const bridge = items.find(item => item.name === 'repo_bridge');
      const ollama = items.find(item => item.name === 'ollama');
      const allReady = items.length > 0 && items.every(item => item.state === 'ready');
      const someReady = items.some(item => item.state === 'ready');

      const state = document.getElementById('system-state');
      const focusTitle = document.getElementById('focus-title');
      const primary = document.getElementById('primary-action');

      state.className = 'system-state ' + (allReady ? 'ready' : (someReady ? 'attention' : 'offline'));
      state.textContent = allReady ? 'System ready' : (someReady ? 'Partially ready' : 'Not running');

      document.getElementById('next-step').textContent = data.next_step;
      renderCards(data.readiness || { items: [] });

      if (webui && webui.state === 'ready') {
        focusTitle.textContent = 'The builder workspace is ready.';
        primary.textContent = 'Open builder workspace';
        primary.dataset.mode = 'open';
      } else {
        focusTitle.textContent = 'Bring the local builder online.';
        primary.textContent = 'Start builder system';
        primary.dataset.mode = 'start';
      }

      if (bridge && bridge.state !== 'ready' && ollama && ollama.state === 'ready') {
        focusTitle.textContent = 'The model layer is up; the builder bridge still needs attention.';
      }
    }

    async function refreshSummary() {
      try {
        const response = await fetch('/api/summary');
        const data = await response.json();
        applySummary(data);
      } catch (error) {
        const state = document.getElementById('system-state');
        state.className = 'system-state attention';
        state.textContent = 'Status unavailable';
        document.getElementById('focus-title').textContent = 'The control surface could not read local readiness.';
        document.getElementById('next-step').textContent = 'Try refresh again. If the problem persists, open Diagnostics & system controls and run Doctor.';
        appendLog('Summary refresh failed: ' + error);
      }
    }

    async function withBusy(button, label, fn) {
      const original = button ? button.textContent : '';
      if (button) {
        button.disabled = true;
        button.textContent = label;
      }
      try {
        return await fn();
      } finally {
        if (button) {
          button.disabled = false;
          button.textContent = original;
        }
      }
    }

    async function runPrimaryAction() {
      const button = document.getElementById('primary-action');
      if (button.dataset.mode === 'open') {
        await openLink('openwebui', button);
      } else {
        await runAction('up', button);
      }
    }

    async function runAction(action, button = null) {
      await withBusy(button, 'Working…', async () => {
        appendLog(`Running ${action}…`);
        try {
          const response = await fetch(`/api/${action}`, { method: 'POST' });
          const data = await response.json();
          const summary = data.output ? data.output : JSON.stringify(data, null, 2);
          appendLog(`${data.label || action}: ${summary || 'completed'}`);
        } catch (error) {
          appendLog(`Action ${action} failed: ${error}`);
        }
        await refreshSummary();
      });
    }

    async function openLink(name, button = null) {
      await withBusy(button, 'Opening…', async () => {
        appendLog(`Opening ${name}…`);
        try {
          const response = await fetch(`/api/open/${name}`, { method: 'POST' });
          const data = await response.json();
          appendLog(data.opened ? `Opened ${data.opened}` : JSON.stringify(data, null, 2));
        } catch (error) {
          appendLog(`Could not open ${name}: ${error}`);
        }
      });
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
