# W12 G1 — the interior body on every checkerboard cell, 1x and 2x (2026-09-03)

Method (`g1b-body.py`, `g1-body-2x.json` — the `constrained` block is the table below; `body.out`,
`body2.out`, `sharp-ext.out`). Linear luminance over the inset interior; the inset is min(radius,
h/4) on every cell (W11's `interior_box` inset by the radius, which on the capsule — radius = h/2 —
left no rows; 11 px on the capsule, 8 on `rrect-sm`, 20 / 27 / 34 on the rounded rectangles, all
outside the landed band). `toolbar-group`: the three 44-px circles inset by 11 (discs of radius 11,
1152 px at 1x). `glass-over-glass` base: the base's inset interior minus the over pane dilated by 16
CSS px — two 10-px side strips and a 5-px strip below the pane, 2936 px at 1x, measured under the
over pane's outer shadow. Fits: single Gaussian σ (CSS px) with level a and transmission t by least
squares, admissible only (0 ≤ a ≤ 1, 0 ≤ t ≤ 1 — the unconstrained fits on low-contrast cells run to
σ 10–12 with a < 0 and t > 1); vitrea's two-component form (σ 1.25, σ 10, share k free) likewise.
Model-free: the interior mean and standard deviation, and the retained contrast std(Y)/std(plate).

## 1. Native — the reference, both scales

| cell | scale | σ | a | t | r² | mean | std | retained |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 1x | 1.25 | 0.444 | 0.340 | 0.993 | 0.614 | 0.141 | 0.283 |
| | 2x | 1.25 | 0.432 | 0.367 | 0.983 | 0.615 | 0.153 | 0.306 |
| `capsule-button` | 1x | 1.25 | 0.445 | 0.337 | 0.995 | 0.614 | 0.142 | 0.284 |
| | 2x | 1.25 | 0.433 | 0.365 | 0.983 | 0.616 | 0.154 | 0.309 |
| `toolbar-group` | 1x | 1.25 | 0.443 | 0.341 | 0.995 | 0.614 | 0.142 | 0.283 |
| | 2x | 1.25 | 0.430 | 0.371 | 0.984 | 0.616 | 0.154 | 0.308 |
| `rrect-md` | 1x | 1.25 | 0.556 | 0.246 | 0.987 | 0.679 | 0.103 | 0.206 |
| | 2x | **3.0** | 0.473 | 0.413 | 0.985 | 0.680 | 0.122 | 0.245 |
| `rrect-ml` | 1x | 1.25 | 0.609 | 0.165 | 0.968 | 0.691 | 0.069 | 0.138 |
| | 2x | **≥ 6** | (0.262) | (0.857) | 0.975 | 0.691 | 0.087 | 0.173 |
| `rrect-lg` | 1x | 1.0 | 0.659 | 0.093 | 0.908 | 0.706 | 0.042 | 0.084 |
| | 2x | **≥ 6** | (0.438) | (0.534) | 0.930 | 0.705 | 0.057 | 0.113 |
| `glass-over-glass` base | 1x | 1.25 | 0.565 | 0.193 | 0.945 | 0.661 | 0.079 | 0.158 |
| | 2x | 4.0 | 0.441 | 0.442 | 0.952 | 0.661 | 0.085 | 0.169 |

