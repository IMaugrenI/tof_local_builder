from __future__ import annotations

import io
import json
import threading
import urllib.error
import urllib.request
import webbrowser
from contextlib import redirect_stdout
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable
from urllib.parse import parse_qs, urlparse

from tof_cli.commands import check, doctor, down, setup, status, up
from tof_cli.builder.artifact_ops import artifact_diff, artifact_handoff, artifact_inventory, artifact_preview
from tof_cli.builder.model_ops import ollama_tags
from tof_cli.builder.ollama_chat import ModelChatError
from tof_cli.builder.agent_ops import AgentManager, BuildError
from tof_cli.builder.agent_bridge import AgentBridge, BridgeError
from tof_cli.builder.project_intelligence import project_context
from tof_cli.builder.knowledge_ops import KnowledgeError, search_knowledge
from tof_cli.builder.conversation_store import ConversationError, ConversationStore
from tof_cli.builder.job_journal import JournalError
from tof_cli.builder.task_runner import run_task_once
from tof_cli.builder.task_ops import task_guide
from tof_cli.ui.guidance import explain_readiness
from tof_cli.builder.repo_bridge_ops import sandbox_report, source_repo_report
from tof_cli.core.env_ops import read_env


@dataclass(frozen=True)
class ActionSpec:
    label: str
    handler: Callable[..., int]
    kwargs: dict[str, object]
    safe_level: str


ACTIONS = {
    "setup": ActionSpec("Choose and prepare my project", setup.handle, {}, "SAFE"),
    "up": ActionSpec("Start my workspace", up.handle, {"skip_wizard": False, "skip_model_ensure": False}, "SAFE"),
    "check": ActionSpec("Check if everything is ready", check.handle, {}, "SAFE"),
    "status": ActionSpec("Show technical status", status.handle, {}, "SAFE"),
    "doctor": ActionSpec("Find problems", doctor.handle, {}, "SAFE"),
    "down": ActionSpec("Stop my workspace", down.handle, {"remove_orphans": False}, "SAFE"),
}

LINKS = {
    "repo_bridge_health": {"label": "Project connection details", "url": "http://127.0.0.1:8099/health"},
    "ollama": {"label": "AI model details", "url": "http://127.0.0.1:11434"},
}

