## Extracted from the v0.2 decompiled expanded_routes.rpy - the ten-situation gauntlet.

label expanded_binary_situations:

    $ expanded_binary_good = 0
    $ expanded_binary_risky = 0

    scene bg dorm_lobby
    with fade

    "The academy throws ten clean binary tests at Sam. None of them stay clean once people are involved."

    "Binary situation 1 of 10: Rumor Screenshot."

    menu:
        "Rumor Screenshot"
        "Delete the screenshot and ask the person directly.":

            $ expanded_binary_good += 1
            $ integrity += 1
            mc "I can live with the slower answer."
        "Forward it to gain leverage.":

            $ expanded_binary_risky += 1
            $ morality -= 1
            mc "Fast answers leave marks. I know."

    "Binary situation 2 of 10: Locked Archive."

    menu:
        "Locked Archive"
        "Find an authorized witness before opening it.":

            $ expanded_binary_good += 1
            $ integrity += 1
            mc "I can live with the slower answer."
        "Pick the lock before security returns.":

            $ expanded_binary_risky += 1
            $ morality -= 1
            mc "Fast answers leave marks. I know."

    "Binary situation 3 of 10: Clinic File."

    menu:
        "Clinic File"
        "Protect patient privacy.":

            $ expanded_binary_good += 1
            $ integrity += 1
            mc "I can live with the slower answer."
        "Search the file for useful dirt.":

            $ expanded_binary_risky += 1
            $ morality -= 1
            mc "Fast answers leave marks. I know."

    "Binary situation 4 of 10: Pool Test."

    menu:
        "Pool Test"
        "Demand a retest in public.":

            $ expanded_binary_good += 1
            $ integrity += 1
            mc "I can live with the slower answer."
        "Quietly swap the sample labels.":

            $ expanded_binary_risky += 1
            $ morality -= 1
            mc "Fast answers leave marks. I know."

    "Binary situation 5 of 10: Gala Lie."

    menu:
        "Gala Lie"
        "Tell Maxine why the Lady is there.":

            $ expanded_binary_good += 1
            $ integrity += 1
            mc "I can live with the slower answer."
        "Pretend the Lady is just a donor guest.":

            $ expanded_binary_risky += 1
            $ morality -= 1
            mc "Fast answers leave marks. I know."

    "Binary situation 6 of 10: Mural Night."

    menu:
        "Mural Night"
        "Paint only the approved wall.":

            $ expanded_binary_good += 1
            $ integrity += 1
            mc "I can live with the slower answer."
        "Use the forbidden wall for maximum impact.":

            $ expanded_binary_risky += 1
            $ morality -= 1
            mc "Fast answers leave marks. I know."

    "Binary situation 7 of 10: Cosplay Mask."

    menu:
        "Cosplay Mask"
        "Protect Kira's real name.":

            $ expanded_binary_good += 1
            $ integrity += 1
            mc "I can live with the slower answer."
        "Reveal it to stop a rumor faster.":

            $ expanded_binary_risky += 1
            $ morality -= 1
            mc "Fast answers leave marks. I know."

    "Binary situation 8 of 10: Bully Apology."

    menu:
        "Bully Apology"
        "Let Brielle apologize without an audience.":

            $ expanded_binary_good += 1
            $ integrity += 1
            mc "I can live with the slower answer."
        "Make her apologize in public.":

            $ expanded_binary_risky += 1
            $ morality -= 1
            mc "Fast answers leave marks. I know."

    "Binary situation 9 of 10: Headmaster Bargain."

    menu:
        "Headmaster Bargain"
        "Refuse protection that costs someone else.":

            $ expanded_binary_good += 1
            $ integrity += 1
            mc "I can live with the slower answer."
        "Accept the deal and stay enrolled.":

            $ expanded_binary_risky += 1
            $ morality -= 1
            mc "Fast answers leave marks. I know."

    "Binary situation 10 of 10: Reporter Deadline."

    menu:
        "Reporter Deadline"
        "Delay the story until consent is clear.":

            $ expanded_binary_good += 1
            $ integrity += 1
            mc "I can live with the slower answer."
        "Publish now before the evidence disappears.":

            $ expanded_binary_risky += 1
            $ morality -= 1
            mc "Fast answers leave marks. I know."

    if expanded_binary_good >= expanded_binary_risky:
        "Sam comes out of the gauntlet with more trust than leverage."
    else:
        "Sam comes out with leverage, and the uncomfortable knowledge that leverage always asks to be used again."

    jump expanded_route_return
