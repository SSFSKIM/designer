# W13 G1 — the runtime sweep of the RE-FORMED depth ramp (2026-09-03)

The form the first sweep's §7 asked for, turned through the real GPU renderer: the span law
W11c fitted kept UNDERNEATH the ramp as its deep value, the ramp a near-contour excursion
above it. 72 points over both scales. Commands, base and provenance: `README.md` beside
this file.

**Headline. The re-formed law does not reach the wave's stops either, and the reason is
again structural rather than a matter of finding a better point — but it is a DIFFERENT
structure, and it is one the paper model can state in closed form without any capture.**
At 1x, S4 needs a start above 0.600 to move `checkerboard__rrect-sm` at all, and
`checkerboard__rrect-ml`'s band only improves for a start below about 0.583; the two
requirements are disjoint and the reach cannot bridge them, because the reach decides how
much of a surface the excursion covers and not which surfaces it touches. At 2x it is
worse: **the point at which the ramp is inert on every calibration cell is simultaneously
the maximum `ssimBand` on all five of them**, so no point in the 36 raises any 2x band row
at all. §6 shows why from G0's own numbers, and shows that the third form the parent is
considering inherits the same 2x defect.

## 1. The span the law actually reads

`root.ts` passes `Math.min(bounds.width, bounds.height)` — the surface's SHORTER border-box
extent, which is what the renderer takes too ("a 320×44 toolbar is a thin strip whichever
way it is long", `sizeThickness`'s doc). The deep sharp share the re-formed law puts under
the ramp follows from that span through the restored span curve:

| cell | box W × H | span = min(W, H) | first sweep §4's "span" | kDeep(span) | sDeep = 1 − kDeep |
| --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 64 × 32 | **32** | 64 | 0.4000 | **0.6000** |
| `capsule-button` | 120 × 44 | **44** | 120 | 0.4050 | **0.5950** |
| `toolbar-group` | 44 × 44 (×3) | **44** | 44 | 0.4050 | **0.5950** |
| `rrect-md` | 160 × 96 | **96** | 160 | 0.5190 | **0.4810** |
| `rrect-ml` | 224 × 128 | **128** | 224 | 0.6362 | **0.3638** |
| `glass-over-glass` | 220 × 130 (base) | **130** | 220 | 0.6440 | **0.3560** |
| `rrect-lg` | 280 × 160 | **160** | 280 | 0.7638 | **0.2362** |

**The first sweep's §4 table used the LARGER dimension as its "span" column.** That table's
`k` values are not wrong — they were computed from the numbers in the column — but the
column is the box's width, not the span the renderer resolves, so the retired law's spread
was read one cell too far to the right. It is left as recorded; this table is the correction
beside it, not a rewrite. Nothing in §4's mechanism argument turns on it: the retired law
still runs 0.400 to 0.764 across the real spans against the first form's near-flat
projection, which is the same finding with different numbers.

Two thresholds fall straight out of the column on the right, and both are properties of the
FORM rather than of any constant in it:

- **`rrect-sm` sits exactly at `sizeSpanMin`.** Its span is 32, where the span curve is the
  floor exactly, so its deep sharp share is exactly `1 − sizeScatterFloor` = 0.600. The
  excursion is `max(0, s₀ − sDeep)`, so **any start at or below 0.600 leaves that cell
  bit-identical**, at every reach, at both scales. S4 asks for a rise on every checkerboard
  cell; nothing is not a rise.
- **The capsule and the toolbar group are 0.595.** They are the next two up, and they sit
  0.005 below `rrect-sm` rather than anywhere near the thick cells.

## 2. What was swept

1x: 30 points (start {0.55, 0.65, 0.75, 0.85} × reach {20, 30, 50, 80, 100, 150, 200, 300},
two skipped on a port collision — README). 2x: 36 points (start {0.25, 0.35, 0.45, 0.55,
0.65, 0.75} × reach {20, 40, 60, 100, 200, 300}). Plus a 6-point 1x refinement at start
{0.575, 0.61} × reach {50, 80, 100}, which exists only to measure §3's two thresholds
instead of interpolating them.

The wave's declared grid was start {0.55…0.85} × reach {100, 150, 200, 300} at 1x and start
{0.25…0.55} × reach {100, 200, 300} at 2x. **Both were extended before the first capture**,
on §1's reading, and every declared point is kept as a subset. Two reasons, both computable
without a GPU:

- The declared reaches are all longer than any calibration cell's half-span at 1x (the
  half-spans are 16 to 80 CSS px; a reach of 100 device px is 100 CSS px at dpr 1). At a
  reach that long the excursion covers the whole surface and the "near-contour" form
  degenerates into the first form. The projection over each cell's real box, at dpr 1:

  | reach, device px | tb | sm | caps | md | ml | lg | spread |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | span law (no ramp) | 0.405 | 0.400 | 0.405 | 0.519 | 0.636 | 0.764 | **0.364** |
  | 20 | 0.370 | 0.367 | 0.376 | 0.468 | 0.571 | 0.687 | 0.321 |
  | 30 | 0.363 | 0.361 | 0.368 | 0.448 | 0.543 | 0.653 | 0.292 |
  | 50 | 0.358 | 0.357 | 0.361 | 0.415 | 0.494 | 0.591 | 0.235 |
  | 100 | 0.354 | 0.353 | 0.355 | 0.382 | 0.424 | 0.484 | 0.131 |
  | 200 | 0.352 | 0.352 | 0.353 | 0.366 | 0.387 | 0.417 | **0.065** |
  | 300 | 0.351 | 0.351 | 0.352 | 0.361 | 0.375 | 0.395 | 0.044 |

  At the declared reaches the span grading the form exists to keep is mostly gone — 0.065
  of spread at reach 200 against the law's 0.364 — which is the first form's flatness
  returning. Reaches of 20 to 50 device px are where the form is a band at all.
