## Maxine route expansion - v0.4.0
## Five explicit scenes inserted into the existing Maxine / Clara storyline.
## All characters are adults aged 18 or older.

default mx_shower_done = False
default mx_library_done = False

image cg mx_shower_nude = "images/nsfw/cg/cg_mx_shower_nude.png"
image cg mx_shower_wall = "images/nsfw/cg/cg_mx_shower_wall.png"
image cg mx_shower_facial = "images/nsfw/cg/cg_mx_shower_facial.png"
image cg mx_night_top = "images/nsfw/cg/cg_mx_night_top.png"
image cg mx_titfuck = "images/nsfw/cg/cg_mx_titfuck.png"
image cg mx_oops = "images/nsfw/cg/cg_mx_oops.png"
image cg mx_library = "images/nsfw/cg/cg_mx_library.png"
image cg mx_library_after = "images/nsfw/cg/cg_mx_library_after.png"
image cg mx_last_lie_nude = "images/nsfw/cg/cg_mx_last_lie_nude.png"
image cg mx_last_lie_sex = "images/nsfw/cg/cg_mx_last_lie_sex.png"
image cg mx_cum_covered = "images/nsfw/cg/cg_mx_cum_covered.png"
image cg mx_wedding_night = "images/nsfw/cg/cg_mx_wedding_night.png"
image cg mx_wedding_titfuck = "images/nsfw/cg/cg_mx_wedding_titfuck.png"
image cg mx_wedding_facial = "images/nsfw/cg/cg_mx_wedding_facial.png"
image cg mx_wedding_morning = "images/nsfw/cg/cg_mx_wedding_morning.png"


## 1. The shower she traded for
label maxine_shower_scene:

    scene bg communal_showers
    with fade

    "Clara's schedule said 2:10. The corridor said nothing at all, which was the point of 2:10."
    "I had the towel over my shoulder and one hand on the door when I heard the water running in the second stall."
    "Maxine's shower bag was on the bench. Her hand wraps were hanging off it like a shed skin."

    maxine "You are late."
    mc "This is my slot."
    maxine "I traded. Clara thinks I am having a crisis."
    mc "Are you?"
    maxine "I am having a shower. With you. It is a small crisis."

    "The curtain pulled back."

    scene cg mx_shower_nude
    with dissolve

    "Steam, and water, and Maxine Hart entirely naked, one hand braced on the tile, not pretending to be shy about it."
    "I had seen her topless in a bed with the morning in my eyes. This was different. This was her standing up, choosing it, watching me count."
    "She had a red mark on her shoulder from the tennis bag. Water ran down her stomach and disappeared where the conversation was going."

    maxine "Well?"
    mc "You are going to get the floor wet."
    maxine "Reed. Get in."

    "I got in."

    scene cg mx_shower_wall
    with dissolve

    "The wall was cold. She was not. She put her leg up over my hip and her mouth against my ear and told me, in exact words, where to put my hands."
    "The water hammered the tiles. Every sound we made came back at us twice, so we learned to be quiet the way people learn a language - badly, and then all at once."

    maxine "If you drop me, I am telling everyone it was the tiles."
    mc "If I drop you, the tiles will have a story too."

    "She laughed into my shoulder, and then stopped laughing, and then her hand was flat on the tile above my head and she was making a sound that had nothing to do with laughing."
    "It was fast and slippery and ridiculous and her hair was in my mouth. It was the best two minutes of my first week."

    menu:
        "She is close. Where do you finish?"

        "Across her chest and stomach.":
            "I pulled out and she took it on her skin, head back under the water, grinning at the ceiling."
            maxine "There. Now I have to shower anyway."

        "Paint her face.":
            jump maxine_shower_facial

    "She soaped her hands and washed me off with the same efficiency she used on the dorm's broken things."
    "Her fingers were careful. Her mouth was not."

    maxine "You know what the worst part of this is?"
    mc "The water pressure?"
    maxine "I am going to be nice to Clara for a week."

    $ mx_shower_done = True
    return


label maxine_shower_facial:

    scene cg mx_shower_facial
    with dissolve

    "I pulled out and she turned her face up into it, eyes closed, water running over her cheekbones, and got a stripe across her cheek and her chin and one eyelid."
    "She opened her eyes carefully. The left one was stuck."

    maxine "You have got to be kidding me."
    mc "You turned."
    maxine "I turned? I was standing here being a masterpiece and you aimed."
    mc "I did not aim. That is the problem."

    "She wiped her eye with the back of her wrist, looked at the water running it off her chin, and started laughing so hard she had to put her forehead on my shoulder."

    maxine "I am going to think about this in the library."
    mc "You are going to think about this in the library?"
    maxine "Every time someone says the word 'custodial'. I do not make the rules."

    $ mx_shower_done = True
    return


