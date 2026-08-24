# S2 — Geometry field error & shader cost — Findings

> **Parent spec:** `docs/doperpowers/specs/2026-08-24-vitrea-liquid-glass-design.md`
> **Child id:** S2 — Geometry field error & shader cost spike
> **Parent pin:** commit `b756ccd`
> **Design inheritance:** §Geometry, §Gating spikes (S2) — binding. **Contract:** X8.
> **Blocks:** C3 (geometry kernel), C6 (WebGPU renderer).
> **Harness:** `spikes/s2-geometry-field/` — standalone TypeScript + vitest, no vitrea
> package dependencies, runnable as `pnpm test`. Intended for C3 to adopt as its
> error-bound regression base.
>
> This document proposes. It does not edit the parent spec; §"Impact on C3/C6 and X8"
> below is written for the parent's Decision Log and Revision Note to absorb.

---

## Verdict

**The error bound is met. Do not promote distance-mask atlases into v1.**

A parametric pseudo-SDF holds the following bound across the full required matrix
— smoothing {0, 0.2, 0.4, 0.6, 0.8, 1.0} × sizes {16, 32, 64, 120, 320, 600} px ×
aspect {1:1, 3:1, 8:1} × corner radius {0.15, 0.3, 0.5} of the short side, 324
shapes:

| band | field value error, max | field value error, p95 | gradient direction, max | gradient direction, p95 |
| --- | --- | --- | --- | --- |
| \|d\| ≤ 1 px | **0.166 px** | 0.142 px | **1.55°** | 1.20° |
| \|d\| ≤ 4 px | **0.166 px** | 0.150 px | **2.62°** | 1.73° |
| \|d\| ≤ 8 px | **0.170 px** | 0.156 px | **2.91°** | 2.55° |

The recommended family is **`rsupn`** — a radial-support field: the standard
analytic rounded-rectangle SDF whose corner radius becomes a low-order polynomial
in the corner angle, plus a first-order gradient normalization. It uses no
transcendentals, no branches in the corner algebra, and no texture lookups. On the
spec's mobile benchmark scene it costs 5% of the ~2 ms GPU budget with field
passes scoped to group bounds, or 31% under a deliberately pessimistic
whole-frame bound.

All cost figures come from one serialized benchmark run,
`bench/results.json` `generatedAt` 2026-08-24T14:29:14.670Z — see §4 for why the
provenance is called out.

The gradient figures are the gradient of the normalized field. A cheaper normal
is available and is identical on the contour but up to 4.26° off it; that
trade-off is priced in §6 under C6, because it is C6's to make.

The capsule limit is not approximated at all: it is **exact to machine
precision**, for every requested smoothing (§Capsule limit below explains why).

The `{center, size, radii, smoothing, thickness}` channel set **survives
unchanged**. No X8 revision is required. Three clarifications and one
recommendation are proposed instead — see §Impact.

**The finding that matters most is not the bound.** It is that the bound is
*smaller than the distance between the spec's chosen reference contour family and
Apple's actual corner*. The pseudo-SDF is not the limiting factor on geometric
fidelity; the choice of reference curve is. Numbers in §3.

---

## 1. What was measured, and why the numbers can be trusted

The optics read two different things off the field, so both are measured
separately:

- **field value** near the boundary — this is where the rim sits and how wide it
  reads. Reported in px.
- **field gradient direction** — this is the surface normal, which sets which way
  refraction bends. Reported in degrees.

Ground truth is *exact*, not a solver estimate. Two independent paths exist in the
harness and they check each other:

1. `exactSignedDistance` — closed form for line and arc segments; for cubics,
   dense seeding plus Newton refinement on `d/dt |C(t) − P|² = 0`, converging to
   machine precision. This is the "dense adaptive sampling + Newton refinement on
   a grid" reference the brief asks for.
2. `sampleBand` — the band sampler used for the sweep. It generates query points
   as `contourPoint + δ · outwardNormal`, so the reference distance is *exactly*
   `δ` and the reference gradient is *exactly* that normal, with no solver in the
   loop. The identity holds because a true signed distance field has `|∇d| = 1`
   and `∇d(P)` equals the outward unit normal at the closest contour point. The
   sampler enforces the medial-axis limit past which the identity breaks.

What makes the resulting figures load-bearing rather than plausible:

- The reference contour **closes to 1e-9** and is **G1 to 1e-15 rad** — the
  cubic/arc joins were derived consistently, not merely joined positionally.
- At smoothing 0 the reference degenerates to a plain circular rounded rectangle,
  and the exact solver agrees with the independent closed-form rounded-box SDF to
  **1e-9 over a grid**. Two implementations of the same shape agreeing to machine
  precision is the strongest single check available here.
- The sign from the closest-point normal agrees with **independent even-odd ray
  casting** at every grid point more than 1e-3 from the contour.
- The reported **max** is not the worst grid sample. It is locally refined by
  pattern search over (contour parameter, offset), so it is the continuous field's
  real worst case.
- The coefficient fit is an **exact Chebyshev (L∞) solve**, not a general
  optimizer. Pinning the corner offset to the true corner reach makes the
  objective linear in the coefficients, and the resulting residual
  **equioscillates across 11 alternating extrema at ±1.408e-3 r**. That is the
  textbook signature of an L∞ optimum: the reported deviation is the family's
  capability, not the optimizer's luck.

