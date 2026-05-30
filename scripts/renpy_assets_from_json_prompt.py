#!/usr/bin/env python3
"""Generate Ren'Py-ready image assets from JSON prompts via Automatic1111.

The script intentionally keeps policy and prompt restrictions out of the
client. It sends the prompt payload you provide to your local A1111 API, then
saves the returned images and optional Ren'Py destination copies.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_API_URL = "http://127.0.0.1:7860"
DEFAULT_OUTPUT_DIR = "art/generated"
DEFAULT_RENPY_PATTERN = "game/images/nsfw/{character}/{slot}.png"

CONTROL_KEYS = {
    "api_url",
    "assets",
    "base_dir",
    "character",
    "copies",
    "copy_to",
    "defaults",
    "endpoint",
    "filename",
    "init_image",
    "init_images",
    "mask",
    "metadata",
    "name",
    "output_dir",
    "overwrite",
    "overwrite_renpy",
    "payload",
    "renpy_path",
    "renpy_pattern",
    "renpy_root",
    "save_metadata",
    "slot",
    "timestamp_output_dir",
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
    parser.add_argument("prompt_json", type=Path, help="JSON file containing one prompt or an assets list.")
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
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
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
            if key in {"api_url", "defaults", "output_dir", "renpy_pattern", "renpy_root"}
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


def build_payload(config: dict[str, Any], asset: dict[str, Any], base_dir: Path) -> tuple[str, dict[str, Any]]:
    if not isinstance(asset, dict):
        raise ConfigError("Each asset entry must be a JSON object.")

    defaults = config.get("defaults", {})
    if defaults is None:
        defaults = {}
    if not isinstance(defaults, dict):
        raise ConfigError("'defaults' must be an object when provided.")

    payload = dict(defaults)
    direct_payload = asset.get("payload", {})
    if direct_payload is None:
        direct_payload = {}
    if not isinstance(direct_payload, dict):
        raise ConfigError("'payload' must be an object when provided.")
    payload.update(direct_payload)

    for key, value in asset.items():
        if key not in CONTROL_KEYS:
            payload[key] = value

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


def output_filename(asset: dict[str, Any], image_index: int, total_images: int, run_stamp: str) -> str:
    name = slugify(asset.get("name", "asset"))
    template = str(asset.get("filename") or f"{name}_{run_stamp}.png")
    context = {
        "name": name,
        "raw_name": str(asset.get("name", name)),
        "character": slugify(asset.get("character", "")),
        "slot": slugify(asset.get("slot", "")),
        "index": image_index + 1,
        "index0": image_index,
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
    if total_images > 1 and "{index" not in template and "{index0" not in template:
        stem = f"{stem}_{image_index + 1:02d}"
    return f"{stem}{suffix}"


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
) -> dict[str, Any]:
    endpoint, payload = build_payload(config, asset, base_dir)
    name = str(asset.get("name") or payload.get("prompt", "asset")[:40])
    out_dir = output_directory(args, config, asset, base_dir)
    dest_templates = destination_templates(args, config, asset, base_dir)

    if args.dry_run:
        preview = str(payload["prompt"]).replace("\n", " ")[:140]
        filename = output_filename(asset, 0, 1, run_stamp)
        context = {
            "name": slugify(asset.get("name", "asset")),
            "raw_name": str(asset.get("name", "asset")),
            "character": slugify(asset.get("character", "")),
            "slot": slugify(asset.get("slot", "")),
            "index": 1,
            "index0": 0,
            "stamp": run_stamp,
        }
        print(f"[dry-run] {name}: {endpoint} -> {out_dir}")
        print(f"          file: {filename}")
        print(f"          prompt: {preview}")
        for template in dest_templates:
            destination = resolve_path(render_template(template, context), base_dir)
            print(f"          renpy copy: {destination}")
        return {
            "name": name,
            "endpoint": endpoint,
            "dry_run": True,
            "output_dir": str(out_dir),
            "renpy_templates": dest_templates,
        }

    response = post_a1111(api_url, endpoint, payload, args.timeout)
    images = response.get("images")
    if not isinstance(images, list) or not images:
        raise RuntimeError(f"A1111 did not return any images for asset {name!r}.")

    out_dir.mkdir(parents=True, exist_ok=True)
    info = parse_info(response.get("info"))
    outputs: list[str] = []
    renpy_outputs: list[str] = []

    for image_index, image_base64 in enumerate(images):
        image_bytes = decode_image(str(image_base64))
        filename = output_filename(asset, image_index, len(images), run_stamp)
        output_path = ensure_output_path(out_dir / filename, args.overwrite)
        output_path.write_bytes(image_bytes)
        outputs.append(str(output_path))

        context = {
            "name": slugify(asset.get("name", "asset")),
            "raw_name": str(asset.get("name", "asset")),
            "character": slugify(asset.get("character", "")),
            "slot": slugify(asset.get("slot", "")),
            "index": image_index + 1,
            "index0": image_index,
            "stamp": run_stamp,
        }
        for template in dest_templates:
            if image_index > 0 and "{index" not in template and "{index0" not in template:
                continue
            destination = resolve_path(render_template(template, context), base_dir)
            written = write_exact_bytes(destination, image_bytes, args.overwrite_renpy)
            renpy_outputs.append(str(written))

        if not args.no_metadata:
            save_metadata(
                output_path,
                {
                    "asset": name,
                    "endpoint": endpoint,
                    "api_url": api_url,
                    "request": redacted_payload(payload),
                    "a1111_info": info,
                    "renpy_outputs": renpy_outputs,
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
        "a1111_info": info,
    }


def main() -> int:
    args = parse_args()
    base_dir = args.base_dir.resolve()

    try:
        config = load_json(args.prompt_json)
        api_url = str(args.api_url or config.get("api_url") or DEFAULT_API_URL)
        run_stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        results = [
            process_asset(args, config, asset, base_dir, api_url, run_stamp)
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
