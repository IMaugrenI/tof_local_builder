#!/usr/bin/env python3
from __future__ import annotations

import html
import json

import wizard as base


def _host_class(info: dict) -> str:
    ram = info.get("ram_gb")
    if isinstance(ram, (int, float)):
        if ram <= 8:
            return "light"
        if ram >= 24:
            return "stronger"
    return "balanced"


def _host_recommendation(info: dict) -> dict[str, object]:
    host_class = _host_class(info)
    acceleration = str(info.get("recommended_acceleration", "cpu"))
    model = str(info.get("recommended_model", "qwen2.5:0.5b"))
    supports_gui = bool(info.get("supports_gui"))
    docker_reachable = bool(info.get("docker_reachable"))
    has_render = bool(info.get("has_render_node"))
    has_nvidia = bool(info.get("has_nvidia"))

    title_map = {
        "light": "Leicht starten / Start light",
        "balanced": "Ausgewogen starten / Start balanced",
        "stronger": "Etwas stärker möglich / Slightly stronger is possible",
    }
    profile_map = {
        "light": "cpu_light",
        "balanced": "cpu_balanced",
        "stronger": "optional_3b",
    }
    summary_map = {
        "light": "Dieser Host wirkt eher leicht. Ein kleines Profil reduziert Reibung beim ersten Start. / This host looks on the lighter side. A small profile reduces friction on the first start.",
        "balanced": "Dieser Host wirkt nach einem guten Standardfall. Ein ausgewogenes Profil ist hier meist der beste Einstieg. / This host looks like a good default case. A balanced profile is usually the best entry point here.",
        "stronger": "Dieser Host wirkt etwas stärker. Du kannst ruhig mit mehr Spielraum starten, ohne die sichere Basis zu verlieren. / This host looks a bit stronger. You can start with a bit more room without losing the safe baseline.",
    }

    bullets: list[str] = [
        f"Profil-Empfehlung / Profile recommendation: {profile_map[host_class]}",
        f"Beschleunigung / Acceleration: {acceleration}",
        f"Standardmodell / Default model: {model}",
    ]
    if has_nvidia:
        bullets.append("NVIDIA ist sichtbar. Später kann bewusst ein stärkeres Profil getestet werden. / NVIDIA is visible. A stronger profile can be tested later on purpose.")
    elif has_render:
        bullets.append("Ein Render-Node ist sichtbar. Hardware-Pfade können später bewusst getestet werden. / A render node is visible. Hardware paths can be tested later on purpose.")
    else:
        bullets.append("Kein GPU-Hinweis erkannt. CPU-first bleibt der sichere Start. / No GPU hint detected. CPU-first stays the safe starting point.")
    if not docker_reachable:
        bullets.append("Docker ist aktuell nicht erreichbar. Erst das beheben, dann weiter konfigurieren. / Docker is not reachable right now. Fix that first, then continue configuring.")
    if not supports_gui:
        bullets.append("Keine GUI erkannt. In diesem Fall fällt der Builder auf den Konsolen-Wizard zurück. / No GUI detected. In that case the builder falls back to the console wizard.")

    return {
        "title": title_map[host_class],
        "summary": summary_map[host_class],
        "bullets": bullets,
    }


