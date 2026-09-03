# W12 G0 — the instrument, validated on vitrea's own captures (2026-09-03)

**Claim.** A warp-recovery instrument reads the lens displacement field D(u) along a
straight edge of a checkerboard cell without assuming its shape, and on vitrea's own
`checkerboard__rrect-md__rest` GPU captures it recovers the analytic law
`D(u) = 20.8 × 1.6 × (1 − u/20.8)²` (lens depth 8 × 2.6 = 20.8 CSS px at span 96,
`lensRefractionGain` 1.6, `refractionScale` 1) to **0.35 CSS px at 1x and 0.33 at 2x**
over 2 ≤ u ≤ 20 when the four edges are fitted jointly, and prefers the blur-before
order (the shader's) by **3–5× in RMS**. Code: `w12lib.py`; run: `g0.py` → `g0.json`,
`g0-instrument.png`, `g0-tables.md`.

## 1. The instrument

- **Lines.** Every pixel column (top/bottom edge) or row (left/right) within ±pitch/4 of a
  checker column/row centre and within the straight part of the edge (4 px clear of the
  corner radius), from 4 px outside the contour to 40 px inside. Depth u is measured from
  the contour at pixel centres, in CSS px (device px ÷ scale).
- **The model is exact on a straight edge.** The checkerboard is separable,
  P = ½(1 − sx(x)·sy(y)), so any 2-D Gaussian blur of it restricted to a fixed column is
  a 1-D blurred square wave along the normal times a per-line *cross factor*
  e(σ) = (g_σ ∗ sx)(x), computed in closed form (erf). That holds for both orders as long
  as the warp is normal to the edge and depends only on u — the straight-edge case. The
  plate is analytic and asserted equal to the committed raster on every line used
  (self-test max |Δ| = 0.0 at 1x and 2x; the probe rasters likewise).
- **Body.** Two components, W11c's form: sharp σ1 (free) with weight 1 − k, heavy σ2 = 10
  CSS px with weight k (free). Per line-set: level a, transmission t, k, σ1.
- **Orders.** Blur-before: `Y = a + t·½(1 − Σ w_c e_c(σ_c) Q_c(s(u)))`, Q_c the blurred
  source wave sampled at s = u + D(u). Blur-after: the sharp wave is warped onto the screen
  grid and blurred along u (padding continues D(u<0) = D(0); a stated approximation).
  The pixel is integrated over its footprint on a fine grid (8 samples per CSS px).
- **D.** A clamped cubic B-spline, knots every 2 px from 0 to 28, the last three
  coefficients pinned so D = D′ = D″ = 0 at 28, a second-difference penalty λ (0.01) on
  the coefficients; s′ is free to change sign, so the fold is representable.
  `scipy.optimize.least_squares` (trf), three restarts (the landed law, zero, 1.3× the
  law).
- **Joint over edges.** The checker boundaries sit at different source depths on each
  edge (top: s = 4, 20, 36; bottom: 12, 28, 44; left/right of `rrect-md`: 16, 32), and a
  depth where the sampled source lies inside a flat cell carries no information about D.
  One edge alone therefore leaves parts of D to the prior; the four edges together, with
  a shared D and per-edge (a, t, k, σ1), constrain it through the fold. A *constraint
  map* — Σ over edges of the mean |∂Y/∂s| at each depth — is reported beside every D so
  a reader can see where D is data and where it is the prior.

## 2. Validation on vitrea (must pass before any reference reading — contract X4)

D(u) recovered against the analytic law, CSS px (`g0-tables.md` has every row):

| curve | u=1 | u=2 | u=4 | u=6 | u=8 | u=10 | u=12 | u=14 | u=16 | u=18 | u=20 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analytic law | 30.2 | 27.2 | 21.7 | 16.8 | 12.6 | 9.0 | 6.0 | 3.6 | 1.8 | 0.6 | 0.0 |
| **1x joint blur-before, λ 0.01** | 29.8 | 26.8 | 21.8 | 16.9 | 12.5 | 8.8 | 5.8 | 3.4 | 1.7 | 0.5 | 0.0 |
| **2x joint blur-before, λ 0.01** | 30.0 | 26.9 | 21.7 | 16.9 | 12.5 | 8.9 | 5.8 | 3.4 | 1.7 | 0.6 | 0.1 |
| 1x joint blur-after | 29.0 | 25.8 | 21.2 | 17.1 | 13.3 | 9.9 | 7.0 | 4.6 | 2.8 | 1.5 | 0.7 |
| 1x top edge alone | 28.5 | 25.3 | 20.7 | 16.5 | 12.5 | 8.9 | 6.0 | 3.6 | 1.8 | 0.6 | 0.0 |
| 1x bottom edge alone | 29.8 | 26.8 | 21.8 | 17.2 | 13.2 | 9.8 | 7.1 | 4.8 | 3.1 | 1.8 | 0.9 |
| 1x left edge alone | 30.0 | 27.1 | 22.4 | 17.8 | 13.4 | 9.3 | 5.9 | 3.5 | 1.8 | 0.8 | 0.4 |

| acceptance | 1x | 2x |
| --- | --- | --- |
| max \|D − law\| over 2 ≤ u ≤ 20, joint blur-before, λ 0.003 / 0.01 / 0.03 | 0.23 / **0.35** / 0.77 px (at u = 2) | 0.25 / **0.33** / 0.57 px |
| the same, one edge alone (top / bottom / left / right) | 1.85 / 1.34 / 0.99 / 0.82 | 1.70 / 1.26 / 0.73 / 0.62 |
| joint RMS, blur-before (t/b/l/r) | 0.0043 / 0.0037 / 0.0042 / 0.0038 | 0.0042 / 0.0043 / 0.0044 / 0.0040 |
| joint RMS, blur-after | 0.0238 / 0.0142 / 0.0158 / 0.0167 | 0.0136 / 0.0124 / 0.0177 / 0.0185 |
| order discrimination (after ÷ before, mean) | **4.5×** | **3.7×** |
| joint blur-after, max \|D − law\| | 1.38 px | 1.05 px |
| per-edge σ1 / k, blur-before (t/b/l/r) | 1.59/1.63/1.71/1.66 · 0.26/0.00/0.00/0.35 | 1.64/1.67/1.72/1.70 · 0.35/0.32/0.00/0.34 |

**Passes** (≤ 1 px on all four edges, both scales, blur-before preferred): with the joint
fit. **One edge alone does not pass on the top and bottom edges** — 1.85 and 1.34 px at
1x — and the constraint map says why: on the top edge the band's sampled source depth
runs 34 → 17 through the cell [20, 36) with one crossing, so u ≈ 3–6 (constraint
0.014–0.03 against 0.08–0.10 where a boundary is crossed) is the prior's. The joint fit
is therefore the instrument; single-edge D is reported only as a symmetry check.

**Two things the validation records about vitrea itself, for whoever owns them.** The
effective sharp σ of vitrea's capture reads **1.6–1.7 CSS px** against the profile's
`blurSigma` 1.25 (bilinear sampling of the displaced body and the pixel footprint are
modelled; the rest is the tier's), and its heavy share k reads 0.26–0.36 against the
law's 0.52 at span 96 (the σ-10 component leaks only 14% of its contrast at pitch 16, so
k is weakly identified here). Neither moves D.

## 3. Limits stated

- The bootstrap band (lines resampled with replacement) is degenerate — adjacent lines
  are near-replicas — and reads as ±0 px; it is kept in the JSON but the **constraint map
  is the honest uncertainty**.
- D(0) and D(1) are the spline's extrapolation: the fit window starts at u = 1.0 (the
  rim pixel at u = 0.5 is excluded at 1x; at 2x the pixels at 0.25 and 0.75 are).
- A constant t cannot express a transmission or level that changes with depth inside
  the band; the G1 findings add a multiplicative dark-line term where the reference
  needs it.
- λ trades smoothness for fidelity: 0.003 is closest on vitrea (0.23 px) but is left at
  0.01 for the reference so the fold region, where the constraint dips, does not ring.
