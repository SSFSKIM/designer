# W20 — the capsule's corner on the GPU tier (2026-09-05)

**Status: OPEN — chartered 2026-09-05 on wave Decision Log 23 (c), the first GPU-tier wave under
the amended discipline; found by the user's eye on the W19 landing sheet ("where it was not round
but rectangular") and pinned the same day (claims §5.83). G0 opens on Decision Log 1's
recommendations.**

Composite spec: design at the top; Decision Log, Surprises, Deferred and Revision Notes at the
tail. Parent: `2026-08-28-post-v1-wave.md` (the W20 row; Decision Log 23). The geometry this wave
corrects is C3's two-reference corner model (parent design spec Decision Log #22 (a)) and S2's
Apple corner fit (`spikes/s2-geometry-field`); the instrument it corrects is the shape axis's
declared search region (wave Decision Log 15; `packages/calibration/src/component-region.ts`).
Successor by Decision Log 23 (c): W21, the dark scheme, opens at this wave's close on the corrected
capsule cells.

## Purpose

The renderer resolves every surface's corner from its channel values:
`packages/renderer-webgpu/src/instances.ts` takes `surface.reference ?? "apple-continuous"` and
calls `resolveFromChannels(channels, reference, surface.family)`, which hands the radius to
`resolveCorner(size, radius, smoothing, reference)` and never reads the family. Under the Apple
reference `resolveCorner` clamps the radius so that Apple's measured corner reach fits the side —
`r = min(radius, min(halfW, halfH) / 1.52866495)`, the saturation ratio 0.327083 — and
`buildAppleContour` does the same for the contour. The geometry package's spec resolver
(`resolveShape`) makes a `capsule` exact (radius = budget, smoothing 0, on the Figma reference),
but nothing on the render path goes through it.

So on the GPU tier a 120 × 44 capsule draws with corners of radius 14.39 CSS px instead of 22
(28.78 device px instead of 44 at 2x), and a 44 × 44 circle draws as a rounded square. A smaller
radius in the same box is a fuller shape: the drawn shape is a superset of the stadium, and the
difference is four shoulders at the ends, 232 px per capsule at 1x (4.8 % of the surface), 948 at
2x, 696 for the toolbar's three circles. Everything the field drives — the fill, the lens, the rim,
the highlight, the tint — stops at the clamped contour; the backdrop blur, masked by the DOM's own
stadium, does not. Against Apple the shoulders read a mean |ΔL| of 0.38 over the photo, 0.35 over
the checkerboard and 0.13 over light-solid where the body reads 0.036, 0.067 and 0.006, and a ring
2 px outside the clamped contour reads 0.004–0.012: the material stops exactly there
(`packages/calibration/results/2026-09-05-w20-capsule-corner/finding/`). The CSS tier draws the
DOM's shape and is unaffected.

