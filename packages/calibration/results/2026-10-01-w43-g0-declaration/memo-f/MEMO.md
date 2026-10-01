# Memo F — the Glass appearance slider in Apple's declared tree (2026-10-01)

Charter clause 2, Design "Memo F", X38, X42. `dump-layers` ran through the W39 side bundle at
x = 0, 0.125, …, 1 in all four endpoints at 2x, plus x = 0.25 at 1x. That was 40 launches and 264
scene dumps, all admitted, on six shapes on dark-solid (s = 44, 64, 80, 96, 128, 160) and rrect-md on
photo and the checkerboard at 0, 0.25 and 1. The run record is `run/`, the reading `reading/` and the
fold `reading/fold.json`. **Every number here is a pointer to Apple's declared configuration**, read
from the inputs of a private filter. The pixels referee them (X38).

**The control held.** At x = 0.5 every surface reproduces memo D field for field, with zero
departures in all four endpoints. The machine, the side bundle and the fresh-launch rule read what
memo D read on 2026-09-29.

## 1. What moves with x, and nothing else does

| input (glassBackground unless marked) | light | dark | role in LT |
| --- | --- | --- | --- |
| `BlurFillNormalOpacity` | **= x** at all nine positions | the same | w |
| `BlurFillLightenOpacity` / `…DarkenOpacity` | 0.675 + 0.45x on [0, 0.5], 0.9 on [0.5, 1] | Darken, the same ramp | λ |
| `FaceColorMatrixFillColor` | white; alpha 0.4x on [0, 0.5], then 0.2 + 0.6(x − 0.5) | grey 0.25·\|x − 0.5\|; alpha 0 on [0, 0.5], then x − 0.5 | T |
| `FaceColorMatrixMaxLuma` = `…MaxLumaSDR` | 1 / 0.94, unchanged | at s ≥ 80 on [0, 0.5]: max(0.45 − 0.2x, 0.6 − (0.36 + 0.48x)·t); memo D's max(0.35, 0.6 − 0.6t) on [0.5, 1]; 0.6 at s ≤ 64 | T |
| `bd.scale` (the backdrop capture scale) | 0.5 at s ≤ 96 for x < 1, **0.125 at x = 1** on every shape; rrect-ml 0.25 at 0.875 (active) or from 0.625 (receded); rrect-lg 0.5 at x ≤ 0.25, then 0.25 | the same, except rrect-lg at 0.5 up to x = 0.375 and rrect-ml from 0.75 when receded | C and W |

**Nothing else moves at any position, in any endpoint, on any shape.** That covers:
- the narrow blur's radius 5, its opacities and SDF distances;
- the fill's radius 8;
- the face matrix's black, white and saturation, and the clamp;
- refraction, the bleed, the shadows, the ring shadow and the highlight;
- the SDF output, the margin and the element.

**The backdrop control holds.** At 0, 0.25 and 1, rrect-md on photo and on the checkerboard is
field-for-field identical to dark-solid in all four endpoints.

**1x against 2x at 0.25.** All 24 scene-endpoints differ only in memo D's four one-device-pixel
terms.

## 2. Memo D's span laws at 0.25

Every law memo D wrote holds unchanged at 0.25 (`dumpcheck.py` against memo D's reference), except two:
- **the dark MaxLuma law:** its slope in t is 0.48 against 0.6, and its floor 0.40 against 0.35;
- **the backdrop capture scale on rrect-lg:** 0.5 at x = 0.25 against 0.25 at 0.5, in all four
  endpoints.

The scale step memo D could not attribute to span or area is now also a function of x, the scheme
and the pose. It reads like a resolution choice that follows the effective blur. That is a pointer,
not a reading of why.

## 3. The dark scheme's ramps

Darken follows Lighten's ramp exactly. The dark face fill is inert below 0.5 (alpha 0) and becomes a
dark grey at alpha x − 0.5 above it. The dark cap relaxes as the glass clears: at x = 0 it reads 0.54
at s = 80, 0.48 at 96 and 0.45 at 128 and 160. So dark native T depends on x below 0.5 on every
span stratum the probe reads above t = 0. The w-test inverts T natively at each position, so this
enters the statistic only through its own greys.

## What this says for the declaration

- **The w-test's prediction is stated in all four 2x endpoints** (`reading/fold.json`). Between 0.25
  and 0.5 no input that sets C or W moves on the w-test's support shapes (s = 44, 64, 96). The capture
  scale moves only on rrect-lg, which is not support. Normal reads exactly 0.25 and 0.5, so
  w(0.25)/w(0.5) = **0.5**. λ moves (0.9 → 0.7875 in both schemes) and enters only the lifted side.
  The face fill and the dark cap move; they are T, and T is inverted per position.
- **The ladder's ends are not one-knob.** At x = 1 the capture scale is 0.125 on every shape, against
  0.5. The x = 1 cells read W through a backdrop sampled at a quarter of the density, and the ladder's
  description must say so. At x = 0, λ is 0.675, the light fill is clear, and the dark cap is relaxed
  at s ≥ 80. At x = 0.75 the probe's shapes keep their 0.5 capture.
- **For G2 and G3**, read at x = 0.25 against 0.5:
  - the rrect-lg capture scale differs, so the canonical rrect-lg cells' realisation changes with x;
  - the dark T changes at s ≥ 80;
  - the light fill halves;
  - the hinge weakens by 0.1125.
  These are pointers for clause 7's verdict per law; none is a fitted value.
