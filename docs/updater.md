# Private Update Flow

The game includes an update screen in v0.0.3.

## How It Works

The in-game updater checks a JSON manifest:

```json
{
  "version": "0.0.4",
  "apk_url": "https://updates.example.com/samandem/android/latest.apk",
  "sha256": "replace-with-apk-sha256",
  "notes": "Release notes shown in the game."
}
```

If the manifest version is newer than the installed game version, the Update screen shows a Download button. On Android, the download opens through the system browser or installer flow. Android will always ask the player before installing an APK.

## Secure Storage

Do not embed a GitHub token, private API key, or permanent secret in the APK. APK contents can be extracted.

Recommended setup:

1. Keep the GitHub repository private.
2. Use `.github/workflows/android-artifact.yml` to build APK artifacts.
3. Add a small private update gate later, such as a Cloudflare Worker.
4. The game points `update_manifest_url` to the Worker URL.
5. The Worker verifies tester access and returns either the manifest or a short-lived APK URL.

This keeps the app free of secrets while still blocking unauthorized downloads.

## Current Placeholder

The game currently has:

```renpy
default update_manifest_url = ""
```

Set this in `Sam And Em/game/updater.rpy` when the private update gate exists.