## 2. Room 214, the fan is broken
label maxine_night_scene:

    scene bg dorm_room_214
    with fade

    if mx_shower_done:
        "By midnight the room had given up on the fan entirely. Maxine had given up on most of her clothes."
    else:
        "By midnight the room had given up on the fan entirely. Maxine had given up on most of her clothes, and on the idea that I was going to be sensible about it."

    "She was on top of the sheets in a tank top and a pair of shorts that had been a pair of shorts earlier in the evening."
    "The window was open. The city was doing its usual impression of a warm room."

    maxine "You are breathing on me."
    mc "I am breathing on the ceiling."
    maxine "You are breathing on the ceiling in my direction."
    mc "I can sleep in the corridor."
    maxine "You can sleep in the corridor the night I stop wanting you in the bed, Reed. So, not tonight."

    "She sat up, looked at me for a moment over the collar of her tank top, and decided something."

    scene cg mx_night_top
    with dissolve

    "The tank top went over her head. The shorts followed it. She sat back on her heels, entirely naked in the blue window light, with the look of someone who had just taken something out of a box and could not believe she had waited."

    maxine "There. Now you can stare."
    mc "I was staring before."
    maxine "Before, you were staring at the carpet and hoping. This is better."

    "This is better."

    scene cg mx_titfuck
    with dissolve

    "She pushed me down against the headboard, straddled my thighs, and gathered her breasts in both hands."
    "She did it the way she did everything - with competence, and a joke already behind her teeth."

    maxine "Look, I am a tomboy. I am not a nun. There are things I know how to do that do not involve a tennis racket."
    mc "You are going to have to prove that."
    maxine "I am going to have to demonstrate. Prove is for exams."

    "She spat in her palm, slicked me with it, and slid her knees further apart."
    "Then she pushed her breasts together around me and started to move."

    "It was slow, then not. She had to lean in on her elbows to keep the angle, which put her face close to mine, which meant that every time she breathed out I could feel it."
    "The old bed made a noise like a metronome. Somewhere downstairs somebody was watching something too loudly."

    maxine "Okay. I am going to say something and you are not allowed to make it weird."
    mc "You have made everything you have said tonight weird."
    maxine "You are the best thing that has happened to this room. Including the fan."

    "I did not manage an answer. She took that as an answer."

    "Then her hands lost their grip, and the angle went, and she leaned down to fix it - fast, laughing, careless -"

    scene cg mx_oops
    with dissolve

    " - and I came across her chin, her cheek, and the bridge of her nose."

    "Maxine froze."
    "The clock on the desk ticked."
    "Then she put one finger up, caught a stripe at the corner of her mouth, and looked at it like a jeweller."

    maxine "Well. That is more than you owe me."
    mc "I am so sorry."
    maxine "You are not sorry. You are thanking God I was not three inches further down."
    mc "I am doing both."

    "She laughed. She did not wipe it off. She sat back on her heels, naked, marked, and told me to get the packet of tissues from the desk drawer."

    maxine "Spatial awareness of a cat, this one. The cat would have landed, though."
    mc "Next time I will aim."
    maxine "Next time you will ask. That is better."

    "She wiped her face with one tissue. She used three more on her chest and then complained the packet was expensive."
    "Afterward she lay down on her back with her arms above her head, no sheet, no shirt, no shame, and watched the ceiling fan that was not moving."

    maxine "If you tell anyone the best night of my week was in this furnace, I will say you dreamed it."
    mc "And if I say I did not?"
    maxine "Then I will say you should dream more. Now sleep. You are on the side with no sheet."

    return


## 3. The library, after closing
label maxine_library_scene:

    scene cg mx_library
    with dissolve

    "The library closed at ten. We were in the stacks at ten past, which is the sort of arithmetic that has consequences."
    "Maxine had a hand flat on a shelf of old history and the other on my shoulder, and her hips were doing a patient, mocking kind of arithmetic against the exact place I was trying not to say anything about."

    maxine "If you can hear the cart, you have time to stop."
    mc "I can hear the cart."
    maxine "Then stop talking."

    "She had gone up the ladder for a book and come down without her skirt. She had one leg around mine and the jeans I had been wearing were somewhere behind us, doing nothing."
    "When my hand found her, she breathed out my name in a voice she never used for anybody else, and the cart went away down the next aisle."

    "After that it was very quiet and very fast. Her forehead against the lower shelf. My hand over her mouth - she bit it, lightly, to tell me she had it. The old shelf creaked once, an accusation, and we did not answer it."

    maxine "Left. Slightly left. There- okay. Okay. Do not stop, do not narrate, do not say anything cute."
    mc "Wouldn't dream of it."
    maxine "That was cute. It was cute. I am going to-"

    scene cg mx_library_after
    with dissolve

    "I pulled out at the last possible moment, and the last possible moment was a suggestion, not a fact."
    "She looked down at the white stripe across her thigh, at the hem of her skirt, at the library due-date slip I had the presence of mind to press to it."

    maxine "Reed."
    mc "It was clean."
    maxine "It was a due-date slip. For a book on the Enlightenment."
    mc "It was clean Enlightenment."

    "She laughed so loudly that the cart two aisles away stopped, considered, and moved on."
    "She put the slip in my coat pocket, folded the corner down, and kissed my jaw where the shelf had left a mark."

    maxine "You can return that in the morning."
    mc "To whom?"
    maxine "To me. I have been the librarian of this for a month. You are just finding out."

    $ mx_library_done = True
    return


