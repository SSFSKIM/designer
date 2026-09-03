# W12 G1 — the depth ramp and the kernel (2026-09-03, coordinator's addition)

Method (`g1b-ramp.py`, `ramp.json`, `ramp.out`, `sharp-ext.out`). Two questions from the
ShatteredGlass reading of Apple's `glassBackground` filter: is the sharp share a ramp in depth rather
than a law in span, and is the backdrop a quarter-scale buffer with one blur radius in buffer pixels.

## 1a. The sharp share by depth shell, native 1x, joint across the probe's pitch axis

At one pitch the two-component form is not identifiable (the σ 10 component leaves a pitch-8 or
pitch-16 checker no contrast, so k trades against t and the fit puts k at 0 or 1); joint across pitches
8 / 16 / 32 / 64 of the W9 probe, with (a, t, k) shared per 1-px shell and the landed D(u) applied in
the band (u < L) and D = 0 beyond, it is. Grid k ∈ {0, 0.05, …, 1}, σ 1.25 / 10. Shells inside the
band (u ≤ L + 4) are confounded by the landed law's shape (see `g1-corners.md`) and are listed for
completeness only.

| u | `rrect-md` k (a, t, rms) | `rrect-ml` k | `rrect-lg` k | `rrect-sm` k | `capsule` k |
| --- | --- | --- | --- | --- | --- |
| 6 | 0.75 (band) | 0.85 | 0.85 | 0.50 (0.261, 0.727, 0.025) | 0.70 (band) |
| 8 | 0.70 (band) | 0.80 | 0.80 | 0.50 (0.264, 0.719, 0.021) | 0.45 (band) |
| 10 | 0.40 (band) | 0.60 | 0.60 | 0.50 (0.263, 0.717, 0.019) | 0.20 (0.382, 0.449, 0.028) |
| 12 | 0.50 (band) | 0.60 | 0.55 | 0.60 (0.237, 0.751, 0.016) | 0.15 (0.390, 0.434, 0.020) |
| 14 | 0.50 (band) | 0.60 | 0.55 | 0.55 (0.255, 0.722, 0.014) | 0.10 (0.403, 0.412, 0.020) |
| 16 | 0.45 (band) | 0.55 | 0.50 | — | 0.10 (0.405, 0.408, 0.020) |
| 18 | 0.30 (band) | 0.45 | 0.50 | — | 0.20 (0.395, 0.417, 0.016) |
| 20 | 0.40 (band) | 0.50 | 0.55 | — | 0.15 (0.410, 0.395, 0.015) |
| 22 | 0.45 (0.416, 0.530, 0.010) | 0.55 | 0.55 | — | — |
| 24 | 0.45 (0.413, 0.538, 0.012) | 0.55 | 0.55 | — | — |
| 26 | 0.45 (0.416, 0.535, 0.012) | 0.55 | 0.55 | — | — |
| 28 | 0.50 (0.408, 0.548, 0.011) | 0.60 | 0.60 | — | — |
| 30 | 0.50 (0.406, 0.552, 0.011) | 0.60 | 0.60 | — | — |
| 32 | 0.50 (0.406, 0.553, 0.013) | 0.60 | 0.60 | — | — |
| 34 | 0.50 (0.408, 0.547, 0.012) | 0.55 | 0.65 | — | — |
| 36 | 0.55 (0.403, 0.557, 0.010) | 0.65 | 0.70 | — | — |
| 38 | 0.55 (0.403, 0.556, 0.011) | 0.60 | 0.70 | — | — |
| 40 | 0.55 (0.404, 0.553, 0.014) | 0.60 | 0.65 | — | — |

(`rrect-ml`'s deep rows: a 0.42–0.44, t 0.50–0.55, rms 0.009–0.014; `rrect-lg`'s: a 0.45–0.48, t
0.44–0.50, rms 0.012–0.017. Half-spans: md 48, ml 64, lg 80, sm 16, capsule 22.)

**Reading.** Beyond the band the heavy share k rises with depth inside every large cell — `rrect-md`
0.45 (u 22–26) → 0.50 (28–34) → 0.55 (36–40), `rrect-ml` 0.55 → 0.60 → 0.65, `rrect-lg` 0.55 →
0.60 → 0.70 — so there is a ramp in depth. But the curves do **not** collapse onto one curve in u: at
the same depth the three spans sit 0.05–0.10 apart (u 22: 0.45 / 0.55 / 0.55; u 30: 0.50 / 0.60 /
0.60; u 40: 0.55 / 0.60 / 0.65), and they do not collapse in u over the half-span either (md at
u/half 0.83 reads 0.55 where lg at 0.5 reads 0.65). The small spans sit apart from each other too:
`rrect-sm` 0.50–0.60 at u 6–14 against the capsule's 0.10–0.20 at u 10–20 — two cells of nearly the
same span (32 and 44) and the same interior level and the same sharp amplitude (t·(1 − k) ≈ 0.36 on
both), differing only in the heavy term's amplitude (0.36 against 0.06). The capsule's reading rests
on the pitch-32/64 cells, where its 22-px half-height holds under two periods of the pattern, so take
its k as "low, poorly conditioned" rather than 0.15; the shape (all corner) or the conditioning, not
the span, is what separates the two. The
answer to "ramp or span law" is **both, and neither alone**: a depth ramp of roughly +0.1 per 20 px
that rides on a per-cell offset the span (or the shape — the capsule is all corner) sets. Vitrea's
`kScatter` is a per-span constant (0.40 / 0.405 / 0.52 / 0.64 / 0.76 for sm / capsule / md / ml / lg)
— right on the large spans' deep values, high on the capsule by 0.25, and flat where the reference
ramps.

