# Sam And Em

Sam And Em is an adult visual novel and life-sim built in Ren'Py.

The story follows an 18-year-old young man who discovers that he has a strange power: he can hear the thoughts of people around him, and eventually learn to influence those thoughts. At first, the power feels like a secret advantage. As the story grows, it becomes a moral test.

The player will decide what kind of person he becomes.

## Core Premise

The protagonist begins as an ordinary young adult moving to a new adult academy and trying to understand his place in the world. When the dorm leader accidentally assigns him to Maxine's room because she assumes Alex is a girl's name, he discovers his mind-reading ability during the argument that follows.

At first, the power appears as accidental flashes of private thought. Then Alex realizes he can do more than hear people. He can nudge a thought, lean on hesitation, and push someone toward a decision they were already considering.

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

All romanceable and sexual characters must be explicitly 18 or older. NSFW content can exist in the story, but it should be written with clear adult framing and avoid sexual situations based on force, blackmail, or mind-control coercion.

Mind-reading and manipulation can create moral tension, but sexual scenes should be based on consent and character agency.

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

Current version: v0.0.5.

The first playable prototype contains two scenes:

- The protagonist arrives at the academy dorm and reunites with Maxine.
- The protagonist meets Clara, the dorm leader, and experiences a second mind-reading incident.

The prototype introduces the first good/evil choices through how the player responds to private thoughts.

v0.0.2 adds the first character gallery with one private image entry each for Alex, Clara, and Maxine.

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
