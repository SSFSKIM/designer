# W13 G0 — the windowed instrument, and what it recovers from a known law (2026-09-03)

**Claim.** W12 G0's warp-recovery model, run the other way round — the lens displacement
pinned at `main`'s landed law and the body's mix free per 4 CSS px depth window — reads the
sharp share by depth from a straight edge. On a synthetic field with a known k(u) it recovers
that k to **0.003 (flat) and 0.007 (ramped)** in every validated window when three checker
pitches are pooled, which is the configuration every reference reading in `g0-ramp.md` uses.
On vitrea's own canonical GPU captures, where the material's share is one number per span, it
reads k(u) **flat to 0.012–0.046** at every span and both scales — inside the ±0.05 contract
X4 asks for — and reads that number's **level** right to 0.008 on `rrect-md` and wrong by
0.07–0.12 on the other three spans, for a reason the synthetic quantifies: the canonical bed
offers **one** spatial frequency, and at one frequency the transmission and a uniform shift
of the share trade against each other almost exactly. Code: `w13lib.py`; runs:
`g0_validate.py` → `parts/g0-validation.json`, `g0_selftest.py` → `parts/g0-selftest.json`.

## 1. The instrument

**The model.** Along a pixel line normal to a straight edge, at fine depth u on line c:

```
Y = a + t · [ (1 − k(u))·A(x_src, y_src) + k(u)·B(x_src, y_src) ]
```

- `A` and `B` are the two body components' blurred backdrop, in linear luminance, read at
  the point the shader samples. A checkerboard is separable, so a separable blur of it is
  `½(1 − Sx(x)·Sy(y))` with each `S` the ±1 square wave convolved with that component's 1-D
  kernel — exact, evaluated by interpolation on a dense 1-D grid. Any other backdrop
  (`photo` here) is blurred as a raster at device resolution and read with cubic
  interpolation; that path carries the raster's own interpolation error and is used only
  where the frequency it adds is what makes a fit identifiable.
- `(x_src, y_src) = p − dir·D(depth)` is `main`'s landed lens, **fixed** (the wave's first
  binding rule): `D(u) = S·max(0, 1 − u/L′)^p` with `S = lensRefractionGain·min(0.8·span, 60)`,
  `L′ = lensExtentGain·min(0.25·span, 20)`, `p = lensProfileExponent` — 44.7 / 26.74 / 3.69
  on spans ≥ 80 — and `dir` the rounded rect's unit normal blended toward the inscribed
  oval by `ω = lensOvalization·smoothstep(64, 72, span)` (0.8 on the three large spans, 0
  on `rrect-sm` and the capsule). The tangential part of `dir` is what magnifies the band
  along the edge, so the source's cross coordinate moves with depth and the model carries
  that per (line, depth) rather than through a scalar magnification.
  Checked against claims §5.49 §2's crossings: D reads **33.6 / 24.6 / 12.0 / 0.3 CSS px** at
  u 2 / 4 / 8 / 20, the same numbers `material.ts`'s own doc comment quotes.
- `k(u)` is one number per depth window, windows being 4 CSS px bins from the contour to
  span/2. The window indicator is applied on the fine grid **before** the pixel is
  integrated over its footprint, so a pixel straddling a boundary carries both windows.
- Depth is the rounded rect's **SDF depth**, not the distance to this edge, and a sample is
  used only where the two agree — where this edge is the nearest feature. That is what makes
  the straight-edge reduction exact; it also means only the lines near an edge's midpoint
  reach the deep windows, and the left and right edges of a shape whose span is its height
  reach almost none of them. A capsule has no straight vertical edge at all and contributes
  its top and bottom only.

**The solve.** At fixed widths the model is bilinear: linear in (a, t) given k, linear in k
given (a, t). It is solved by alternating least squares on accumulated normal equations —
one level and one transmission per line set (a line set is one backdrop × one edge), one
share per window shared by every set. No optimiser, no restarts, no penalty; the fit
converges in tens of iterations from a flat start. Lines are strided to at most 48 per set
because adjacent lines are near-replicas.

**Two modes, and why the second one is only a diagnostic.** A variant frees the two window
coefficients separately (`solve_free_t`), which makes the per-window transmission a fitted
quantity and would say whether the reference's transmission changes with depth rather than
only its mix. It is identified only where several pitches are pooled; at one pitch it wanders
(§2). The readings in `g0-ramp.md` all use the shared-t mode.

