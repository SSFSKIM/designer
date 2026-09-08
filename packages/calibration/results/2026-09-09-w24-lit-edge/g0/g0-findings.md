# W24 G0 — the angular instrument, the read on both beds, and the lit edge's law

Spike; deliverable is findings, not a merge. Worktree `agent-a22f98cf20d905337`, branched from
`b245aef`. Everything below is measured on the landed 0.12.0 bed (`408ad2e`) and on the reference
fixtures; nothing canonical was written, and the holdout was neither fitted on nor captured.

**The one-paragraph answer.** Apple's rim is lit, the light is symmetric about the top-left ↔
bottom-right diagonal, and its form is `|n · L|` to a power near 1 with **no ambient floor at all**
— the wave chartered `a + (1 − a)|n · L|^p` with `a` expected at 0.15 dark and 0.25 light, and every
grouping of nineteen reference rows fits `a` to 0.000. The symmetric form beats the one-sided
Lambert W22 fitted to 0 by a factor of two on residual and the flat rim vitrea ships by rather more.
The mechanism is implemented behind two constants inert at their defaults, every golden and the
isolation proof's pinned hashes reproduce byte for byte, and the amplitude's re-expression is
closed-form rather than fitted: the shader normalises the dot product by `cos 45°`, so the four
straight sides are untouched at every exponent and W23's contour reads move by at most **0.00021**
against a bound of 0.005. Two things the charter did not expect came out of the read and are put to
the parent in section 8: the reference's angular contrast **depends on the scale** (the 1x light
bed's corners sit BELOW its straight sides where the 2x bed's sit above), and on a **thick** rounded
rectangle the reference's rim varies ALONG a straight side whose silhouette is straight to 0.05 px —
which no function of the normal can carry.

---

## 1. The instrument (a)

`read-angular.py`, with `instrument.txt` as its validation record and `diagnose.py` as its geometry
diagnostic. It does what the Design binds: parametrises the declared shape's boundary (a capsule as
two straight spans and two semicircles, a rounded rectangle as four spans and four quarter arcs of
the declared radius, from `scenes.json`, centred on the declared canvas and scaled by dpr), samples
it at 0.25 device px and never fewer than 720 points, reads at each the peak excess over W21's
eroded body along the inward normal from 1 CSS px outside to 4 CSS px inside, and reports the
profile in sixteen 22.5° bins **centred on the compass directions** and by segment, native against
web, with the brightest/dimmest ratio and the brightest bin's direction.

Bins centred and not edge-aligned is the one design choice with consequences: a rounded rectangle's
four straight sides each carry exactly one normal direction, and centring puts each side wholly
inside `N`, `E`, `S` or `W` instead of splitting it across two. The four diagonal bins are then the
corner arcs' own, which is where the lit edge lives.

### 1.1 Validation by injection

A synthetic rim of `A · (0.2 + 0.8 |cos(θ − 315°)|)`, one CSS px deep, painted from the shape's own
signed distance field and read back. The expectation is binned over the SAME boundary samples the
read uses rather than evaluated at the bin's centre angle — `|cos|` has a kink at its zero, so over
the 22.5° of the dimmest bin its mean stands 40 % above its centre value and a perfect reader would
have looked five codes wrong.

| cell | A | straight bins, worst \|error\| | arc bins, worst relative |
| --- | --- | --- | --- |
| 2x dark `dark-solid__rrect-md` (r 40 device px) | 0.05 | 0.000001 — **PASS** (bound 0.0005) | 2.0 % |
| 2x light `dark-solid__rrect-md` (r 40) | 0.20 | 0.000015 — **PASS** | 2.1 % |
| 1x dark `dark-solid__capsule-button` (r 22) | 0.02 | 0.000017 — **PASS** | 8.6 % |
| 1x light `mid-dark-solid__capsule-button` (r 22) | 0.10 | 0.000146 — **PASS** | 8.5 % |

