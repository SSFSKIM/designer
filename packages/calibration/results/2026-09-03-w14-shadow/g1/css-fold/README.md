# W14 G1 — the CSS tier's thick amplitude derived, and read by capture (2026-09-03)

Claims §5.65 §2 and §6(ii) executed and verified. The sweep fitted the composite's four
provisional constants **on the tier that has a lift**, and the CSS tier — which by W14 Decision
Log 4 (user) does not paint the lift — inherited an anchor that assumes light is being added
back, so its thick spans over-darkened badly and its exterior was further from the reference
than before the wave. This run reads the fix by capture.

The fix is a **conversion, not a constant**. Outside the coverage the GPU tier composites, in
the encoded domain, `out = B·(1 − α) + L`; one multiply can only produce `out = B·(1 − α′)`;
matching them at the backdrop level the tier already reads gives `α′ = α − L/B`, with `L`
evaluated from the profile's own `liftAmplitude`, the span rise between `liftSpanMin` and
`liftSpanFull`, and the same sRGB encode the shader emits its lift through. No second anchor
set, no per-tier constant, no tier flag: `cssTierShadowAlpha` in
`packages/platform-web/src/optics.ts`, pinned against the renderer by
`packages/calibration/test/tier-coherence.test.ts`.

Branch `w14-g1-shadow`, commit `c27b372` (which also writes the sweep's chosen constants into
both profile documents and the runtime defaults they pin). Nothing was fitted here; the
derivation has no free parameter.

## The derived correction, from the profile and nothing else

At the tier's own backdrop statistic (the backdrop's encoded-space mean, decoded — the
checkerboard's is 0.214 linear), with `liftAmplitude` 0.0100, `liftSpanMin` 64 and
`liftSpanFull` 118:

| backdrop | span | rise | peak occlusion before | after | Δ occlusion | Δ encoded alpha |
| --- | --- | --- | --- | --- | --- | --- |
| checkerboard (L 0.214) | 44 | 0.000 | 0.3310 | 0.3310 | **0.0000** | 0.0000 |
| checkerboard | 96 | 0.637 | 0.3700 | 0.3034 | 0.0666 | 0.0352 |
| checkerboard | 128 | 1.000 | 0.4480 | 0.3494 | 0.0986 | 0.0553 |
| checkerboard | 160 | 1.000 | 0.4790 | 0.3836 | 0.0954 | 0.0553 |
| `light-solid` (L 0.891) | 44 | 0.000 | 0.1328 | 0.1328 | **0.0000** | 0.0000 |
| `light-solid` | 96 | 0.637 | 0.3700 | 0.2323 | 0.1377 | 0.0708 |
| `dark-solid` (L 0.0117) | 44 | 0.000 | 0.0089 | 0.0089 | **0.0000** | 0.0000 |
| `dark-solid` | 96 | 0.637 | 0.3700 | 0.3539 | 0.0161 | 0.0087 |

