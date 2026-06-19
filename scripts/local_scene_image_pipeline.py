#!/usr/bin/env python3
"""Turn a scene into a local, repeatable visual novel CG generation job.

Pipeline:
1. Ask a local Ollama LLM to convert the scene into a polished image prompt.
2. Cache that prompt so reruns use the exact same wording.
3. Send the prompt to local Automatic1111 with deterministic seeds/settings.

The default prompt policy is adult-themed but non-explicit: fictional adults
only, no visible genitals, no exposed nipples, no sex acts, no see-through
clothing, and no minors.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_A1111_URL = "http://127.0.0.1:7860"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "llama3.1:8b"
DEFAULT_OUTPUT_DIR = Path("art/generated/local_scene_pipeline")

STYLE_PREFIX = (
    "masterpiece, best quality, highres, polished cinematic anime visual novel CG, "
    "professional game art, detailed expressive eyes, detailed hair, clean linework, "
    "soft cel shading, smooth skin rendering, dramatic but readable lighting, "
    "rich background detail"
)

STYLE_SUFFIX = (
    "single coherent scene, no panels, no inset portraits, balanced VN composition, "
    "sharp focus, premium cloud-generation quality"
)

DEFAULT_NEGATIVE = (
    "worst quality, low quality, normal quality, lowres, blurry, jpeg artifacts, sketch, "
    "unfinished, bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, "
    "deformed hands, distorted face, crossed eyes, asymmetrical eyes, bad proportions, "
    "mutated limbs, extra arms, extra legs, cropped head, out of frame, character sheet, "
    "reference sheet, collage, split screen, side panel, inset portrait, thumbnails, "
    "duplicate character, extra face, watermark, signature, text, logo"
)

SAFETY_NEGATIVE = (
    "explicit nudity, exposed nipples, visible genitals, see-through clothing, "
    "sex act, penetration, oral sex, erotic contact, minor, child, teen"
)

CHARACTER_ANCHORS = {
    "alex": "Alex, fictional adult man age 22, short messy black hair, soft brown eyes, slim average build, gentle anxious expression, black hoodie and dark/white shirt palette",
    "maxine": "Maxine, fictional adult woman age 22, athletic tomboy build, short spiky black hair with vivid blue streaks, blue eyes, confident grin, navy sporty palette",
    "clara": "Clara, fictional adult woman age 23, long auburn red-brown hair swept to one side, warm brown eyes, composed dorm-leader poise, cream and ivory palette",
    "lady": "Clara as the Lady, fictional adult woman age 23, long auburn red-brown hair swept to one side, warm brown eyes, elegant dangerous poise, cream and ivory palette",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", nargs="?", help="Scene text to turn into a professional VN CG.")
    parser.add_argument("--scene-file", type=Path, help="Read scene text from a file instead of the positional scene.")
    parser.add_argument("--slug", help="Stable output slug. Defaults to a scene-derived slug.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true", help="Build prompt and payload, but do not call A1111.")
    parser.add_argument("--refresh-prompt", action="store_true", help="Ask the LLM again even if a cached prompt exists.")
    parser.add_argument("--no-llm", action="store_true", help="Use the deterministic template prompt instead of Ollama.")
    parser.add_argument("--llm-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--llm-model", default=DEFAULT_OLLAMA_MODEL)
    parser.add_argument("--llm-temperature", type=float, default=0.05)
    parser.add_argument("--list-llm-models", action="store_true", help="List local Ollama models and exit.")
    parser.add_argument("--a1111-url", default=DEFAULT_A1111_URL)
    parser.add_argument("--guidelines", default="", help="Extra art-direction guidance sent to the LLM and appended to the prompt.")
    parser.add_argument("--style-prefix", default=STYLE_PREFIX, help="Base quality/style prompt prefix.")
    parser.add_argument("--style-suffix", default=STYLE_SUFFIX, help="Base composition/style prompt suffix.")
    parser.add_argument("--negative-prompt", default=DEFAULT_NEGATIVE, help="Base negative prompt.")
    parser.add_argument("--always-negative", default=SAFETY_NEGATIVE, help="Always-on negative prompt tags.")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--steps", type=int, default=34)
    parser.add_argument("--cfg-scale", type=float, default=6.5)
    parser.add_argument("--sampler", default="DPM++ 2M")
    parser.add_argument("--scheduler", default="Karras")
    parser.add_argument("--checkpoint", help="Optional A1111 checkpoint override.")
    parser.add_argument("--seed", type=int, help="Fixed seed. Defaults to a stable scene hash.")
    parser.add_argument("--variants", type=int, default=1, help="Number of deterministic seed-step variants.")
    parser.add_argument("--seed-step", type=int, default=9973)
    parser.add_argument("--init-image", type=Path, help="Optional img2img source image.")
    parser.add_argument("--denoise", type=float, default=0.32, help="img2img denoising strength.")
    parser.add_argument("--extra-positive", default="", help="Extra positive prompt text appended after the LLM prompt.")
    parser.add_argument("--extra-negative", default="", help="Extra negative prompt text appended after defaults.")
    return parser.parse_args()


def resolve(path: Path, base_dir: Path) -> Path:
    return path if path.is_absolute() else (base_dir / path).resolve()


def read_scene(args: argparse.Namespace, base_dir: Path) -> str:
    if args.scene_file:
        path = resolve(args.scene_file, base_dir)
        return path.read_text(encoding="utf-8").strip()
    if args.scene:
        return args.scene.strip()
    raise ValueError("Provide a scene argument or --scene-file.")


def stable_int(value: str, modulo: int = 2_147_483_647) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:16], 16) % modulo


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value[:80] or "scene"


def scene_slug(scene: str) -> str:
    words = " ".join(scene.split()[:10])
    return f"{slugify(words)}_{stable_int(scene, 999999):06d}"


def detected_character_anchors(scene: str) -> list[str]:
    lowered = scene.lower()
    anchors: list[str] = []
    for key, anchor in CHARACTER_ANCHORS.items():
        if key in lowered:
            anchors.append(anchor)
    return anchors


def local_template_prompt(scene: str, guidelines: str) -> dict[str, Any]:
    anchors = detected_character_anchors(scene)
    anchor_text = "; ".join(anchors) if anchors else "fictional adult characters, age 22 or older"
    return {
        "positive_prompt": (
            f"{scene}. Subjects: {anchor_text}. Professional adult visual novel CG, "
            "skin-forward but non-explicit wardrobe, emotional eye contact, cinematic composition, "
            "strong story beat, polished anime game art."
        ),
        "negative_prompt": "flat lighting, amateur composition, dull background, plastic skin, overexposed highlights",
        "composition_notes": "Use a readable 16:9-style VN CG composition adapted to the requested output size.",
    }


def list_ollama_models(api_url: str) -> list[str]:
    url = f"{api_url.rstrip('/')}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach Ollama at {url}. Start Ollama or use --no-llm.") from exc
    models = payload.get("models", [])
    if not isinstance(models, list):
        return []
    names: list[str] = []
    for model in models:
        if isinstance(model, dict) and model.get("name"):
            names.append(str(model["name"]))
    return sorted(names)


def ollama_prompt_request(scene: str, slug: str, args: argparse.Namespace, seed: int) -> dict[str, Any]:
    anchors = detected_character_anchors(scene)
    anchor_text = "\n".join(f"- {anchor}" for anchor in anchors) or "- Use fictional adult characters, age 22 or older."
    guideline_text = args.guidelines.strip() or "No additional art-direction notes."
    instruction = f"""
