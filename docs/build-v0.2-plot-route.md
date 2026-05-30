# Build v0.2 - Plot Route

This version incorporates the backwards plot tree into the real Sam And Em Ren'Py project at:

```text
C:\Repos\AI\samandem\Sam And Em
```

## Story Files

- `Sam And Em/game/script.rpy` now jumps from the shower schedule scene into `expanded_route_hub`, then can continue into `route_act_one`.
- `Sam And Em/game/expanded_routes.rpy` contains the generated expanded cast route hub, eight 15-choice route scaffolds, and the 10-situation binary gauntlet.
- `Sam And Em/game/routes_v02.rpy` contains the complete v0.2 route expansion.
- `docs/route-choice-tree.md` documents the ending logic and route pressure.

## Assets

The route uses CGs and character-set assets under:

```text
Sam And Em/game/images/nsfw/
```

Root-level `game/` and `prompts/` folders are ignored because they come from running tools in the wrong workspace. Use `scripts/prompts/` for prompt JSON and `Sam And Em/game/` for playable Ren'Py files.

## Endings

- `The Wedding Garden` - Maxine happy end.
- `Two Tickets Anywhere` - Lady happy end.
- `The Dropout` - Max bad end.
- `The Locked Door` - Lady bad end.
- `Transfer Papers` and `Summer Alone` - neutral fallbacks.

## Build Notes

The local Android helper is:

```powershell
python --version
powershell -ExecutionPolicy Bypass -File scripts\build_android_local.ps1
```

The project version and Android metadata are set to `0.2.3`.
