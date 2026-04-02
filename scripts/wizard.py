#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import webbrowser
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


def _can_use_tk(info: dict) -> bool:
    if not info.get("supports_gui"):
        return False
    try:
        import tkinter  # noqa: F401
        return True
    except Exception:
        return False


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

    print("\nToF Local Builder – Erstsetup\n")
    print("Dieser Wizard richtet den Builder einmal lokal ein und übergibt danach an die Web-Oberfläche.\n")
    print("Erkannter Host:")
    for line in host_summary_lines(info):
        print(f"- {line}")
    print()

    while True:
        prompt = f"Quellpfad [{current_source}]: " if current_source else "Quellpfad: "
        value = input(prompt).strip() or current_source
        value = normalize_source_path(value)
        if source_path_valid(value):
            source_path = value
            break
        print("Pfad ungültig oder nicht vorhanden. Bitte einen existierenden Ordner angeben.\n")

    print("\nModelloptionen:")
    for index, option in enumerate(MODEL_OPTIONS, start=1):
        print(f"  {index}. {option}")
    while True:
        choice = input(f"Standardmodell [{current_model}]: ").strip()
        if not choice:
            model = current_model
            break
        if choice.isdigit() and 1 <= int(choice) <= len(MODEL_OPTIONS):
            selected = MODEL_OPTIONS[int(choice) - 1]
            if selected == "custom":
                custom = input("Eigenen Modellnamen eingeben: ").strip()
                if custom:
                    model = custom
                    break
            else:
                model = selected
                break
        elif choice:
            model = choice
            break
        print("Ungültige Auswahl.\n")

    acceleration_options = recommended_acceleration_options(info)
    print("\nBeschleunigungsoptionen:")
    for index, option in enumerate(acceleration_options, start=1):
        print(f"  {index}. {option}")
    while True:
        choice = input(f"Beschleunigung [{current_acceleration}]: ").strip()
        if not choice:
            acceleration = current_acceleration
            break
        if choice.isdigit() and 1 <= int(choice) <= len(acceleration_options):
            acceleration = acceleration_options[int(choice) - 1]
            break
        if choice in acceleration_options:
            acceleration = choice
            break
        print("Ungültige Auswahl.\n")

    browser_raw = input(f"Browser nach dem Start öffnen [{'J' if current_browser else 'N'}]: ").strip().lower()
    open_browser = current_browser if not browser_raw else browser_raw in {"j", "ja", "y", "yes", "1"}

    merged = apply_setup_values(
        env,
        source_repo_path=source_path,
        default_model=model,
        acceleration=acceleration,
        open_browser=open_browser,
    )
    write_env_file(env_path, merged, order)

    print("\nSetup gespeichert.")
    print(f"- SOURCE_REPO_PATH={merged['SOURCE_REPO_PATH']}")
    print(f"- DEFAULT_OLLAMA_MODEL={merged['DEFAULT_OLLAMA_MODEL']}")
    print(f"- BUILDER_ACCELERATION={merged['BUILDER_ACCELERATION']}")
    print(f"- BUILDER_OPEN_BROWSER={merged['BUILDER_OPEN_BROWSER']}")
    print()
    return 0


