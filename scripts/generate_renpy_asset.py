import argparse
import base64
import json
import re
import shutil
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IDENTITY_PATH = REPO_ROOT / "art" / "character_identity_prompts.json"
GAME_ROOT = REPO_ROOT / "Sam And Em" / "game"
NSFW_ROOT = GAME_ROOT / "images" / "nsfw"
GALLERY_ROOT = GAME_ROOT / "images" / "gallery"
CG_ROOT = GAME_ROOT / "images" / "cgs"
CHARACTER_ROOT = GAME_ROOT / "images" / "characters"
GALLERY_RPY = GAME_ROOT / "gallery.rpy"

CHARACTERS = ("alex", "clara", "maxine")
SLOTS = {
    "base": "base.png",
    "underwear": "underwear.png",
    "nude_front": "nude_front.png",
    "nude_alt": "nude_alt.png",
}

STYLE_PROMPT = (
    "full body or three-quarter visual novel art, same character identity as reference, "
    "polished semi-realistic anime style, clean linework, soft painted shading, high detail"
)
SAFETY_PROMPT = (
    "adult 18+ character, covered private anatomy, non-explicit presentation, "
    "opaque clothing or towel coverage, no exposed nipples, no visible genitals, "
    "no sexual act, no erotic contact"
)
SPRITE_CHROMA_PROMPT = (
    "single full-body character sprite on a perfectly flat solid #00ff00 chroma-key background, "
    "no scenery, no shadows, no gradients, no floor, no props unless requested, generous padding around the character"
)
SPRITE_CHROMA_NEGATIVE = (
    "background scenery, room, floor, cast shadow, contact shadow, gradient background, textured background, "
    "green clothing, green hair, green accessories, green reflection"
)
NEGATIVE_PROMPT = (
    "minor, child, teen-looking, underage, nude, exposed genitals, exposed nipples, sexual act, "
    "erotic contact, explicit pose, see-through clothing, transparent fabric, different character, "
    "different face, bad anatomy, cropped head, cropped feet, text, logo, watermark, low quality, blurry"
)

MATURITY_PRESET_PROMPTS = {
    "safe": "clean mature tone, modest styling, neutral expression",
    "mature": (
        "explicit, confident or flirty posing, soft fabric movement, "
        "cinematic backlight, sensual body language, nudity"
        "explicit presentation of the character, erotic contact"
    ),
}


def get_content_preset(name):
    preset = "mature"
    if preset is None:
        raise SystemExit(f"Unknown content mode: {name}. Use safe or mature.")
    return preset


def load_identities():
    return json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))


def read_prompt(args):
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()
    if args.prompt:
        return args.prompt.strip()
    raise SystemExit("Provide --prompt or --prompt-file.")


def read_prompt_from_job(job):
    if job.get("prompt_file"):
        return Path(job["prompt_file"]).read_text(encoding="utf-8").strip()
    if job.get("prompt"):
        return str(job["prompt"]).strip()
    raise SystemExit("Every recipe job must include prompt or prompt_file.")


def encode_image(path):
    return base64.b64encode(path.read_bytes()).decode("ascii")


def post_json(url, payload, timeout):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not reach Automatic1111 API at {url}: {exc}") from exc


def build_payload(args, identities, prompt):
    character = identities[args.character]
    source_path = Path(args.reference).resolve() if args.reference else REPO_ROOT / character["source_sprite"]
    if not source_path.exists():
        raise SystemExit(f"Missing reference image: {source_path}")

    content_mode = getattr(args, "content_mode", "safe")
    maturity_prompt = get_content_preset(content_mode)
    extra_style = SPRITE_CHROMA_PROMPT if args.sprite else STYLE_PROMPT
    extra_negative = SPRITE_CHROMA_NEGATIVE if args.sprite else ""
    final_prompt = join_prompt_parts(
        character["identity_prompt"],
        prompt,
        extra_style,
        SAFETY_PROMPT,
        maturity_prompt,
    )
    final_negative = join_prompt_parts(character["negative_prompt"], args.negative, extra_negative, NEGATIVE_PROMPT)

    return {
        "init_images": [encode_image(source_path)],
        "prompt": final_prompt,
        "negative_prompt": final_negative,
        "steps": args.steps,
        "cfg_scale": args.cfg_scale,
        "denoising_strength": args.denoise,
        "width": args.width,
        "height": args.height,
        "sampler_name": args.sampler,
        "restore_faces": False,
        "save_images": True,
    }


