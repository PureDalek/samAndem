default persistent.age_verified = False

label splashscreen:

    if persistent.age_verified:
        return

    scene black

    centered "{size=54}{b}Adults Only{/b}{/size}\n\nThis game contains mature themes, nudity, sexual content, and adult situations.\n\nAll sexual characters are fictional adults age 18 or older.\n\nYou must be 18 or older to play."

    menu:
        "Are you 18 or older?"

        "Yes, I am 18 or older.":
            $ persistent.age_verified = True
            $ renpy.save_persistent()
            return

        "No, exit the game.":
            $ renpy.quit()
