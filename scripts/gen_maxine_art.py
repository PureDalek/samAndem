# -*- coding: utf-8 -*-
"""Render the Maxine route expansion CGs (v0.4.0) from the local Forge API."""
import base64
import json
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageStat

HOST = "http://127.0.0.1:7861"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Sam And Em" / "game" / "images" / "nsfw" / "cg"
ART = ROOT / "art" / "generated" / "maxine_expansion"
OUT.mkdir(parents=True, exist_ok=True)
ART.mkdir(parents=True, exist_ok=True)

STYLE = ("polished semi-realistic anime visual novel art, high-end game illustration, soft painterly cel shading, "
         "clean crisp lineart, detailed expressive eyes, natural skin texture, cinematic lighting, 2.5D, adult characters")
MAXINE = ("Maxine Hart, adult woman 21 years old, busty athletic tomboy, short spiky black hair with vivid blue streaks, "
          "bright blue eyes, strong toned shoulders and arms, tanned skin, white boxing hand wraps on her wrists, "
          "confident teasing grin")
SAM = ("Sam Reed, adult man 18 years old, short messy black hair, soft brown eyes, pale skin with light freckles, "
       "slim average build, gentle expression")

NEG = ("worst quality, low quality, normal quality, lowres, blurry, jpeg artifacts, sketch, unfinished, bad anatomy, "
       "bad hands, extra fingers, missing fingers, fused fingers, deformed hands, distorted face, crossed eyes, "
       "asymmetrical eyes, bad proportions, mutated limbs, extra arms, extra legs, long neck, cropped head, cropped feet, "
       "out of frame, multiple views, character sheet, reference sheet, collage, split screen, inset portrait, "
       "thumbnails, border, frame, text, watermark, signature, logo, child, teen, underage, loli, shota, schoolgirl, "
       "childlike face, plastic skin, doll, 3d render, duplicate, two heads, two faces, censored, mosaic, "
       "extra person, third person, crowd")
NEG_CLOTH = NEG + (", clothing, bra, panties, shirt, dress, underwear, swimsuit, towel, sheet covering chest, "
                   "fabric over breasts, barbie doll anatomy")

SCENES = [
    ("cg_mx_shower_nude",
     f"{STYLE}. {MAXINE} completely nude in a steam-filled tiled communal shower, water running over her shoulders and "
     f"breasts, one hand braced on the wet tile, looking back at the viewer over her shoulder, large bare breasts with "
     f"visible nipples, toned stomach, bare hips and thighs, wet hair, explicit adult female nudity, confident and unashamed",
     NEG_CLOTH),
    ("cg_mx_shower_wall",
     f"{STYLE}. {MAXINE} and {SAM} having sex against the tiled wall of a steam-filled communal shower, she is completely "
     f"nude with one leg lifted around his hip, her back to the tiles, his hands under her thighs, explicit penetration, "
     f"bare breasts pressed to his chest, water streaming over both of them, wet hair, breathless laugh, explicit adult scene",
     NEG),
    ("cg_mx_shower_facial",
     f"{STYLE}. {MAXINE} kneeling under the running shower, completely nude, face turned up, laughing, semen across her "
     f"cheek, chin and one closed eyelid, {SAM} standing over her with his hand in her wet hair, water streaming, "
     f"bare breasts, explicit adult scene, affectionate and ridiculous",
     NEG_CLOTH),
    ("cg_mx_night_top",
     f"{STYLE}. {MAXINE} kneeling on a rumpled dorm bed at night, completely nude, arms above her head, bare breasts with "
     f"visible nipples, toned stomach, bare hips and thighs, blue window light on her skin, old fan in the background, "
     f"looking directly at the viewer with a daring grin, explicit adult female nudity",
     NEG_CLOTH),
    ("cg_mx_titfuck",
     f"{STYLE}. {MAXINE} straddling {SAM} on a dorm bed, topless, pushing her large bare breasts together around his erect "
     f"penis, titfuck, eye contact, her hands and his on her breasts, his cock glistening between them, his hands on her "
     f"hips, warm lamp light, explicit adult sexual scene",
     NEG),
    ("cg_mx_oops",
     f"{STYLE}. {MAXINE} kneeling on a dorm bed, completely nude, caught by surprise and laughing, semen across her chin, "
     f"cheek and the bridge of her nose, one eye half-closed, her finger raised to her face, {SAM} frozen beneath her, "
     f"warm lamp light, explicit adult scene, funny and intimate",
     NEG_CLOTH),
    ("cg_mx_library",
     f"{STYLE}. {MAXINE} and {SAM} having sex standing between tall old library shelves, she is pressed back against the "
     f"books, skirt shoved up, one leg around his hip, her hand over her own mouth, his hand at her waist, jeans open, "
     f"low warm shelf light, dust in the air, explicit adult scene, quiet and urgent",
     NEG),
    ("cg_mx_library_after",
     f"{STYLE}. {MAXINE} standing in a library aisle afterwards, skirt still hiked, looking down at a white stripe of cum "
     f"across her thigh, holding a folded library due-date slip, amused and flushed, {SAM} half out of frame, warm shelf "
     f"light, explicit adult scene",
     NEG),
    ("cg_mx_last_lie_nude",
     f"{STYLE}. {MAXINE} sitting on the edge of a dorm bed at midnight, robe open and fallen to her hips, completely "
     f"nude beneath, bare breasts with visible nipples, bare thighs, rain-streaked window and blue light, wet-eyed and "
     f"vulnerable, explicit adult female nudity, intimate",
     NEG_CLOTH),
    ("cg_mx_last_lie_sex",
     f"{STYLE}. {MAXINE} and {SAM} having sex on a dorm bed, she is on her back with her legs around him, completely nude, "
     f"her hands on his face, rain-blue window light across the sheets, explicit penetration, bare breasts, "
     f"emotional and physical, explicit adult scene",
     NEG),
    ("cg_mx_cum_covered",
     f"{STYLE}. {MAXINE} lying back on a rumpled bed after sex, completely nude, laughing, semen streaked across her "
     f"stomach, chest, collarbone and one breast, her hand on her own hip, robe open beneath her, rain-blue window light, "
     f"explicit adult scene, marked and unbothered",
     NEG_CLOTH),
    ("cg_mx_wedding_night",
     f"{STYLE}. {MAXINE} on a hotel bed in a white wedding dress pulled down to her waist, veil still in her hair, "
     f"riding {SAM}, both explicit, bare breasts, his hands on her waist, warm lamp light, champagne on the nightstand, "
     f"explicit adult wedding-night scene",
     NEG),
    ("cg_mx_wedding_titfuck",
     f"{STYLE}. {MAXINE} kneeling over {SAM} on a hotel bed, wedding dress open around her waist and veil falling across "
     f"him, pushing her large bare breasts around his erect penis, titfuck, wedding ring visible on her hand, laughing, "
     f"warm lamp light, explicit adult scene",
     NEG),
    ("cg_mx_wedding_facial",
     f"{STYLE}. {MAXINE} in the morning after her wedding, veil off, hair loose, my shirt unbuttoned and nothing else, "
     f"laughing with semen across her cheek and chin, wedding ring hand raised, hotel window sun, explicit adult scene, "
     f"affectionate and filthy",
     NEG),
]


