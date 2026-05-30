#!/usr/bin/env python3
"""Generate Sam And Em expanded cast design and prompt catalogs.

This is intentionally data-first: prompts and route specs are saved before any
cloud or local generation so image outputs can be recreated later.
"""

from __future__ import annotations

import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PROMPT_DIR = REPO / "scripts" / "prompts"
DOCS_DIR = REPO / "docs"


NEGATIVE_PROMPT = (
    "low quality, blurry, bad anatomy, extra fingers, missing fingers, "
    "deformed hands, watermark, text, logo, explicit nudity, exposed nipples, "
    "visible genitals, sex act, penetration, oral sex, see-through clothing, "
    "minor, child, teen"
)


STYLE_ANCHOR = (
    "18+ adult cast, mature college visual novel CG, polished cinematic game art, "
    "everyone fully clothed or securely covered, emotionally charged but non-explicit"
)


CHARACTERS = [
    {
        "id": "morrigan",
        "name": "Morrigan Vale",
        "role": "nerd goth occult-studies tutor",
        "age": 22,
        "identity": "short black bob with violet underlights, pale olive skin, gray eyes, round glasses, black cardigan, silver moon pins, anxious sharp wit",
        "palette": "black, violet, silver, library green",
        "route_theme": "truth hidden in forbidden books",
        "happy_end": "Alex helps her publish the buried archive safely and they open a tiny midnight study room together.",
        "bad_end": "Alex uses her research as leverage and she vanishes from campus before the archive burns.",
        "outfits": [
            ("base", "black cardigan, pleated charcoal skirt, opaque tights, round glasses, moon pins"),
            ("raincoat", "oversized black raincoat, violet scarf, messenger bag full of annotated books"),
            ("formal", "black velvet formal dress with high neckline, silver constellation jewelry"),
            ("archive", "rolled sleeves, ink-stained gloves, lanyard access card, practical boots"),
        ],
        "cg_scenes": [
            "late library table surrounded by coded notes and cold coffee",
            "rainy archive doorway with a forbidden key between her fingers",
            "occult club basement where candles are electric but the fear is real",
            "gala corner where she recognizes the headmaster's forged signature",
            "quiet stairwell confession after Alex hears a thought she meant to bury",
            "server room discovery with violet monitor light on her glasses",
            "greenhouse midnight study break under glass roof rain",
            "disciplinary hearing where she risks expulsion to tell the truth",
            "burned archive aftermath with soot on her sleeves",
            "happy ending private study room opening after graduation",
        ],
    },
    {
        "id": "brielle",
        "name": "Brielle Ashford",
        "role": "blonde bully and legacy-donor queen",
        "age": 22,
        "identity": "long glossy blonde ponytail, icy blue eyes, athletic rich-girl posture, white varsity jacket, diamond hairclip, perfect smile used like a weapon",
        "palette": "white, gold, powder blue, black accents",
        "route_theme": "power, humiliation, and choosing whether to protect the person who hurt you",
        "happy_end": "Alex forces Brielle to face what her family bought, and she publicly breaks from them.",
        "bad_end": "Alex humiliates her back until she becomes Max's most useful ally.",
        "outfits": [
            ("base", "white varsity jacket, gold-trimmed top, tailored campus skirt, diamond hairclip"),
            ("training", "opaque pale blue athletic set, varsity warmup jacket, high ponytail"),
            ("formal", "elegant gold-and-white gala dress with structured shoulders, high collar, opaque bodice, floor-length closed skirt with no slit, fully covered chest, diamond hairclip"),
            ("detention", "rumpled school uniform jacket over a buttoned white shirt and opaque undershirt, tailored skirt, phone clutched like armor, makeup slightly smudged, fully covered chest"),
        ],
        "cg_scenes": [
            "cafeteria table where she blocks Alex's seat with a smile",
            "locker hallway confrontation while her friends record everything",
            "training room challenge after she insults Maxine",
            "donor gala balcony where her father calls during a threat",
            "empty classroom apology that almost turns into another attack",
            "rain-soaked parking lot after Max betrays her",
            "student council office with blackmail photos spread out",
            "public assembly where she chooses truth over family money",
            "bad route corridor where she gives Max the final rumor",
            "happy ending scholarship fundraiser she rebuilds honestly",
        ],
    },
    {
        "id": "mina",
        "name": "Mina Sato",
        "role": "art major and mural rebel",
        "age": 23,
        "identity": "messy teal-black pixie cut, warm brown eyes, paint on hands, cropped denim jacket over opaque black tank, sketchbook always under one arm",
        "palette": "teal, coral, denim, warm paint colors",
        "route_theme": "art as evidence and confession",
        "happy_end": "Alex helps Mina finish a forbidden mural that exposes the academy without destroying her future.",
        "bad_end": "Alex pushes her into vandalism, and she takes the fall for his need to be dramatic.",
        "outfits": [
            ("base", "paint-splattered denim jacket, opaque black tank, loose cargo pants"),
            ("studio", "oversized apron, tied hair, fingerless gloves, paint-stained sneakers"),
            ("formal", "asymmetric teal gallery dress, coral earrings, clean boots"),
            ("mural", "hooded work jumpsuit, respirator around neck, paint roller harness"),
        ],
        "cg_scenes": [
            "studio introduction with canvas facing the wall",
            "roof mural sketch under campus security lights",
            "gallery critique where Alex hears the professor's cruel thought",
            "paint fight that stays playful and fully clothed",
            "storage closet discovery of stolen donor portraits",
            "night wall-painting decision with lookouts posted",
            "formal gallery opening where her work accuses the headmaster",
            "disciplinary board where she refuses to name Alex",
            "bad ending whitewashed mural and empty studio",
            "happy ending public mural unveiling after the academy backs down",
        ],
    },
    {
        "id": "kira",
        "name": "Kira Sol",
        "role": "cosplayer and prop-engineering prodigy",
        "age": 21,
        "identity": "warm tan skin, dark brown twin buns with pink clips, bright hazel eyes, cropped bomber jacket covered in enamel pins, confident theatrical grin",
        "palette": "pink, black, neon cyan, chrome",
        "route_theme": "identity, performance, and what remains when the costume comes off",
        "happy_end": "Alex protects her real identity during a convention scandal and helps her choose the stage on her own terms.",
        "bad_end": "Alex leaks her secret to win a fight and destroys her convention career.",
        "outfits": [
            ("base", "pin-covered black bomber jacket, pink hoodie, cargo skirt over opaque leggings"),
            ("workshop", "safety goggles, tool belt, oversized graphic tee, fingerless gloves"),
            ("hero_cosplay", "original armored heroine costume, opaque bodysuit, chrome shoulder plates, cape"),
            ("formal", "sleek black-and-pink event dress with prop-star hairpiece"),
        ],
        "cg_scenes": [
            "prop workshop where sparks fly from a harmless broken sword",
            "campus convention booth surrounded by handmade armor",
            "masked hallway rescue when Max tries to expose her",
            "late-night sewing floor with fabric everywhere",
            "stage rehearsal where Alex hears panic under her perfect voice",
            "storage room choice to hide or reveal the costume damage",
            "cosplay contest finale under neon lights",
            "green room confrontation after her legal name leaks",
            "bad ending empty convention table with torn badge",
            "happy ending original hero premiere with Alex in the front row",
        ],
    },
    {
        "id": "sienna",
        "name": "Sienna Cross",
        "role": "swimmer and scholarship rival",
        "age": 22,
        "identity": "deep brown skin, short natural curls under swim cap, powerful shoulders, calm green eyes, navy team jacket, stopwatch necklace",
        "palette": "navy, aqua, white, lane-line red",
        "route_theme": "discipline, rivalry, and refusing to cheat even when everyone expects it",
        "happy_end": "Alex clears her name in a doping accusation and she chooses trust over perfect control.",
        "bad_end": "Alex lets suspicion win and she loses her scholarship defending him.",
        "outfits": [
            ("base", "navy team tracksuit, white sneakers, stopwatch necklace"),
            ("pool", "modest one-piece racing swimsuit, swim cap, towel over shoulders"),
            ("formal", "aqua formal jumpsuit, silver chain, sleek curls"),
            ("rehab", "team hoodie, kinesiology tape, recovery sandals, duffel bag"),
        ],
        "cg_scenes": [
            "pool deck first rivalry with stopwatch between them",
            "early morning lane practice while campus is empty",
            "trainer office where test results look suspicious",
            "rainy bus stop after an away meet loss",
            "locker room hallway where Alex chooses privacy over mind-reading",
            "scholarship hearing with chlorine still in her hair",
            "infirmary recovery after she swims injured",
            "championship pool moment before the final race",
            "bad ending empty lane and revoked scholarship board",
            "happy ending sunrise swim after her record is restored",
        ],
    },
    {
        "id": "nadia",
        "name": "Nadia Quinn",
        "role": "campus nurse and quiet whistleblower",
        "age": 27,
        "identity": "soft copper curls in a low bun, amber eyes, warm brown skin, teal scrubs under cream cardigan, tired kindness, badge clipped backwards",
        "palette": "teal, cream, copper, clinic white",
        "route_theme": "care, consent, and the cost of medical secrets",
        "happy_end": "Alex helps Nadia expose falsified clinic records without violating patient privacy.",
        "bad_end": "Alex pressures her for private files and she loses her license protecting students.",
        "outfits": [
            ("base", "teal scrubs, cream cardigan, badge, practical flats"),
            ("night_shift", "navy scrub jacket, messy bun, coffee, emergency pager"),
            ("formal", "modest copper wrap dress, cream shawl, small gold earrings"),
            ("field", "first-aid vest, trauma bag, rain boots, tied-back curls"),
        ],
        "cg_scenes": [
            "clinic intake where she notices Alex hiding a bruise",
            "medicine cabinet audit with missing labels",
            "night shift hallway lit by vending machines",
            "field injury at the pool where she protects Sienna's privacy",
            "records room moral test with locked patient files",
            "coffee break confession about the headmaster's pressure",
            "gala medical emergency staged to steal records",
            "licensing board call while Alex waits outside",
            "bad ending clinic door with her name removed",
            "happy ending mobile clinic day after the whistleblower case",
        ],
    },
    {
        "id": "helena",
        "name": "Headmaster Helena Voss",
        "role": "evil headmaster and academy power broker",
        "age": 39,
        "identity": "tall poised woman, silver-streaked black hair in a severe bun, dark green eyes, tailored black suit, emerald brooch, calm smile that never reaches her eyes",
        "palette": "black, emerald, ivory, antique gold",
        "route_theme": "authority, corruption, and the temptation to trade truth for protection",
        "happy_end": "Alex exposes Voss through evidence rather than revenge, forcing her resignation.",
        "bad_end": "Alex accepts her bargain and becomes her informant.",
        "outfits": [
            ("base", "tailored black suit, ivory blouse, emerald brooch, polished heels"),
            ("gala", "black-and-emerald formal gown with high collar, gold academy chain"),
            ("office", "rolled sleeves, reading glasses, legal folders, severe bun"),
            ("trial", "charcoal court-ready suit, no jewelry except academy ring"),
        ],
        "cg_scenes": [
            "headmaster office introduction with Alex's file open",
            "scholarship threat delivered as a polite offer",
            "gala toast where every donor applauds at once",
            "private elevator bargain after Alex reads her thought",
            "archive confrontation with Morrigan's evidence",
            "clinic-record blackmail over Nadia's shoulder",
            "student assembly where Mina's mural goes live behind her",
            "trial preparation room with her ring on the table",
            "bad ending office contract signing in cold lamplight",
            "happy ending resignation walk past silent students",
        ],
    },
    {
        "id": "rhea",
        "name": "Rhea Mallory",
        "role": "campus reporter and debate-club tactician",
        "age": 24,
        "identity": "sharp dark curls, russet skin, intense hazel eyes, red blazer, recorder pen, old press badge, smile like a cross-examination",
        "palette": "red, charcoal, paper white, brass",
        "route_theme": "truth, privacy, and who gets hurt when a story breaks",
        "happy_end": "Alex helps Rhea publish the truth with consent from the students involved.",
        "bad_end": "Alex feeds her secrets for revenge and the story ruins innocent people.",
        "outfits": [
            ("base", "red blazer, black trousers, press badge, recorder pen"),
            ("field", "charcoal trench coat, camera bag, rain-specked notebook"),
            ("debate", "crisp white shirt, red tie, lapel mic, formal slacks"),
            ("late_night", "oversized academy sweatshirt, messy curls, laptop glow"),
        ],
        "cg_scenes": [
            "newspaper office interrogation over cold pizza",
            "debate club ambush where she proves Alex lied by omission",
            "rainy stakeout outside the donor building",
            "audio booth where a recording can save or ruin Maxine",
            "library microfilm discovery with Morrigan beside her",
            "anonymous source meeting that could be a trap",
            "gala press line where she asks the forbidden question",
            "deadline night with the story title still blank",
            "bad ending printed article that names the wrong student",
            "happy ending consent-based expose on the academy steps",
        ],
    },
]


