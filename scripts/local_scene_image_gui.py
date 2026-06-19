#!/usr/bin/env python3
"""Desktop GUI for the local scene image pipeline."""

from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from local_scene_image_pipeline import (
    DEFAULT_A1111_URL,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_URL,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_NEGATIVE,
    SAFETY_NEGATIVE,
    STYLE_PREFIX,
    STYLE_SUFFIX,
)


ROOT = Path(__file__).resolve().parents[1]
PIPELINE_SCRIPT = ROOT / "scripts" / "local_scene_image_pipeline.py"
SETTINGS_PATH = ROOT / "art" / "generated" / "local_scene_pipeline" / "gui_settings.json"

DEFAULT_GUIDELINES = (
    "skin-forward but non-explicit wardrobe, cinematic VN framing, expressive eye contact, "
    "consistent character identity, premium polished game CG finish"
)

FALLBACK_SAMPLERS = ["DPM++ 2M", "DPM++ 2M SDE", "Euler a", "Euler", "DDIM"]
FALLBACK_SCHEDULERS = ["Karras", "Exponential", "Polyexponential", "Automatic", "Simple", "Normal"]

TAG_TARGETS = {
    "Guidelines": "guidelines",
    "Quality / Style Prefix": "style_prefix",
    "Composition / Style Suffix": "style_suffix",
    "Base Negative Prompt": "negative_prompt",
    "Always-On Negative Prompt": "always_negative",
    "Extra Positive Prompt": "extra_positive",
    "Extra Negative Prompt": "extra_negative",
}


def fetch_json(url: str, timeout: int = 10) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def text_get(widget: tk.Text) -> str:
    return widget.get("1.0", "end").strip()


def text_set(widget: tk.Text, value: str) -> None:
    widget.configure(state="normal")
    widget.delete("1.0", "end")
    widget.insert("1.0", value)


