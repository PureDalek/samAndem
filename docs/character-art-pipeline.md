# Character Art Pipeline

This project uses the main sprites as the character identity source of truth.

## Source Sprites

- Sam: `Sam And Em/game/images/characters/protagonist.png`
- Maxine: `Sam And Em/game/images/characters/maxine.png`
- Clara: `Sam And Em/game/images/characters/dorm_leader.png`

## Identity Anchors

Sam:
- Young adult male, 18+.
- Short messy black hair, soft brown eyes, slim average build.
- Gentle anxious expression.
- Black hoodie and white shirt palette.

Maxine:
- Young adult woman, 18+.
- Short spiky black hair with vivid blue streaks, blue eyes.
- Athletic tomboy build, confident grin.
- Navy sporty palette, sleeveless hoodie, hand wraps.

Clara:
- Young adult woman, 18+.
- Long auburn/red-brown hair swept to one side, warm brown eyes.
- Composed dorm-leader poise.
- Beige cardigan, white blouse, elegant cream/brown palette.

## Required Fully Nude Reference

Every character needs one canonical fully nude reference before their art is
considered complete. This is a required identity reference, not an optional
pin-up, and it must exist in all three art lanes:

```text
Sam And Em/game/images/nsfw/<character>/nude_front.png
Sam And Em/game/images/nsfw/cg/cg_<character>_nude_reference.png
art/generated/nsfw/<character>_nude_reference_01.png
art/generated/nsfw/<character>_nude_reference_01.json
```

The character image is `768x1024`, the CG is `1024x768`, and the source asset
keeps the highest generated or authored resolution. The same face, hair, body
proportions, skin tone, markings, and adult age must read across all three.

The reference must be fully nude and full body from head to feet. Clothing,
lingerie, towels, robes, sheets, props, hands, or crops must not conceal the
breasts, hips, buttocks, genitals, or defining body details. Lingerie-only,
towel-only, implied-nude, and partial-crop variants do not satisfy the
requirement.

This applies to Sam, Maxine, Clara, Morrigan, Brielle, Mina, Kira, Sienna,
Nadia, Helena, Rhea, and every character added later. See
`docs/character-art-requirements.md` for paths, sizes, and the completion
checklist.

## Automatic1111 Setup

Local webui path:

```text
C:\Repos\Ai-Tools\stable-diffusion-webui
```

The venv currently has CUDA Torch installed, but Windows is not exposing the NVIDIA GPU:

```text
torch: 2.9.1+cu128
cuda: 12.8
torch.cuda.is_available(): False
torch.cuda.device_count(): 0
NVIDIA status: Error, ConfigManagerErrorCode 21
```

Fix the GPU state first, then use Automatic1111 img2img with the matching source sprite as the reference for each character.

## Asset Manager

Open the local asset manager with:

```powershell
cd C:\Repos\AI\samandem
python scripts\character_asset_manager.py
```

The manager can:

- Import locally-created 18+ images into `base`, `underwear` (renamed to `lingerie` in
  the game UI), `nude_front`, and `nude_alt` slots.
- Back up replaced files under `asset_backups`.
- Build character-consistent 18+ prompts from `art/character_identity_prompts.json`.
- Send image-to-image requests to Automatic1111 when the webui is running with `--api`.

## Prompt-To-Ren'Py Generator

Run prompt-generation commands from the repository root:

```powershell
cd C:\Repos\AI\samandem
```

JSON prompt files should target the real Ren'Py project folder:

```json
{
  "renpy_root": "Sam And Em",
  "renpy_pattern": "game/images/nsfw/{character}/{slot}.png"
}
```

Do not use a root-level `game/` folder for Sam And Em assets; that path is ignored as an accidental wrong-workspace output.

