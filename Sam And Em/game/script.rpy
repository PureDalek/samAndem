# Sam And Em - v0.0.1 prototype story.

define mc = Character("[player_name]", color="#5d8cff")
define dorm = Character("Clara", color="#d78355")
define maxine = Character("Maxine", color="#66c46a")
define mind = Character(None, what_italic=True, what_color="#8f6cff")

default player_name = "Alex"
default morality = 0
default mind_power_control = 0
default clara_trust = 0
default maxine_trust = 0

image bg academy_dorm_exterior = "images/backgrounds/academy_dorm_exterior.png"
image bg dorm_lobby = "images/backgrounds/dorm_lobby.png"

image mc neutral = "images/characters/protagonist.png"
image clara neutral = "images/characters/dorm_leader.png"
image maxine neutral = "images/characters/maxine.png"

transform sprite_left:
    xalign 0.18
    yalign 1.0
    zoom 0.62

transform sprite_center:
    xalign 0.5
    yalign 1.0
    zoom 0.62

transform sprite_right:
    xalign 0.82
    yalign 1.0
    zoom 0.62

label start:

    scene bg academy_dorm_exterior
    with fade

    "The academy looked smaller in the brochure."
    "In person, it had weight. Brick walls. Old windows. A dorm entrance that seemed to know every secret before anyone confessed it."

    show mc neutral at sprite_left
    with dissolve

    mc "New room. New rules. New chance to not mess everything up."

    "My phone buzzed before I reached the front steps."

    maxine "Turn around, genius."

    show maxine neutral at sprite_right
    with dissolve

    maxine "You were about to walk past me with that tragic lost-puppy face."

    mc "I was going for mysterious transfer student."

    maxine "You landed on guy who packed socks in a panic."

    "Maxine grinned like she had been saving that one for the whole trip."
    "She was my best friend, which meant she knew exactly where to hit and exactly when to pretend she had not."

    mc "You really transferred too?"

    maxine "Somebody has to make sure you survive orientation."

    jump scene_dorm_lobby

label scene_dorm_lobby:

    scene bg dorm_lobby
    with fade

    "The dorm lobby smelled like polished wood, coffee, and too many people pretending they were not anxious."

    show clara neutral at sprite_center
    with dissolve

    dorm "You must be Alex."

    "The woman at the desk looked up from a clipboard. Calm eyes. Perfect posture. A smile that could welcome you or warn you depending on how smart you were."

    dorm "I'm Clara. Last year student, dorm leader, emergency contact for disasters involving keys, curfews, and bad decisions."

    show maxine neutral at sprite_right
    with dissolve

    maxine "Please tell me you have the room list. He has been pretending not to panic since the gate."

    dorm "Of course."

    "Clara ran one finger down the clipboard, stopped, and frowned."

    dorm "Maxine Hart. Room 214."

    maxine "That's me."

    dorm "Alex Reed. Room 214."

    mc "Wait. Same room?"

    dorm "That cannot be right."

    "She checked the page again. Then the next page. Then the page after that."

    dorm "I am sorry. The system marked Alex as a girl's name."

    maxine "It can be."

    mc "It is also very much not, in my case."

    dorm "West Hall is currently full. I can move you tomorrow, maybe the day after, but tonight..."

    "She stopped speaking."
    "A pressure bloomed behind my eyes. Not pain. Not exactly."

    mind "This is my mistake. If I separate them, I need an incident report. If I let him stay, people will talk. But Maxine knows him. They are adults. One night is not the end of the world."

    "The words were not in the room."
    "They were in Clara."

    mc "Clara?"

    dorm "Yes?"

    "Her lips had not moved."

    mind "He looks like he heard me. Impossible."

    "The pressure sharpened. For one impossible second, I could feel the shape of her hesitation, like a door with my hand already on the handle."

    menu:
        "Clara is debating whether to let Alex stay in Maxine's room tonight. What do you do?"

        "Respect the boundary and answer honestly.":
            $ morality += 1
            $ clara_trust += 1
            mc "If it makes things easier, I can sleep in the lobby or call a hotel."
            maxine "Alex, you do not have hotel money."
            dorm "No. This is my mistake, not yours."
            "Clara exhaled, making the decision herself."
            dorm "One night. Door stays unlocked unless both of you agree otherwise. I move you tomorrow."

        "Nudge her thought toward letting you stay.":
            $ morality -= 1
            $ mind_power_control += 1
            "I did not know how I did it."
            "I just leaned into the thought: Maxine knows him. They are adults. It is fine."
            mind "They are adults. It is fine. I have bigger problems than one harmless room error."
            dorm "Actually..."
            "Clara blinked, then squared her shoulders as if the decision had always been obvious."
            dorm "You can stay there for now. If either of you complains, I change the arrangement immediately."

    dorm "Welcome to West Hall, Alex."

    maxine "See? First day and you already survived the boss fight."

    "I took the key."
    "The metal felt ordinary in my palm."
    "The power in my head did not."

    jump scene_morning_room

label scene_morning_room:

    scene bg dorm_lobby
    with fade

    "The first night in Room 214 was awkward in the way only old friendship could survive."
    "Maxine claimed the bed by the window. I took the spare mattress. The ancient fan rattled like it had personal problems."
    "By morning, the room was too warm, the sheets were twisted, and sunlight leaked through the blinds."

    maxine "Mmm... stupid heat..."

    "I opened my eyes and froze."
    "Maxine was half-asleep on top of her sheets, topless from the heat, one arm thrown over her face."
    "For a second, my brain forgot every language it had ever learned."

    menu:
        "How do you handle the moment?"

        "Look away and wake her gently.":
            $ morality += 1
            $ maxine_trust += 1
            mc "Max. Hey. You might want to grab a shirt."
            maxine "Huh?"
            "I turned toward the wall before she fully woke up."
            maxine "Oh. Wow. Great. First morning and I am already losing at roommate etiquette."
            mc "For the record, I am staring very respectfully at this wall."
            maxine "Good. The wall deserves attention."

        "Let yourself look for a moment before speaking.":
            $ morality -= 1
            "I knew I should look away."
            "I also knew I waited too long."
            maxine "Alex?"
            "Her voice snapped me back into myself."
            mc "Sorry. I just woke up."
            maxine "Then wake up facing literally anywhere else."
            "She grabbed a shirt from the floor, cheeks flushed more with irritation than embarrassment."

    maxine "This room is an oven."

    mc "I will ask Clara about the fan."

    maxine "Ask Clara about separate rooms too, unless you plan on developing heroic wall-staring powers."

    "I almost laughed."
    "Then the pressure behind my eyes returned, soft and waiting."

    mind "Please don't make this weird. Please still be my friend."

    "Maxine smiled like nothing had changed."
    "Her thoughts were not as good at pretending."

    "End of v0.0.3 prototype."

    return
