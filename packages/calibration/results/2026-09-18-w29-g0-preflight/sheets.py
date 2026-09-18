#!/usr/bin/env python3
"""G0's two sheets — the slider, and what the granted bundle draws on 27.

    sheets.py <scratch-root> <out-dir>

**`slider.png`.** Per cell, the four slider positions G0 captured, then three
amplified differences: the centre against each end, and the centre against itself
across two runs. The last column is the one that makes the others readable — a
difference strip is only evidence if the same cell's difference from itself is
beside it, at the same gain, and visibly empty.

**`sdk-gating.png`.** The (c) cell set as the **granted** bundle drew it on 27 —
the bundle whose `LC_BUILD_VERSION` records `sdk 26.0` — beside the committed 26.5
fixture of the same cell, and their amplified difference. What it shows is that a
26.0-linked binary is not drawing 26.5's material on this OS. What it is **not** is
a measurement of what 27 changed: two axes move between those columns, the OS and
the transparency slider, which did not exist on 26.5 and whose position on this
machine is not the one any 26.5 capture was taken at. The native delta is G2's, on
G1's bed, against a declared noise bar; nothing here anticipates it.

Amplification is 8x absolute difference, the gain the W28 sheets use, so a strip
here and a strip there mean the same thing.
"""
import os
import sys

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
FIXTURES = os.path.join(REPO, "apps/reference-apple/fixtures")

GAIN = 8
GAP = 10
PAD = 34
LABEL = 26
BACKGROUND = (20, 20, 20)
INK = (235, 235, 235)


def amplified(a, b):
    return ImageChops.difference(a.convert("RGB"), b.convert("RGB")).point(
        lambda v: min(255, v * GAIN))


def row(images, captions):
    """One row of equal-height images with a caption under each."""
    height = max(i.height for i in images)
    width = sum(i.width for i in images) + GAP * (len(images) - 1)
    canvas = Image.new("RGB", (width, height + LABEL), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    x = 0
    for image, caption in zip(images, captions):
        canvas.paste(image.convert("RGB"), (x, 0))
        draw.text((x + 2, height + 6), caption, fill=INK)
        x += image.width + GAP
    return canvas


def stack(rows, title):
    width = max(r.width for r in rows)
    height = sum(r.height for r in rows) + GAP * (len(rows) - 1)
    canvas = Image.new("RGB", (width + PAD * 2, height + PAD * 2 + LABEL), BACKGROUND)
    ImageDraw.Draw(canvas).text((PAD, PAD // 2), title, fill=INK)
    y = PAD + LABEL
    for r in rows:
        canvas.paste(r, (PAD, y))
        y += r.height + GAP
    return canvas


def load(path):
    return Image.open(path).convert("RGB")


scratch = sys.argv[1]
out = sys.argv[2]
os.makedirs(out, exist_ok=True)

# --- the slider sheet -------------------------------------------------------
ARM = os.path.join(scratch, "d/cap/active-2x")
CELLS = [
    ("apple-macos-26.5-2x-light-standard", "photo__rrect-md__rest"),
    ("apple-macos-26.5-2x-dark-standard", "photo__rrect-md__rest"),
    ("apple-macos-26.5-2x-light-standard", "checkerboard__capsule-button__rest"),
    ("apple-macos-26.5-2x-light-standard", "hc-text__rrect-sm__rest"),
]
rows = []
for profile, scene in CELLS:
    def at(position, run=1):
        return load(os.path.join(ARM, f"{position}-r{run}", profile, f"{scene}.png"))

    left, centre, right = at("0.0"), at("0.5"), at("1.0")
    found = at("0.5459057")
    centre2 = at("0.5", 2)
    rows.append(row([left, centre, right, found],
                    ["0.0 (clear)", "0.5 (centre)", "1.0 (tinted)",
                     "0.5459057 (as found)"]))
    rows.append(row([amplified(centre, left), amplified(centre, right),
                     amplified(centre, found), amplified(centre, centre2)],
                    [f"centre-0.0 x{GAIN}", f"centre-1.0 x{GAIN}",
                     f"centre-asfound x{GAIN}", f"centre r1-r2 x{GAIN} (the bar)"]))
    rows.append(row([Image.new("RGB", (1, 1), BACKGROUND)], [f"{profile}/{scene}"]))

sheet = stack(rows, "W29 G0 (d): NSGlassTintAmount on the harness's own cells, 2x active, macOS 27.0 26A428")
sheet.save(os.path.join(out, "slider.png"), optimize=True)
print(f"→ {os.path.join(out, 'slider.png')} {sheet.size}")

# --- the SDK-gating sheet ---------------------------------------------------
EDGE = os.path.join(scratch, "e/edge-2x/0.5459057-r1")
GRANTED = os.path.join(scratch, "d/cap/active-2x/0.5459057-r1")
PAIRS = [
    (GRANTED, "apple-macos-26.5-2x-light-standard", "photo__rrect-md__rest"),
    (GRANTED, "apple-macos-26.5-2x-light-standard", "checkerboard__capsule-button__rest"),
    (GRANTED, "apple-macos-26.5-2x-light-standard", "hc-text__rrect-sm__rest"),
    (EDGE, "apple-macos-26.5-2x-light-standard", "photo__rrect-lg__rest"),
]
rows = []
for root, profile, scene in PAIRS:
    now = load(os.path.join(root, profile, f"{scene}.png"))
    then_path = os.path.join(FIXTURES, profile, f"{scene}.png")
    if not os.path.exists(then_path):
        continue
    then = load(then_path)
    rows.append(row([then, now, amplified(then, now)],
                    ["26.5 committed fixture", "27, granted bundle (sdk 26.0)",
                     f"difference x{GAIN}"]))
    rows.append(row([Image.new("RGB", (1, 1), BACKGROUND)], [f"{profile}/{scene}"]))

# ASCII in the drawn titles: PIL's default bitmap font has no em dash and renders
# one as a replacement box, which is a caption that misreads on the one artefact a
# reader looks at before anything else.
sheet = stack(rows, "W29 G0 (c): the granted bundle's own pixels on 27 - NOT the native delta (G2's)")
sheet.save(os.path.join(out, "sdk-gating.png"), optimize=True)
print(f"→ {os.path.join(out, 'sdk-gating.png')} {sheet.size}")
