# 18+ Story Asset Plan

Goal: produce professional-grade R-rated 18+ visual novel assets for the
current story.

## Project Policy

All depicted characters are fictional adults aged 18 or older. The game is
explicit friendly by design: generated assets can include 18+ partial and
full nudity, sensual framing, intimate consent-based interaction, and mature
CGs.

Hard bans in every prompt, preset, and negative:

- Minors (`minor`, `child`, `teen`, `underage`, `loli`, `shota`,
  `schoolgirl`, `schoolboy`).
- Non-consent (`non-consent`, `coercion`, `blackmail`, `mind-control consent`,
  `assault`).
- Bestiality.

Describe each scene honestly. Wording should call out the actual apparel and
pose the prompt wants: open robe, low-slung lounge pants, low towel, sheer
lingerie, bare shoulders, bare midriff, bare thighs, intimate lighting,
emotional eye contact. Avoid "fully clothed" / "fully covered" disclaimers;
those only push the model toward fake-looking coverage.

The `import_explicit_adult_asset.py` script renames, resizes, backs up, and
wires user-supplied 18+ art into Ren'Py slots. The script does not generate,
upscale, rewrite, or describe sexual content. It is a file-handling lane
only.

## Required Character Nude Reference

Every character must have a canonical fully nude reference before their
story CGs are approved. The reference is mandatory in three places: the
character image slot, the CG folder, and the source asset folder.

```text
Sam And Em/game/images/nsfw/<character>/nude_front.png
Sam And Em/game/images/nsfw/cg/cg_<character>_nude_reference.png
art/generated/nsfw/<character>_nude_reference_01.png
art/generated/nsfw/<character>_nude_reference_01.json
```

The reference must be fully nude and full body from head to feet. Lingerie,
underwear, towels, robes, sheets, props, hands, and crops must not hide the
breasts, hips, buttocks, genitals, or defining body details. This is required
for Alex, Maxine, Clara, Morrigan, Brielle, Mina, Kira, Sienna, Nadia, Helena,
Rhea, and every character added later.

See `docs/character-art-requirements.md` for the canonical checklist.

## Story CG Targets

The review concept batch is:

```text
prompts/story_nsfw_concept_assets.json
```

It creates non-overwriting review candidates under:

```text
art/generated/story_nsfw_concepts
```

Current targets:

- `story_b2_maxine_almost_date_skin`: late library almost-date; temptation vs honesty.
- `story_c1_gala_balcony_skin`: gala route lock; Maxine, Alex, and Clara in romantic triangle tension.
- `story_c2m_maxine_last_lie_skin`: Maxine confession scene; intimacy plus hard truth.
- `story_c2l_lady_real_name_skin`: Clara/Lady hotel reveal; trust, passports, danger.
- `story_c2j_lady_no_questions_skin`: envelope scene; sensual suspense and legal danger.
- `story_e1_wedding_private_vow_skin`: Maxine happy ending; private vow after graduation.
- `story_e2_two_tickets_skin`: Lady happy ending; clean escape with two open-ended tickets.

## Generation Commands

Use the bundled Python in Codex desktop if `python` is not on PATH:

```powershell
$py = "C:\Users\pured\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
```

Validate JSON:

```powershell
& $py -m json.tool prompts\story_nsfw_concept_assets.json
```

Dry-run path resolution without calling A1111:

```powershell
& $py scripts\renpy_assets_from_json_prompt.py prompts\story_nsfw_concept_assets.json --dry-run
```

Preflight A1111 resources when the web UI is running with `--api`:

```powershell
& $py scripts\renpy_assets_from_json_prompt.py prompts\story_nsfw_concept_assets.json --preflight --dry-run
```

Generate review candidates:

```powershell
& $py scripts\renpy_assets_from_json_prompt.py prompts\story_nsfw_concept_assets.json --preflight --overwrite
```

Build a review report and contact sheet from generated candidates:

```powershell
& $py scripts\review_story_nsfw_concepts.py
```

This writes:

```text
art/diagnostics/story_nsfw_concept_review.md
art/diagnostics/story_nsfw_concept_review.jpg
```

After visual review, import an approved candidate into its Ren'Py slot:

```powershell
& $py scripts\review_story_nsfw_concepts.py --approve "story_c2m_maxine_last_lie_skin=art/generated/story_nsfw_concepts/<approved-file>.png"
```

Approved imports back up the previous game CG under:

