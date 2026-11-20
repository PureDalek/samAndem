# 18+ Character Asset Pipeline

The game ships with an in-game 18+ character set screen at `game/character_sets.rpy`.

## Slots

Each main character ships four 18+ asset slots:

```text
base.png
underwear.png
nude_front.png
nude_alt.png
```

Folders:

```text
Sam And Em/game/images/nsfw/alex/
Sam And Em/game/images/nsfw/clara/
Sam And Em/game/images/nsfw/maxine/
```

The filenames stay stable so previously imported art still loads. The UI
displays them as `Base`, `Lingerie`, `Nude - Front`, and `Nude - Alt`. Files
may be omitted at runtime: a missing file shows a `Missing` placeholder, never
a build break.

## Required Fully Nude Reference

Content is not art-complete without a canonical fully nude reference for every
character. The reference must be stored in all three art lanes:

```text
Sam And Em/game/images/nsfw/<character>/nude_front.png
Sam And Em/game/images/nsfw/cg/cg_<character>_nude_reference.png
art/generated/nsfw/<character>_nude_reference_01.png
art/generated/nsfw/<character>_nude_reference_01.json
```

`nude_front.png` is the mandatory in-game character image. `nude_alt.png` is
an optional alternate pose, not a replacement. The CG is `1024x768`, the
character image is `768x1024`, and the source asset keeps the highest generated
or authored resolution.

The reference must be fully nude, full body from head to feet, and clear of
clothing, towels, robes, sheets, props, hands, or crops that hide the breasts,
hips, buttocks, genitals, or defining body details. Lingerie, underwear,
implied nudity, and partial crops do not count.

This applies to Alex, Maxine, Clara, Morrigan, Brielle, Mina, Kira, Sienna,
Nadia, Helena, Rhea, and every character added later. See
`docs/character-art-requirements.md` for the canonical checklist.

## Rules

- All depicted characters must be fictional adults age 18 or older.
- Do not use assets involving coercion, assault, blackmail, or mind-control sexual consent.
- Keep release builds aligned with the age gate.

## Local Generation Notes

Automatic1111 is configured at:

```text
C:\Repos\Ai-Tools\stable-diffusion-webui
```

The local launch args were updated to:

```text
--api --skip-torch-cuda-test
```

If CUDA is unavailable, generation may fall back to CPU and be very slow. Fixing GPU acceleration requires a working CUDA-enabled Torch install matching the local NVIDIA driver.
