# Sam And Em

Sam And Em is an adult visual novel and life-sim built in Ren'Py.

The story follows an 18-year-old young man who discovers that he has a strange power: he can hear the thoughts of people around him, and eventually learn to influence those thoughts. At first, the power feels like a secret advantage. As the story grows, it becomes a moral test.

The player will decide what kind of person he becomes.

## Core Premise

The protagonist begins as an ordinary young adult moving to a new adult academy and trying to understand his place in the world. When the dorm leader accidentally assigns him to Maxine's room because she assumes Sam is a girl's name, he discovers his mind-reading ability during the argument that follows.

At first, the power appears as accidental flashes of private thought. Then Sam realizes he can do more than hear people. He can nudge a thought, lean on hesitation, and push someone toward a decision they were already considering.

His power can be used in different ways:

- Help people by understanding what they cannot say out loud.
- Solve problems by uncovering secrets and hidden motives.
- Build trust through empathy and careful choices.
- Manipulate people for personal gain.
- Push relationships toward darker outcomes.
- Choose between a good path, an evil path, or something in between.

The game should make the player feel that every use of the power has a cost, especially when the easier choice is not the honest one.

## Initial Cast

The first playable version should focus on three characters:

### Main Character

The main character is an 18-year-old young man starting over at a new academy. He arrives with very little control over his life, then discovers he has the ability to read minds after a dorm assignment mistake puts him in Maxine's room. At first, the power appears in flashes: stray thoughts, emotional impressions, and secrets people never meant to reveal.

The player decides whether he becomes empathetic and protective, selfish and manipulative, or something more complicated.

### Dorm Leader

The dorm leader is a confident last-year student who manages the protagonist's dorm. She is busty, mature, socially sharp, and used to being in control. She knows the academy's rules, politics, and private tensions better than almost anyone.

She can become an early guide, obstacle, temptation, or rival depending on the player's choices. Her route should test whether the protagonist respects boundaries when he realizes even strong people have hidden vulnerabilities.

### Maxine

Maxine is the protagonist's best female friend. She is a busty tomboy with a bold personality, a competitive streak, and a habit of teasing the protagonist when he gets too serious. She knows him better than anyone else at the academy and gives the story a more grounded emotional center.

Her route should explore loyalty, jealousy, trust, and the danger of using supernatural power on someone who already cares about him.

## Tone

The tone should mix mystery, drama, romance, temptation, comedy, and adult life-sim storytelling. The game is inspired by adult sandbox visual novels, but it should have its own original characters, locations, plot, and identity.

## Adult Content

This game is intended for adult players only.

All romanceable and sexual characters are fictional adults aged 18 or older. The game is built to depict explicit 18+ adult content, including but not limited to: partial and full nudity, sensual framing, intimate consent-based interaction, and mature romantic visual novel CGs. There is no upper-level euphemistic "non-explicit" policy.

Hard limits that never change:

- Every depicted character must be 18 or older. Minors, loli, shota, school-age framing, and under-18 visual cues are banned in every prompt, preset, and negative prompt.
- Sexual content must be consent-based. Coercion, blackmail, mind-control sexual consent, and assault are banned from prompts and presets.
- Bestiality is banned.
- Character identity cues for the three romanceable characters (Sam, Maxine, Clara) are pinned to "young adult", "18+", and "adult" wording in every identity anchor.

## Character Art Reference

Every character must have a canonical **fully nude** reference artwork in
three places before their art is considered complete:

- Character image: `Sam And Em/game/images/nsfw/<character>/nude_front.png`
- CG: `Sam And Em/game/images/nsfw/cg/cg_<character>_nude_reference.png`
- Source asset: `art/generated/nsfw/<character>_nude_reference_01.png` with
  matching `.json` metadata

The fully nude reference is required for every character in the current cast
(Sam, Maxine, Clara, Morrigan, Brielle, Mina, Kira, Sienna, Nadia, Helena, and
Rhea) and every character added later. Lingerie, towels, robes, bedsheets,
cropped framing, and implied nudity do not satisfy the requirement. The
reference must show the whole character from head to feet with their defining
body details unobstructed, so future sprites and CGs have a reliable identity
source.

See `docs/character-art-requirements.md` for the full definition, file sizes,
and completion checklist.

## Main Features

Planned systems include:

- Branching good and evil story paths.
- Mind-reading dialogue options.
- Mind-influence choices with consequences.
- Relationship stats.
- Character schedules.
- Time of day and day progression.
- Quest log.
- Town map with repeatable locations.
- Money and inventory systems.
- Phone/messages system.
- Unlockable romance and NSFW scenes.
- Multiple endings based on morality and relationships.