The matrix never saw it. The shape axis bounds both sides' silhouettes to the declared component
region, and a surface larger than declared fills the region exactly: `silhouetteAreaWeb` =
`componentRegionArea` = 4872, IoU 1.000, contour p95 0, corner-curvature delta 0 on every capsule
cell of the bed, both tiers, since v1. The bed carries 19 capsule scenes and 2 toolbar-group
scenes — 21 of 40 at every profile — so every GPU-tier row on more than half the bed was measured
through the shoulders. The same clamp reaches every author: the react binding's `capsule` prop and
the demo's capsule scenes go through this path, and any `fixed-rounded-rect` host whose radius
exceeds 0.327 of its short side (the default host shape's radius 12 on anything under 37 px) is
clamped the same way. Pill buttons, circles and `rounded-full` are the most common control shapes
on the web.

This wave makes the capsule exact on the render path under every reference, measures what Apple
does to a `.continuous` rounded rectangle past the saturation ratio instead of assuming it, gives
the shape axis an instrument that can see a surface larger than declared, and lands the corrected
geometry on the canonical bed with the GPU tier's capsule cells re-read. It fits no constant and
touches no material law, so the profile hash and the matrix keys do not change.

## Parent-Level Acceptance

- **A capsule is a stadium on the GPU tier.** `resolveFromChannels` with `family: "capsule"`
  resolves the corner as `resolveShape` does — radius at the budget, effective smoothing 0 — under
  both references; a geometry unit test asserts it at 120 × 44 and 44 × 44 (a circle), and
  `toContour` of the resolved capsule matches a stadium to the contour tolerance S2 declared.
- **Apple past the saturation ratio is measured, not assumed.** A native probe of
  `RoundedRectangle(cornerRadius: r, style: .continuous)` on a 120 × 44 box at r ∈ {14, 16, 18,
  20, 22} (ratios 0.318…0.5) with `Capsule()` beside it, over `light-solid` and `checkerboard` at
  1x, read by pixel contour; the law Apple follows recorded in claims. The renderer's Apple
  reference follows that law above the ratio, or — if one law does not fit the probe within the
  instrument's floor — the saturation stays a documented refusal with the probe's readings beside
  it (the user's decision at G1, Decision Log 1). Either way the capsule is exact by the clause
  above.
- **The shape axis sees a surface larger than declared.** The capsule cells read what the pixels
  say before the fix (IoU under 1, a positive contour distance, the shoulders' area) and return to
  ~1.000 after; the instrument's recovery of a known dilation is recorded beside its first reading
  (X4). The rounded-rectangle cells, whose ratios are all under 0.327 (rrect-sm 0.25, rrect-md
  0.208, rrect-ml 0.211, rrect-lg 0.2125, glass-over-glass 0.185 and 0.286), do not move on it.
- **The bed improves where the shoulders were and moves nowhere else.** On the canonical rebuild
  every GPU-tier capsule and toolbar-group cell improves on OKLab ΔE and SSIM against Apple or its
  change is attributed by pixel; no GPU-tier rounded-rectangle or glass-over-glass cell moves; the
  CSS tier is byte-identical on every capture (this wave touches no CSS code); the seven floors
  keep; the predicate list is re-read and every change attributed; the goldens that move are
  attributed through the isolation proof.
- **The user's eye.** The landing sheet puts the GPU capsule beside Apple's and the CSS tier's at
  the W19 sheet's zoom on the bed's capsule cells and the toolbar; the round ends are visible as
  such.
- The rebuild once from the main checkout; the holdout read once, at the landing.

## Grounding Baseline (the W19 bed, 2026-09-05, `802a53e`)

- Canonical `results/matrix.json`: 229 cells; the GPU tier byte-identical to the W18 bed
  (claims §5.82). Floors: the seven of W17/W18/W19 on rrect-md, rrect-ml, glass-over-glass and
  rrect-lg — none on a capsule cell.
- `photo__capsule-button__rest` at 1x light: GPU ΔE 0.0027 mean over the primary profile's
  capsules, SSIM 0.988; the shoulders are 0.36 % of the cell and 4.8 % of the surface, which is how
  a 0.38 error hides under those means.
- The goldens: eleven scenes, none a capsule; `rim-two-references` draws under both references
  and is the one to watch at G1.
- The finding's evidence: `results/2026-09-05-w20-capsule-corner/finding/` — `shoulders.py`,
  `shoulders.txt`, `corners.png`, `shoulders.png`, `css-vs-gpu.png`.

## Design (advisory unless marked)

**The capsule (binding).** A capsule's corner is its budget under any reference; the fix belongs
in `resolveFromChannels`, which is the one path a morph takes every frame and the one the renderer
takes, so that an interpolated capsule and an authored one resolve the same. `morph.ts` refuses a
morph across references; a capsule resolved on the Figma reference morphing into a rounded rect on
the Apple reference must still be legal (it is today only because the capsule was silently on the
Apple reference), so G1 either resolves the capsule under the reference it was given with the
radius unclamped and smoothing 0, or teaches the morph solver that the capsule limit is shared by
both references. The first is simpler and is the recommendation.

**The Apple reference past the ratio (advisory, resolved by G0).** Three candidates for what Apple
does when `reach · r` no longer fits the side: keep the radius and compress the shoulder (reach →
budget, the corner tending to a circular arc at r = budget — the reference family's own clamp
policy, which `corner.ts` calls exact at the capsule limit); keep the reach and clamp the radius
(what vitrea does now, and what `apple.test.ts` pins under the name "Apple's budget policy is its
own", without a measurement behind it — S2 fitted the corner below the ratio only); or something
else the probe will show. The harness draws `Capsule()` for the bed's capsules, a circular stadium
by definition, so the bed does not answer this; the probe does. If the first candidate holds within
the instrument's floor, `resolveCorner` and `buildAppleContour` take `r = min(radius, budget)` and
`reach = min(APPLE_REACH · r, budget)`, with the dump's shoulder points compressed along the edge
by `reach / (APPLE_REACH · r)` and the pseudo-SDF coefficients re-derived at the compressed reach
(the Figma family at the smoothing ceiling is the closed form S2 already validated at the capsule
limit); the transition at the ratio must be continuous in r, which the reach formula gives.

**The instrument (advisory).** The declared region stays the shadow's fence (Decision Log 15's
reason is intact), dilated by the corner budget on the sides the shadow does not reach — left,
right and above — so a surface up to its bounding box shows; below, the region's edge stays where
the shadow makes it necessary. The alternative — the tier's own raster silhouette from the optics
canvas's alpha on a transparent page — is exact but blind to the DOM-masked blur, which is a
surface too; G0 decides with the numbers. The dilation must not admit the outer shadow on the
sides (W8's offset is vertical; W14 measured the span law) and must not move any
rounded-rectangle cell.

**What does not change (binding).** No material constant; the profile hash; the CSS tier's code;
the matrix keys. The capsule cells' material rows (interior, rim, shadow) will move because the
region they are read in no longer holds shoulders — attributed, not fitted.

## Children

### G0: The finding on the instrument, and Apple past the ratio — spike

Purpose: make the matrix see what the pixels show, and replace the assumed Apple policy with a
measured one. Deliverables: the shape axis's dilated region (or raster silhouette) behind a flag,
run over the W19 bed to scratch — the capsule cells' IoU / contour / curvature moving off 1.000 /
0 / 0, the rounded-rectangle cells unmoved, the recovery of a synthetic 4 px dilation recorded
(X4); the native probe (`scenes-w20-probe.json`: the five ratios and the capsule over two
backgrounds at 1x) captured in the harness and its contours read; the law fitted or the refusal
written; the goldens' and the bindings' exposure listed (`rim-two-references`; the react `capsule`
prop; the demo's capsule scenes; `DEFAULT_HOST_SHAPE` under 37 px). Findings to
`results/2026-09-05-w20-capsule-corner/g0/g0-findings.md`; claims §5.84. Stops: none — a spike.
Its bed: the W19 bed at `802a53e`.

### G1: The fix declared and dry-run — controlled

Purpose: the capsule exact on the render path; the Apple reference above the ratio per G0's law or
left as a documented refusal (the user's decision); the instrument landed as the axis's default;
the geometry unit tests (the capsule under both references; `apple.test.ts`'s saturation test
re-pointed with its reason; the morph across the capsule limit); the goldens attributed through
the isolation proof; the whole GPU tier dry-run to scratch at every profile with the holdout
untouched, the capsule and toolbar cells' before/after tables and the rounded-rectangle cells'
byte-identity. Stops (declared before the run): any rounded-rectangle or glass-over-glass GPU
capture moving by more than the frame-timing pair's code; any capsule cell worsening on ΔE or
SSIM against Apple; the CSS tier moving at all; a golden moving without a pixel attribution.
Claims §5.85.

### G2: The landing and its referee — controlled

Purpose: merge; the canonical rebuild once from the main checkout (GPU tier, every profile; the CSS
tier re-run and verified byte-identical); the referee against the W19 bed (`g2-verify.py` in
W19's shape: counts, CSS byte-identity, GPU capsule cells before/after, rounded rectangles
byte-identical, the seven floors, the predicate re-read, the cross-tier coherence on capsule
cells); the sheets at both scales; the chain green; recomposition against the acceptance above;
claims §5.86; W21 opens. The holdout read once, here.

## Cross-Child Contracts

- **X1 — the instrument before the fix.** G0's instrument reads the defect before G1 removes it;
  G1's dry run is measured on that instrument, not on the clipped one.
- **X2 — no fitted constant.** The wave is geometry and instrument; the material profile document
  and its hash do not change; if a capsule cell's material row moves, the attribution is the
  region, never a constant.
- **X3 (inverse) — the CSS tier byte-identical.** As W18 and W19 held the GPU tier fixed, this
  wave holds the CSS tier fixed, verified on every capture at G1 and G2.
- **X4 — the instrument's recovery.** A known dilation injected into a capture and recovered by
  the axis, recorded beside the first reading.
- **X5 — by eye.** The landing sheet at the W19 sheet's zoom on capsule and toolbar cells,
  native | CSS | GPU landed | GPU before.

## Ordering & Dependency Map

G0 → G1 → G2 → W21 (the dark scheme; wave Decision Log 23 (c)). The native probe rides inside G0
behind its TCC gate as W18's and W19's did; if the grant is not available in the session, G0
closes on the instrument and the capsule fix proceeds (the capsule needs no probe), and the Apple
reference above the ratio stays a documented refusal until the probe runs.

## Risks & Mitigations

- **The probe's contour at ratios near 0.5 is one pixel of curvature difference.** Read at 1x over
  `light-solid` (a clean delta) and over the checkerboard; fit the corner's circle radius per rung
  and compare to r; the instrument's floor is the grid (0.5 px), declared before reading.
- **The morph solver refuses the capsule after the fix.** Covered by G1's unit test on the morph
  across the capsule limit; the fix chooses the resolution that keeps it legal.
- **The dilated region admits the shadow on some cell.** G0 runs the instrument over every cell
  and lists any rounded-rectangle cell that moves; the dilation is per-side.
- **The capsule cells' floors.** None exist; the seven floors are on rounded rectangles and the
  stack, which do not move.

## Deferred / Out of Scope

- **Authored rounded rectangles above the ratio under the Apple reference**, if the probe shows a
  law the wave cannot model within its bound: recorded with the probe's readings, its own charter.
- **Per-corner radii** (W5, re-deferred at the cut) — untouched.
- **The CSS tier's contour line.** In the same view the CSS tier reads a one-pixel line of
  0.12–0.17 |ΔL| along the whole stadium contour (`shoulders.txt`, the CSS ring) — the rim band on
  the CSS tier, W16 Deferred, seen again; recorded, not this wave's.
- **The dark scheme** — W21, next by Decision Log 23 (c), on the corrected capsule cells.

## Tracking Map

| child | where | status |
| --- | --- | --- |
| G0 | `packages/calibration/results/2026-09-05-w20-capsule-corner/g0/`, `apps/reference-apple/scenes-w20-probe.json` | OPEN |
| G1 | — | not started |
| G2 | — | not started |

## Decision Log

### Decision Log 1 — the cut, the binding rules, and what the user decides (2026-09-05)

**The cut.** Three children as W19's: a spike that builds the instrument and measures Apple past
the ratio, a controlled gate that declares and dry-runs the fix, a controlled landing. The capsule
fix does not wait on the probe; the Apple reference's policy above the ratio does.

**Bound here.** The capsule is a stadium under every reference on the render path. No constant is
fitted. The CSS tier does not move. The instrument lands before the fix is measured.

**Put to the user, with the recommendation.**

1. *The Apple reference above the saturation ratio.* (a) Measure in G0 and model in G1 if one law
   fits the probe within the grid's floor; else leave the saturation as a documented refusal with
   the readings beside it — **recommended**: the capsule is fixed either way, and the general case
   deserves a measurement rather than a second assumption. (b) Model the reference family's
   smoothing-ceiling policy now without the probe. (c) Leave the general case as it is and fix
   only the capsule.
2. *The instrument.* (a) The declared region dilated per side by the corner budget where the
   shadow does not reach — **recommended**: keeps Decision Log 15's fence and admits the shoulders.
   (b) The tier's own raster silhouette from the optics canvas. (c) Both, the dilation as the
   default and the raster as a diagnostic.
3. *The order against W21.* (a) This wave first, W21 on the corrected cells — **recommended and
   ruled by wave Decision Log 23 (c)**. (b) W21 first.

Under the user's standing instruction ("for decisions, all according to your recommendation") the
recommendations execute unless the user says otherwise; G1's landing keeps the user's eye's veto.

## Surprises & Discoveries

- **The finding is the user's (2026-09-05).** Nineteen waves of sheets, and the question "is fixing
  the geometry bug of the WebGPU tier, where it was not round but rectangular, also in
  consideration?" is what put the parent's eye on the GPU column. The parent had looked at the
  same sheet and read tint, not shape. Recorded in the wave doc's Surprises and as a memory note.

## Outcomes & Retrospective

(at recomposition)

## Revision Notes

- 2026-09-05: v1 — chartered on wave Decision Log 23 (c) from claims §5.83, the finding pinned
  the same day; Decision Log 1 written; G0 opens.