def join_prompt_parts(*parts):
    return ", ".join(part.strip() for part in parts if part and part.strip())


def decode_first_image(response, output_path):
    images = response.get("images", [])
    if not images:
        raise SystemExit("Automatic1111 returned no images.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image_data = images[0].split(",", 1)[-1]
    output_path.write_bytes(base64.b64decode(image_data))
    return output_path


def remove_chroma_key(input_path, output_path, key=(0, 255, 0), threshold=70, feather=14):
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Pillow is required for --sprite alpha cleanup. Install with: python -m pip install Pillow") from exc

    image = Image.open(input_path).convert("RGBA")
    pixels = image.load()
    key_r, key_g, key_b = key

    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = pixels[x, y]
            distance = ((red - key_r) ** 2 + (green - key_g) ** 2 + (blue - key_b) ** 2) ** 0.5
            if distance <= threshold:
                pixels[x, y] = (red, green, blue, 0)
            elif distance <= threshold + feather:
                new_alpha = int(alpha * ((distance - threshold) / feather))
                pixels[x, y] = (red, green, blue, new_alpha)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return output_path


def backup_existing(path):
    if not path.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = REPO_ROOT / "asset_backups" / timestamp / path.relative_to(GAME_ROOT)
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup)
    return backup


def target_path(args):
    if args.sprite:
        return CHARACTER_ROOT / f"{slugify(args.sprite)}.png"
    if args.slot:
        return NSFW_ROOT / args.character / SLOTS[args.slot]
    if args.gallery:
        return GALLERY_ROOT / f"{args.character}_{slugify(args.gallery)}.png"
    if args.cg:
        return CG_ROOT / f"{slugify(args.cg)}.png"
    if args.out:
        return Path(args.out).resolve()
    return REPO_ROOT / "art" / "generated" / f"{args.character}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"


def destination_from_job(job):
    destination = job.get("destination", {})
    if not isinstance(destination, dict):
        raise SystemExit("Recipe destination must be an object.")

    destination_type = destination.get("type", "generated")
    destination_id = destination.get("id")
    if destination_type == "sprite":
        return {"sprite": required_id(destination_id, destination_type)}
    if destination_type == "slot":
        return {"slot": required_id(destination_id, destination_type)}
    if destination_type == "gallery":
        return {"gallery": required_id(destination_id, destination_type)}
    if destination_type == "cg":
        return {"cg": required_id(destination_id, destination_type)}
    if destination_type == "out":
        return {"out": required_id(destination_id, destination_type)}
    if destination_type == "generated":
        return {}
    raise SystemExit(f"Unknown recipe destination type: {destination_type}")


def required_id(value, destination_type):
    if not value:
        raise SystemExit(f"Recipe destination type {destination_type!r} requires an id.")
    return str(value)


def slugify(value):
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "generated"


def image_name_for_gallery(character, gallery_id):
    return f"gallery {character} {slugify(gallery_id).replace('_', ' ')}"