BINARY_SITUATIONS = [
    ("bs01", "Rumor Screenshot", "Delete the screenshot and ask the person directly.", "Forward it to gain leverage."),
    ("bs02", "Locked Archive", "Find an authorized witness before opening it.", "Pick the lock before security returns."),
    ("bs03", "Clinic File", "Protect patient privacy.", "Search the file for useful dirt."),
    ("bs04", "Pool Test", "Demand a retest in public.", "Quietly swap the sample labels."),
    ("bs05", "Gala Lie", "Tell Maxine why the Lady is there.", "Pretend the Lady is just a donor guest."),
    ("bs06", "Mural Night", "Paint only the approved wall.", "Use the forbidden wall for maximum impact."),
    ("bs07", "Cosplay Mask", "Protect Kira's real name.", "Reveal it to stop a rumor faster."),
    ("bs08", "Bully Apology", "Let Brielle apologize without an audience.", "Make her apologize in public."),
    ("bs09", "Headmaster Bargain", "Refuse protection that costs someone else.", "Accept the deal and stay enrolled."),
    ("bs10", "Reporter Deadline", "Delay the story until consent is clear.", "Publish now before the evidence disappears."),
]


ROUTE_STEPS = [
    ("01_first_signal", "Notice her first contradiction", "Ask a direct, respectful question", "Use mind-reading before she consents"),
    ("02_public_pressure", "A public scene pulls her into Alex's trouble", "Lower the temperature", "Turn the crowd into a weapon"),
    ("03_private_offer", "She offers private help with a hidden cost", "Ask what the cost is", "Accept because it feels intimate"),
    ("04_max_interference", "Max or another rival twists the moment", "Document it", "Answer with humiliation"),
    ("05_first_outfit_shift", "She changes context and outfit for her real world", "Notice the emotional shift", "Comment only on how she looks"),
    ("06_secret_room", "A restricted room becomes available", "Bring a witness", "Go alone for speed"),
    ("07_false_evidence", "Evidence points at the wrong person", "Slow down and verify", "Use it immediately"),
    ("08_vulnerable_confession", "She admits why this matters to her", "Keep the confession private", "Trade it for leverage"),
    ("09_scholarship_cost", "The route threatens Alex's scholarship", "Accept consequences openly", "Hide the connection"),
    ("10_second_outfit_shift", "She appears in a formal or role-specific outfit", "Meet the role she is choosing", "Treat the outfit as permission"),
    ("11_headmaster_move", "The headmaster offers a bargain", "Refuse the bargain", "Take protection now"),
    ("12_friendship_test", "Maxine/Clara asks what Alex is doing", "Tell the partial truth clearly", "Lie until the route is locked"),
    ("13_route_lock", "The route asks for a visible commitment", "Choose her path with boundaries", "Choose possession or secrecy"),
    ("14_final_evidence", "The final proof is dangerous to use", "Use it with consent", "Use it for revenge"),
    ("15_ending_choice", "Final binary ending gate", "Protect truth and autonomy", "Win at any cost"),
]