**What the fit window excludes.** Depths below 2 CSS px (the rim highlight and the rim pixel
are not in the body model), everything outside the silhouette, and any pixel whose footprint
crosses out of the region where this edge is nearest. The reported windows start at u = 4 and
stop at span/2 − 4.

## 2. What is identified, and what is not

The self-test that matters is not "does the fit converge" but "is k(u) identified at all".
`g0_selftest.py` and `g0_validate.py` §2 answer it by building a synthetic capture from the
forward model itself at a known k(u) — flat at `main`'s own share, and a ramp from 0.5 at the
contour to 1 at the centre — adding Gaussian noise of σ 0.002 in linear luminance, and
refitting. Maximum |k − truth| over the validated windows, `rrect-md` and `rrect-lg` at 1x:

| pooled backdrops | `rrect-md` flat | `rrect-md` ramp | `rrect-lg` flat | `rrect-lg` ramp |
| --- | --- | --- | --- | --- |
| `checkerboard` alone (pitch 16 — vitrea's canonical bed) | 0.0199 | **0.3704** | **0.2632** | **0.3363** |
| `checkerboard` + `photo` | 0.0140 | 0.1644 | 0.1041 | 0.1589 |
| **pitches 16 / 32 / 64 (the reference reading)** | **0.0010** | **0.0031** | **0.0010** | **0.0030** |
| pitches 8 / 16 / 32 / 64 | 0.0017 | 0.0050 | 0.0031 | 0.0065 |

The mechanism of the one-pitch failure is exact and worth stating, because it decides what
the instrument may be pointed at. What a fit sees at one spatial frequency is the product
`t · [α + k·(β − α)]`, α and β the two components' contrast transfer at that frequency. At
pitch 16 the sharp component keeps ≈ 0.97 of the fundamental and the σ-10 heavy one ≈ 0.15,
so a uniform scaling of `t` can be undone by a uniform affine shift of `k` with almost no
residual cost: in the one-pitch synthetic above the fit returned `t` 0.232 against the truth
0.42 and a ramp with 1.6× the true amplitude, at the same RMS. A second backdrop breaks it
only if its `β/α` is very different — a **coarse** pitch, where the heavy component still
passes most of its contrast. `photo` is not coarse enough (its low-frequency amplitude is
small), which is why it halves the error rather than removing it.

Two consequences, both binding on how the readings are used:

1. Every reference reading in `g0-ramp.md` pools pitches 16 / 32 / 64, where the estimator's
   own error is 0.003.
2. On vitrea's canonical bed, which carries the checkerboard at pitch 16 only, the *shape* of
   k(u) is identified and the *level* is not. §3 reports both, and the level's miss is the
   degeneracy, measured.

## 3. The plate self-test

The analytic plate must equal the committed raster the capture was taken over, along every
line the instrument uses. Over **140 line sets** — five components × pitches 8 / 16 / 32 / 64
× four edges × two scales, minus the 20 combinations with no straight-edge line (a capsule's
vertical edges; a coarse pitch with no cell centre inside a short straight run) — the maximum
|analytic − raster| is **0.00000000**. `g3lib.verify_plates` agrees at both scales on every
pitch family.

## 4. Contract X4 — the recovery of vitrea's own uniform share

`main` renders one heavy share per span, `scatterThickness(span) = 0.4 + 0.6·smoothstep(32,
256, span)`: 0.400 / 0.405 / 0.519 / 0.636 / 0.764 on spans 32 / 44 / 96 / 128 / 160. The
instrument was run on vitrea's own canonical GPU captures with the widths pinned at the
profile's (σ_sharp `blurSigma` 1.25, σ_heavy `blurSigma`·`sizeScatterGainMax` 10 CSS px),
once on the checkerboard alone and once pooling `photo` where the bed has it.

| cell | truth k | k mean | k min | k max | **spread** | level error | fitted t | RMS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `capsule-button` 1x | 0.405 | 0.519 | 0.510 | 0.523 | **0.013** | +0.114 | 0.620 | 0.0070 |
| `capsule-button` 1x + `photo` | 0.405 | 0.514 | 0.505 | 0.518 | **0.013** | +0.109 | 0.614 | 0.0048 |
| `rrect-md` 1x | 0.519 | 0.515 | 0.508 | 0.524 | **0.016** | **−0.004** | 0.476 | 0.0070 |
| `rrect-md` 1x + `photo` | 0.519 | 0.521 | 0.514 | 0.530 | **0.016** | **+0.002** | 0.482 | 0.0052 |
| `rrect-ml` 1x | 0.636 | 0.515 | 0.504 | 0.532 | **0.028** | −0.121 | 0.364 | 0.0063 |
| `rrect-ml` 1x + `photo` | 0.636 | 0.563 | 0.554 | 0.578 | **0.025** | −0.073 | 0.401 | 0.0049 |
| `rrect-lg` 1x | 0.764 | 0.519 | 0.499 | 0.535 | **0.035** | −0.245 | 0.238 | 0.0042 |
| `rrect-lg` 1x + `photo` | 0.764 | 0.671 | 0.657 | 0.681 | **0.024** | −0.093 | 0.340 | 0.0040 |
| `capsule-button` 2x | 0.405 | 0.525 | 0.518 | 0.530 | **0.012** | +0.120 | 0.624 | 0.0094 |
| `capsule-button` 2x + `photo` | 0.405 | 0.522 | 0.515 | 0.526 | **0.012** | +0.117 | 0.620 | 0.0069 |
| `rrect-md` 2x | 0.519 | 0.522 | 0.504 | 0.549 | **0.045** | **+0.003** | 0.474 | 0.0087 |
| `rrect-md` 2x + `photo` | 0.519 | 0.527 | 0.510 | 0.554 | **0.045** | **+0.008** | 0.480 | 0.0065 |
| `rrect-ml` 2x | 0.636 | 0.522 | 0.508 | 0.541 | **0.033** | −0.114 | 0.358 | 0.0063 |
| `rrect-ml` 2x + `photo` | 0.636 | 0.567 | 0.554 | 0.583 | **0.029** | −0.069 | 0.393 | 0.0050 |
| `rrect-lg` 2x | 0.764 | 0.522 | 0.501 | 0.546 | **0.046** | −0.242 | 0.238 | 0.0045 |
| `rrect-lg` 2x + `photo` | 0.764 | 0.670 | 0.655 | 0.686 | **0.031** | −0.094 | 0.336 | 0.0042 |

**Met, on the property the wave turns on: the instrument does not manufacture a ramp.** The
spread of k(u) across the validated windows (4 ≤ u ≤ span/2 − 4) is 0.012–0.046 on every cell
at both scales, so every window is within ±0.05 of every other and within ±0.05 of the cell's
own mean. The reference's readings in `g0-ramp.md` move by 0.2–0.5 over the same windows, an
order of magnitude above this instrument's flat-field noise.

**Not met on the level, on three of the four spans, and the reason is §2's degeneracy, not
the model.** `rrect-md` — the cell the whole bed is scored on — comes back within 0.008 at
both scales. The other three miss by 0.07 to 0.12 with `photo` pooled, and the fitted
transmission moves in exactly the compensating direction (`rrect-lg` 1x: k 0.519 with t 0.238
against a truth of k 0.764, which at the same identified product implies t ≈ 0.38). The
synthetic in §2 puts the same estimator's one-pitch error on `rrect-lg` at 0.26 flat, so the
measured 0.245 is the degeneracy and nothing else. There is no coarse-pitch backdrop in the
canonical bed and this wave captures nothing, so the level cannot be closed here; the
reference is never read this way.

**The spread over edges.** Each cell was also fitted on one edge at a time. The per-window
standard deviation across the four edges is in `parts/g0-validation.json`
(`per_edge_sd`); it is the honest uncertainty, the nominal standard errors from the
normal equations being optimistic because adjacent lines are near-replicas.

## 5. Sensitivity to the assumed widths

The GPU tier's heavy component is a **mip chain level**, not a Gaussian (claims §5.58 §1), so
"σ_heavy 10 CSS px" is a nominal width, not a rendered one. The same fits were repeated over
a coarse grid of both widths on `checkerboard` + `photo`:

| cell | best σ_sharp | best σ_heavy | k mean | spread | truth k | RMS |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` 1x | 1.50 | 14.0 | 0.504 | 0.009 | 0.519 | 0.0039 |
| `rrect-lg` 1x | 1.50 | 14.0 | 0.648 | 0.017 | 0.764 | 0.0032 |
| `rrect-md` 2x | 1.50 | 8.0 | 0.518 | 0.014 | 0.519 | 0.0044 |
| `rrect-lg` 2x | 2.00 | 14.0 | 0.635 | 0.012 | 0.764 | 0.0032 |

Two readings. First, the pixels want a sharp σ of **1.5 CSS px** against the profile's 1.25
and a heavy σ of **12–14 CSS px** against the nominal 10 — the same direction W12 G0 recorded
(σ1 read 1.6–1.7 there) and consistent with the mip tap's footprint being wider than the
level's nominal Gaussian. Second, and this is what the sensitivity question was asked for:
across the **whole** 30-point grid the flatness of k(u) stays between 0.009 and 0.106 while
the level moves over a range of 0.19–0.79. **The shape of k(u) is robust to the assumed
widths; its level is not.** The reference's tables carry that limit with them.

## 5b. The candidate's build, read without capturing anything

W12 G3's runtime sweep left its **last** point's web captures in scratch, and their
`report__webgpu.json` names the patch: `sizeScatterScaleTerm` **0.35** on the candidate
branch, 2x. That is a second vitrea build with different known widths (the device-pixel ones:
σ_sharp 0.625, σ_heavy 5 CSS px at 2x) and a different known share
(min(1, `scatterThickness(span)` + 0.35) = 0.869 on `rrect-md`, 0.986 on `rrect-ml`), so the
instrument can be checked against it for free.

| cell | truth k | k mean at the nominal widths | spread | best grid point | k mean there | spread |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` 2x | 0.869 | 0.672 | **0.031** | σ 1.25 / 8.0 | 0.647 | **0.009** |
| `rrect-ml` 2x | 0.986 | 0.912 | **0.024** | σ 1.25 / 7.0 | 0.890 | **0.017** |

Flatness over the whole 35-point width grid: 0.007–0.093 on `rrect-md`, 0.007–0.118 on
`rrect-ml`. **The flatness contract holds on a second build**; the level again does not, and
here it is worse than on `main` for a computable reason. With the device-pixel widths the
heavy component at 2x is σ 5 CSS px, which keeps **0.62** of the pitch-16 fundamental against
`main`'s **0.15**; the two components' contrast transfer is that much closer together, so the
one-frequency trade of §2 is that much flatter. The best grid point's σ_heavy 7–8 CSS px
against the nominal 5 is the same mip-tap widening (×1.4–1.6) §5 found on `main` (×1.2–1.4).

The wave's optional capture of the term-**0** point was therefore **not run**: the check it
was there to buy — the instrument on the candidate's known law — is answered by the retained
0.35 captures, and no GPU or canonical capture path was touched.

## 6. Limits stated

- The level of k is identified only where the pooled backdrops differ strongly in the ratio
  the two components' contrast transfer takes; the reference readings satisfy that, vitrea's
  canonical bed does not.
- The lens is fixed by decision. Its 0.6–1.3 px mid-depth residual at 2x (§5.55 §4) is
  therefore *inside* the residual of every fit here, and any part of it that correlates with
  depth is absorbed by the windows near the band. The near-contour windows (u < 4) are
  excluded for that reason and because the rim highlight is not in the body model; the
  first reported window is [4, 8).
- The residual RMS on the reference (0.005–0.023 in linear luminance, `g0-ramp.md` §1) is two
  to four times vitrea's (0.004–0.009) on the same geometry. The model is vitrea's body under
  vitrea's lens; on the reference it is an approximation and the difference is the size of
  what is not modelled — the reference's own lens residual, its rim, and the level structure
  §5.55 §3 recorded on the thin material.
- The transmission is assumed constant with depth (the shared-t mode). If the reference's
  transmission itself ramps, that ramp is inside k(u). The free-t mode exists to test this
  and is identified on the pooled pitches; it is not exercised in this round's tables and is
  named in `g0-ramp.md`'s "what the declaration should carry" as the first thing G1 should
  check before it fits a form.
- `photo` enters through the raster path, which blurs a device-resolution raster and reads it
  with cubic interpolation. For the sharp component at 1x (σ 1.25 CSS px = 1.25 device px)
  that is a real if small model error; it is used only on vitrea's cells, never on a
  reference reading.
- The candidate build read in §5b is the sweep's 0.35 point, not the term-0 point the
  charter names; the two differ in the share, not in the widths, and the widths are what the
  check is about.
