# W12 G1 — the reference's straight-edge displacement field (2026-09-03)

Instrument: `w12lib.py`, validated in `g0-instrument.md` (G0 passes: vitrea's own law recovered
to 0.35 / 0.33 CSS px at 1x / 2x, blur-before preferred 3.7–4.5×; contract X4 — every reference
table below carries that recovery beside it). Runs: `g1_cell.py` (spline D, per-edge fits, forms,
band/interior σ), `g1_extra.py` (two-term forms, k(u) ramp), `g1_dark.py` (dark-line term, the
[3, 40] window), `g1_pairs.py` (edge pairs), `g1_power.py` (the power form), the crossing table
and the holdout in this file's history. Data: `g1-native-*.json`, `g1x-*.json`, `g1d-*.json`,
`g1p-*.json`, `g1w-*.json`, `g1-crossings.json`, `g1-holdout.json`; tables `g1-tables.md`;
figures `g1-field.png` (the field), `g1-overlay-md.png` (reference against vitrea, data only),
`g1-profiles-native-rrect-md-p16-{1x,2x}.png` (data against model), `g1-native-*.png` (per cell).
Cells: native `checkerboard__{rrect-md,rrect-ml,rrect-lg}__rest` at 1x pitch 16 (canonical), 1x
pitch 32 and 64 (the W9 probe bed), 2x pitch 16 (canonical); spans 96 / 128 / 160, lens depth
20.8 on all three under vitrea's law.

**Claim.** The reference's lens along a straight edge is **one profile, independent of span
(96–160) and of scale (1x and 2x agree in CSS px), the same on all four edges**, and it is
steeper than vitrea's near the contour and equal to it deeper in: model-free boundary
crossings put it at **D = 34 at u ≈ 2, 29 at u ≈ 3, 24 at u ≈ 4, 12 at u ≈ 8, 0 at u ≈ 20 CSS px**,
against vitrea's 27 / 24 / 22 / 12.6 / 0. The non-parametric field is reproduced to the spline's
own pixel RMS by a three-parameter power law, **D(u) ≈ 42·(1 − u/23)³** (fitted range S 40–44,
L 20–24, p 2.6–3.0), which beats the landed quadratic, a physical circular/superellipse bevel
and a two-term inner/outer profile on the fit cells and on the held-out span at both scales. The
reference **blurs before it displaces** (the fold is as sharp as a source-space σ ≈ 1.2–1.5
compressed by the fold; blur-after cannot make it); the band's sharp σ is **≈ 1.45 CSS px at
both scales**, which at 1x is the interior's σ and at 2x is half the interior's (σ 2.5–3): at 2x
the band is sharper than the body behind it. There is **no dark line**: on a solid backdrop the
material reads exactly 1.000 of its deep level from u = 2.5 inward on every edge at both scales;
the line the eye saw inside the rim is the lens crossing a checker boundary at u ≈ 2.

## 1. The field, model-free: boundary crossings

Along a line normal to an edge the checker boundaries sit at known source depths s_k (top edge of
`rrect-md`: 4, 20, 36; bottom: 12, 28, 44; left/right: 16, 32; `rrect-lg` left/right: 12, 28, 44).
Where the mean profile of a parity group crosses the midpoint of its bright and dark plateaus at
depth u_k, the sampled source is at a boundary, so D(u_k) = s_k − u_k with no model at all
(rim-adjacent crossings at u < 1.9 that disagree with every fit by > 4 px are two rim artefacts
and are dropped). Native, pitch 16:

