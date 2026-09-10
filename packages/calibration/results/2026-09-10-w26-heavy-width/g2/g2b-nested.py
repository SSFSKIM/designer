"""W26 G2b — the one floor that remains, looked at rather than argued about.

`texture / holdout / checkerboard__glass-over-glass__rest / apple-macos-26.5-2x-dark-standard ::
silhouetteIoU` reads 0.90362 against a floor of 0.9257 (pinned at 0.92707), and the harness's
`silhouetteHolesWeb` goes 39 → 45 against a `silhouetteHolesNative` of 0. The parent asked what the
holes ARE: the checkerboard showing through a too-transparent dark pane that the narrower blur
exposes, or the extractor.

The question is answerable without knowing the harness's silhouette internals, because the two
hypotheses predict different things about quantities this file CAN measure directly:

  * **if it is the pane**, the candidate's interior level or the structure it passes has to have
    moved — a more transparent pane sits nearer the backdrop and passes more of the checker;
  * **if it is the extractor**, the interior barely moves and what moves is how many pixels sit on
    the wrong side of a threshold, which is a property of how many were already sitting ON it.

So this reports the pane's interior level and standard deviation in linear Rec.709 luma against the
native's, how far the PICTURE moved between the two materials, and the population of pixels near a
luminance-delta threshold together with how many of them re-cross it. A threshold of 0.02 is used as
a probe because it is the order the harness works at; **this is not a restatement of the harness's
own silhouette rule** — the harness recovers a hole-free mask from a native whose interior carries
MORE under-threshold pixels than either vitrea column, so its rule is doing something more than a
bare threshold and this file does not guess what.

It also writes `sheets/g2b-nested-4x.png`: the base pane at 4× per CSS px, native | 0.14.0 | the
candidate, because the numbers below say the pane did not move and the eye should get to check that.

    g2b-nested.py --canonical <captures dir> --candidate <captures dir> [--out-prefix DIR]
"""

import argparse
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
FIXTURES = os.path.join(ROOT, "apps", "reference-apple", "fixtures")
BACKGROUNDS = os.path.join(FIXTURES, "backgrounds")
SCENE = "checkerboard__glass-over-glass__rest"
PROFILE = "apple-macos-26.5-2x-dark-standard"
SCALE = 2
# `glass-over-glass`'s BASE pane, from `scenes.json`: 260 × 130 centred on the 320 × 200 canvas.
BASE = (30.0, 35.0, 260.0, 130.0)
PROBES = (0.01, 0.02, 0.03, 0.05)


def luma(path):
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255.0
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return lin[..., 0] * 0.2126 + lin[..., 1] * 0.7152 + lin[..., 2] * 0.0722


def crop(image, left, top, width, height, scale):
    box = (int(round(left * scale)), int(round(top * scale)),
           int(round((left + width) * scale)), int(round((top + height) * scale)))
    return image.crop(box)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--out-prefix", default=os.path.join(HERE, "sheets"))
    args = ap.parse_args()

    columns = [
        ("native", os.path.join(FIXTURES, PROFILE, f"{SCENE}.png")),
        ("0.14.0", os.path.join(args.canonical, PROFILE, SCENE, f"{SCENE}__webgpu.png")),
        ("candidate", os.path.join(args.candidate, PROFILE, SCENE, f"{SCENE}__webgpu.png")),
    ]
    background = os.path.join(BACKGROUNDS, f"checkerboard@{SCALE}x.png")
    if not os.path.exists(background):
        background = os.path.join(BACKGROUNDS, "checkerboard@1x.png")

    left, top, width, height = BASE
    y0, y1 = int(top * SCALE), int((top + height) * SCALE)
    x0, x1 = int(left * SCALE), int((left + width) * SCALE)
    region = (slice(y0, y1), slice(x0, x1))
    bg = luma(background)[region]

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit("W26 G2b — the nested pane's base, 2x dark, GPU tier: what the holes are")
    emit("=" * 104)
    emit("  Region: the stack's BASE pane, its whole declared box. Levels are linear Rec.709 luma.")
    emit()

    read = {}
    tiles = []
    for label, path in columns:
        if not os.path.exists(path):
            emit(f"  {label:10s} (no capture at {path})")
            continue
        read[label] = luma(path)[region]
        image = Image.open(path).convert("RGB")
        tile = crop(image, left - 4, top - 4, width + 8, height + 8, SCALE)
        tiles.append((label, tile.resize((tile.width * 2, tile.height * 2), Image.NEAREST)))

    emit(f"  {'source':10s} {'level':>9s} {'sd':>9s}   the pane's own interior")
    for label in ("native", "0.14.0", "candidate"):
        if label in read:
            emit(f"  {label:10s} {read[label].mean():9.5f} {read[label].std():9.5f}")
    emit(f"  {'backdrop':10s} {bg.mean():9.5f} {bg.std():9.5f}   what it is passing")
    emit()

    if "0.14.0" in read and "candidate" in read:
        moved = np.abs(read["candidate"] - read["0.14.0"])
        emit(f"  How far the PICTURE moved, 0.14.0 → candidate, over {moved.size} pixels:")
        emit(f"    mean |Δluma| {moved.mean():.6f} ({moved.mean() * 255:.2f} of an 8-bit code), "
             f"max {moved.max():.6f} ({moved.max() * 255:.2f} codes)")
        emit()
        emit("  Pixels under a |luma − backdrop| threshold, and how many re-cross it:")
        emit(f"    {'threshold':>10s} {'native':>9s} {'0.14.0':>9s} {'candidate':>10s} "
             f"{'newly under':>12s} {'newly over':>11s}")
        for probe in PROBES:
            dn = np.abs(read["native"] - bg) if "native" in read else None
            do = np.abs(read["0.14.0"] - bg)
            dw = np.abs(read["candidate"] - bg)
            emit(f"    {probe:10.2f} {int((dn < probe).sum()) if dn is not None else -1:9d} "
                 f"{int((do < probe).sum()):9d} {int((dw < probe).sum()):10d} "
                 f"{int(((do >= probe) & (dw < probe)).sum()):12d} "
                 f"{int(((do < probe) & (dw >= probe)).sum()):11d}")
        do = np.abs(read["0.14.0"] - bg)
        near = int((np.abs(do - 0.02) < 0.005).sum())
        emit(f"    pixels sitting within 0.005 of the 0.02 probe at 0.14.0: {near}")

    if tiles:
        gap = 8
        width_px = sum(t.width for _l, t in tiles) + gap * (len(tiles) + 1)
        height_px = max(t.height for _l, t in tiles) + 2 * gap
        sheet = Image.new("RGB", (width_px, height_px), (24, 24, 24))
        x = gap
        for _label, tile in tiles:
            sheet.paste(tile, (x, gap))
            x += tile.width + gap
        os.makedirs(args.out_prefix, exist_ok=True)
        out = os.path.join(args.out_prefix, "g2b-nested-4x.png")
        sheet.save(out)
        emit()
        emit(f"  native | 0.14.0 | candidate, the base pane at 4× per CSS px -> {out}")

    with open(os.path.join(HERE, "g2b-nested.txt"), "w") as handle:
        handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