The ShatteredGlass working values (a blur-opacity ramp 0.5 → 1 from the edge to 10 px in) would put
the sharp share at 0 beyond u = 10; the measured sharp share is 0.45–0.55 at u 22–40 on `rrect-md`
and still 0.3 at u = 40 on `rrect-lg`. Whatever the ramp's true form, it is not those numbers.

## 1b. The sharp amplitude at pitch 16, both scales (the identifiable quantity at one pitch)

Per 1-px shell, `Y = a + amp·G_σs(P)` at the displaced position (landed D in the band), σ_s free in
{1.25, 1.5, 2, 2.5, 3, 4}; amp = t·(1 − k) is the sharp component's amplitude. Beyond the band with
D = 0 and the σ grid extended to 8 (`sharp-ext.out`), the deep interior:

| u | `rrect-md` 1x σ / amp | `rrect-md` 2x σ / amp | `rrect-lg` 1x σ / amp | `rrect-lg` 2x σ / amp |
| --- | --- | --- | --- | --- |
| 10 (band) | 1.25 / 0.276 | 2.0 / 0.341 | 1.25 / 0.170 | 3.0 / 0.319 |
| 14 (band) | 2.0 / 0.319 | 2.0 / 0.353 | 1.25 / 0.181 | 3.0 / 0.309 |
| 18 (band) | 1.25 / 0.318 | 2.0 / 0.382 | 1.25 / 0.193 | 4.0 / 0.443 |
| 24 | 1.25 / 0.268 | 3.0 / 0.425 | 1.25 / 0.166 | ≥ 8 |
| 28 | 1.5 / 0.262 | 3.0 / 0.423 | 1.25 / 0.153 | ≥ 8 |
| 32 | 1.25 / 0.244 | 3.0 / 0.388 | 1.25 / 0.146 | ≥ 8 |
| 36 | 1.25 / 0.224 | 3.5 / 0.453 | 1.25 / 0.134 | ≥ 8 |
| 40 | 1.25 / 0.217 | 4.0 / 0.496 | 1.25 / 0.125 | ≥ 8 |
| 44 | 1.25 / 0.206 | 5.0 / 0.686 | 1.25 / 0.112 | ≥ 8 |
| 52 | — | — | 1.25 / 0.098 | ≥ 8 |
| 60 | — | — | 1.25 / 0.078 | ≥ 8 |
| 68 | — | — | 1.25 / 0.061 | ≥ 8 |
| 76 | — | — | 1.25 / 0.041 | ≥ 8 |

Vitrea webgpu for the record: σ 1.5 (1x) / 1.5–2.0 (2x), amp 0.23–0.25 at every depth on `rrect-md`,
flat as the law says (`ramp.out`).