def asset_name(character_id: str, kind: str, slug: str) -> str:
    return f"{character_id}_{kind}_{slug}".replace("-", "_")


def make_sprite_prompt(character: dict[str, object], slot: str, outfit: str) -> dict[str, str]:
    cid = str(character["id"])
    return {
        "name": asset_name(cid, "sprite", slot),
        "character": cid,
        "slot": slot,
        "filename": f"{asset_name(cid, 'sprite', slot)}_{{index:02d}}.png",
        "renpy_path": f"Sam And Em/game/images/expanded/{cid}/{slot}.png",
        "cloud_prompt": (
            f"Use case: stylized-concept. Asset type: Ren'Py character sprite. "
            f"Subject: {character['name']}, {character['age']} year old adult, {character['role']}; "
            f"{character['identity']}. Outfit: {outfit}. Style: polished Sam And Em visual novel sprite, "
            f"full body standing pose, plain light background, clean linework, no text, no watermark, non-explicit."
        ),
        "local_a1111_prompt": (
            f"18+ adult visual novel sprite, {character['name']}, {character['role']}, "
            f"{character['identity']}, {outfit}, full body standing pose, plain light background, "
            f"clean linework, polished game asset, non-explicit"
        ),
    }


def make_cg_prompt(character: dict[str, object], index: int, scene: str) -> dict[str, str]:
    cid = str(character["id"])
    slug = f"{index:02d}"
    return {
        "name": asset_name(cid, "cg", slug),
        "character": cid,
        "filename": f"{asset_name(cid, 'cg', slug)}_{{index:02d}}.png",
        "renpy_path": f"Sam And Em/game/images/expanded/cg/{asset_name(cid, 'cg', slug)}.png",
        "scene": scene,
        "cloud_prompt": (
            f"Use case: illustration-story. Asset type: Ren'Py CG. {STYLE_ANCHOR}. "
            f"Main character: {character['name']}, {character['age']} year old adult, {character['role']}; "
            f"{character['identity']}. Scene: {scene}. Composition: cinematic 16:9 visual novel event CG, "
            f"clear emotional focus, campus setting, no text, no watermark, non-explicit."
        ),
        "local_a1111_prompt": (
            f"{STYLE_ANCHOR}, {character['name']}, {character['role']}, {character['identity']}, "
            f"{scene}, cinematic 16:9 visual novel event CG, campus setting, no text, no watermark"
        ),
    }