def _stacked_wizard_html(self, error: str | None = None) -> str:
    state = self.server.state
    info = state.info
    acceleration_options = base.recommended_acceleration_options(info)
    selection_map = state.selection_map
    current_task_key = state.current_task_key
    current_profile_key = state.current_profile_key
    current_model = state.current_model
    manual_tag = base._manual_fallback_tag(state.catalog)

    selected_entries = base._selection_entries(selection_map, current_task_key, current_profile_key)
    recommendation = base._recommended_entry(selected_entries)
    recommendation_tag = recommendation.get("tag") if recommendation else ""
    selected_tags = [str(entry.get("tag", "")).strip() for entry in selected_entries if entry.get("tag")]
    default_model = base._default_model_for_selection(current_model, selected_tags, recommendation_tag)

    if current_model not in selected_tags and current_model not in base.MODEL_OPTIONS:
        model_choice = manual_tag
        custom_model = current_model
    elif current_model in selected_tags:
        model_choice = current_model
        custom_model = ""
    elif default_model in selected_tags:
        model_choice = default_model
        custom_model = ""
    else:
        model_choice = manual_tag
        custom_model = ""

    task_options_html = "".join(
        f'<option value="{base.html.escape(option["key"])}"{" selected" if option["key"] == current_task_key else ""}>{base.html.escape(option["label"])}<\/option>'
        for option in base.TASK_CHOICES
    )
    profile_options_html = "".join(
        f'<option value="{base.html.escape(option["key"])}"{" selected" if option["key"] == current_profile_key else ""}>{base.html.escape(option["label"])}<\/option>'
        for option in base.PROFILE_CHOICES
    )
    model_options_html = "".join(
        f'<option value="{base.html.escape(entry["tag"])}"{" selected" if entry["tag"] == model_choice else ""}>{base.html.escape(entry["tag"])}<\/option>'
        for entry in selected_entries
    )
    model_options_html += (
        f'<option value="{base.html.escape(manual_tag)}"{" selected" if model_choice == manual_tag else ""}>{base.html.escape(manual_tag)}<\/option>'
    )
    acceleration_html = "".join(
        f'<option value="{base.html.escape(option)}"{" selected" if option == state.current_acceleration else ""}>{base.html.escape(option)}<\/option>'
        for option in acceleration_options
    )
    host_cards = "".join(f"<li>{base.html.escape(line)}</li>" for line in base.host_summary_lines(info))
    error_html = f'<div class="notice error">{base.html.escape(error)}</div>' if error else ""
    checked = "checked" if state.current_browser else ""
    source_value = base.html.escape(state.current_source)
    custom_value = base.html.escape(custom_model)

    current_task = base._task_choice_map().get(current_task_key, base.TASK_CHOICES[0])
    current_profile = base._profile_choice_map().get(current_profile_key, base.PROFILE_CHOICES[0])
    recommendation_text = recommendation_tag or default_model
    recommendation_note = str(recommendation.get("notes", "")).strip() if recommendation else ""

    selection_map_json = base.json.dumps(selection_map, ensure_ascii=False)
    manual_tag_json = base.json.dumps(manual_tag, ensure_ascii=False)
    current_model_json = base.json.dumps(current_model, ensure_ascii=False)
    current_task_json = base.json.dumps(current_task_key, ensure_ascii=False)
    current_profile_json = base.json.dumps(current_profile_key, ensure_ascii=False)
    task_choices_json = base.json.dumps(base.TASK_CHOICES, ensure_ascii=False)
    profile_choices_json = base.json.dumps(base.PROFILE_CHOICES, ensure_ascii=False)

    host_rec = _host_recommendation(info)
    host_rec_title = base.html.escape(str(host_rec["title"]))
    host_rec_summary = base.html.escape(str(host_rec["summary"]))
    host_rec_bullets = "".join(f"<li>{base.html.escape(str(item))}</li>" for item in host_rec["bullets"])

    return f"""<!doctype html>
<html lang=\"de\">
<head>
  <meta charset=\"utf-8\">
  <title>ToF Local Builder – Setup</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
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
      --shadow: 0 28px 90px rgba(0, 0, 0, 0.38);
      --radius: 18px;
      --section-gap: 24px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;
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
    .stack {{
      display: grid;
      gap: var(--section-gap);
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
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
    h2 {{
      margin: 0 0 10px;
      font-size: 1.25rem;
    }}
    h3 {{
      margin: 0 0 10px;
      font-size: 1rem;
    }}
    p {{
      margin: 0 0 14px;
      color: var(--muted);
      line-height: 1.66;
    }}
    .intro-grid,
    .host-grid {{
      display: grid;
      gap: 16px;
      margin-top: 22px;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    }}
    .mini,
    .host-box {{
      background: var(--panel-soft);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
    }}
    .mini ul,
    .host-box ul,
    .host-list {{
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
      line-height: 1.55;
    }}
    .host-list {{
      display: grid;
      gap: 10px;
      list-style: none;
      padding-left: 0;
    }}
    .host-list li {{
      background: var(--panel-soft);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 11px 13px;
      color: var(--muted);
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
    .notice.recommendation {{
      border-color: rgba(123, 216, 143, 0.22);
      background: rgba(123, 216, 143, 0.08);
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
    input[type=\"text\"], select {{
      width: 100%;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: rgba(8, 12, 18, 0.92);
      color: var(--text);
      padding: 13px 14px;
      font-size: 0.95rem;
      outline: none;
    }}
    input[type=\"text\"]:focus, select:focus {{
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
  </style>
</head>
<body>
  <div class=\"shell\">
    <div class=\"stack\">
      <section class=\"panel\">
        <div class=\"eyebrow\">local setup · de / en</div>
        <h1>ToF Local Builder<br>Erstsetup / First setup</h1>
        <p>
          Diese kurze lokale Seite richtet den Builder einmal ein und übergibt danach an die Hauptoberfläche.
          Die Quelle bleibt read-only. Schreibpfade bleiben in der Sandbox.
        </p>
        <p>
          This short local page configures the builder once and then hands over to the main interface.
          The source remains read-only. Writable paths stay inside the sandbox.
        </p>
        <div class=\"intro-grid\">
          <article class=\"mini\">
            <h3>Was hier gesetzt wird / What gets configured</h3>
            <ul>
              <li>Quellpfad / Source path</li>
              <li>Aufgabentyp / Task type</li>
              <li>Leistungsprofil / Performance profile</li>
              <li>Standardmodell / Default model</li>
              <li>Beschleunigungsmodus / Acceleration mode</li>
            </ul>
          </article>
          <article class=\"mini\">
            <h3>Ablauf / Flow</h3>
            <ul>
              <li>Erst lesen, dann Host prüfen / Read first, then inspect the host</li>
              <li>Empfehlung grob einordnen / Place the recommendation</li>
              <li>Danach lokal einstellen / Then configure locally</li>
              <li>Zum Schluss an Open WebUI übergeben / Finally hand off to Open WebUI</li>
            </ul>
          </article>
        </div>
      </section>

      <section class=\"panel\">
        <h2>Erkannter Host / Detected host</h2>
        <p>
          Diese Etage zeigt zuerst, wie der Builder den lokalen Rechner grob einordnet,
          und gibt danach eine kleine Startempfehlung für Profil und Beschleunigung.
        </p>
        <div class=\"host-grid\">
          <article class=\"host-box\">
            <h3>{host_rec_title}</h3>
            <p>{host_rec_summary}</p>
            <ul>
              {host_rec_bullets}
            </ul>
          </article>
          <article class=\"host-box\">
            <h3>Host-Ansicht / Host view</h3>
            <ul class=\"host-list\">
              {host_cards}
            </ul>
          </article>
        </div>
      </section>

      <section class=\"panel\">
        <h2>Lokale Einrichtung / Local configuration</h2>
        <p>Der Builder fragt jetzt zuerst nach Aufgabe und Profil. / The builder now asks for task and profile first.</p>
        {error_html}
        <div id=\"recommendation_box\" class=\"notice recommendation\">
          <strong>Empfohlen / Recommended:</strong> <span id=\"recommendation_tag\">{base.html.escape(recommendation_text)}</span><br>
          <span id=\"recommendation_note\">{base.html.escape(recommendation_note)}</span><br>
          <span id=\"selection_hint\">{base.html.escape(current_task["label"])} · {base.html.escape(current_profile["label"])}</span>
        </div>
        <form method=\"post\" action=\"/submit\">
          <label>
            <span>Quellpfad / Source path
              <small>Existierender Ordner, read-only genutzt. / Existing directory, used read-only.</small>
            </span>
            <input type=\"text\" name=\"source_repo_path\" value=\"{source_value}\" placeholder=\"/home/.../mein_repo\" required>
          </label>

          <label>
            <span>Wofür brauchst du den Builder? / What do you need the builder for?
              <small>Der Wizard schneidet die Modellwahl zuerst nach Aufgabe. / The wizard cuts model choices by task first.</small>
            </span>
            <select name=\"task\" id=\"task\">
              {task_options_html}
            </select>
          </label>

          <label>
            <span>Wie leicht soll das Setup bleiben? / How light should the setup stay?
              <small>Von sehr leicht bis stärker optional. / From very light to stronger optional.</small>
            </span>
            <select name=\"profile\" id=\"profile\">
              {profile_options_html}
            </select>
          </label>

          <label>
            <span>Empfohlenes Modell / Recommended model</span>
            <select name=\"model\" id=\"model\">
              {model_options_html}
            </select>
          </label>

          <label>
            <span>Eigenes Modell / Custom model
              <small>Nur nötig, wenn oben `custom` gewählt ist. / Only needed when `custom` is selected above.</small>
            </span>
            <input type=\"text\" id=\"custom_model\" name=\"custom_model\" value=\"{custom_value}\" placeholder=\"qwen2.5-coder:1.5b\">
          </label>

          <label>
            <span>Beschleunigungsmodus / Acceleration mode</span>
            <select name=\"acceleration\">
              {acceleration_html}
            </select>
          </label>

          <label class=\"checkbox\">
            <input type=\"checkbox\" name=\"open_browser\" value=\"1\" {checked}>
            <span>
              <strong>Nach dem Start automatisch an die Hauptoberfläche übergeben / Automatically hand off to the main interface after startup</strong>
            </span>
          </label>

          <div class=\"actions\">
            <button type=\"submit\">Speichern und weiter / Save and continue</button>
            <a class=\"link-button\" href=\"/cancel\">Abbrechen / Cancel</a>
          </div>
        </form>
      </section>
    </div>
  </div>
  <script>
    const selectionMap = {selection_map_json};
    const taskChoices = {task_choices_json};
    const profileChoices = {profile_choices_json};
    const manualTag = {manual_tag_json};
    const currentModel = {current_model_json};
    const currentTask = {current_task_json};
    const currentProfile = {current_profile_json};

    const taskSelect = document.getElementById(\"task\");
    const profileSelect = document.getElementById(\"profile\");
    const modelSelect = document.getElementById(\"model\");
    const customInput = document.getElementById(\"custom_model\");
    const recommendationTagNode = document.getElementById(\"recommendation_tag\");
    const recommendationNoteNode = document.getElementById(\"recommendation_note\");
    const selectionHintNode = document.getElementById(\"selection_hint\");

    const getModels = (taskKey, profileKey) => {{
      const taskGroup = selectionMap[taskKey] || {{}};
      const models = taskGroup[profileKey];
      return Array.isArray(models) ? models : [];
    }};

    const firstRecommendedTag = (models) => {{
      const recommended = models.find((item) => item.recommended);
      return recommended ? recommended.tag : (models[0]?.tag || \"\");
    }};

    const taskLabel = (taskKey) => {{
      const item = taskChoices.find((entry) => entry.key === taskKey);
      return item ? item.label : taskKey;
    }};

    const profileLabel = (profileKey) => {{
      const item = profileChoices.find((entry) => entry.key === profileKey);
      return item ? item.label : profileKey;
    }};

    const syncCustomState = () => {{
      const enabled = modelSelect.value === manualTag;
      customInput.disabled = !enabled;
      if (!enabled && customInput.value && modelSelect.value !== manualTag) {{
        customInput.value = \"\";
      }}
    }};

    const rebuildModels = () => {{
      const taskKey = taskSelect.value || currentTask;
      const profileKey = profileSelect.value || currentProfile;
      const models = getModels(taskKey, profileKey);
      const selectedBefore = modelSelect.value || currentModel;
      const customValue = customInput.value.trim();

      modelSelect.innerHTML = \"\";

      for (const model of models) {{
        const option = document.createElement(\"option\");
        option.value = model.tag;
        option.textContent = model.tag;
        modelSelect.appendChild(option);
      }}

      const customOption = document.createElement(\"option\");
      customOption.value = manualTag;
      customOption.textContent = manualTag;
      modelSelect.appendChild(customOption);

      const availableTags = models.map((model) => model.tag);
      let nextValue = \"\";

      if (availableTags.includes(selectedBefore)) {{
        nextValue = selectedBefore;
      }} else if (selectedBefore === manualTag || (customValue && !availableTags.includes(customValue))) {{
        nextValue = manualTag;
      }} else {{
        nextValue = firstRecommendedTag(models) || manualTag;
      }}

      modelSelect.value = nextValue;

      const recommended = models.find((item) => item.recommended) || models[0] || null;
      recommendationTagNode.textContent = recommended ? recommended.tag : (customValue || \"\");
      recommendationNoteNode.textContent = recommended ? (recommended.notes || \"\") : \"\";
      selectionHintNode.textContent = `${{taskLabel(taskKey)}} · ${{profileLabel(profileKey)}}`;

      syncCustomState();
    }};

    taskSelect.addEventListener(\"change\", rebuildModels);
    profileSelect.addEventListener(\"change\", rebuildModels);
    modelSelect.addEventListener(\"change\", syncCustomState);

    rebuildModels();
  </script>
</body>
</html>"""


base.WizardHandler._wizard_html = _stacked_wizard_html


if __name__ == "__main__":
    raise SystemExit(base.main())