You are a senior visual novel art director writing prompts for a local Stable Diffusion / Automatic1111 pipeline.

Return JSON only with these keys:
- positive_prompt: a single polished prompt for a professional cinematic anime visual novel CG
- negative_prompt: extra negative terms not already covered by the default negative prompt
- composition_notes: one short sentence explaining the intended frame

Rules:
- Fictional adults only, 18+.
- Adult-themed and skin-forward is allowed, but keep it non-explicit.
- Do not request visible genitals, exposed nipples, sex acts, penetration, oral sex, see-through clothing, erotic contact, minors, text, logos, or watermarks.
- Use concrete visual language: wardrobe, pose, lighting, mood, setting, props, and story beat.
- Preserve character identity when a known character appears.
- Make the image professional, polished, and repeatable.

Known character anchors:
{anchor_text}

Additional art-direction guidelines:
{guideline_text}

Scene slug: {slug}
Scene:
{scene}
""".strip()
    body = {
        "model": args.llm_model,
        "prompt": instruction,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": args.llm_temperature,
            "seed": seed,
        },
    }
    url = f"{args.llm_url.rstrip('/')}/api/generate"
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8"))
    raw = str(payload.get("response", "")).strip()
    if not raw:
        raise ValueError(
            f"Ollama model {args.llm_model!r} returned an empty response. "
            f"Try another --llm-model, run 'ollama pull {DEFAULT_OLLAMA_MODEL}', or use --no-llm."
        )
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.S)
        if not match:
            raise ValueError(
                f"Ollama model {args.llm_model!r} did not return JSON: {raw[:500]}. "
                f"Try another --llm-model or use --no-llm."
            )
        data = json.loads(match.group(0))
    if not isinstance(data, dict) or not str(data.get("positive_prompt", "")).strip():
        raise ValueError("Ollama JSON must include a non-empty positive_prompt.")
    return {
        "positive_prompt": str(data.get("positive_prompt", "")).strip(),
        "negative_prompt": str(data.get("negative_prompt", "")).strip(),
        "composition_notes": str(data.get("composition_notes", "")).strip(),
    }


def load_or_create_prompt(scene: str, slug: str, seed: int, args: argparse.Namespace, base_dir: Path) -> dict[str, Any]:
    output_dir = resolve(args.output_dir, base_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = output_dir / f"{slug}.prompt.json"
    if prompt_path.exists() and not args.refresh_prompt:
        return json.loads(prompt_path.read_text(encoding="utf-8"))
    if args.no_llm:
        prompt = local_template_prompt(scene, args.guidelines)
        llm_mode = "template"
    else:
        prompt = ollama_prompt_request(scene, slug, args, seed)
        llm_mode = "ollama"
    prompt_record = {
        "scene": scene,
        "slug": slug,
        "seed": seed,
        "llm_mode": llm_mode,
        "llm_model": None if args.no_llm else args.llm_model,
        "guidelines": args.guidelines,
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        **prompt,
    }
    prompt_path.write_text(json.dumps(prompt_record, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return prompt_record


def encode_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def combine_prompt_parts(parts: list[str]) -> str:
    terms: list[str] = []
    seen: set[str] = set()
    for part in parts:
        for term in part.split(","):
            cleaned = " ".join(term.strip().split())
            key = cleaned.casefold()
            if cleaned and key not in seen:
                terms.append(cleaned)
                seen.add(key)
    return ", ".join(terms)


def build_prompt(prompt_record: dict[str, Any], args: argparse.Namespace) -> tuple[str, str]:
    positive_parts = [
        args.style_prefix.strip(),
        str(prompt_record["positive_prompt"]).strip(),
        args.guidelines.strip(),
        args.extra_positive.strip(),
        args.style_suffix.strip(),
    ]
    negative_parts = [
        args.negative_prompt.strip(),
        str(prompt_record.get("negative_prompt", "")).strip(),
        args.extra_negative.strip(),
        args.always_negative.strip(),
        SAFETY_NEGATIVE,
    ]
    positive = combine_prompt_parts(positive_parts)
    negative = combine_prompt_parts(negative_parts)
    return positive, negative


def build_a1111_payload(
    positive: str,
    negative: str,
    seed: int,
    args: argparse.Namespace,
    base_dir: Path,
) -> tuple[str, dict[str, Any]]:
    payload: dict[str, Any] = {
        "prompt": positive,
        "negative_prompt": negative,
        "steps": args.steps,
        "cfg_scale": args.cfg_scale,
        "width": args.width,
        "height": args.height,
        "sampler_name": args.sampler,
        "scheduler": args.scheduler,
        "seed": seed,
        "batch_size": 1,
        "n_iter": 1,
        "restore_faces": False,
    }
    if args.checkpoint:
        payload["override_settings"] = {"sd_model_checkpoint": args.checkpoint}
        payload["override_settings_restore_afterwards"] = True
    if args.init_image:
        init_path = resolve(args.init_image, base_dir)
        payload["init_images"] = [encode_image(init_path)]
        payload["denoising_strength"] = args.denoise
        payload["resize_mode"] = 0
        return "img2img", payload
    return "txt2img", payload


def call_a1111(api_url: str, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{api_url.rstrip('/')}/sdapi/v1/{endpoint}"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"A1111 returned HTTP {exc.code} for {endpoint}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach A1111 at {api_url}. Make sure webui is running with --api.") from exc


def save_generation(
    response: dict[str, Any],
    output_dir: Path,
    slug: str,
    seed: int,
    variant_index: int,
    endpoint: str,
    payload: dict[str, Any],
    prompt_record: dict[str, Any],
) -> list[Path]:
    images = response.get("images", [])
    if not isinstance(images, list) or not images:
        raise RuntimeError("A1111 did not return any images.")
    saved: list[Path] = []
    for image_index, image_value in enumerate(images):
        image_b64 = str(image_value).split(",", 1)[-1]
        image_bytes = base64.b64decode(image_b64)
        suffix = f"v{variant_index:02d}_{image_index:02d}"
        image_path = output_dir / f"{slug}_seed_{seed}_{suffix}.png"
        meta_path = image_path.with_suffix(".json")
        image_path.write_bytes(image_bytes)
        meta = {
            "slug": slug,
            "seed": seed,
            "variant_index": variant_index,
            "endpoint": endpoint,
            "request": payload,
            "prompt_record": prompt_record,
            "a1111_info": response.get("info"),
            "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        }
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        saved.append(image_path)
    return saved


def main() -> int:
    args = parse_args()
    base_dir = Path.cwd().resolve()
    try:
        if args.list_llm_models:
            names = list_ollama_models(args.llm_url)
            if names:
                print("\n".join(names))
            else:
                print("No Ollama models found.")
            return 0
        scene = read_scene(args, base_dir)
        slug = slugify(args.slug) if args.slug else scene_slug(scene)
        seed = args.seed if args.seed is not None else stable_int(f"{slug}\n{scene}")
        output_dir = resolve(args.output_dir, base_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        prompt_record = load_or_create_prompt(scene, slug, seed, args, base_dir)
        positive, negative = build_prompt(prompt_record, args)
        print(f"slug: {slug}")
        print(f"seed: {seed}")
        print(f"prompt cache: {output_dir / f'{slug}.prompt.json'}")
        print(f"positive prompt: {positive}")
        print(f"negative prompt: {negative}")
        all_saved: list[Path] = []
        for variant_index in range(args.variants):
            variant_seed = seed + variant_index * args.seed_step
            endpoint, payload = build_a1111_payload(positive, negative, variant_seed, args, base_dir)
            if args.dry_run:
                print(f"[dry-run] {endpoint} seed={variant_seed}")
                print(json.dumps(payload, indent=2, ensure_ascii=True))
                continue
            response = call_a1111(args.a1111_url, endpoint, payload)
            saved = save_generation(response, output_dir, slug, variant_seed, variant_index, endpoint, payload, prompt_record)
            all_saved.extend(saved)
            for path in saved:
                print(f"[saved] {path}")
        if all_saved:
            print(f"[ok] saved {len(all_saved)} image(s) to {output_dir}")
        elif args.dry_run:
            print("[ok] dry-run complete")
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
