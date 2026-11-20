# Local Scene Image Pipeline

Use `scripts/local_scene_image_pipeline.py` when you want a single scene
description turned into a repeatable local image-generation job.

For the GUI:

```powershell
$py = "C:\Users\pured\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $py scripts\local_scene_image_gui.py
```

The GUI exposes scene text, art-direction guidelines, quality/style prompt,
base negative prompt, always-on negative prompt, extra positive/negative
prompt text, Ollama model, A1111 checkpoint, sampler, scheduler, seed,
variants, img2img source image, denoise, and dry-run/generate buttons.

The Prompt tab also has a tag editor. Pick a prompt field, type one or more
comma-separated tags, then use Add, Remove, or Sort Unique.

GUI prompt/settings text is saved to a local user-owned profile:

```text
art/generated/local_scene_pipeline/scene_image_gui_profile.locked.json
```

That file is ignored by Git and marked read-only after saving. Treat it as
GUI-owned: generation scripts read it by default, and the GUI save path is the
normal way to change it.

The flow is:

1. Send the scene to a local Ollama model for prompt polish.
2. Cache the polished prompt under `art/generated/local_scene_pipeline`.
3. Send the cached prompt to local Automatic1111 with fixed seeds/settings.

The generator path is for fictional 18+ adult VN art. Adult themes, partial
and full nudity, sensual framing, and intimate consent-based interaction are in
scope. The hard bans stay in the always-on negative prompt: minors, loli,
shota, non-consent, coercion, blackmail, mind-control consent, assault,
bestiality.

## Requirements

Start Ollama and pull a model:

```powershell
ollama serve
ollama pull llama3.1:8b
```

Or list the models already installed locally:

```powershell
$py = "C:\Users\pured\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $py scripts\local_scene_image_pipeline.py --list-llm-models
```

Start Automatic1111 with its API enabled:

```powershell
webui-user.bat --api
```

List the A1111 checkpoints/samplers available on this machine:

```powershell
& $py scripts\renpy_assets_from_json_prompt.py --list-resources
```

## Dry Run

Use `--dry-run` first. It writes or reuses the prompt cache and prints the
payload that would be sent to A1111.

The script reads the GUI profile by default. Disable that for one run with:

```powershell
& $py scripts\local_scene_image_pipeline.py "Scene text" --no-settings-profile --no-llm --dry-run
```

Template-only dry run, useful even when Ollama is not running:

```powershell
$py = "C:\Users\pured\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $py scripts\local_scene_image_pipeline.py "Maxine and Alex in a rainlit dorm room, emotional honesty, warm lamp, blue rain window" --slug maxine_rain_dorm --no-llm --dry-run
```

Ollama-polished dry run:

```powershell
& $py scripts\local_scene_image_pipeline.py "Maxine and Alex in a rainlit dorm room, emotional honesty, warm lamp, blue rain window" --slug maxine_rain_dorm --refresh-prompt --dry-run
```

If you want to use a different installed Ollama model, add `--llm-model`:

```powershell
& $py scripts\local_scene_image_pipeline.py "Maxine and Alex in a rainlit dorm room, emotional honesty, warm lamp, blue rain window" --slug maxine_rain_dorm --llm-model "<installed model name>" --refresh-prompt --dry-run
```

Tune always-on negative tags from the CLI with `--always-negative`:

```powershell
& $py scripts\local_scene_image_pipeline.py "Maxine and Alex in a rainlit dorm room, emotional honesty, warm lamp, blue rain window" --slug maxine_rain_dorm --no-llm --dry-run --always-negative "flat lighting, plastic skin, text, watermark"
```

Force specific character anchors when the scene text is ambiguous:

```powershell
& $py scripts\local_scene_image_pipeline.py "A private balcony confession under warm city lights" --characters maxine,alex --no-llm --dry-run
```

Character identity is loaded from:

```text
art/character_identity_prompts.json
```

After the first good prompt, omit `--refresh-prompt` so future runs reuse the
same cached wording.

## Generate

Replace the checkpoint with one from `--list-resources`:

```powershell
& $py scripts\local_scene_image_pipeline.py "Maxine and Alex in a rainlit dorm room, emotional honesty, warm lamp, blue rain window" --slug maxine_rain_dorm --seed 56530358 --checkpoint "<your checkpoint name>" --variants 2
```

Outputs are saved as PNG files with sidecar JSON metadata:

```text
art/generated/local_scene_pipeline/<slug>_seed_<seed>_v00_00.png
art/generated/local_scene_pipeline/<slug>_seed_<seed>_v00_00.json
```

## Similar Results

For images that stay close across runs, keep these the same:

- `--slug`
- `--seed`
- cached prompt file, meaning do not use `--refresh-prompt`
- checkpoint
- sampler, scheduler, steps, CFG scale, width, and height
- Automatic1111 extensions and backend settings

Use `--variants` for controlled alternates. The script adds `--seed-step` to
the base seed for each variant.

For the closest repeated composition, feed a selected image back through
img2img:

```powershell
& $py scripts\local_scene_image_pipeline.py "Maxine and Alex in a rainlit dorm room, emotional honesty, warm lamp, blue rain window" --slug maxine_rain_dorm_refine --seed 56530358 --checkpoint "<your checkpoint name>" --init-image art\generated\local_scene_pipeline\maxine_rain_dorm_seed_56530358_v00_00.png --denoise 0.35
```

Lower `--denoise` values keep the image closer to the input. Higher values
change pose, lighting, and composition more aggressively.

Exact pixels can still change if the checkpoint, VAE, CUDA settings, extensions,
or A1111 version change. Same settings on the same backend should produce very
similar images, and often identical images.