def make_route_node(character: dict[str, object], step: tuple[str, str, str, str]) -> dict[str, object]:
    step_id, situation, honest_choice, risky_choice = step
    cid = str(character["id"])
    return {
        "id": f"{cid}_{step_id}",
        "situation": f"{character['name']}: {situation}.",
        "choice_a": {
            "text": honest_choice,
            "effect": ["trust +1", "integrity +1"],
        },
        "choice_b": {
            "text": risky_choice,
            "effect": ["heat +1", "control +1"],
        },
    }


def build_assets() -> dict[str, object]:
    assets: list[dict[str, str]] = []
    for character in CHARACTERS:
        for slot, outfit in character["outfits"]:
            assets.append(make_sprite_prompt(character, slot, outfit))
        for index, scene in enumerate(character["cg_scenes"], 1):
            assets.append(make_cg_prompt(character, index, scene))

    return {
        "api_url": "cloud-imagegen-or-http://127.0.0.1:7860",
        "output_dir": "art/generated/expanded_cast",
        "renpy_root": "Sam And Em",
        "negative_prompt": NEGATIVE_PROMPT,
        "notes": [
            "Generate cloud images from cloud_prompt first.",
            "Use local_a1111_prompt to recreate locally with Automatic1111.",
            "All characters are adults. Keep generated assets non-explicit and fully covered.",
            "Any outfit/context change has a dedicated sprite prompt.",
        ],
        "characters": [
            {
                key: value
                for key, value in character.items()
                if key not in {"cg_scenes", "outfits"}
            }
            for character in CHARACTERS
        ],
        "assets": assets,
    }