Disclosures, so the aggregation is not read as stronger than it is:

- `p95` is aggregated as *the worst shape's p95*, measured over a
  contour-uniform × offset-uniform sample measure. That measure over-weights
  corners relative to area, which is the right bias for a rim (a contour-length
  quantity) and a conservative one for the value statistic.
- Gradients are measured by central differences **of the field as returned**, so
  the figure characterizes the field a shader actually evaluates rather than a
  hand-derived analytic normal that might not match it. Samples sitting on a C1
  kink of the field are detected and excluded — and **0 of 324 shapes have any
  kink sample inside \|d\| ≤ 8**, so in practice nothing was excluded. At
  smoothing 0, where every family is exact, the measured gradient error is 0.014°;
  that is the measurement's own noise floor.
- The gradient figures do not depend on the differencing step. Sweeping it over
  four orders of magnitude (1e-2 to 1e-6 of the corner radius) moves the reported
  worst-case gradient error by **0.0015°** — from 2.9140° to 2.9141°. The field's
  `max(q, 0)` clamp introduces a C2 seam that a coarse central difference could
  in principle straddle and inflate; it does not. `src/diag-step.ts` reproduces
  this.
- Only **uniform corner radii** were swept. Per-corner radii are untested — see
  §Impact.

---

## 2. The candidates

All four share one corner-local setup. With half-extents `(W, H)` and a corner
offset `re`: `q = (|x| − (W − re), |y| − (H − re))`, and `qc = max(q, 0)`. Zero
positive components is the deep interior, one is the straight-edge region, two is
the corner sector. Every family reduces to the exact half-plane distance in the
straight-edge region, so **all four are exact against the straight edges by
construction** and the entire contest is inside the corner sector.

| id | family | fitted coefficients | transcendentals |
| --- | --- | --- | --- |
| A `roundbox` | standard analytic rounded-rect SDF, radius reparameterized by smoothing | 1 | none |
| B `superell` | superellipse exponent mapped onto the same corner, normalized by \|∇\| | 2 | 3 × `pow` |
| C `rsup` | radial-support field: `R(θ) = re · (1 + Σ kᵢ·sin(2θ)^(i+2))`, degree 5 | 5 | none |
| D `rsupn` | C plus the first-order normalization `d = (ρ − R) / √(1 + (R′/ρ)²)` | 5 (shared with C) | none |

Two design points in C/D are load-bearing and worth carrying into C3:

**The corner offset is the true corner *reach* `p = (1 + s_eff)·r`, not the radius
`r`.** Anchoring at `r` leaves the corner's "shoulder" — the zero-curvature run
where the cubic peels off the straight edge — outside the field's corner sector,
where no angular correction can reach it, and the field silently reports the
straight-edge distance there. With `re = p` the sector coincides exactly with the
true corner, `R(0) = R(π/2) = p` is exact, and the fit loses a degenerate degree
of freedom. `p` is already derived CPU-side, so this costs the shader nothing.

**`sin(2θ)` and `cos(2θ)` come out of the clamped corner vector by division, with
no `atan2` and no trigonometry**: `sin 2θ = 2·qc.x·qc.y / ρ²` and
`cos 2θ = (qc.x² − qc.y²) / ρ²`. That is what makes an angular correction
affordable at all. The basis starts at the *square* of `sin 2θ` because the true
radial support has `R′(0) = 0` — the corner leaves the straight edge both
tangentially and with zero curvature. Odd powers above that are included because
`R` is not an even function of θ about 0; a `sin²`-only basis converges visibly
more slowly.

### Contour deviation (scale-free)

Max |field| on the true contour, in units of the corner radius `r`. This is the
zero-level-set error, and it is the quantity that scales with shape size.

| smoothing | A `roundbox` | B `superell` | C `rsup` | D `rsupn` |
| --- | --- | --- | --- | --- |
| 0.00 | 4.6e-15 | 4.4e-15 | 4.6e-15 | 4.4e-15 |
| 0.20 | 1.325e-3 | 1.034e-3 | 3.145e-4 | 3.178e-4 |
| 0.40 | 4.926e-3 | 3.113e-3 | 5.629e-4 | 5.549e-4 |
| 0.60 | 1.033e-2 | 4.414e-3 | 5.405e-4 | 5.340e-4 |
| 0.80 | 1.712e-2 | 3.719e-3 | 1.377e-3 | 1.344e-3 |
| 1.00 | 2.490e-2 | 9.009e-4 | 3.379e-4 | 3.282e-4 |

| family | worst dev / r | at smoothing | px at r = 40 | px at r = 150 |
| --- | --- | --- | --- | --- |
| A `roundbox` | 2.490e-2 | 1.00 | 0.996 | 3.735 |
| B `superell` | 4.450e-3 | 0.65 | 0.178 | 0.668 |
| C `rsup` | 1.407e-3 | 0.85 | 0.056 | 0.211 |
| D `rsupn` | 1.383e-3 | 0.85 | 0.055 | 0.208 |