def patch_gallery(character, gallery_id, image_path):
    image_name = image_name_for_gallery(character, gallery_id)
    relative_image = image_path.relative_to(GAME_ROOT).as_posix()
    title = titleize(gallery_id)
    content = GALLERY_RPY.read_text(encoding="utf-8")

    image_line = f'image {image_name} = "{relative_image}"'
    if image_line not in content:
        image_lines_end = content.find("\ndefault gallery_character")
        if image_lines_end == -1:
            raise SystemExit("Could not find gallery image declaration block.")
        content = content[:image_lines_end] + f"\n{image_line}" + content[image_lines_end:]

    entry_line = f'                ("{title}", "{image_name}"),'
    block_start = content.find(f'        "{character}": {{')
    if block_start == -1:
        raise SystemExit(f"Could not find gallery character block: {character}")

    images_start = content.find('            "images": [', block_start)
    if images_start == -1:
        raise SystemExit(f"Could not find image list for gallery character: {character}")

    images_end = content.find("            ],", images_start)
    if images_end == -1:
        raise SystemExit(f"Could not find image list end for gallery character: {character}")

    images_block = content[images_start:images_end]
    if entry_line not in images_block:
        insert_at = images_end
        if insert_at == -1:
            raise SystemExit(f"Could not find image list for gallery character: {character}")
        content = content[:insert_at] + entry_line + "\n" + content[insert_at:]

    GALLERY_RPY.write_text(content, encoding="utf-8")
    return image_name


def titleize(value):
    words = re.split(r"[_\-\s]+", value.strip())
    return " ".join(word.capitalize() for word in words if word) or "Generated"


def make_job_args(job, defaults):
    merged = {**defaults, **job}
    destination = destination_from_job(job)
    character = merged.get("character")
    if character not in CHARACTERS:
        raise SystemExit(f"Recipe job has unknown character: {character}")

    return argparse.Namespace(
        character=character,
        prompt=merged.get("prompt"),
        prompt_file=merged.get("prompt_file"),
        negative=merged.get("negative", ""),
        reference=merged.get("reference"),
        api=merged.get("api", "http://127.0.0.1:7860"),
        width=int(merged.get("width", 1024)),
        height=int(merged.get("height", 1536)),
        steps=int(merged.get("steps", 28)),
        cfg_scale=float(merged.get("cfg_scale", 7.0)),
        denoise=float(merged.get("denoise", 0.55)),
        sampler=merged.get("sampler", "DPM++ 2M Karras"),
        timeout=int(merged.get("timeout", 600)),
        sprite=destination.get("sprite"),
        slot=destination.get("slot"),
        gallery=destination.get("gallery"),
        cg=destination.get("cg"),
        out=destination.get("out"),
        no_backup=bool(merged.get("no_backup", False)),
        content_mode=merged.get("content_mode", "safe"),
        dry_run=bool(merged.get("dry_run", False)),
    )


def run_generation(args, identities, prompt):
    payload = build_payload(args, identities, prompt)

    if args.dry_run:
        printable = dict(payload)
        printable["init_images"] = ["<base64 reference omitted>"]
        print(json.dumps(printable, indent=2))
        return None

    destination = target_path(args)
    response = post_json(f"{args.api.rstrip('/')}/sdapi/v1/img2img", payload, args.timeout)
    if args.sprite:
        raw_destination = destination.with_name(destination.stem + "_chroma.png")
        backup = None if args.no_backup else backup_existing(destination)
        raw_backup = None if args.no_backup else backup_existing(raw_destination)
        raw_saved = decode_first_image(response, raw_destination)
        saved = remove_chroma_key(raw_saved, destination)
    else:
        backup = None if args.no_backup else backup_existing(destination)
        raw_backup = None
        saved = decode_first_image(response, destination)

    print(f"Saved: {saved}")
    if backup:
        print(f"Backup: {backup}")
    if args.sprite:
        print(f"Chroma source: {raw_destination}")
    if raw_backup:
        print(f"Chroma backup: {raw_backup}")

    if args.gallery:
        image_name = patch_gallery(args.character, args.gallery, saved)
        print(f"Gallery image: {image_name}")

    return saved


