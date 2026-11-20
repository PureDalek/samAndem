import base64, json, shutil, sys, time, urllib.request
from pathlib import Path
from PIL import Image, ImageFilter

HOST="http://127.0.0.1:7861"
ROOT=Path(r"C:\Repos\AI\samandem"); G=ROOT/"Sam And Em"/"game"/"images"
ART=ROOT/"art"/"generated"/"art_v03"; ART.mkdir(parents=True,exist_ok=True)
BAK=ROOT/"art"/"backups"/"art_v03_original"; BAK.mkdir(parents=True,exist_ok=True)
LOG=ART/"render.log"

STYLE=("polished semi-realistic anime visual novel art, high-end game illustration, soft painterly cel shading, "
       "clean crisp lineart, detailed expressive eyes, natural skin texture, cinematic lighting, 2.5D, adult characters")
SAM=("adult man, 18 years old, short messy black hair, soft brown eyes, pale skin with light freckles, slim average build, "
      "gentle anxious expression, clean-shaven")
CLARA=("adult woman, 22 years old, long auburn red-brown hair, warm brown eyes, full curvy figure, large natural bust, "
       "composed confident expression, fair warm skin")
MAXINE=("adult woman, 21 years old, busty athletic tomboy, short spiky black hair with vivid blue streaks, bright blue eyes, "
        "strong toned shoulders and arms, tanned skin, hand wraps, teasing confident grin")
LADY=("adult woman in her mid thirties, elegant, long black hair, jade green eyes, burgundy coat, mysterious composed expression")

NEG=("worst quality, low quality, normal quality, lowres, blurry, jpeg artifacts, sketch, unfinished, "
"bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, deformed hands, distorted face, crossed eyes, "
"asymmetrical eyes, bad proportions, mutated limbs, extra arms, extra legs, long neck, cropped head, out of frame, "
"multiple views, character sheet, reference sheet, collage, split screen, inset portrait, thumbnails, border, frame, "
"text, watermark, signature, logo, child, teen, underage, loli, shota, schoolgirl, childlike face, plastic skin, doll, "
"3d render, duplicate, two heads, two faces, censored, mosaic")
NBG=NEG+", people, characters, person, silhouette, cropped figure"
NCHAR=NEG+", background clutter, furniture, multiple characters, two people, shadow on floor, cropped feet"
NCHROMA=NCHAR+", gradient background, scenery, green hair, green clothing, green skin, patterned background, floor line"
NNSFW=NEG+", clothes, bra, panties, shirt, dress, underwear, swimsuit, towel, sheet covering chest, fabric over breasts, barbie doll anatomy"
NMALE=NNSFW+", female, breasts, girl"
NFEM=NNSFW+", male, penis, boy"

def job(path, prompt, w, h, scale, neg, steps=34, cfg=5.0):
    return dict(path=path, prompt=prompt, w=w, h=h, scale=scale, neg=neg, steps=steps, cfg=cfg)

J=[]
# ---------- backgrounds (16:9, no people) ----------
bg_common=f"{STYLE}, detailed visual novel background art, no characters, cinematic composition"
J.append(job("backgrounds/academy_dorm_exterior.png",
 f"{bg_common}. A grand old brick academy dormitory at dusk: tall arched windows glowing warm, ivy on the stone, "
 f"wet granite steps, a brass lamp by the entrance, autumn trees, violet rain clouds, empty street, establishing shot",1536,864,1.25,NBG))
J.append(job("backgrounds/dorm_lobby.png",
 f"{bg_common}. The lobby of an old student dormitory: dark wood reception desk, brass key rack, leather couches, "
 f"a crowded noticeboard, checkerboard tile floor, tall windows with evening light, warm lamps, worn elegance, empty",1536,864,1.25,NBG))
J.append(job("backgrounds/dorm_room_214.png",
 f"{bg_common}. A small student dorm room in the morning: two narrow beds with rumpled white sheets, one spare mattress, "
 f"an old rattling fan, wooden floor, blinds letting in bars of sunlight, books and a backpack, lived-in, empty of people",1536,864,1.25,NBG))