**Family A — the plain analytic rounded box, reparameterize the radius however
you like — misses by 3.7 px at a 150 px corner.** That is the single most
important negative result here: the field that a naive shader ships is not
adequate at vitrea's radii, and reparameterizing the radius cannot fix it,
because the error is a shape mismatch and not a scale mismatch.

Family B is both worse and more expensive: a superellipse has no straight
segment, so no exponent reproduces the corner's zero-curvature shoulder.

### Band error, full matrix

| family | value max | value p95 | grad max | grad p95 | max \|∇\|−1 |
| --- | --- | --- | --- | --- | --- |
| **\|d\| ≤ 1 px** | | | | | |
| A `roundbox` | 2.2436 | 2.2210 | 7.093° | 6.630° | 0.0000 |
| B `superell` | 0.8063 | 0.7896 | 2.945° | 2.465° | 0.0271 |
| C `rsup` | 0.1919 | 0.1530 | 2.281° | 1.477° | 0.0785 |
| **D `rsupn`** | **0.1663** | **0.1415** | **1.545°** | **1.201°** | 0.0203 |
| **\|d\| ≤ 4 px** | | | | | |
| A `roundbox` | 2.2436 | 2.2339 | 7.093° | 6.521° | 0.0000 |
| B `superell` | 0.8063 | 0.7909 | 7.261° | 2.917° | 0.0658 |
| C `rsup` | 0.3690 | 0.2474 | 4.258° | 3.336° | 0.0785 |
| **D `rsupn`** | **0.1663** | **0.1503** | **2.622°** | **1.728°** | 0.0273 |
| **\|d\| ≤ 8 px** | | | | | |
| A `roundbox` | 2.2436 | 2.2352 | 7.093° | 6.402° | 0.0000 |
| B `superell` | 0.8063 | 0.7917 | 13.043° | 6.124° | 0.0763 |
| C `rsup` | 0.5736 | 0.4019 | 4.258° | 3.689° | 0.0785 |
| **D `rsupn`** | **0.1697** | **0.1556** | **2.914°** | **2.553°** | 0.0273 |

`|∇|−1` is the eikonal defect. It matters independently of the value error:
refraction strength is read off the field's slope, so a field whose gradient
magnitude drifts is not usable as a distance even where its zero set is right.
Family C's 7.9% defect is exactly what family D's normalization removes, and it is
why D — not C — is the recommendation despite the two sharing a coefficient table
and a zero level set. The normalization costs one `rsqrt` and buys a 3.4×
reduction in band value error.

### Where the worst cases sit

| smoothing | shapes | value max | value p95 | grad max | grad p95 |
| --- | --- | --- | --- | --- | --- |
| 0.00 | 54 | 0.0000 | 0.0000 | 0.014° | 0.000° |
| 0.20 | 54 | 0.0594 | 0.0571 | 1.224° | 1.057° |
| 0.40 | 54 | 0.1080 | 0.0993 | 2.217° | 1.829° |
| 0.60 | 54 | 0.1175 | 0.0948 | 2.294° | 2.013° |
| 0.80 | 54 | 0.1663 | 0.1556 | 2.728° | 2.364° |
| 1.00 | 54 | 0.1697 | 0.1556 | 2.914° | 2.553° |

The two bounds are set by opposite ends of the size range, and both worst cases
are benign for the optics:

- The **value** worst case (0.166 px in the rim band) is at **large radii** — a
  600 px shape with a 180 px corner. Gradient error at that same point is only
  0.86°. This follows the r-linear contour deviation.
- The **gradient** worst case (2.914° at \|d\| ≤ 8) is at the **smallest shapes** —
  8 px away from a 2.4 px-radius corner, i.e. more than three radii outside a
  16 px chip, where refraction reads essentially nothing. Inside the rim band the
  same shapes are well under 1.6°.

The band error does **not** grow without bound with shape size, because the band
is a fixed 8 px while the corner grows:

| size px | r px | value max | value max / r | grad max |
| --- | --- | --- | --- | --- |
| 16 | 2.40 | 0.1310 | 5.458e-2 | 2.728° |
| 32 | 4.80 | 0.1560 | 3.249e-2 | 2.619° |
| 64 | 9.60 | 0.1485 | 1.547e-2 | 1.974° |
| 120 | 18.00 | 0.1267 | 7.039e-3 | 1.545° |
| 320 | 48.00 | 0.1171 | 2.439e-3 | 1.513° |
| 600 | 90.00 | 0.1523 | 1.693e-3 | 1.392° |

Absolute band error stays in a **0.12–0.17 px** envelope across three orders of
magnitude of size. C6 can treat ~0.17 px as a flat budget rather than a
size-dependent one.

### Capsule limit

| family | requested smoothing | s_eff | value max | grad max |
| --- | --- | --- | --- | --- |
| A `roundbox` | 0 … 1 (all) | 0.000000 | 5.0e-13 | 1.4e-2° |
| B `superell` | 0 … 1 (all) | 0.000000 | 4.9e-13 | 1.4e-2° |
| C `rsup` | 0 … 1 (all) | 0.000000 | 5.0e-13 | 1.4e-2° |
| D `rsupn` | 0 … 1 (all) | 0.000000 | 4.9e-13 | 1.4e-2° |

