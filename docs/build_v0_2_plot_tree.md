# Build v0.2 - Plot Tree Version

This build incorporates `docs/plot_tree.md` into a playable Ren'Py source version.

## Added

- `game/options.rpy` sets the project name, version, resolution, save directory, and build name.
- `game/script.rpy` adds a complete branching visual novel route:
  - Act 1: first week, Lady introduction, Max warning.
  - Act 2: scholarship review, Maxine almost-date, Lady favor, Max pressure.
  - Act 3: gala route lock, final route tests, endings.
- Existing CG assets in `game/images/nsfw/cg/` are wired into the route.
- Existing character sprites for Alex, Maxine, and Clara are declared for early scenes.

## Endings

- `THE WEDDING GARDEN` - Maxine happy end.
- `TWO TICKETS ANYWHERE` - Lady happy end.
- `THE DROPOUT` - Max bad end.
- `THE LOCKED DOOR` - Lady bad end.
- `TRANSFER PAPERS` and `SUMMER ALONE` - neutral fallbacks.

## Route Variables

- `maxine_trust`
- `lady_trust`
- `integrity`
- `max_rage`
- `college_stability`
- `lady_heat`

## How To Run

Open this folder as a Ren'Py project and launch it from the Ren'Py launcher.

If building a distribution from the launcher, the configured build name is:

```text
ourgame_plot_tree_v0_2
```
