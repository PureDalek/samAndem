image gallery alex private 01 = "images/gallery/alex_private_01.png"
image gallery alex private 02 = "images/gallery/alex_private_02.png"
image gallery clara private 01 = "images/gallery/clara_private_01.png"
image gallery clara private 02 = "images/gallery/clara_private_02.png"
image gallery maxine private 01 = "images/gallery/maxine_private_01.png"
image gallery maxine private 02 = "images/gallery/maxine_private_02.png"

default gallery_character = "alex"

init python:
    gallery_entries = {
        "alex": {
            "name": "Alex",
            "images": [
                ("Private 01", "gallery alex private 01"),
                ("Private 02", "gallery alex private 02"),
            ],
        },
        "clara": {
            "name": "Clara",
            "images": [
                ("Private 01", "gallery clara private 01"),
                ("Private 02", "gallery clara private 02"),
            ],
        },
        "maxine": {
            "name": "Maxine",
            "images": [
                ("Private 01", "gallery maxine private 01"),
                ("Private 02", "gallery maxine private 02"),
            ],
        },
    }

screen character_gallery():
    tag menu
    default gallery_character = "alex"

    use game_menu(_("Gallery")):

        vbox:
            spacing 24
            xalign 0.5
            yalign 0.0

            hbox:
                spacing 18
                xalign 0.5

                for character_id, character in gallery_entries.items():
                    textbutton character["name"] action SetScreenVariable("gallery_character", character_id)

            $ character = gallery_entries[gallery_character]

            label character["name"]:
                xalign 0.5

            grid 3 1:
                spacing 18
                xalign 0.5

                for title, image_name in character["images"]:
                    button:
                        xsize 360
                        ysize 220
                        action ShowMenu("gallery_viewer", image_name, title)

                        add image_name:
                            xysize (360, 203)

                        text title:
                            xalign 0.5
                            yalign 1.0

                for i in range(3 - len(character["images"])):
                    null width 360 height 220

screen gallery_viewer(image_name, title):
    tag menu

    add image_name

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

            textbutton _("Back") action ShowMenu("character_gallery"):
                xalign 1.0

    key "game_menu" action ShowMenu("character_gallery")
