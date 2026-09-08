"""W23 grounding — pixel profiles across the rim and zoomed crops, from captures that exist.

Prints encoded luma (linear Rec.709 luma, re-encoded) along a column through the top edge and a
row through the left edge, for the native fixture and every web capture handed in, so the rim's
placement and amplitude are seen per pixel rather than as a band's peak row.
"""
import sys, os
import numpy as np
from PIL import Image

def lin(a):
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
def enc(a):
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * np.maximum(a, 0) ** (1 / 2.4) - 0.055)
def luma(path):
    c = lin(np.asarray(Image.open(path).convert("RGB"), dtype=np.float64))
    return c[..., 0] * 0.2126 + c[..., 1] * 0.7152 + c[..., 2] * 0.0722

REPO = "/Users/new/Developer/GitHub/designer"
SCR = "/Users/new/.claude/jobs/5c70e47f/tmp/w22/g0/fit"
import json
SIZES = {k: tuple(v["size"]) for k, v in json.load(open(REPO + "/apps/reference-apple/scenes.json"))["components"].items() if "size" in v}

def box(scene, dpr):
    comp = scene.split("__")[1]
    w, h = SIZES[comp]
    x0 = (320 - w) // 2; y0 = (200 - h) // 2
    return x0 * dpr, y0 * dpr, (x0 + w) * dpr, (y0 + h) * dpr

def sources(profile, scene, dpr):
    out = [("native", f"{REPO}/apps/reference-apple/fixtures/{profile}/{scene}.png")]
    for tag, d in (("rim004", f"{SCR}/light-spec0-rim004-{dpr}x"), ("rim018", f"{SCR}/light-spec0-rim018-{dpr}x")):
        p = f"{d}/web-captures/{profile}/{scene}/{scene}__webgpu.png"
        if os.path.exists(p): out.append((tag, p))
    out.append(("landed", f"{REPO}/packages/calibration/web-captures/{profile}/{scene}/{scene}__webgpu.png"))
    return [(t, p) for t, p in out if os.path.exists(p)]

def profile(profile_key, scene, dpr):
    x0, y0, x1, y1 = box(scene, dpr)
    srcs = sources(profile_key, scene, dpr)
    ims = [(t, luma(p)) for t, p in srcs]
    cx = (x0 + x1) // 2; cy = (y0 + y1) // 2
    print(f"\n== {profile_key} {scene} box=({x0},{y0})-({x1},{y1})  columns: " + "  ".join(t for t, _ in ims))
    print("-- top edge, column mean over x in [cx-10, cx+10], rows y0-4 .. y0+9 (encoded luma)")
    for y in range(y0 - 4, y0 + 10):
        vals = [enc(im[y, cx - 10:cx + 10].mean()) for _, im in ims]
        print(f"  y={y - y0:+3d}  " + "  ".join(f"{v:7.4f}" for v in vals))
    print("-- left edge, row mean over y in [cy-6, cy+6], columns x0-4 .. x0+9")
    for x in range(x0 - 4, x0 + 10):
        vals = [enc(im[cy - 6:cy + 6, x].mean()) for _, im in ims]
        print(f"  x={x - x0:+3d}  " + "  ".join(f"{v:7.4f}" for v in vals))

def montage(profile_key, scene, dpr, out, zoom=6, pad=6, size=(64, 40)):
    x0, y0, x1, y1 = box(scene, dpr)
    srcs = sources(profile_key, scene, dpr)
    crops = []
    for t, p in srcs:
        im = Image.open(p).convert("RGB")
        c = im.crop((x0 - pad * dpr, y0 - pad * dpr, x0 - pad * dpr + size[0] * dpr, y0 - pad * dpr + size[1] * dpr))
        crops.append(c.resize((c.width * zoom // dpr, c.height * zoom // dpr), Image.NEAREST))
    W = sum(c.width for c in crops) + 4 * (len(crops) - 1); H = crops[0].height
    sheet = Image.new("RGB", (W, H), (255, 0, 255)); x = 0
    for c in crops:
        sheet.paste(c, (x, 0)); x += c.width + 4
    sheet.save(out); print("wrote", out, "order:", [t for t, _ in srcs])

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "profile":
        profile(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    else:
        montage(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])
