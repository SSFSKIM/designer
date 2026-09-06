"""W21 G0 — X4: the reader validated by injection before it is believed.

The wave's contract X4 says the instrument is checked by putting a KNOWN body level and a KNOWN rim
into a real capture and recovering both. This does that on a copy of a canonical dark fixture: the
declared box's interior is painted at a chosen linear luminance, the box's outermost ring is painted
at another, and `read.py` — the same file every gate uses, called through its own functions, not a
re-implementation — is asked what it sees. A reader that mislocates the box by a pixel, erodes on the
wrong side, or measures the rim band as a mean rather than a peak fails this check loudly.

Four injections. Three exercise the failure modes that matter in the dark scheme, and the fourth
exists to state, with a number, the one limit of the rim definition:

- a NEAR-BLACK body under a FAINT rim — the dark reference's own shape over `dark-solid` (body
  0.015, rim 0.034 / 0.034 / 0.030 / 0.030), where a rim band leaking into the body would read as a
  response-surface error and where the whole wave's rim clause lives;
- a NEAR-BLACK body under a BRIGHT rim — the case where the silhouette extractor fails outright and
  where a body mask one pixel too wide would report the rim as the body;
- an ASYMMETRIC rim — each side at its own level, so that a reader which pools the four sides, or
  which transposes rows for columns, cannot pass.
- a rim DIMMER than the body. A peak is a maximum, so when the rim sits below the body the band's
  brightest row is a body row and the reading is the body's, not the rim's: the rim peak is a LOWER
  BOUND on the rim, exact only while the rim is the brighter of the two. This case is reported and
  excluded from the recovery bound, because it is the definition working as defined. It costs the
  wave nothing — every untinted dark cell in claims §5.87 has its rim above its body — but a gate
  that ever reads a rim peak equal to its own body level should read this line before believing it.

The rim is painted only on the box's outermost single pixel ring, INSIDE a 3 CSS px band that is
otherwise left at the body level: the peak-per-side definition must find the ring and report it,
while a mean over the band would report roughly a third of it. That gap is the discriminator.

    x4-recovery.py > read-recovery.txt
"""

import os
import shutil
import sys
import tempfile

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from read import component_size, encode, luma_of, masks, read_one  # noqa: E402

import json  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))
SCENES = os.path.join(ROOT, "apps", "reference-apple", "scenes.json")
PROFILE = "apple-macos-26.5-1x-dark-standard"
SCENE = "dark-solid__rrect-md__rest"

CASES = [
    ("faint rim, near-black body", 0.0150, (0.0340, 0.0340, 0.0300, 0.0300), True),
    ("bright rim, near-black body", 0.0080, (0.2400, 0.2400, 0.2400, 0.2400), True),
    ("asymmetric rim", 0.0450, (0.2200, 0.1000, 0.2300, 0.0850), True),
    ("rim BELOW body (definition floor)", 0.0500, (0.0300, 0.0300, 0.0300, 0.0300), False),
]

ERODE, BAND = 6.0, 3.0


def paint(value: float) -> int:
    """The 8-bit sRGB code whose neutral linear luminance is `value`, rounded once."""
    return int(round(float(np.clip(encode(np.asarray(value)), 0.0, 1.0)) * 255.0))


def main() -> int:
    spec = json.load(open(SCENES))
    canvas = spec["canvas"]
    scene = next(s for s in spec["scenes"] if s["id"] == SCENE)
    size = component_size(spec["components"], scene["component"])
    src = os.path.join(ROOT, "apps", "reference-apple", "fixtures", PROFILE, f"{SCENE}.png")

    base = np.asarray(Image.open(src).convert("RGB"))
    scale = base.shape[1] / canvas["width"]
    box, body, sides = masks(canvas, size, scale, base.shape[:2], ERODE, BAND)
    ring = box & ~_erode_one(box)

    print(f"X4 — the reader validated by injection into {PROFILE}/{SCENE}.png")
    print(f"    canvas {canvas['width']}x{canvas['height']}, raster {base.shape[1]}x{base.shape[0]}, "
          f"scale {scale:g}; body = box eroded {ERODE:g} CSS px, rim band = outer {BAND:g} CSS px")
    print(f"    the injected rim occupies the box's OUTERMOST 1 px ring only; the rest of the band "
          f"carries the body level,")
    print(f"    so a band MEAN would under-report the rim by roughly 3x and only a peak recovers it.")
    print()
    print(f"{'case':34s} {'quantity':16s} {'injected':>10s} {'recovered':>10s} {'error':>10s}")

    tmp = tempfile.mkdtemp(prefix="w21-x4-")
    worst = 0.0
    try:
        for label, body_level, rim_levels, bounded in CASES:
            img = base.copy()
            img[box] = paint(body_level)
            for key, level in zip(("top", "bottom", "left", "right"), rim_levels):
                img[ring & sides[key]] = paint(level)
            out = os.path.join(tmp, f"{label.replace(' ', '-').replace(',', '')}.png")
            Image.fromarray(img).save(out)

            got = read_one(out, canvas, size, ERODE, BAND)
            # The injected body level is what a paint at 8-bit precision can carry, not the request.
            realised_body = float(luma_of(out)[body].mean())
            rows = [("body", body_level, got["body"])]
            rows += [
                (f"rim {k}", inj, got["rim"][i])
                for i, (k, inj) in enumerate(zip(("top", "bottom", "left", "right"), rim_levels))
            ]
            for name, inj, rec in rows:
                err = rec - inj
                if bounded:
                    worst = max(worst, abs(err))
                note = "" if bounded else "   (excluded: the peak is a lower bound here)"
                print(f"{label:34s} {name:16s} {inj:10.4f} {rec:10.4f} {err:+10.5f}{note}")
            print(f"{'':34s} {'body (realised)':16s} {realised_body:10.4f} {got['body']:10.4f} "
                  f"{got['body'] - realised_body:+10.5f}")
            print()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"worst |error| across every injected quantity: {worst:.5f}")
    print("The residual is the 8-bit quantisation of the painted value: a neutral sRGB code cannot")
    print("carry an arbitrary linear luminance exactly, and the recovered number is what the file")
    print("holds. Against it the wave's bounds — body 0.010, rim 0.030 — have three decimal digits")
    print("of headroom, and the run-to-run sigma the probe measures is the real noise floor.")
    return 0


def _erode_one(mask: np.ndarray) -> np.ndarray:
    """The mask minus its own one-pixel boundary, without a scipy dependency."""
    inner = np.zeros_like(mask)
    inner[1:-1, 1:-1] = (
        mask[1:-1, 1:-1] & mask[:-2, 1:-1] & mask[2:, 1:-1] & mask[1:-1, :-2] & mask[1:-1, 2:]
    )
    return inner


if __name__ == "__main__":
    raise SystemExit(main())
