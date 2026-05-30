import argparse
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IDENTITY_PATH = REPO_ROOT / "art" / "character_identity_prompts.json"

VARIANTS = {
    "underwear": {
        "alex": "modest private dorm loungewear, dark boxer-style sleep shorts, loose open black hoodie, plain white undershirt, barefoot, fully covered, non-explicit",
        "maxine": "covered private dorm loungewear, navy sports crop tank, high-waisted athletic sleep shorts, sleeveless hoodie open, hand wraps, fully covered, non-explicit",
        "clara": "covered private dorm loungewear, cream satin camisole, soft beige robe cardigan, dark lounge shorts, elegant slippers, fully covered, non-explicit",
    },
    "base": {
        "alex": "standard academy arrival outfit, black hoodie, white t-shirt, jeans, backpack, sneakers",
        "maxine": "standard sporty tomboy outfit, navy sports bra top under open sleeveless hoodie, track pants, hand wraps, sneakers",
        "clara": "standard dorm leader outfit, beige cardigan, white blouse, black pencil skirt, lanyard, heels",
    },
    "implied_steam": {
        "alex": "private shower-room character art, bare shoulders, opaque towel wrapped at the waist, thick steam and soft light covering all private anatomy, fully non-explicit",
        "maxine": "private shower-room character art, bare shoulders, opaque towel wrapped securely around the chest and upper thighs, thick steam and soft light covering all private anatomy, fully non-explicit",
        "clara": "private shower-room character art, bare shoulders, opaque towel wrapped securely around the chest and upper thighs, thick steam and soft light covering all private anatomy, elegant pose, fully non-explicit",
    },
    "covered_spa": {
        "alex": "covered spa-wrap character art, opaque dark towel wrap at the waist, white tank top visible, warm rim light and soft mist, non-explicit",
        "maxine": "covered spa-wrap character art, opaque navy towel wrap worn securely high around the chest and upper thighs, cool rim light and soft mist, non-explicit",
        "clara": "covered spa-wrap character art, opaque cream towel wrap worn securely high around the chest and upper thighs, warm rim light and soft mist, non-explicit",
    },
    "backlit_robe": {
        "alex": "soft backlit robe character art, loose dark robe and opaque lounge shorts, white undershirt, dramatic side light and mist, non-explicit",
        "maxine": "soft backlit robe character art, navy sports crop top and opaque athletic shorts, cool side light and mist, non-explicit",
        "clara": "soft backlit robe character art, cream camisole and opaque dark lounge shorts under a soft beige open robe, warm side light and mist, non-explicit",
    },
}

STYLE_PROMPT = (
    "full body visual novel sprite, same face and hair as source sprite, same character identity, "
    "polished semi-realistic anime style, clean linework, soft painted shading, black background, "
    "centered, head-to-toe visible, high detail"
)

GLOBAL_NEGATIVE = (
    "child, minor, teen-looking, underage, nude, exposed genitals, exposed nipples, sexual act, "
    "explicit pose, see-through clothing, different character, different face, bad anatomy, extra fingers, "
    "missing fingers, cropped feet, cropped head, text, logo, watermark, low quality, blurry"
)


def load_identities():
    return json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))


def encode_image(path):
    return base64.b64encode(path.read_bytes()).decode("ascii")


def build_prompt(character_id, variant, identities):
    if character_id not in identities:
        raise SystemExit(f"Unknown character: {character_id}")
    if variant not in VARIANTS:
        raise SystemExit(f"Unknown variant: {variant}")
    if character_id not in VARIANTS[variant]:
        raise SystemExit(f"Variant {variant!r} is not defined for {character_id!r}")

    identity = identities[character_id]
    prompt = ", ".join(
        [
            identity["identity_prompt"],
            VARIANTS[variant][character_id],
            STYLE_PROMPT,
        ]
    )
    negative = ", ".join([identity["negative_prompt"], GLOBAL_NEGATIVE])
    return prompt, negative


def build_img2img_payload(character_id, variant, identities, width, height, steps, cfg_scale, denoise):
    identity = identities[character_id]
    source_path = REPO_ROOT / identity["source_sprite"]
    if not source_path.exists():
        raise SystemExit(f"Missing source sprite: {source_path}")

    prompt, negative = build_prompt(character_id, variant, identities)
    return {
        "init_images": [encode_image(source_path)],
        "prompt": prompt,
        "negative_prompt": negative,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "denoising_strength": denoise,
        "width": width,
        "height": height,
        "sampler_name": "DPM++ 2M Karras",
        "restore_faces": False,
        "save_images": True,
    }


def post_json(url, payload):
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not reach Automatic1111 API at {url}: {exc}") from exc


def save_response_images(response, output_dir, character_id, variant):
    images = response.get("images", [])
    if not images:
        raise SystemExit("Automatic1111 returned no images.")

    output_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for index, image_data in enumerate(images, start=1):
        image_bytes = base64.b64decode(image_data.split(",", 1)[-1])
        out_path = output_dir / f"{character_id}_{variant}_{index:02d}.png"
        out_path.write_bytes(image_bytes)
        saved.append(out_path)
    return saved


def main():
    parser = argparse.ArgumentParser(
        description="Build safe Automatic1111 prompts/payloads for Sam And Em character-consistent art."
    )
    parser.add_argument("character", choices=["alex", "maxine", "clara", "all"])
    parser.add_argument("--variant", choices=sorted(VARIANTS), default="underwear")
    parser.add_argument("--mode", choices=["prompt", "payload", "generate"], default="prompt")
    parser.add_argument("--api", default="http://127.0.0.1:7860")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1536)
    parser.add_argument("--steps", type=int, default=28)
    parser.add_argument("--cfg-scale", type=float, default=7.0)
    parser.add_argument("--denoise", type=float, default=0.35)
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "art" / "generated"))
    args = parser.parse_args()

    identities = load_identities()
    characters = list(identities) if args.character == "all" else [args.character]

    if args.mode == "prompt":
        result = {}
        for character_id in characters:
            prompt, negative = build_prompt(character_id, args.variant, identities)
            result[character_id] = {"prompt": prompt, "negative_prompt": negative}
        print(json.dumps(result, indent=2))
        return

    payloads = {
        character_id: build_img2img_payload(
            character_id,
            args.variant,
            identities,
            args.width,
            args.height,
            args.steps,
            args.cfg_scale,
            args.denoise,
        )
        for character_id in characters
    }

    if args.mode == "payload":
        printable = dict(payloads)
        for payload in printable.values():
            payload["init_images"] = ["<base64 source sprite omitted>"]
        print(json.dumps(printable, indent=2))
        return

    output_dir = Path(args.out_dir)
    for character_id, payload in payloads.items():
        response = post_json(f"{args.api.rstrip('/')}/sdapi/v1/img2img", payload)
        saved = save_response_images(response, output_dir, character_id, args.variant)
        for path in saved:
            print(path)


if __name__ == "__main__":
    sys.exit(main())
