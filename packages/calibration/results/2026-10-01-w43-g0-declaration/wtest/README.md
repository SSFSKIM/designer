# W43 G0 (e): the w-test, drafted and rehearsed (not yet hashed)

Charter `docs/doperpowers/specs/2026-10-01-w43-glass-0-25-generation.md` v1.2, Design "The w-test",
clause 8, X46. This directory declares the free-side statistic, its support, its resolution and its
verdict rule, and runs the three rehearsals the Design asks for before the hash. Nothing here reads a
0.25 pixel; none exists yet. memo F's reading is folded in: the prediction is stated in all four
endpoints (`prediction.json`).

| file | what it is |
| --- | --- |
| `wtest.py` | the statistic, support, resolution, verdict, memo F's hook and the lifted-side reading |
| `w42frames.py` | the probe's 0.5 counterparts from `w42-archive`, guarded Reader, roles calibration + validation, `~/vitrea-w42/g1` denied; cached outside the repository |
| `rehearse.py` | rehearsals 3 (W42's 0.5 frames, fixes the support), 1 (synthetic LT) and 2 (a two-sided control) |
| `support.json` | the supported regions per statistic, support rule and endpoint, with their pixels; fixed at the hash |
| `rehearsal-r{1,2,3}.{txt,json}` | the rehearsals' outputs |

## The statistic

Under LT's composite, on the **free side** (light C ≥ W, dark C ≤ W) M − C = w (W − C) for any k, λ and
T. So per region r = (T25⁻¹(y25) − C) / (T50⁻¹(y50) − C) reads w(0.25) / w(0.5), predicted 0.5.

- **Regions.** One free-side and one lifted-side region per structured probe cell: the union of W42's
  region populations restricted to the free (or lifted) level of the cell's two levels, and to pixels
  where, for **every k in [1.4, 2.5]** (the span of W42's fitted points) under LT's maps, the narrow
  term is within 0.5 code of the level and the wide term at least 24 codes from it. The free level is
  the brighter in light and the darker in dark, whatever k, because W mixes the two levels.
- **y** is the region median per channel of the plurality frame; **T_x** is native, per channel and
  stratum, through the probe's own greys at x (W42's at 0.5); in dark at s ≥ 96 only ordinates ≤ 208.
  The region's M is the mean over channels of the per-channel inversions.
- **Resolution** dr = (dM25 + |r| dM50) / |M50 − C|, dM = (0.5 + 0.5 + interp) / slope: the median's
  half-code quantisation, the grey ordinate's, and the table's interpolation error estimated from the
  curvature of the three nearest ordinates.
- **Excluded before the read:** under 12 px; a censored 0.5 median (X21); |M50 − C| < 12 codes; in dark at
  s ≥ 96 an inverted M50 above 208; a predicted dr above 0.10, the resolution that separates 0.5 from
  0.7 by two dr.
- **Verdict** per endpoint: PASS iff |r − r_pred| ≤ dr on every supported, measured region (at least
  one); FAIL otherwise, with the measured r. A censored 0.25 median is UNMEASURED.
- **Lifted side**, never gated: r_lift = (w25 + λ25 (1 − w25)) / (w50 + λ50 (1 − w50)) gives λ25,
  set beside the two scalings of the declared Lighten ramp. In light they are 0.7595 (ratio) and
  0.7555 (difference) from λ50 0.868: **indistinguishable at any resolution the bed reaches**
  (Δr_lift ≈ 0.003), so the lifted reading tests the ramp's size, not its form.

## Rehearsal 3: W42's 0.5 frames fix the support (`rehearsal-r3.txt`, `support.json`)

The probe's 116 counterparts were read through the guarded Reader, roles calibration and validation
only. One counterpart has two states, and its plurality is read. These are the supported free-side
regions under the declared rule (k in [1.4, 2.5], median statistic), after `bp-p1-c32-rrect-64`
joined the probe (proposal P2, adopted before the hash):

| endpoint | supported | regions (pixels, observed \|M50 − C\|, predicted dr) |
| --- | ---: | --- |
| light active | 4 | P1 c32 capsule (221, 62.2, 0.057); P1 c32 rrect-64 (1,536, 58.4, 0.061); P1 c64 capsule (354, 38.0, 0.094); 32-pt bright square on rrect-md (832, 45.7, 0.080) |
| light receded | 2 | P1 c32 capsule (12, 47.0, 0.092); P1 c32 rrect-64 (42, 47.0, 0.092) |
| dark active | 3 | P1 c32 capsule (221, 61.8, 0.056); P1 c32 rrect-64 (1,536, 59.5, 0.060); P1 c64 capsule (116, 48.3, 0.081) |
| dark receded | 2 | P1 c32 capsule (12, 49.6, 0.081); P1 c32 rrect-64 (42, 48.5, 0.084) |

- **The test reads mostly t = 0.** Every supported region but light active's square lies on the
  capsule or rrect-64, where the active narrow opacity is 0. The pitch-16 checkers drop out
  everywhere: the narrow term never reaches the level inside a 16-pt square over the k span. Most
  rrect-md regions satisfy the model conditions but are under-resolved, at dr 0.14–0.53.
- **Why dr cannot be smaller with this statistic.** The capture is deterministic, so a region median
  and a grey ordinate are each one integer: half a code of quantisation each, at each position,
  divided by T's slope. A region needs \|M50 − C\| of about 30 codes in light and 20 in dark to reach
  0.10. In dark below 128 the sparse greys (0, 64, 128) add interpolation error.
- The least-squares k span alone (`ls-span`, [2.0, 2.25]) gives the same counts.

## Rehearsal 1: synthetic LT (`rehearsal-r1.txt`; the 40-seed record, run after memo F's window)

LT is rendered at k 2.138 and W42's λ50 per endpoint, at w 0.25 and 0.5. Each render goes through two
0.5 transfers: the measured native T, and memo C's denser curve. Each transfer has two 0.25 variants:
in light, unchanged and with the face fill 0.2 → 0.1; in dark, unchanged and with a 15 % high-end
compression. The captures are quantised, and the T tables are rebuilt from the synthetic greys at the
seven probe levels. There are 40 seeds per scenario.

Results for the median statistic under the declared support:
- **The null, r = 0.5** (64 scenarios): **every seed PASSes**, so the size is 0. \|r − 0.5\| ≤ 0.069
  and z = \|r − r_true\|/dr ≤ 0.82, so the declared dr is honest.
- **Power:** at r = 0.7 and at r = 1.0 (32 scenarios), **every seed FAILs**.
- **λ independence:** the free-side r moves by exactly 0 across λ25 ∈ {0.875 λ50, λ50 − 0.1125, 0.2,
  1.3}, in all 64 checks.
- **Under the ls-span support** the result is the same: null pass 1.0, z ≤ 0.91, alternatives fail.
- **The per-pixel mean statistic (P1) is not honest.** Its null pass rate falls to 0.95–0.975 and its
  z reaches 1.3. The median stays the declared statistic.

## Rehearsal 2: the two-sided linear control (`rehearsal-r2.txt`; 40 seeds)

- **With no hinge** (λ = 0 at both positions), the free and lifted readings agree within their dr:
  free 0.47–0.52, lifted 0.43–0.50.
- **With the hinge restored**, the lifted side reads its expected (w25 + λ25(1 − w25)) / (w50 + λ50(1 −
  w50)) within dr. λ25 is recovered to ±0.02 in the receded endpoints and to ±0.002 in the active
  ones.

## The prediction, stated from memo F (`prediction.json`)

`prediction_from_fold` feeds `prediction()` memo F's inputs that move between 0.25 and 0.5 on the
support's spans (`../memo-f/reading/fold.json`). None of those inputs sets C or W; the capture scale
moves only on rrect-lg, which is not support. Normal reads exactly 0.25 and 0.5. The prediction is
**stated in all four endpoints, r_pred = 0.5**.

## memo F's hook

`prediction(memo_f)` takes memo F's reading per endpoint: the moving fields at 0.25 against 0.5, and
Normal at both. It states the prediction only where none of the C inputs moves (blur radius,
opacities, distances, backdrop scale and margin) and none of the W inputs moves (fill radius, backdrop
scale and margin). It sets r_pred = Normal25 / Normal50. Face, MaxLuma and clamp inputs that move are
absorbed by native T per position. Lighten and Darken that move enter only the lifted reading.
