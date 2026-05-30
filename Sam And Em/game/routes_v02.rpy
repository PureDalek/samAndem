# Route expansion for v0.2.0.

define lady = Character("The Lady", color="#b989ff")
define max_rival = Character("Max", color="#ff7066")
define dean = Character("Dean Vale", color="#b8b8b8")

default integrity = 0
default lady_trust = 0
default lady_heat = 0
default max_rage = 0
default college_stability = 0
default route_lock = "open"

image cg b2_maxine_almost_date = "images/nsfw/cg/cg_b2_maxine_almost_date.png"
image cg c1_gala_private_balcony = "images/nsfw/cg/cg_c1_gala_private_balcony.png"
image cg c2m_maxine_last_lie = "images/nsfw/cg/cg_c2m_maxine_last_lie.png"
image cg c2l_lady_real_name = "images/nsfw/cg/cg_c2l_lady_real_name.png"
image cg c2j_lady_no_questions = "images/nsfw/cg/cg_c2j_lady_no_questions.png"
image cg e1_wedding_garden_private_vow = "images/nsfw/cg/cg_e1_wedding_garden_private_vow.png"
image cg e2_two_tickets_private_compartment = "images/nsfw/cg/cg_e2_two_tickets_private_compartment.png"

label route_act_one:

    scene bg dorm_lobby
    with fade

    "By the end of the first week, West Hall had already decided what I was."
    "To Maxine, I was the friend she still wanted to trust."
    "To Clara, I was a problem she hoped could become responsible."
    "To everyone else, I was a rumor with a room key."

    show maxine neutral at sprite_right
    show mc neutral at sprite_left
    with dissolve

    maxine "Scholarship office wants you at review night."

    mc "That sounds serious."

    maxine "It is serious. You get one weird dorm scandal, maybe. Two gets expensive."

    "A laugh came from the lobby doors."

    show maxine neutral at sprite_center
    with dissolve

    "Max leaned against the frame like he owned the building."

    max_rival "Still babysitting him, Maxine?"

    maxine "Still practicing being unpleasant, Max?"

    "His smile tightened."

    max_rival "Careful. People are starting to ask why the new guy keeps ending up where he does not belong."

    menu:
        "How do you answer Max's first public jab?"

        "Walk away and keep Maxine out of it.":
            $ integrity += 1
            $ college_stability += 1
            mc "Not doing this in the lobby."
            maxine "Good call."
            "Max looked disappointed, which felt like a small victory."

        "Let Maxine defend you.":
            $ maxine_trust += 1
            $ max_rage += 1
            mc "He is trying to get a reaction."
            maxine "Then he can enjoy not getting one."

        "Mock Max in front of everyone.":
            $ morality -= 1
            $ max_rage += 2
            mc "Does the tough-guy routine come with a student discount?"
            "The lobby laughed before Max could stop it."
            max_rival "Cute."
            "His thoughts hit colder than his voice."
            mind "I will make him regret that."

    jump route_lady_edge

label route_lady_edge:

    scene bg academy_dorm_exterior
    with fade

    "That night, I found the old gallery gate open."
    "A woman stood beneath the archway, reading the scholarship board like it was a confession."

    lady "Alex Reed. Room 214. New transfer. Unusually popular with emergencies."

    show mc neutral at sprite_left
    with dissolve

    mc "Do I know you?"

    lady "Not yet."

    "She smiled without giving me her name."
    "Her thoughts were quiet. Not empty. Guarded."

    lady "I know why the academy wants review night to go smoothly. I also know who benefits if it does not."

    menu:
        "The mysterious woman knows too much. What do you do?"

        "Ask what she wants before flirting with danger.":
            $ integrity += 1
            $ lady_trust += 1
            mc "If you know something useful, say it straight."
            lady "Good. Curiosity with a spine."

        "Flirt and avoid the hard question.":
            $ lady_trust += 1
            $ lady_heat += 1
            $ integrity -= 1
            mc "Do you always introduce yourself like a warning label?"
            lady "Only to people who might ignore one."

        "Tell Maxine about the meeting immediately.":
            $ maxine_trust += 1
            $ integrity += 1
            mc "I have to tell Maxine I saw you."
            lady "Honest before interesting. Rare."

    jump route_scholarship_review