J.append(job("backgrounds/communal_showers.png",
 f"{bg_common}. A tiled communal dorm shower room: steam in the air, row of shower heads, a wooden bench, grey lockers, "
 f"a paper notice taped to the door, misty overhead light, wet floor reflections, empty",1536,864,1.25,NBG))

# ---------- shipped story CGs (16:9) ----------
J.append(job("cgs/maxine_morning_cg.png",
 f"{STYLE}. {MAXINE}, lying half-asleep on top of rumpled white sheets in a small dorm room, one arm thrown over her face, "
 f"completely topless, large bare breasts with visible nipples, blue-striped sleep shorts, bare midriff and thighs, "
 f"morning sunlight through blinds striping her body, old fan blurred, explicit adult nudity, intimate warm atmosphere, 16:9",1536,864,1.25,NNSFW))
J.append(job("cgs/clara_intervention_cg.png",
 f"{STYLE}. {CLARA}, standing in the doorway of a steam-filled tiled communal shower, topless, holding a white towel firmly "
 f"across her chest, long wet auburn hair over her shoulders, water droplets on her skin, stern composed expression, "
 f"backlit by corridor light, steam and tile, authoritative and flustered at once, 16:9",1536,864,1.25,NCHAR))
J.append(job("cgs/shower_schedule_cg.png",
 f"{STYLE}. {CLARA}, in a beige cardigan over a white towel, damp auburn hair, holding a clipboard with a handwritten shower "
 f"schedule and a pen, standing in a dorm corridor, looking up with a dry unimpressed expression; in the background "
 f"{SAM} in a towel holds a shower bag, mortified. 16:9 visual novel CG, morning light",1536,864,1.25,NCHAR))

# ---------- character sprites (transparent via chroma) ----------
def sprite(name,prompt,neg=NCHROMA): return job(f"characters/{name}.png",prompt,704,1472,1.25,neg)
pose="full body standing pose, facing viewer, complete figure from shoes to top of hair, generous empty margin around the figure, even soft studio lighting, clean silhouette"
J.append(sprite("protagonist", f"{STYLE}. {SAM}, student. He wears a black hoodie over a white t-shirt, dark jeans, white sneakers, a canvas backpack strap. {pose}. Flat solid chroma-key pure green background (#00FF00), no shadow on the background, no scenery"))
J.append(sprite("maxine", f"{STYLE}. {MAXINE}, in a navy sports bra under an open sleeveless hoodie, dark track pants, white sneakers, white hand wraps. Confident grin, hand on hip. {pose}. Flat solid chroma-key pure green background (#00FF00), no shadow on the background, no scenery"))
J.append(sprite("dorm_leader", f"{STYLE}. {CLARA}, dorm leader, in a beige cardigan, white silk blouse, black pencil skirt, a lanyard with keys, dark heels, stockings. Composed smile, clipboard at her side. {pose}. Flat solid chroma-key pure green background (#00FF00), no shadow on the background, no scenery"))

# ---------- gallery (explicit, 2 each) ----------
J.append(job("gallery/alex_private_01.png",
 f"{STYLE}. Explicit adult male nude study. {SAM}, in a dim dorm room at night, sitting on the edge of a bed, "
 f"completely nude, visible penis, bare chest and shoulders, warm lamp, laptop glow, looking away, tense and handsome, "
 f"35mm, shallow depth of field, 16:9",1536,864,1.25,NMALE))
J.append(job("gallery/alex_private_02.png",
 f"{STYLE}. Explicit adult male nude study, full body. {SAM}, standing by a window at dawn, completely nude, visible penis, "
 f"boxer briefs in one hand, bare feet, curtain light across his chest, shy half-smile, tall portrait composition",
 704,1472,1.25,NMALE))
