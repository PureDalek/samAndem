init python:
    character_asset_sets = {
        "alex": {
            "name": "Sam",
            "folder": "images/nsfw/alex",
            "slots": [
                ("Base", "base.png"),
                ("Lingerie", "underwear.png"),
                ("Nude - Front", "nude_front.png"),
                ("Nude - Alt", "nude_alt.png"),
            ],
        },
        "clara": {
            "name": "Clara",
            "folder": "images/nsfw/clara",
            "slots": [
                ("Base", "base.png"),
                ("Lingerie", "underwear.png"),
                ("Nude - Front", "nude_front.png"),
                ("Nude - Alt", "nude_alt.png"),
            ],
        },
        "maxine": {
            "name": "Maxine",
            "folder": "images/nsfw/maxine",
            "slots": [
                ("Base", "base.png"),
                ("Lingerie", "underwear.png"),
                ("Nude - Front", "nude_front.png"),
                ("Nude - Alt", "nude_alt.png"),
            ],
        },
    }

    def character_asset_path(character_id, filename):
        character = character_asset_sets[character_id]
        return character["folder"] + "/" + filename

screen character_sets():
    tag menu
    default selected_character = "alex"

    use game_menu(_("Character Sets"), scroll="viewport"):

        vbox:
            spacing 22
            xalign 0.5
            xsize 1180

            text _("18+ explicit character asset slots. Add your own 18+ character art files to the listed folders."):
                xalign 0.5
                textalign 0.5

            hbox:
                spacing 18
                xalign 0.5

                for character_id, character in character_asset_sets.items():
                    textbutton character["name"] action SetScreenVariable("selected_character", character_id)

            $ character = character_asset_sets[selected_character]

            label character["name"]:
                xalign 0.5

            grid 2 2:
                spacing 18
                xalign 0.5

                for title, filename in character["slots"]:
                    $ asset_path = character_asset_path(selected_character, filename)

                    button:
                        xsize 430
                        ysize 280
                        if renpy.loadable(asset_path):
                            action ShowMenu("asset_viewer", asset_path, character["name"] + " - " + title)
                        else:
                            action NullAction()

                        vbox:
                            xfill True
                            yfill True

                            if renpy.loadable(asset_path):
                                add asset_path:
                                    xysize (430, 242)
                            else:
                                frame:
                                    xsize 430
                                    ysize 242
                                    background "#222c"
                                    text _("Missing"):
                                        xalign 0.5
                                        yalign 0.5

                            text title:
                                xalign 0.5

            text _("Folder: ") + character["folder"]:
                xalign 0.5
                textalign 0.5

screen asset_viewer(asset_path, title):
    tag menu

    add asset_path

    frame:
        background "#0008"
        padding (48, 0)
        xfill True
        ysize 96
        yalign 0.0

        hbox:
            xfill True
            yalign 0.5

            text title:
                size 42
                color "#ffffff"

            null width 30

            textbutton _("Back") action ShowMenu("character_sets"):
                xalign 1.0

    key "game_menu" action ShowMenu("character_sets")
