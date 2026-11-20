#!/usr/bin/env python3
"""Import user-supplied explicit 18+ story CGs into Ren'Py CG slots.

This helper does not generate, edit, upscale, describe, or inspect sexual
content. It only performs file handling for a finished user-supplied 18+ image:
slot mapping, optional resize/crop, backup, and PNG save.

All imported images must depict fictional adults aged 18 or older. Aliases
match the canonical CG keys (`c1`, `c2m`, `e1`, etc.) and a short legible form
(`gala`, `vow`, `compartment`, ...). The on-disk CG assets still carry the
original `_private_` wording in their filenames because those files are
committed; only the *alias keys* were tidied up so the user-facing CLI no
longer hands out euphemistic names.
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover - depends on local runtime packages.
    Image = None


TARGET_SIZE = (1024, 768)

CG_SLOTS: dict[str, Path] = {
    "b2": Path("game/images/nsfw/cg/cg_b2_maxine_almost_date.png"),
    "almost_date": Path("game/images/nsfw/cg/cg_b2_maxine_almost_date.png"),
    "cg_b2": Path("game/images/nsfw/cg/cg_b2_maxine_almost_date.png"),
    "c1": Path("game/images/nsfw/cg/cg_c1_gala_private_balcony.png"),
    "gala": Path("game/images/nsfw/cg/cg_c1_gala_private_balcony.png"),
    "cg_c1": Path("game/images/nsfw/cg/cg_c1_gala_private_balcony.png"),
    "c2j": Path("game/images/nsfw/cg/cg_c2j_lady_no_questions.png"),
    "no_questions": Path("game/images/nsfw/cg/cg_c2j_lady_no_questions.png"),
    "cg_c2j": Path("game/images/nsfw/cg/cg_c2j_lady_no_questions.png"),
    "c2l": Path("game/images/nsfw/cg/cg_c2l_lady_real_name.png"),
    "real_name": Path("game/images/nsfw/cg/cg_c2l_lady_real_name.png"),
    "cg_c2l": Path("game/images/nsfw/cg/cg_c2l_lady_real_name.png"),
    "c2m": Path("game/images/nsfw/cg/cg_c2m_maxine_last_lie.png"),
    "last_lie": Path("game/images/nsfw/cg/cg_c2m_maxine_last_lie.png"),
    "cg_c2m": Path("game/images/nsfw/cg/cg_c2m_maxine_last_lie.png"),
    "e1": Path("game/images/nsfw/cg/cg_e1_wedding_garden_private_vow.png"),
    "vow": Path("game/images/nsfw/cg/cg_e1_wedding_garden_private_vow.png"),
    "cg_e1": Path("game/images/nsfw/cg/cg_e1_wedding_garden_private_vow.png"),
    "e2": Path("game/images/nsfw/cg/cg_e2_two_tickets_private_compartment.png"),
    "compartment": Path("game/images/nsfw/cg/cg_e2_two_tickets_private_compartment.png"),
    "cg_e2": Path("game/images/nsfw/cg/cg_e2_two_tickets_private_compartment.png"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "slot",
        nargs="?",
        help="Story CG slot alias, for example c2l, real_name, cg_c2l, vow, or compartment.",
    )
    parser.add_argument("source", nargs="?", type=Path, help="Finished user-provided image to import.")
    parser.add_argument(
        "--mode",
        choices=("cover", "contain", "copy"),
        default="cover",
        help="Resize behavior. cover crops to fill 1024x768; contain letterboxes; copy preserves dimensions.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate paths and print planned changes only.")
    parser.add_argument("--list-slots", action="store_true", help="List supported slot aliases and exit.")
    return parser.parse_args()


def resolve(path: Path, base_dir: Path) -> Path:
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def list_slots() -> None:
    seen: dict[Path, list[str]] = {}
    for alias, destination in sorted(CG_SLOTS.items()):
        seen.setdefault(destination, []).append(alias)
    for destination, aliases in sorted(seen.items(), key=lambda item: str(item[0])):
        print(f"{destination}: {', '.join(aliases)}")


def backup_destination(destination: Path, base_dir: Path) -> Path | None:
    if not destination.exists():
        return None
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = base_dir / "art" / "backups" / f"explicit_adult_asset_import_{stamp}"
    try:
        relative_destination = destination.relative_to(base_dir)
    except ValueError:
        relative_destination = Path(destination.name)
    backup_path = backup_root / relative_destination
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(destination, backup_path)
    return backup_path


def open_rgb(path: Path) -> Image.Image:
    if Image is None:
        raise RuntimeError("Pillow is required for image import and resizing.")
    image = Image.open(path)
    if image.mode == "RGBA":
        background = Image.new("RGBA", image.size, (0, 0, 0, 255))
        background.alpha_composite(image)
        return background.convert("RGB")
    return image.convert("RGB")


def cover_resize(image: Image.Image) -> Image.Image:
    source_w, source_h = image.size
    target_w, target_h = TARGET_SIZE
    source_ratio = source_w / source_h
    target_ratio = target_w / target_h
    if source_ratio > target_ratio:
        crop_h = source_h
        crop_w = int(source_h * target_ratio)
    else:
        crop_w = source_w
        crop_h = int(source_w / target_ratio)
    left = max(0, (source_w - crop_w) // 2)
    top = max(0, (source_h - crop_h) // 2)
    cropped = image.crop((left, top, left + crop_w, top + crop_h))
    return cropped.resize(TARGET_SIZE, Image.Resampling.LANCZOS)


def contain_resize(image: Image.Image) -> Image.Image:
    canvas = Image.new("RGB", TARGET_SIZE, (0, 0, 0))
    fitted = image.copy()
    fitted.thumbnail(TARGET_SIZE, Image.Resampling.LANCZOS)
    canvas.paste(fitted, ((TARGET_SIZE[0] - fitted.width) // 2, (TARGET_SIZE[1] - fitted.height) // 2))
    return canvas


def import_image(source: Path, destination: Path, mode: str, dry_run: bool, base_dir: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Source image not found: {source}")
    if source.resolve() == destination.resolve():
        raise ValueError("Source and destination are the same file.")
    if Image is None:
        raise RuntimeError("Pillow is required for image import and resizing.")
    with Image.open(source) as probe:
        source_size = probe.size
    print(f"source: {source} ({source_size[0]}x{source_size[1]})")
    print(f"destination: {destination}")
    print(f"mode: {mode}")
    if dry_run:
        print("[dry-run] no files changed")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup_path = backup_destination(destination, base_dir)
    if mode == "copy":
        shutil.copy2(source, destination)
    else:
        image = open_rgb(source)
        if mode == "cover":
            output = cover_resize(image)
        else:
            output = contain_resize(image)
        output.save(destination, format="PNG")
    if backup_path:
        print(f"backup: {backup_path}")
    print(f"[imported] {source} -> {destination}")


def main() -> int:
    args = parse_args()
    base_dir = Path.cwd().resolve()
    if args.list_slots:
        list_slots()
        return 0
    if not args.slot or not args.source:
        print("error: slot and source are required unless --list-slots is used.", file=sys.stderr)
        return 2
    slot = args.slot.strip().lower()
    if slot not in CG_SLOTS:
        valid = ", ".join(sorted(CG_SLOTS))
        print(f"error: unknown slot {args.slot!r}. Valid aliases: {valid}", file=sys.stderr)
        return 2
    try:
        source = resolve(args.source, base_dir)
        destination = resolve(CG_SLOTS[slot], base_dir)
        import_image(source, destination, args.mode, args.dry_run, base_dir)
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