| span | scale | D(u) from crossings (u → D) | vitrea's own crossings (u → D) | vitrea's law at those u |
| --- | --- | --- | --- | --- |
| `rrect-md` | 1x | 1.7–2.0 → **34.2**; 2.8–3.0 → **29.1**; 4.05 → **24.0**; 7.9 → **12.1**; 19.8 → 0.2 | 2.6–2.7 → 25.3; 8.5 → 11.5; 20.1 → −0.1 | 25.4 / 11.6 / 0 |
| `rrect-ml` | 1x | 2.0 → 34.0; 3.0 → 29.0; 4.0 → 24.0; 7.9 → 12.1; 19.9 → 0.1 | 2.5–2.8 → 25.3; 8.4 → 11.6; 20.1 → 0 | — |
| `rrect-lg` | 1x | 2.0 → 34.0; 4.0 → 24.0 (three edges); 7.95 → 12.05; 19.85 → 0.15 | 2.6–2.8 → 25.3; 8.4 → 11.6; 20.2 → 0 | — |
| `rrect-md` | 2x | 2.2–2.4 → **33.7**; 2.7–2.9 → **29.2**; 4.0 → **24.0**; 7.55 → **12.4**; 20.3 → −0.3 | 2.6–2.7 → 25.3; 8.4 → 11.6; 20.2 → 0 | — |
| `rrect-ml` | 2x | 2.4 → 33.6; 2.9 → 29.1; 3.9–4.0 → 24.0; 7.4 → 12.6; 20.45 → −0.45 | same | — |
| `rrect-lg` | 2x | 2.4–2.6 → 33.5; 4.0–4.45 → 23.8; 6.9–7.4 → 12.85; 20.5–21.0 → −0.8 | same | — |

Every span and both scales sit on one curve. The instrument's reading of vitrea by the same
crossings reproduces vitrea's law to 0.1 px (25.3 against 25.4; 11.5 against 11.6), so the
crossing table is trustworthy at the same level. The single systematic scale difference: the
first crossing sits 0.5 CSS px deeper at 2x (2.3 against 1.85 on `rrect-md`) — one device pixel,
the rim's own width — and the fold's outer crossing 0.4 px shallower; elsewhere the two scales
agree within 0.5 px.

## 2. The field, non-parametric: the joint spline

Joint over the four edges (shared D; per-edge a, t, k, σ1), blur-before, λ 0.01; CSS px. The
constraint map (Σ over edges of |∂Y/∂s|) is in `g1-tables.md`; at pitch 16 it is ≥ 0.07 for
2 ≤ u ≤ 20 except a dip at u ≈ 5–6 (0.01–0.04), so the mid-band value there is smoothness-bridged
between crossings; pitch 64 on `rrect-lg` has no crossing in range (constraint ≤ 0.03
everywhere) and is the prior, not data — it is listed and then ignored.

| cell | u=1 | u=2 | u=3 | u=4 | u=6 | u=8 | u=10 | u=12 | u=14 | u=16 | u=18 | u=20 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| vitrea 1x (G0) | 29.8 | 26.8 | 24.2 | 21.8 | 16.9 | 12.5 | 8.8 | 5.8 | 3.4 | 1.7 | 0.5 | 0.0 |
| vitrea 2x (G0) | 30.0 | 26.9 | 24.2 | 21.7 | 16.9 | 12.5 | 8.9 | 5.8 | 3.4 | 1.7 | 0.6 | 0.1 |
| vitrea's law | 30.2 | 27.2 | 24.4 | 21.7 | 16.8 | 12.6 | 9.0 | 6.0 | 3.6 | 1.8 | 0.6 | 0.0 |
| `rrect-md` p16 1x | 36.6 | 32.2 | 28.0 | 24.1 | 17.1 | 11.7 | 7.9 | 4.9 | 2.7 | 1.3 | 0.5 | 0.1 |
| `rrect-md` p32 1x | 37.3 | 31.4 | 27.0 | 23.1 | 16.6 | 11.6 | 7.9 | 4.9 | 2.7 | 1.3 | 0.5 | 0.1 |
| `rrect-md` p64 1x | 37.6 | 31.7 | 27.3 | 23.5 | 17.1 | 11.9 | 7.9 | 4.9 | 2.8 | 1.2 | 0.5 | 0.3 |
| `rrect-md` p16 2x | 35.6 | 31.7 | 28.0 | 24.3 | 17.2 | 11.7 | 8.1 | 5.5 | 3.3 | 1.7 | 0.4 | 0.1 |
| `rrect-ml` p16 1x | 36.5 | 32.0 | 27.9 | 24.1 | 17.2 | 11.8 | 8.0 | 5.0 | 2.7 | 1.4 | 0.6 | 0.1 |
| `rrect-ml` p32 1x | 37.6 | 32.3 | 27.8 | 23.7 | 17.0 | 12.0 | 8.2 | 5.0 | 2.8 | 1.4 | 0.8 | 0.3 |
| `rrect-ml` p64 1x | 37.5 | 32.3 | 27.7 | 23.6 | 16.9 | 12.1 | 8.5 | 5.5 | 3.2 | 1.7 | 0.9 | 0.3 |
| `rrect-ml` p16 2x | 35.9 | 31.6 | 28.0 | 24.4 | 17.3 | 11.7 | 8.0 | 5.3 | 3.1 | 1.6 | 0.5 | 0.2 |
| `rrect-lg` p16 1x (holdout) | 36.0 | 31.3 | 27.3 | 23.7 | 17.2 | 11.6 | 7.2 | 4.0 | 1.8 | 0.4 | −0.1 | 0.0 |
| `rrect-lg` p32 1x | 38.3 | 33.3 | 28.9 | 24.9 | 17.5 | 11.8 | 8.0 | 5.5 | 3.4 | 1.7 | 0.6 | 0.1 |
| `rrect-lg` p16 2x | 42.9 | 34.0 | 28.0 | 23.6 | 17.0 | 11.9 | 8.1 | 5.4 | 3.3 | 1.7 | 0.6 | 0.0 |
| (`rrect-lg` p64 1x — unconstrained) | 33.9 | 30.7 | 28.3 | 26.1 | 22.0 | 18.4 | 15.0 | 12.0 | 9.4 | 7.0 | 4.9 | 3.1 |

