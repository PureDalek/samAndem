# Ren'Py Assets From JSON Prompt

Generate local Ren'Py image assets with Automatic1111:

```powershell
python scripts/renpy_assets_from_json_prompt.py prompts/renpy_assets.example.json
```

Automatic1111 must be running with `--api`, usually at:

```text
http://127.0.0.1:7860
```

## Adult Asset Batch

The current adult-themed game assets are generated from the same high-quality
SDXL preset family used by the online-style quality test:

- Character sprites use `samandem_sdxl_sprite`.
- Story CGs use `samandem_sdxl_cg`.
- Both presets use the Hassaku XL Illustrious checkpoint, hires fix, ADetailer,
  stronger quality prompts, and covered-content negative prompts.

Validate the batch before spending time on generation:

```powershell
python scripts/renpy_assets_from_json_prompt.py prompts/nsfw_assets.json --preflight --dry-run
```

For the shipping-quality baseline, import the known-good Sam And Em references:

```powershell
Copy-Item -Recurse -Force "C:\Repos\AI\samandem\Sam And Em\game\images\nsfw\*" "game\images\nsfw"
```

The prompt batch is now reference-driven for controlled variations. Each asset
uses `img2img`, an `init_image` from the Sam And Em reference set, and low
denoise values so composition and identity do not drift.

For skin-forward non-explicit variants, do not pad the positive prompt with
generic phrases like `fully clothed` or `fully covered`. Use concrete visual
coverage instead: `open hoodie`, `shirtless`, `low-slung lounge pants`,
`sports bra`, `high-cut shorts`, `open robe`, `small towel wrap`, `bare
shoulders`, `bare midriff`, `bare thighs`, `skin highlights`, and
`strategic towel placement`. Keep explicit anatomy and sexual acts in the
negative prompt, not as repetitive positive-prompt disclaimers.

Do not use this generator wrapper, local A1111, or online generation prompts to
create explicit nude or sexual images. If the user provides finished private
adult artwork, this repo can import it into game slots after resizing and
backup, but the tooling should not generate, edit, upscale, or describe explicit
sexual content.

When preflight passes and you intentionally want to regenerate reference-based
variations:

```powershell
python scripts/renpy_assets_from_json_prompt.py prompts/nsfw_assets.json --preflight --overwrite-renpy
```

## Story CG Concept Batch

Use this batch for non-overwriting, story-specific NSFW review candidates:

```powershell
python scripts/renpy_assets_from_json_prompt.py prompts/story_nsfw_concept_assets.json --dry-run
python scripts/renpy_assets_from_json_prompt.py prompts/story_nsfw_concept_assets.json --preflight --overwrite
```

It writes review images to `art/generated/story_nsfw_concepts` and does not
copy them into Ren'Py slots. See `docs/nsfw_story_asset_plan.md` for the target
story beats and quality gate.

Generated source files and metadata are saved under:

```text
art/generated/nsfw
```

Ren'Py-ready copies are written into:

```text
game/images/nsfw
```

The `nude_front` and `nude_alt` slot names are game-facing slot names only.
Prompts in `prompts/nsfw_assets.json` should remain covered: no visible genitals,
no exposed nipples, no sex acts, no see-through clothing, and no underage content.
Use opaque robes, towels, underwear, steam, backlight, and framing for the strongest
adult mood that still stays usable in this project.

Validate the JSON without calling A1111:

```powershell
python scripts/renpy_assets_from_json_prompt.py prompts/renpy_assets.example.json --dry-run
```

Validate the local model/sampler/ADetailer resources before generation:

```powershell
python scripts/renpy_assets_from_json_prompt.py prompts/blonde_quality_test.json --preflight --dry-run
```

Generate the high-quality blonde sprite test:

```powershell
python scripts/renpy_assets_from_json_prompt.py prompts/blonde_quality_test.json --preflight
```

List the local A1111 resources available to JSON prompts:

```powershell
python scripts/renpy_assets_from_json_prompt.py --list-resources
```

For a scene-to-image workflow that uses a local Ollama LLM to polish a scene
prompt before sending it to A1111, see `docs/local_scene_image_pipeline.md`.

Overwrite existing Ren'Py destination files when copying generated assets:

```powershell
python scripts/renpy_assets_from_json_prompt.py prompts/renpy_assets.example.json --overwrite-renpy
```

## JSON Shape

Use either a top-level `assets` list or a single object with `prompt`.

Top-level fields:

- `api_url`: A1111 API root.
- `output_dir`: where generated images and manifests are saved.
- `renpy_root`: optional Ren'Py project root.
- `renpy_pattern`: optional copy path template, defaulting to `game/images/characters/{character}/{slot}.png`.
- `quality_preset`: built-in or custom quality preset name. Built-ins: `samandem_sdxl_sprite`, `samandem_sdxl_cg`.
- `quality_presets`: optional map of custom preset definitions.
- `defaults`: request fields merged into every A1111 payload.
- `assets`: prompt entries.

Each asset can include any A1111 payload field directly, plus:

- `name`: asset identifier used for filenames.
- `quality_preset` or `preset`: override or add quality presets for one asset.
- `checkpoint` or `model`: request-local A1111 checkpoint override.
- `prompt_prefix`, `style_anchor`, `character_anchor`, `scene`, and `prompt_suffix`: reusable prompt pieces composed around `prompt`.
- `negative_prefix` and `negative_suffix`: reusable negative prompt pieces.
- `seed_count`, `base_seed`, and `seed_step`: deterministic seed ladder for consistent variant batches.
- `adetailer`: object/list/boolean shortcut for ADetailer always-on script arguments.
- `endpoint`: `txt2img` or `img2img`; omitted means `txt2img` unless `init_image` is present.
- `filename`: output filename template. Supports `{name}`, `{raw_name}`, `{character}`, `{slot}`, `{index}`, `{index0}`, `{variant}`, `{variant0}`, `{seed}`, and `{stamp}`.
- `character` and `slot`: used with `renpy_root` and `renpy_pattern`.
- `renpy_path`, `copy_to`, or `copies`: explicit destination path templates.
- `init_image`, `init_images`, and `mask`: local files loaded as base64 for img2img.
- `payload`: object merged into the A1111 request for advanced fields.

Relative paths are resolved from the directory where you run the script, unless you pass `--base-dir`.