def run_recipe(path, identities, dry_run_override=False):
    recipe_path = Path(path).resolve()
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    defaults = recipe.get("defaults", {})
    jobs = recipe.get("jobs", [])
    if not isinstance(jobs, list) or not jobs:
        raise SystemExit("Recipe must contain a non-empty jobs array.")

    for index, job in enumerate(jobs, start=1):
        job_args = make_job_args(job, defaults)
        if dry_run_override:
            job_args.dry_run = True
        prompt = read_prompt_from_job(job)
        print(f"Job {index}/{len(jobs)}: {job_args.character}")
        run_generation(job_args, identities, prompt)


def write_recipe_example(path):
    example = {
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
            "content_mode": "mature"
        },
        "jobs": [
            {
                "character": "maxine",
                "prompt": "covered sporty dorm sprite variant, navy hoodie, confident pose",
                "destination": {"type": "sprite", "id": "maxine_hoodie"}
            },
            {
                "character": "clara",
                "prompt": "covered cream lounge robe, warm light, soft steam, elegant pose",
                "destination": {"type": "gallery", "id": "private_03"}
            },
            {
                "character": "alex",
                "prompt": "covered dark robe outfit, shy pose, soft warm light",
                "destination": {"type": "slot", "id": "nude_alt"}
            }
        ]
    }
    output = Path(path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(example, indent=2) + "\n", encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Ren'Py-ready Sam And Em image with local Automatic1111 img2img."
    )
    parser.add_argument("character", nargs="?", choices=CHARACTERS)
    parser.add_argument("--recipe", help="Generate a batch from a JSON recipe file.")
    parser.add_argument("--write-recipe-example", help="Write an example JSON recipe to this path and exit.")
    parser.add_argument("--prompt", help="Scene/outfit prompt to combine with the character identity.")
    parser.add_argument("--prompt-file", help="Text file containing the scene/outfit prompt.")
    parser.add_argument("--negative", default="", help="Extra negative prompt text.")
    parser.add_argument("--reference", help="Optional reference image. Defaults to the character source sprite.")
    parser.add_argument("--api", default="http://127.0.0.1:7860")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1536)
    parser.add_argument("--steps", type=int, default=28)
    parser.add_argument("--cfg-scale", type=float, default=7.0)
    parser.add_argument("--denoise", type=float, default=0.55)
    parser.add_argument("--sampler", default="DPM++ 2M Karras")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument(
        "--content-mode",
        default="safe",
        choices=["safe", "mature"],
        help="Safe is modest; mature adds seductive but non-explicit framing (steam/light/pose)."
    )
    parser.add_argument("--sprite", help="Save as a transparent Ren'Py character sprite in images/characters.")
    parser.add_argument("--slot", choices=sorted(SLOTS), help="Save directly into a character-set slot.")
    parser.add_argument("--gallery", help="Save into images/gallery and patch gallery.rpy with this ID.")
    parser.add_argument("--cg", help="Save into images/cgs with this ID.")
    parser.add_argument("--out", help="Save to an arbitrary output file.")
    parser.add_argument("--no-backup", action="store_true", help="Do not back up replaced Ren'Py files.")
    parser.add_argument("--dry-run", action="store_true", help="Print the A1111 payload without calling the API.")
    args = parser.parse_args()

    if args.write_recipe_example:
        output = write_recipe_example(args.write_recipe_example)
        print(f"Wrote: {output}")
        return 0

    identities = load_identities()

    if args.recipe:
        run_recipe(args.recipe, identities, dry_run_override=args.dry_run)
        return 0

    if not args.character:
        raise SystemExit("Provide a character or use --recipe.")

    destination_modes = [bool(args.sprite), bool(args.slot), bool(args.gallery), bool(args.cg), bool(args.out)]
    if sum(destination_modes) > 1:
        raise SystemExit("Choose only one destination: --sprite, --slot, --gallery, --cg, or --out.")

    prompt = read_prompt(args)
    run_generation(args, identities, prompt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