Reference minus vitrea's law, the eleven constrained cells: **+5 to +7 at u = 1–2, +3.5 at 3,
+2 at 4, +0.3 at 6, −0.7 at 8, −1.0 at 10, −0.8 at 12, −0.6 at 14, −0.3 at 16, 0 at 20.** The
spline sits ~1–2 px under the crossings at u = 2–3 (32 against 34; 28 against 29), the penalty's
cost on the steepest part; with the fit window moved to [3, 40] (`g1d-*`, no near-contour data at
all) the same cells read 30 / 23.5 / 17.2 / 11.8 at u = 2 / 4 / 6 / 8 — the deeper field does not
depend on how the contour is treated. D(0) and D(1) are extrapolations (the fit starts at u = 1,
and the rim pixel is out); the crossing table is the near-contour authority.

**Inner width.** D < 1 px from u ≈ 17–18 and D < 10% of its peak from u ≈ 16 on every
constrained cell; the profile reaches zero at 19–20 CSS px on spans 96, 128 and 160 alike. Those
three spans all sit at or past `sizeSpanMax` (96), where vitrea's lens depth is the constant 20.8,
so this bed **cannot separate "a fixed width in CSS px" from "a width that scales with a
saturated lens depth"** — the small spans (`rrect-sm` L 8, `capsule-button` L 9.2 under vitrea's
law) are the discriminating cells and belong to the other G1 worker.

## 3. Blur order, and the band's σ

Joint RMS per edge (t/b/l/r), the two orders each with their own D, and blur-after with
blur-before's D held (is the preference a D artefact?):