def post(payload, timeout=1800):
    req = urllib.request.Request(HOST + "/sdapi/v1/txt2img", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


urllib.request.urlopen(urllib.request.Request(
    HOST + "/sdapi/v1/options",
    data=json.dumps({"sd_model_checkpoint": "unholyDesireMixFoolS_v60.safetensors"}).encode(),
    headers={"Content-Type": "application/json"}, method="POST"), timeout=300).read()
time.sleep(2)

for idx, (name, prompt, neg) in enumerate(SCENES, 1):
    out = OUT / f"{name}.png"
    for attempt, seed in enumerate((960000 + idx * 31, 960500 + idx * 31, 961000 + idx * 31), 1):
        payload = dict(prompt=prompt, negative_prompt=neg, steps=38, cfg_scale=5.5, width=1024, height=768,
                       sampler_name="DPM++ 2M Karras", scheduler="Karras", seed=seed, batch_size=1, n_iter=1,
                       enable_hr=True, hr_scale=1.5, hr_upscaler="R-ESRGAN 4x+", hr_second_pass_steps=14,
                       hr_additional_modules=[], denoising_strength=0.35,
                       alwayson_scripts={"ADetailer": {"args": [True, False,
                           {"ad_model": "face_yolov8s.pt",
                            "ad_prompt": "detailed face, detailed eyes, natural skin, symmetrical features",
                            "ad_negative_prompt": "deformed face, bad eyes, crossed eyes, distorted mouth",
                            "ad_denoising_strength": 0.30, "ad_inpaint_only_masked": True,
                            "ad_inpaint_padding": 32, "ad_use_steps": False}]}})
        t = time.time()
        res = post(payload)
        tmp = ART / f"raw_{name}.png"
        tmp.write_bytes(base64.b64decode(res["images"][0].split(",", 1)[-1]))
        im = Image.open(tmp).convert("RGB")
        sd = sum(ImageStat.Stat(im).stddev) / 3
        print(f"[{idx:02d}/{len(SCENES)}] {name} try{attempt} {im.size} sd={sd:.1f} {time.time()-t:.1f}s", flush=True)
        if sd > 6:
            tmp.replace(out)
            break
    else:
        print(f"!! {name} stayed blank", flush=True)
print("DONE")
