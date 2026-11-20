# Ren'Py Assets From JSON Prompt

Generate local Ren'Py image assets with Automatic1111:

```powershell
python scripts/renpy_assets_from_json_prompt.py scripts/prompts/renpy_assets.example.json
```

Automatic1111 must be running with `--api`, usually at:

```text
http://127.0.0.1:7860
```

## Scene GUI Settings

JSON batches read the scene-maker GUI profile by default:

```text
art/generated/local_scene_pipeline/scene_image_gui_profile.locked.json
```

That makes JSON assets inherit the same GUI style prefix/suffix, guidelines,
negative prompt, always-on negative prompt, A1111 URL, checkpoint, sampler,
size, steps, CFG, seed, and denoise unless the JSON or command line overrides
them.

Dry-run a JSON batch with the GUI profile:

```powershell
$py = "C:\Users\pured\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $py scripts\renpy_assets_from_json_prompt.py scripts\prompts\renpy_assets.example.json --dry-run
```

Run without the GUI profile for one command:

```powershell
& $py scripts\renpy_assets_from_json_prompt.py scripts\prompts\renpy_assets.example.json --no-settings-profile --dry-run
```

For stronger character consistency, JSON assets can set `character` or
`characters`:

```json
{
  "name": "balcony_confession",
  "characters": ["maxine", "alex"],
  "prompt": "private balcony confession under warm city lights"
}
```

## 18+ Asset Batch

The current 18+ game assets are generated from the same high-quality SDXL
preset family used by the online-style quality test:

- Character sprites use `samandem_sdxl_sprite`.
- Story CGs use `samandem_sdxl_cg`.
- Both presets use the Hassaku XL Illustrious checkpoint, hires fix, ADetailer,
  and stronger quality prompts. The hard bans stay in every preset negative:
  minors, non-consent, coercion, assault, bestiality. The presets no longer
  pretend that explicit nudity is impossible; they only ban minors and
  non-consent framing.

Validate the batch before spending time on generation:

```powershell
python scripts/renpy_assets_from_json_prompt.py scripts/prompts/explicit_assets.json --preflight --dry-run
```

For the shipping-quality baseline, import the known-good Sam And Em references:

```powershell
Copy-Item -Recurse -Force "C:\Repos\AI\samandem\Sam And Em\game\images\nsfw\*" "game\images\nsfw"
```

The prompt batch is now reference-driven for controlled variations. Each asset
uses `img2img`, an `init_image` from the Sam And Em reference set, and low
denoise values so composition and identity do not drift.

For R-rated 18+ variants, drop the `fully clothed` / `fully covered`
disclaimer habit. Use concrete wardrobe and pose wording: `open hoodie`,
`shirtless`, `low-slung lounge pants`, `sports bra`, `high-cut shorts`,
`open robe`, `low towel wrap`, `bare shoulders`, `bare midriff`, `bare
thighs`, `skin highlights`. Keep minors, non-consent, coercion, assault, and
bestiality bans in the negative prompt instead of as positive-prompt
disclaimers.

Do not use this generator wrapper, local A1111, or online generation prompts to
create explicit nude or sexual images. If the user provides finished private
adult artwork, this repo can import it into game slots after resizing and
backup, but the tooling should not generate, edit, upscale, or describe explicit
sexual content.

When preflight passes and you intentionally want to regenerate reference-based
variations:

```powershell
python scripts/renpy_assets_from_json_prompt.py scripts/prompts/nsfw_assets.json --preflight --overwrite-renpy
```

## Story CG Concept Batch

Use this batch for non-overwriting, story-specific 18+ review candidates:

```powershell
python scripts/renpy_assets_from_json_prompt.py scripts/prompts/story_nsfw_concept_assets.json --dry-run
python scripts/renpy_assets_from_json_prompt.py scripts/prompts/story_nsfw_concept_assets.json --preflight --overwrite
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

The `nude_front` slot is the canonical **fully nude** reference for that
character; `nude_alt` is an optional alternate pose. Covered towel, robe,
lingerie, and implied-nude variants can live in other slots or CGs, but they
do not replace the required fully nude reference.

The reference must also exist as a CG and as a source asset:

```text
Sam And Em/game/images/nsfw/<character>/nude_front.png
Sam And Em/game/images/nsfw/cg/cg_<character>_nude_reference.png
art/generated/nsfw/<character>_nude_reference_01.png
art/generated/nsfw/<character>_nude_reference_01.json
```

Prompts in `scripts/prompts/explicit_assets.json` may reach R-rated 18+
nudity framing; the maturity preset controls how explicit. The hard bans stay
in every negative (`minor`, `child`, `teen`, `non-consent`, `assault`,
`bestiality`). See `docs/character-art-requirements.md` for the canonical
checklist.

Validate the JSON without calling A1111:

```powershell
python scripts/renpy_assets_from_json_prompt.py scripts/prompts/renpy_assets.example.json --dry-run
```

Validate the local model/sampler/ADetailer resources before generation:

```powershell
python scripts/renpy_assets_from_json_prompt.py scripts/prompts/blonde_quality_test.json --preflight --dry-run
```

Generate the high-quality blonde sprite test:

```powershell
python scripts/renpy_assets_from_json_prompt.py scripts/prompts/blonde_quality_test.json --preflight
```

List the local A1111 resources available to JSON prompts:

```powershell
python scripts/renpy_assets_from_json_prompt.py --list-resources
```

For a scene-to-image workflow that uses a local Ollama LLM to polish a scene
prompt before sending it to A1111, see `docs/local_scene_image_pipeline.md`.

Overwrite existing Ren'Py destination files when copying generated assets:

```powershell
python scripts/renpy_assets_from_json_prompt.py scripts/prompts/renpy_assets.example.json --overwrite-renpy
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
- `characters`: optional string/list such as `["maxine", "alex"]` for direct identity anchoring.
- `seed_count`, `base_seed`, and `seed_step`: deterministic seed ladder for consistent variant batches.
- `adetailer`: object/list/boolean shortcut for ADetailer always-on script arguments.
- `endpoint`: `txt2img` or `img2img`; omitted means `txt2img` unless `init_image` is present.
- `filename`: output filename template. Supports `{name}`, `{raw_name}`, `{character}`, `{slot}`, `{index}`, `{index0}`, `{variant}`, `{variant0}`, `{seed}`, and `{stamp}`.
- `character` and `slot`: used with `renpy_root` and `renpy_pattern`.
- `renpy_path`, `copy_to`, or `copies`: explicit destination path templates.
- `init_image`, `init_images`, and `mask`: local files loaded as base64 for img2img.
- `payload`: object merged into the A1111 request for advanced fields.

Relative paths are resolved from the directory where you run the script, unless you pass `--base-dir`.