| cell | blur-before | blur-after | after, before's D | after ÷ before |
| --- | --- | --- | --- | --- |
| vitrea md 1x (G0) | .0043/.0037/.0042/.0038 | .0238/.0142/.0158/.0167 | — | 4.5× |
| `rrect-md` p16 1x | .0413/.0409/.0249/.0214 | .0547/.0418/.0429/.0422 | .0386/.0373/.0321/.0297 | 1.4× |
| `rrect-md` p32 1x | .0168/.0170/.0099/.0104 | .0376/.0207/.0499/.0506 | .0183/.0182/.0484/.0491 | 2.9× |
| `rrect-md` p64 1x | .0161/.0095/.0046/.0046 | .0389/.0245/.0081/.0081 | .0229/.0235/.0079/.0079 | 2.3× |
| `rrect-md` p16 2x | .0502/.0522/.0259/.0262 | .0614/.0553/.0558/.0549 | .0423/.0456/.0448/.0442 | 1.5× |
| `rrect-ml` p16 1x | .0285/.0293/.0239/.0271 | .0423/.0300/.0349/.0369 | .0261/.0264/.0271/.0300 | 1.3× |
| `rrect-ml` p32 1x | .0197/.0255/.0082/.0079 | .0519/.0414/.0461/.0462 | .0261/.0285/.0454/.0456 | 3.0× |
| `rrect-ml` p64 1x | .0143/.0111/.0049/.0049 | .0274/.0637/.0568/.0568 | .0277/.0227/.0568/.0568 | 4.5× |
| `rrect-lg` p16 1x | .0244/.0244/.0209/.0233 | .0523/.0343/.0323/.0343 | .0229/.0221/.0188/.0213 | 1.6× |
| `rrect-lg` p32 1x | .0144/.0128/.0178/.0238 | .0282/.0222/.0254/.0306 | .0162/.0207/.0231/.0282 | 1.5× |
| `rrect-lg` p16 2x | .0318/.0340/.0303/.0319 | .0442/.0429/.0415/.0429 | .0291/.0356/.0347/.0361 | 1.3× |

Blur-before wins on every cell at every pitch. The margin is largest where the fold is best
resolved (pitch 32/64 left/right: 5–7×) and smallest at pitch 16 top/bottom, where the residual is
dominated by the steep first crossing (§1) that neither order places to the half pixel. Read
against the profiles (`g1-profiles-*.png`): the reference's transitions at the fold (u ≈ 8 and
u ≈ 20 on the top edge) are 2 px wide and its band plateau is flat; blur-after spreads them over
6 px and rounds the plateau, at any σ.

Band against interior, D held, blur-before (σ1 CSS px; k the heavy share):

| cell | band σ1 (u 1–22), t/b/l/r | band k | interior σ1 (u 24–40) | interior k |
| --- | --- | --- | --- | --- |
| `rrect-md` p16 1x | 1.44/1.44/1.61/1.61 | .43/.40/.32/.31 | 1.50 ×4 | 0 ×4 (heavy unidentifiable at pitch 16) |
| `rrect-md` p32 1x | 1.43/2.33/1.48/1.48 | .15/.33/.26/.29 | 1.73/1.44/4.5/4.5 | .52/.62/.40/.38 |
| `rrect-md` p64 1x | 1.47/1.50/1.50/1.50 | .32/.36/.41/.41 | 3.05/1.50/1.50/1.50 | .36/.27/.38/.38 |
| `rrect-ml` p64 1x | 1.77/1.42/1.48/1.48 | .35/.49/.31/.31 | 1.52/1.51/1.50/1.50 | .51/.46/.36/.36 |
| **`rrect-md` p16 2x** | **1.46/1.46/1.45/1.46** | .36/.32/.20/.29 | **2.46/1.81/2.51/1.83** | **.84/.85/.83/.85** |
| **`rrect-ml` p16 2x** | **1.49/1.48/1.48/1.48** | .41/.40/.46/.45 | **2.98/2.13/2.41/2.41** | **.85/.87/.86/.86** |
| **`rrect-lg` p16 2x** | 1.28/2.81/2.78/2.70 | .44/.83/.83/.83 | 3.83/3.06/3.78/2.41 | .85/.89/.87/.90 |

At 1x the band's sharp σ (≈ 1.45) is the interior's (≈ 1.5), and the heavy share where it is
identifiable (pitch 32/64) is 0.3–0.5 in both, i.e. W11c's body. **At 2x the band reads
σ 1.45–1.5 while the interior reads σ 2.5–3 (or the two-component form at k 0.85)** — the band
samples a sharper source than the body behind it. The per-line k(u) ramp the coordinator asked
for (`g1x-*`, k rising toward the contour) lowers the pitch-16 RMS by 5–20% with k_edge → 1.0 over
3–9 px, but that is the ramp absorbing the near-contour misfit of §1 (the same fits at pitch 64
send k_edge both ways), so the ramp is **inconclusive as parametrised**; the band-versus-interior σ
above is the clean statistic, and it says the 2x blur grows with distance from the edge from ≈ 1.5
to ≈ 3 CSS px. At 1x nothing grows, because the 1x interior is already sharp (the σ-1.25 leak).