Zero at every span at or below the knee, and it shrinks with the backdrop: over `dark-solid`
the correction is 0.0087 in encoded alpha, which is a quarter of one code of 255 (§"what is
not bit-identical" below).

## What the capture says — the thick spans, band `3-6` below, `1 − a`

Reference against the CSS tier before (the wave's own confirmation matrix,
`../sweep/matrix-confirm.json`) and after. Full table in `band-and-perceptual.out`.

| profile | cell | span | reference | before | after | error before → after |
| --- | --- | --- | --- | --- | --- | --- |
| 1x light | `checkerboard__rrect-md` | 96 | 0.1925 | 0.2439 | **0.1991** | 0.0514 → **0.0066** |
| 1x light | `checkerboard__rrect-ml` | 128 | 0.2195 | 0.3058 | **0.2350** | 0.0863 → **0.0156** |
| 2x light | `checkerboard__rrect-md` | 96 | 0.1904 | 0.2440 | **0.1986** | 0.0535 → **0.0082** |
| 2x light | `checkerboard__rrect-ml` | 128 | 0.2194 | 0.3045 | **0.2344** | 0.0851 → **0.0150** |
| 1x dark | `checkerboard__rrect-md` | 96 | 0.1525 | 0.1849 | **0.1586** | 0.0323 → **0.0061** |
| 2x dark | `checkerboard__rrect-md` | 96 | 0.1524 | — | 0.1570 | — → 0.0046 |
| 1x light | `photo__rrect-ml` | 128 | 0.1889 | 0.2508 | **0.2011** | 0.0619 → **0.0121** |
| 1x light | `photo__rrect-md` | 96 | 0.2013 | 0.2129 | 0.1803 | 0.0116 → **0.0211** |
| 2x light | `photo__rrect-md` | 96 | 0.2012 | 0.2139 | 0.1776 | 0.0127 → 0.0237 |
| 1x dark | `photo__rrect-md` | 96 | 0.1567 | 0.1607 | 0.1354 | 0.0040 → 0.0213 |

The checkerboard cells the finding was raised on land within 0.0066–0.0156 of the reference,
from 0.0514–0.0863. The span-160 cells are **holdout** and were not read: the holdout was read
once for this configuration in the sweep and is not read again here.

`photo__rrect-md` is the one place the fold over-corrects, and it is the residual the
derivation predicts rather than a surprise. `photo` is a structured backdrop, so the tone
statistic the tier keys on and the σ-40 blurred light the GPU tier actually copies are not the
same number; the fold subtracts what the statistic implies. It is the same mechanism that makes
`photo__rrect-ml` improve by 0.05 — the term being subtracted is larger there — and the sign of
the error at span 96 says the estimate is a little heavy on that bed. Recorded as the CSS
tier's own gap; it closes when the two-layer body lets the tier paint the lift instead of
folding it away.

## `ssimOutside` and `ssimMean`: no row falls, and the solids move most

Every row that moves, moves up. The largest rises are on `light-solid`, whose thick cells were
carrying the full correction with no structure to blur it:

| profile | cell | `ssimOutside` | `ssimMean` |
| --- | --- | --- | --- |
| 1x light | `light-solid__rrect-md` | 0.9265 → **0.9438** | 0.9755 → 0.9798 |
| 1x light | `light-solid__rrect-ml` | 0.9074 → **0.9371** | 0.9608 → 0.9711 |
| 2x light | `light-solid__rrect-md` | 0.9443 → **0.9551** | 0.9835 → 0.9860 |
| 2x light | `light-solid__rrect-ml` | 0.9345 → **0.9500** | 0.9747 → 0.9798 |
| 1x light | `checkerboard__rrect-md` | 0.8982 → 0.8984 | 0.8962 → 0.8963 |
| 1x light | `checkerboard__rrect-ml` | 0.8751 → 0.8759 | 0.8480 → 0.8482 |
| 1x light | `photo__rrect-ml` | 0.8973 → 0.8995 | 0.9460 → 0.9467 |

The checkerboard's own rise is small because SSIM's luminance term on a pitch-16 checker is
dominated by the squares, not by the shadow's level — which is why this wave reads the shadow
on X7's affine pair and not on SSIM, and why the pair's 8× improvement above shows as +0.0008
here. No `ssimOutside` or `ssimMean` row in the run falls.

## Thin cells, and what is and is not bit-identical

`byte-identity.out` hashes every capture against the confirmation run's.

- **Every thin cell is byte-identical**, at both scales and in both schemes: all
  `capsule-button` (span 44), `rrect-sm` (32) and `toolbar-group` cells, tinted and untinted.
  The rise is zero at and below `liftSpanMin`, so the fold is exactly the identity there.
- **Every dark-backdrop THIN cell is byte-identical**: `dark-solid__capsule-button` and
  `impulse__capsule-button`, tinted and untinted.
- **Dark-backdrop THICK cells are not.** `dark-solid__rrect-md` and `impulse__rrect-md` change,
  by **at most 1 code of 255** — `dark-solid__rrect-md` on 3.0% of its pixels with a mean
  absolute difference of 0.03 codes, `impulse__rrect-md` on 0.02% of its pixels. This is
  honest rather than a defect: over `dark-solid` the GPU tier's lift is not identically zero
  either (its backdrop is linear 0.0117, not black — claims §5.65 §3), so the fold removes a
  real 0.25-of-a-code difference between the tiers instead of pretending it away. Over a
  backdrop that is actually black, `V = 0` and both terms vanish. `ssimOutside` on
  `dark-solid__rrect-md` reads 0.8883 → 0.8884.
- 17 of 26 captures at 1x light, 17 of 26 at 2x light and 7 of 10 at 1x dark are byte-identical;
  every capture that changed is a thick surface (`rrect-md` at span 96 or `rrect-ml` at 128).

## The GPU tier is untouched

The only renderer-side change in `c27b372` is `DEFAULT_MATERIAL_PROFILE.outerShadow` moving to
the constants the sweep chose, and those are **exactly** what the confirmation run already
applied through `chosen-light.json` and `chosen-dark.json` — verified by comparing the committed
profile documents' `patch` blocks against the two chosen documents, which are identical key for
key and value for value. No shader, no law and no geometry moved, and no GPU capture was taken
in this run.

## Commands

The GPU was checked free before the run (`pgrep -f 'compare.ts|sweep.ts'` empty **and**
`lsof -i :5189` empty — a stale vite server on the harness's fixed port has outlived a run
twice and `pgrep` does not see it), held 22:02:53–22:04:26, and released. Every capture and the
matrix went to scratch; the main checkout's `results/matrix.json` and `web-captures/` were
never written.

    cd .claude/worktrees/w14-g1/packages/calibration
    S=/Users/new/.claude/jobs/5c70e47f/tmp/w14/css-fold

    VITREA_WEB_CAPTURES=$S/caps/1x-light npx tsx cli/compare.ts \
      --profile apple-macos-26.5-1x-light-standard \
      --material-profile profiles/apple-macos-26.5-1x-light-standard.json \
      --renderer css --set calibration,validation \
      --write-partial --out-matrix $S/matrix-css-fold.json

    # and three more into the same matrix, one profile per run:
    #   2x-light  --profile apple-macos-26.5-2x-light-standard  (light document)
    #   1x-dark   --profile apple-macos-26.5-1x-dark-standard   (dark document)
    #   2x-dark   --profile apple-macos-26.5-2x-dark-standard   (dark document)

`--set calibration,validation`: **holdout is not read here.** It was read once for this frozen
configuration in the sweep (`../sweep/README.md`) and nothing has been fitted since.

The two readings:

    python3 fold.py $S/matrix-css-fold.json > band-and-perceptual.out
    python3 identical.py \
      /Users/new/.claude/jobs/5c70e47f/tmp/w14/sweep/caps/confirm-1x-light-css \
      $S/caps/1x-light                                      # and 2x-light, 1x-dark

`fold.py` reads the X7 pair (`affineWeb` / `affineNative`, direction `below`, band `3-6`,
`slopeALinear` so that `1 − a` is the occlusion) and the two perceptual rows out of both
matrices; `identical.py` hashes the PNGs. Both are thirty lines over the schema and hold no
state, like `../sweep/read.py` beside them.

## Files

- `matrix-css-fold.json` — the four runs written into one matrix with `--write-partial`.
- `band-and-perceptual.out` — every non-holdout CSS cell: the reference's `1 − a`, the tier's
  before and after, and `ssimOutside` / `ssimMean` on both sides.
- `byte-identity.out` — the per-capture hash comparison against the confirmation run.
- `fold.py`, `identical.py` — the two readers.

## What the declaration must answer

1. **S6's miss is closed on the checkerboard and the cause is named** (claims §5.65 §2): the
   tier gap was the lift read through sRGB's decode, and the fix is a conversion of the shared
   profile. The declaration can state the CSS tier's thick spans as landing within 0.016 of the
   reference at both scales rather than 0.086 past it.
2. **`photo__rrect-md` is 0.021 low after the fold, from 0.012 high before it.** One multiply
   solved at a tone statistic cannot follow a structured backdrop's blurred light, and the
   declaration should carry that as the CSS tier's own residual with the two-layer body named
   as what closes it — not as a fitting question, since nothing here is fitted.
3. **Dark-backdrop thick cells move by one code.** The bit-identity the deferral assumed holds
   for every thin cell and for every dark-backdrop thin cell, and not for the two thick cells
   over a near-black backdrop, because the GPU tier's lift is not identically zero there
   either. It is worth one sentence rather than a floor.