## 4. The last lie
label maxine_last_lie_scene:

    scene cg mx_last_lie_nude
    with dissolve

    "The rain had been going for an hour. Maxine was still on the edge of the bed, and the robe was no longer anything anyone could call tied."
    "It had opened down the middle and she had not fixed it. She had let me look, which is not the same as not caring."
    "Her shoulders were wet from the window. The rest of her was warm to the touch, and mine, at least in the room we were in."

    maxine "You cannot fix this with a hand on my knee."
    mc "I know."
    maxine "You can try."

    "So I tried."

    scene cg mx_last_lie_sex
    with dissolve

    "We started slow, because she was still talking and I was still listening, and then she stopped talking and I stopped listening and her legs came up around my back."
    "The rain got louder. The bed got louder. She put the flat of her hand against my mouth once, not to be quiet, only because it was there and because she liked the shape of it."

    "For a while there was no route, no lady, no scholarship, no future. There was Maxine Hart, wet-faced and laughing and saying my name in two syllables like she had just learned what it was for."
    "Then there was just her breath and the rain and her hand on the back of my neck."

    scene cg mx_cum_covered
    with dissolve

    "She asked me to finish on her and I did."
    "Not neatly. There was a lot of it - some across her stomach, some on her chest, a careless line up to her collarbone and a streak on her breast where her own hand had gone after it."
    "She did not close her robe. She lay there in the blue rain-light, marked, and looked at me like the argument had finally gone her way."

    maxine "There. Now you have to talk to me."
    mc "I was going to talk to you anyway."
    maxine "No, you were going to be brave and noble. This is better. Brave and noble has no fingerprints."

    "She put a finger on her own stomach and drew a line through it."

    maxine "If you tell anyone what I look like right now, I will deny it."
    mc "And if I don't?"
    maxine "Then you will have to remember."

    "She wiped her hand on the sheet, pulled the robe over one shoulder and not the other, and made room."

    maxine "Come here. The talking is later. The rain is not going to stay forever."

    "The rain stayed for another hour. So did she."

    return


## 5. Wedding night
label maxine_wedding_night:

    scene cg mx_wedding_night
    with fade

    "The hotel room was on the top floor and the bridal suite was the only room on it that had not been told to keep the rates down."
    "Maxine got out of her shoes in the doorway, got out of the veil in the corridor, and got out of the top half of the dress before I had finished shutting the door."

    maxine "This dress has forty buttons. Clara sewed them. She said, and I quote, 'Make him work for it.'"
    mc "How am I doing?"
    maxine "You are doing it with your mouth. That was not the plan, but it is working."

    "The dress was around her waist. She was not wearing anything under it because she had made a decision at eleven in the morning and stuck to it like a promise."
    "She put one knee on the bed, looked at the white satin falling off her, and laughed."

    maxine "Do you know how many times I have seen the Wedding Garden ending?"
    mc "In the route tree?"
    maxine "In my head. I did not think it would be a real hotel room with a real ceiling fan and you."

    scene cg mx_wedding_titfuck
    with dissolve

    "She pulled me up onto the bed and got the dress over my shoulders, and then she was over me, still in the veil, and the veil pooled on my chest."
    "The dress stayed around her middle like a white line. She pushed her breasts together and I watched the ring on her finger catch the lamp while she moved."

    maxine "Admire it. It cost you my entire savings, one tennis bag, and a night of pretending to like your friends."
    mc "You like my friends."
    maxine "I like you. The friends are a recurring fee."

    "She caught my mouth before I could answer. The satin was still cold from the window and she was not."

    scene cg mx_wedding_night
    with dissolve

    "We rolled over. She ended up on her back with one leg still caught in the dress, the veil across the floor and the ring on her hand and nothing else between us."
    "She said my name once, quietly, like she was checking it against the paperwork."
    "Then she said it louder, and the hotel did not care, and neither did we."

    "Afterward she did not move. There was a stripe of me across her stomach and a stripe of the veil across her hair, and she was too married to be embarrassed about either."

    maxine "So. Mrs. Reed."
    mc "You did not take my name."
    maxine "I took your everything else. I can call myself Mrs. Reed in this room."

    scene cg mx_wedding_facial
    with dissolve

    "The second time was slower, and then it was not slow at all, and then she pushed me up and said - with the towel in her hand and the ring in the towel - that she had not planned on going to breakfast with a face."
    "She looked at me under her eyelashes and said, 'Well? You promised me a wedding present.'"
    "So she got one."

    scene cg mx_wedding_morning
    with fade

    "In the morning there was sun on the curtains, coffee going cold on the desk, and Maxine Hart asleep with half her face on my arm and half the wedding on the floor."
    "She had dried streaks on her stomach. She had the veil over one shoulder like a blanket. She had my shirt on and nothing else."

    "She opened one eye."

    maxine "You are taking a picture."
    mc "I don't own a camera."
    maxine "You are taking a picture with your face."
    mc "I would like a copy."

    "She snorted, kissed my shoulder, and went back to sleep."
    "The fan was working. The room was cool. West Hall had, at last, delivered."

    return