**At 1x the sharp component keeps its σ (1.25) and loses amplitude with depth, linearly**: `rrect-lg`
0.166 at u 24 → 0.041 at u 76, −0.0024 per px, extrapolating to ≈ 0.22 at the contour and to zero near
u ≈ 93 (past the cell's centre at 80); `rrect-md` 0.268 → 0.206 over u 24 → 44, −0.003 per px. A ramp
keyed to the distance from the edge in CSS px, on every large cell, spanning the whole half-span —
not a 10-px ramp.

**At 2x the sharp component does not vanish; its σ widens with depth instead**: `rrect-md` σ 2 in the
band, 3 at u 24–32, 3.5 at 36, 4 at 40, 5 at the centre; `rrect-lg` 3–4 in the band and past the grid's
top (8) from u 24 in. The prediction "the 2x sharp share vanishes beyond ≈ 12 CSS px while the 1x one
persists to ≈ 25" is **not** what the bed shows: at 2x the structure persists to the centre of
`rrect-md` (amp 0.5–0.7 at σ 4–5 — that is the reference's higher 2x transmission, `g1-body-2x.md`),
it is the *width* that ramps. The two scales ramp different things: share at 1x, σ at 2x.

## 2. The kernel, from the impulse cell

`impulse__rrect-md__rest`: 4-px bright squares on black, 64-px spacing; one square sits at the cell's
centre (u 44.5 at 1x, 44.2 at 2x) and two at u ≈ 16 (inside the band's tail, not used). Crop ±20 CSS
px around the central square, three models fitted by least squares with a free level: (i) one
Gaussian, (ii) sharp G_σs + heavy G_σh with free amplitudes, (iii) the quarter-scale tent — the plate
box-averaged by 4 device px on each of the 16 grid phases, one Gaussian in buffer px, bilinear
upsample with pixel-centre alignment.

| capture | observed peak above level / FWHM | (i) single σ CSS px, rms, r² | (ii) σs + σh, sharp amplitude share, rms | (iii) tent σ buffer px (= CSS px), rms, r² |
| --- | --- | --- | --- | --- |
| native 1x | 0.056 / 8 px | 3.0, 0.0028, 0.909 | 2.5 + 14, 0.18, **0.0022** | 0.5 (= 2.0), 0.0025, 0.922 |
| native 2x | 0.062 / 9 px | **5.0**, 0.0018, 0.969 | 3 + 6, 0.21, 0.0017 | 2.5 (= 5.0), 0.0018, 0.969 |
| vitrea 1x | 0.135 / 6 px | 1.5, 0.0030, 0.950 | 1.5 + 14, 0.19, **0.0017** | 0.5 (= 2.0), 0.0030, 0.949 |
| vitrea 2x | 0.122 / 5 px | 2.0, 0.0029, 0.950 | 1.5 + 12, 0.23, **0.0019** | 0.75 (= 1.5), 0.0029, 0.951 |

Row profiles through the centre (linear luminance, CSS px steps, native): 1x 0.429 … 0.434 (×12)
0.440 0.456 0.468 0.479 **0.485 ×4** 0.479 0.468 0.456 0.440 0.434 (×12) … 0.429 — a flat-topped
core 4 px wide with 4-px flanks, on a base 0.005 above the crop's edge that extends the full ±14 px;
2x 0.429 … 0.434 (×4) 0.440 0.445 0.451 0.451 0.456 0.462 0.468 0.479 **0.491 ×2** 0.485 0.474 0.462
0.462 0.456 0.451 0.445 0.445 0.440 0.434 … — one broad hump, no flat top, no separate base.

**Plainly:**

- The 1x kernel is a **narrow core on a wide base**: the two-component fit beats the single Gaussian
  (0.0022 against 0.0028) and the profile shows the base directly (+0.005 out to ±14 px, the σ 14
  term). The core reads σ 2.5 on a 4-px square where the checkerboard reads σ 1.25 — a 4-px square
  blurred by σ 1.25 keeps a flat top, which the profile has, so the two instruments agree on "a
  sharp core"; the exact σ is not resolvable from one impulse.
- The 2x kernel is **one Gaussian near σ 5 CSS px** (r² 0.969; the two-component fit gains 0.0001 and
  its "heavy" term is σ 6, i.e. not a second component). Not σ 3: the checkerboard's σ 3 is the inset
  interior's average and the σ scan (§1b) shows 3 at u 24 rising to 5 at the centre where the impulse
  sits. The two instruments agree at the same depth.
- **A quarter-scale buffer with one blur radius in buffer pixels does not explain both scales.** Its
  best buffer σ is 0.5 px at 1x and 2.5 px at 2x — a factor 5 apart, where one radius would be equal —
  and it predicts the 2x σ in CSS px to be *half* the 1x one, while the bed's 2x kernel is *wider* in
  CSS px (5 against 2–3) and wider still in device px (10 against 2–3). At 1x the tent (rms 0.0025)
  sits between the single Gaussian and the two-component form; at 2x it is the single Gaussian
  (σ_b 2.5 = 10 device px, where the tent's 4-px shape is invisible). What a quarter-scale buffer
  *would* explain is the 1x wide base and the sharp core if the tent were the core: the fit says the
  core is sharper than a 4-px tent at 1x (the two-component σs 2.5 with the flat top the tent cannot
  keep). So: the base and core at 1x are real, the 2x is a single wide blur, and the scale dependence
  is in the blur radius growing with the device scale (≈ 2–3 → 10 device px), the opposite of a fixed
  buffer-space radius.
- Vitrea reads its own law on both: σ 1.5 core + wide base (the σ 10 chain sampled at ≈ 0.5 share),
  scale-invariant in CSS px, as designed.

## 3. Numbers to carry

- 1x: heavy share k rises ≈ +0.10 from u 22 to 40 in every large cell, on per-cell offsets 0.45 / 0.55
  / 0.55 (md / ml / lg); the sharp amplitude falls linearly with depth (lg: −0.0024 per px, 0.166 → 0.041
  over u 24 → 76). Capsule k 0.10–0.20 against `rrect-sm` 0.50–0.60 at like depths.
- 2x: sharp σ ramps 2 → 3 → 4 → 5 CSS px from the band to `rrect-md`'s centre; `rrect-lg` ≥ 8 at
  every depth ≥ 24; amplitude does not vanish.
- Impulse: 1x core σ ≈ 2.5 (4-px square; flat top) + base σ ≈ 14 at 0.18 amplitude share; 2x one
  Gaussian σ 5.0 CSS px; the quarter-scale tent needs σ_b 0.5 (1x) against 2.5 (2x) buffer px.
