#!/usr/bin/env python3
"""Review and import story NSFW concept candidates.

This helper does not call A1111. It scans generated review candidates, creates
an optional contact sheet/report, and imports approved winners into Ren'Py CG
slots with a backup of the previous files.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - depends on local runtime packages.
    Image = None
    ImageDraw = None
    ImageFont = None


DEFAULT_PROMPT_JSON = Path("prompts/story_nsfw_concept_assets.json")
DEFAULT_SHEET = Path("art/diagnostics/story_nsfw_concept_review.jpg")
DEFAULT_REPORT = Path("art/diagnostics/story_nsfw_concept_review.md")

APPROVAL_DESTINATIONS = {
    "story_b2_maxine_almost_date_skin": Path("game/images/nsfw/cg/cg_b2_maxine_almost_date.png"),
    "story_c1_gala_balcony_skin": Path("game/images/nsfw/cg/cg_c1_gala_private_balcony.png"),
    "story_c2m_maxine_last_lie_skin": Path("game/images/nsfw/cg/cg_c2m_maxine_last_lie.png"),
    "story_c2l_lady_real_name_skin": Path("game/images/nsfw/cg/cg_c2l_lady_real_name.png"),
    "story_c2j_lady_no_questions_skin": Path("game/images/nsfw/cg/cg_c2j_lady_no_questions.png"),
    "story_e1_wedding_private_vow_skin": Path("game/images/nsfw/cg/cg_e1_wedding_garden_private_vow.png"),
    "story_e2_two_tickets_skin": Path("game/images/nsfw/cg/cg_e2_two_tickets_private_compartment.png"),
}


@dataclass
class Candidate:
    asset_name: str
    path: Path
    seed: str
    width: int | None = None
    height: int | None = None
    prompt: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-json", type=Path, default=DEFAULT_PROMPT_JSON)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--sheet", type=Path, default=DEFAULT_SHEET)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--approve",
        action="append",
        default=[],
        metavar="ASSET=PNG",
        help="Import an approved candidate into its game slot. Can be repeated.",
    )
    parser.add_argument(
        "--skip-sheet",
        action="store_true",
        help="Write only the markdown report, useful when Pillow is unavailable.",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("assets"), list):
        raise ValueError(f"{path} must contain an object with an assets list.")
    return data


def resolve_path(path: Path, base_dir: Path) -> Path:
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def asset_names(config: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for asset in config["assets"]:
        if isinstance(asset, dict) and asset.get("name"):
            names.append(str(asset["name"]))
    return names


def read_sidecar(path: Path) -> dict[str, Any]:
    sidecar = path.with_suffix(".json")
    if not sidecar.exists():
        return {}
    try:
        with sidecar.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def image_size(path: Path) -> tuple[int | None, int | None]:
    if Image is None:
        return None, None
    try:
        with Image.open(path) as img:
            return img.width, img.height
    except OSError:
        return None, None


def collect_candidates(output_dir: Path, names: list[str]) -> dict[str, list[Candidate]]:
    grouped: dict[str, list[Candidate]] = {name: [] for name in names}
    if not output_dir.exists():
        return grouped
    for name in names:
        for path in sorted(output_dir.glob(f"{name}*.png")):
            meta = read_sidecar(path)
            width, height = image_size(path)
            seed = str(meta.get("seed", ""))
            request = meta.get("request") if isinstance(meta.get("request"), dict) else {}
            prompt = str(request.get("prompt", ""))
            grouped[name].append(
                Candidate(asset_name=name, path=path, seed=seed, width=width, height=height, prompt=prompt)
            )
    return grouped


def write_report(path: Path, grouped: dict[str, list[Candidate]], output_dir: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Story NSFW Concept Review",
        "",
        f"Generated candidate directory: `{output_dir}`",
        "",
        "Only import candidates that pass the quality gate in `docs/nsfw_story_asset_plan.md`.",
        "",
    ]
    for name, candidates in grouped.items():
        destination = APPROVAL_DESTINATIONS.get(name)
        lines.append(f"## {name}")
        if destination:
            lines.append(f"Target slot: `{destination}`")
        if not candidates:
            lines.append("")
            lines.append("No candidates found yet.")
            lines.append("")
            continue
        lines.append("")
        for index, candidate in enumerate(candidates, start=1):
            dimensions = ""
            if candidate.width and candidate.height:
                dimensions = f" ({candidate.width}x{candidate.height})"
            seed = f", seed {candidate.seed}" if candidate.seed else ""
            lines.append(f"{index}. `{candidate.path}`{dimensions}{seed}")
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fit_image(path: Path, box: tuple[int, int]) -> Any:
    with Image.open(path) as img:
        image = img.convert("RGB")
    image.thumbnail(box, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", box, (246, 246, 246))
    canvas.paste(image, ((box[0] - image.width) // 2, (box[1] - image.height) // 2))
    return canvas


def write_sheet(path: Path, grouped: dict[str, list[Candidate]]) -> bool:
    if Image is None or ImageDraw is None or ImageFont is None:
        return False

    rows: list[Candidate | str] = []
    for name, candidates in grouped.items():
        rows.append(name)
        rows.extend(candidates or ["No candidates found"])

    thumb = (360, 270)
    gutter = 18
    label_h = 54
    width = gutter * 3 + thumb[0] * 2
    row_h = thumb[1] + label_h + gutter
    height = gutter + max(len(rows), 1) * row_h
    sheet = Image.new("RGB", (width, height), (30, 32, 36))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        small = ImageFont.truetype("arial.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    x_positions = [gutter, gutter * 2 + thumb[0]]
    col = 0
    y = gutter
    for item in rows:
        if isinstance(item, str):
            if col:
                y += row_h
                col = 0
            draw.text((gutter, y), item, fill=(255, 255, 255), font=font)
            y += label_h
            continue
        x = x_positions[col]
        draw.rectangle((x, y, x + thumb[0], y + thumb[1] + label_h), fill=(250, 250, 250))
        label = item.path.name
        if item.seed:
            label = f"{label} | seed {item.seed}"
        draw.text((x + 8, y + 6), label[:58], fill=(20, 20, 20), font=small)
        dimensions = ""
        if item.width and item.height:
            dimensions = f"{item.width}x{item.height}"
        draw.text((x + 8, y + 25), dimensions, fill=(70, 70, 70), font=small)
        sheet.paste(fit_image(item.path, thumb), (x, y + label_h))
        col += 1
        if col == 2:
            col = 0
            y += row_h
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.crop((0, 0, width, max(y + row_h, gutter + row_h))).save(path, quality=95)
    return True


def parse_approval(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise ValueError(f"Approval must be ASSET=PNG, got {value!r}.")
    name, raw_path = value.split("=", 1)
    name = name.strip()
    if name not in APPROVAL_DESTINATIONS:
        valid = ", ".join(sorted(APPROVAL_DESTINATIONS))
        raise ValueError(f"Unknown asset {name!r}. Valid assets: {valid}")
    return name, Path(raw_path.strip().strip('"'))


def backup_destination(destination: Path, backup_root: Path, base_dir: Path) -> None:
    if not destination.exists():
        return
    try:
        relative_destination = destination.relative_to(base_dir)
    except ValueError:
        relative_destination = Path(destination.name)
    backup_path = backup_root / relative_destination
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(destination, backup_path)


def import_approvals(approvals: list[str], base_dir: Path) -> list[str]:
    if not approvals:
        return []
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = base_dir / "art" / "backups" / f"story_nsfw_before_approval_{stamp}"
    imported: list[str] = []
    for value in approvals:
        name, source = parse_approval(value)
        source_path = resolve_path(source, base_dir)
        if not source_path.exists():
            raise FileNotFoundError(f"Approved candidate not found: {source_path}")
        destination = resolve_path(APPROVAL_DESTINATIONS[name], base_dir)
        backup_destination(destination, backup_root, base_dir)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        imported.append(f"{source_path} -> {destination}")
    return imported


def main() -> int:
    args = parse_args()
    base_dir = Path.cwd().resolve()
    try:
        config = load_config(resolve_path(args.prompt_json, base_dir))
        output_dir = resolve_path(args.output_dir or Path(str(config.get("output_dir", ""))), base_dir)
        grouped = collect_candidates(output_dir, asset_names(config))
        write_report(resolve_path(args.report, base_dir), grouped, output_dir)
        if not args.skip_sheet:
            wrote_sheet = write_sheet(resolve_path(args.sheet, base_dir), grouped)
            if not wrote_sheet:
                print("warning: Pillow is not available; skipped contact sheet.", file=sys.stderr)
        imported = import_approvals(args.approve, base_dir)
        for line in imported:
            print(f"[imported] {line}")
        total = sum(len(candidates) for candidates in grouped.values())
        print(f"[ok] found {total} candidate(s) in {output_dir}")
        print(f"[ok] report: {resolve_path(args.report, base_dir)}")
        if not args.skip_sheet:
            print(f"[ok] sheet: {resolve_path(args.sheet, base_dir)}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