J.append(job("gallery/clara_private_01.png",
 f"{STYLE}. Explicit adult female nude study. {CLARA}, in her dorm room at night, seated at a vanity, completely nude, "
 f"large bare breasts with visible nipples, auburn hair down over one shoulder, warm lamp and mirror bulbs, "
 f"silk robe puddled on the chair, composed and unbothered, 16:9",1536,864,1.25,NFEM))
J.append(job("gallery/clara_private_02.png",
 f"{STYLE}. Explicit adult female nude study, full body. {CLARA}, standing three-quarter back, looking over her shoulder, "
 f"completely nude, bare breasts visible in profile, auburn hair down her back, hand on a dresser, bedroom at dusk, "
 f"tall portrait composition",704,1472,1.25,NFEM))
J.append(job("gallery/maxine_private_01.png",
 f"{STYLE}. Explicit adult female nude study. {MAXINE}, in her dorm room, topless on rumpled sheets, "
 f"large bare breasts with visible nipples, navy sleep shorts, hand wraps, athletic thighs, laughing at someone off-frame, "
 f"morning light, candid, 16:9",1536,864,1.25,NFEM))
J.append(job("gallery/maxine_private_02.png",
 f"{STYLE}. Explicit adult female nude study, full body. {MAXINE}, standing in a hotel-room gym mirror light, "
 f"completely nude except for white hand wraps, athletic curvy body, large bare breasts with visible nipples, "
 f"toned arms and stomach, short spiky black hair with blue streaks, blue eyes, cocky grin, tall portrait composition",
 704,1472,1.25,NFEM))

# ---------- NSFW character slots (3:4) ----------
def slot(c,name,prompt,neg):
    return job(f"nsfw/{c}/{name}.png",prompt,768,1024,1.5,neg)
J.append(slot("alex","base", f"{STYLE}. {SAM}, standing in his dorm room, wearing a black hoodie over a white t-shirt, dark jeans, sneakers, "
    f"backpack strap in one hand, nervous but warm, three-quarter length, plain warm grey studio background",NCHAR))
J.append(slot("alex","underwear", f"{STYLE}. {SAM}, standing in his dorm room, wearing only dark boxer briefs, bare chest and shoulders, "
    f"slim average build, hand behind his neck, shy half-smile, low intimate light, plain neutral background",NCHAR))
J.append(slot("alex","nude_front", f"{STYLE}. Explicit adult male nude study. {SAM}, standing full frontal, completely nude, "
    f"visible penis and testicles, arms relaxed, bare feet, natural body, candid eye contact, soft studio light, plain light background",NMALE))
J.append(slot("alex","nude_alt", f"{STYLE}. Explicit adult male nude study. {SAM}, sitting on the edge of his dorm bed, completely nude, "
    f"soft half-erect penis, one knee up, leaning back on one hand, looking at the viewer, warm lamp, intimate",NMALE))
J.append(slot("maxine","base", f"{STYLE}. {MAXINE}, in a navy cropped athletic top and low-rise track pants, white hand wraps, "
    f"sneakers, standing with a cocky grin, hand on hip, three-quarter length, plain neutral studio background",NCHAR))
J.append(slot("maxine","underwear", f"{STYLE}. {MAXINE}, in a navy sports bra and matching high-cut athletic shorts, white hand wraps, "
    f"bare toned midriff and legs, stretching one arm overhead, confident, plain neutral studio background",NCHAR))
J.append(slot("maxine","nude_front", f"{STYLE}. Explicit adult female nude study. {MAXINE}, standing full frontal, completely nude except for white hand wraps, "
    f"large bare breasts with visible nipples, athletic toned body, bare hips and thighs, visible vulva, cocky grin, soft studio light, plain light background",NFEM))
J.append(slot("maxine","nude_alt", f"{STYLE}. Explicit adult female nude study. {MAXINE}, kneeling on a rumpled bed, completely nude, "
    f"hand wraps, one arm across her chest and the other low, bare breasts, athletic thighs, looking over her shoulder at the viewer, "
    f"warm morning light, explicit",NFEM))
