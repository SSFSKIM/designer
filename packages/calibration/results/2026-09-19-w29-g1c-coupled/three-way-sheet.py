#!/usr/bin/env python3
"""26.5 | 27 coupled | 27 decoupled, on one strip — the picture §5.151 §9 could not have.

W29 G1c Part B, claims §5.152 §B. The native-delta sheets are pair sheets by
construction: one 26.5 cell, one 27 cell, their amplified difference. The
question this child answers is a three-way one — the same cell on the 26.5 bed,
on the 27 bed in the state 26.5 forced, and on the 27 bed in the state macOS 27
gives you by turning contrast on — and no pair sheet can show it.

Read left to right the strip separates the two changes that §5.151 §9 had to
refuse to separate: 26.5 → coupled is the MATERIAL, coupled → decoupled is the
TOGGLE, and 26.5 → decoupled is the confounded reading the ledger reports for the
profile of that name.

    three-way-sheet.py [--scale 4]

Reads committed fixtures only and writes into `sheets/` beside this file.
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
FIX = os.path.join(REPO, "apps", "reference-apple", "fixtures")

BEDS = [
    ("26.5 (coupled: the only state it had)", "apple-macos-26.5-1x-light-increased-contrast"),
    ("27 coupled (IC=1, RT=1)", "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5"),
    ("27 decoupled (IC=1, RT=0)", "apple-macos-27.0-1x-light-increased-contrast-glass0.5"),
]

# Four cells, chosen for what they separate rather than for how they score: a
# photo backdrop where the toggle is most visible, a text backdrop where
# legibility is the axis the mode exists for, a near-black backdrop where the
# extractor's threshold is the §5.151 §4 finding, and a tinted cell.
CELLS = [
    "photo__rrect-lg__rest",
    "hc-text__capsule-button__inactive",
    "dark-solid__rrect-md-clear20__inactive",
    "photo__capsule-button__inactive-tint-orange",
]

scale = 4
if "--scale" in sys.argv:
    scale = int(sys.argv[sys.argv.index("--scale") + 1])

manifest = json.load(open(os.path.join(FIX, "manifest.json"), encoding="utf-8"))
byprofile = {p["profileKey"]: {f["sceneId"]: f["file"] for f in p["fixtures"]}
             for p in manifest["profiles"]}

out_dir = os.path.join(HERE, "sheets")
os.makedirs(out_dir, exist_ok=True)
written = []
for cell in CELLS:
    images = []
    for _, key in BEDS:
        path = byprofile.get(key, {}).get(cell)
        if path is None:
            break
        images.append(Image.open(os.path.join(FIX, path)).convert("RGB"))
    if len(images) != len(BEDS):
        print("skipped (not on every bed): " + cell)
        continue
    w, h = images[0].size
    gap = 8
    strip = Image.new("RGB", (w * len(images) * scale + gap * (len(images) - 1), h * scale),
                      (20, 20, 20))
    for i, image in enumerate(images):
        strip.paste(image.resize((w * scale, h * scale), Image.NEAREST),
                    (i * (w * scale + gap), 0))
    name = "three-way__%s__x%d.png" % (cell, scale)
    strip.save(os.path.join(out_dir, name))
    written.append(name)

print("%d strips written under %s" % (len(written), out_dir))
for name in written:
    print("  " + name)
print()
print("left to right: " + " | ".join(label for label, _ in BEDS))
