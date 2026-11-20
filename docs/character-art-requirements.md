# Character Art Requirements

This file is the canonical checklist for character art. Every character must
meet it before that character is considered art-complete.

## Required Fully Nude Reference

Every character needs one clean, canonical, **fully nude** reference artwork.
It is required reference art, not an optional pin-up and not a stand-in for
lingerie, a towel, a robe, a bedsheet, or implied nudity.

The reference must:

- Be a full-body pose from the top of the head to the soles of the feet.
- Show the character completely nude with no clothing or opaque covering.
- Keep the breasts, hips, buttocks, and genitals readable and unobstructed.
- Have hands, hair, props, and framing clear of the body so proportions and
  skin details can be checked.
- Match the character's canonical face, hair, body type, skin tone, tattoos,
  scars, and other identity marks.
- Be clearly an adult character aged 18 or older.
- Use a neutral stance and readable silhouette; sensuality is allowed but
  clarity comes first.

Partial nudity, "implied" nudity, a towel held in front, or a crop that hides
the hips or legs does not satisfy this requirement.

## Required Locations

Every character needs the same fully nude reference in all three art lanes:

| Lane | Required path | Target size |
| --- | --- | --- |
| Character image | `Sam And Em/game/images/nsfw/<character>/nude_front.png` | `768x1024` |
| CG | `Sam And Em/game/images/nsfw/cg/cg_<character>_nude_reference.png` | `1024x768` |
| Source asset | `art/generated/nsfw/<character>_nude_reference_01.png` plus `.json` metadata | Highest generated or authored resolution |

`nude_alt.png` is an optional second character pose/angle. It may also be fully
nude, but it does not replace the required `nude_front.png` reference.

The three artwork files must depict the same character, body proportions, skin
details, and age. The source asset is the working file; the character image
and CG are the approved in-project reference copies.

## Current Cast Checklist

The requirement applies to every character in the current cast and to any
character added later:

- Alex
- Maxine
- Clara
- Morrigan
- Brielle
- Mina
- Kira
- Sienna
- Nadia
- Helena
- Rhea

For each name, use the lowercase character id already used by the art
pipeline (`alex`, `maxine`, `clara`, `morrigan`, `brielle`, `mina`, `kira`,
`sienna`, `nadia`, `helena`, `rhea`).

## Completion Gate

A character is not art-complete until the reference exists in all three art
lanes and every item below has been visually checked:

- [ ] Character image: `game/images/nsfw/<character>/nude_front.png`
- [ ] CG reference: `game/images/nsfw/cg/cg_<character>_nude_reference.png`
- [ ] Source asset: `art/generated/nsfw/<character>_nude_reference_01.png`
- [ ] Metadata: `art/generated/nsfw/<character>_nude_reference_01.json`
- [ ] Character identity and body details match across all files
- [ ] The character reads as a fictional adult aged 18 or older