This is not a lucky result, it is structural, and C3 should know why. Figma's
**rounding-and-smoothing budget** clamps effective smoothing to `budget/r − 1`,
where the budget for a uniform radius is half the short side. At the capsule limit
`r` equals the budget, so effective smoothing is forced to **exactly 0** — a
capsule is always a true stadium, and every family is exact on it. The same clamp
means smoothing 1.0 is only reachable when `r ≤ ¼` of the short side, which is
what keeps the worst-case radius (and hence the r-linear error) bounded.

The clamp is continuous in size (`d s_eff / d size = 1/r` while clamped, 0 after),
so it is safe under morph interpolation. That is asserted in the suite.

---

## 3. The reference itself is the binding constraint

The spec seeds `smoothing` from Figma-squircle fitting, so Figma's construction is
the primary reference and everything above is measured against it. But Figma's
family is *not* Apple's curve, and vitrea's stated tie-breaker is fidelity. So the
harness carries Apple's actual corner too.

**Apple's `.continuous` corner**, recomputed in the harness from a macOS 26
`CGPath` dump and asserted from the control points alone:

- Edge reach **1.528665 r**. This is not reverse-engineered folklore: Apple
  publishes it as `+[CALayer cornerCurveExpansionFactor:]` for
  `kCACornerCurveContinuous`.
- **Three cubics per corner**, no arc primitive — but the middle cubic *is* a
  genuine circular arc. Its control-handle length matches the exact arc-as-cubic
  identity `(4/3)·tan(sweep/4)·R` to **1.5e-7**, at radius **0.931253 r**, centre
  **0.950002 r**, sweep **50.0000°**. (The handle identity is the real proof; the
  radius and centre alone could be a coincidence of symmetry.)
- **G2 — zero curvature — where the corner meets the straight edge.** This is the
  join that reads visually, and Apple gets it right.
- **A 2.4532° tangent break at both shoulder/arc joins.** Apple's own path is not
  even G1 there. "Continuous curvature" holds at the straight-edge join and
  nowhere else.
- Radius saturates at **r/side = 0.327083**, a different budget policy from
  Figma's.

That 2.4532° figure is the most useful number in this section, because it
**calibrates the gradient budget**. The reference curve vitrea is chasing carries
a 2.45° normal discontinuity of its own. A pseudo-SDF whose gradient error peaks
at 1.55° in the rim band is *below the reference's own normal discontinuity*.
Chasing further precision on the normal is chasing an artifact of the target.

**How far Figma's family can get from Apple**, two-sided Hausdorff, units of r:

| Figma smoothing | Hausdorff / r |
| --- | --- |
| 0.00 | 1.380e-2 |
| 0.20 | 1.373e-2 |
| 0.40 | 1.054e-2 |
| 0.60 | 3.613e-3 |
| **0.66** | **1.960e-3** |
| 0.80 | 7.830e-3 |
| 1.00 | 1.933e-2 |

Best match **smoothing = 0.66** at 1.960e-3 r (0.6566 with the radius free to
scale by 0.9988, at 1.749e-3 r). Two consequences:

1. **The widely cited "Figma smoothing 0.6 = iOS" is not the best fit.** 0.6 is
   nearly 2× worse than 0.66. This directly answers one of the spec's named
   delegated unknowns ("corner smoothing values") with a number, ahead of C7.
2. **The reference gap (1.96e-3 r) exceeds the field's own worst-case contour
   deviation against that reference (1.38e-3 r).** The intermediate family costs
   more accuracy than the field approximation does.

Measured end-to-end against Apple's corner — the comparison that decides it:

| field configuration | value max | value p95 | grad max | grad p95 |
| --- | --- | --- | --- | --- |
| D `rsupn`, fit to **Apple directly** | **0.104 px** | 0.090 px | **1.752°** | 0.871° |
| D `rsupn`, fit to Figma at smoothing 0.66 | 0.670 px | 0.626 px | 2.316° | 1.393° |
| A `roundbox`, best radius scale | 2.070 px | 2.044 px | 4.505° | 3.608° |

**Routing through Figma's family costs 6.4× the value error of fitting the same
field directly to Apple's curve.** The radial-support family is
reference-agnostic: `R(θ)` fits whatever corner it is given. Fit against Apple's
own corner it reaches **6.06e-4 r** contour deviation — better than it fits
Figma's family, and 3× closer to Apple than Figma's best smoothing can get.

That residual barely improves with a higher-order basis (6.06e-4 → 6.02e-4 for one
extra term), because it is limited by Apple's own 2.45° tangent break rather than
by the polynomial. The field is as close to Apple's curve as a smooth field can
usefully get.

---

## 4. Shader cost

**Provenance.** Every cost figure below comes from one run:
`spikes/s2-geometry-field/bench/results.json`, `generatedAt`
**2026-08-24T14:29:14.670Z**, produced with that process verified as the sole GPU
client. Regenerate the tables from it with `npx tsx bench/report-cost.ts` rather
than trusting this transcription.