label route_scholarship_review:

    scene bg dorm_lobby
    with fade

    "Dean Vale read from my file like every sentence had weight."

    dean "Rooming error. Shower incident. Conflict with another student."

    mc "The first two were accidents."

    dean "So far."

    "The review was not a punishment. That made it worse."
    "It was a warning from the future."

    menu:
        "How does Alex handle the scholarship review?"

        "Take the review seriously.":
            $ college_stability += 2
            $ integrity += 1
            mc "Tell me what I need to do to stay enrolled."
            dean "Start with attendance. Continue with fewer incidents."

        "Ask Maxine to help you prepare.":
            $ maxine_trust += 1
            $ college_stability += 1
            mc "Maxine knows the system better than I do. Can she help me build a plan?"
            dean "That is the first practical thing you have said today."

        "Skip the follow-up to meet the Lady.":
            $ lady_trust += 1
            $ college_stability -= 2
            $ lady_heat += 1
            "The email sat unanswered while I crossed campus toward the gallery gate."
            "It felt romantic until the second warning arrived."

    jump route_maxine_almost_date

label route_maxine_almost_date:

    scene cg b2_maxine_almost_date
    with fade

    "Maxine claimed a corner table in the library and surrounded it with books, snacks, and aggressive optimism."

    maxine "Tonight, we save your scholarship and prove you can read something other than minds."

    mc "You make tutoring sound threatening."

    maxine "It is."

    "My phone buzzed."
    "A message from an unknown number filled the screen."

    lady "If you want the truth about Max, come now."

    menu:
        "The Lady calls during Maxine's almost-date."

        "Stay with Maxine and silence the phone.":
            $ maxine_trust += 2
            $ lady_trust -= 1
            $ integrity += 1
            mc "It can wait."
            maxine "Good answer."
            "Her smile turned softer than the joke deserved."

        "Tell Maxine the truth and go check.":
            $ integrity += 1
            $ lady_trust += 1
            mc "The woman from the gate says she knows something about Max. I do not want to sneak out."
            maxine "I hate that I respect that."

        "Lie to Maxine and leave.":
            $ maxine_trust -= 2
            $ integrity -= 1
            $ lady_heat += 1
            mc "Forgot something in my room."
            mind "He is lying."
            "Maxine's smile stayed in place. Her thought did not."

    jump route_lady_favor

label route_lady_favor:

    scene bg academy_dorm_exterior
    with fade

    "The Lady waited by the service road with a key envelope pinched between two fingers."

    lady "Return this to the admin archive. No questions, no names."

    mc "That is a lot of no for one envelope."

    lady "Then ask the right question."

    menu:
        "The Lady asks for a small favor."

        "Help only after she explains.":
            $ lady_trust += 1
            $ integrity += 1
            $ lady_heat -= 1
            mc "I am not carrying mystery evidence."
            lady "It is not evidence. It is a warning. And you are learning."

        "Do it without asking.":
            $ lady_trust += 1
            $ lady_heat += 2
            $ integrity -= 1
            "I took the envelope before common sense could catch up."
            lady "Loyalty is beautiful. Dangerous, but beautiful."

        "Refuse kindly.":
            $ integrity += 1
            $ lady_trust -= 1
            mc "I like you better when you are not testing whether I will be stupid for you."
            lady "That might be the most disappointing compliment I have ever received."

    jump route_max_weak_point

label route_max_weak_point:

    scene bg dorm_lobby
    with fade

    "Max found me after dinner."
    "He had screenshots, rumors, and the smile of someone who thought fear was a leash."

    max_rival "Maxine know about the midnight gallery girl?"

    mc "You stalking me now?"

    max_rival "I am protecting her from bad decisions."

    menu:
        "Max threatens to twist the truth."

        "Confess to Maxine before Max can.":
            $ maxine_trust += 2
            $ integrity += 1
            $ max_rage += 1
            mc "Then I will tell her first."
            max_rival "You think honesty makes you untouchable?"

        "Beg Max to keep quiet.":
            $ max_rage += 1
            $ integrity -= 1
            mc "Just do not drag Maxine into this."
            max_rival "That sounded almost like leverage."

        "Humiliate Max publicly.":
            $ max_rage += 3
            $ college_stability -= 1
            $ integrity -= 1
            mc "You are not protecting anyone. You are just angry she stopped needing you."
            "The cafeteria went silent."
            mind "I will break him."

    jump route_gala_lock