The two columns are two different quantities and are reported apart. On a straight side the painted
line lands on whole pixels and what comes back is the reader's own arithmetic: it recovers the
injected profile to a millionth to a ten-thousandth of linear luminance, which is a fifth of a code
at worst. On an ARC the same one-CSS-px line is rasterised across two pixels at partial coverage, so
its peak is genuinely lower in the raster than in the paint, and the reader returns what the raster
holds. **That is the instrument's declared limit on corners and arcs — a systematic under-read of
about 8.5 % at a 22-device-px radius and 2 % at 40 — and it means every corner contrast in this
gate's tables is a LOWER BOUND on the reference's own.** Re-encoded to 8 bits the straight-side
error is 0.24–0.69 codes, which is the bed's resolution and not the reader's.

### 1.2 Against the parent's reader

`finding/angular-read.py` bins by ARCLENGTH clockwise from the top-left of the top edge and searches
1…4 DEVICE px; this one bins by the normal's ANGLE and searches 1…4 CSS px. The quantity neither
binning touches is the SEGMENT mean, and the two agree there **to 0.0001 on every segment of every
cell the parent read** — on the 2x dark `dark-solid__rrect-md`, the parent's `top 0.0332 tr 0.0056
right 0.0320 br 0.0418` against this reader's `top 0.0332 tr 0.0055 right 0.0319 br 0.0418`. On a
capsule the parent's `right-arc` is this reader's `tr` and `br` averaged: parent 0.0205 against
(0.0105 + 0.0299)/2 = 0.0202. `instrument.txt` §2 runs the whole read again through the parent's own
window so the difference between the two tables is the binning alone.

### 1.3 The geometry diagnostic, and the two ways this reader can be wrong

Per bin: samples, mean peak depth, TRUNCATED (peak at the far end of the window — the bin is a lower
limit, not a reading), OUTSIDE (peak outside the declared contour — the bin is reading the backdrop)
and CLIP. On the solid rows the mean peak depth is +0.12…+0.23 CSS px inside the contour and nothing
truncates, so the declared circular-arc parametrisation finds the rim where it is even though
Apple's corner is continuous rather than circular. Two limits do bite and both feed the fit's mask:

- **OUTSIDE.** Over a backdrop BRIGHTER than the body, the window's 1 CSS px of outward reach reads
  the backdrop. It costs six to eight of sixteen bins on the dark scheme's `mid-dark-solid` rows
  (backdrop 0.0595 against a body of 0.0285) and all sixteen on the dark scheme's `light-solid`
  rows, where the "rim" would otherwise read 0.74. Those bins are excluded per bin, printed, and the
  window is left as the Design binds it rather than narrowed to make a table look better.
- **CLIP**, on the light scheme's `light-solid` rows, whose body is 0.93 and whose rim runs into the
  encoding's ceiling. Those rows read a ratio of 1.03–1.18 where the same material over a dark
  backdrop reads 7.7, and they are excluded from the fit by a `body + peak > 0.97` test rather than
  fitted as if the material were flat there.

---

## 2. The read (b)

`angular-read.txt` — every cell of all six canonical profiles, native against the landed 0.12.0
captures, on the GPU tier and on the CSS tier beside it; then W9's light probe grid and W21's dark
probe grid, native, with vitrea's side of both under `ladder/probe9-base` and `ladder/probe21-base`.
`tables.txt` reduces it to one line per cell. The holdout's landed captures are read here and
nowhere else: W23 G3 spent that read, and clause (b) asks for the whole bed.

### 2.1 The verdict, per cell, on the untinted solid rows

`peak` is the brightest bin, `floor` the dimmest as a fraction of it, `ratio` their quotient, and
`bright` the brightest bin's compass direction. Reference first, vitrea second.

| cell | ref bright | ref peak | ref floor | ref ratio | ours bright | ours peak | ours floor | ours ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2x dark `dark-solid__rrect-md` | NNW | 0.0420 | 0.039 | 25.9 | N | 0.0361 | 0.802 | 1.25 |
| 2x dark `dark-solid__capsule-button` | NW | 0.0333 | 0.063 | 16.0 | N | 0.0248 | 0.797 | 1.25 |
| 2x dark `mid-dark-solid__capsule-button` | NW | 0.0712 | 0.411 | 2.43 | N | 0.0599 | 0.932 | 1.07 |
| 1x dark `dark-solid__rrect-md` | WNW | 0.0246 | 0.047 | 21.1 | N | 0.0251 | 0.803 | 1.25 |
| 1x dark `dark-solid__capsule-button` | NW | 0.0208 | 0.081 | 12.4 | E | 0.0173 | 0.778 | 1.29 |
| 2x light `dark-solid__rrect-md` | SSE | 0.2901 | 0.130 | 7.72 | N | 0.3317 | 0.672 | 1.49 |
| 2x light `mid-dark-solid__capsule-button` | SE | 0.3067 | 0.161 | 6.23 | N | 0.3548 | 0.696 | 1.44 |
| 1x light `dark-solid__rrect-md` | S | 0.1892 | 0.183 | 5.46 | S | 0.2098 | 0.429 | 2.33 |
| 1x light `mid-dark-solid__capsule-button` | N | 0.1906 | 0.172 | 5.82 | N | 0.2354 | 0.501 | 2.00 |
| 1x light `light-solid__rrect-md` (at the ceiling) | N | 0.0634 | 0.849 | 1.18 | N | 0.0678 | 0.823 | 1.22 |

Every reference row that is not at the ceiling reads a ratio between 2.2 and 26; every vitrea row
reads between 1.01 and 2.33, and no vitrea row's brightest bin exceeds its dimmest by more than a
factor of 2.4. That is the user's "a consistent line drawn on the edge", in numbers, and it is what
the wave exists to correct.

The brightest direction is `NW` or `NNW` or `SE` or `SSE` on every solid reference row of the dark
bed and on the 2x light bed. The four straight sides are equal to within 5 % on the reference and
to within 1 % on vitrea — which is exactly why three waves of per-side readers saw nothing.

### 2.2 The collapsed cells carry the same profile

The reference collapses `dark-solid__capsule-button` and `impulse__capsule-button` on both beds at
both scales (W23 G0 §1; the light and dark fixtures are byte-identical), and the probe grids'
`dark-solid__rrect-sm` and `dark-solid__rrect-lg` with them. Fitted alone, those seven fixtures give
axis 136.0°, exponent 1.15, ambient 0.000 against the uncollapsed rows' 136.0°, 1.00, 0.000. The
2x dark collapsed capsule runs `NE 0.0021 → NW 0.0333` where the finding read 0.007 → 0.031 through
the parent's window; the shape is the same one. **So the factor multiplies the collapsed rim too,
and it does so as one multiplication outside W23's trade bracket rather than as a second constant.**

### 2.3 The tinted rows, and the structured rows, as context

Tinted, 2x dark: `dark-solid__capsule-button` +orange reads ratio 12.5 in the reference (peak SE
0.1644) against 1.47 in vitrea — the painted rim is lit exactly as the bare one is. Over structured
backdrops the read is the BACKDROP's structure and not the material's: the 2x dark
`checkerboard__rrect-md` reads a ratio of 242 with its brightest bin at `NNE`, wherever a bright
square happens to meet the contour. Those rows are a check on the mechanism's reach, never fitting
ground, and they are why the fit uses solid rows only.

### 2.4 The CSS tier

Context only. On the 2x dark bed the tier's rim reads 0.0036 on the `dark-solid` capsule and 0.0070
on the `dark-solid` rrect against the reference's 0.0333 and 0.0420 — an order of magnitude dimmer,
which is W23's own deferred CSS rim fit and not this wave's term. The tier cannot vary a rim around
a contour at all; §6 records what that costs.

---

## 3. The law (c)

`fit-law.py`, on the reference's own bins, over the untinted solid rows of both canonical beds at
both scales and both probe grids, deduplicated by fixture digest (the collapsed cells' light and
dark fixtures are the same bytes) and masked per bin for clip, truncation and outside-reach. Twenty
rows, 285 bins. `A_cell` is solved per cell and never carried; the fit is of the SHAPE.

### 3.1 The form: symmetric, and it beats the alternatives on every grouping

RMS of the normalised bin residual — each cell divided by its own brightest bin, so that a light row
whose rim is 0.28 and a dark row whose rim is 0.04 weigh the same:

| rows | symmetric `\|cos(θ − φ)\|^p` | one-sided `max(cos, 0)^p` | flat (what vitrea draws) |
| --- | --- | --- | --- |
| both schemes | **0.1475** at φ 136.0°, p 1.05, a 0.000 | 0.2881 | 0.3121 |
| light | 0.1757 at 137.5°, 0.80, 0.000 | 0.2807 | 0.3027 |
| dark | 0.1009 at 135.5°, 1.25, 0.000 | 0.2939 | 0.3204 |
| light 2x | 0.0782 at 136.0°, 1.10, 0.020 | 0.2866 | 0.3287 |
| dark 2x | 0.0740 at 135.5°, 1.30, 0.000 | 0.2933 | 0.3226 |
| canonical bed | 0.1226 at 136.0°, 1.10, 0.000 | 0.2929 | 0.3224 |
| probe grids | 0.1728 at 136.0°, 1.00, 0.000 | 0.2819 | 0.2990 |

**Symmetric, decisively.** The one-sided Lambert cannot reach both ends of a diagonal whose two
corners the reference draws equal to a thousandth (2x dark: tl 0.0418, br 0.0418; 2x light: tl
0.2786, br 0.2823), and it degenerates in the fit — it runs to the grid's ceiling on both the
exponent (3.00) and the ambient (0.600) trying to become symmetric and still loses by a factor of
two. That, and not its gain, is why W22 rightly fitted `specularGain` to 0 (claims §5.94 §3): the
term had the wrong shape, so no amount of it helped.

### 3.2 The axis: 136°, and the rows do not separate it from the diagonal

Per cell, fitted alone: dark rows 135.0° ± 0.7° (min 133.5, max 136.0), light rows 137.7° ± 1.5°
(min 135.5, max 141.0). The joint fit is 136.0°. **The recommendation is the exact diagonal, 135°**,
for a reason that is a mechanism and not a rounding: only at 135° is the factor equal on all four
straight sides, and that is what makes the amplitude's re-expression exact (§4) instead of a 2 %
trade against W23's straight-span reads. The light rows' 2.7° preference is recorded here as the
residual it is, and it is worth one thousandth of RMS.

The axis is **not** `lightDirection`. That constant is [−0.3714, −0.9285] — a bearing of 338.2°, an
axis of 158.2°, 22° away — and it was fitted for the inner shadow and the sweep. The seam chosen
keeps it there untouched (§5).

### 3.3 The exponent: near 1, and it is not a root

The Design expected p ≈ 0.5–0.7 from the straight sides sitting at 0.75–0.85 of the peak. They do,
but the axis is not exactly 45° from them and the null is much deeper than a root would allow, so
the two readings pull apart: the joint fit is **p = 1.05**, the 2x rows (whose arcs the raster
actually carries) give 1.10 light and 1.30 dark, and the per-cell spread is 0.65…1.55. Vitrea's own
rows, fitted against the reference on rendered captures (§4.2), want 1.10 ± 0.22 light and
1.24 ± 0.17 dark. **The schemes overlap and one exponent carries both.**

### 3.4 The ambient fraction: there is none

Every grouping fits `a` to 0.000 over a search of 0…0.6 in steps of 0.005; the largest value any
grouping wants is 0.020 (light 2x). The charter's 0.15/0.25 came from reading the dimmest BIN as if
it were the profile's floor, and it is not: the bin mean of `|cos|^p` over the 22.5° straddling the
null is already 0.10–0.16, which is the whole of what the null bins carry. A constant every row
fits to zero is a constant the material does not have (C9a §6.2), so **the ambient term is declined
and removed rather than shipped at 0.**

### 3.5 The law, stated

```
rim = rimWidthWeight(d) × (√2 · |n · L|)^p × (rimAmplitude × present + rimCollapsed × toneAdapt)
      L = (−1, −1)/√2      p = rimLitExponent      (recommended 1.15; see §7)