**Setup.** Headless Playwright Chromium 151.0.7922.34, WebGPU on an Apple
`metal-3` adapter. Fullscreen-triangle render pass, `rgba8unorm` target, 256
shapes in a storage buffer, 15 repetitions per point, ≥ 50 ms per measurement, 3
discarded warmup iterations. **GPU `timestamp-query` was available and used**;
wall-clock timing was recorded alongside at every point and agrees with it to
within about 1.5%, so the fallback path was never needed and the two methods
corroborate each other.

Five things make these numbers a measurement rather than a demo, and each was a
way to get a confident wrong answer:

- **The first headless attempt was rejected**, not used. Playwright's default
  `chromium_headless_shell` does expose `navigator.gpu`, but only as Google
  SwiftShader, a CPU software rasterizer — roughly 100× slow, and output that
  looks exactly like a benchmark. The harness now gates on a hardware adapter and
  falls through to the full Chromium binary, which is what produced every number
  here.
- **Chrome quantizes timestamp-query results to 100 µs by default**, which would
  swamp measurements of this size. The run passes
  `--disable-dawn-features=timestamp_quantization`. Without it the fine-grained
  slope is unrecoverable.
- **Cost is extracted as a slope, not a single timing.** The fragment shader
  evaluates the field K times per pixel for K ∈ {1, 2, 4, 8, 16, 32}, and cost per
  evaluation is the least-squares slope of time against K. That subtracts
  render-pass fixed cost instead of attributing it to the field.
- **The compiler did not hoist the repeated evaluations.** This is the property
  whose failure would silently invalidate everything: `r² ≥ 0.9985` on every slope
  fit, a 16–28× rise from K=1 to K=32, and ≥ 98% of the K=32 time in the marginal
  term. The harness gates on it explicitly and refuses to report a slope that does
  not scale.
- **Additive blending had to be enabled** or this GPU's tiler culled the repeated
  draws within a pass and produced physically impossible times. Pass timing also
  uses paired passes of N and 2N draws, `(T(2N) − T(N)) / N`, which cancels the
  pass fixed cost exactly.
- **Cost per evaluation per pixel agrees between the two resolutions** to within
  0.7% for every variant and 0.2% for four of the five, across a 1.75× difference
  in pixel count. That was not designed as a check and is the strongest single
  piece of evidence that what is being measured is per-pixel work rather than
  fixed overhead.
- **The GPU had exactly one client.** This is not pedantry: an earlier pair of
  overlapping benchmark processes on this machine inflated the small-quantity
  variants by up to 7% and made the family-D-versus-family-A ratio wander between
  3.3× and 3.9×. In the serialized run every net cost agrees to three significant
  figures across two independent resolutions, and the ratio is 3.9× at both. That
  cross-resolution agreement is the evidence the run is clean; a contended run
  does not produce it. An earlier solo run agrees with this one on family D to
  within 0.12%.

Two limitations of the workload, so it is not read as more general than it is.
The shape index is **pixel-invariant**: every lane in a wave reads the same
instance, which is what a per-group field pass iterating its group's instances
actually does, but it means these figures do not price a divergent per-lane
gather. And family B is measured on its **expensive branch** — most benchmark
pixels land where both corner components are positive and take all five `pow`
calls — which is the fair comparison for a corner-heavy workload but is family
B's worst case.

### Which candidates were ported

All four, plus a null baseline. The two most accurate — C and D — share a
coefficient table and a zero level set, so pricing them against each other does
not choose between them on accuracy; it prices the normalization that separates
them, which turns out to be the useful thing to know. A and B are carried because
they are what someone reaches for instead: A is the analytic box that every
rounded-rectangle shader already ships, and B is the superellipse usually
suggested for "squircle on the GPU".

### Cost per field evaluation per pixel

| variant | mobile 1170×2532 | net of loop | desktop 2880×1800 | net of loop |
| --- | --- | --- | --- | --- |
| `null` (loop + storage load only) | 0.00903 ns | — | 0.00904 ns | — |
| A `roundbox` | 0.01350 ns | 0.00447 ns | 0.01349 ns | 0.00445 ns |
| C `rsup` | 0.01872 ns | 0.00970 ns | 0.01874 ns | 0.00970 ns |
| **D `rsupn`** | **0.02640 ns** | **0.01737 ns** | **0.02644 ns** | **0.01740 ns** |
| B `superell` | 0.03243 ns | 0.02340 ns | 0.03266 ns | 0.02362 ns |

`net` subtracts the `null` variant, isolating the field arithmetic from the
per-iteration instance load and accumulate that any real shader also pays.

Family D's per-pixel cost is **identical at both resolutions to three significant
figures**. The cost is purely per-pixel ALU with no resolution-dependent term,
which is what makes it safe to extrapolate to scenes below.

### One full-screen field pass, one evaluation per pixel

| variant | mobile (2.96 Mpx) | desktop (5.18 Mpx) |
| --- | --- | --- |
| A `roundbox` | 0.0400 ms | 0.0699 ms |
| C `rsup` | 0.0555 ms | 0.0971 ms |
| **D `rsupn`** | **0.0782 ms** | **0.1371 ms** |
| B `superell` | 0.0961 ms | 0.1693 ms |

### Against the spec's benchmark scenes and ~2 ms GPU budget

