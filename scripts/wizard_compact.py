#!/usr/bin/env python3
from __future__ import annotations

import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning)

import wizard_stacked as stacked


def _compact_host_recommendation(info: dict) -> dict[str, object]:
    host_class = stacked._host_class(info)
    acceleration = str(info.get("recommended_acceleration", "cpu"))
    model = str(info.get("recommended_model", "qwen2.5:0.5b"))
    docker_reachable = bool(info.get("docker_reachable"))
    supports_gui = bool(info.get("supports_gui"))
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
        "light": "Eher leichter Host. Für den ersten Start ist ein kleines Profil am ruhigsten. / Lighter host. A small profile is the calmest first start.",
        "balanced": "Guter Standardfall. Ein ausgewogenes Profil passt hier meist am besten. / Good default case. A balanced profile usually fits best here.",
        "stronger": "Etwas stärkerer Host. Mehr Spielraum ist hier vertretbar. / Slightly stronger host. A bit more headroom is reasonable here.",
    }

    bullets: list[str] = [
        f"Profil / Profile: {profile_map[host_class]}",
        f"Beschleunigung / Acceleration: {acceleration}",
        f"Modell / Model: {model}",
    ]
    if has_nvidia:
        bullets.append("NVIDIA erkannt. Stärker später möglich. / NVIDIA detected. Stronger later is possible.")
    elif has_render:
        bullets.append("Render-Node erkannt. Hardware-Pfad später testbar. / Render node detected. Hardware path can be tested later.")
    else:
        bullets.append("Keine GPU erkannt. CPU-first passt gut. / No GPU detected. CPU-first fits well.")
    if not docker_reachable:
        bullets.append("Docker gerade nicht erreichbar. Erst das fixen. / Docker is not reachable right now. Fix that first.")
    if not supports_gui:
        bullets.append("Keine GUI erkannt. Konsolen-Wizard aktiv. / No GUI detected. Console wizard will be used.")

    return {
        "title": title_map[host_class],
        "summary": summary_map[host_class],
        "bullets": bullets,
    }


stacked._host_recommendation = _compact_host_recommendation


def _compact_html(self, error: str | None = None) -> str:
    page = stacked._stacked_wizard_html(self, error)
    page = page.replace("<\\/option>", "</option>")
    page = page.replace(
        "Diese Etage zeigt zuerst, wie der Builder den lokalen Rechner grob einordnet,\n          und gibt danach eine kleine Startempfehlung für Profil und Beschleunigung.",
        "Kurze Host-Einordnung plus kleine Startempfehlung für Profil und Beschleunigung. / Short host view plus a small starting recommendation for profile and acceleration.",
    )
    page = page.replace(
        "<h3>Host-Ansicht / Host view</h3>",
        "<h3>Host kurz / Host quick view</h3>",
    )
    page = page.replace(
        ".intro-grid,\n    .host-grid {\n      display: grid;\n      gap: 16px;\n      margin-top: 22px;",
        ".intro-grid,\n    .host-grid {\n      display: grid;\n      gap: 14px;\n      margin-top: 16px;",
    )
    page = page.replace(
        ".mini,\n    .host-box {\n      background: var(--panel-soft);\n      border: 1px solid var(--border);\n      border-radius: 14px;\n      padding: 16px;\n    }",
        ".mini,\n    .host-box {\n      background: var(--panel-soft);\n      border: 1px solid var(--border);\n      border-radius: 14px;\n      padding: 14px;\n    }",
    )
    page = page.replace(
        ".host-list {\n      display: grid;\n      gap: 10px;\n      list-style: none;\n      padding-left: 0;\n    }",
        ".host-list {\n      display: grid;\n      gap: 8px;\n      list-style: none;\n      padding-left: 0;\n    }",
    )
    page = page.replace(
        ".host-list li {\n      background: var(--panel-soft);\n      border: 1px solid var(--border);\n      border-radius: 12px;\n      padding: 11px 13px;\n      color: var(--muted);\n    }",
        ".host-list li {\n      background: var(--panel-soft);\n      border: 1px solid var(--border);\n      border-radius: 12px;\n      padding: 9px 12px;\n      color: var(--muted);\n    }",
    )
    return page


stacked.base.WizardHandler._wizard_html = _compact_html


if __name__ == "__main__":
    raise SystemExit(stacked.base.main())
