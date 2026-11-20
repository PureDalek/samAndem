# 18+ Character Asset Slots

Put user-supplied 18+ character set images here.

Every character depicted in these files must be a fictional adult aged 18 or
older. Hard ban on minors, non-consent, coercion, assault, and bestiality.

Expected structure:

```text
images/nsfw/alex/base.png
images/nsfw/alex/underwear.png
images/nsfw/alex/nude_front.png
images/nsfw/alex/nude_alt.png

images/nsfw/clara/base.png
images/nsfw/clara/underwear.png
images/nsfw/clara/nude_front.png
images/nsfw/clara/nude_alt.png

images/nsfw/maxine/base.png
images/nsfw/maxine/underwear.png
images/nsfw/maxine/nude_front.png
images/nsfw/maxine/nude_alt.png
```

The game UI labels these as `Base`, `Lingerie`, `Nude - Front`, and
`Nude - Alt` so the slot purpose is honest.

## Required Fully Nude Reference

Every character must have one canonical fully nude reference in each art
lane, not just the optional character-set slots:

```text
images/nsfw/<character>/nude_front.png
images/nsfw/cg/cg_<character>_nude_reference.png
art/generated/nsfw/<character>_nude_reference_01.png
art/generated/nsfw/<character>_nude_reference_01.json
```

`nude_front.png` is mandatory for every character and is the in-game
reference. `nude_alt.png` is an optional alternate pose. The CG is `1024x768`;
the character image is `768x1024`; the source asset keeps the highest
generated or authored resolution.

The reference must be fully nude and full body from the top of the head to the
soles of the feet. Clothing, lingerie, towels, robes, sheets, props, hands, or
crops must not conceal the breasts, hips, buttocks, genitals, or defining body
details. Lingerie-only, towel-only, implied-nude, and partial-crop art do not
satisfy the requirement.

This covers Alex, Maxine, Clara, Morrigan, Brielle, Mina, Kira, Sienna, Nadia,
Helena, Rhea, and every character added later. See
`docs/character-art-requirements.md` for the canonical checklist.

Recommended image size: `1920x1080` for CGs, or transparent PNGs for sprites.

The game detects these files at runtime from the Character Sets screen.
Missing files show as empty slots instead of breaking the build.