The spec's mobile scene is 8 surfaces in 3 groups; the desktop scene is that at
2×. Group rendering goes through a per-group field pass, so the field is
evaluated once per instance per covered pixel. Two bounds, because the realistic
figure depends on how tightly the group field passes are scoped:

| | mobile, share of 2 ms | desktop, share of 2 ms |
| --- | --- | --- |
| **D `rsupn`, pessimistic** — all 8 surfaces at *every* pixel of the frame | 0.626 ms — **31%** | 1.096 ms — **55%** |
| A `roundbox`, same pessimistic bound | 0.320 ms — 16% | 0.560 ms — 28% |
| C `rsup`, same pessimistic bound | 0.444 ms — 22% | 0.777 ms — 39% |
| B `superell`, same pessimistic bound | 0.769 ms — 38% | 1.354 ms — 68% |
| **D `rsupn`, scoped** — field passes covering ~15% of the frame in total | **0.094 ms — 5%** | **0.164 ms — 8%** |

The pessimistic row is a deliberate over-estimate: it assumes every group's field
pass covers the entire frame, which defeats the purpose of scoping a field pass to
its group's bounds. Real toolbars, buttons and menu platters cover a small
fraction of a 390×844 viewport. **The scoped row is the number to plan with; the
pessimistic row is the number that proves the choice is safe even if scoping is
never implemented.**

The honest cost of the accuracy: family D is **3.9× family A's net field
arithmetic** at both resolutions, which at the pessimistic bound is +0.31 ms on
mobile and +0.54 ms on desktop. That is a real fraction of a 2 ms budget, and it
buys the difference between 2.24 px and 0.17 px of field error. Family B costs
*more* than D while being 4.7× less accurate, so the pow-based superellipse is
dominated on both axes and can be dropped from consideration entirely.

### What the normalization costs, and the cheaper tier it implies

Families C and D differ only by the first-order `|∇|` normalization, so the gap
between them is that term's price:

| | cost | value error, \|d\| ≤ 8 | gradient error, \|d\| ≤ 8 | \|∇\|−1 |
| --- | --- | --- | --- | --- |
| C `rsup` | 0.00970 ns net | 0.574 px | 4.258° | 0.0785 |
| D `rsupn` | 0.01737 ns net | **0.170 px** | **2.915°** | 0.0273 |

The normalization **roughly doubles family C's field arithmetic** (1.79×) and is
about 1.7× the cost of an entire plain rounded box on its own — +0.023 ms per
full-screen mobile pass, or +0.18 ms (9% of the budget) at the pessimistic
8-surface bound. In exchange it buys 3.4× on value error, 1.5× on gradient error,
and takes the eikonal defect from 7.9% to 2.7%.

That is clearly worth paying, and family D remains the recommendation. But it also
means **family C is a coherent cheaper tier rather than a rejected candidate**:
same coefficient table, same zero level set, same authored channels, 29% less
total cost, degrading to 0.57 px and 4.26°. If the quality governor ever needs to
degrade *within* the texture tier — which the spec's §Performance envelope
explicitly prefers over switching tiers — dropping the normalization is a
one-branch, one-uniform change with a measured cost and a measured penalty. It is
the natural first governor step.

**Caveat on family C, stated because it bounds what the above supports.** Family
C's *error* figures come from the TypeScript field in `src/candidates.ts`, which
is under the committed test suite. Its *cost* figure comes from the WGSL
`sd_rsup`, which was verified against that TypeScript by inspection only — unlike
family D and family A, it was **not** put through the f32 cross-check below. The
cost number is a cost number and does not depend on the port being bit-accurate,
but **C6 must run the f32 cross-check on `sd_rsup` before shipping family C as a
governor tier.** Extending `bench/make-f32-check.ts` to emit a third expected
column is the whole job.

### f32 precision does not eat the error budget

The declared bound is ~0.17 px, and family D evaluates a degree-5 polynomial with
alternating coefficients up to ±3.3, so f32 cancellation is a real thing to check
rather than assume. The shader's f32 output was compared against f64 evaluation of
the identical arithmetic over 5,535 points on and around the true contour of three
shapes:

| candidate | max abs diff | p99 | p50 | max relative to corner reach |
| --- | --- | --- | --- | --- |
| D `rsupn` | **4.08e-5 px** | 1.91e-5 px | 1.91e-6 px | 4.82e-7 |
| A `roundbox` | 3.03e-5 px | 1.60e-5 px | 1.80e-6 px | 4.79e-7 |

**f32 costs 4.1e-5 px — 0.024% of the declared bound**, and family D is no worse
than the single-subtraction family A in this respect. The polynomial's
conditioning is a non-issue at this basis order. It would stop being a non-issue
at order 7, where coefficients reach ~56 (see §5).

This check does double duty, and the second job is arguably the more important
one: agreement at the 1e-5 level also **validates the WGSL port itself**. The
TypeScript `rsupn.evalAt` is written as a line-for-line mirror of `sd_rsupn` —
branchless, same clamp, same Horner order — so a transcription error in the shader
would show up here as a gross disagreement, not a rounding difference. The error
tables in §2 are computed from the TypeScript field; this is the evidence that the
shader C6 will ship computes the same function. Family C has no such evidence yet,
which is exactly the caveat above.
---

## 5. Recommendation