def run_tk_wizard(env_path: Path, env: dict, order: list[str], info: dict) -> int:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    class WizardApp:
        def __init__(self) -> None:
            self.root = tk.Tk()
            self.root.title("ToF Local Builder Setup")
            self.root.geometry("760x560")
            self.root.resizable(False, False)

            self.source_var = tk.StringVar(value=env.get("SOURCE_REPO_PATH", "") if source_path_valid(env.get("SOURCE_REPO_PATH", "")) else "")
            self.model_var = tk.StringVar(value=env.get("DEFAULT_OLLAMA_MODEL", info["recommended_model"]))
            self.custom_model_var = tk.StringVar("")
            self.acceleration_var = tk.StringVar(value=env.get("BUILDER_ACCELERATION", info["recommended_acceleration"]))
            self.open_browser_var = tk.BooleanVar(value=env.get("BUILDER_OPEN_BROWSER", "1") == "1")

            self.acceleration_options = recommended_acceleration_options(info)
            if self.acceleration_var.get() not in self.acceleration_options:
                self.acceleration_var.set(info["recommended_acceleration"])
            if self.model_var.get() not in MODEL_OPTIONS:
                self.custom_model_var.set(self.model_var.get())
                self.model_var.set("custom")

            self.page_index = 0
            self.pages: list[ttk.Frame] = []

            outer = ttk.Frame(self.root, padding=16)
            outer.pack(fill="both", expand=True)

            self.title_var = tk.StringVar()
            ttk.Label(outer, textvariable=self.title_var, font=("TkDefaultFont", 14, "bold")).pack(anchor="w")
            ttk.Label(
                outer,
                text="Einmaliger Setup-Wizard für den lokalen Builder. Danach geht es direkt auf die Web-Oberfläche.",
                wraplength=720,
            ).pack(anchor="w", pady=(6, 12))

            self.content = ttk.Frame(outer)
            self.content.pack(fill="both", expand=True)

            nav = ttk.Frame(outer)
            nav.pack(fill="x", pady=(12, 0))
            self.back_button = ttk.Button(nav, text="Zurück", command=self.back)
            self.back_button.pack(side="left")
            self.next_button = ttk.Button(nav, text="Weiter", command=self.next)
            self.next_button.pack(side="right")
            self.finish_button = ttk.Button(nav, text="Einrichtung speichern", command=self.finish)
            self.finish_button.pack(side="right", padx=(0, 8))

            self.review_text: tk.Text | None = None
            self.custom_model_entry: ttk.Entry | None = None

            self._build_pages()
            self.show_page(0)

        def _build_pages(self) -> None:
            self.pages = [self._page_welcome(), self._page_source(), self._page_runtime(), self._page_review()]

        def _page_welcome(self) -> ttk.Frame:
            frame = ttk.Frame(self.content)
            ttk.Label(
                frame,
                text="Willkommen. Der Wizard richtet Quelle, Modell und Beschleunigungsmodus ein und schreibt danach die .env für den Builder.",
                wraplength=700,
                justify="left",
            ).pack(anchor="w")
            summary = tk.Text(frame, height=14, wrap="word")
            summary.pack(fill="both", expand=True, pady=(14, 0))
            summary.insert("1.0", "\n".join(host_summary_lines(info)))
            summary.configure(state="disabled")
            return frame

        def _page_source(self) -> ttk.Frame:
            frame = ttk.Frame(self.content)
            ttk.Label(frame, text="Schritt 1 – Quellpfad wählen", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
            ttk.Label(
                frame,
                text="Der Builder liest diese Quelle nur read-only. Ausgaben landen weiter nur in der Sandbox.",
                wraplength=700,
            ).pack(anchor="w", pady=(8, 16))
            row = ttk.Frame(frame)
            row.pack(fill="x")
            entry = ttk.Entry(row, textvariable=self.source_var)
            entry.pack(side="left", fill="x", expand=True)
            ttk.Button(row, text="Ordner wählen", command=self.choose_source).pack(side="left", padx=(8, 0))
            ttk.Label(
                frame,
                text="Beispiel: ein lokales Arbeitsrepo oder ein read-only aufbereiteter Quellordner.",
                wraplength=700,
            ).pack(anchor="w", pady=(16, 0))
            return frame

        def _page_runtime(self) -> ttk.Frame:
            frame = ttk.Frame(self.content)
            ttk.Label(frame, text="Schritt 2 – Standardlaufzeit wählen", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
            ttk.Label(frame, text="Der Standard bleibt klein und einsteigerfreundlich.", wraplength=700).pack(anchor="w", pady=(8, 16))

            ttk.Label(frame, text="Standardmodell").pack(anchor="w")
            model_box = ttk.Combobox(frame, textvariable=self.model_var, values=MODEL_OPTIONS, state="readonly")
            model_box.pack(anchor="w", fill="x")
            model_box.bind("<<ComboboxSelected>>", lambda _event: self.update_custom_model_state())

            ttk.Label(frame, text="Eigenes Modell", padding=(0, 16, 0, 0)).pack(anchor="w")
            self.custom_model_entry = ttk.Entry(frame, textvariable=self.custom_model_var)
            self.custom_model_entry.pack(anchor="w", fill="x")

            ttk.Label(frame, text="Beschleunigungsmodus", padding=(0, 16, 0, 0)).pack(anchor="w")
            ttk.Combobox(frame, textvariable=self.acceleration_var, values=self.acceleration_options, state="readonly").pack(anchor="w", fill="x")

            ttk.Checkbutton(frame, text="Web-Oberfläche nach dem Start automatisch im Browser öffnen", variable=self.open_browser_var).pack(anchor="w", pady=(16, 0))

            host_note = tk.Text(frame, height=7, wrap="word")
            host_note.pack(fill="both", expand=True, pady=(16, 0))
            host_note.insert(
                "1.0",
                "\n".join(
                    [
                        f"Empfehlung dieses Hosts: {info['recommended_acceleration']}",
                        f"Empfohlenes Startmodell: {info['recommended_model']}",
                        "Tipp: stärkere Geräte können später in der .env auf größere Modelle wechseln.",
                    ]
                ),
            )
            host_note.configure(state="disabled")
            self.update_custom_model_state()
            return frame

        def _page_review(self) -> ttk.Frame:
            frame = ttk.Frame(self.content)
            ttk.Label(frame, text="Schritt 3 – Zusammenfassung", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
            ttk.Label(
                frame,
                text="Wenn du speicherst, schreibt der Wizard die .env. Danach startet der normale Builder-Pfad weiter.",
                wraplength=700,
            ).pack(anchor="w", pady=(8, 16))
            self.review_text = tk.Text(frame, height=18, wrap="word")
            self.review_text.pack(fill="both", expand=True)
            return frame

        def choose_source(self) -> None:
            selected = filedialog.askdirectory(title="Quellordner wählen")
            if selected:
                self.source_var.set(normalize_source_path(selected))

        def update_custom_model_state(self) -> None:
            if not self.custom_model_entry:
                return
            if self.model_var.get() == "custom":
                self.custom_model_entry.configure(state="normal")
            else:
                self.custom_model_entry.configure(state="disabled")
                self.custom_model_var.set("")

        def current_model(self) -> str:
            if self.model_var.get() == "custom":
                return self.custom_model_var.get().strip()
            return self.model_var.get().strip()

        def validate_current_page(self) -> bool:
            if self.page_index == 1:
                candidate = normalize_source_path(self.source_var.get())
                if not source_path_valid(candidate):
                    messagebox.showerror("Ungültiger Pfad", "Bitte einen existierenden Quellordner auswählen.")
                    return False
                self.source_var.set(candidate)
            if self.page_index == 2:
                if not self.current_model():
                    messagebox.showerror("Modell fehlt", "Bitte ein Standardmodell auswählen oder einen eigenen Modellnamen eingeben.")
                    return False
            return True

        def refresh_review(self) -> None:
            if not self.review_text:
                return
            model = self.current_model() or info["recommended_model"]
            content = [
                "Builder-Zusammenfassung",
                "",
                f"SOURCE_REPO_PATH={normalize_source_path(self.source_var.get())}",
                f"DEFAULT_OLLAMA_MODEL={model}",
                f"BUILDER_ACCELERATION={self.acceleration_var.get()}",
                f"BUILDER_OPEN_BROWSER={'1' if self.open_browser_var.get() else '0'}",
                "",
                "Host-Erkennung:",
                *host_summary_lines(info),
                "",
                "Hinweis: Nach dem Speichern startet der normale Builder weiter und verweist danach auf die Web-Oberfläche.",
            ]
            self.review_text.configure(state="normal")
            self.review_text.delete("1.0", "end")
            self.review_text.insert("1.0", "\n".join(content))
            self.review_text.configure(state="disabled")

        def show_page(self, index: int) -> None:
            self.page_index = index
            titles = [
                "Willkommen",
                "Quelle auswählen",
                "Laufzeit festlegen",
                "Zusammenfassung",
            ]
            self.title_var.set(titles[index])
            for child in self.content.winfo_children():
                child.pack_forget()
            self.pages[index].pack(fill="both", expand=True)
            self.back_button.configure(state="normal" if index > 0 else "disabled")
            self.next_button.configure(state="normal" if index < len(self.pages) - 1 else "disabled")
            self.finish_button.configure(state="normal" if index == len(self.pages) - 1 else "disabled")
            if index == len(self.pages) - 1:
                self.refresh_review()

        def next(self) -> None:
            if not self.validate_current_page():
                return
            self.show_page(min(self.page_index + 1, len(self.pages) - 1))

        def back(self) -> None:
            self.show_page(max(self.page_index - 1, 0))

        def finish(self) -> None:
            if not self.validate_current_page():
                return
            merged = apply_setup_values(
                env,
                source_repo_path=self.source_var.get(),
                default_model=self.current_model(),
                acceleration=self.acceleration_var.get(),
                open_browser=self.open_browser_var.get(),
            )
            write_env_file(env_path, merged, order)
            messagebox.showinfo("Setup gespeichert", "Die lokale Einrichtung wurde gespeichert. Jetzt läuft der normale Builder-Start weiter.")
            self.root.destroy()

        def run(self) -> int:
            self.root.mainloop()
            return 0

    return WizardApp().run()


def ensure_wizard(force: bool = False) -> int:
    env_path = get_default_env_path()
    env, order = parse_env_file(env_path)
    env = merge_env(env)
    info = detect_host()
    if not force and not needs_first_run_wizard(env):
        return 0
    if _can_use_tk(info):
        return run_tk_wizard(env_path, env, order, info)
    return run_console_wizard(env_path, env, order, info)


def main() -> int:
    parser = argparse.ArgumentParser(description="ToF Local Builder setup wizard")
    parser.add_argument("--ensure", action="store_true", help="run the wizard only when setup is incomplete")
    parser.add_argument("--force", action="store_true", help="force the wizard to run")
    parser.add_argument("--open-webui", action="store_true", help="open the local WebUI in the default browser")
    args = parser.parse_args()

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