J.append(slot("clara","base", f"{STYLE}. {CLARA}, in a beige cardigan over a white blouse and a black pencil skirt, lanyard, heels, "
    f"composed dorm-leader posture, three-quarter length, plain neutral studio background",NCHAR))
J.append(slot("clara","underwear", f"{STYLE}. {CLARA}, in a cream satin bralette and matching shorts, soft robe slipping off her shoulders, "
    f"auburn hair down, bare legs, composed and warm, plain neutral studio background",NCHAR))
J.append(slot("clara","nude_front", f"{STYLE}. Explicit adult female nude study. {CLARA}, standing full frontal, completely nude, "
    f"large bare breasts with visible nipples, full curvy figure, bare hips and thighs, visible vulva, auburn hair down, calm confident gaze, "
    f"soft studio light, plain light background",NFEM))
J.append(slot("clara","nude_alt", f"{STYLE}. Explicit adult female nude study. {CLARA}, seated on a chair, three-quarter back, looking over her shoulder, "
    f"completely nude, bare breasts visible in profile, auburn hair swept to one side, bare back and hip, elegant, warm lamp light",NFEM))

# ---------- NSFW story CGs (4:3) ----------
J.append(job("nsfw/cg/cg_b2_maxine_almost_date.png",
 f"{STYLE}. Late library almost-date. {MAXINE} leaning across a corner table toward a young man, cropped navy athletic top, "
 f"low-rise shorts, bare shoulders and midriff, books pushed aside, warm desk lamp, knees almost touching, heated eye contact, "
 f"intimate temptation, 4:3 visual novel CG",1024,768,1.5,NCHAR))
J.append(job("nsfw/cg/cg_c1_gala_private_balcony.png",
 f"{STYLE}. Campus gala, private balcony at night. {MAXINE} in a navy low-back evening gown with a thigh slit, bare shoulders, "
 f"standing close to a young man in a loosened black suit, city lights below, tension; in the doorway {CLARA} in a cream slip dress "
 f"watches them, romantic jealousy, 4:3 visual novel CG",1024,768,1.5,NCHAR))
J.append(job("nsfw/cg/cg_c2j_lady_no_questions.png",
 f"{STYLE}. Hotel room, late night. {LADY}, in a black satin slip and undone coat, sitting on the edge of the bed beside a sealed "
 f"envelope, police lights moving across the curtains, one hand on a young man's chest, sensual suspense, 4:3 visual novel CG",
 1024,768,1.5,NCHAR))
J.append(job("nsfw/cg/cg_c2l_lady_real_name.png",
 f"{STYLE}. Hotel room, warm lamp. {LADY}, robe open, black slip beneath, bare shoulders and thigh, two train tickets on the table, "
 f"leaning close to a young man, vulnerability and trust, 4:3 visual novel CG, explicit adult intimacy",1024,768,1.5,NCHAR))
J.append(job("nsfw/cg/cg_c2m_maxine_last_lie.png",
 f"{STYLE}. Rain at midnight, dorm room. {MAXINE}, sitting on the edge of the bed in an open robe over bare skin, rain-light on her face, "
 f"a young man kneeling in front of her, her hand on his jaw, hard truth and intimacy, 4:3 visual novel CG",1024,768,1.5,NCHAR))
J.append(job("nsfw/cg/cg_e1_wedding_garden_private_vow.png",
 f"{STYLE}. Wedding garden after the ceremony, string lights. {MAXINE} in an ivory silk wedding dress, one shoulder bare, "
 f"her forehead against a young man's, his hand at her waist, private vow, golden dusk, intimate and explicit-sensual, 4:3 visual novel CG",
 1024,768,1.5,NCHAR))
J.append(job("nsfw/cg/cg_e2_two_tickets_private_compartment.png",
 f"{STYLE}. Night train, private compartment. {LADY} in a black slip, seated across a young man's lap, two tickets on the table, "
 f"city lights sliding past the window, her hand at his collar, explicit adult intimacy, 4:3 visual novel CG",1024,768,1.5,NCHAR))

