#!/usr/bin/env python3
"""UIClip (Wu et al., UIST 2024; MIT) as a non-LLM quality column for the settling builds.

    python3 uiclip.py [--out uiclip.json]

Scores every built page's first-viewport and full-page capture against its brief, with the model
card's sliding-window recipe: the image is resized so its shorter side is 224 px, cut into
224 × 224 windows along the longer side, the window embeddings averaged, and the score is the
softmax weight on "well-designed" against "poor design" for the same description (0–1, higher is
better). Writes {id: {"fv": s, "full": s, "brief": …}} to figma-design-workspace/settling/uiclip.json.
The model is ~0.2 B parameters and runs on the CPU; the first run downloads it.
"""
import json, os, sys, re
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../.."))
WS = os.environ.get("SETTLING_WS") or os.path.join(REPO, "figma-design-workspace/settling")
sys.path.insert(0, HERE)
import rate

IMG_SIZE = 224; DEVICE = "cpu"; LOGIT_SCALE = 100
# The hub client's large-file download stalled on this machine (66 MB of 605 MB, then nothing)
# while a plain curl of the same file ran at 2 MB/s, so UICLIP_PATH may name a local directory
# holding config.json and model.safetensors fetched by curl; the hub id is the default.
MODEL = os.environ.get("UICLIP_PATH") or "biglab/uiclip_jitteredwebsites-2-224-paraphrased_webpairs_humanpairs"
PROCESSOR = "openai/clip-vit-base-patch32"
Image.MAX_IMAGE_PIXELS = None

model = CLIPModel.from_pretrained(MODEL).eval().to(DEVICE)
processor = CLIPProcessor.from_pretrained(PROCESSOR)


def tensor_of(out, *names):
    """transformers 5 returns an output object from get_*_features where 4 returned the tensor."""
    if torch.is_tensor(out):
        return out
    for n in names:
        v = getattr(out, n, None)
        if v is not None:
            return v
    return out[0]


def text_emb(descs):
    inp = processor(text=descs, return_tensors="pt", padding=True, truncation=True, max_length=77)
    with torch.no_grad():
        out = model.get_text_features(input_ids=inp["input_ids"].to(DEVICE), attention_mask=inp["attention_mask"].to(DEVICE))
    return tensor_of(out, "text_embeds", "pooler_output")


def preresize(im):
    ar = im.width / im.height
    return im.resize((int(ar * IMG_SIZE), IMG_SIZE)) if ar > 1 else im.resize((IMG_SIZE, int(IMG_SIZE / ar)))


def windows(im):
    im = preresize(im.convert("RGB")); w, h = im.size; sq = min(w, h); longer = max(w, h)
    n = (longer + sq - 1) // sq; step = (longer - sq) // (n - 1) if n > 1 else sq
    out = []
    for y in range(0, h - sq + 1, step if h > w else sq):
        for x in range(0, w - sq + 1, step if w > h else sq):
            out.append(im.crop((x, y, x + sq, y + sq)))
    return out


def image_emb(im):
    ws = windows(im); inp = processor(images=ws, return_tensors="pt")
    with torch.no_grad():
        f = tensor_of(model.get_image_features(pixel_values=inp["pixel_values"].to(DEVICE)), "image_embeds", "pooler_output")
    return f.mean(dim=0, keepdim=True)


def score(desc, im):
    t = text_emb(["ui screenshot. well-designed. " + desc, "ui screenshot. poor design. " + desc])
    t = t / t.norm(dim=-1, keepdim=True)
    i = image_emb(im); i = i / i.norm(dim=-1, keepdim=True)
    return float((LOGIT_SCALE * i @ t.T).softmax(dim=-1)[0, 0])


def description(ev):
    """The brief with its delivery sentence removed: what the page is, for the text side."""
    t = rate.brief_text(ev)
    t = re.sub(r"\s*(Build it as a|Single HTML file)[^.]*\.?", "", t)
    return t.strip()


if __name__ == "__main__":
    out_path = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(WS, "uiclip.json")
    cells = json.load(open(rate.MANIFEST))["cells"]
    out = {}
    for c in cells:
        d = os.path.join(WS, "builds", c["id"])
        if not (os.path.exists(os.path.join(d, "shot-fv.png")) and os.path.exists(os.path.join(d, "shot-full.png"))):
            continue
        desc = description(c["eval"])
        out[c["id"]] = {"brief": c["brief"], "arm": c["arm"], "seed": c["seedLabel"],
                        "fv": score(desc, Image.open(os.path.join(d, "shot-fv.png"))),
                        "full": score(desc, Image.open(os.path.join(d, "shot-full.png")))}
        print(c["brief"], c["arm"], c["seedLabel"], c["id"], round(out[c["id"]]["fv"], 3), round(out[c["id"]]["full"], 3), flush=True)
    json.dump(out, open(out_path, "w"), indent=1)
    print("wrote", out_path, len(out), "pages")