READINESS_TARGETS = {
    "repo_bridge": {"label": "Project access", "url": "http://127.0.0.1:8099/health"},
    "ollama": {"label": "AI model", "url": "http://127.0.0.1:11434"},
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

    .action-feedback {
      display: none;
      margin-top: 16px;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,.015);
      color: var(--muted);
    }

    .action-feedback.show { display: block; }
    .action-feedback.ok {
      color: var(--ok);
      border-color: rgba(113,195,155,.28);
      background: rgba(113,195,155,.045);
    }
    .action-feedback.attention {
      color: #e5bf82;
      border-color: rgba(216,168,95,.30);
      background: rgba(216,168,95,.05);
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
          <span class="product-name">Local Workspace</span>
        </span>
      </div>
      <span class="local-pill">Stays on this computer</span>
    </header>

    <main id="main">
      <section class="hero">
        <div>
          <p class="eyebrow">LOCAL AI WORKSPACE</p>
          <h1>Work with your project. Keep control.</h1>
          <p class="lead">Choose a project on your computer and work with local AI without changing the original files. New work is kept separately until you decide what to keep.</p>
        </div>

        <div class="hero-principles" aria-label="Builder principles">
          <div class="principle"><span>01</span><div>Your original project stays untouched.</div></div>
          <div class="principle"><span>02</span><div>New files are kept in a separate work area.</div></div>
          <div class="principle"><span>03</span><div>You decide what is kept, moved or shared.</div></div>
        </div>
      </section>

      <section class="workspace" aria-labelledby="workspace-title">
        <div class="section-head">
          <div>
            <p class="eyebrow">YOUR WORKSPACE</p>
            <h2 id="workspace-title">What should you do next?</h2>
          </div>
          <span class="system-state offline" id="system-state">Checking what is ready</span>
        </div>

        <div class="focus-panel">
          <p class="focus-label">Next step</p>
          <h3 id="focus-title">Checking your workspace…</h3>
          <p class="next-step" id="next-step" aria-live="polite">Finding the best next step…</p>
          <div class="service-card" id="guidance-panel" aria-live="polite">Checking recommended next steps…</div>
          <div class="focus-actions">
            <button class="btn btn-primary" id="primary-action" type="button" onclick="runPrimaryAction()">Start workspace</button>
            <button class="btn btn-secondary" type="button" onclick="refreshSummary()">Check again</button>
          </div>
          <div class="action-feedback" id="action-feedback" role="status" aria-live="polite"></div>
        </div>

        <div class="readiness" id="cards" aria-label="Workspace readiness"></div>
      </section>

      <section class="workflow" aria-labelledby="workflow-title">
        <div class="section-head">
          <div>
            <p class="eyebrow">GET STARTED</p>
            <h2 id="workflow-title">Three simple steps, then you can work.</h2>
          </div>
        </div>

        <div class="workflow-grid">
          <article class="step">
            <span class="step-number">01 · CHOOSE</span>
            <h3>Choose your project.</h3>
            <p>Tell ToF which project you want to work with. Your original project stays protected.</p>
            <button class="btn btn-secondary" type="button" onclick="runAction('setup', this)">Choose project</button>
          </article>

          <article class="step">
            <span class="step-number">02 · START</span>
            <h3>Start your workspace.</h3>
            <p>ToF starts the local tools it needs and prepares your AI model.</p>
            <button class="btn btn-secondary" type="button" onclick="runAction('up', this)">Start workspace</button>
          </article>

          <article class="step">
            <span class="step-number">03 · CHECK</span>
            <h3>Make sure everything is ready.</h3>
            <p>ToF checks the important parts so you know whether you can begin.</p>
            <button class="btn btn-secondary" type="button" onclick="runAction('check', this)">Check readiness</button>
          </article>
        </div>
      </section>

      <section class="workflow" id="builder-chat" aria-labelledby="task-title">
        <div class="section-head">
          <div>
            <p class="eyebrow">BUILDER ASSISTANT</p>
            <h2 id="task-title">Work with your local AI.</h2>
            <p class="service-hint">Describe a task and receive a direct Ollama reply here. No external chat service is needed. The original project remains read-only.</p>
          </div>
        </div>
        <div class="service-card" id="project-context" aria-live="polite">
          Select a source project to view its read-only overview.
        </div>
        <div class="service-card" style="margin-top:14px;">
          <strong>Read-only architecture inspection</strong>
          <p class="service-hint">Examine relevant modules and source matches before a build. This does not run a model or modify files.</p>
          <button class="btn btn-quiet" type="button" id="architecture-inspect" onclick="inspectArchitecture()">Inspect project for this task</button>
          <p class="service-hint" id="architecture-status" role="status" aria-live="polite">Enter a task to focus the inspection.</p>
          <pre class="log" id="architecture-context" style="white-space:pre-wrap;max-height:28rem;overflow:auto;" hidden></pre>
        </div>
        <div class="service-card" style="margin-top:14px;">
          <strong>Optional local Knowledge search</strong>
          <p class="service-hint">Only when you click Search and confirm: look up indexed, unverified excerpts from the separately running ToF Local Knowledge service. Results are not shared with your model or development job.</p>
          <label for="knowledge-query">Document search phrase</label>
          <input id="knowledge-query" type="text" maxlength="500" style="width:100%;padding:10px;margin:8px 0 12px" placeholder="Search my indexed local documents (optional)">
          <button class="btn btn-quiet" id="knowledge-search" type="button" onclick="searchLocalKnowledge()">Search Knowledge</button>
          <p class="service-hint" id="knowledge-status" role="status" aria-live="polite">Knowledge is optional and stays separate. No document access occurs automatically.</p>
          <div id="knowledge-results"></div>
        </div>
        <div class="service-card" style="margin-top:18px;">
          <label for="task-type">Task type</label>
          <select id="task-type" style="width:100%;padding:10px;margin:8px 0 14px" onchange="refreshTaskModels()"></select>
          <label for="task-model">Local model</label>
          <select id="task-model" style="width:100%;padding:10px;margin:8px 0 14px"></select>
          <p class="service-hint" id="task-hint">Checking installed models…</p>
          <label for="task-goal">Your task</label>
          <textarea id="task-goal" maxlength="2000" rows="5" style="width:100%;padding:12px;margin:8px 0 14px" placeholder="Describe what you want to build, inspect or discuss."></textarea>
          <button class="btn btn-primary" id="task-send" type="button" onclick="sendTask()">Ask Builder</button>
          <button class="btn btn-quiet" type="button" onclick="clearTaskChat()">New conversation</button>
          <button class="btn btn-quiet" type="button" onclick="saveLocalConversation()">Save locally</button>
          <button class="btn btn-quiet" type="button" onclick="restoreLocalConversation()">Restore saved</button>
          <button class="btn btn-quiet" type="button" onclick="deleteLocalConversation()">Delete saved</button>
          <p class="service-hint" id="conversation-storage-status" role="status" aria-live="polite">Conversation saving is optional and only happens when you click Save locally. It stays in your project sandbox.</p>
          <p class="service-hint" id="task-message" role="status" aria-live="polite">Conversations stay in this browser tab. No model-generated file operations run automatically.</p>
          <div id="task-conversation" class="service-card" style="margin-top:18px;" aria-live="polite">
            <strong>Conversation</strong>
            <div id="task-thread" style="margin-top:12px;">Describe a task to begin.</div>
          </div>
          <div class="service-card" style="margin-top:18px;">
            <strong>Build draft files in the sandbox</strong>
            <p class="service-hint">One click starts a bounded architecture scan, plan and up to six draft files in sandbox/output. After a restart, interrupted jobs can be continued only when the saved files and source still match. No draft is overwritten and the original project stays read-only.</p>
            <button class="btn btn-secondary" type="button" id="build-start" onclick="startSandboxBuild()">Generate sandbox draft</button>
            <button class="btn btn-quiet" type="button" id="build-cancel" onclick="cancelSandboxBuild()" disabled>Cancel build</button>
            <button class="btn btn-secondary" type="button" id="build-resume" onclick="resumeSandboxBuild()" disabled>Continue safely</button>
            <p id="build-status" class="service-hint" role="status" aria-live="polite">No build is running.</p>
            <div id="build-details" class="service-hint"></div>
            <strong style="display:block;margin-top:18px;">Recent local builds</strong>
            <div id="build-history" class="service-hint">No build history loaded yet.</div>
          </div>
        </div>
      </section>

      <section class="workflow" aria-labelledby="artifact-title">
        <div class="section-head">
          <div>
            <p class="eyebrow">REVIEW YOUR WORK</p>
            <h2 id="artifact-title">Generated files — review before keeping.</h2>
            <p class="service-hint">Only sandbox/workspace and sandbox/output are listed. Your original project stays read-only. No files are copied back automatically.</p>
          </div>
          <button class="btn btn-secondary" type="button" onclick="refreshArtifacts()">Refresh files</button>
        </div>
        <p class="service-hint" id="review-progress">Review generated text before adopting changes.</p>
        <label class="service-hint"><input id="review-pending-only" type="checkbox" onchange="refreshArtifacts()"> Only files needing review</label>
        <p class="service-hint">Marks stay in this browser; no files are applied or committed automatically.</p>
        <div class="service-card" id="artifact-list" aria-live="polite">Select “Refresh files” to inspect the generated sandbox files.</div>
        <details style="margin-top:16px;">
          <summary>Read-only text preview</summary>
          <div class="details-body"><pre class="log" id="artifact-preview">Choose a small text file using its Preview button.</pre></div>
        </details>
      </section>

      <section class="details-grid" aria-label="Advanced controls">
        <details>
          <summary>Problems & technical details</summary>
          <div class="details-body">
            <div class="advanced-actions">
              <button class="btn btn-quiet" type="button" onclick="runAction('status', this)">Show technical status</button>
              <button class="btn btn-quiet" type="button" onclick="runAction('doctor', this)">Find a problem</button>
              <button class="btn btn-danger" type="button" onclick="runAction('down', this)">Stop workspace</button>
            </div>
          </div>
        </details>

        <details>
          <summary>Connection details</summary>
          <div class="details-body">
            <div class="advanced-actions">
              <button class="btn btn-quiet" type="button" onclick="openLink('repo_bridge_health', this)">Project connection</button>
              <button class="btn btn-quiet" type="button" onclick="openLink('ollama', this)">AI model</button>
            </div>
          </div>
        </details>
      </section>

      <details style="margin-top:16px;">
        <summary>Technical activity log</summary>
        <div class="details-body">
          <div class="log" aria-live="polite"><pre id="log">Your local workspace controls are ready.</pre></div>
        </div>
      </details>
    </main>

    <footer class="footer">
      <span>ToF Systems · Local Workspace</span>
      <span>Your project stays local · original files stay protected</span>
    </footer>
  </div>

  <script>
    let currentSummary = null;
    let conversation = [];
    let conversationScope = '';
    let currentBuildId = '';
    let pollBuildTimer = null;

    function clearTaskChat() {
      conversation = [];
      const thread = document.getElementById('task-thread');
      thread.textContent = 'Conversation cleared. Start a new task.';
      document.getElementById('task-message').textContent = 'Ready for a new conversation.';
    }

    function appendChat(role, content) {
      const thread = document.getElementById('task-thread');
      if (!thread.querySelector('article')) thread.replaceChildren();
      const entry = document.createElement('article');
      entry.className = 'service-card';
      entry.style.marginTop = '10px';
      const title = document.createElement('strong');
      title.textContent = role === 'user' ? 'You' : 'Builder';
      const message = document.createElement('pre');
      message.className = 'log';
      message.style.minHeight = '0';
      message.style.maxHeight = 'none';
      message.style.marginTop = '8px';
      message.textContent = content;
      entry.append(title, message);
      thread.appendChild(entry);
      while (thread.childElementCount > 12) thread.removeChild(thread.firstElementChild);
    }
    const REVIEW_STORAGE_KEY = 'tof_builder_reviewed_v1';
    let reviewedTokens = new Set();
    const inspectedTokens = new Set();
    let visibleArtifacts = [];
    try {
      const saved = JSON.parse(localStorage.getItem(REVIEW_STORAGE_KEY) || '[]');
      if (Array.isArray(saved)) reviewedTokens = new Set(
        saved.filter(item => typeof item === 'string' && /^[a-f0-9]{64}$/.test(item)).slice(-5000)
      );
    } catch (error) { reviewedTokens = new Set(); }

    function saveReviews() {
      try {
        localStorage.setItem(REVIEW_STORAGE_KEY, JSON.stringify([...reviewedTokens].slice(-5000)));
      } catch (error) {
        document.getElementById('review-progress').textContent =
          'Browser storage is unavailable. Review marks last only for this page.';
      }
    }

    function reviewToken(area, path) {
      const item = visibleArtifacts.find(entry => entry.area === area && entry.path === path);
      return item ? item.review_token : null;
    }

    function changeReview(token, reviewed) {
      if (!token || (reviewed && !inspectedTokens.has(token))) return;
      if (reviewed) reviewedTokens.add(token);
      else reviewedTokens.delete(token);
      saveReviews();
      refreshArtifacts();
    }

    function appendLog(text) {
      const log = document.getElementById('log');
      log.textContent = `[${new Date().toLocaleTimeString()}] ${text}\n\n` + log.textContent;
    }

    function showFeedback(message, kind = 'ok') {
      const box = document.getElementById('action-feedback');
      box.className = `action-feedback show ${kind}`;
      box.textContent = message;
    }

    function friendlyState(state) {
      if (state === 'ready') return 'Ready';
      if (state === 'not_reachable') return 'Not available';
      if (String(state).startsWith('http_')) return 'Needs attention';
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
        hint.textContent = item.detail || (item.state === 'ready'
          ? 'Ready on this computer.'
          : 'Not ready yet.');

        top.append(name, state);
        card.append(top, hint);
        root.appendChild(card);
      }
    }

    function renderGuidance(guidance) {
      const panel = document.getElementById('guidance-panel');
      panel.replaceChildren();
      const heading = document.createElement('strong');
      heading.textContent = guidance.status === 'ready'
        ? 'Workspace checklist complete' : 'Next steps to get ready';
      panel.appendChild(heading);
      const checks = guidance.checks || [];
      if (!checks.length) {
        const note = document.createElement('p');
        note.className = 'service-hint';
        note.textContent = guidance.status === 'ready'
          ? 'Source, sandbox, model and services are ready.'
          : 'Status is incomplete. Choose Find problems to inspect it.';
        panel.appendChild(note);
        return;
      }
      checks.slice(0, 6).forEach((item, index) => {
        const row = document.createElement('p');
        row.className = 'service-hint';
        row.textContent = (index + 1) + '. ' + item.label + ': ' + item.next_step;
        panel.appendChild(row);
      });
      const suggested = guidance.priority?.suggested_action;
      if (['setup', 'up', 'check', 'doctor', 'status'].includes(suggested)) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-secondary';
        button.textContent = 'Next: ' + ({
          setup: 'Configure paths or model', up: 'Start workspace',
          check: 'Check status', doctor: 'Find problems',
          status: 'Show status',
        }[suggested]);
        button.addEventListener('click', () => runAction(suggested, button));
        panel.appendChild(button);
      }
    }

    function renderProjectContext(project) {
      const box = document.getElementById('project-context');
      box.replaceChildren();
      const label = document.createElement('strong');
      label.textContent = project.source_name
        ? 'Project: ' + project.source_name
        : 'No readable source project selected';
      const state = document.createElement('p');
      state.className = 'service-hint';
      state.textContent = 'Original project (read-only): ' + (project.source_state || 'unavailable')
        + ' · Sandbox: ' + (project.sandbox_state || 'unavailable');
      const paths = document.createElement('p');
      paths.className = 'service-hint';
      paths.textContent = 'Source: ' + (project.source_path || 'not set')
        + ' · Sandbox: ' + (project.sandbox_path || 'not set');
      box.append(label, state, paths);
      if ((project.top_level || []).length) {
        const files = document.createElement('p');
        files.className = 'service-hint';
        files.textContent = 'Top level (read-only): '
          + project.top_level.map(entry => entry.name + (entry.kind === 'directory' ? '/' : '')).join(', ')
          + (project.truncated ? ' · more items not shown' : '');
        box.appendChild(files);
      }
    }

    function renderTaskGuide(guide) {
      const select = document.getElementById('task-type');
      const previous = select.value || 'code';
      select.replaceChildren();
      (guide.tasks || []).forEach(task => {
        const option = document.createElement('option');
        option.value = task.key;
        option.textContent = task.label;
        select.appendChild(option);
      });
      if ((guide.tasks || []).some(task => task.key === previous)) select.value = previous;
      refreshTaskModels();
    }

    function refreshTaskModels() {
      const guide = (currentSummary || {}).task_guide || {};
      const task = document.getElementById('task-type').value;
      const models = document.getElementById('task-model');
      const previous = models.value;
      models.replaceChildren();
      const installed = new Set(guide.installed_models || []);
      const recommended = new Set((guide.recommendations || {})[task]?.map(item => item.tag) || []);
      const preferred = (guide.preferred_models || {})[task] || [];
      (guide.installed_models || []).forEach(tag => {
        const option = document.createElement('option');
        option.value = tag;
        option.textContent = tag + (recommended.has(tag) ? ' · task suggested' : '');
        models.appendChild(option);
      });
      if (installed.has(previous) && (recommended.has(previous) || !preferred.length)) {
        models.value = previous;
      } else if (preferred.length && installed.has(preferred[0])) {
        models.value = preferred[0];
      } else if (installed.has(previous)) {
        models.value = previous;
      } else if (installed.has(guide.configured_default)) {
        models.value = guide.configured_default;
      }
      const hint = document.getElementById('task-hint');
      hint.textContent = guide.model_service_reachable
        ? installed.size + ' installed model(s). '
          + (preferred.length
            ? 'Suggested for this task: ' + preferred[0] + '. '
            : 'No matching model profile installed; any installed model may be selected. ')
          + 'The selected model will be used directly here.'
        : 'Ollama unavailable. Start the workspace and check again.';
    }

    async function saveLocalConversation() {
      const status = document.getElementById('conversation-storage-status');
      if (!conversation.length) {
        status.textContent = 'No conversation to save yet.';
        return;
      }
      try {
        const response = await fetch('/api/conversation/save', {
          method: 'POST',
          headers: {'Content-Type': 'application/json', 'X-Builder-Request': '1'},
          body: JSON.stringify({messages: conversation}),
        });
        const data = await response.json();
        status.textContent = response.ok
          ? 'Conversation saved locally for this project. No cloud sync was started.'
          : (data.error || 'Could not save the conversation.');
      } catch (error) {
        status.textContent = 'Could not save the conversation locally.';
      }
    }

    async function restoreLocalConversation() {
      const status = document.getElementById('conversation-storage-status');
      try {
        const response = await fetch('/api/conversation');
        const data = await response.json();
        if (!response.ok) {
          status.textContent = data.error || 'Saved conversation is unavailable.';
          return;
        }
        if (!data.saved || !Array.isArray(data.messages) || !data.messages.length) {
          status.textContent = 'No saved conversation for this project.';
          return;
        }
        clearTaskChat();
        conversation = data.messages;
        conversation.forEach(message => appendChat(message.role, message.content));
        status.textContent = 'Saved conversation restored for this project. No model call was made.';
      } catch (error) {
        status.textContent = 'Could not restore the saved local conversation.';
      }
    }

    async function deleteLocalConversation() {
      const status = document.getElementById('conversation-storage-status');
      if (!confirm('Delete the saved local conversation for this project? This does not delete the current browser conversation.')) return;
      try {
        const response = await fetch('/api/conversation/delete', {
          method: 'POST',
          headers: {'Content-Type': 'application/json', 'X-Builder-Request': '1'},
          body: JSON.stringify({}),
        });
        const data = await response.json();
        status.textContent = response.ok
          ? 'Saved conversation deleted from the local project sandbox.'
          : (data.error || 'Could not delete the saved conversation.');
      } catch (error) {
        status.textContent = 'Could not delete the local snapshot.';
      }
    }

    async function sendTask() {
      const guide = (currentSummary || {}).task_guide || {};
      const goal = document.getElementById('task-goal').value.trim();
      const task = document.getElementById('task-type').value;
      const model = document.getElementById('task-model').value;
      const message = document.getElementById('task-message');
      const button = document.getElementById('task-send');
      if (!goal || goal.length > 2000 || !(guide.installed_models || []).includes(model)) {
        message.textContent = 'Enter a task and select an installed local model.';
        return;
      }
      await withBusy(button, 'Builder is thinking…', async () => {
        message.textContent = 'Asking your local model. This can take a moment on CPU systems.';
        try {
          const response = await fetch('/api/task', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-Builder-Request': '1'},
            body: JSON.stringify({task, model, goal, history: conversation})
          });
          const data = await response.json();
          if (!response.ok) {
            message.textContent = data.error || 'The local AI could not process the task.';
            return;
          }
          appendChat('user', goal);
          appendChat('assistant', data.content || '(empty answer)');
          conversation.push({role: 'user', content: goal});
          conversation.push({role: 'assistant', content: String(data.content || '').slice(0, 4000)});
          conversation = conversation.slice(-10);
          while (conversation.reduce((size, item) => size + item.content.length, 0) > 9000) conversation.shift();
          document.getElementById('task-goal').value = '';
          message.textContent = 'Model: ' + data.model + '. No source files were changed.';
        } catch (error) {
          message.textContent = 'The local model request failed. Check readiness and try again.';
        }
      });
    }

    function showBuild(record) {
      if (!record || typeof record !== 'object') return;
      currentBuildId = record.id;
      const status = document.getElementById('build-status');
      status.textContent = (record.status || 'unknown') + ': ' + (record.current_step || '') +
        (record.error ? ' — ' + record.error : '');
      const details = document.getElementById('build-details');
      details.replaceChildren();
      if (record.summary) {
        const p = document.createElement('p');
        p.textContent = record.summary;
        details.appendChild(p);
      }
      if (Array.isArray(record.steps) && record.steps.length) {
        const p = document.createElement('p');
        p.textContent = 'Plan: ' + record.steps.join(' · ');
        details.appendChild(p);
      }
      if (Array.isArray(record.files) && record.files.length) {
        const p = document.createElement('p');
        p.textContent = 'Sandbox output: ' + record.files.join(', ');
        details.appendChild(p);
      }
      if (record.syntax_checks && typeof record.syntax_checks === 'object') {
        const checks = Object.entries(record.syntax_checks).slice(0, 3);
        if (checks.length) {
          const p = document.createElement('p');
          p.textContent = 'Static syntax checks (not a test run): ' +
            checks.map(([path, result]) => path + ': ' + String(result).replaceAll('_', ' ')).join(' · ');
          details.appendChild(p);
        }
      }
      const running = ['queued', 'resuming', 'inspecting', 'planning', 'generating', 'cancelling'].includes(record.status);
      document.getElementById('build-cancel').disabled = !running;
      document.getElementById('build-resume').disabled = !Boolean(record.resumable);
      document.getElementById('build-start').disabled = running;
      if (pollBuildTimer) { clearTimeout(pollBuildTimer); pollBuildTimer = null; }
      if (running) {
        pollBuildTimer = setTimeout(refreshActiveBuild, 2000);
      } else if (record.status === 'completed' || record.status === 'failed' ||
                 record.status === 'cancelled' || record.status === 'interrupted') {
        refreshArtifacts();
        refreshBuildHistory();
      }
    }

    async function refreshActiveBuild() {
      if (!currentBuildId) return;
      try {
        const response = await fetch('/api/build?id=' + encodeURIComponent(currentBuildId));
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Build status unavailable');
        showBuild(data);
      } catch (error) {
        document.getElementById('build-status').textContent =
          'Could not fetch build progress. Use Recent local builds to inspect the journal.';
        document.getElementById('build-cancel').disabled = true;
      }
    }

    async function refreshBuildHistory() {
      try {
        const response = await fetch('/api/builds');
        const data = await response.json();
        const root = document.getElementById('build-history');
        root.replaceChildren();
        if (!response.ok) {
          root.textContent = data.error || 'Configure a project and sandbox to view jobs.';
          return;
        }
        if (!Array.isArray(data.items) || !data.items.length) {
          root.textContent = 'No previous builds for this project.';
          return;
        }
        data.items.slice(0, 10).forEach(job => {
          const button = document.createElement('button');
          button.className = 'btn btn-quiet';
          button.style.margin = '5px 6px 0 0';
          button.textContent = (job.status || '?') + ': ' + String(job.goal || '').slice(0, 44);
          button.addEventListener('click', () => {
            currentBuildId = job.id;
            refreshActiveBuild();
          });
          root.appendChild(button);
        });
        if (!currentBuildId) {
          currentBuildId = data.items[0].id;
          refreshActiveBuild();
        }
      } catch (error) {
        document.getElementById('build-history').textContent = 'Local build history is unavailable.';
      }
    }

    async function searchLocalKnowledge() {
      const query = document.getElementById('knowledge-query').value.trim();
      const message = document.getElementById('knowledge-status');
      const results = document.getElementById('knowledge-results');
      if (!query || query.length > 500) {
        message.textContent = 'Enter a document search phrase of up to 500 characters.';
        return;
      }
      if (!confirm('Search all currently enabled sources in your local ToF Knowledge service? Indexed excerpts may contain private information. They will be shown here only and will not be sent to the Builder AI.')) {
        message.textContent = 'Knowledge search cancelled. No document query was sent.';
        return;
      }
      const button = document.getElementById('knowledge-search');
      await withBusy(button, 'Searching…', async () => {
        message.textContent = 'Searching local Knowledge (read-only).';
        results.replaceChildren();
        try {
          const response = await fetch('/api/knowledge/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-Builder-Request': '1'},
            body: JSON.stringify({query}),
          });
          const data = await response.json();
          if (!response.ok) {
            message.textContent = data.error || 'Knowledge service is unavailable.';
            return;
          }
          message.textContent = data.count
            ? data.count + ' local indexed excerpt(s). Unverified references only.'
            : 'No indexed excerpts found in enabled local Knowledge sources.';
          (data.hits || []).forEach(hit => {
            const card = document.createElement('article');
            card.className = 'service-card';
            card.style.marginTop = '8px';
            const name = document.createElement('strong');
            name.textContent = hit.citation_label || hit.relative_path || 'Indexed document';
            const text = document.createElement('p');
            text.className = 'service-hint';
            text.textContent = hit.preview_text || '';
            const meta = document.createElement('p');
            meta.className = 'service-hint';
            meta.textContent = 'Source: ' + (hit.relative_path || '?') + (hit.page_no == null ? '' : ' · Page ' + hit.page_no);
            card.append(name, text, meta);
            results.appendChild(card);
          });
        } catch (error) {
          message.textContent = 'Could not reach the local Knowledge search service.';
        }
      });
    }

    async function inspectArchitecture() {
      const goal = document.getElementById('task-goal').value.trim();
      const message = document.getElementById('architecture-status');
      const output = document.getElementById('architecture-context');
      if (!goal || goal.length > 2000) {
        message.textContent = 'Enter a task of up to 2000 characters first.';
        return;
      }
      const button = document.getElementById('architecture-inspect');
      await withBusy(button, 'Inspecting…', async () => {
        message.textContent = 'Reading selected project structure (read-only).';
        try {
          const response = await fetch('/api/project/inspect', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-Builder-Request': '1'},
            body: JSON.stringify({goal}),
          });
          const data = await response.json();
          if (!response.ok) {
            message.textContent = data.error || 'Project inspection is unavailable.';
            output.hidden = true;
            return;
          }
          output.textContent = data.context || '(No relevant files found.)';
          output.hidden = false;
          message.textContent = 'Inspection complete. Source excerpts are untrusted reference material; no files were changed.';
        } catch (error) {
          message.textContent = 'Could not inspect this project. Check the project connection.';
          output.hidden = true;
        }
      });
    }

    async function startSandboxBuild() {
      const guide = (currentSummary || {}).task_guide || {};
      const goal = document.getElementById('task-goal').value.trim();
      const task = document.getElementById('task-type').value;
      const model = document.getElementById('task-model').value;
      const state = document.getElementById('build-status');
      if (!goal || goal.length > 2000 || !(guide.installed_models || []).includes(model)) {
        state.textContent = 'Enter a development task and choose an installed model first.';
        return;
      }
      const button = document.getElementById('build-start');
      await withBusy(button, 'Starting build…', async () => {
        try {
          const response = await fetch('/api/build', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-Builder-Request': '1'},
            body: JSON.stringify({task, model, goal}),
          });
          const data = await response.json();
          if (!response.ok) { state.textContent = data.error || 'Could not start build.'; return; }
          showBuild(data);
          refreshBuildHistory();
        } catch (error) {
          state.textContent = 'Could not start the build. Check readiness and retry.';
        }
      });
    }

    async function resumeSandboxBuild() {
      if (!currentBuildId) return;
      const button = document.getElementById('build-resume');
      await withBusy(button, 'Verifying saved files…', async () => {
        try {
          const response = await fetch('/api/build/resume', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-Builder-Request': '1'},
            body: JSON.stringify({id: currentBuildId}),
          });
          const data = await response.json();
          if (!response.ok) {
            document.getElementById('build-status').textContent =
              data.error || 'Saved task cannot be resumed safely; review drafts first.';
            return;
          }
          showBuild(data);
        } catch (error) {
          document.getElementById('build-status').textContent =
            'Could not resume this job. No existing draft was overwritten.';
        }
      });
    }

    async function cancelSandboxBuild() {
      if (!currentBuildId) return;
      const button = document.getElementById('build-cancel');
      await withBusy(button, 'Cancelling…', async () => {
        try {
          const response = await fetch('/api/build/cancel', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-Builder-Request': '1'},
            body: JSON.stringify({id: currentBuildId}),
          });
          const data = await response.json();
          if (!response.ok) {
            document.getElementById('build-status').textContent = data.error || 'Cannot cancel build.';
            return;
          }
          showBuild(data);
        } catch (error) {
          document.getElementById('build-status').textContent = 'Cancellation request failed.';
        }
      });
    }

    function applySummary(data) {
      const source = String((data.task_guide || {}).project?.source_path || '');
      if (conversationScope && conversationScope !== source) clearTaskChat();
      conversationScope = source;
      currentSummary = data;
      renderTaskGuide(data.task_guide || {});
      renderProjectContext((data.task_guide || {}).project || {});
      const items = (data.readiness || {}).items || [];
      const bridge = items.find(item => item.name === 'repo_bridge');
      const ollama = items.find(item => item.name === 'ollama');
      const allReady = items.length > 0 && items.every(item => item.state === 'ready');
      const someReady = items.some(item => item.state === 'ready');

      const state = document.getElementById('system-state');
      const focusTitle = document.getElementById('focus-title');
      const primary = document.getElementById('primary-action');

      state.className = 'system-state ' + (allReady ? 'ready' : (someReady ? 'attention' : 'offline'));
      state.textContent = allReady ? 'Everything ready' : (someReady ? 'Still getting ready' : 'Not started');

      document.getElementById('next-step').textContent = data.next_step;
      renderGuidance(data.guidance || {});
      renderCards(data.readiness || { items: [] });

      if (ollama && ollama.state === 'ready') {
        focusTitle.textContent = allReady ? 'Everything is ready.' : 'Workspace available — check remaining requirements.';
        primary.textContent = 'Open workspace';
        primary.dataset.mode = 'open';
      } else {
        focusTitle.textContent = 'Start your workspace when you are ready.';
        primary.textContent = 'Start workspace';
        primary.dataset.mode = 'start';
      }

      if (bridge && bridge.state !== 'ready' && ollama && ollama.state === 'ready') {
        focusTitle.textContent = 'The AI model is ready, but access to your project still needs attention.';
      }
    }

    async function refreshArtifacts() {
      const root = document.getElementById('artifact-list');
      root.textContent = 'Checking sandbox files…';
      try {
        const response = await fetch('/api/artifacts');
        const data = await response.json();
        if (!response.ok || data.status !== 'ok') {
          root.textContent = 'Sandbox is not available. Choose project and check the workspace paths first.';
          return;
        }
        visibleArtifacts = data.items;
        const markable = data.items.filter(item => item.review_token);
        const reviewed = markable.filter(item => reviewedTokens.has(item.review_token)).length;
        document.getElementById('review-progress').textContent =
          reviewed + ' of ' + markable.length + ' visible text files marked reviewed. '
          + (data.truncated ? 'More files exist beyond this view.' : 'No original files were changed.');
        root.replaceChildren();
        if (!data.items.length) {
          root.textContent = 'No generated files yet. Files appear here after approved sandbox work.';
          return;
        }
        const heading = document.createElement('p');
        heading.className = 'service-hint';
        heading.textContent = data.total + ' file(s) found. '
          + (data.truncated ? 'Showing a limited set. ' : '')
          + 'Preview is read-only; manually review changes before moving them to a source project.';
        root.appendChild(heading);
        const pendingOnly = document.getElementById('review-pending-only').checked;
        for (const item of data.items) {
          if (pendingOnly && item.review_token && reviewedTokens.has(item.review_token)) continue;
          const row = document.createElement('div');
          row.className = 'service-card';
          row.style.marginTop = '10px';
          const label = document.createElement('strong');
          label.textContent = item.area + '/' + item.path;
          const detail = document.createElement('p');
          detail.className = 'service-hint';
          detail.textContent = item.size_bytes + ' bytes · ' + item.modified_at;
          row.append(label, detail);
          if (item.previewable) {
            const compare = document.createElement('button');
            compare.type = 'button';
            compare.className = 'btn btn-quiet';
            compare.textContent = 'Compare to source';
            compare.addEventListener('click', () => compareArtifact(item.area, item.path));
            row.appendChild(compare);
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'btn btn-quiet';
            button.textContent = 'Preview';
            button.addEventListener('click', () => previewArtifact(item.area, item.path));
            row.appendChild(button);
          }
          if (item.review_token) {
            const done = reviewedTokens.has(item.review_token);
            const flag = document.createElement('button');
            flag.type = 'button';
            flag.className = 'btn btn-quiet';
            flag.textContent = done ? 'Undo reviewed' : 'Mark reviewed';
            flag.disabled = !done && !inspectedTokens.has(item.review_token);
            flag.title = done ? 'Remove browser review mark' : 'Preview or compare this exact file first';
            flag.addEventListener('click', () => changeReview(item.review_token, !done));
            row.appendChild(flag);
            if (done) {
              const exportButton = document.createElement('button');
              exportButton.className = 'btn btn-secondary';
              exportButton.type = 'button';
              exportButton.textContent = 'Copy reviewed handoff';
              exportButton.addEventListener('click', () =>
                copyReviewedHandoff(item.area, item.path, item.review_token));
              row.appendChild(exportButton);
            }
            const status = document.createElement('p');
            status.className = 'service-hint';
            status.textContent = done ? 'Reviewed in this browser; no source changes applied'
              : 'Needs review';
            row.appendChild(status);
          }
          root.appendChild(row);
        }
      } catch (error) {
        root.textContent = 'Could not list sandbox files. Check the local control UI.';
      }
    }

    async function copyReviewedHandoff(area, path, token) {
      const output = document.getElementById('artifact-preview');
      const current = reviewToken(area, path);
      if (!reviewedTokens.has(token) || current !== token) {
        output.textContent = 'The review is stale. Refresh and inspect this file again.';
        return;
      }
      try {
        const query = new URLSearchParams({area, path, token});
        const response = await fetch('/api/artifact-handoff?' + query.toString());
        const data = await response.json();
        if (!response.ok || data.status !== 'ready') {
          throw Error(data.error || 'File changed or cannot be safely handed off');
        }
        if (data.kind === 'no_changes') {
          output.textContent = 'Identical to the original: nothing to transfer.';
          return;
        }
        await navigator.clipboard.writeText(data.content);
        output.closest('details').open = true;
        output.textContent = 'Copied ' + data.kind + ' for ' + data.path
          + '. Review and apply manually in your own editor. Original source unchanged.';
      } catch (error) {
        output.closest('details').open = true;
        output.textContent = 'Handoff not copied: ' + String(error);
      }
    }

    async function previewArtifact(area, path) {
      const output = document.getElementById('artifact-preview');
      output.textContent = 'Loading text preview…';
      try {
        const query = new URLSearchParams({area, path});
        const response = await fetch('/api/artifact-preview?' + query.toString());
        const data = await response.json();
        output.textContent = response.ok
          ? data.area + '/' + data.path + '\\n\\n' + data.content
          : 'Preview unavailable: ' + (data.error || 'unknown reason');
        if (response.ok) {
          output.closest('details').open = true;
          const token = reviewToken(area, path);
          if (token) inspectedTokens.add(token);
          refreshArtifacts();
        }
      } catch (error) {
        output.textContent = 'Unable to read this text preview.';
      }
    }

    async function compareArtifact(area, path) {
      const output = document.getElementById('artifact-preview');
      output.closest('details').open = true;
      output.textContent = 'Comparing to read-only source…';
      try {
        const query = new URLSearchParams({area, path});
        const response = await fetch('/api/artifact-diff?' + query.toString());
        const data = await response.json();
        if (!response.ok) {
          output.textContent = 'Comparison unavailable: ' + (data.error || 'unknown reason');
        } else if (data.status === 'new_file') {
          output.textContent = 'New file: no matching source path exists. Review the preview before adopting.';
        } else if (data.status === 'source_unavailable' || data.status === 'source_too_large') {
          output.textContent = 'Source cannot be compared: ' + data.status;
        } else if (data.status === 'identical') {
          output.textContent = 'Generated file is identical to the source.';
        } else {
          output.textContent = 'Read-only diff (minus = source, plus = generated)\\n\\n'
            + data.diff + (data.truncated ? '\\n[Diff truncated — inspect files directly]' : '');
        }
        if (response.ok && (data.status === 'changed' || data.status === 'identical')
            && !data.truncated) {
          const token = reviewToken(area, path);
          if (token) inspectedTokens.add(token);
          refreshArtifacts();
        }
      } catch (error) {
        output.textContent = 'Could not compare this artifact.';
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
        state.textContent = 'Could not check status';
        document.getElementById('focus-title').textContent = 'ToF could not check what is ready.';
        document.getElementById('next-step').textContent = 'Try checking again. If the problem remains, open “Problems & technical details” and choose “Find a problem”.';
        showFeedback('I could not check the workspace. Try again. If it still fails, choose “Find a problem” below.', 'attention');
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
        document.getElementById('builder-chat').scrollIntoView({behavior: 'smooth'});
      } else {
        await runAction('up', button);
      }
    }

    async function runAction(action, button = null) {
      await withBusy(button, 'Working…', async () => {
        appendLog(`Running ${action}…`);
        try {
          const response = await fetch(`/api/${action}`, { method: 'POST', headers: {'X-Builder-Request': '1'} });
          const data = await response.json();
          const summary = data.output ? data.output : JSON.stringify(data, null, 2);
          appendLog(`${data.label || action}: ${summary || 'completed'}`);
          if (!response.ok || Number(data.exit_code || 0) !== 0) {
            showFeedback('That did not finish successfully. Open “Problems & technical details” and choose “Find a problem”.', 'attention');
          } else {
            showFeedback('Done. I checked the current state again for you.', 'ok');
          }
        } catch (error) {
          showFeedback('That did not work. Check that the local workspace is still running, then try again.', 'attention');
          appendLog(`Action ${action} failed: ${error}`);
        }
        await refreshSummary();
      });
    }

    async function openLink(name, button = null) {
      await withBusy(button, 'Opening…', async () => {
        appendLog(`Opening ${name}…`);
        try {
          const response = await fetch(`/api/open/${name}`, { method: 'POST', headers: {'X-Builder-Request': '1'} });
          const data = await response.json();
          appendLog(data.opened ? `Opened ${data.opened}` : JSON.stringify(data, null, 2));
          showFeedback(data.opened ? 'Opened on this computer.' : 'The page could not be opened automatically. Use the technical details below if you need the address.', data.opened ? 'ok' : 'attention');
        } catch (error) {
          showFeedback('The page could not be opened automatically. Check that the local workspace is running.', 'attention');
          appendLog(`Could not open ${name}: ${error}`);
        }
      });
    }

    refreshSummary();
    refreshArtifacts();
    refreshBuildHistory();
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



