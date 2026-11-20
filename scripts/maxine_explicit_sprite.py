#!/usr/bin/env python3
"""From-scratch explicit Maxine sprite generator (txt2img only).

Bypasses the project's locked GUI profile, the character-context wrapper
that injects the identity profile string, the samandem_sdxl preset
prompt_prefix, init_image composition, and HR upscale. Two test variants
per run so we can isolate whether the ``samandem_maxine`` trigger token
itself (a concept/Lora-style binding in the SDXL checkpoint) is the
cloth-anchoring force, or whether the cloth language wins anyway.

Variants
--------
* ``trigger``    -> includes the literal ``samandem_maxine,`` token the
  existing pipeline uses.
* ``notrigger``  -> describes Maxine by physical traits only, no
  samandem_maxine binding.

Whitelist
---------
18+ adults only. The negative prompt explicitly excludes minors (child,
teen, underage, loli, shota), non-consent, coercion, assault,
bestiality, plus a strong anti-clothing block.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "art" / "generated" / "maxine_tests"

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"

MAXINE_PHYSICAL = (
    "1girl, young adult woman 18+, short spiky black hair with vivid blue "
    "streaks, blue eyes, athletic tomboy build, confident grin, fair skin"
)

# Explicit tokens go first with weight, then cloth-removal negations, then
# identity. Weighted at 1.4-1.5 to overcome the trigger's cloth bias when used.
EXPLICIT_PREFIX = (
    "masterpiece, best quality, highres, "
    "(fully nude:1.5), (completely bare:1.4), (exposed nipples:1.4), "
    "(uncensored:1.3), bare skin head to toe, "
    "no clothing, no cloth, no towel, no robe, no bra, no panties, "
    "no bikini, no bandages, no wrapping, no wrapper, no sports bra, "
    "no hoodie, no sweatshirt, no dress, no skirt, no pants, no shorts, "
    "fully unclothed, "
)

PROMPT_TRIGGER = (
    EXPLICIT_PREFIX
    + "samandem_maxine, young adult woman 18+, athletic tomboy build, "
    "short spiky black hair with vivid blue streaks, blue eyes, "
    "confident grin, full front-facing body, standing confident pose, "
    "plain light background, single character only"
)

PROMPT_NO_TRIGGER = (
    EXPLICIT_PREFIX
    + MAXINE_PHYSICAL
    + ", full front-facing body, standing confident pose, "
    "plain light background, single character only"
)

# Cloths are tagged with weight; minors/non-consent/bestiality are explicit
# negatives; quality filters cover the usual SD pitfalls.
EXPLICIT_NEGATIVE = (
    "clothing, clothes, covered, underwear, panties, bra, bikini, "
    "sports bra, bandages, wrapper, towel, robe, wrappings, shirt, "
    "hoodie, sweatshirt, pants, shorts, dress, skirt, "
    "minor, child, teen, underage, loli, shota, schoolgirl, schoolboy, "
    "non-consent, coercion, blackmail, mind-control consent, assault, bestiality, "
    "worst quality, low quality, normal quality, lowres, blurry, jpeg artifacts, "
    "bad anatomy, extra fingers, missing fingers, fused fingers, deformed hands, "
    "watermark, signature, text, logo, cropped head, out of frame, multiple views"
)


def post_payload(payload: dict, timeout: int = 240) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def write_image(response: dict, out_path: Path) -> tuple[int, int]:
    images = response.get("images", [])
    if not images:
        raise RuntimeError(
            f"A1111 returned no images; response keys={list(response.keys())}"
        )
    raw = base64.b64decode(images[0])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(raw)
    info_raw = response.get("info", "{}")
    width = height = 0
    try:
        meta = json.loads(info_raw)
        width = int(meta.get("width", 0))
        height = int(meta.get("height", 0))
    except json.JSONDecodeError:
        pass
    return width, height


def build_payload(args, prompt: str) -> dict:
    return {
        "prompt": prompt,
        "negative_prompt": EXPLICIT_NEGATIVE,
        "steps": args.steps,
        "cfg_scale": args.cfg_scale,
        "width": args.width,
        "height": args.height,
        "sampler_name": args.sampler,
        "scheduler": args.scheduler,
        "seed": args.seed,
        "batch_size": 1,
        "n_iter": 1,
        "restore_faces": False,
        "enable_hr": False,
        "override_settings": {
            "sd_model_checkpoint": args.checkpoint,
        },
        "override_settings_restore_afterwards": True,
    }


def short_ckpt(name: str) -> str:
    base = name.split(".")[0]
    return base.replace(" ", "_").replace("/", "_")


def run_variant(args, variant: str, seed: int) -> Path:
    prompt = PROMPT_TRIGGER if variant == "trigger" else PROMPT_NO_TRIGGER
    payload = build_payload(args, prompt)
    payload["seed"] = seed
    print(
        f"[run] variant={variant} seed={seed} ckpt={args.checkpoint} "
        f"sampler={args.sampler} scheduler={args.scheduler} "
        f"steps={args.steps} cfg={args.cfg_scale}"
    )
    response = post_payload(payload)
    ck = short_ckpt(args.checkpoint)
    out = OUT_DIR / f"maxine_{variant}_{ck}_seed-{seed}.png"
    sidecar = OUT_DIR / f"maxine_{variant}_{ck}_seed-{seed}.json"
    width, height = write_image(response, out)
    sidecar.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    info_raw = response.get("info", "{}")
    info = json.loads(info_raw)
    print(
        f"[ok] {out.name}  ({out.stat().st_size} bytes, {width}x{height}) "
        f"actual_seed={info.get('seed')} actual_sampler={info.get('sampler_name')}"
    )
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--variant",
        choices=["trigger", "notrigger", "both"],
        default="both",
        help="which test variants to run (default: both)",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        default=2,
        help="how many seeds to run per variant (default: 2 -> 4 PNGs)",
    )
    parser.add_argument(
        "--base-seed",
        type=int,
        default=1302777804,
        help="starting seed; subsequent seeds add 9973 each step",
    )
    parser.add_argument(
        "--checkpoint",
        default="hassakuXLIllustrious_v34.safetensors [1618edb443]",
        help="A1111 checkpoint title (hash-bracketed suffix optional)",
    )
    parser.add_argument("--sampler", default="Euler a")
    parser.add_argument("--scheduler", default="sgm_uniform")
    parser.add_argument("--steps", type=int, default=28)
    parser.add_argument("--cfg_scale", type=float, default=7.0)
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument(
        "--seed",
        type=int,
        default=-1,
        help="unused (kept for one-shot debugging)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    variants = (
        ["trigger", "notrigger"] if args.variant == "both" else [args.variant]
    )
    seeds = [args.base_seed + (9973 * i) for i in range(args.seeds)]
    print(
        f"[plan] variants={variants}  seeds={seeds}  "
        f"out_dir={OUT_DIR}"
    )
    print(f"[plan] prompt-positive-trigger-prefix: {PROMPT_TRIGGER[:120]}...")
    print(f"[plan] prompt-positive-notrigger-prefix: {PROMPT_NO_TRIGGER[:120]}...")
    print(f"[plan] negative-prefix: {EXPLICIT_NEGATIVE[:120]}...")
    for variant in variants:
        for seed in seeds:
            run_variant(args, variant, seed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
