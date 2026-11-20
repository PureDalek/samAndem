# -*- coding: utf-8 -*-
from story_v03a import ROUTES as RA
from story_v03b import ROUTES as RB
ROUTES = {**RA, **RB}
ORDER = [ROUTES[k] for k in ("morrigan","brielle","mina","kira","sienna","nadia","helena","rhea")]
HUB_INTRO = [
 "West Hall keeps opening new doors. Some are friendships. Some are evidence. Some are traps with better lighting.",
 "The dorm has a way of introducing you to people one crisis at a time. These are the ones who were still standing after.",
]