```text
art/backups/story_nsfw_before_approval_<timestamp>
```

## Built-In ImageGen Fallback

When A1111 is down, the built-in image generator can still produce polished
story CG candidates. Keep the positive prompt concrete and skin-forward:
open robe, low-slung lounge pants, sheer lingerie, bare shoulders, bare
midriff, bare thighs, intimate lighting, emotional eye contact.

Avoid positive phrases like `fully clothed` or `fully covered`; put non-consent
and minor bans only in the negative prompt.

Use this fallback for one polished candidate at a time, then save the selected
result under `art/generated/story_nsfw_concepts` with a filename that starts
with the matching story asset key so the review helper can pick it up.

## User-Supplied 18+ Import Lane

If the project is reformatted around user-sourced 18+ art, keep that flow
separate from generation:

- Put incoming files in a temporary review folder outside `game/images`.
- Confirm only file suitability: dimensions, format, slot mapping, and whether
  the depicted characters are fictional 18+ adults.
- Do not create, edit, prompt, upscale, or describe sexual content.
- Import only approved files into the existing Ren'Py slots with backups.

List supported story CG slot aliases:

```powershell
& $py scripts\import_explicit_adult_asset.py --list-slots
```

Dry-run a user-supplied 18+ import:

```powershell
& $py scripts\import_explicit_adult_asset.py c2l C:\path\to\finished-image.png --dry-run
```

Import a finished user-supplied 18+ file into a story CG slot:

```powershell
& $py scripts\import_explicit_adult_asset.py c2l C:\path\to\finished-image.png --mode cover
```

The importer writes a `1024x768` PNG by default and backs up the previous slot
under `art/backups/explicit_adult_asset_import_<timestamp>`.

## Quality Gate

Do not copy generated candidates into `game/images/nsfw/cg` until they pass
visual review.

Acceptance checklist:

- Story beat is clear without reading the prompt.
- Character identity matches the current Maxine, Alex, and Clara references.
- Composition reads as a VN event CG at first glance.
- Skin-forward 18+ styling is present.
- No duplicate people, childlike faces, broken hands, text, panels, watermarks,
  random costume drift, or background incoherence.
- Image dimensions match the target slot: `1024x768` for CGs.

## Current Status

- JSON validation: passing.
- Dry-run path resolution: passing.
- Review/import helper: passing with 14 current built-in candidates.
- Imported story CGs:
  - `game/images/nsfw/cg/cg_b2_maxine_almost_date.png`
  - `game/images/nsfw/cg/cg_c1_gala_private_balcony.png`
  - `game/images/nsfw/cg/cg_c2m_maxine_last_lie.png`
  - `game/images/nsfw/cg/cg_c2l_lady_real_name.png`
  - `game/images/nsfw/cg/cg_c2j_lady_no_questions.png`
  - `game/images/nsfw/cg/cg_e1_wedding_garden_private_vow.png`
  - `game/images/nsfw/cg/cg_e2_two_tickets_private_compartment.png`
- Imported 1024x768 sources:
  - `art/generated/story_nsfw_concepts/story_b2_maxine_almost_date_skin_builtin_20260619-000747_1024x768.png`
  - `art/generated/story_nsfw_concepts/story_c1_gala_balcony_skin_builtin_20260619-000845_1024x768.png`
  - `art/generated/story_nsfw_concepts/story_c2m_maxine_last_lie_skin_builtin_20260618-233027_1024x768.png`
  - `art/generated/story_nsfw_concepts/story_c2l_lady_real_name_skin_builtin_20260619-000144_1024x768.png`
  - `art/generated/story_nsfw_concepts/story_c2j_lady_no_questions_skin_builtin_20260619-001102_1024x768.png`
  - `art/generated/story_nsfw_concepts/story_e1_wedding_private_vow_skin_builtin_20260619-002210_1024x768.png`
  - `art/generated/story_nsfw_concepts/story_e2_two_tickets_skin_builtin_20260619-002447_1024x768.png`
- Backups of previous game CGs: `art/backups/story_nsfw_before_approval_20260618-233549`, `art/backups/story_nsfw_before_approval_20260619-000320`, `art/backups/story_nsfw_before_approval_20260619-001238`, and `art/backups/story_nsfw_before_approval_20260619-002622`.
- A1111 preflight/generation: blocked until `http://127.0.0.1:7860` is running
  with `--api`.