**Adopt family D (`rsupn`). Do not promote distance-mask atlases.**

The parent spec asks for "a declared, measured error bound" without naming a
number, so S2 owes both the bound and the argument that it is sufficient. The
argument has three parts, in decreasing order of how much weight it carries:

1. **The gradient error is below the reference curve's own normal
   discontinuity.** Apple's `.continuous` path breaks tangent by 2.4532° at both
   shoulder/arc joins. Our worst rim-band gradient error is 1.55°. Refraction
   direction cannot be made more faithful than the target's own normal is
   well-defined, so the normal is not where fidelity is lost.
2. **The value error is at or below rim antialiasing.** 0.17 px worst case is
   0.51 device px at the mobile benchmark scene's DPR 3, and 0.34 at the desktop
   scene's DPR 2. A rim is a soft, antialiased feature a few device pixels wide;
   a half-pixel shift in its position at the single worst point of the single
   worst shape in a 324-shape matrix is not a fidelity claim anyone can falsify
   by eye. The p95 is 0.156 px.
3. **It is met without transcendentals, branches, or texture bandwidth**, which
   is what keeps the fallback unnecessary rather than merely undesirable. A
   distance-mask atlas would buy accuracy vitrea cannot perceive, in exchange for
   VRAM, an authoring/bake step, and resolution-dependent morphs.

The honest caveat: parts 1 and 2 are arguments from physical scale and from the
reference's own precision, not from a perceptual study. If C7's calibration diff
later shows a shape-axis residual that traces to the field rather than to the
reference family, the numbers here are precise enough to re-open the decision
without re-running the spike — raise the basis order (§below) first, and only
then reconsider the atlas.

The declared bound, for the parent Decision Log:

> The v1 parametric pseudo-SDF (radial-support field, degree-5 corner correction
> in sin 2θ, first-order gradient normalization) holds, against the
> continuous-corner reference contour, across smoothing [0, 1], sizes 16–600 px,
> aspect 1:1–8:1 and corner radii to half the short side: field value error
> ≤ 0.17 px and gradient direction error ≤ 2.92° within |d| ≤ 8 px; ≤ 0.17 px and
> ≤ 1.55° within |d| ≤ 1 px, the gradient taken on the normalized field (a
> cheaper unnormalized normal holds ≤ 4.26°, equal on the contour).
> Capsules and circular corners (smoothing 0) are
> exact to machine precision. Error is linear in corner radius at the zero level
> set (1.4e-3 · r) and bounded at ~0.17 px absolute over the measured size range.

Secondary recommendations:

- **Fit the coefficient table against whichever contour family calibration
  designates, and fit `profile: "continuous"` against Apple's curve directly**
  rather than against Figma at smoothing 0.66. Same shader, same channels, same
  cost — one different coefficient table, worth 6.4× on value error. Figma's
  family remains the right *authoring* parameterization (it spans the range
  continuously and `smoothing` interpolates); it is the wrong thing to *render*
  when the target is Apple.
- **Keep family C as the quality governor's first step within the texture tier.**
  Dropping the `|∇|` normalization is one branch and one uniform, saves 29% of the
  field's total cost (0.444 ms against 0.626 ms at the pessimistic 8-surface
  mobile bound), and degrades the bound to 0.57 px and 4.26° — same coefficient
  table, same zero level set, same authored channels. The spec's §Performance
  envelope prefers degrading *within* a tier before switching tiers, and this is
  a cleaner within-tier step than reducing refraction resolution. It is a
  proposal, not a validated deliverable: family C's WGSL is inspection-verified
  only and needs the f32 cross-check before it ships (§4).
- **Basis order is a tuning knob, not a design commitment.** Five terms give
  1.38e-3 r worst case with coefficients bounded by 3.3. Seven give 6.6e-4 r but
  push coefficients to ~56, which starts to matter in f32. If calibration ever
  wants tighter, raise the order and re-express the polynomial in a Chebyshev
  basis rather than monomials.
- Record that a plain analytic rounded-box SDF was measured and **rejected** at
  2.24 px band error and 7.09° gradient error. This is the cheap option, and the
  reason it is not viable should not have to be rediscovered.

---

## 6. Impact on C3, C6 and X8

### X8 — shape channel set: **survives unchanged**

`{ center, size, radii, smoothing, thickness }` needs no revision. Every channel
stays numeric and interpolable. No Revision Note to the parent is required for the
channel set. Three clarifications are proposed, none of which change the
interface:

1. **`smoothing` is clamped by a budget derived from `size` and `radii`.**
   Effective smoothing is `min(smoothing, budget/r − 1)` with `budget = ½·min(w, h)`
   for a uniform radius. This is a real interaction between X8 channels and it must
   be implemented, not assumed away — it is what makes capsules exact and what
   bounds the worst-case radius. It is continuous in size, so morphs do not snap;
   that property is asserted in the suite. The authored value should be preserved
   and the clamp applied at derivation, so shrinking and re-growing a shape is
   lossless.
2. **`thickness` needs no separate error bound.** The spec derives a concentric
   shape as a level-set offset of the parent field, which makes the inner
   contour's accuracy identically the field's value error at `d = −thickness`.
   For thickness ≤ 8 px that is the table above (≤ 0.17 px), asserted in the
   suite. Thickness > 8 px is outside the measured band and would need a wider
   sweep before being claimed.
