# Sam And Em v0.4.0 — Maxine Unbound

An explicit-content expansion focused entirely on Maxine Hart's route. The rest of the game is unchanged from v0.3.0.

## New scenes

Five scenes are now woven into the existing Maxine / Clara storyline, in the order a player actually reaches them.

1. **The shower she traded for** — after Clara's shower-schedule scene. Maxine swapped her slot for Sam's and is waiting in the second stall. Nude reveal, wall sex under the water, and a finish the player chooses (chest or face). If the face is chosen she gets a stripe across one closed eye and laughs until she has to lean on him.
2. **Room 214, the fan is broken** — that night. She strips, sits back on her heels and talks him through it. Tit-fuck on the bed; at the end her hands slip and he comes across her chin, cheek and the bridge of her nose. The "oops" is played for laughter, not embarrassment, and she stays naked afterward.
3. **The library after closing** — reached only if `maxine_trust >= 2` after the almost-date. Standing sex between the stacks, her skirt somewhere else, a librarian's cart two aisles away. He pulls out a moment too late and marks her thigh and skirt hem; she presses a due-date slip to it and pockets the slip.
4. **The last lie** — inserted into `route_c2m_last_lie` before the ending branch. The robe is open, the rain is loud, the sex starts slow and stops being slow. She asks him to finish on her; the following CG is her marked and unbothered, robe open, making him promise to remember it.
5. **The wedding night** — after the Wedding Garden vows. The dress is unbuttoned to her waist in the corridor, then a tit-fuck with the veil still on, then the bed, then a facial she asks for by name, then the morning after: his shirt, her ring, dried streaks, and half a wedding on the floor.

## Art

- **15 new CGs** at 1536×1152: `cg_mx_shower_nude`, `shower_wall`, `shower_facial`, `night_top`, `titfuck`, `oops`, `library`, `library_after`, `last_lie_nude`, `last_lie_sex`, `cum_covered`, `wedding_night`, `wedding_titfuck`, `wedding_facial`, `wedding_morning`.
- Composition QA: the solo shower frame was re-rendered until the person detector counted exactly one figure; the remaining frames were checked for blank output and stray people.
- Contact sheet: `art/generated/maxine_expansion/contact_maxine_expansion.jpg`.

## Writing

- ~2,600 new words of prose across the five scenes.
- Maxine's voice is kept consistent: blunt, competitive, funny under pressure, allergic to being treated as delicate.
- The explicit beats are consent-forward; she asks, she directs, and she gets the last line.
- The protagonist is renamed **Sam** across all scripts, menus, documentation and prompt text. "Alex" was a legacy default that disagreed with the title; the room-assignment joke now reads "short for Samantha."

## Technical

- New `default mx_shower_done` / `mx_library_done` flags.
- Calls wired at the correct points in `script.rpy`, `route_maxine_almost_date`, `route_c2m_last_lie` and `ending_maxine_wedding`.
- Lint clean at 1,421 dialogue blocks, 16,629 words, 162 menus, 150 images, 29 screens.
- Android `versionName` 0.4.0, `numeric_version` 23.

## Known scope

This expands Maxine's existing route; it does not add a new branch structure. Clara / Lady and the eight expanded-cast routes are unchanged from v0.3.0.