- The declared 2x start ceiling of 0.55 is below `rrect-sm`'s 0.600 and the capsule's and
  toolbar's 0.595, so no declared 2x point could move three of the five cells S4 scores.
  The 2x start axis was extended to 0.65 and 0.75 to cross that threshold.

Every table's `main` row is the W12 close bed with the X6 band rows,
`../../g0/matrix-x6-baseline.json`.

**One asymmetry to hold while reading the deltas.** At 1x the branch equals `main` exactly
wherever the ramp is inert — the widths are device-pixel quantities and dpr 1 leaves them
where they were — so a 1x delta IS the ramp. At 2x the branch already differs from the W12
close before the ramp acts, because it carries candidate A's device-pixel widths: that
pedestal is `rrect-sm` +0.0246, capsule +0.0246, toolbar +0.0044, `rrect-md` −0.0152,
`rrect-ml` −0.0191 on `ssimBand`, and −0.0160 on the worst `ssimMean`. Every 2x number
below is the widths plus whatever the ramp added.

## 3. 1x: the two requirements are disjoint, measured

`ΔssimBand` against the W12 close, the five calibration checkerboard cells:

| point | sm | caps | md | ml | tb | rises | worst ΔssimMean | S1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s₀ 0.55, U 50 | +0.0000 | +0.0000 | +0.0023 | +0.0024 | +0.0000 | 2 | +0.0000 | PASS |
| s₀ 0.55, U 80 | +0.0000 | +0.0000 | +0.0027 | +0.0022 | +0.0000 | 2 | −0.0008 | PASS |
| **s₀ 0.575, U 50** | +0.0000 | +0.0000 | +0.0025 | **+0.0007** | +0.0000 | 2 | +0.0000 | PASS |
| s₀ 0.575, U 80 | +0.0000 | +0.0000 | +0.0025 | **−0.0004** | +0.0000 | 1 | −0.0020 | PASS |
| **s₀ 0.61, U 50** | **+0.0019** | +0.0001 | +0.0018 | **−0.0027** | +0.0004 | 4 | −0.0006 | PASS |
| s₀ 0.61, U 80 | +0.0019 | −0.0004 | +0.0016 | −0.0046 | +0.0002 | 3 | −0.0038 | FAIL |
| s₀ 0.65, U 30 | +0.0037 | +0.0029 | −0.0007 | −0.0055 | +0.0011 | 3 | −0.0016 | PASS |
| s₀ 0.65, U 50 | +0.0044 | +0.0032 | +0.0001 | −0.0078 | +0.0012 | 4 | −0.0021 | FAIL |
| s₀ 0.75, U 50 | +0.0046 | +0.0059 | −0.0083 | −0.0232 | +0.0000 | 3 | −0.0065 | FAIL |
| s₀ 0.85, U 300 | −0.0039 | −0.0007 | −0.0333 | −0.0691 | −0.0063 | 0 | −0.0464 | FAIL |

