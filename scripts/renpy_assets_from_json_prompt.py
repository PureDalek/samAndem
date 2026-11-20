#!/usr/bin/env python3
"""Generate 18+ Ren'Py-ready image assets from JSON prompts via Automatic1111.

The script sends the prompt payload you provide to your local A1111 API, then
saves the returned images and optional Ren'Py destination copies.

Content policy: every depicted character must be a fictional adult aged 18 or
older. The built-in presets ban minors, non-consent, coercion, blackmail,
mind-control consent, assault, and bestiality. Preset wording allows R-rated
18+ adult nudity and intimate framing rather than euphemistic 'covered'
language.
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
from copy import deepcopy
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from scene_image_profile import LOCKED_PROFILE_PATH, load_profile
from local_scene_image_pipeline import (
    DEFAULT_CHARACTER_PROFILE,
    SAFETY_NEGATIVE,
    build_character_context,
)


DEFAULT_API_URL = "http://127.0.0.1:7860"
DEFAULT_OUTPUT_DIR = "art/generated"
DEFAULT_RENPY_PATTERN = "game/images/nsfw/{character}/{slot}.png"
DEFAULT_QUALITY_PRESET = "samandem_sdxl_sprite"

BUILTIN_QUALITY_PRESETS: dict[str, dict[str, Any]] = {
    "samandem_sdxl_sprite": {
        "checkpoint": "hassakuXLIllustrious_v34.safetensors [1618edb443]",
        "prompt_prefix": (
            "masterpiece, best quality, highres, polished anime visual novel character sprite, "
            "professional game asset, refined face, expressive detailed eyes, detailed hair, "
            "confident clean linework, soft cel shading, smooth skin rendering, crisp silhouette"
        ),
        "prompt_suffix": (
            "single character only, one uninterrupted full body, centered composition, clean blank studio background, "
            "balanced anatomy, sharp focus, premium cloud-generation quality"
        ),
        "negative_prompt": (
            "worst quality, low quality, normal quality, lowres, blurry, jpeg artifacts, sketch, "
            "unfinished, bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, "
            "deformed hands, distorted face, crossed eyes, asymmetrical eyes, bad proportions, "
            "mutated limbs, extra arms, extra legs, cropped head, cropped feet, out of frame, "
            "character sheet, reference sheet, design sheet, multiple views, multiple poses, collage, "
            "split screen, side panel, inset portrait, thumbnails, duplicate character, extra face, "
            "watermark, signature, text, logo, see-through clothing for non-consent framing, "
            "minor, child, teen, underage, loli, shota, schoolgirl, schoolboy, "
            "non-consent, coercion, blackmail, mind-control consent, assault, bestiality"
        ),
        "payload": {
            "steps": 36,
            "cfg_scale": 6.5,
            "width": 768,
            "height": 1152,
            "sampler_name": "DPM++ 2M",
            "scheduler": "Karras",
            "seed": 314159265,
            "subseed_strength": 0,
            "batch_size": 1,
            "n_iter": 1,
            "enable_hr": True,
            "hr_scale": 1.25,
            "hr_upscaler": "R-ESRGAN 4x+ Anime6B",
            "hr_second_pass_steps": 14,
            "denoising_strength": 0.35,
            "restore_faces": False,
        },
        "adetailer": {
            "enabled": True,
            "model": "face_yolov8n.pt",
            "prompt": "beautiful detailed face, symmetrical eyes, polished anime eyes, clean eyelashes",
            "negative_prompt": "deformed face, bad eyes, crossed eyes, lazy eye, distorted mouth",
            "denoising_strength": 0.28,
            "inpaint_only_masked": True,
            "inpaint_padding": 32,
        },
    },
    "samandem_sdxl_cg": {
        "checkpoint": "hassakuXLIllustrious_v34.safetensors [1618edb443]",
        "prompt_prefix": (
            "masterpiece, best quality, highres, polished cinematic anime visual novel CG, "
            "professional game art, detailed eyes, detailed hair, clean linework, soft cel shading, "
            "dramatic but readable lighting"
        ),
        "prompt_suffix": "single scene, no panels, balanced composition, sharp focus, premium cloud-generation quality",
        "negative_prompt": (
            "worst quality, low quality, normal quality, lowres, blurry, bad anatomy, bad hands, "
            "extra fingers, missing fingers, character sheet, reference sheet, collage, split screen, "
            "side panel, inset portrait, thumbnails, duplicate character, extra face, watermark, signature, text, logo, "
            "minor, child, teen, underage, loli, shota, schoolgirl, schoolboy, "
            "non-consent, coercion, blackmail, mind-control consent, assault, bestiality"
        ),
        "payload": {
            "steps": 34,
            "cfg_scale": 6.5,
            "width": 1024,
            "height": 768,
            "sampler_name": "DPM++ 2M",
            "scheduler": "Karras",
            "seed": 271828182,
            "batch_size": 1,
            "n_iter": 1,
            "enable_hr": True,
            "hr_scale": 1.25,
            "hr_upscaler": "R-ESRGAN 4x+ Anime6B",
            "hr_second_pass_steps": 12,
            "denoising_strength": 0.32,
            "restore_faces": False,
        },
        "adetailer": {
            "enabled": True,
            "model": "face_yolov8n.pt",
            "prompt": "beautiful detailed face, symmetrical eyes, polished anime eyes",
            "negative_prompt": "deformed face, bad eyes, crossed eyes, distorted mouth",
            "denoising_strength": 0.25,
            "inpaint_only_masked": True,
            "inpaint_padding": 32,
        },
    },
}

CONTROL_KEYS = {
    "api_url",
    "assets",
    "base_dir",
    "base_seed",
    "character",
    "copies",
    "copy_to",
    "defaults",
    "endpoint",
    "filename",
    "adetailer",
    "character_anchor",
    "checkpoint",
    "characters",
    "init_image",
    "init_images",
    "mask",
    "metadata",
    "model",
    "name",
    "output_dir",
    "overwrite",
    "overwrite_renpy",
    "payload",
    "preset",
    "prompt_prefix",
    "prompt_suffix",
    "negative_prefix",
    "negative_suffix",
    "quality_preset",
    "quality_presets",
    "renpy_path",
    "renpy_pattern",
    "renpy_root",
    "save_metadata",
    "scene",
    "seed_count",
    "seed_step",
    "slot",
    "style_anchor",
    "timestamp_output_dir",
    "use_default_quality_preset",
}


class ConfigError(ValueError):
    """Raised when the prompt JSON cannot be interpreted."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate image assets from a JSON prompt batch using a local "
            "Automatic1111 --api server."
        )
    )
    parser.add_argument(
        "prompt_json",
        type=Path,
        nargs="?",
        help="JSON file containing one prompt or an assets list.",
    )
    parser.add_argument("--settings-profile", type=Path, default=LOCKED_PROFILE_PATH)
    parser.add_argument("--no-settings-profile", action="store_true", help="Ignore the scene GUI settings profile.")
    parser.add_argument("--character-profile", type=Path, default=DEFAULT_CHARACTER_PROFILE)
    parser.add_argument(
        "--api-url",
        default=None,
        help=f"A1111 API root. Defaults to JSON api_url or {DEFAULT_API_URL}.",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory used to resolve relative input/output paths. Defaults to the current directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=f"Override generated output directory. Defaults to JSON output_dir or {DEFAULT_OUTPUT_DIR}.",
    )
    parser.add_argument(
        "--renpy-root",
        type=Path,
        default=None,
        help="Ren'Py project root used with character/slot destinations.",
    )
    parser.add_argument("--timeout", type=int, default=300, help="HTTP timeout in seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print requests without calling A1111.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing generated files when an exact output filename already exists.",
    )
    parser.add_argument(
        "--overwrite-renpy",
        action="store_true",
        help="Allow replacing files copied into Ren'Py destination paths.",
    )
    parser.add_argument("--no-metadata", action="store_true", help="Skip sidecar metadata and manifest JSON files.")
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Check the configured A1111 server, model, sampler, and ADetailer detector before generation.",
    )
    parser.add_argument(
        "--list-resources",
        action="store_true",
        help="Print local A1111 models, samplers, and ADetailer detectors, then exit.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise ConfigError(f"Prompt JSON not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc

    if isinstance(data, list):
        return {"assets": data}
    if not isinstance(data, dict):
        raise ConfigError("Prompt JSON must be an object, an assets object, or a list of assets.")
    if "assets" not in data and "prompt" in data:
        config = {
            key: value
            for key, value in data.items()
            if key in {
                "api_url",
                "adetailer",
                "checkpoint",
                "character_anchor",
                "defaults",
                "model",
                "negative_prefix",
                "negative_suffix",
                "output_dir",
                "preset",
                "prompt_prefix",
                "prompt_suffix",
                "quality_preset",
                "quality_presets",
                "renpy_pattern",
                "renpy_root",
                "scene",
                "style_anchor",
                "use_default_quality_preset",
            }
        }
        config["assets"] = [data]
        return config
    if "assets" not in data:
        raise ConfigError("Prompt JSON must contain an 'assets' list or a top-level 'prompt'.")
    if not isinstance(data["assets"], list):
        raise ConfigError("'assets' must be a list.")
    return data


def resolve_path(value: str | Path, base_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def slugify(value: Any, fallback: str = "asset") -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9._-]+", "_", text)
    text = text.strip("._-")
    return text or fallback


def read_image_base64(path_value: str | Path, base_dir: Path) -> str:
    path = resolve_path(path_value, base_dir)
    if not path.exists() and not Path(path_value).is_absolute():
        renpy_project_path = resolve_path(Path("Sam And Em") / Path(path_value), base_dir)
        if renpy_project_path.exists():
            path = renpy_project_path
    if not path.exists():
        raise ConfigError(f"Image file not found: {path}")
    return base64.b64encode(path.read_bytes()).decode("ascii")


def strip_base64_prefix(value: str) -> str:
    if "," in value and value[:32].lower().startswith("data:image"):
        return value.split(",", 1)[1]
    return value


def decode_image(value: str) -> bytes:
    try:
        return base64.b64decode(strip_base64_prefix(value), validate=False)
    except ValueError as exc:
        raise RuntimeError("A1111 returned an image that could not be decoded.") from exc


def merge_dicts(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in update.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def listify(value: Any, field_name: str) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value]
    raise ConfigError(f"'{field_name}' must be a string or list.")


def clean_prompt_fragment(value: Any) -> str:
    return str(value).strip().strip(",")


def join_prompt_parts(parts: list[Any]) -> str:
    seen: set[str] = set()
    cleaned: list[str] = []
    for part in parts:
        text = clean_prompt_fragment(part)
        if not text:
            continue
        key = re.sub(r"\s+", " ", text.lower())
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(text)
    return ", ".join(cleaned)


def stable_seed(value: str) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 2147483647


def load_settings(args: argparse.Namespace, base_dir: Path) -> dict[str, Any]:
    if args.no_settings_profile:
        return {}
    profile_path = resolve_path(args.settings_profile, base_dir)
    try:
        return load_profile(profile_path)
    except FileNotFoundError:
        return {}


def profile_payload_defaults(settings: dict[str, Any]) -> dict[str, Any]:
    defaults: dict[str, Any] = {}
    for key in ("width", "height", "steps", "seed", "batch_size", "n_iter"):
        value = settings.get(key)
        if value not in (None, ""):
            defaults[key] = int(value)
    for source_key, payload_key in (("cfg_scale", "cfg_scale"), ("denoise", "denoising_strength")):
        value = settings.get(source_key)
        if value not in (None, ""):
            defaults[payload_key] = float(value)
    if settings.get("sampler"):
        defaults["sampler_name"] = str(settings["sampler"])
    if settings.get("scheduler"):
        defaults["scheduler"] = str(settings["scheduler"])
    if settings.get("checkpoint"):
        defaults["override_settings"] = {"sd_model_checkpoint": str(settings["checkpoint"])}
        defaults["override_settings_restore_afterwards"] = True
    return defaults


def configured_characters(asset: dict[str, Any]) -> str | None:
    value = asset.get("characters")
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    if isinstance(value, str):
        return value
    if asset.get("character"):
        return str(asset["character"])
    return None


def asset_scene_text(asset: dict[str, Any], payload: dict[str, Any]) -> str:
    parts = [
        str(asset.get("name", "")),
        str(asset.get("scene", "")),
        str(asset.get("character_anchor", "")),
        str(asset.get("prompt", "")),
        str(payload.get("prompt", "")),
    ]
    return ", ".join(part for part in parts if part.strip())


def profile_text(settings: dict[str, Any], key: str) -> str:
    value = settings.get(key, "")
    return str(value).strip() if value is not None else ""


def selected_preset_names(config: dict[str, Any], asset: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for source in (config, asset):
        for key in ("quality_preset", "preset"):
            names.extend(str(item) for item in listify(source.get(key), key))
    return names


def available_quality_presets(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    presets = deepcopy(BUILTIN_QUALITY_PRESETS)
    custom = config.get("quality_presets", {})
    if custom is None:
        custom = {}
    if not isinstance(custom, dict):
        raise ConfigError("'quality_presets' must be an object when provided.")
    for name, preset in custom.items():
        if not isinstance(preset, dict):
            raise ConfigError(f"Quality preset {name!r} must be an object.")
        presets[str(name)] = preset
    return presets


def preset_stack(config: dict[str, Any], asset: dict[str, Any]) -> list[dict[str, Any]]:
    names = selected_preset_names(config, asset)
    if not names and (config.get("use_default_quality_preset") or asset.get("use_default_quality_preset")):
        names = [DEFAULT_QUALITY_PRESET]
    presets = available_quality_presets(config)
    stack: list[dict[str, Any]] = []
    for name in names:
        if name not in presets:
            available = ", ".join(sorted(presets))
            raise ConfigError(f"Unknown quality preset {name!r}. Available presets: {available}")
        stack.append(presets[name])
    return stack


def collect_text(config: dict[str, Any], asset: dict[str, Any], presets: list[dict[str, Any]], key: str) -> list[Any]:
    values: list[Any] = []
    for preset in presets:
        values.extend(listify(preset.get(key), key))
    values.extend(listify(config.get(key), key))
    values.extend(listify(asset.get(key), key))
    return values


def requested_checkpoint(
    config: dict[str, Any],
    asset: dict[str, Any],
    presets: list[dict[str, Any]],
    settings: dict[str, Any],
) -> str | None:
    checkpoint = None
    for preset in presets:
        checkpoint = preset.get("checkpoint") or preset.get("model") or checkpoint
    checkpoint = settings.get("checkpoint") or checkpoint
    checkpoint = config.get("checkpoint") or config.get("model") or checkpoint
    checkpoint = asset.get("checkpoint") or asset.get("model") or checkpoint
    if checkpoint is None:
        retuצNone
    return str(checkpoint)


def apply_checkpoint(payload: dict[str, Any], checkpoint: str | None) -> None:
    if not checkpoint:
        return
    overrides = dict(payload.get("override_settings") or {})
    overrides["sd_model_checkpoint"] = checkpoint
    payload["override_settings"] = overrides
    payload.setdefault("override_settings_restore_afterwards", True)


def merged_adetailer(config: dict[str, Any], asset: dict[str, Any], presets: list[dict[str, Any]]) -> Any:
    merged: Any = None
    for source in [*presets, config, asset]:
        value = source.get("adetailer")
        if value is None:
            continue
        if isinstance(value, dict) and isinstance(merged, dict):
            merged = merge_dicts(merged, value)
        else:
            merged = deepcopy(value)
    return merged


def adetailer_arg_from_object(value: dict[str, Any]) -> dict[str, Any]:
    if value.get("enabled") is False:
        return {"ad_model": "None", "ad_tab_enable": False}
    arg = {
        "ad_model": str(value.get("model") or value.get("ad_model") or "face_yolov8n.pt"),
        "ad_tab_enable": True,
        "ad_prompt": str(value.get("prompt") or value.get("ad_prompt") or ""),
        "ad_negative_prompt": str(value.get("negative_prompt") or value.get("ad_negative_prompt") or ""),
        "ad_confidence": float(value.get("confidence", value.get("ad_confidence", 0.3))),
        "ad_denoising_strength": float(value.get("denoising_strength", value.get("ad_denoising_strength", 0.28))),
        "ad_inpaint_only_masked": bool(value.get("inpaint_only_masked", value.get("ad_inpaint_only_masked", True))),
        "ad_inpaint_only_masked_padding": int(value.get("inpaint_padding", value.get("ad_inpaint_only_masked_padding", 32))),
    }
    if "mask_min_ratio" in value or "ad_mask_min_ratio" in value:
        arg["ad_mask_min_ratio"] = float(value.get("mask_min_ratio", value.get("ad_mask_min_ratio")))
    if "mask_max_ratio" in value or "ad_mask_max_ratio" in value:
        arg["ad_mask_max_ratio"] = float(value.get("mask_max_ratio", value.get("ad_mask_max_ratio")))
    if "steps" in value or "ad_steps" in value:
        arg["ad_use_steps"] = True
        arg["ad_steps"] = int(value.get("steps", value.get("ad_steps")))
    if "cfg_scale" in value or "ad_cfg_scale" in value:
        arg["ad_use_cfg_scale"] = True
        arg["ad_cfg_scale"] = float(value.get("cfg_scale", value.get("ad_cfg_scale")))
    return arg


def apply_adetailer(payload: dict[str, Any], value: Any) -> None:
    if value in (None, False):
        return
    if value is True:
        value = {}
    if isinstance(value, dict):
        args = [adetailer_arg_from_object(value)]
    elif isinstance(value, list):
        args = [adetailer_arg_from_object(item) if isinstance(item, dict) else item for item in value]
    else:
        raise ConfigError("'adetailer' must be an object, list, true, or false.")

    scripts = dict(payload.get("alwayson_scripts") or {})
    existing = scripts.get("ADetailer") or scripts.get("adetailer") or {}
    existing_args = list(existing.get("args") or [])
    existing["args"] = [*existing_args, *args]
    scripts["ADetailer"] = existing
    payload["alwayson_scripts"] = scripts


def expand_seed_payloads(payload: dict[str, Any], asset: dict[str, Any]) -> list[tuple[int, dict[str, Any]]]:
    raw_count = asset.get("seed_count", 1)
    try:
        seed_count = int(raw_count)
    except (TypeError, ValueError) as exc:
        raise ConfigError("'seed_count' must be an integer.") from exc
    if seed_count < 1:
        raise ConfigError("'seed_count' must be at least 1.")

    raw_step = asset.get("seed_step", 9973)
    try:
        seed_step = int(raw_step)
    except (TypeError, ValueError) as exc:
        raise ConfigError("'seed_step' must be an integer.") from exc

    seed = asset.get("base_seed", payload.get("seed"))
    if seed in (None, -1, "-1"):
        seed = stable_seed(str(asset.get("name") or payload.get("prompt") or "asset"))
    try:
        base_seed = int(seed)
    except (TypeError, ValueError) as exc:
        raise ConfigError("'base_seed' or payload seed must be an integer.") from exc

    if seed_count == 1:
        locked_payload = deepcopy(payload)
        locked_payload["seed"] = base_seed
        return [(0, locked_payload)]

    expanded: list[tuple[int, dict[str, Any]]] = []
    for index in range(seed_count):
        variant_payload = deepcopy(payload)
        variant_payload["seed"] = (base_seed + index * seed_step) % 2147483647
        expanded.append((index, variant_payload))
    return expanded


def compose_profile_prompts(
    args: argparse.Namespace,
    config: dict[str, Any],
    asset: dict[str, Any],
    payload: dict[str, Any],
    settings: dict[str, Any],
    base_dir: Path,
    presets: list[dict[str, Any]],
) -> None:
    scene_text = asset_scene_text(asset, payload)
    context_args = argparse.Namespace(
        character_profile=args.character_profile,
        characters=configured_characters(asset),
    )
    character_context = build_character_context(scene_text, context_args, base_dir)

    positive = join_prompt_parts(
        [
            profile_text(settings, "style_prefix"),
            *collect_text(config, asset, presets, "prompt_prefix"),
            *collect_text(config, asset, presets, "style_anchor"),
            *collect_text(config, asset, presets, "character_anchor"),
            str(character_context.get("positive_prompt", "")),
            *collect_text(config, asset, presets, "scene"),
            str(payload.get("prompt", "")),
            *collect_text(config, asset, presets, "prompt_suffix"),
            profile_text(settings, "guidelines"),
            profile_text(settings, "extra_positive"),
            profile_text(settings, "style_suffix"),
        ]
    )

    negative = join_prompt_parts(
        [
            profile_text(settings, "negative_prompt"),
            str(character_context.get("negative_prompt", "")),
            *(preset.get("negative_prompt") for preset in presets),
            *collect_text(config, asset, presets, "negative_prefix"),
            str(payload.get("negative_prompt", "")),
            *collect_text(config, asset, presets, "negative_suffix"),
            profile_text(settings, "extra_negative"),
            profile_text(settings, "always_negative"),
            SAFETY_NEGATIVE,
        ]
    )

    if positive:
        payload["prompt"] = positive
    if negative:
        payload["negative_prompt"] = negative


def build_payload(
    config: dict[str, Any],
    asset: dict[str, Any],
    base_dir: Path,
    settings: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[str, dict[str, Any]]:
    if not isinstance(asset, dict):
        raise ConfigError("Each asset entry must be a JSON object.")

    presets = preset_stack(config, asset)
    defaults = config.get("defaults", {})
    if defaults is None:
        defaults = {}
    if not isinstance(defaults, dict):
        raise ConfigError("'defaults' must be an object when provided.")

    payload: dict[str, Any] = {}
    for preset in presets:
        preset_payload = preset.get("payload", preset.get("defaults", {}))
        if preset_payload is None:
            preset_payload = {}
        if not isinstance(preset_payload, dict):
            raise ConfigError("Quality preset payload/defaults must be an object.")
        payload = merge_dicts(payload, preset_payload)
    payload = merge_dicts(payload, profile_payload_defaults(settings))
    payload = merge_dicts(payload, defaults)
    direct_payload = asset.get("payload", {})
    if direct_payload is None:
        direct_payload = {}
    if not isinstance(direct_payload, dict):
        raise ConfigError("'payload' must be an object when provided.")
    payload = merge_dicts(payload, direct_payload)

    for key, value in asset.items():
        if key not in CONTROL_KEYS:
            payload[key] = value

    compose_profile_prompts(args, config, asset, payload, settings, base_dir, presets)
    apply_checkpoint(payload, requested_checkpoint(config, asset, presets, settings))
    apply_adetailer(payload, merged_adetailer(config, asset, presets))

    endpoint = str(asset.get("endpoint") or "").strip().lower()
    has_init_image = "init_image" in asset or "init_images" in asset or "init_images" in payload
    if not endpoint:
        endpoint = "img2img" if has_init_image else "txt2img"
    if endpoint not in {"txt2img", "img2img"}:
        raise ConfigError(f"Unsupported endpoint '{endpoint}'. Use 'txt2img' or 'img2img'.")

    if "prompt" not in payload or not str(payload["prompt"]).strip():
        name = asset.get("name", "<unnamed>")
        raise ConfigError(f"Asset {name!r} is missing a prompt.")

    if endpoint == "img2img":
        init_images = []
        if "init_image" in asset:
            init_images.append(asset["init_image"])
        if "init_images" in asset:
            if not isinstance(asset["init_images"], list):
                raise ConfigError("'init_images' must be a list when provided.")
            init_images.extend(asset["init_images"])
        if init_images:
            payload["init_images"] = [read_image_base64(path, base_dir) for path in init_images]
        if "mask" in asset:
            payload["mask"] = read_image_base64(asset["mask"], base_dir)
        if "init_images" not in payload:
            raise ConfigError("img2img assets need init_image, init_images, or payload.init_images.")

    return endpoint, payload


def post_a1111(api_url: str, endpoint: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    url = f"{api_url.rstrip('/')}/sdapi/v1/{endpoint}"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"A1111 returned HTTP {exc.code} for {endpoint}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Could not reach A1111 at {api_url}. Make sure webui is running with --api."
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("A1111 returned a response that was not valid JSON.") from exc


def get_a1111(api_url: str, path: str, timeout: int) -> Any:
    url = f"{api_url.rstrip('/')}{path}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"A1111 returned HTTP {exc.code} for {path}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Could not reach A1111 at {api_url}. Make sure webui is running with --api."
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"A1111 returned invalid JSON for {path}.") from exc


def collect_resource_names(api_url: str, timeout: int) -> dict[str, set[str]]:
    models = get_a1111(api_url, "/sdapi/v1/sd-models", timeout)
    samplers = get_a1111(api_url, "/sdapi/v1/samplers", timeout)
    try:
        adetailer_models = get_a1111(api_url, "/adetailer/v1/ad_model", timeout).get("ad_model", [])
    except RuntimeError:
        adetailer_models = []

    model_names: set[str] = set()
    for model in models:
        for key in ("title", "model_name", "filename"):
            value = model.get(key)
            if value:
                model_names.add(str(value))

    sampler_names = {str(sampler.get("name")) for sampler in samplers if sampler.get("name")}
    adetailer_names = {str(name) for name in adetailer_models}
    return {"models": model_names, "samplers": sampler_names, "adetailer": adetailer_names}


def list_resources(api_url: str, timeout: int) -> None:
    resources = collect_resource_names(api_url, timeout)
    for label in ("models", "samplers", "adetailer"):
        print(f"{label}:")
        for name in sorted(resources[label]):
            print(f"  {name}")


def sampler_is_available(requested: str, available: set[str]) -> bool:
    if requested in available:
        return True
    scheduler_suffixes = (" Karras", " Exponential", " Polyexponential", " Automatic")
    for suffix in scheduler_suffixes:
        if requested.endswith(suffix) and requested[: -len(suffix)] in available:
            return True
    return False


def adetailer_models_from_payload(payload: dict[str, Any]) -> list[str]:
    scripts = payload.get("alwayson_scripts")
    if not isinstance(scripts, dict):
        return []
    adetailer = scripts.get("ADetailer") or scripts.get("adetailer")
    if not isinstance(adetailer, dict):
        return []
    models: list[str] = []
    for arg in adetailer.get("args") or []:
        if isinstance(arg, dict):
            model = arg.get("ad_model")
            if model and model != "None":
                models.append(str(model))
    return models


def preflight_config(
    config: dict[str, Any],
    args: argparse.Namespace,
    base_dir: Path,
    api_url: str,
    settings: dict[str, Any],
) -> None:
    resources = collect_resource_names(api_url, args.timeout)
    for asset in config["assets"]:
        endpoint, payload = build_payload(config, asset, base_dir, settings, args)
        name = str(asset.get("name") or payload.get("prompt", "asset")[:40])
        checkpoint = (payload.get("override_settings") or {}).get("sd_model_checkpoint")
        if checkpoint and str(checkpoint) not in resources["models"]:
            raise ConfigError(f"Asset {name!r} requests missing checkpoint: {checkpoint}")
        sampler = payload.get("sampler_name")
        if sampler and not sampler_is_available(str(sampler), resources["samplers"]):
            raise ConfigError(f"Asset {name!r} requests missing sampler: {sampler}")
        for ad_model in adetailer_models_from_payload(payload):
            if resources["adetailer"] and ad_model not in resources["adetailer"]:
                raise ConfigError(f"Asset {name!r} requests missing ADetailer detector: {ad_model}")
        print(f"[preflight] {name}: {endpoint} resources ok")


def ensure_output_path(path: Path, overwrite: bool) -> Path:
    if overwrite or not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    for number in range(1, 10000):
        candidate = path.with_name(f"{stem}_{number:03d}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find an available filename near {path}")


def render_template(template: str, context: dict[str, Any]) -> str:
    try:
        return template.format(**context)
    except KeyError as exc:
        raise ConfigError(f"Unknown template key {exc} in {template!r}") from exc
    except ValueError as exc:
        raise ConfigError(f"Invalid template {template!r}: {exc}") from exc


def output_directory(
    args: argparse.Namespace,
    config: dict[str, Any],
    asset: dict[str, Any],
    base_dir: Path,
) -> Path:
    raw = args.output_dir or asset.get("output_dir") or config.get("output_dir") or DEFAULT_OUTPUT_DIR
    return resolve_path(raw, base_dir)


def output_filename(
    asset: dict[str, Any],
    image_index: int,
    total_images: int,
    run_stamp: str,
    seed: int | None = None,
    variant_index: int | None = None,
) -> str:
    name = slugify(asset.get("name", "asset"))
    template = str(asset.get("filename") or f"{name}_{run_stamp}.png")
    context = {
        "name": name,
        "raw_name": str(asset.get("name", name)),
        "character": slugify(asset.get("character", "")),
        "slot": slugify(asset.get("slot", "")),
        "index": image_index + 1,
        "index0": image_index,
        "seed": seed if seed is not None else "",
        "variant": (variant_index + 1) if variant_index is not None else image_index + 1,
        "variant0": variant_index if variant_index is not None else image_index,
        "stamp": run_stamp,
    }
    rendered = render_template(template, context)
    path = Path(rendered)
    suffix = path.suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        suffix = ".png"
        stem = slugify(path.name)
    else:
        stem = slugify(path.stem)
    variant_tokens = ("{index", "{index0", "{variant", "{variant0", "{seed")
    if total_images > 1 and not any(token in template for token in variant_tokens):
        stem = f"{stem}_{image_index + 1:02d}"
    return f"{stem}{suffix}"


def template_context(
    asset: dict[str, Any],
    image_index: int,
    run_stamp: str,
    seed: int | None = None,
    variant_index: int | None = None,
) -> dict[str, Any]:
    return {
        "name": slugify(asset.get("name", "asset")),
        "raw_name": str(asset.get("name", "asset")),
        "character": slugify(asset.get("character", "")),
        "slot": slugify(asset.get("slot", "")),
        "index": image_index + 1,
        "index0": image_index,
        "seed": seed if seed is not None else "",
        "variant": (variant_index + 1) if variant_index is not None else image_index + 1,
        "variant0": variant_index if variant_index is not None else image_index,
        "stamp": run_stamp,
    }


def destination_templates(
    args: argparse.Namespace,
    config: dict[str, Any],
    asset: dict[str, Any],
    base_dir: Path,
) -> list[str]:
    templates: list[str] = []

    for key in ("renpy_path", "copy_to"):
        value = asset.get(key)
        if isinstance(value, str):
            templates.append(value)
        elif isinstance(value, list):
            templates.extend(str(item) for item in value)
        elif value is not None:
            raise ConfigError(f"'{key}' must be a string or list of strings.")

    copies = asset.get("copies")
    if isinstance(copies, str):
        templates.append(copies)
    elif isinstance(copies, list):
        templates.extend(str(item) for item in copies)
    elif copies is not None:
        raise ConfigError("'copies' must be a string or list of strings.")

    renpy_root = args.renpy_root or asset.get("renpy_root") or config.get("renpy_root")
    if renpy_root and asset.get("character") and asset.get("slot"):
        pattern = str(asset.get("renpy_pattern") or config.get("renpy_pattern") or DEFAULT_RENPY_PATTERN)
        root_path = resolve_path(renpy_root, base_dir)
        templates.append(str(root_path / pattern))

    return templates


def write_exact_bytes(path: Path, data: bytes, overwrite: bool) -> Path:
    if path.exists() and not overwrite:
        raise RuntimeError(f"Ren'Py destination already exists: {path}. Use --overwrite-renpy to replace it.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def parse_info(info: Any) -> Any:
    if not isinstance(info, str):
        return info
    try:
        return json.loads(info)
    except json.JSONDecodeError:
        return info


def redacted_payload(payload: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(payload)
    if "init_images" in redacted:
        redacted["init_images"] = [f"<base64 image {index + 1} omitted>" for index, _ in enumerate(redacted["init_images"])]
    if "mask" in redacted:
        redacted["mask"] = "<base64 mask omitted>"
    return redacted


def save_metadata(path: Path, metadata: dict[str, Any]) -> None:
    sidecar = path.with_suffix(".json")
    sidecar.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")


def process_asset(
    args: argparse.Namespace,
    config: dict[str, Any],
    asset: dict[str, Any],
    base_dir: Path,
    api_url: str,
    run_stamp: str,
    settings: dict[str, Any],
) -> dict[str, Any]:
    endpoint, payload = build_payload(config, asset, base_dir, settings, args)
    seed_payloads = expand_seed_payloads(payload, asset)
    name = str(asset.get("name") or payload.get("prompt", "asset")[:40])
    out_dir = output_directory(args, config, asset, base_dir)
    dest_templates = destination_templates(args, config, asset, base_dir)

    if args.dry_run:
        preview = str(payload["prompt"]).replace("\n", " ")[:140]
        print(f"[dry-run] {name}: {endpoint} -> {out_dir} ({len(seed_payloads)} request(s))")
        print(f"          prompt: {preview}")
        for variant_index, variant_payload in seed_payloads:
            seed = int(variant_payload.get("seed", -1))
            filename = output_filename(
                asset,
                variant_index,
                len(seed_payloads),
                run_stamp,
                seed=seed,
                variant_index=variant_index,
            )
            context = template_context(asset, variant_index, run_stamp, seed=seed, variant_index=variant_index)
            print(f"          file: {filename} (seed {seed})")
            for template in dest_templates:
                destination = resolve_path(render_template(template, context), base_dir)
                print(f"          renpy copy: {destination}")
        return {
            "name": name,
            "endpoint": endpoint,
            "dry_run": True,
            "output_dir": str(out_dir),
            "renpy_templates": dest_templates,
            "requests": len(seed_payloads),
        }

    out_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[str] = []
    renpy_outputs: list[str] = []
    infos: list[Any] = []
    total_images_hint = len(seed_payloads) * max(int(payload.get("batch_size", 1)), 1) * max(int(payload.get("n_iter", 1)), 1)

    for variant_index, variant_payload in seed_payloads:
        response = post_a1111(api_url, endpoint, variant_payload, args.timeout)
        images = response.get("images")
        if not isinstance(images, list) or not images:
            raise RuntimeError(f"A1111 did not return any images for asset {name!r}.")

        info = parse_info(response.get("info"))
        infos.append(info)
        seed = int(variant_payload.get("seed", -1))

        for image_base64 in images:
            image_index = len(outputs)
            image_bytes = decode_image(str(image_base64))
            filename = output_filename(
                asset,
                image_index,
                total_images_hint,
                run_stamp,
                seed=seed,
                variant_index=variant_index,
            )
            output_path = ensure_output_path(out_dir / filename, args.overwrite)
            output_path.write_bytes(image_bytes)
            outputs.append(str(output_path))

            context = template_context(asset, image_index, run_stamp, seed=seed, variant_index=variant_index)
            image_renpy_outputs: list[str] = []
            for template in dest_templates:
                if image_index > 0 and "{index" not in template and "{index0" not in template:
                    continue
                destination = resolve_path(render_template(template, context), base_dir)
                written = write_exact_bytes(destination, image_bytes, args.overwrite_renpy)
                image_renpy_outputs.append(str(written))
                renpy_outputs.append(str(written))

            if not args.no_metadata:
                save_metadata(
                    output_path,
                    {
                        "asset": name,
                        "endpoint": endpoint,
                        "api_url": api_url,
                        "variant": variant_index + 1,
                        "seed": seed,
                        "request": redacted_payload(variant_payload),
                        "a1111_info": info,
                        "renpy_outputs": image_renpy_outputs,
                    },
                )

    print(f"[ok] {name}: wrote {len(outputs)} image(s)")
    for output in outputs:
        print(f"     {output}")
    for output in renpy_outputs:
        print(f"     copied to {output}")

    return {
        "name": name,
        "endpoint": endpoint,
        "outputs": outputs,
        "renpy_outputs": renpy_outputs,
        "a1111_info": infos[0] if len(infos) == 1 else infos,
    }


def main() -> int:
    args = parse_args()
    base_dir = args.base_dir.resolve()

    try:
        settings = load_settings(args, base_dir)
        if args.list_resources:
            api_url = str(args.api_url or settings.get("a1111_url") or DEFAULT_API_URL)
            list_resources(api_url, args.timeout)
            return 0
        if args.prompt_json is None:
            raise ConfigError("Prompt JSON is required unless --list-resources is used.")
        config = load_json(args.prompt_json)
        api_url = str(args.api_url or config.get("api_url") or settings.get("a1111_url") or DEFAULT_API_URL)
        if args.preflight:
            preflight_config(config, args, base_dir, api_url, settings)
        run_stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        results = [
            process_asset(args, config, asset, base_dir, api_url, run_stamp, settings)
            for asset in config["assets"]
        ]

        if not args.dry_run and not args.no_metadata:
            manifest_dir = resolve_path(args.output_dir or config.get("output_dir") or DEFAULT_OUTPUT_DIR, base_dir)
            manifest_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = manifest_dir / f"manifest_{run_stamp}.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "generated_at": run_stamp,
                        "prompt_json": str(args.prompt_json.resolve()),
                        "api_url": api_url,
                        "settings_profile": None if args.no_settings_profile else str(resolve_path(args.settings_profile, base_dir)),
                        "results": results,
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            print(f"[ok] manifest: {manifest_path}")
        return 0
    except (ConfigError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