def post(path,payload,timeout=1800):
    r=urllib.request.Request(HOST+path,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(r,timeout=timeout) as resp: return json.loads(resp.read().decode())

def key_green(src, dst_rgba, dst_chroma):
    im=Image.open(src).convert("RGB")
    import numpy as np
    a=np.asarray(im).astype(np.int32)
    r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    dom=g-np.maximum(r,b)
    alpha=np.clip((150.0-dom)*2.2,0,255).astype(np.uint8)
    alpha=Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    spill=np.maximum(r,b)
    g2=np.minimum(g,spill+np.where(alpha>8,0,255))
    rgb=np.stack([r,g2,b],axis=2).clip(0,255).astype(np.uint8)
    out=Image.fromarray(rgb,"RGB").convert("RGBA"); out.putalpha(alpha)
    out.save(dst_rgba)
    im.copy().save(dst_chroma)

post("/sdapi/v1/options",{"sd_model_checkpoint":"unholyDesireMixFoolS_v60.safetensors"},timeout=300); time.sleep(2)
t_all=time.time()
for n,jb in enumerate(J,1):
    out=G/jb["path"]; out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():
        bk=BAK/jb["path"]; bk.parent.mkdir(parents=True,exist_ok=True)
        if not bk.exists(): shutil.copy2(out,bk)
    neg=jb["neg"]
    if "nude" in jb["path"] or "gallery" in jb["path"] or "cg/" in jb["path"]:
        pass
    payload={"prompt":jb["prompt"],"negative_prompt":neg,"steps":jb["steps"],"cfg_scale":jb["cfg"],
      "width":jb["w"],"height":jb["h"],"sampler_name":"DPM++ 2M Karras","scheduler":"Karras",
      "seed":770000+n*137,"batch_size":1,"n_iter":1,
      "enable_hr":True,"hr_scale":jb["scale"],"hr_upscaler":"R-ESRGAN 4x+","hr_second_pass_steps":14,
      "hr_additional_modules":[],"denoising_strength":0.35,
      "alwayson_scripts":{"ADetailer":{"args":[True,False,{
        "ad_model":"face_yolov8s.pt","ad_prompt":"detailed face, detailed eyes, natural skin, symmetrical features",
        "ad_negative_prompt":"deformed face, bad eyes, crossed eyes, distorted mouth","ad_denoising_strength":0.30,
        "ad_inpaint_only_masked":True,"ad_inpaint_padding":32,"ad_use_steps":False},
        {"ad_model":"hand_yolov8s.pt","ad_prompt":"detailed hands, five fingers, natural anatomy",
         "ad_negative_prompt":"extra fingers, missing fingers, fused fingers, deformed hands","ad_denoising_strength":0.34,
         "ad_inpaint_only_masked":True,"ad_inpaint_padding":48,"ad_use_steps":False}]}}}
    t=time.time()
    try:
        res=post("/sdapi/v1/txt2img",payload)
        tmp=ART/("raw_"+out.name); tmp.write_bytes(base64.b64decode(res["images"][0].split(",",1)[-1]))
        if jb["path"].startswith("characters/"):
            key_green(tmp, out, out.with_name(out.stem+"_chroma.png"))
        else:
            shutil.copy2(tmp,out)
        msg=f"[{n:02d}/{len(J)}] {jb['path']} {out.size if hasattr(out,'size') else ''} {time.time()-t:.1f}s"
        print(msg,flush=True); LOG.write_text(LOG.read_text(encoding="utf-8")+msg+"\n",encoding="utf-8") if LOG.exists() else LOG.write_text(msg+"\n",encoding="utf-8")
    except Exception as e:
        print(f"[{n:02d}/{len(J)}] {jb['path']} FAIL {e}",flush=True)
print(f"ALL DONE {time.time()-t_all:.1f}s")