Full tables: `1x-grid.tables.txt`, `refine.tables.txt`.

**S4 is never met. The best is four of five, and the fifth is always `rrect-ml`.** The two
thresholds are now measured rather than argued:

- Below the start of 0.600 that `rrect-sm` needs, three cells report `+0.0000` — not "small",
  exactly zero, at every reach in the grid. The refinement's `s₀ 0.575` row is the same.
- `rrect-ml`'s band is +0.0007 at s₀ 0.575 and −0.0027 at s₀ 0.61, both at reach 50, so it
  crosses zero at **s₀ ≈ 0.583** — **0.017 below the 0.600 the smallest cell needs**. The
  window in which both could hold is empty.

The reach cannot close that gap, and the grid shows why: across every start, changing the
reach moves the SIZE of each cell's response and never its SIGN. The reach sets how much of
a surface lies under the excursion; whether a surface is touched at all is decided by
`s₀ − sDeep(span)`, which has no reach in it.

Best on the wave's own priorities: **s₀ 0.61, reach 50** — S1 passes at −0.0006, four cells
rise, `rrect-ml` falls 0.0027. Runner-up **s₀ 0.55, reach 50** — S1 passes at exactly
+0.0000 and the two cells that move both rise, but three cells are untouched. Neither meets
S4, and the wave's S2/S3 are 2x stops that §5 disposes of.

## 4. 1x interior, as a check

The 1x interior improves where the ramp acts. `interiorStdDev` web against native:
`rrect-md` 0.0994 → 0.1102 against 0.1131, `rrect-ml` 0.0769 → 0.1022 against 0.0865 at
s₀ 0.55 reach 100. `rrect-ml` overshoots — the ramp puts more structure into it than the
reference has — which is the same overshoot the first sweep recorded on the large spans, in
a smaller amount. The 1x interior is not a stop in this wave; it is recorded so the
overshoot is on the record beside the band it was bought with.

## 5. 2x: the ramp cannot raise any band row at all

`ΔssimBand` against the W12 close (widths pedestal included), and the interior gap
`max |isdW − isdN|` over the five cells:

| point | sm | caps | md | ml | tb | rises | max Δisd | worst ΔssimMean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **s₀ ≤ 0.35, ANY reach (12 points)** | **+0.0246** | **+0.0246** | **−0.0152** | **−0.0191** | **+0.0044** | 3 | **0.0071** | −0.0160 |
| s₀ 0.45, U 20 | +0.0246 | +0.0246 | −0.0152 | −0.0238 | +0.0044 | 3 | 0.0071 | −0.0172 |
| s₀ 0.45, U 300 | +0.0246 | +0.0246 | −0.0152 | −0.0354 | +0.0044 | 3 | 0.0146 | −0.0248 |
| s₀ 0.55, U 20 | +0.0246 | +0.0246 | −0.0179 | −0.0298 | +0.0044 | 3 | 0.0071 | −0.0188 |
| s₀ 0.65, U 20 | +0.0235 | +0.0235 | −0.0232 | −0.0364 | +0.0016 | 3 | 0.0076 | −0.0205 |
| s₀ 0.75, U 300 | +0.0135 | +0.0107 | −0.0601 | −0.1039 | −0.0113 | 2 | 0.0628 | −0.0568 |

Full table: `2x-grid.tables.txt`.