label route_gala_lock:

    scene cg c1_gala_private_balcony
    with fade

    "Review night became a gala because the academy liked pretending money was the same as grace."
    "Maxine stood beside me under balcony lights."
    "The Lady watched from the doorway."
    "Max waited for the first mistake."

    menu:
        "This choice locks the final route."

        "Stand beside Maxine openly.":
            $ maxine_trust += 1
            $ integrity += 1
            $ route_lock = "maxine"
            mc "Maxine deserves the truth and my choice. I am not hiding either."

        "Step outside with the Lady and demand the truth.":
            $ lady_trust += 1
            $ route_lock = "lady"
            mc "If I leave with you, I need the truth. Not a prettier mystery."

        "Chase Max after his insult.":
            $ max_rage += 2
            $ college_stability -= 1
            $ route_lock = "max"
            "Max laughed once and walked away."
            "I followed before anyone could stop me."

        "Cover for the Lady's suspicious contact.":
            $ lady_heat += 2
            $ integrity -= 1
            $ route_lock = "jail"
            "A stranger slipped a sealed envelope into the Lady's bag."
            "When security looked over, I stepped into their sightline."

    if route_lock == "maxine":
        jump route_c2m_last_lie
    elif route_lock == "lady":
        jump route_c2l_real_name
    elif route_lock == "max":
        jump route_c2b_alone
    else:
        jump route_c2j_no_questions

label route_c2m_last_lie:

    scene cg c2m_maxine_last_lie
    with fade

    "The rain started after midnight."
    "Maxine sat beside me, robe tied tight, eyes tired of almost-truths."

    maxine "If there is one more thing, Alex, I need it from you. Not from Max. Not from rumors."

    menu:
        "Maxine asks for the last truth."

        "Confess everything before Max can.":
            $ integrity += 2
            $ maxine_trust += 2
            mc "I met the Lady. I lied once. I almost used my power because it was easy. I am telling you because I want to stop being that guy."
            maxine "That hurts."
            maxine "But it sounds like you."

        "Attack Max's reputation instead.":
            $ max_rage += 2
            $ integrity -= 1
            mc "Max is the problem. He is obsessed with making me look guilty."
            maxine "That was not an answer."

        "Leave Maxine in the dark.":
            $ maxine_trust -= 2
            $ integrity -= 2
            mc "There is nothing else."
            mind "Please believe me."
            "My own thought sounded like a lie."

    if maxine_trust >= 5 and integrity >= 3 and college_stability >= 1 and max_rage <= 5:
        jump ending_maxine_wedding
    elif max_rage >= 6 or college_stability <= -2:
        jump ending_max_dropout
    else:
        jump ending_neutral_transfer

label route_c2l_real_name:

    scene cg c2l_lady_real_name
    with fade

    "The Lady's hotel room was warmer than the night outside."
    "Two tickets waited on the table."

    lady "My name is Elise."

    mc "That true?"

    lady "True enough to be dangerous."

    menu:
        "Elise offers a life beyond the academy."

        "Choose her, but set boundaries.":
            $ lady_trust += 2
            $ integrity += 2
            $ lady_heat -= 1
            mc "I will go with you. I will not carry secrets I do not understand."
            lady "Then you are choosing me, not the fantasy."

        "Promise to do anything.":
            $ lady_trust += 1
            $ lady_heat += 2
            $ integrity -= 2
            mc "Whatever you need. No questions."
            lady "Do not offer that lightly."

        "Ask for time to end things cleanly with Maxine.":
            $ integrity += 1
            $ maxine_trust += 1
            mc "If I leave, I do it without humiliating someone who trusted me."
            lady "Painfully decent. I can work with that."

    if lady_trust >= 4 and integrity >= 2 and lady_heat <= 3:
        jump ending_lady_train
    elif lady_heat >= 4 and integrity <= 0:
        jump route_c2j_no_questions
    else:
        jump ending_neutral_summer

