# Character Asset Pipeline

The game supports optional adult character set images through `game/character_sets.rpy`.

## Slots

Each initial character has these slots:

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

The files are not required. If a file is missing, the Character Sets screen shows a missing placeholder.

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
