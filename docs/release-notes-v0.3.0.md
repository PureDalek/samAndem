# Sam And Em v0.3.0 — The Expanded Cast

First release where the eight expanded routes are both **reachable** and **fully written**, and where the whole shipped image set is rendered at release quality.

## Story

- Recovered `expanded_cast.rpy` and `expanded_routes.rpy` from compiled bytecode with `unrpyc`; the source files had been lost because `Sam And Em/.gitignore` excludes `game/**/*.rpyc` and the `.rpy` originals were gone. Both are now normal tracked sources.
- Rebuilt `expanded_routes.rpy` from scaffolding into real prose. The old file was eight copies of the same 1,579-word template with 2 repeated lines per choice; the new file is 7,805 words of route-specific writing.
- Eight routes, ten beats each, fifteen choices each, three endings each:
  - **Morrigan Vale** — occult tutor. Knowledge as leverage vs. knowledge as care. Endings: The Margin / Footnote / Errata.
  - **Brielle Ashford** — legacy-donor queen. Money, worth, and the receipt. Endings: Unsponsored / Heiress / Receipt.
  - **Mina Sato** — mural rebel. Being seen against being useful. Endings: Wet Paint / Second Coat / Whitewash.
  - **Kira Sol** — cosplayer and prop engineer. Performance as courage. Endings: Practical Effects / Limited Run / Recast.
  - **Sienna Cross** — scholarship swimmer. The body as proof. Endings: Taper / Touch / False Start.
  - **Nadia Quinn** — campus nurse. Care as self-erasure. Endings: On Call / Patient / Chart.
  - **Helena Voss** — headmaster. Power, age, and the ledger. Endings: Head of School / Term's End / The Ledger.
  - **Rhea Mallory** — campus reporter. Truth against damage. Endings: Byline / Source / Off Record.
- Ending selection is by route score (`good` vs `risky`, ±3), so choices matter and each route has a genuine good, neutral, and bad outcome.
- The route hub is now the destination of the intro; the original Maxine / Clara story is the "Continue the Maxine / Clara route" branch. The ten-situation gauntlet is preserved verbatim from v0.2.
- Cleared routes are marked in the hub via `persistent.seen_routes`.

## Art

- **32 new character sprites** — four per route (base, alternate, formal, intimate/role), 880×1840, on transparent alpha with matching chroma-key variants.
- **80 new route CGs** — ten per route, each illustrating its canonical beat: first contradiction, public scene, private help with a price, rival twist, real-world outfit, restricted room, evidence against the wrong person, the admission, the scholarship threat, the formal/role outfit. 1536×1152.
- **Rebuilt shipped art** (38 files): 1920×1080 backgrounds, 1920×1080 story CGs, 880×1840 character sprites with alpha, 1920×1080 and 880×1840 gallery pieces, 1152×1536 NSFW character slots, and 1536×1152 NSFW story CGs.
- Explicit level now follows the scene rather than the file convention: `shower_schedule` is fully nude (the character is mid-correction in a shower corridor), `c2m_last_lie` is nude (the confession happens after the robe comes open), and the gallery sets are full nude studies.
- `maxine/nude_alt` is validated as a single-figure composition; `alex/base` and the wedding CG were re-rendered to remove duplicate/background figures.

## Technical fixes

- Missing image sources: 112 declared images in `expanded_cast.rpy` now exist on disk.
- Forge hires-pass black frames: the literal token `16:9` in a prompt is parsed as a hires scale of 1.777 and returns a black image; ratio tokens were removed from every hires prompt and replaced by explicit `hr_scale`.
- Chroma-keying: sprites are keyed by corner-seeded connected components (OpenCV) with despill and feathered alpha instead of green-dominance thresholds, which failed on the muted studio green the model actually renders.
- Sprite/menu indent bug in the route emitter that collapsed menu choice blocks after the first dialogue line.
- `helena` speaker was undefined in `expanded_cast.rpy`; added.
- `quick_menu` / screens split verified; `screens.rpy` duplicate removal is unchanged and lint-clean.

## Verification

- Ren'Py 8.5.3 lint: clean, 0 errors.
- 1,255 dialogue blocks, 14,049 words, 161 menus, 135 images, 29 screens.
- Image QA: 0 blank frames, 0 missing declared files, sprite alpha present on all six character files.
- Android build: `com.puredalek.samandem-0.3.0` (`numeric_version` 22), `sensorLandscape`.

## Known scope

This is a content-complete preview build, not a 1.0. The eight new routes are 10-beat previews with a single ending branch each; there is no per-beat CG gallery entry yet, and voice/SFX are still stubs. The Maxine / Clara route remains the v0.2 slice.