**All twelve points at start 0.25 and 0.35 report identical numbers to four decimals across
six different reaches.** That is the signature of an excursion clamped to zero on every
scored cell (the smallest deep sharp share among them is `rrect-ml`'s 0.3638), and it means
those rows are the device-pixel widths alone with the ramp contributing nothing.

**The inert point is the maximum `ssimBand` on all five calibration cells**: `rrect-sm`
0.9663, capsule 0.8879, `rrect-md` 0.9163, `rrect-ml` 0.9205, toolbar 0.7476. Not one of the
36 points beats it anywhere. So at 2x the sweep's answer is that the best available action
is no action: the ramp is strictly harmful on this bed.

**S3, and the question of whether any point preserves §5.58 §2's interior while raising a
band row.** At the inert point the interior is exactly the widths-alone reading:

| cell | main web | inert web | native | gap | S3 (≤ 0.005) |
| --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 0.1372 | 0.1647 | 0.1636 | 0.0011 | PASS |
| `capsule-button` | 0.1189 | 0.1500 | 0.1552 | 0.0052 | FAIL |
| `rrect-md` | 0.0973 | 0.1260 | 0.1272 | 0.0011 | PASS |
| `rrect-ml` | 0.0746 | 0.1029 | 0.1018 | 0.0010 | PASS |
| `toolbar-group` | 0.1203 | 0.1510 | 0.1581 | 0.0071 | FAIL |

Those four thick/small numbers reproduce the charter's Grounding Baseline for §5.58 §2
(`rrect-md` 0.1260 against 0.1272, `-ml` 0.1029 against 0.1018, `-sm` 0.1647 against 0.1636,
capsule 0.1500 against 0.1552) cell for cell, which is the check that this branch carries
candidate A's widths unchanged. Three of the five are inside S3's 0.005; the capsule misses
by 0.0002 and the toolbar group by 0.0021.

**The answer is no, and for a stronger reason than "no point does both".** No 2x point
raises any band row at all, so the conjunction is empty by its second clause alone. And the
interior degrades monotonically with any ramp action: the maximum gap goes 0.0071 → 0.0089 →
0.0146 → 0.0273 → 0.0628 as the start and reach grow. The best 2x interior on record and the
best 2x band rows on this bed are the same configuration, and it is the one where the ramp
does nothing.

## 6. Paper section: what G0 says the excursion should be, and what the third form can do

No GPU. `paper.py` computes all of it; `paper.txt` and `paper-fit.txt` are its output.

### 6.1 The excursion the reference implies, per cell and scale

G0's start-by-cell readings (`../../g0/g0-ramp.md` §1's read-off table for the thick spans
and its finding 4 for the thin ones) set against the code's `sDeep(span)` from §1:

| cell | span | sDeep | G0 s₀ 1x | s₀ − sDeep 1x | G0 s₀ 2x | s₀ − sDeep 2x |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 32 | 0.6000 | 0.637 | **+0.0370** | 0.483 | **−0.1170** |
| `capsule-button` | 44 | 0.5950 | 0.642 | **+0.0470** | 0.437 | **−0.1580** |
| `toolbar-group` | 44 | 0.5950 | 0.642 | **+0.0470** | 0.437 | **−0.1580** |
| `rrect-md` | 96 | 0.4810 | 0.512 | **+0.0310** | 0.192 | **−0.2890** |
| `rrect-ml` | 128 | 0.3638 | 0.501 | **+0.1372** | 0.179 | **−0.1848** |
| `rrect-lg` | 160 | 0.2362 | 0.410 | **+0.1738** | 0.141 | **−0.0952** |

**At 1x every cell's implied excursion is positive**, so the form pushes in the right
direction — but by only +0.031 to +0.047 on the four cells at spans 32 to 96, which is why
§3's usable window is so narrow: the reference wants a start of ≈0.64 on the thin cells and
≈0.51 on `rrect-md`, and one number cannot be both when their deep values are 0.600 and
0.481.

**At 2x every cell's implied excursion is negative**, by 0.095 to 0.289. The reference's
sharp share at the contour at 2x is BELOW vitrea's deep value everywhere. An excursion that
can only add sharpness above the deep value has the wrong sign at every 2x cell, which is
exactly what §5 measured on the GPU. §5 is not an unlucky grid; it is this table.

### 6.2 The third form at its G0-pinned constants