def _configured_links(env: dict[str, str] | None = None) -> dict[str, dict[str, str]]:
    """Resolve browser links from the same existing configuration as Compose."""
    values = env if env is not None else read_env()
    config = {
        "repo_bridge_health": ("REPO_BRIDGE_PORT", "8099", "/health"),
        "ollama": ("OLLAMA_PORT", "11434", ""),
    }
    result = {}
    for name, (key, default, suffix) in config.items():
        try:
            port = int(values.get(key, default))
            if not (1 <= port <= 65535):
                raise ValueError("invalid port")
            url = f"http://127.0.0.1:{port}{suffix}"
        except (ValueError, TypeError):
            url = ""
        result[name] = {"label": LINKS[name]["label"], "url": url}
    return result


def _open_link(name: str) -> dict[str, object]:
    link = _configured_links()[name]
    if not link["url"]:
        return {"opened": None, "label": link["label"], "error": "invalid_local_port"}
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
    env = read_env()
    urls = {
        'repo_bridge': f"http://127.0.0.1:{env.get('REPO_BRIDGE_PORT', '8099')}/health",
        'ollama': f"http://127.0.0.1:{env.get('OLLAMA_PORT', '11434')}/api/tags",
    }
    items = []
    for key, target in READINESS_TARGETS.items():
        url = urls[key]
        items.append({'name': key, 'label': target['label'], 'url': url, 'state': _probe_url(url)})

    for key, label, report in (
        ('source', 'Read-only project', source_repo_report(env)),
        ('sandbox', 'Writable workspace', sandbox_report(env)),
    ):
        state = 'ready' if report['state'] == 'ok' else 'not_reachable'
        items.append({'name': key, 'label': label, 'state': state,
                      'detail': report['path'] if state == 'ready' else f"Path needs attention: {report['state']}"})

    model = env.get('DEFAULT_OLLAMA_MODEL', 'qwen2.5:0.5b')
    try:
        found = model in ollama_tags(env.get('OLLAMA_PORT', '11434'))
    except Exception:
        found = False
    items.append({'name': 'default_model', 'label': 'Selected AI model',
                  'state': 'ready' if found else 'not_reachable',
                  'detail': model if found else f"Selected model not available: {model}"})
    return {'items': items}