Parenthesised (a, t) are at the admissibility edge and not readings. Where σ says "≥ 6": at pitch 16
a Gaussian wider than ≈ 5 CSS px leaves the checker no contrast, so the fit cannot tell 6 from 12 and
(a, t) trade against each other; the deep-interior σ scan with the grid extended to 8 (`sharp-ext.out`)
reads `rrect-md` 2x σ 3.0 at u 24–32, 3.5 at 36, 4.0 at 40, 5.0 at 44 (the centre), and `rrect-lg`
2x σ 8 (the grid's top) at every depth from 24 to 76. The impulse kernel at `rrect-md`'s centre
(`g1-depth-ramp.md` §2) reads σ 5 at 2x, consistent with the scan.

**What is scale-invariant in the reference and what is not.** The interior *mean* is the same at both
scales on every cell (0.614 / 0.615, 0.679 / 0.680, 0.691 / 0.691, 0.706 / 0.705): the level law is a
points law. The interior *structure* is not: on the small spans the 2x reference retains 8% more
contrast than the 1x one at the same σ 1.25 (t 0.365 against 0.337); on `rrect-md` it retains 19%
more (0.245 against 0.206) with a *wider* σ (3.0 against 1.25) and a higher t (0.413 against 0.246)
and a lower a (0.473 against 0.556); on `rrect-ml` and `-lg` it retains 25–35% more with a σ the
pitch-16 cell can no longer identify. At 1x every cell sits at σ 1.25 with t falling from 0.34 to
0.09 as the span grows (the sharp leak fading, §5.41); at 2x the small cells sit at σ 1.25 and the
large cells at σ 3 → ≥ 6 with t staying high. The 2x reference is not a wider 1x reference: its σ
grows with span (and with depth — `g1-depth-ramp.md` §1b) where the 1x reference's share shifts.

## 2. Vitrea, both tiers, against the native at 2x

| cell (2x) | side | σ | a | t | r² | mean | std | retained | Δmean vs native | Δretained vs native |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | webgpu | 2.0 | 0.508 | 0.342 | 0.997 | 0.679 | 0.123 | 0.246 | **+0.064** | −0.060 |
| | css | 5.0 | 0.288 | 0.627 | 0.991 | 0.602 | 0.098 | 0.195 | −0.013 | −0.111 |
| `capsule-button` | webgpu | 2.0 | 0.512 | 0.338 | 0.997 | 0.681 | 0.123 | 0.247 | **+0.065** | −0.062 |
| | css | 5.0 | 0.301 | 0.615 | 0.991 | 0.608 | 0.096 | 0.193 | −0.008 | −0.116 |
| `toolbar-group` | webgpu | 2.0 | 0.512 | 0.338 | 0.997 | 0.681 | 0.121 | 0.242 | **+0.065** | −0.066 |
| | css | 5.0 | 0.289 | 0.632 | 0.991 | 0.605 | 0.097 | 0.194 | −0.011 | −0.114 |
| `rrect-md` | webgpu | 1.5 | 0.582 | 0.239 | 0.997 | 0.701 | 0.095 | 0.190 | +0.021 | **−0.055** |
| | css | 6.0 | 0.340 | 0.599 | 0.991 | 0.639 | 0.062 | 0.124 | −0.041 | −0.121 |
| `rrect-ml` | webgpu | 2.0 | 0.602 | 0.196 | 0.996 | 0.700 | 0.070 | 0.140 | +0.009 | −0.033 |
| | css | 6.0 | 0.459 | 0.358 | 0.989 | 0.638 | 0.036 | 0.072 | −0.053 | −0.101 |
| `rrect-lg` | webgpu | 2.0 | 0.635 | 0.129 | 0.997 | 0.700 | 0.046 | 0.093 | −0.005 | −0.020 |
| | css | 8.0 | 0.348 | 0.580 | 0.981 | 0.638 | 0.020 | 0.041 | −0.067 | −0.072 |
| `glass-over-glass` base | webgpu | 2.0 | 0.574 | 0.186 | 0.912 | 0.667 | 0.065 | 0.130 | +0.006 | −0.039 |
| | css | 8.0 | 0.134 | 0.954 | 0.695 | 0.611 | 0.033 | 0.066 | −0.050 | −0.103 |

The 1x rows are in `g1-body-2x.json` and `body2.out`; vitrea's mean and retained contrast are the
same at both scales within 0.01 on every cell (the laws are in CSS px, and the capture confirms the
tier keeps them; the σ column moves one grid step, 1.5 → 2.0, on the GPU tier), so the gap at 2x is
the reference moving, not vitrea.

**The transmission and level gap at 2x, per cell (GPU tier):**

- Small spans (`rrect-sm`, `capsule-button`, `toolbar-group`): the level is **0.064–0.065 too high**
  (0.679–0.681 against 0.615) and the retained contrast **20% too low** (0.246 against 0.306); vitrea's
  σ 2.0 against the reference's 1.25. The level gap is the same at 1x (0.674 against 0.614; the
  canonical matrix's `interiorMeanNative/Web` rows read 0.621 / 0.678 on the capsule at 1x and
  0.623 / 0.685 at 2x, so it is a known, bounded row, not a new one) — it is not a 2x gap, it is the
  small-span level.
- `rrect-md`: level +0.021, contrast −22% (0.190 against 0.245), σ 1.5 against 3.0 — vitrea is sharper
  and flatter: the reference at 2x is a wider blur passing more of it.
- `rrect-ml`, `rrect-lg`: level within 0.01, contrast −19% / −18% (0.140 / 0.093 against 0.173 / 0.113).
- The CSS tier is 0.04–0.07 **below** the reference in level on the large spans and 0.10–0.12 below
  in retained contrast everywhere (its single mixed σ 5–8): the two-layer CSS body's evidence, unchanged.

**The σ the 2x reference wants, per span:** 1.25 at spans 32–44 (and the toolbar's 44-px circles), 3.0
at 96 (rising to 5 at the centre of the cell), ≥ 6 at 128 and 160 (8 at the grid's top on `rrect-lg` at
every depth). A single number per span will not do it at 96 (the σ ramps with depth); at 128–160 the
pitch-16 cell cannot identify the number and a 2x probe with pitch 32/64 would.

## 3. `photo__rrect-md__rest` at 2x, from the canonical matrix

Keys: `profileKey apple-macos-26.5-2x-light-standard`, `sceneId photo__rrect-md__rest`, renderer
`webgpu` (tier texture, captured 2026-09-03T00:08:39Z) and `css` (tier dom, 2026-09-03T00:11:00Z).

| tier | `oklabDeltaEMean` | `ssimMean` | `interiorMeanNative` | `interiorMeanWeb` | `interiorStdDevNative` | `interiorStdDevWeb` |
| --- | --- | --- | --- | --- | --- | --- |
| webgpu | 0.0121 | 0.9978 | 0.6654 | 0.6590 | 0.0591 | 0.0487 |
| css | 0.0129 | 0.9740 | 0.6654 | 0.7268 | 0.0591 | 0.0549 |

On the photo the GPU tier's level is within 0.007 of the reference and its structure 18% low (the
same contrast shortfall the checkerboard shows at 2x); the CSS tier is 0.06 high in level. The
luminance slope through the backdrop (`luminanceSlopeNative` 0.439, web 0.296 gpu / 0.454 css) says
the same in the matrix's own terms: the GPU tier passes 2/3 of the backdrop variation the reference
passes at 2x.

## 4. Numbers to carry

- Reference interior mean is scale-invariant on every cell (±0.001); retained contrast is 8–35% higher
  at 2x, with σ 1.25 (spans ≤ 44), 3 → 5 (96, rising with depth), ≥ 6 (128, 160).
- GPU tier at 2x: level +0.064 on the small spans (a 1x gap too), +0.021 on md, ±0.01 on ml/lg;
  retained contrast −18 to −22% on every span.
- Photo md 2x: gpu ΔE 0.0121, level −0.006, structure −18%; css ΔE 0.0129, level +0.061.