s₀(span, dpr) = thin + (thick − thin) · `sizeThickness`(span), `sizeThickness` being the
material's existing curve, smoothstep(`sizeSpanMin` 32, `sizeSpanMax` 96), the knee at 64
the face and the shadow already blend across. Deep value the restored span law; reach a
length in device px. Constants as pinned: 1x thin 0.64 / thick 0.47 / reach 120; 2x thin
0.46 / thick 0.17 / reach 100.

**dpr 1:**

| cell | span | sizeThickness | s₀(span) | sDeep | excursion | moves? |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 32 | 0.0000 | 0.6400 | 0.6000 | +0.0400 | YES |
| `capsule-button` | 44 | 0.0923 | 0.6243 | 0.5950 | +0.0293 | YES |
| `toolbar-group` | 44 | 0.0923 | 0.6243 | 0.5950 | +0.0293 | YES |
| `rrect-md` | 96 | 1.0000 | 0.4700 | 0.4810 | **−0.0110** | **no** |
| `rrect-ml` | 128 | 1.0000 | 0.4700 | 0.3638 | +0.1062 | YES |
| `glass-over-glass` | 130 | 1.0000 | 0.4700 | 0.3560 | +0.1140 | YES |
| `rrect-lg` | 160 | 1.0000 | 0.4700 | 0.2362 | +0.2338 | YES |

The thin/thick split does what the single start could not: it moves the three small cells
AND the large ones. It fails on exactly one cell, `rrect-md`, and by a hair — the thick
start 0.47 sits 0.011 below that cell's deep sharp share of 0.481, so the excursion clamps
to zero there. `rrect-md` is at span 96, which is `sizeThickness`'s saturation point, so it
is the first cell to receive the thick start in full while still carrying a fairly light
deep value. **A thick start anywhere above 0.481 moves it**; G0's own `rrect-md` reading is
0.512, which is above 0.481, so the pinned 0.47 is below what G0 read on that cell rather
than a limit of the form. This is worth one more paper check before any capture: the thick
constant fitted to G0's thick cells jointly is ≈0.47 because `rrect-lg`'s 0.410 pulls it
down, and `rrect-md` is the cell that pays.

**dpr 2:**

| cell | span | sizeThickness | s₀(span) | sDeep | excursion | moves? |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 32 | 0.0000 | 0.4600 | 0.6000 | −0.1400 | **no** |
| `capsule-button` | 44 | 0.0923 | 0.4332 | 0.5950 | −0.1618 | **no** |
| `toolbar-group` | 44 | 0.0923 | 0.4332 | 0.5950 | −0.1618 | **no** |
| `rrect-md` | 96 | 1.0000 | 0.1700 | 0.4810 | −0.3110 | **no** |
| `rrect-ml` | 128 | 1.0000 | 0.1700 | 0.3638 | −0.1938 | **no** |
| `glass-over-glass` | 130 | 1.0000 | 0.1700 | 0.3560 | −0.1860 | **no** |
| `rrect-lg` | 160 | 1.0000 | 0.1700 | 0.2362 | −0.0662 | **no** |

**At 2x the third form at its G0-pinned constants moves nothing — not one cell, at any
reach.** Every start is below its cell's deep value. The thin/thick grading is a 1x
improvement over the second form and changes nothing at all at 2x, because the defect at 2x
is not that the start is one number: it is that the whole reference lies on the heavy side
of vitrea's deep value and the excursion is one-signed. S4 at 2x is unreachable for the
third form as stated, exactly as it is for the second.

### 6.3 The thin cells at 2x, plainly, and what a scale term on the floor would have to be

G0 §1's finding 4 says it directly: the reference's thin surfaces read a sharp share of
0.483 (`rrect-sm`) and 0.437–0.480 (capsule) at 2x, while "vitrea's `sizeScatterFloor` 0.4
gives them a sharp share of 0.60 / 0.595, which at 1x is nearly right and at 2x is 0.13–0.16
too high". **The form as stated cannot express a deep value below the floor** — the floor IS
the deep value at `sizeSpanMin`, and the excursion only adds sharpness on top of it. So on
the thin cells at 2x the second form is 0.117 to 0.158 too sharp before it starts, and can
only make that worse.