def _summary_payload() -> dict[str, object]:
    readiness = _readiness_payload()
    all_ready = bool(readiness['items']) and all(item['state'] == 'ready' for item in readiness['items'])
    guidance = explain_readiness(readiness['items'])
    next_step = guidance['next_step']
    return {
        'next_step': next_step,
        'actions': [
            {'name': key, 'label': spec.label, 'safe_level': spec.safe_level}
            for key, spec in ACTIONS.items()
        ],
        'links': _configured_links(),
        'readiness': readiness,
        'guidance': guidance,
        'task_guide': task_guide(),
    }


def _json_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, indent=2).encode('utf-8')



def run_ui(host: str = '127.0.0.1', port: int = 8795, open_browser: bool = True) -> int:
    if host not in ('127.0.0.1', 'localhost'):
        raise ValueError("Builder control UI must bind to loopback")
    if not 1 <= port <= 65535:
        raise ValueError("Invalid Builder control UI port")

    chat_limit = threading.BoundedSemaphore(value=1)
    agent_manager = AgentManager(model_gate=chat_limit)

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, content_type: str, body: bytes) -> None:
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)

        def _valid_request(self, *, mutation: bool = False) -> bool:
            host = self.headers.get('Host', '')
            if host not in (f'127.0.0.1:{port}', f'localhost:{port}'):
                return False
            origin = self.headers.get('Origin')
            if origin and origin != 'http://' + host:
                return False
            if self.headers.get('Sec-Fetch-Site') == 'cross-site':
                return False
            if mutation and self.headers.get('X-Builder-Request') != '1':
                return False
            return True

        def do_GET(self) -> None:  # noqa: N802
            if not self._valid_request():
                self._send(403, 'application/json; charset=utf-8', _json_bytes({'error': 'forbidden'}))
                return
            parsed = urlparse(self.path)
            if parsed.path == '/api/identity':
                self._send(200, 'application/json; charset=utf-8',
                           _json_bytes({'app': 'tof_local_builder', 'ui': 'control'}))
                return
            if parsed.path == '/':
                self._send(200, 'text/html; charset=utf-8', HTML.encode('utf-8'))
                return
            if parsed.path == '/api/summary':
                self._send(200, 'application/json; charset=utf-8', _json_bytes(_summary_payload()))
                return
            if parsed.path == '/api/conversation':
                try:
                    result = ConversationStore(read_env()).load()
                except (ConversationError, JournalError, OSError) as exc:
                    self._send(400, 'application/json; charset=utf-8', _json_bytes({'error': str(exc)}))
                    return
                self._send(200, 'application/json; charset=utf-8', _json_bytes(result))
                return
            if parsed.path == '/api/build':
                job_id = parse_qs(parsed.query).get('id', [''])[0]
                try:
                    result = agent_manager.status(job_id)
                except (JournalError, ValueError, OSError) as exc:
                    self._send(400, 'application/json; charset=utf-8', _json_bytes({'error': str(exc)}))
                    return
                self._send(200, 'application/json; charset=utf-8', _json_bytes(result))
                return
            if parsed.path == '/api/builds':
                try:
                    result = agent_manager.recent()
                except (JournalError, ValueError, OSError) as exc:
                    self._send(400, 'application/json; charset=utf-8', _json_bytes({'error': str(exc)}))
                    return
                self._send(200, 'application/json; charset=utf-8', _json_bytes({'items': result}))
                return
            if parsed.path == '/api/artifacts':
                self._send(200, 'application/json; charset=utf-8', _json_bytes(artifact_inventory(read_env())))
                return
            if parsed.path == '/api/artifact-handoff':
                values = parse_qs(parsed.query)
                area = values.get('area', [''])[0]
                relative = values.get('path', [''])[0]
                token = values.get('token', [''])[0]
                try:
                    result = artifact_handoff(read_env(), area, relative, token)
                except (ValueError, OSError) as exc:
                    self._send(400, 'application/json; charset=utf-8',
                               _json_bytes({'error': str(exc)}))
                    return
                self._send(200, 'application/json; charset=utf-8', _json_bytes(result))
                return
            if parsed.path == '/api/artifact-diff':
                values = parse_qs(parsed.query)
                area = values.get('area', [''])[0]
                relative_path = values.get('path', [''])[0]
                try:
                    comparison = artifact_diff(read_env(), area, relative_path)
                except (ValueError, OSError) as exc:
                    self._send(400, 'application/json; charset=utf-8', _json_bytes({'error': str(exc)}))
                    return
                self._send(200, 'application/json; charset=utf-8', _json_bytes(comparison))
                return
            if parsed.path == '/api/artifact-preview':
                values = parse_qs(parsed.query)
                area = values.get('area', [''])[0]
                relative_path = values.get('path', [''])[0]
                try:
                    preview = artifact_preview(read_env(), area, relative_path)
                except (ValueError, OSError) as exc:
                    self._send(400, 'application/json; charset=utf-8', _json_bytes({'error': str(exc)}))
                    return
                self._send(200, 'application/json; charset=utf-8', _json_bytes(preview))
                return
            self._send(404, 'application/json; charset=utf-8', _json_bytes({'error': 'not found'}))

        def do_POST(self) -> None:  # noqa: N802
            if not self._valid_request(mutation=True):
                self._send(403, 'application/json; charset=utf-8', _json_bytes({'error': 'forbidden'}))
                return
            parsed = urlparse(self.path)
            if parsed.path in ('/api/conversation/save', '/api/conversation/delete'):
                if not self.headers.get('Content-Type', '').lower().startswith('application/json'):
                    self._send(415, 'application/json; charset=utf-8', _json_bytes({'error': 'JSON required'}))
                    return
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                except ValueError:
                    length = 0
                if not 0 < length <= 24_000:
                    self._send(413, 'application/json; charset=utf-8', _json_bytes({'error': 'Invalid snapshot size'}))
                    return
                try:
                    payload = json.loads(self.rfile.read(length))
                    if not isinstance(payload, dict):
                        raise ValueError('Expected a JSON object')
                    store = ConversationStore(read_env())
                    if parsed.path.endswith('/save'):
                        result = store.save(payload.get('messages'))
                    else:
                        result = store.delete()
                except (ConversationError, JournalError, ValueError, OSError) as exc:
                    self._send(400, 'application/json; charset=utf-8', _json_bytes({'error': str(exc)}))
                    return
                self._send(200, 'application/json; charset=utf-8', _json_bytes(result))
                return
            if parsed.path == '/api/knowledge/search':
                if not self.headers.get('Content-Type', '').lower().startswith('application/json'):
                    self._send(415, 'application/json; charset=utf-8', _json_bytes({'error': 'JSON required'}))
                    return
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                except ValueError:
                    length = 0
                if not 0 < length <= 2048:
                    self._send(413, 'application/json; charset=utf-8', _json_bytes({'error': 'Invalid request size'}))
                    return
                try:
                    payload = json.loads(self.rfile.read(length))
                    query = payload.get('query') if isinstance(payload, dict) else None
                    result = search_knowledge(query, read_env())
                except (KnowledgeError, TypeError, ValueError, OSError) as exc:
                    self._send(400, 'application/json; charset=utf-8', _json_bytes({'error': str(exc)}))
                    return
                self._send(200, 'application/json; charset=utf-8', _json_bytes(result))
                return
            if parsed.path == '/api/project/inspect':
                if not self.headers.get('Content-Type', '').lower().startswith('application/json'):
                    self._send(415, 'application/json; charset=utf-8', _json_bytes({'error': 'JSON required'}))
                    return
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                except ValueError:
                    length = 0
                if not 0 < length <= 4096:
                    self._send(413, 'application/json; charset=utf-8', _json_bytes({'error': 'Invalid request size'}))
                    return
                try:
                    payload = json.loads(self.rfile.read(length))
                    goal = payload.get('goal') if isinstance(payload, dict) else None
                    if not isinstance(goal, str) or not 0 < len(goal.strip()) <= 2000:
                        raise ValueError('Enter a task before inspecting the project')
                    bridge = AgentBridge(read_env())
                    result = project_context(bridge, goal.strip())
                except (ValueError, TypeError, BridgeError, OSError) as exc:
                    self._send(400, 'application/json; charset=utf-8', _json_bytes({'error': str(exc)}))
                    return
                self._send(200, 'application/json; charset=utf-8',
                           _json_bytes({'context': result, 'read_only': True, 'files_modified': False}))
                return
            if parsed.path in ('/api/build', '/api/build/cancel', '/api/build/resume'):
                if not self.headers.get('Content-Type', '').lower().startswith('application/json'):
                    self._send(415, 'application/json; charset=utf-8', _json_bytes({'error': 'JSON required'}))
                    return
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                except ValueError:
                    length = 0
                if not 0 < length <= 8_192:
                    self._send(413, 'application/json; charset=utf-8', _json_bytes({'error': 'Invalid request size'}))
                    return
                try:
                    payload = json.loads(self.rfile.read(length))
                    if not isinstance(payload, dict):
                        raise ValueError('Expected a JSON object')
                    if parsed.path.endswith('/cancel'):
                        result = agent_manager.cancel(payload.get('id'))
                    elif parsed.path.endswith('/resume'):
                        result = agent_manager.resume(payload.get('id'))
                    else:
                        result = agent_manager.start(
                            payload.get('task'), payload.get('model'), payload.get('goal'),
                        )
                except (BuildError, BridgeError, JournalError, ModelChatError, ValueError, TypeError, OSError) as exc:
                    self._send(400, 'application/json; charset=utf-8', _json_bytes({'error': str(exc)}))
                    return
                self._send(200, 'application/json; charset=utf-8', _json_bytes(result))
                return
            if parsed.path == '/api/task':
                if not self.headers.get('Content-Type', '').lower().startswith('application/json'):
                    self._send(415, 'application/json; charset=utf-8', _json_bytes({'error': 'JSON required'}))
                    return
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                except ValueError:
                    length = 0
                if not 0 < length <= 16_384:
                    self._send(413, 'application/json; charset=utf-8', _json_bytes({'error': 'Request too large or empty'}))
                    return
                if not chat_limit.acquire(blocking=False):
                    self._send(429, 'application/json; charset=utf-8', _json_bytes(
                        {'error': 'Builder is already handling another AI request'}))
                    return
                try:
                    try:
                        payload = json.loads(self.rfile.read(length))
                        if not isinstance(payload, dict):
                            raise ValueError('Expected an object')
                        result = run_task_once(
                            task=payload.get('task'), model=payload.get('model'),
                            goal=payload.get('goal'), history=payload.get('history'),
                        )
                    except (ValueError, TypeError, ModelChatError) as exc:
                        self._send(400, 'application/json; charset=utf-8', _json_bytes({'error': str(exc)}))
                        return
                    self._send(200, 'application/json; charset=utf-8', _json_bytes(result))
                finally:
                    chat_limit.release()
                return
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