3. **`radii` was swept uniform only.** Per-corner radii are untested here. Figma
   distributes each side's budget between its two corners in proportion to their
   radii, so per-corner radii imply a per-corner budget, a per-corner effective
   smoothing, and a per-corner coefficient set. The field's corner algebra is
   built on `|x|, |y|` and is therefore mirror-symmetric by construction — it
   cannot express four different corners as written. **C3 should treat per-corner
   radii as an explicit scope decision, not an implementation detail.** If v1
   needs them, the corner sector must be selected by quadrant before the corner
   algebra runs, and the sweep must be re-run.

### C3 — geometry kernel

- Adopt `spikes/s2-geometry-field/` as the error-bound regression base. `pnpm test`
  in that directory runs 46 tests in ~15 s, including the declared bounds, the
  exactness properties, and the coefficient table's integrity. The bounds are set
  slightly above the measured values with the measured values recorded beside them,
  so refactoring noise does not fail the suite but a real regression does.
- The coefficient table is **committed** (`src/coefficients.ts`, regenerated by
  `npm run fit`) rather than computed at test time. C3 should keep it committed for
  the same reason: a table that silently moves when the fitter is touched is not a
  regression target.
- Implement the budget clamp, the corner reach `p` as the field's corner offset,
  and the transcendental-free `sin 2θ` / `cos 2θ` derivation. Each is load-bearing
  for the bound, and the reasons are documented at the definitions.
- The reference contour family is **G1 but not G2**: the cubic meets the circular
  arc with a curvature step of 0.39–0.57 / r, and smoothing 1.0 is the only
  curvature-continuous member of the family (the arc vanishes there). Do not
  assume G2 anywhere in the kernel.

### C6 — WebGPU renderer

- Per-instance uniforms widen by **six floats**: the corner offset `re` and five
  coefficients. These are *derived*, not authored — computed CPU-side from
  `{size, radii, smoothing}` — so they are an instance-buffer layout change, not
  an API or channel change. During a morph they must be recomputed per frame,
  which is trivial at v1's surface counts but should be batched with the existing
  geometry sync rather than done per draw.
- The field is branchless in the corner algebra; the only guard is a clamp on the
  squared corner radius to keep the deep-interior case from producing NaN. Keep
  that clamp — it is cheaper than a branch and it is why the straight-edge region
  needs no special case.
- **How the normal is computed is a real decision, and it is not free.** The
  gradient bound in §2 is measured by central-differencing the *normalized* field.
  A shader doing that pays four extra field evaluations per pixel — roughly five
  times the cost in §4. The tempting shortcut is the closed-form level-set normal
  of the *unnormalized* radial-support field, `normalize(ρ̂ − (R′/ρ)·θ̂)`, where
  `ρ̂` is the normalized clamped corner vector, `θ̂` its perpendicular, and `R′`
  the correction derivative the field already computes for its normalization
  term. That normal costs essentially nothing. Measured over the full matrix
  (`src/diag-normal.ts`, pooled samples rather than per-shape aggregation, so
  compare the max columns only):

  | band | closed-form normal, max | normalized-field gradient, max |
  | --- | --- | --- |
  | \|d\| ≤ 1 px | 2.641° | 1.545° |
  | \|d\| ≤ 4 px | 4.257° | 2.622° |
  | \|d\| ≤ 8 px | 4.257° | 2.915° |

  The two agree to four decimal places **on the contour** — the normalization
  changes level sets only away from the zero set — so rim lighting is indifferent
  and the choice only affects refraction at depth. The free normal is 1.5–1.7×
  worse there, and its \|d\| ≤ 8 figure (4.257°) is exactly family C's gradient
  error, which is the same statement: taking the cheap normal is taking family
  C's gradient while keeping family D's values. **Either accept ≤ 4.26° for
  refraction and take the free normal, or derive the analytic gradient of the
  normalized field** — that needs no extra field evaluations either, just more
  algebra than this shortcut. What is not available is the ≤ 2.92° bound at the
  free normal's price.
- The eikonal defect stays under 0.03, so the field can be treated as a distance
  for refraction-strength purposes without renormalization.

### C7 — calibration (informational; C7 is not blocked by S2)

- Expect a residual against Apple on any metric that differentiates the surface
  normal, at both shoulder/arc joins, from the reference curve itself — 2.45°
  tangent break in Apple's path, 0.36/r curvature break. A specular rim will show
  it. That is a property of the target, not a defect in vitrea.
- The best-matching Figma smoothing is **0.66**, not the commonly cited 0.6. If the
  Apple-direct coefficient table is adopted per §5, this number becomes
  informational rather than load-bearing.
- Apple saturates its corner reach at r/side = 0.327083 and warps past that point.
  vitrea's budget policy (Figma's) differs. Shapes above that radius ratio are not
  comparable to Apple and should be excluded from fidelity claims or measured
  separately.

### Not blocked, not changed

Nothing in §rendering contract, §honesty core, or the motion or colour contracts
is touched by these findings. S2's gate on C3 and C6 can be released.