## 4. The near-contour profile: no dark line

Native `light-solid__rrect-md__rest` and `__rrect-ml__`, mean line profile ÷ deep level (u 25–35),
every edge:

| scale | u = 0.25 / 0.5 / 0.75 / 1.0 / 1.25 | u = 1.5 | u = 2.5 … 12.5 |
| --- | --- | --- | --- |
| 1x (pixel centres 0.5, 1.5, 2.5 …) | 1.069 (u 0.5) | 1.038 | **1.000, 1.000, 1.000 …** on all four edges, both spans |
| 2x | 1.069 / 1.058 / 1.047 / 1.023 / 1.000 | 1.000 | **1.000 …** on all four edges, both spans |
| vitrea 1x / 2x | 1.073 / 1.073 → 1.037 | 0.990 | 0.990–0.991 to u ≈ 5.5, 0.999 by 8, 1.000 by 12 |

The reference's rim is a 1.5-px bright line (7% then 4% over the level) and then **exactly the
interior level from u = 2.5 on** — no transmission drop, no shadow, on any edge, at either scale.
The "thin dark line inside the rim" of §5.48 and the Fresnel advisory are therefore not features
of the material: on the checkerboard the profile dips to mid-grey at u ≈ 2 on *both* parities
(`g1-overlay-md.png`, top edge: 0.82 → 0.62 → 0.78), which is the sampled source crossing a
boundary (s = 36 at u ≈ 1.8, §1), and on the solid backdrop there is nothing there. A dark-line
term added to the model (`g1d-*`, multiplicative Gaussian dip, free depth/width) changes the
RMS by < 0.001 and fits δ ≈ 0.02–0.06 — noise. Vitrea, by contrast, carries a 1% darkening from
u ≈ 1.5 to 5.5 on solids (its inner shadow) that the reference does not have; recorded for the
rim/shadow owner, not fitted here.

## 5. Edge dependence: none beyond the instrument's resolution

Per-edge independent fits (`g1-tables.md`) differ near the contour by up to 7 px at pitch 32
(top/bottom 32–35 against left/right 25–26 at u = 2), but each single edge is unconstrained
exactly where it disagrees (left/right at pitch 32 have no crossing for u < 10). Edge-pair fits
(top+bottom share D; left+right share D; λ 0.003) where both pairs are constrained:

| cell | pair | D at u = 3 / 4 / 6 / 8 / 12 |
| --- | --- | --- |
| `rrect-md` p16 1x | tb / lr | 28.5 / 23.9 / 16.8 / 11.6 / 4.0 — 28.4 / 24.7 / 18.0 / 13.2 / 5.0 |
| `rrect-md` p32 1x | tb / lr | 28.7 / 24.1 / 16.6 / 11.4 / 4.6 — 28.8 / 24.3 / 16.8 / 11.9 / 4.9 |
| `rrect-ml` p32 1x | tb / lr | 27.9 / 23.2 / 15.8 / 10.7 / 4.3 — 27.6 / 23.7 / 16.8 / 11.9 / 4.9 |
| `rrect-md` p16 2x | tb / lr | 27.9 / 23.6 / 17.6 / 11.4 / 4.5 — 28.4 / 24.8 / 17.5 / 11.7 / 5.8 |

The pairs agree within 1.5 px wherever both carry a crossing, and the crossing table (§1) puts
the top, bottom, left and right boundaries on one curve directly. The light direction moves the
rim's brightness, not the lens. The cost of sharing D across all four edges is ≤ 0.004 RMS on any
edge against that edge's own best fit.

## 6. The forms, ranked

Pixel-model fits (joint over the four edges, blur-before; RMS is the mean over edges) and fits to
the recovered field (weighted by the constraint; px):