class SceneImageGui:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sam And Em Local Scene Image Pipeline")
        self.root.geometry("1240x820")
        self.root.minsize(1080, 720)

        self.log_queue: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.process: subprocess.Popen[str] | None = None
        self.text_fields: dict[str, tk.Text] = {}

        self.llm_url = tk.StringVar(value=DEFAULT_OLLAMA_URL)
        self.llm_model = tk.StringVar(value=DEFAULT_OLLAMA_MODEL)
        self.llm_temperature = tk.StringVar(value="0.05")
        self.no_llm = tk.BooleanVar(value=False)
        self.refresh_prompt = tk.BooleanVar(value=False)

        self.a1111_url = tk.StringVar(value=DEFAULT_A1111_URL)
        self.checkpoint = tk.StringVar(value="")
        self.sampler = tk.StringVar(value="DPM++ 2M")
        self.scheduler = tk.StringVar(value="Karras")

        self.slug = tk.StringVar(value="")
        self.output_dir = tk.StringVar(value=str((ROOT / DEFAULT_OUTPUT_DIR).resolve()))
        self.width = tk.StringVar(value="1024")
        self.height = tk.StringVar(value="768")
        self.steps = tk.StringVar(value="34")
        self.cfg_scale = tk.StringVar(value="6.5")
        self.seed = tk.StringVar(value="")
        self.variants = tk.StringVar(value="1")
        self.seed_step = tk.StringVar(value="9973")
        self.init_image = tk.StringVar(value="")
        self.denoise = tk.StringVar(value="0.32")
        self.tag_target = tk.StringVar(value="Base Negative Prompt")
        self.tag_value = tk.StringVar(value="")

        self._build_ui()
        self.root.after(100, self._drain_queue)

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 6))

        prompt_tab = ttk.Frame(self.notebook)
        settings_tab = ttk.Frame(self.notebook)
        output_tab = ttk.Frame(self.notebook)
        self.notebook.add(prompt_tab, text="Prompt")
        self.notebook.add(settings_tab, text="Models and Settings")
        self.notebook.add(output_tab, text="Output")

        self._build_prompt_tab(prompt_tab)
        self._build_settings_tab(settings_tab)
        self._build_output_tab(output_tab)
        self._build_actions()

    def _build_prompt_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)

        left = ttk.Frame(parent)
        right = ttk.Frame(parent)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=4)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=4)
        left.columnconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self._add_text(left, "scene", "Scene", "", height=11, row=0)
        self._add_text(left, "guidelines", "Guidelines", DEFAULT_GUIDELINES, height=6, row=1)
        self._add_text(left, "extra_positive", "Extra Positive Prompt", "", height=5, row=2)

        self._add_text(right, "style_prefix", "Quality / Style Prefix", STYLE_PREFIX, height=6, row=0)
        self._add_text(right, "style_suffix", "Composition / Style Suffix", STYLE_SUFFIX, height=4, row=1)
        self._add_text(right, "negative_prompt", "Base Negative Prompt", DEFAULT_NEGATIVE, height=6, row=2)
        self._add_text(right, "extra_negative", "Extra Negative Prompt", "", height=3, row=3)
        self._add_text(right, "always_negative", "Always-On Negative Prompt", SAFETY_NEGATIVE, height=4, row=4)

        self._build_tag_editor(parent)

    def _build_settings_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(2, weight=1)

        llm = ttk.LabelFrame(parent, text="Ollama")
        llm.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=4)
        self._entry(llm, "URL", self.llm_url, 0)
        self.llm_model_box = self._combo(llm, "Model", self.llm_model, 1, [])
        self._entry(llm, "Temperature", self.llm_temperature, 2, width=12)
        ttk.Checkbutton(llm, text="No LLM", variable=self.no_llm).grid(row=3, column=1, sticky="w", padx=6, pady=4)
        ttk.Checkbutton(llm, text="Refresh Prompt Cache", variable=self.refresh_prompt).grid(
            row=4, column=1, sticky="w", padx=6, pady=4
        )
        ttk.Button(llm, text="Refresh LLM Models", command=self.refresh_llm_models).grid(
            row=5, column=1, sticky="w", padx=6, pady=(4, 8)
        )

        a1111 = ttk.LabelFrame(parent, text="Automatic1111")
        a1111.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=4)
        self._entry(a1111, "URL", self.a1111_url, 0)
        self.checkpoint_box = self._combo(a1111, "Checkpoint", self.checkpoint, 1, [])
        self.sampler_box = self._combo(a1111, "Sampler", self.sampler, 2, FALLBACK_SAMPLERS)
        self.scheduler_box = self._combo(a1111, "Scheduler", self.scheduler, 3, FALLBACK_SCHEDULERS)
        ttk.Button(a1111, text="Refresh A1111 Models", command=self.refresh_a1111_models).grid(
            row=4, column=1, sticky="w", padx=6, pady=(4, 8)
        )

        gen = ttk.LabelFrame(parent, text="Generation")
        gen.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(8, 4))
        for col in range(6):
            gen.columnconfigure(col, weight=1)
        self._entry(gen, "Slug", self.slug, 0, column=0, width=24)
        self._entry(gen, "Width", self.width, 0, column=2, width=10)
        self._entry(gen, "Height", self.height, 0, column=4, width=10)
        self._entry(gen, "Steps", self.steps, 1, column=0, width=10)
        self._entry(gen, "CFG Scale", self.cfg_scale, 1, column=2, width=10)
        self._entry(gen, "Seed", self.seed, 1, column=4, width=14)
        self._entry(gen, "Variants", self.variants, 2, column=0, width=10)
        self._entry(gen, "Seed Step", self.seed_step, 2, column=2, width=10)
        self._entry(gen, "Denoise", self.denoise, 2, column=4, width=10)
        self._path_entry(gen, "Output Dir", self.output_dir, 3, directory=True)
        self._path_entry(gen, "Init Image", self.init_image, 4, directory=False)

        ttk.Button(gen, text="Open Output Folder", command=self.open_output_dir).grid(
            row=5, column=1, sticky="w", padx=6, pady=(4, 8)
        )

        stored = ttk.LabelFrame(parent, text="Presets")
        stored.grid(row=2, column=0, columnspan=2, sticky="new", pady=(8, 4))
        ttk.Button(stored, text="Save Settings", command=self.save_settings).grid(row=0, column=0, padx=6, pady=8)
        ttk.Button(stored, text="Load Settings", command=self.load_settings).grid(row=0, column=1, padx=6, pady=8)
        ttk.Button(stored, text="Copy Command", command=self.copy_command).grid(row=0, column=2, padx=6, pady=8)

    def _build_output_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        self.log = ScrolledText(parent, wrap="word")
        self.log.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

    def _build_actions(self) -> None:
        actions = ttk.Frame(self.root)
        actions.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        actions.columnconfigure(0, weight=1)
        self.status = tk.StringVar(value="Ready")
        ttk.Label(actions, textvariable=self.status).grid(row=0, column=0, sticky="w")
        self.refresh_all_button = ttk.Button(actions, text="Refresh Models", command=self.refresh_all_models)
        self.refresh_all_button.grid(row=0, column=1, padx=4)
        self.dry_button = ttk.Button(actions, text="Dry Run", command=lambda: self.start_pipeline(dry_run=True))
        self.dry_button.grid(row=0, column=2, padx=4)
        self.generate_button = ttk.Button(actions, text="Generate", command=lambda: self.start_pipeline(dry_run=False))
        self.generate_button.grid(row=0, column=3, padx=4)
        self.stop_button = ttk.Button(actions, text="Stop", command=self.stop_pipeline, state="disabled")
        self.stop_button.grid(row=0, column=4, padx=4)

    def _add_text(self, parent: ttk.Frame, key: str, label: str, value: str, height: int, row: int) -> tk.Text:
        frame = ttk.LabelFrame(parent, text=label)
        frame.grid(row=row, column=0, sticky="nsew", pady=(0, 8))
        frame.columnconfigure(0, weight=1)
        widget = ScrolledText(frame, height=height, wrap="word")
        widget.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        text_set(widget, value)
        self.text_fields[key] = widget
        return widget

    def _build_tag_editor(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Tag Editor")
        frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        frame.columnconfigure(3, weight=1)
        ttk.Label(frame, text="Field").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        target = ttk.Combobox(frame, textvariable=self.tag_target, values=list(TAG_TARGETS), state="readonly", width=28)
        target.grid(row=0, column=1, sticky="w", padx=6, pady=6)
        ttk.Label(frame, text="Tag(s)").grid(row=0, column=2, sticky="w", padx=6, pady=6)
        ttk.Entry(frame, textvariable=self.tag_value).grid(row=0, column=3, sticky="ew", padx=6, pady=6)
        ttk.Button(frame, text="Add", command=self.add_tag).grid(row=0, column=4, padx=6, pady=6)
        ttk.Button(frame, text="Remove", command=self.remove_tag).grid(row=0, column=5, padx=6, pady=6)
        ttk.Button(frame, text="Sort Unique", command=self.sort_unique_tags).grid(row=0, column=6, padx=6, pady=6)

    def _entry(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        row: int,
        column: int = 0,
        width: int = 42,
    ) -> ttk.Entry:
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", padx=6, pady=4)
        entry = ttk.Entry(parent, textvariable=variable, width=width)
        entry.grid(row=row, column=column + 1, sticky="ew", padx=6, pady=4)
        parent.columnconfigure(column + 1, weight=1)
        return entry

    def _combo(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        row: int,
        values: list[str],
    ) -> ttk.Combobox:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=6, pady=4)
        combo = ttk.Combobox(parent, textvariable=variable, values=values)
        combo.grid(row=row, column=1, sticky="ew", padx=6, pady=4)
        parent.columnconfigure(1, weight=1)
        return combo

    def _path_entry(self, parent: ttk.Frame, label: str, variable: tk.StringVar, row: int, directory: bool) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=6, pady=4)
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, columnspan=4, sticky="ew", padx=6, pady=4)
        command = (lambda: self._choose_directory(variable)) if directory else (lambda: self._choose_file(variable))
        ttk.Button(parent, text="Browse", command=command).grid(row=row, column=5, sticky="e", padx=6, pady=4)

    def _choose_directory(self, variable: tk.StringVar) -> None:
        value = filedialog.askdirectory(initialdir=variable.get() or str(ROOT))
        if value:
            variable.set(value)

    def _choose_file(self, variable: tk.StringVar) -> None:
        value = filedialog.askopenfilename(
            initialdir=str(ROOT),
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")],
        )
        if value:
            variable.set(value)

    def selected_tag_widget(self) -> tk.Text:
        key = TAG_TARGETS.get(self.tag_target.get())
        if not key or key not in self.text_fields:
            raise ValueError("Choose a prompt field first.")
        return self.text_fields[key]

    def split_tags(self, value: str) -> list[str]:
        tags: list[str] = []
        seen: set[str] = set()
        for raw in value.replace("\n", ",").split(","):
            tag = " ".join(raw.strip().split())
            key = tag.casefold()
            if tag and key not in seen:
                tags.append(tag)
                seen.add(key)
        return tags

    def set_tags(self, widget: tk.Text, tags: list[str]) -> None:
        text_set(widget, ", ".join(tags))

    def add_tag(self) -> None:
        additions = self.split_tags(self.tag_value.get())
        if not additions:
            messagebox.showinfo("Tag Editor", "Type one or more comma-separated tags to add.")
            return
        try:
            widget = self.selected_tag_widget()
        except ValueError as exc:
            messagebox.showerror("Tag Editor", str(exc))
            return
        tags = self.split_tags(text_get(widget))
        seen = {tag.casefold() for tag in tags}
        for tag in additions:
            if tag.casefold() not in seen:
                tags.append(tag)
                seen.add(tag.casefold())
        self.set_tags(widget, tags)

    def remove_tag(self) -> None:
        removals = {tag.casefold() for tag in self.split_tags(self.tag_value.get())}
        if not removals:
            messagebox.showinfo("Tag Editor", "Type one or more comma-separated tags to remove.")
            return
        try:
            widget = self.selected_tag_widget()
        except ValueError as exc:
            messagebox.showerror("Tag Editor", str(exc))
            return
        tags = [tag for tag in self.split_tags(text_get(widget)) if tag.casefold() not in removals]
        self.set_tags(widget, tags)

    def sort_unique_tags(self) -> None:
        try:
            widget = self.selected_tag_widget()
        except ValueError as exc:
            messagebox.showerror("Tag Editor", str(exc))
            return
        tags = sorted(self.split_tags(text_get(widget)), key=str.casefold)
        self.set_tags(widget, tags)

    def gather_settings(self) -> dict[str, Any]:
        return {
            "scene": text_get(self.text_fields["scene"]),
            "guidelines": text_get(self.text_fields["guidelines"]),
            "style_prefix": text_get(self.text_fields["style_prefix"]),
            "style_suffix": text_get(self.text_fields["style_suffix"]),
            "negative_prompt": text_get(self.text_fields["negative_prompt"]),
            "always_negative": text_get(self.text_fields["always_negative"]),
            "extra_positive": text_get(self.text_fields["extra_positive"]),
            "extra_negative": text_get(self.text_fields["extra_negative"]),
            "llm_url": self.llm_url.get().strip(),
            "llm_model": self.llm_model.get().strip(),
            "llm_temperature": self.llm_temperature.get().strip(),
            "no_llm": self.no_llm.get(),
            "refresh_prompt": self.refresh_prompt.get(),
            "a1111_url": self.a1111_url.get().strip(),
            "checkpoint": self.checkpoint.get().strip(),
            "sampler": self.sampler.get().strip(),
            "scheduler": self.scheduler.get().strip(),
            "slug": self.slug.get().strip(),
            "output_dir": self.output_dir.get().strip(),
            "width": self.width.get().strip(),
            "height": self.height.get().strip(),
            "steps": self.steps.get().strip(),
            "cfg_scale": self.cfg_scale.get().strip(),
            "seed": self.seed.get().strip(),
            "variants": self.variants.get().strip(),
            "seed_step": self.seed_step.get().strip(),
            "init_image": self.init_image.get().strip(),
            "denoise": self.denoise.get().strip(),
        }

    def apply_settings(self, settings: dict[str, Any]) -> None:
        for key in [
            "scene",
            "guidelines",
            "style_prefix",
            "style_suffix",
            "negative_prompt",
            "always_negative",
            "extra_positive",
            "extra_negative",
        ]:
            if key in settings:
                text_set(self.text_fields[key], str(settings[key]))
        for name in [
            "llm_url",
            "llm_model",
            "llm_temperature",
            "a1111_url",
            "checkpoint",
            "sampler",
            "scheduler",
            "slug",
            "output_dir",
            "width",
            "height",
            "steps",
            "cfg_scale",
            "seed",
            "variants",
            "seed_step",
            "init_image",
            "denoise",
        ]:
            if name in settings:
                getattr(self, name).set(str(settings[name]))
        if "no_llm" in settings:
            self.no_llm.set(bool(settings["no_llm"]))
        if "refresh_prompt" in settings:
            self.refresh_prompt.set(bool(settings["refresh_prompt"]))

    def build_command(self, dry_run: bool) -> list[str]:
        settings = self.gather_settings()
        scene = settings["scene"]
        if not scene:
            raise ValueError("Add a scene before running.")
        cmd = [sys.executable, str(PIPELINE_SCRIPT), scene]
        if dry_run:
            cmd.append("--dry-run")
        if settings["slug"]:
            cmd += ["--slug", settings["slug"]]
        if settings["output_dir"]:
            cmd += ["--output-dir", settings["output_dir"]]
        if settings["refresh_prompt"]:
            cmd.append("--refresh-prompt")
        if settings["no_llm"]:
            cmd.append("--no-llm")
        else:
            cmd += ["--llm-url", settings["llm_url"]]
            cmd += ["--llm-model", settings["llm_model"]]
            cmd += ["--llm-temperature", settings["llm_temperature"]]
        cmd += ["--a1111-url", settings["a1111_url"]]
        cmd += ["--guidelines", settings["guidelines"]]
        cmd += ["--style-prefix", settings["style_prefix"]]
        cmd += ["--style-suffix", settings["style_suffix"]]
        cmd += ["--negative-prompt", settings["negative_prompt"]]
        cmd += ["--always-negative", settings["always_negative"]]
        cmd += ["--extra-positive", settings["extra_positive"]]
        cmd += ["--extra-negative", settings["extra_negative"]]
        for key, flag in [
            ("width", "--width"),
            ("height", "--height"),
            ("steps", "--steps"),
            ("cfg_scale", "--cfg-scale"),
            ("sampler", "--sampler"),
            ("scheduler", "--scheduler"),
            ("variants", "--variants"),
            ("seed_step", "--seed-step"),
        ]:
            if settings[key]:
                cmd += [flag, settings[key]]
        if settings["checkpoint"]:
            cmd += ["--checkpoint", settings["checkpoint"]]
        if settings["seed"]:
            cmd += ["--seed", settings["seed"]]
        if settings["init_image"]:
            cmd += ["--init-image", settings["init_image"]]
            cmd += ["--denoise", settings["denoise"]]
        return cmd

    def start_pipeline(self, dry_run: bool) -> None:
        if self.process and self.process.poll() is None:
            messagebox.showwarning("Pipeline Running", "Stop the current run before starting another.")
            return
        try:
            cmd = self.build_command(dry_run)
        except ValueError as exc:
            messagebox.showerror("Missing Setting", str(exc))
            return
        self._set_running(True)
        self._log("\n> " + subprocess.list2cmdline(cmd) + "\n")
        thread = threading.Thread(target=self._run_subprocess, args=(cmd,), daemon=True)
        thread.start()

    def _run_subprocess(self, cmd: list[str]) -> None:
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert self.process.stdout is not None
            for line in self.process.stdout:
                self.log_queue.put(("log", line))
            rc = self.process.wait()
            self.log_queue.put(("done", rc))
        except OSError as exc:
            self.log_queue.put(("log", f"error: {exc}\n"))
            self.log_queue.put(("done", 1))

    def stop_pipeline(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self._log("[stop] terminate requested\n")

    def _set_running(self, running: bool) -> None:
        state = "disabled" if running else "normal"
        self.refresh_all_button.configure(state=state)
        self.dry_button.configure(state=state)
        self.generate_button.configure(state=state)
        self.stop_button.configure(state="normal" if running else "disabled")
        self.status.set("Running" if running else "Ready")

    def _log(self, message: str) -> None:
        self.log.insert("end", message)
        self.log.see("end")

    def _drain_queue(self) -> None:
        try:
            while True:
                kind, payload = self.log_queue.get_nowait()
                if kind == "log":
                    self._log(str(payload))
                elif kind == "done":
                    self._log(f"[exit] {payload}\n")
                    self._set_running(False)
                    self.process = None
                elif kind == "llm_models":
                    self._apply_llm_models(payload)
                elif kind == "a1111_models":
                    self._apply_a1111_models(payload)
                elif kind == "status":
                    self.status.set(str(payload))
        except queue.Empty:
            pass
        self.root.after(100, self._drain_queue)

    def refresh_all_models(self) -> None:
        self.refresh_llm_models()
        self.refresh_a1111_models()

    def refresh_llm_models(self) -> None:
        self.status.set("Refreshing Ollama models")
        threading.Thread(target=self._fetch_llm_models, daemon=True).start()

    def _fetch_llm_models(self) -> None:
        try:
            payload = fetch_json(f"{self.llm_url.get().rstrip('/')}/api/tags")
            names = sorted(str(item["name"]) for item in payload.get("models", []) if item.get("name"))
            self.log_queue.put(("llm_models", names))
            self.log_queue.put(("status", "Ready"))
        except (OSError, KeyError, TypeError, urllib.error.URLError, json.JSONDecodeError) as exc:
            self.log_queue.put(("log", f"[ollama] {exc}\n"))
            self.log_queue.put(("status", "Ready"))

    def refresh_a1111_models(self) -> None:
        self.status.set("Refreshing A1111 models")
        threading.Thread(target=self._fetch_a1111_models, daemon=True).start()

    def _fetch_a1111_models(self) -> None:
        base = self.a1111_url.get().rstrip("/")
        data: dict[str, list[str]] = {"checkpoints": [], "samplers": FALLBACK_SAMPLERS, "schedulers": FALLBACK_SCHEDULERS}
        try:
            models = fetch_json(f"{base}/sdapi/v1/sd-models")
            data["checkpoints"] = sorted(
                str(item.get("title") or item.get("model_name"))
                for item in models
                if item.get("title") or item.get("model_name")
            )
        except (OSError, TypeError, urllib.error.URLError, json.JSONDecodeError) as exc:
            self.log_queue.put(("log", f"[a1111 models] {exc}\n"))
        try:
            samplers = fetch_json(f"{base}/sdapi/v1/samplers")
            data["samplers"] = sorted(str(item["name"]) for item in samplers if item.get("name"))
        except (OSError, TypeError, urllib.error.URLError, json.JSONDecodeError, KeyError):
            pass
        try:
            schedulers = fetch_json(f"{base}/sdapi/v1/schedulers")
            names = []
            for item in schedulers:
                if isinstance(item, dict) and (item.get("name") or item.get("label")):
                    names.append(str(item.get("name") or item.get("label")))
            if names:
                data["schedulers"] = sorted(names)
        except (OSError, TypeError, urllib.error.URLError, json.JSONDecodeError):
            pass
        self.log_queue.put(("a1111_models", data))
        self.log_queue.put(("status", "Ready"))

    def _apply_llm_models(self, names: list[str]) -> None:
        self.llm_model_box.configure(values=names)
        if names and self.llm_model.get() not in names:
            self.llm_model.set(names[0])
        self._log(f"[ollama] {len(names)} model(s)\n")

    def _apply_a1111_models(self, data: dict[str, list[str]]) -> None:
        checkpoints = data.get("checkpoints", [])
        samplers = data.get("samplers", FALLBACK_SAMPLERS)
        schedulers = data.get("schedulers", FALLBACK_SCHEDULERS)
        self.checkpoint_box.configure(values=checkpoints)
        self.sampler_box.configure(values=samplers)
        self.scheduler_box.configure(values=schedulers)
        if checkpoints and self.checkpoint.get() not in checkpoints:
            self.checkpoint.set(checkpoints[0])
        if samplers and self.sampler.get() not in samplers:
            self.sampler.set(samplers[0])
        if schedulers and self.scheduler.get() not in schedulers:
            self.scheduler.set(schedulers[0])
        self._log(f"[a1111] {len(checkpoints)} checkpoint(s), {len(samplers)} sampler(s)\n")

    def save_settings(self) -> None:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(json.dumps(self.gather_settings(), indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        self._log(f"[settings] saved {SETTINGS_PATH}\n")

    def load_settings(self) -> None:
        path = SETTINGS_PATH
        if not path.exists():
            selected = filedialog.askopenfilename(
                initialdir=str(SETTINGS_PATH.parent),
                filetypes=[("JSON", "*.json"), ("All files", "*.*")],
            )
            if not selected:
                return
            path = Path(selected)
        settings = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(settings, dict):
            messagebox.showerror("Settings Error", "Settings file must contain a JSON object.")
            return
        self.apply_settings(settings)
        self._log(f"[settings] loaded {path}\n")

    def copy_command(self) -> None:
        try:
            cmd = self.build_command(dry_run=True)
        except ValueError as exc:
            messagebox.showerror("Missing Setting", str(exc))
            return
        text = subprocess.list2cmdline(cmd)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self._log("[clipboard] copied dry-run command\n")

    def open_output_dir(self) -> None:
        path = Path(self.output_dir.get()).expanduser()
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        path.mkdir(parents=True, exist_ok=True)
        os.startfile(path)


def main() -> int:
    root = tk.Tk()
    app = SceneImageGui(root)
    try:
        app.refresh_all_models()
    except tk.TclError:
        pass
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
