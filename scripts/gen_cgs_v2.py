import base64, json, sys, time, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, r"C:\Repos\AI\samandem\scripts")
from cg_board import BOARD, T

HOST="http://127.0.0.1:7861"
ROOT=Path(r"C:\Repos\AI\samandem"); GAME=ROOT/"Sam And Em"/"game"; ART=ROOT/"art"/"generated"/"expanded_art"
CH=json.loads((ROOT/"scripts"/"characters.json").read_text(encoding="utf-8"))
OUT=GAME/"images"/"expanded"/"cg"; OUT.mkdir(parents=True,exist_ok=True)
SHEETS=ART/"cg_sheets"; SHEETS.mkdir(parents=True,exist_ok=True)

STYLE=("polished semi-realistic anime visual novel event CG, cinematic composition, detailed painterly background, "
"expressive eyes, soft rim lighting, volumetric atmosphere, film grain, 2.5D illustration, adult characters, high production value")
CN="cinematic 16:9 event CG, two-shot, shallow depth of field, detailed environment, expressive faces, single coherent scene, no text, no panels, no inset"
NEG=("worst quality, low quality, normal quality, lowres, blurry, jpeg artifacts, sketch, unfinished, bad anatomy, bad hands, "
"extra fingers, missing fingers, fused fingers, deformed hands, distorted face, crossed eyes, asymmetrical eyes, bad proportions, "
"mutated limbs, extra arms, extra legs, long neck, cropped head, out of frame, multiple views, character sheet, reference sheet, collage, "
"split screen, inset portrait, thumbnails, border, frame, text, watermark, signature, logo, child, teen, underage, loli, shota, schoolgirl, "
"childlike face, plastic skin, doll, 3d render, duplicate, two heads, two faces, censored, mosaic")
NEG_CLOTH=  NEG+", nude, topless, naked, bare breasts, nipples, lingerie, underwear, swimsuit, towel, sheet covering body"
NEG_PART=   NEG+", fully nude, bare breasts, nipples, topless, panties visible"
NEG_NUDE=   NEG+", clothes, bra, panties, shirt, dress, gown, underwear, swimsuit, towel, sheet covering chest, fabric over breasts"
NUDE_TAG={
 0:"fully dressed, complete outfit, modest styling.",
 1:"sensual but clothed, garment loosened or slipped, bare shoulders, visible collarbone and upper chest, bare thigh.",
 2:"explicit adult nudity, completely nude, bare breasts with visible nipples, bare hips and thighs, navel, natural body, no clothing.",
}

def post(path,payload,timeout=1200):
    r=urllib.request.Request(HOST+path,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(r,timeout=timeout) as resp: return json.loads(resp.read().decode())

post("/sdapi/v1/options",{"sd_model_checkpoint":"unholyDesireMixFoolS_v60.safetensors"},timeout=300); time.sleep(3)

def F(sz,b=False):
    p=r"C:\Windows\Fonts\arialbd.ttf" if b else r"C:\Windows\Fonts\arial.ttf"
    try: return ImageFont.truetype(p,sz)
    except Exception: return ImageFont.load_default()

manifest=[]
for ci,(c,beats) in enumerate(BOARD.items()):
    for i,(shot,level) in enumerate(beats,1):
        f=OUT/f"{c}_cg_{i:02d}.png"
        prompt=f"{STYLE}. {CH[c]['identity']}. {shot}. {NUDE_TAG[level]} {CN}"
        payload={"prompt":prompt,"negative_prompt":(NEG_NUDE if level>=2 else (NEG_PART if level==1 else NEG_CLOTH)),
          "steps":34,"cfg_scale":5.0,"width":1024,"height":768,"sampler_name":"DPM++ 2M Karras","scheduler":"Karras",
          "seed":330000+i*1013+ci*17,"batch_size":1,"n_iter":1,"enable_hr":True,"hr_scale":1.5,
          "hr_upscaler":"R-ESRGAN 4x+","hr_second_pass_steps":13,"hr_additional_modules":[],"denoising_strength":0.36,
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
            f.write_bytes(base64.b64decode(res["images"][0].split(",",1)[-1]))
            print(f"[{c} {i:02d}] {T[i-1]}  L{level}  {time.time()-t:.1f}s",flush=True)
        except Exception as e:
            print(f"[{c} {i:02d}] FAIL {e}",flush=True)
            continue
        manifest.append({"char":c,"beat":i,"title":T[i-1],"level":level,"file":str(f),"prompt":prompt})
    # per-route contact sheet
    items=[Image.open(OUT/f"{c}_cg_{j:02d}.png").convert("RGB") for j in range(1,11)]
    CW=360; CHW=int(CW*768/1024); COLS=5; PAD=10; CAP=40
    sh=Image.new("RGB",(PAD+COLS*(CW+PAD),PAD+2*(CHW+CAP+PAD)+46),(18,18,22)); d=ImageDraw.Draw(sh)
    d.text((PAD+2,12),f"{c.upper()}  ·  CANONICAL CG SET",font=F(22,True),fill=(240,236,228))
    for j,it in enumerate(items):
        x=PAD+(j%COLS)*(CW+PAD); y=46+PAD+(j//COLS)*(CHW+CAP+PAD)
        sh.paste(it.resize((CW,CHW),Image.LANCZOS),(x,y))
        d.text((x,y+CHW+4),f"{j+1:02d} {T[j][:44]}",font=F(11,True),fill=(205,200,192))
    sh.save(SHEETS/f"{c}_cg_sheet.jpg",quality=90)
    print(f"--- {c}: sheet written ---",flush=True)

(ART/"cg_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
print("ALL 80 DONE")