```

---

## 4. The mechanism, and the amplitude re-expressed (c)

### 4.1 The re-expression is closed form, and it is the `√2`

W23's `rimAlpha` and `rimLevelGain` were fitted on the straight spans, which under a directional
factor sit at `(cos 45°)^p` of the peak. Rather than dividing the fitted amplitude by that number —
which would move four profile constants, would have to move again whenever `p` moved, and would
leave the CSS tier needing its own re-fit — the shader normalises the dot product INSIDE the power:

```wgsl
let lit = pow(max(abs(dot(normal, ou.rimLit.xy)) * 1.4142135, 1e-6), ou.rimLit.z);
```

At the default axis the factor is **exactly 1 wherever the normal is horizontal or vertical, at
every exponent**. No fitted amplitude moves, W23's clause 2 and this wave's clause 4 hold by
construction rather than by tolerance, only the corners and the arcs change, and the CSS tier —
whose one inset layer draws the straight-span value — needs no counterpart and no re-fit.

**The straight-span check, on the ladder.** W23's own `read-contour.py`, unmodified, on every solid
side of every solid untinted row of both ladder points against the landed bed: the worst movement is
**0.00021** of linear luminance per CSS px (1x light `light-solid__capsule-button`, top, at
exponent 1),
against a bound of 0.005. Not one side of one row moved by as much as a twentieth of the bound. The
same check read on the angular bins: the four straight BINS move by at most 0.00052.

### 4.2 The shader draws what the arithmetic says

Two rendered ladder points (exponent 1 and 2) against the landed bed at exponent 0. On every
unclipped solid row, `rendered` against `landed × factor(p)` in absolute linear luminance:

| point | worst \|rendered − landed × factor\| |
| --- | --- |
| exponent 1, dark bed | 0.00024 … 0.00158 |
| exponent 1, light bed (`dark-solid` rows) | 0.00076 … 0.00860 |
| exponent 2, dark bed | 0.00079 … 0.00191 |
| exponent 2, light bed (`dark-solid` rows) | 0.02772 |

On the dark bed, where the rim IS the whole of the near-contour excess, the shader and the
arithmetic agree to two thousandths. On the light bed the peak the reader returns is the rim plus
the lens's own near-contour band, so the identity is approximate and degrades with the exponent;
that is a statement about the reader, not about the shader. The `light-solid` rows are printed and
excluded: their peak is at the encoding's ceiling.

That agreement is what licenses interpolating the exponent in closed form between the rendered
points instead of sweeping it, which is what keeps this ladder to eight runs.

---

## 5. The exact diff for G2

| file | change |
| --- | --- |
| `renderer-webgpu/src/material.ts` | `MaterialOptics.rimLitExponent` (default **0**, per variant, beside `specularPower`) and `MaterialProfile.rimLitAxis` (default `[−0.7071, −0.7071]`, profile level, beside `lightDirection`), both with the doc comments this gate's numbers are in; `withMaterialOverrides` merges the axis; `MaterialProfilePatch` gains it; `opticsUnderPolicy`'s `border: "strong"` fold takes `rimLitExponent` to 0 beside `rimLevelGain` — a border a preference asked for is one brightness the whole way round. |
| `renderer-webgpu/src/wgsl/optics.ts` | one `rimLit : vec4f` on the uniform (xy axis, z exponent, w free) and one factor on the rim line: `rw * lit * (rimAmplitude * present + rimCollapsed * toneAdapt)`. |
| `renderer-webgpu/src/passes.ts` | `OpticsArgs.rimLitAxis` / `.rimLitExponent`; the optics uniform grows 100 → 104 floats; `d[100..102]`, `d[103]` free. |
| `renderer-webgpu/src/renderer.ts` | `rimLitAxis: material.rimLitAxis`, `rimLitExponent: optics.rimLitExponent`. |
| `platform-web/src/optics.ts` | **no constant moves.** A doc comment on `rimAmplitude` records why the tier cannot carry the factor, and that the `√2` normalisation means it does not have to: the amplitude it returns is the straight-span value, unchanged. |
| `calibration/scripts/capture-web.ts` | `"rimLitAxis"` added to `MATERIAL_PATCH_KEYS`; the exponent lives under `optics` and needs no entry. |
| `renderer-webgpu/test/backdrop-tone.test.ts` | the pinned rim string becomes `rw * lit * (…)` and the `lit` line is pinned beside it, so the seam cannot move unrecorded. |

**The seam, and why `spec` is left alone.** `light.xy` reaches only the one-sided `spec` term in the
optics pass; the inner shadow reads `light.z` and `light.w`. The new factor takes its own axis
constant, so `lightDirection` keeps its meaning for the shadow and the sweep by construction rather
than by care. `spec` itself is left in place and untouched: `specularGain` is 0 on both shipped
profiles so it contributes nothing, and retiring `specularPower` / `specularGain` is a profile-shape
change that belongs to the wave's declaration (G2), not to a gate whose whole claim is that nothing
moved. G2 should retire them when it adopts the exponent, and record it against §5.94 §3.

**One consequence G2 must handle.** Adding the two constants moves the profile documents'
`resolvedMaterialSha256` even though nothing renders differently, and
`packages/calibration/test/tuned-profiles.test.ts` is red in this worktree because of it. At the
seam, with the exponent at 0, the fingerprints are `b0cec2a7c4729d42` (light, was
`c426a37744c38cce`) and `68fc69f548c89881` (dark, was `bf5752ac1b152238`); with the fitted exponent
they will move again. G2 re-records them with the reason, and because the cell key includes the
document's hash the canonical rebuild starts from `rm results/matrix.json` in any case.

---

## 6. The goldens (X2)

`goldens-attribution.txt`.

**At the defaults, byte for byte.** 31 of 31 `@golden` tests pass — the 15 pinned golden scenes AND
the isolation proof's pinned hashes rendered from the named pre-C9a profile. Two new profile
constants, one more factor on the rim line, one more vec4 on the uniform and the CSS tier's doc
comment, and not one pixel moved.

*A record correction, beside and not over the first reading.* Three runs of that suite launched with
`nohup … & disown` were lost to the HARNESS and not to the material — once to
`net::ERR_CONNECTION_REFUSED` on four scenes and twice to the fixture page never reaching
`data-vitrea-ready`. The cause is the detachment: Playwright's `webServer` is a child of the test
process and a disowned run loses it. Run in the foreground the suite passes 31/31 in nine seconds,
twice, at the same commit. The lost runs stay in the file and the clean run is appended after them.
**Nothing in this wave's remaining GPU work should be detached with `disown` if it owns a
`webServer`; `compare.ts` is unaffected and its eight ladder runs detached correctly.**

**At every ladder point, the rim band and nothing else.** Per golden scene, the largest 8-bit
channel delta against the shipped render inside the contour band (3 px of a coverage discontinuity)
and outside it:

| point | inBand, over the scenes | outside | pixels moved outside |
| --- | --- | --- | --- |
| `rimLitExponent 1` | 14 … 79 | **0** | **0** |
| `rimLitExponent 2` | 20 … 90 | **0** | **0** |
| `rimLitAxis` rotated to [−0.9239, −0.3827], exponent 0 | **0** | **0** | **0** |

The largest movement outside any contour band over every scene and every point is **0**. The third
point is the inertness proof from the other side: the axis alone, at the exponent the mechanism is
inert at, moves nothing at all, so `rimLitExponent` is the whole gate.

---

## 7. The recommendation, Decision-Log-2 shaped

> **(a) The lit edge is a symmetric directional factor on the whole rim, with no ambient floor.**
> `rim = rw × (√2·|n · L|)^p × (rimAmplitude × present + rimCollapsed × toneAdapt)`, `L` the exact
> diagonal (−1, −1)/√2 and `p` one constant for both schemes. The symmetric form beats the one-sided
> Lambert 0.148 to 0.288 of normalised RMS over 285 reference bins and the flat rim 0.148 to 0.312;
> the ambient fraction the wave chartered fits to 0.000 on every grouping and is declined under
> C9a §6.2 rather than shipped at zero.
>
> **(b) The axis is the exact diagonal and not the fitted 136.0°.** The rows do not separate the two
> (a thousandth of RMS), and only the diagonal makes the factor equal on all four straight sides,
> which is what makes the amplitude's re-expression closed-form: the `√2` inside the power leaves
> every W23 constant, the CSS tier's rim, and W23's straight-span reads exactly where they are, at
> every exponent. Measured on the ladder: the worst straight-span move is 0.00021 against 0.005.
>
> **(c) The exponent is 1.15, one constant, both schemes.** The reference's joint fit is 1.05; its
> 2x rows give 1.10 light and 1.30 dark; vitrea's own rows against the reference give 1.10 ± 0.22
> light and 1.24 ± 0.17 dark. The schemes overlap, so one constant is what the rows separate. 1.15
> is the value at which the most rows meet both halves of clause 1 (4 of 12, against 2 at 1.00, 2 at
> 1.30 and 0 at 1.45).
>
> **(d) Clause 1's absolute bin bound is not a bound this term can meet, and the parent should
> re-state it.** The mechanism cuts the worst bin error on every solid row by half to three
> quarters — 2x light `dark-solid__rrect-md` 0.2020 → 0.0845, 2x light `mid-dark-solid__capsule`
> 0.2038 → 0.0958, 1x light `dark-solid__rrect-md` 0.1070 → 0.0503, 2x dark `dark-solid__rrect-md`
> 0.0292 → 0.0109, 1x dark 0.0194 → 0.0080, and the two collapsed capsule rows to 0.0024/0.0040 —
> but the residual it leaves is W23's AMPLITUDE, not this wave's shape, and on the light bed that
> residual is 0.05–0.10 against a clause bound of 0.03. The ratio half is reachable: at 1.15 the
> capsule rows land within 13–15 % of the reference, and the dark rrect rows reach −5 % at 1.30.
> The parent should either re-state clause 1 as an improvement on the landed bed (which is what this
> term can be held to) or take the miss with these numbers.
>
> **(e) The exponent may want a second anchor at dpr 2, and the user decides whether to pay for
> one.** The reference's angular contrast is scale-dependent (§8.1): every 2x row wants 1.30–1.45
> and every 1x row 0.85–1.10. `rimWidth2x` is the precedent — a second anchor interpolated by
> `rampAtScale`, inert at dpr ≤ 1. It would be a third constant on evidence four rows wide, so the
> recommendation is to ship ONE exponent now and record the scale dependence, not to fit two.

---

## 8. Every gap the metrics do not catch

**8.1 The reference's angular contrast depends on the scale, and the instrument explains only part
of it.** On the same scene and the same fixture bed, the reference's lit-diagonal bins over its
straight-side bins read 1.07 at 1x and 1.39 at 2x on the dark `dark-solid` capsule, and 0.70 at 1x
against 1.18 at 2x on the light `dark-solid__rrect-md`. The injection test measures the reader's own
arc under-read at 8.5 % at a 22-device-px radius and 2 % at 40, which accounts for roughly a third
of the gap; the rest is the reference drawing a weaker lit contrast at 1x. The band INTEGRAL, which
is conserved under rasterisation and is W23's own contour quantity, is reported beside the peak in
every read and shows the same split (1.07 against 1.39), so this is not an artefact of reading a
peak. **Consequence: at 1x in the LIGHT scheme the reference's corner arcs sit BELOW its straight
sides (0.126 against 0.178 on `dark-solid__rrect-md`), and a factor of the form `(√2|n·L|)^p` is ≥ 1
at the corners by construction — so on those rows the law moves the corners the WRONG WAY.** It is
still a net improvement there (0.1070 → 0.0503 worst bin) because the landed bed is further out
still, but the sign is wrong and it is recorded, not hidden.

**8.2 On a THICK rounded rectangle the reference's rim varies along a straight side, and no function
of the normal can carry it.** `along-span.py` / `along-span.txt`. Read along the first contour row,
the 2x dark `dark-solid__rrect-md`'s top edge runs 0.0442 → 0.0158 from left to right in eighths and
its right edge 0.0120 → 0.0417 from top to bottom — brightest nearest the top-left and the
bottom-right corner, monotone across the whole span and not only near its ends. Three controls say
this is the material and not an artefact:

- **the body.** One CSS px inside the rim the interior is 0.0153 at every depth and every position,
  to four figures. There is no sheen under the rim for the peak to inherit.
- **the silhouette.** A shape sitting a fraction of a pixel askew produces exactly this signature.
  It is not that: on the same bed and the same scale the CAPSULE's top edge has a fitted slope of
  −0.000000 px per px, so there is no rotation in the capture at all; the rrect's own edge is
  straight to a residual RMS of 0.064 px, and the slope it does carry is 0.29 px across a 231 px
  span in the dark fixture against 0.11 px in the light one — the same geometry, so the shift is a
  by-product of the rim's own gradient pulling the half-level crossing, not a rotation, and it is a
  fifth of what the read would need.
- **the background.** Uniform to the last bit at all eight canvas margins, on every fixture read.

It is size-selective — the capsule (44 CSS px short side) and `rrect-sm` (32) are dead flat across
the middle six eighths of their spans, `rrect-md` (96, the size law's own `sizeSpanMax`) and
`rrect-lg` (160) are graded, in both schemes and on both probe grids — which points at the thickness
law rather than at the corner. **This is a term the wave's
chartered form cannot express and the bin statistic cannot see** (the gradation lives WITHIN the
`N`, `E`, `S`, `W` bins, whose means the law matches). It belongs in the wave's Deferred list with
these numbers; the shader has the fragment's own position and the shape's box, so a further
positional term is available if a later wave charters it.

**8.3 The dark scheme's `mid-dark-solid` rows are half unreadable by this instrument.** Their
backdrop (0.0595) is brighter than their body (0.0285), so six to eight of sixteen bins have their
peak outside the declared contour and are excluded. Their reference ratio therefore reads 1.37–1.50
where the unmasked bins read 2.2–2.4. A reader that found the contour from the silhouette rather
than from the declaration would recover them; this one declares the loss instead.

**8.4 A holdout row moves the wrong way and G2's S1 will see it.** `mid-dark-solid__capsule-button`
(holdout, both schemes) has a worst bin error of 0.0124/0.0145 on the landed bed, 0.0087/0.0086 at
exponent 1.00, and then 0.0124/0.0128 at 1.15 and 0.0164/0.0172 at 1.30 — it gets worse above 1.0.
Its reference ratio over the readable bins is 1.37–1.50, the flattest of any solid row, so the
factor overshoots it. Nothing was fitted on it and nothing was captured for it; it is named here so
that G2's dry run is not surprised by it.

**8.5 The reference's profile is sharper than `|cos|^p` in its shoulder.** On the 2x dark
`dark-solid__rrect-md` the reference reads 0.78 of its peak at 45° off the axis and 0.11 at 67.5°,
where a single power law fitted to the first predicts 0.52 at the second. The residual is
concentrated in the `NNE` / `ENE` family of bins and it is the largest single term left in the fit
(worst absolute bin error 0.0090 dark, 0.097 light). A form with a flatter lobe and a wider null
would fit better; no row of any bed separates one, and the wave's clause 1 does not need one.

**8.6 The exponent is one number over a scale-dependent, size-dependent surface.** Per cell the fit
runs 0.65…1.55 with the largest single splits by scale (§8.1) and by shape (the capsule wants
1.10/1.45 where `rrect-md` wants 0.85/1.35 in the same scheme). Carrying one constant is what the
rows support; the spread is the price and it is on the record.

**8.7 By eye.** Not done at this gate — X6 asks for the sheet at a zoom where the arcs are visible
and G0 rendered no sheet. The 4× dark-capsule sheet is G2's, and it should be cut from a capture at
the declared exponent rather than from a ladder point.

---

## 9. The files

| file | what it is |
| --- | --- |
| `read-angular.py` | the instrument (X1) |
| `instrument.sh` / `instrument.txt`, `diagnose.py` | (a) the injection, the parent crosscheck, the geometry diagnostic |
| `run-reads.sh`, `reads/`, `angular-read.txt`, `tables.py`, `tables.txt` | (b) every cell of six profiles on both tiers, and both probe grids |
| `make-candidates.py`, `ladder.sh`, `read-ladder.sh`, `ladder/` | (c) the eight-run scratch ladder and its reads |
| `fit.sh`, `fit-law.py`, `fit-vitrea.py`, `fit-law.txt`, `fit-law.json`, `fit-vitrea.json` | (c) the law on the reference and on vitrea's own pixels, and the straight-span check |
| `along-span.py`, `along-span.txt` | (d) §8.2 — the rim along a straight side, and its three controls |
| `golden-ladder.spec.ts`, `golden-ladder.sh`, `goldens-rerun.sh`, `goldens-attribution.txt` | (c) the goldens (X2) |

Scratch, never committed: `/Users/new/.claude/jobs/5c70e47f/tmp/w24/g0/` — the candidate profile
documents, every ladder capture, the capture logs and the injection rasters. The wave's `DONE`
marker for X4 is written there by `ladder.sh`.
