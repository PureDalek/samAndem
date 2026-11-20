import argparse
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from a1111_character_prompts import (
    REPO_ROOT,
    VARIANTS,
    build_img2img_payload,
    build_prompt,
    load_identities,
    post_json,
    save_response_images,
)
from import_character_assets import ASSET_ROOT, CHARACTERS, SLOTS, import_asset, validate_source


CHARACTER_OPTIONS = sorted(CHARACTERS)
SLOT_OPTIONS = list(SLOTS)


class CharacterAssetManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sam And Em Asset Manager")
        self.geometry("900x640")
        self.minsize(760, 520)
        self.identities = load_identities()
        self._build_ui()

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=12)

        import_frame = ttk.Frame(notebook, padding=12)
        prompt_frame = ttk.Frame(notebook, padding=12)
        notebook.add(import_frame, text="Import Assets")
        notebook.add(prompt_frame, text="Safe A1111 Prompts")

        self._build_import_tab(import_frame)
        self._build_prompt_tab(prompt_frame)

    def _build_import_tab(self, parent):
        parent.columnconfigure(1, weight=1)

        ttk.Label(parent, text="Character").grid(row=0, column=0, sticky="w", pady=4)
        self.import_character = tk.StringVar(value=CHARACTER_OPTIONS[0])
        ttk.Combobox(parent, textvariable=self.import_character, values=CHARACTER_OPTIONS, state="readonly").grid(
            row=0, column=1, sticky="ew", pady=4
        )

        ttk.Label(parent, text="Slot").grid(row=1, column=0, sticky="w", pady=4)
        self.import_slot = tk.StringVar(value="nude_front")
        ttk.Combobox(parent, textvariable=self.import_slot, values=SLOT_OPTIONS, state="readonly").grid(
            row=1, column=1, sticky="ew", pady=4
        )

        ttk.Label(parent, text="Source image").grid(row=2, column=0, sticky="w", pady=4)
        self.source_path = tk.StringVar()
        source_entry = ttk.Entry(parent, textvariable=self.source_path)
        source_entry.grid(row=2, column=1, sticky="ew", pady=4)
        ttk.Button(parent, text="Browse", command=self._browse_source).grid(row=2, column=2, padx=(8, 0), pady=4)

        self.backup_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Back up replaced file", variable=self.backup_enabled).grid(
            row=3, column=1, sticky="w", pady=4
        )

        action_row = ttk.Frame(parent)
        action_row.grid(row=4, column=1, sticky="w", pady=12)
        ttk.Button(action_row, text="Import", command=self._import_selected_asset).pack(side="left")
        ttk.Button(action_row, text="Open Target Folder", command=self._open_target_folder).pack(side="left", padx=8)

        self.import_status = tk.StringVar(value=f"Target root: {ASSET_ROOT}")
        ttk.Label(parent, textvariable=self.import_status, wraplength=760).grid(
            row=5, column=0, columnspan=3, sticky="w", pady=8
        )

    def _build_prompt_tab(self, parent):
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(7, weight=1)

        ttk.Label(parent, text="Character").grid(row=0, column=0, sticky="w", pady=4)
        self.prompt_character = tk.StringVar(value=CHARACTER_OPTIONS[0])
        ttk.Combobox(parent, textvariable=self.prompt_character, values=CHARACTER_OPTIONS, state="readonly").grid(
            row=0, column=1, sticky="ew", pady=4
        )

        ttk.Label(parent, text="Variant").grid(row=1, column=0, sticky="w", pady=4)
        self.prompt_variant = tk.StringVar(value="underwear")
        ttk.Combobox(parent, textvariable=self.prompt_variant, values=sorted(VARIANTS), state="readonly").grid(
            row=1, column=1, sticky="ew", pady=4
        )

        self.api_url = tk.StringVar(value="http://127.0.0.1:7860")
        ttk.Label(parent, text="A1111 API").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(parent, textvariable=self.api_url).grid(row=2, column=1, sticky="ew", pady=4)

        settings = ttk.Frame(parent)
        settings.grid(row=3, column=1, sticky="ew", pady=4)
        self.width = tk.IntVar(value=1024)
        self.height = tk.IntVar(value=1536)
        self.steps = tk.IntVar(value=28)
        self.cfg_scale = tk.DoubleVar(value=7.0)
        self.denoise = tk.DoubleVar(value=0.35)
        self._number_entry(settings, "Width", self.width, 0)
        self._number_entry(settings, "Height", self.height, 1)
        self._number_entry(settings, "Steps", self.steps, 2)
        self._number_entry(settings, "CFG", self.cfg_scale, 3)
        self._number_entry(settings, "Denoise", self.denoise, 4)

        action_row = ttk.Frame(parent)
        action_row.grid(row=4, column=1, sticky="w", pady=12)
        ttk.Button(action_row, text="Build Prompt", command=self._build_explicit_prompt).pack(side="left")
        ttk.Button(action_row, text="Copy Prompt", command=self._copy_prompt).pack(side="left", padx=8)
        ttk.Button(action_row, text="Generate Variant", command=self._generate_explicit_variant).pack(side="left")

        self.prompt_status = tk.StringVar(value="Generated images save to art/generated.")
        ttk.Label(parent, textvariable=self.prompt_status, wraplength=760).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=4
        )

        ttk.Label(parent, text="Prompt output").grid(row=6, column=0, sticky="nw", pady=4)
        self.prompt_text = tk.Text(parent, height=16, wrap="word")
        self.prompt_text.grid(row=7, column=0, columnspan=2, sticky="nsew", pady=4)

    def _number_entry(self, parent, label, variable, column):
        frame = ttk.Frame(parent)
        frame.grid(row=0, column=column, padx=(0, 8))
        ttk.Label(frame, text=label).pack(anchor="w")
        ttk.Entry(frame, textvariable=variable, width=8).pack(anchor="w")

    def _browse_source(self):
        path = filedialog.askopenfilename(
            title="Choose image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")],
        )
        if path:
            self.source_path.set(path)

    def _import_selected_asset(self):
        try:
            source = validate_source(self.source_path.get())
            destination, backup_path = import_asset(
                source,
                self.import_character.get(),
                self.import_slot.get(),
                no_backup=not self.backup_enabled.get(),
            )
        except SystemExit as exc:
            messagebox.showerror("Import failed", str(exc))
            return

        status = f"Imported to {destination}"
        if backup_path:
            status += f"\nBackup saved to {backup_path}"
        self.import_status.set(status)
        messagebox.showinfo("Import complete", status)

    def _open_target_folder(self):
        folder = ASSET_ROOT / self.import_character.get()
        folder.mkdir(parents=True, exist_ok=True)
        try:
            import os

            os.startfile(folder)
        except OSError as exc:
            messagebox.showerror("Open folder failed", str(exc))

    def _build_explicit_prompt(self):
        prompt, negative = build_prompt(self.prompt_character.get(), self.prompt_variant.get(), self.identities)
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert(tk.END, f"PROMPT:\n{prompt}\n\nNEGATIVE PROMPT:\n{negative}\n")
        self.prompt_status.set("18+ prompt built from the character identity bank using the chosen variant.")

    def _copy_prompt(self):
        text = self.prompt_text.get("1.0", tk.END).strip()
        if not text:
            self._build_explicit_prompt()
            text = self.prompt_text.get("1.0", tk.END).strip()
        self.clipboard_clear()
        self.clipboard_append(text)
        self.prompt_status.set("Prompt copied to clipboard.")

    def _generate_explicit_variant(self):
        character = self.prompt_character.get()
        variant = self.prompt_variant.get()
        try:
            payload = build_img2img_payload(
                character,
                variant,
                self.identities,
                self.width.get(),
                self.height.get(),
                self.steps.get(),
                self.cfg_scale.get(),
                self.denoise.get(),
            )
            response = post_json(f"{self.api_url.get().rstrip('/')}/sdapi/v1/img2img", payload)
            saved = save_response_images(response, REPO_ROOT / "art" / "generated", character, variant)
        except Exception as exc:
            messagebox.showerror("Generation failed", str(exc))
            return

        self.prompt_status.set("Saved: " + ", ".join(str(path) for path in saved))
        messagebox.showinfo("Generation complete", "\n".join(str(path) for path in saved))


def main():
    parser = argparse.ArgumentParser(description="Open the Sam And Em local character asset manager.")
    parser.add_argument("--print-config", action="store_true", help="Print paths and exit without opening the GUI.")
    args = parser.parse_args()

    if args.print_config:
        print(f"repo_root={REPO_ROOT}")
        print(f"asset_root={ASSET_ROOT}")
        print(f"characters={','.join(CHARACTER_OPTIONS)}")
        print(f"slots={','.join(SLOT_OPTIONS)}")
        return 0

    app = CharacterAssetManager()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