| cell | spline (14 knots) | **power S(1−u/L)^p** | quadratic S(1−u/L)² | bevel (L, T, n) | superbevel (+q) | two-term quad (4) | two-term smooth (4) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` p16 1x | .0321 | **.0321** — 42.1 / 23.2 / 2.99 (field .12 px) | .0360 — 41.4 / 18.1 (.53) | .0562 — 18.7 / 31.9 / **2.38** (2.86) | .0613 (2.81) | .0389 (.53) | .0504 (2.37) |
| `rrect-ml` p16 1x | .0272 | **.0270** — 42.0 / 23.5 / 3.02 (.09) | .0311 — 41.7 / 18.0 (.56) | .0458 — n **2.46** (2.72) | .0488 (2.64) | .0311 (.56) | .0411 (2.38) |
| `rrect-md` p16 2x | .0386 | **.0399** — 40.0 / 23.6 / 2.82 (.34) | .0419 — 38.5 / 19.2 (.58) | .0660 — n 2.06 (2.46) | .0694 (2.38) | .0420 (.58) | .0585 (2.19) |
| `rrect-ml` p16 2x | .0328 | .0353 (L, p ran to 37 / 5.8; field 41.7 / 24.8 / 3.17, .27) | .0465 (.64) | .0554 (2.15) | .0588 (2.06) | .0349 (.64) | .0490 (2.33) |
| `rrect-md` p32 1x | .0135 | **.0136** — 40.0 / 23.3 / 2.91 | .0141 — 32.6 / 19.7 (1.23) | .0723 (2.03) | .0226 (1.99) | .0138 (1.23) | .0285 (3.12) |
| `rrect-md` p64 1x | .0087 | **.0080** — 44.1 / 19.6 / 2.57 | .0087 — 45.0 / 16.2 (1.07) | .0247 (1.89) | .0156 (1.85) | .0084 (1.07) | .0162 (2.83) |
| `rrect-ml` p64 1x | .0088 | .0106 — 43.6 / 22.7 / 3.09 | .0143 (1.01) | .0498 (2.23) | .0351 (2.30) | .0119 (1.01) | .0195 (2.97) |
| `rrect-lg` p16 1x (holdout) | .0233 | **.0229** — 42.4 / 20.7 / 2.68 (.21) | .0232 — 42.2 / 16.4 (.32) | .0296 — n 1.81 (2.38) | .0295 (1.89) | .0225 (.32) | .0230 (2.07) |

- **The power law is the field.** With three parameters it reaches the 14-knot spline's pixel RMS
  on every constrained cell (Δ ≤ 0.002) and sits 0.1–0.3 px from the spline; S 40–44, p 2.6–3.0,
  L 20–24 with the usual (L, p) trade-off (L 19.5 / p 2.5 / S 44.5 threads the crossings of §1
  to 1 px and is within 0.005 RMS of L 23 / p 3 in the pixel model, which prefers the longer
  tail the spline also shows: D(12) ≈ 5, D(16) ≈ 1.5).
- **The quadratic is one parameter short**: 0.003–0.004 worse than the power law at pitch 16, and
  its S 41–42 / L 18 is the steep-near-contour, short-tail compromise.
- **The physical bevel fails**: n runs to the 2.5 bound, the field RMS is 1.5–2.9 px, and the
  reason is structural — Snell through a circular bevel peaks *inside* the contour and falls to
  h(0)·1.12 at the edge, while the measured profile peaks at the contour and decays like a
  steep power. No (L, T, n, q) reproduces D(2) = 34 with D(8) = 12. Recorded, not landed.
- **The two-term inner/outer profile adds nothing**: at four parameters it matches the quadratic's
  field RMS exactly (its outer term collapses to A_out ≈ 8–15 over H_out ≈ 0.6–2 px, a rim-pixel
  patch, or to 5 over 5 with no effect) and is worse than the three-parameter power law in the
  pixel model everywhere. No counter-signed or near-zero region exists for u ≲ 3: D(2) = 34 is the
  largest measured value on every cell, and the solid backdrop (§4) shows nothing there either.
  Whatever `inputOuterRefractionAmount` does in Apple's filter, at this control's working values
  it is not visible as a counter-displacement in the first 3 px.

**Holdout.** D fixed to a form fitted on `rrect-md` + `rrect-ml` (pitch 16, 1x); per-edge
(a, t, k, σ1) refitted on the held-out cells; mean pixel RMS:

| cell | power md+ml (42, 23.3, 3.0) | power crossing-anchored (44.5, 19.5, 2.5) | quadratic md+ml (41.5, 18.1) | vitrea's law (33.3, 20.8) |
| --- | --- | --- | --- | --- |
| **`rrect-lg` p16 1x** | **.0234** | .0242 | .0253 | .0271 |
| **`rrect-lg` p16 2x** | **.0344** | .0388 | .0404 | .0433 |
| `rrect-lg` p32 1x | .0183 | **.0178** | .0203 | .0208 |
| `rrect-md` p16 1x (fit) | .0334 | .0389 | .0371 | .0455 |
| `rrect-md` p16 2x (predicted) | **.0441** | .0494 | .0480 | .0576 |
| `rrect-ml` p16 1x (fit) | .0279 | .0324 | .0312 | .0360 |

The power law fitted at 1x on two spans predicts the third span and the 2x bed better than every
alternative, and vitrea's law is last on every row.

## 7. Answers to the questions asked

1. **Does D depend on the edge?** No, to 1.5 px where the data constrain it (§5); the apparent
   per-edge differences are where a single edge has no crossing.
2. **Does D peak at the contour or inside?** At the contour, as far as the data reach: D(1.7–2.0)
   = 34 is the largest measured value on every cell, the profile is monotone from there, and the
   solid backdrop shows no structure at u < 3 that a counter-signed term would leave. D(0)–D(1)
   are extrapolations under the rim (the power fits put D(0) at 40–44; the spline at 40–47).
3. **Is there a counter-signed or near-zero region for u ≲ 3?** No (§4, §6).
4. **Is the inner width one number across spans?** Yes at 19–20 CSS px on 96 / 128 / 160 — but all
   three sit at the saturated end of vitrea's size law, so "constant" and "∝ saturated lens depth"
   are not separable here; the small spans decide it.
5. **Does the 2x field equal the 1x field in CSS px?** Yes within 0.5 px, the first crossing
   0.5 px deeper at 2x (one device pixel).
6. **What σ does the band want, and is it the interior's?** ≈ 1.45 CSS px under blur-before at
   both scales; the interior's at 1x, half the interior's at 2x (§3).
7. **Which order?** Blur-before, every cell (§3).

## 8. What this says for G2 (advisory, for the parent)

Against the landed lens, the reference differs in the profile alone: `S(1 − u/L)^p` with
S ≈ 42 (2.0 lens depths of 20.8 rather than 1.6), L ≈ 23 (or 19.5 with p 2.5), p ≈ 3 — the same
order (blur-before), the same body at 1x, the same inner width to within 2 px. The visible gap of
§5.48 along a straight edge (`g1-overlay-md.png`) is the sum of three small things: the reference's
D is 5–7 px larger at u = 2–3 (the outer band shows a source 1.5 cells further in, and its first
crossing sits at u ≈ 2 where ours has none), its fold minimum sits ≈ 1 px deeper in the source
(16.7 against 17.6) so its band plateau clears the cell boundary that ours is lifted toward, and
its effective sharp σ is 1.2–1.5 where ours renders 1.6–1.7 against a declared 1.25. At 2x the
same three, plus a body that is σ 3 behind a σ 1.5 band. Landing the profile is one constant
change (the exponent) and one re-fit (S, L) under the W11c stops; the σ discrepancy and the 2x
body ramp are separate findings for their owners.

## 9. Limits

- Straight edges only; corners, small spans (where the lens depth is clamped) and the photo
  backdrop are the other G1 worker's.
- The bootstrap band over lines is degenerate (adjacent lines are replicas) and is not quoted;
  the constraint map is the uncertainty.
- The pixel RMS on the reference (0.02–0.05 at pitch 16) is 5–10× vitrea's (0.004) because the
  first crossing at u ≈ 2 is very steep (|ds/du| ≈ 3.6) and a half-pixel misplacement costs
  0.1 in luminance there; the spline's D at u = 2 is 1–2 px under the crossing for that reason,
  and the crossings, not the spline, are quoted for u ≤ 3.
- One rounding: the rim pixel (u = 0.5 at 1x; 0.25, 0.75 at 2x) is excluded from every fit.