The second form's 2x grid answers the parent's question about whether those cells move at
all and in which direction, and the answer is unambiguous: at every start at or below 0.595
they do not move (twelve points identical to four decimals), and at start 0.65 and 0.75 —
the only two that clear the threshold — they move DOWN, `rrect-sm` from +0.0246 to +0.0235
and +0.0196 and the toolbar from +0.0044 to +0.0016 and −0.0045. **The one direction the
ramp can move them at 2x is the wrong one**, which is what §6.1's negative excursions
predict.

What would a 2x deep value have to be? Reading G0's contour value as the deep value it needs
(`kDeep = 1 − s₀`):

| cell | span | required kDeep 2x | code kDeep | shortfall |
| --- | --- | --- | --- | --- |
| `rrect-sm` | 32 | 0.5170 | 0.4000 | **+0.1170** |
| `capsule-button` | 44 | 0.5630 | 0.4050 | **+0.1580** |
| `rrect-md` | 96 | 0.8080 | 0.5190 | **+0.2890** |
| `rrect-ml` | 128 | 0.8210 | 0.6362 | **+0.1848** |
| `rrect-lg` | 160 | 0.8590 | 0.7638 | **+0.0952** |

Fitting a span curve of the same shape to that column (`paper-fit.txt`):

- **floor 0.530, band top 112, and a CEILING of 0.840** — residual RMS 0.0148, a good fit.
- With the ceiling pinned at 1 and only the floor and the band top free, the best is floor
  0.570, band top 206, residual RMS 0.0612 — **four times worse**, over-light at `rrect-md`
  (0.702 against 0.808) and over-heavy at `rrect-lg` (0.926 against 0.859).

So a scale term on the floor alone does not reach G0's reading. The 2x deep law needs three
things the 1x one does not have: a floor about **0.13 higher** (0.53 against 0.40), a knee
about **half as far out** (≈112 against 256), and a top that **saturates below full
heaviness** (≈0.84 rather than 1). That last one is the constant the current form has no
name for at all, and it is what the negative sharp shares in G0 §1's deep 2x windows were
signalling.

## 7. What this asks of the declaration

Four findings, as this instrument found them.

1. **The re-formed law cannot meet S4 at 1x**, and the obstruction is arithmetic in the
   form: `rrect-sm` sits at `sizeSpanMin`, so its deep sharp share is exactly
   `1 − sizeScatterFloor` and no start at or below 0.600 can touch it, while `rrect-ml`'s
   band only improves below ≈0.583. Measured, not interpolated (§3). Best available: four of
   five at s₀ 0.61 / reach 50, S1 passing at −0.0006.
2. **At 2x the ramp is strictly harmful.** The inert configuration is the maximum on all
   five calibration band rows and carries the best interior on record (§5.58 §2's, three of
   five cells inside S3). No point raises any band row; every point that acts degrades the
   interior. S2 and S3 are therefore not questions this form gets to answer.
3. **The 2x defect is a deep-value defect, not a band defect** (§6.1, §6.3). The reference at
   2x lies on the heavy side of vitrea's deep value at every cell by 0.095 to 0.289 in sharp
   share. A one-signed excursion above the deep value cannot express it at any constants, so
   the third form inherits the failure unchanged: at its G0-pinned 2x constants it moves not
   one cell. Whatever lands at 2x has to move the span law itself — floor ≈0.53, knee ≈112,
   and a ceiling ≈0.84 that the current form has no constant for.
4. **The third form is a real 1x improvement and misses one cell by 0.011.** Grading the
   start thin-to-thick across `sizeThickness` breaks §3's disjointness — it moves the three
   small cells and the three large ones — and fails only on `rrect-md`, whose deep sharp
   share 0.481 sits just above the pinned thick start 0.47. G0's own `rrect-md` start is
   0.512. That is a constants question rather than a form question, and it is answerable on
   paper before any capture.

No confirmation run was made and holdout was not read (README). `rrect-lg` and
`glass-over-glass` appear above only inside computations that read no fixture.
