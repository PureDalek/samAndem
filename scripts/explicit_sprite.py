#!/usr/bin/env python3
"""From-scratch explicit female-character sprite generator (txt2img only).

Bypasses the project's locked GUI profile, character-context wrapper,
samandem_sdxl preset prompt_prefix, init_image composition, and HR
upscale. Supports the two female characters (Maxine + Clara) and two test
variants per character (with vs without the samandem_<char> trigger) so
we can isolate which layer is cloth-anchoring the SDXL output. Each
sidecar dumps BOTH the request payload and the A1111 info response so
we have ground-truth on what model/sampler/seed actually ran.

Variants
--------
* ``trigger``    -> includes the literal ``samandem_<char>`` token the
  existing pipeline uses.
* ``notrigger``  -> describes the character by physical traits only,
  no samandem_<char> binding.

Override smoke test
-------------------
``--smoke-override`` runs two narrow 512x512 sanity calls so we can
confirm whether the A1111 server actually honours
``override_settings.sd_model_checkpoint``. Call-1 has the override,
call-2 strips it. Their ``info.sd_model_name`` strings should differ -
if they don't, the override is being silently dropped.

Whitelist
---------
18+ adults only. The negative prompt explicitly excludes minors (child,
teen, underage, loli, shota), non-consent, coercion, assault,
bestiality, plus a weighted anti-clothing block.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "art" / "generated" / "explicit_sprite_tests"

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"

CHARACTERS = {
    "maxine": {
        "label": "maxine (athletic tomboy, blue-streaked hair)",
        "physical": (
            "1girl, young adult woman 18+, short spiky black hair with vivid blue streaks, "
            "blue eyes, athletic tomboy build, fair naked skin, totally unclothed, "
            "confident grin, explicit bare body, no clothes"
        ),
        "trigger": "samandem_maxine",
    },
    "clara": {
        "label": "clara (elegant dorm leader, long auburn hair)",
        "physical": (
            "1girl, young adult woman 18+, long auburn red-brown hair swept to one side, "
            "warm brown eyes, elegant curvy build, fair skin, composed confident smile"
        ),
        "trigger": "samandem_clara",
    },
}

# Front-weighted explicit emphasis at 1.5-1.8 to overcome a baked-in
# cloth concept on the SDXL checkpoints. Cloth-exclusion then comes
# before the character identity so the explicit instruction is read first.
EXPLICIT_PREFIX = (
    "masterpiece, best quality, highres, "
    "(fully nude:2.1), (completely bare:2.0), (exposed nipples:1.9), "
    "(bare breasts:1.9), (bare pussy:1.8), (uncensored:1.7), "
    "(visible_pussy:1.6), (nude_intentions:1.5), (no_disposable_clothing:1.4), "
    "bare skin head to toe, "
    "no clothing, no cloth, no towel, no robe, no bra, no panties, "
    "no bikini, no bandages, no wrapping, no wrapper, no sports bra, "
    "no hoodie, no sweatshirt, no dress, no skirt, no pants, no shorts, no shirt, "
    "fully unclothed, "
)

EXPLICIT_NEGATIVE = (
    "(clothing, clothes, covered, underwear, panties, bra, bikini, "
    "sports bra, bandages, wrapper, towel, robe, wrappings, shirt, "
    "hoodie, sweatshirt, pants, shorts, dress, skirt:1.7), "
    "(no_covered:1.6), "
    "minor, child, teen, underage, loli, shota, schoolgirl, schoolboy, "
    "non-consent, coercion, blackmail, mind-control consent, assault, bestiality, "
    "worst quality, low quality, normal quality, lowres, blurry, jpeg artifacts, "
    "bad anatomy, extra fingers, missing fingers, fused fingers, deformed hands, "
    "watermark, signature, text, logo, cropped head, out of frame, multiple views"
)


def build_prompt_trigger(character_id: str) -> str:
    cd = CHARACTERS[character_id]
    return (
        EXPLICIT_PREFIX
        + f"{cd['trigger']}, {cd['physical']}, "
        "full front-facing body, standing confident pose, "
        "plain light background, single character only"
    )


def build_prompt_no_trigger(character_id: str) -> str:
    cd = CHARACTERS[character_id]
    return (
        EXPLICIT_PREFIX
        + f"{cd['physical']}, "
        "full front-facing body, standing confident pose, "
        "plain light background, single character only"
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


def short_ckpt(name: str) -> str:
    base = name.split(".")[0]
    return base.replace(" ", "_").replace("/", "_")


def build_payload(args, prompt: str) -> dict:
    payload = {
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
    }
    if args.checkpoint:
        payload["override_settings"] = {"sd_model_checkpoint": args.checkpoint}
        payload["override_settings_restore_afterwards"] = True
    return payload


def write_image(response: dict, out_path: Path) -> tuple[int, int]:
    images = response.get("images", [])
    if not images:
        raise RuntimeError(
            f"A1111 returned no images; keys={list(response.keys())}"
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


def run_variant(args, character_id: str, variant: str, seed: int, out_dir: Path) -> Path:
    prompt = (
        build_prompt_trigger(character_id)
        if variant == "trigger"
        else build_prompt_no_trigger(character_id)
    )
    payload = build_payload(args, prompt)
    payload["seed"] = seed
    print(
        f"[run] character={character_id} variant={variant} seed={seed} "
        f"ckpt={args.checkpoint or '(loaded)'} sampler={args.sampler} "
        f"scheduler={args.scheduler} steps={args.steps} cfg={args.cfg_scale}"
    )
    response = post_payload(payload)
    ck_short = short_ckpt(args.checkpoint) if args.checkpoint else "no_override"
    out = out_dir / f"{character_id}_{variant}_{ck_short}_seed-{seed}.png"
    sidecar = out_dir / f"{character_id}_{variant}_{ck_short}_seed-{seed}.json"
    width, height = write_image(response, out)
    info_meta: dict[str, object] = {}
    try:
        info_meta = json.loads(response.get("info", "{}"))
    except json.JSONDecodeError:
        info_meta = {"raw_info_string": response.get("info", "")[:512]}
    sidecar_obj = {
        "character": character_id,
        "variant": variant,
        "seed": seed,
        "checkpoint_requested": args.checkpoint or None,
        "response_info": info_meta,
        "request": payload,
    }
    sidecar.write_text(
        json.dumps(sidecar_obj, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"[ok] {out.name} ({out.stat().st_size} bytes, {width}x{height}) "
        f"actual_model={info_meta.get('sd_model_name','?')} "
        f"actual_sampler={info_meta.get('sampler_name','?')} "
        f"actual_seed={info_meta.get('seed','?')}"
    )
    return out


def run_smoke_override(args, out_dir: Path) -> int:
    print("[smoke] confirming A1111 honors override_settings.sd_model_checkpoint")
    print(f"[smoke] requested override target: {args.checkpoint}")
    base_seed = args.base_seed

    call_payload_with = {
        "prompt": "SENTINEL_OVERRIDE_ON: simple red apple on plain background",
        "negative_prompt": "watermark, text, logo, blurry",
        "steps": 14,
        "cfg_scale": 6.5,
        "width": 512,
        "height": 512,
        "sampler_name": "Euler a",
        "scheduler": args.scheduler,
        "seed": base_seed,
        "batch_size": 1,
        "n_iter": 1,
        "override_settings": {"sd_model_checkpoint": args.checkpoint},
        "override_settings_restore_afterwards": True,
    }
    r1 = post_payload(call_payload_with, timeout=120)
    info1 = json.loads(r1.get("info", "{}"))
    out1 = out_dir / f"smoke_override_ON_seed-{base_seed}.png"
    write_image(r1, out1)

    call_payload_off = dict(call_payload_with)
    call_payload_off.pop("override_settings", None)
    call_payload_off.pop("override_settings_restore_afterwards", None)
    call_payload_off["prompt"] = (
        "SENTINEL_OVERRIDE_OFF: simple red apple on plain background"
    )
    call_payload_off["seed"] = base_seed + 1
    r2 = post_payload(call_payload_off, timeout=120)
    info2 = json.loads(r2.get("info", "{}"))
    out2 = out_dir / f"smoke_override_OFF_seed-{base_seed + 1}.png"
    write_image(r2, out2)

    model_on = info1.get("sd_model_name", "?")
    model_off = info2.get("sd_model_name", "?")
    different = model_on != model_off
    smoke_obj = {
        "with_override": {
            "requested_checkpoint": args.checkpoint,
            "filename": out1.name,
            "actual_model": model_on,
            "actual_sampler": info1.get("sampler_name"),
        },
        "without_override": {
            "filename": out2.name,
            "actual_model": model_off,
            "actual_sampler": info2.get("sampler_name"),
        },
        "verdict": (
            "OK: override took effect (different models)"
            if different
            else "BLOCKED: same model regardless of override - override_settings.sd_model_checkpoint not honored on this server"
        ),
    }
    smoke_path = out_dir / f"smoke_override_seed-{base_seed}.json"
    smoke_path.write_text(
        json.dumps(smoke_obj, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(f"[smoke] call-1 actual_model={model_on}")
    print(f"[smoke] call-2 actual_model={model_off}")
    print(f"[smoke] {smoke_obj['verdict']}")
    print(f"[smoke] sidecar: {smoke_path}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--character",
        choices=list(CHARACTERS.keys()) + ["both"],
        default="both",
    )
    parser.add_argument(
        "--variant",
        choices=["trigger", "notrigger", "both"],
        default="both",
    )
    parser.add_argument("--seeds", type=int, default=2)
    parser.add_argument("--base-seed", type=int, default=1302777804)
    parser.add_argument(
        "--checkpoint",
        default="hassakuXLIllustrious_v34.safetensors [1618edb443]",
        help=(
            "Model override target. Pass an empty string '' to skip the "
            "override entirely and use whatever A1111 currently has loaded."
        ),
    )
    parser.add_argument("--sampler", default="Euler a")
    parser.add_argument("--scheduler", default="karras")
    parser.add_argument("--steps", type=int, default=28)
    parser.add_argument("--cfg_scale", type=float, default=7.0)
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=-1)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument(
        "--smoke-override",
        action="store_true",
        help="Run ONLY the 2-call override smoke test; skip the full regen.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.smoke_override:
        return run_smoke_override(args, out_dir)
    characters = list(CHARACTERS.keys()) if args.character == "both" else [args.character]
    variants = ["trigger", "notrigger"] if args.variant == "both" else [args.variant]
    seeds = [args.base_seed + (9973 * i) for i in range(args.seeds)]
    print(f"[plan] characters={characters}  variants={variants}  seeds={seeds}")
    for cid in characters:
        print(f"[character] {CHARACTERS[cid]['label']}")
        for variant in variants:
            for seed in seeds:
                run_variant(args, cid, variant, seed, out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
