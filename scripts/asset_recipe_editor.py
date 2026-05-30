import json
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECIPE = REPO_ROOT / "art" / "asset_recipe.example.json"
GENERATOR = REPO_ROOT / "scripts" / "generate_renpy_asset.py"

CHARACTERS = ("alex", "clara", "maxine")
DESTINATION_TYPES = ("sprite", "slot", "gallery", "cg", "out", "generated")
SLOTS = ("base", "underwear", "nude_front", "nude_alt")


def default_recipe():
    return {
        "defaults": {
            "api": "http://127.0.0.1:7860",
            "width": 1024,
            "height": 1536,
            "steps": 28,
            "cfg_scale": 7.0,
            "denoise": 0.55,
            "sampler": "DPM++ 2M Karras",
            "timeout": 600,
            "no_backup": False,
        },
        "jobs": [],
    }


class RecipeEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sam And Em Asset Recipe Editor")
        self.geometry("1040x720")
        self.minsize(920, 620)

        self.recipe_path = tk.StringVar(value=str(DEFAULT_RECIPE))
        self.recipe = default_recipe()
        self.selected_index = None
        self._build_ui()
        if DEFAULT_RECIPE.exists():
            self._load_path(DEFAULT_RECIPE)
        else:
            self._refresh_jobs()
            self._load_defaults()

    def _build_ui(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)

        path_row = ttk.Frame(root)
        path_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        path_row.columnconfigure(1, weight=1)
        ttk.Label(path_row, text="Recipe").grid(row=0, column=0, sticky="w")
        ttk.Entry(path_row, textvariable=self.recipe_path).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(path_row, text="Open", command=self.open_recipe).grid(row=0, column=2)
        ttk.Button(path_row, text="Save", command=self.save_recipe).grid(row=0, column=3, padx=(8, 0))
        ttk.Button(path_row, text="Save As", command=self.save_recipe_as).grid(row=0, column=4, padx=(8, 0))

        left = ttk.Frame(root)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        left.rowconfigure(0, weight=1)

        self.jobs_list = tk.Listbox(left, width=34, height=20)
        self.jobs_list.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.jobs_list.bind("<<ListboxSelect>>", self.select_job)
        ttk.Button(left, text="Add", command=self.add_job).grid(row=1, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(left, text="Duplicate", command=self.duplicate_job).grid(row=1, column=1, sticky="ew", pady=(8, 0), padx=4)
        ttk.Button(left, text="Delete", command=self.delete_job).grid(row=1, column=2, sticky="ew", pady=(8, 0))
        ttk.Button(left, text="Dry Run", command=self.dry_run).grid(row=1, column=3, sticky="ew", pady=(8, 0), padx=(4, 0))

        right = ttk.Notebook(root)
        right.grid(row=1, column=1, sticky="nsew")

        job_tab = ttk.Frame(right, padding=12)
        defaults_tab = ttk.Frame(right, padding=12)
        raw_tab = ttk.Frame(right, padding=12)
        right.add(job_tab, text="Job")
        right.add(defaults_tab, text="Defaults")
        right.add(raw_tab, text="Raw JSON")

        self._build_job_tab(job_tab)
        self._build_defaults_tab(defaults_tab)
        self._build_raw_tab(raw_tab)

    def _build_job_tab(self, parent):
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(5, weight=1)

        self.job_character = tk.StringVar(value="maxine")
        self.job_destination_type = tk.StringVar(value="sprite")
        self.job_destination_id = tk.StringVar(value="maxine_new")
        self.job_reference = tk.StringVar()
        self.job_negative = tk.StringVar()
        self.job_denoise = tk.StringVar()

        ttk.Label(parent, text="Character").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Combobox(parent, textvariable=self.job_character, values=CHARACTERS, state="readonly").grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(parent, text="Destination").grid(row=1, column=0, sticky="w", pady=4)
        destination_row = ttk.Frame(parent)
        destination_row.grid(row=1, column=1, sticky="ew", pady=4)
        destination_row.columnconfigure(1, weight=1)
        ttk.Combobox(destination_row, textvariable=self.job_destination_type, values=DESTINATION_TYPES, state="readonly", width=14).grid(row=0, column=0, sticky="w")
        ttk.Entry(destination_row, textvariable=self.job_destination_id).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Combobox(destination_row, textvariable=self.job_destination_id, values=SLOTS, width=14).grid(row=0, column=2, sticky="e")

        ttk.Label(parent, text="Reference").grid(row=2, column=0, sticky="w", pady=4)
        reference_row = ttk.Frame(parent)
        reference_row.grid(row=2, column=1, sticky="ew", pady=4)
        reference_row.columnconfigure(0, weight=1)
        ttk.Entry(reference_row, textvariable=self.job_reference).grid(row=0, column=0, sticky="ew")
        ttk.Button(reference_row, text="Browse", command=self.browse_reference).grid(row=0, column=1, padx=(8, 0))

        ttk.Label(parent, text="Denoise").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(parent, textvariable=self.job_denoise).grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(parent, text="Negative").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(parent, textvariable=self.job_negative).grid(row=4, column=1, sticky="ew", pady=4)

        ttk.Label(parent, text="Prompt").grid(row=5, column=0, sticky="nw", pady=4)
        self.job_prompt = tk.Text(parent, height=12, wrap="word")
        self.job_prompt.grid(row=5, column=1, sticky="nsew", pady=4)

        action_row = ttk.Frame(parent)
        action_row.grid(row=6, column=1, sticky="e", pady=(8, 0))
        ttk.Button(action_row, text="Apply Job", command=self.apply_job).pack(side="right")

    def _build_defaults_tab(self, parent):
        parent.columnconfigure(1, weight=1)
        self.default_vars = {}
        fields = ["api", "width", "height", "steps", "cfg_scale", "denoise", "sampler", "timeout", "no_backup"]
        for row, field in enumerate(fields):
            ttk.Label(parent, text=field).grid(row=row, column=0, sticky="w", pady=4)
            var = tk.StringVar()
            self.default_vars[field] = var
            ttk.Entry(parent, textvariable=var).grid(row=row, column=1, sticky="ew", pady=4)
        ttk.Button(parent, text="Apply Defaults", command=self.apply_defaults).grid(row=len(fields), column=1, sticky="e", pady=(10, 0))

    def _build_raw_tab(self, parent):
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        self.raw_text = tk.Text(parent, wrap="none")
        self.raw_text.grid(row=0, column=0, sticky="nsew")
        buttons = ttk.Frame(parent)
        buttons.grid(row=1, column=0, sticky="e", pady=(8, 0))
        ttk.Button(buttons, text="Refresh Raw", command=self.refresh_raw).pack(side="right")
        ttk.Button(buttons, text="Apply Raw", command=self.apply_raw).pack(side="right", padx=(0, 8))

    def open_recipe(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("All files", "*.*")])
        if path:
            self._load_path(Path(path))

    def _load_path(self, path):
        try:
            self.recipe = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception as exc:
            messagebox.showerror("Open failed", str(exc))
            return
        self.recipe_path.set(str(path))
        self.selected_index = None
        self._load_defaults()
        self._refresh_jobs()
        self.refresh_raw()

    def save_recipe(self):
        self.apply_defaults()
        self.apply_job(silent=True)
        path = Path(self.recipe_path.get())
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self.recipe, indent=2) + "\n", encoding="utf-8")
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc))
            return
        self.refresh_raw()
        messagebox.showinfo("Saved", str(path))

    def save_recipe_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json"), ("All files", "*.*")])
        if path:
            self.recipe_path.set(path)
            self.save_recipe()

    def _load_defaults(self):
        defaults = self.recipe.setdefault("defaults", {})
        for key, var in self.default_vars.items():
            var.set(str(defaults.get(key, "")))

    def apply_defaults(self):
        defaults = {}
        for key, var in self.default_vars.items():
            value = var.get().strip()
            if value == "":
                continue
            defaults[key] = parse_value(value)
        self.recipe["defaults"] = defaults
        self.refresh_raw()

    def _refresh_jobs(self):
        self.jobs_list.delete(0, tk.END)
        for index, job in enumerate(self.recipe.setdefault("jobs", []), start=1):
            destination = job.get("destination", {})
            label = f"{index}. {job.get('character', '?')} -> {destination.get('type', 'generated')}:{destination.get('id', '')}"
            self.jobs_list.insert(tk.END, label)

    def select_job(self, _event=None):
        selection = self.jobs_list.curselection()
        if not selection:
            return
        self.selected_index = selection[0]
        job = self.recipe["jobs"][self.selected_index]
        destination = job.get("destination", {})
        self.job_character.set(job.get("character", "maxine"))
        self.job_destination_type.set(destination.get("type", "sprite"))
        self.job_destination_id.set(destination.get("id", ""))
        self.job_reference.set(job.get("reference", ""))
        self.job_negative.set(job.get("negative", ""))
        self.job_denoise.set(str(job.get("denoise", "")))
        self.job_prompt.delete("1.0", tk.END)
        self.job_prompt.insert(tk.END, job.get("prompt", ""))

    def add_job(self):
        self.recipe.setdefault("jobs", []).append(
            {
                "character": "maxine",
                "prompt": "covered sprite variant, confident pose",
                "destination": {"type": "sprite", "id": "maxine_new"},
            }
        )
        self._refresh_jobs()
        self.jobs_list.selection_clear(0, tk.END)
        self.jobs_list.selection_set(tk.END)
        self.select_job()

    def duplicate_job(self):
        if self.selected_index is None:
            return
        job = json.loads(json.dumps(self.recipe["jobs"][self.selected_index]))
        self.recipe["jobs"].insert(self.selected_index + 1, job)
        self._refresh_jobs()

    def delete_job(self):
        if self.selected_index is None:
            return
        del self.recipe["jobs"][self.selected_index]
        self.selected_index = None
        self._refresh_jobs()
        self.refresh_raw()

    def apply_job(self, silent=False):
        if self.selected_index is None:
            return
        job = {
            "character": self.job_character.get(),
            "prompt": self.job_prompt.get("1.0", tk.END).strip(),
            "destination": {
                "type": self.job_destination_type.get(),
                "id": self.job_destination_id.get().strip(),
            },
        }
        if self.job_reference.get().strip():
            job["reference"] = self.job_reference.get().strip()
        if self.job_negative.get().strip():
            job["negative"] = self.job_negative.get().strip()
        if self.job_denoise.get().strip():
            job["denoise"] = parse_value(self.job_denoise.get().strip())
        self.recipe["jobs"][self.selected_index] = job
        self._refresh_jobs()
        self.refresh_raw()
        if not silent:
            messagebox.showinfo("Applied", "Job updated.")

    def browse_reference(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")])
        if path:
            self.job_reference.set(path)

    def refresh_raw(self):
        self.raw_text.delete("1.0", tk.END)
        self.raw_text.insert(tk.END, json.dumps(self.recipe, indent=2))

    def apply_raw(self):
        try:
            self.recipe = json.loads(self.raw_text.get("1.0", tk.END))
        except Exception as exc:
            messagebox.showerror("Invalid JSON", str(exc))
            return
        self._load_defaults()
        self._refresh_jobs()

    def dry_run(self):
        self.save_recipe()
        command = [sys.executable, str(GENERATOR), "--recipe", self.recipe_path.get(), "--dry-run"]
        try:
            result = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)
        except Exception as exc:
            messagebox.showerror("Dry run failed", str(exc))
            return
        output = result.stdout if result.returncode == 0 else result.stderr
        show_text_window(self, "Dry Run", output)


def parse_value(value):
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def show_text_window(parent, title, text):
    window = tk.Toplevel(parent)
    window.title(title)
    window.geometry("900x560")
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)
    output = tk.Text(window, wrap="word")
    output.grid(row=0, column=0, sticky="nsew")
    output.insert(tk.END, text)


def main():
    app = RecipeEditor()
    app.mainloop()


if __name__ == "__main__":
    main()
