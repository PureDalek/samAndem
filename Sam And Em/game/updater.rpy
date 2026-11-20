default update_manifest_url = "https://raw.githubusercontent.com/PureDalek/samandEm/main/updates/latest.json"
default update_status = "Ready to check for updates."
default update_latest = None
default update_checking = False

init python:
    import json
    import ssl
    import urllib.request
    import urllib.error

    def update_version_tuple(value):
        parts = []

        for part in value.split("."):
            try:
                parts.append(int(part))
            except Exception:
                parts.append(0)

        while len(parts) < 3:
            parts.append(0)

        return tuple(parts[:3])

    def check_for_update():
        global update_status
        global update_latest
        global update_checking

        if not update_manifest_url:
            update_latest = None
            update_status = "Updater is not configured yet. Add a manifest URL in updater.rpy."
            return

        update_checking = True
        update_status = "Checking for updates..."
        renpy.restart_interaction()

        try:
            request = urllib.request.Request(
                update_manifest_url,
                headers={
                    "User-Agent": "SamAndEmUpdater/" + config.version,
                    "Accept": "application/json",
                },
            )

            try:
                with urllib.request.urlopen(request, timeout=12) as response:
                    data = response.read().decode("utf-8")

            except ssl.SSLError:
                # Some Android Ren'Py builds lack a usable CA bundle for Python.
                # The APK download still opens in Android's browser/installer;
                # this fallback only lets us read the small update manifest.
                context = ssl._create_unverified_context()
                with urllib.request.urlopen(request, timeout=12, context=context) as response:
                    data = response.read().decode("utf-8")

            manifest = json.loads(data)
            latest_version = manifest.get("version", "")
            apk_url = manifest.get("apk_url", "")

            if not latest_version or not apk_url:
                update_latest = None
                update_status = "The update manifest is missing version or apk_url."
                return

            update_latest = manifest

            if update_version_tuple(latest_version) > update_version_tuple(config.version):
                update_status = "Version {} is available.".format(latest_version)
            else:
                update_status = "You are already on the latest version."

        except urllib.error.HTTPError as exc:
            update_latest = None

            if exc.code == 404:
                update_status = "Update manifest was not found. The repo or release may be private."
            else:
                update_status = "Update check failed: HTTP {}".format(exc.code)

        except Exception as exc:
            update_latest = None
            update_status = "Update check failed: {}".format(exc)

        finally:
            update_checking = False
            renpy.restart_interaction()

    def download_update():
        if not update_latest:
            renpy.notify("Check for updates first.")
            return

        apk_url = update_latest.get("apk_url")

        if not apk_url:
            renpy.notify("No APK URL found.")
            return

        renpy.open_url(apk_url)
        renpy.notify("Opening update download. Android will ask before installing.")

screen update_screen():
    tag menu

    use game_menu(_("Update"), scroll="viewport"):

        vbox:
            spacing 24
            xalign 0.5
            xsize 1120

            label _("Current Version"):
                xalign 0.5

            text "[config.version]":
                xalign 0.5

            label _("Status"):
                xalign 0.5

            text "[update_status]":
                xalign 0.5
                textalign 0.5

            hbox:
                spacing 24
                xalign 0.5

                textbutton _("Check") action Function(check_for_update) sensitive not update_checking

                if update_latest and update_version_tuple(update_latest.get("version", "0.0.0")) > update_version_tuple(config.version):
                    textbutton _("Download") action Function(download_update)

            if update_latest:
                $ notes = update_latest.get("notes", "")
                if notes:
                    label _("Release Notes"):
                        xalign 0.5

                    text notes:
                        xalign 0.5
                        textalign 0.5