## Current State

Current version: v0.4.0.

The base prototype opens with the academy dorm setup:

- The protagonist arrives at the academy dorm and reunites with Maxine.
- The protagonist meets Clara, the dorm leader, and experiences a second mind-reading incident.

The prototype introduces the first good/evil choices through how the player responds to private thoughts, then v0.2.0 continues into the first complete branching route slice.

v0.3.0 is the Expanded Cast release:

- Recovered the lost `expanded_cast.rpy` / `expanded_routes.rpy` sources from compiled bytecode (the game had been shipping 7,500 words of route content that was invisible to git and unreachable from `start`).
- Adds eight fully written preview routes: Morrigan Vale, Brielle Ashford, Mina Sato, Kira Sol, Sienna Cross, Nadia Quinn, Headmaster Helena Voss, and Rhea Mallory.
- 10 beats per route, 15 choices, unique prose (~7,800 words), and 3 endings per route (24 endings) driven by the good/risky score.
- The route hub is now entered from the intro; the original Maxine / Clara storyline is the "Continue" branch.
- Full art pass: 32 new character sprites (four per route) and 80 route CGs, plus rebuilt 1920x1080 backgrounds, story CGs, gallery art, 12 character asset slots, and 7 NSFW story CGs.
- Routes already completed are marked in the hub and tracked in persistent save data.

v0.4.0 is the Maxine Unbound release:

- Five new explicit scenes on Maxine's route (~2,600 words), in the order the player reaches them: the traded shower, the night the fan dies, the library after closing, the last-lie confession, and the wedding night / morning after.
- New acts: tit-fuck, two facials, the accidental finish across her face, a library "oops" on her thigh, and two scenes where she is covered and unbothered.
- More continuous nudity: she sleeps bare, moves around the room bare, and the morning-after CG is her in Sam's shirt and nothing else.
- **15 new 1536x1152 CGs** wired into the route, with single-figure composition QA on the solo shower frame.
- The protagonist is now consistently named **Sam** everywhere — text, menus, docs and prompts. "Alex" was a legacy default that disagreed with the title; the room-assignment joke now lands on "short for Samantha."
- Route flags `mx_shower_done` / `mx_library_done`; the library scene is gated on `maxine_trust >= 2`.

v0.0.2 adds the first character gallery with one explicit 18+ image entry each for Sam, Clara, and Maxine.

v0.0.3 adds the updater foundation and updates the opening plot:

- In-game Update screen.
- Remote manifest checker.
- Download button for newer APK versions.
- Private GitHub Actions Android artifact workflow.
- Example update manifest and setup notes.
- New dorm assignment mistake scene.
- First morning roommate scene with Maxine.

v0.0.4 is the bootstrap updater build that points at the live manifest URL.

v0.0.5 is the first target update build referenced by `updates/latest.json`.

v0.0.6 adds the shower mistake sequence:

- Sam accidentally enters the adult women's showers because of unclear dorm signage.
- Clara removes him from the situation and creates a temporary shower schedule.
- The scene reinforces the theme that mind-reading should create responsibility, not entitlement.

v0.0.7 adds the adult content warning and 18+ entry gate.

v0.0.8 adds missing story visuals:

- Room 214 background.
- Maxine morning CG.
- Clara shower intervention CG.
- Clara shower schedule CG.

v0.0.9 fixes updater SSL fallback handling on Android and adds clearer errors when the manifest URL is private or unavailable.

v0.1.0 adds the Character Sets screen and optional adult asset slots for user-provided character art.

v0.2.0 adds the first complete branching route slice:

- Maxine happy ending: The Wedding Garden.
- Lady happy ending: Two Tickets Anywhere.
- Max bad ending: The Dropout.
- Lady bad ending: The Locked Door.
- Two neutral fallback endings.
- A documented route choice tree in `docs/route-choice-tree.md`.

v0.2.1 rebuilds the plot route from the corrected repository root, fixes asset generation paths, and updates the local update manifest for the plot/endings build.

## Development Notes

Project folder:

```text
Sam And Em/
```

Main Ren'Py files:

```text
Sam And Em/game/script.rpy
Sam And Em/game/options.rpy
Sam And Em/game/gui.rpy
Sam And Em/game/screens.rpy
```

The story should begin in `script.rpy`. New systems can be added as separate `.rpy` files under `Sam And Em/game/` as the project grows.
