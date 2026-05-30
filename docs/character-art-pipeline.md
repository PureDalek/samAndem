# Character Art Pipeline

This project uses the main sprites as the character identity source of truth.

## Source Sprites

- Alex: `Sam And Em/game/images/characters/protagonist.png`
- Maxine: `Sam And Em/game/images/characters/maxine.png`
- Clara: `Sam And Em/game/images/characters/dorm_leader.png`

## Identity Anchors

Alex:
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

- Import locally-created images into `base`, `underwear`, `nude_front`, and `nude_alt` slots.
- Back up replaced files under `asset_backups`.
- Build character-consistent safe prompts from `art/character_identity_prompts.json`.
- Send safe img2img requests to Automatic1111 when the webui is running with `--api`.

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

Dry-run a payload:

```powershell
python scripts\generate_renpy_asset.py maxine --prompt "covered locker-room spa CG, opaque navy towel, strong rim light, steam, all private anatomy covered" --gallery private_03 --dry-run
```

Generate and patch the gallery:

```powershell
python scripts\generate_renpy_asset.py maxine --prompt "covered locker-room spa CG, opaque navy towel, strong rim light, steam, all private anatomy covered" --gallery private_03
```

Generate directly into a character-set slot:

```powershell
python scripts\generate_renpy_asset.py clara --prompt "covered cream towel wrap, warm light, soft steam, elegant pose, all private anatomy covered" --slot nude_alt
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

Covered variants available in the prompt tools:

- `underwear`: covered dorm loungewear.
- `covered_spa`: opaque towel/robe art with light mist.
- `backlit_robe`: opaque robe/loungewear art with dramatic light.
- `implied_steam`: opaque towel art with steam coverage.

## Base Model Plan

For reliable consistency, train one LoRA per character after collecting 15-30 approved images per character:

- `samandem_alex_v1`
- `samandem_maxine_v1`
- `samandem_clara_v1`

Recommended workflow:

1. Start from the existing sprite as the canonical face, hair, palette, and silhouette.
2. Generate safe outfit variants with img2img at low denoise strength.
3. Keep only images that match the character closely.
4. Caption each image with the identity anchors above.
5. Train a LoRA per character.
6. Use the LoRA trigger plus the identity anchors for future CGs and sprites.

## Content Boundary

The game can load private adult assets from the optional asset slots, but generated project assets created here should stay non-explicit. User-provided adult assets can be placed in:

```text
Sam And Em/game/images/nsfw/<character>/nude_front.png
Sam And Em/game/images/nsfw/<character>/nude_alt.png
```