def build_routes() -> dict[str, object]:
    return {
        "requirements": {
            "new_character_count": len(CHARACTERS),
            "minimum_female_characters_requested": 4,
            "binary_situation_count": len(BINARY_SITUATIONS),
            "minimum_route_depth": len(ROUTE_STEPS),
            "cg_prompts_per_character": 10,
        },
        "binary_situations": [
            {"id": sid, "title": title, "choice_a": a, "choice_b": b}
            for sid, title, a, b in BINARY_SITUATIONS
        ],
        "route_trees": {
            str(character["id"]): {
                "character": character["name"],
                "theme": character["route_theme"],
                "happy_end": character["happy_end"],
                "bad_end": character["bad_end"],
                "depth": len(ROUTE_STEPS),
                "nodes": [make_route_node(character, step) for step in ROUTE_STEPS],
            }
            for character in CHARACTERS
        },
    }


def build_doc(assets: dict[str, object], routes: dict[str, object]) -> str:
    lines = [
        "# Expanded Cast And Route Plan",
        "",
        "This file is generated by `scripts/generate_expansion_content.py`.",
        "",
        "## Scope Covered In This Slice",
        "",
        f"- New adult characters defined: {len(CHARACTERS)}.",
        f"- Binary situations defined: {len(BINARY_SITUATIONS)}.",
        f"- Route depth per new character: {len(ROUTE_STEPS)} choices.",
        "- CG prompts per new character: 10.",
        "- Outfit-changing sprite prompts are saved for every listed outfit slot.",
        "",
        "## New Characters",
        "",
    ]
    for character in CHARACTERS:
        lines.extend(
            [
                f"### {character['name']} - {character['role']}",
                "",
                f"- Age: {character['age']} adult.",
                f"- Identity: {character['identity']}",
                f"- Palette: {character['palette']}",
                f"- Route theme: {character['route_theme']}",
                f"- Happy end: {character['happy_end']}",
                f"- Bad end: {character['bad_end']}",
                f"- Sprite outfit slots: {', '.join(slot for slot, _ in character['outfits'])}",
                "",
            ]
        )

    lines.extend(
        [
            "## Binary Situations",
            "",
            "| ID | Situation | Choice A | Choice B |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in routes["binary_situations"]:
        lines.append(f"| `{item['id']}` | {item['title']} | {item['choice_a']} | {item['choice_b']} |")

    lines.extend(
        [
            "",
            "## Prompt Files",
            "",
            "- `scripts/prompts/expanded_cast_assets.json` stores cloud and local prompts for sprites and CGs.",
            "- `scripts/prompts/expanded_cast_routes.json` stores the 10 binary situations and every 15-step route tree.",
            "",
            "## Next Implementation Steps",
            "",
            "1. Generate cloud base sprites for each new character's `base` outfit.",
            "2. Review and accept/reject the generated cloud images.",
            "3. Generate alternate outfit sprites as their route scenes are implemented.",
            "4. Generate CGs in route order, starting with each character's first two route-lock CGs.",
            "5. Convert accepted prompts into Ren'Py image declarations and playable labels.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    assets = build_assets()
    routes = build_routes()

    (PROMPT_DIR / "expanded_cast_assets.json").write_text(
        json.dumps(assets, indent=2) + "\n",
        encoding="utf-8",
    )
    (PROMPT_DIR / "expanded_cast_routes.json").write_text(
        json.dumps(routes, indent=2) + "\n",
        encoding="utf-8",
    )
    (DOCS_DIR / "expanded-cast-route-plan.md").write_text(
        build_doc(assets, routes),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