Use `scripts/generate_renpy_asset.py` when you want to write a custom prompt and have local Automatic1111 generate a Ren'Py-ready file from the character base sprite.
The generator reads the scene GUI profile at
`art/generated/local_scene_pipeline/scene_image_gui_profile.locked.json` by
default, so quality/style prompt text, negative prompt text, A1111 URL, size,
steps, sampler, and denoise stay aligned with the scene creator. Use
`--no-settings-profile` for a one-off run that ignores the GUI profile.

Dry-run a payload:

```powershell
python scripts\generate_renpy_asset.py maxine --prompt "low navy towel wrap, strong rim light, steam, bare shoulders, mature sensual mood" --gallery gallery_03 --dry-run
```

Generate and patch the gallery:

```powershell
python scripts\generate_renpy_asset.py maxine --prompt "low navy towel wrap, strong rim light, steam, bare shoulders, mature sensual mood" --gallery gallery_03
```

Generate directly into a character-set slot:

```powershell
python scripts\generate_renpy_asset.py clara --prompt "open cream robe, warm light, soft steam, bare skin, elegant pose, mature sensual mood" --slot nude_alt
```

Destination options:

- `--slot base|underwear|nude_front|nude_alt`: save into `images/nsfw/<character>/`.
- `--gallery <id>`: save into `images/gallery/` and patch `game/gallery.rpy`.
- `--cg <id>`: save into `images/cgs/`.
- `--out <path>`: save to any file path.

Use lower denoise (`--denoise 0.30`) when the original sprite must stay very close. Use higher denoise (`--denoise 0.55` to `0.70`) when the prompt should change the outfit or scene more strongly.

Batch-generate from a JSON recipe:

```powershell
python scripts\generate_renpy_asset.py --recipe art\asset_recipe.example.json --dry-run
python scripts\generate_renpy_asset.py --recipe art\asset_recipe.example.json
```

Create a starter recipe:

```powershell
python scripts\generate_renpy_asset.py --write-recipe-example art\my_asset_recipe.json
```

Edit recipes in a GUI:

```powershell
python scripts\asset_recipe_editor.py
```

The GUI edits `defaults`, adds/removes jobs, saves recipe JSON, and can run a dry-run through `scripts/generate_renpy_asset.py`.

Recipe shape:

```json
{
  "defaults": {
    "api": "http://127.0.0.1:7860",
    "width": 1024,
    "height": 1536,
    "denoise": 0.55
  },
  "jobs": [
    {
      "character": "maxine",
      "prompt": "covered sporty dorm sprite variant, navy hoodie, confident pose",
      "destination": { "type": "sprite", "id": "maxine_hoodie" }
    }
  ]
}
```

Recipe destination types: `sprite`, `slot`, `gallery`, `cg`, `out`, or `generated`.

18+ variants available in the prompt tools:

- `lingerie`: 18+ dorm lingerie / loungewear art.
- `explicit_nude_spa`: adult towel/robe art with light mist.
- `explicit_open_robe`: adult open robe / loungewear art with dramatic light.
- `explicit_shower`: adult private shower art with steam coverage.

## Base Model Plan

For reliable consistency, train one LoRA per character after collecting 15-30 approved images per character:

- `samandem_alex_v1`
- `samandem_maxine_v1`
- `samandem_clara_v1`

Recommended workflow:

1. Start from the existing sprite as the canonical face, hair, palette, and silhouette.
2. Generate 18+ outfit variants with image-to-image at low denoise strength.
3. Keep only images that match the character closely.
4. Caption each image with the identity anchors above.
5. Train a LoRA per character.
6. Use the LoRA trigger plus the identity anchors for future CGs and sprites.

## Content Boundary

The game is built to ship R-rated 18+ content. Generated prompts in this
project are allowed to reach partial and full nudity, sensual framing, and
intimate consent-based interaction as long as every character stays fictional
and 18+.

User-supplied 18+ assets can be placed in:

```text
Sam And Em/game/images/nsfw/<character>/nude_front.png
Sam And Em/game/images/nsfw/<character>/nude_alt.png
```
