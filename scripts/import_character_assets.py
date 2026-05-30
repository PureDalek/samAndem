import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = REPO_ROOT / "Sam And Em" / "game" / "images" / "nsfw"

CHARACTERS = {"alex", "clara", "maxine"}
SLOTS = {
    "base": "base.png",
    "underwear": "underwear.png",
    "nude_front": "nude_front.png",
    "nude_alt": "nude_alt.png",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def parse_target(value):
    try:
        character, slot = value.lower().split(":", 1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use CHARACTER:SLOT, for example maxine:nude_front") from exc

    if character not in CHARACTERS:
        raise argparse.ArgumentTypeError(f"Unknown character {character!r}. Use: {', '.join(sorted(CHARACTERS))}")
    if slot not in SLOTS:
        raise argparse.ArgumentTypeError(f"Unknown slot {slot!r}. Use: {', '.join(sorted(SLOTS))}")
    return character, slot


def validate_source(path):
    source = Path(path).expanduser().resolve()
    if not source.exists() or not source.is_file():
        raise SystemExit(f"Source file not found: {source}")
    if source.suffix.lower() not in IMAGE_EXTENSIONS:
        raise SystemExit(f"Unsupported image type: {source.suffix}. Use PNG, JPG, JPEG, or WEBP.")
    return source


def backup_existing(destination, backup_root):
    if not destination.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = backup_root / timestamp / destination.parent.name
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / destination.name
    shutil.copy2(destination, backup_path)
    return backup_path


def import_asset(source, character, slot, no_backup):
    destination_dir = ASSET_ROOT / character
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / SLOTS[slot]

    backup_path = None
    if not no_backup:
        backup_path = backup_existing(destination, REPO_ROOT / "asset_backups")

    shutil.copy2(source, destination)
    return destination, backup_path


def main():
    parser = argparse.ArgumentParser(
        description="Import locally-created character images into Sam And Em's Ren'Py asset slots."
    )
    parser.add_argument("source", help="Path to the image file to import.")
    parser.add_argument("target", type=parse_target, help="Target slot as CHARACTER:SLOT.")
    parser.add_argument("--no-backup", action="store_true", help="Replace an existing file without backing it up.")
    args = parser.parse_args()

    source = validate_source(args.source)
    character, slot = args.target
    destination, backup_path = import_asset(source, character, slot, args.no_backup)

    print(f"Imported: {source}")
    print(f"Target:   {destination}")
    if backup_path:
        print(f"Backup:   {backup_path}")


if __name__ == "__main__":
    sys.exit(main())