label route_c2b_alone:

    scene bg academy_dorm_exterior
    with fade

    "Max texted a parking-structure location and one sentence."
    "Come alone."

    menu:
        "Max's trap is obvious. What does Alex do?"

        "Meet Max alone.":
            $ max_rage += 2
            $ college_stability -= 2
            $ integrity -= 1
            jump ending_max_dropout

        "Send the messages to campus security.":
            $ college_stability += 2
            $ integrity += 1
            $ max_rage -= 1
            jump ending_neutral_transfer

        "Call Maxine.":
            $ maxine_trust += 1
            $ integrity += 1
            if maxine_trust >= 4:
                jump route_c2m_last_lie
            else:
                jump ending_neutral_summer

label route_c2j_no_questions:

    scene cg c2j_lady_no_questions
    with fade

    "The envelope lay on the bed like it had weight beyond paper."
    "Police lights colored the curtains."

    lady "Carry it across town. Do not open it. Do not ask who it belongs to."

    menu:
        "The envelope decides the Lady route."

        "Carry it and ask no questions.":
            $ lady_heat += 2
            $ integrity -= 2
            jump ending_lady_locked_door

        "Open it and confront her.":
            $ integrity += 2
            $ lady_heat -= 1
            $ lady_trust += 1
            if lady_trust >= 3:
                jump ending_lady_train
            else:
                jump ending_neutral_transfer

        "Leave it and walk away.":
            $ integrity += 1
            $ lady_trust -= 1
            jump ending_neutral_summer

label ending_maxine_wedding:

    scene cg e1_wedding_garden_private_vow
    with fade

    "Graduation came with sunlight, speeches, and Maxine pretending not to cry."
    "The wedding was small. Clara organized the chairs. Dean Vale gave a speech that sounded suspiciously like a final warning."

    maxine "Still nervous?"

    mc "Only because you look like you are about to tease me forever."

    maxine "That was in the vows."

    "I had thought love would be the end of adventure."
    "With Maxine smiling at me in the garden, I understood it was the place I could return to."

    "Ending 1: The Wedding Garden."
    return

label ending_lady_train:

    scene cg e2_two_tickets_private_compartment
    with fade

    "The train left after midnight."
    "Elise slid one ticket across the table and kept the other under her hand."

    lady "Where first?"

    mc "Somewhere we have to learn as we go."

    "She laughed, and for once there was no locked door behind it."

    "Ending 2: Two Tickets Anywhere."
    return

label ending_max_dropout:

    scene bg academy_dorm_exterior
    with fade

    "The fight lasted less than a minute."
    "The consequences lasted longer."
    "By morning, the scholarship office had statements, photos, and one more reason not to believe I belonged there."

    "I left campus with a half-packed bag, a bruised face, and an unread message from Maxine."
    "I told myself college had never been my place."
    "Even in my own head, it sounded false."

    "Ending 3: The Dropout."
    return

label ending_lady_locked_door:

    scene bg dorm_lobby
    with fade

    "The envelope was not heavy until the officer asked me to open my bag."
    "Elise was gone by then."
    "On the holding room television, a travel ad played without sound."

    mc "I thought I was choosing freedom."

    "The locked door answered better than anyone else could."

    "Ending 4: The Locked Door."
    return

label ending_neutral_transfer:

    scene bg academy_dorm_exterior
    with fade

    "I survived the semester, but survival was not the same as belonging."
    "The transfer papers felt lighter than shame and heavier than hope."

    "Neutral Ending: Transfer Papers."
    return

label ending_neutral_summer:

    scene bg dorm_room_214
    with fade

    "Summer arrived quietly."
    "Maxine stopped waiting for apologies I had not earned."
    "The Lady stopped sending messages."
    "For the first time all year, my head was quiet."

    "Neutral Ending: Summer Alone."
    return
