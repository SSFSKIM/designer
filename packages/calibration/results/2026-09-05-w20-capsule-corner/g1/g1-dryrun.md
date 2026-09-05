# W20 G1 — the corrected corner declared and dry-run (2026-09-06)

Executes W20 Decision Log 2 ruling 1 on the design it made binding, and measures it on G0's
instrument (contract X1). Nothing canonical was written: the dry run's matrix and captures are
under `/Users/new/.claude/jobs/5c70e47f/tmp/w20/g1/`, the canonical `results/matrix.json` and
`web-captures/` were read only. Holdout was not read. The CSS tier was not run and no CSS code
moved (contract X3).

Branch `worktree-agent-a463558bb21d8d14b`, from `main` at `fef542b`.

---

## 1. The change

`resolveCorner`'s `apple-continuous` branch (`packages/geometry/src/shape.ts`) no longer clamps the
radius. It takes `r = min(radius, budget)` with `budget = min(halfW, halfH)`, and
`reach = min(APPLE_REACH * r, budget)`. Below the crossing at `APPLE_SATURATION_RADIUS_RATIO`
(0.327083 of the short side) that is bit-for-bit what it did before: S2's Apple-direct fit, the
published reach `APPLE_REACH * r`, `APPLE_RSUP`/`APPLE_RSUPN`'s coefficients, and Apple's own dump
as the contour. Above the crossing the corner resolves through
`resolveCornerConstruction(halfW, halfH, r, APPLE_CONTINUOUS_SMOOTHING_SEED)`, whose own budget
clamp yields exactly the effective smoothing `reach / r - 1`, and takes the reference family's
coefficient table at that smoothing — `coefficientsAt(FIGMA_RSUPN_TABLE, sEff)`, as the Figma
reference already does — because the curve there is that family's construction and not Apple's dump.
The `reference` field stays `"apple-continuous"`.

`ResolvedCorner` gains `saturated`, whose meaning is now "the shoulder is compressed" rather than
"the radius was clamped and the shape is mismodelled"; the renderer resolves through
`resolveCorner` and never builds a contour, so carrying the flag only on the contour builder was
half of why this survived nineteen waves (§5.84 §7). `buildAppleContour` makes the same split for a
caller that has a radius rather than a resolved shape, and `toContour` builds a compressed corner
through `buildReferenceContour` from the resolved corner itself, so the contour and the field the
renderer evaluates come from one set of numbers. `governorFieldParams` re-derives through
`resolveCorner` and therefore takes the same policy for the `rsup` family. `resolveShape`'s capsule
branch is untouched — it was already exact — and the render path now agrees with it exactly.

A capsule is a stadium by construction and needs no family special case: at `r = budget` the reach
is the budget, the effective smoothing is 0, the coefficient table's row at 0 is exactly zero, and
the cubics degenerate to the circular arc. That is also what Apple draws, since `Capsule()` reaches
Core Animation as `RoundedRectangle(cornerRadius: h/2, style: .continuous)` (§5.84 §1).

## 2. The crossing, and whether a blend was needed

**No blend.** At `r = budget / APPLE_REACH` the Apple-direct contour and the reference
construction at the same reach are two different curves. Their symmetric Hausdorff distance,
sampled at 0.01 px, is a constant fraction of the radius because the curves are similar in r:

| box | budget | r* | Hausdorff | as a fraction of r |
| --- | --- | --- | --- | --- |
| 120 × 44 (the bed's capsule) | 22 | 14.3916 | **0.0930 px** | 0.0064609 |
| 64 × 30 | 15 | 9.8125 | **0.0635 px** | 0.0064662 |
| 44 × 44 (the toolbar's circle) | 22 | 14.3916 | 0.0930 px | 0.0064609 |
| 160 × 96 (rrect-md) | 48 | 31.3999 | 0.2027 px | 0.0064568 |
| 280 × 160 (rrect-lg) | 80 | 52.3332 | 0.3379 px | 0.0064562 |

The calibration grid's floor, declared by G0 before it read anything, is 0.5 px. The crossing is
under it at every bed size — 0.093 px at the 44 px short side and 0.063 px at the 30 px one — so
W20 Decision Log 2's condition for a blend is not met and the switch is taken as it stands.
Pinned as `CROSSING_PER_R` in `packages/geometry/test/apple-saturation.test.ts`.

The reach and the effective smoothing are continuous in r across the crossing (both tests in the
same file): at `r* ± 1e-12` the reach is 22 to eight decimals and the smoothing is the Apple seed
to eight, and above the crossing the reach stays pinned at the budget while the smoothing falls
monotonically to exactly 0 at the capsule limit. Sweeping r through the crossing at 0.002 px steps,
the largest step in contour position is **0.0929 px** — the crossing's own distance, at the one
step that straddles it and nowhere else. What is NOT continuous there is the correction
coefficient vector `k`, which switches from the Apple-direct fit to the family's table row; the
contour deviation those two carry is 6.06e-4 r and 6.88e-4 r, so the field's own accuracy is the
same order on both sides of the switch and the observable — where the contour is — steps by the
0.093 px above.

## 3. Tests and the chain

Geometry (`pnpm --filter @vitrea/geometry test`, `lint`): **170 tests pass**, up from 157.

New — `packages/geometry/test/apple-saturation.test.ts`, 12 tests: the capsule on the render path
at 120 × 44 and 44 × 44 under both references (radius 22, reach 22, effective smoothing 0, zero
coefficients, `toContour` against the stadium under 1e-9); the resolved corner carrying `saturated`
where only the contour builder did; the render path and the spec path resolving a capsule
identically; a 120 × 44 at r 18 (ratio 0.409) resolving at r 18, reach 22, smoothing 0.2222 with
the family's coefficients; the bed's six rounded rectangles and the r 14 rung unchanged from
today's numbers, contour identical to Apple's dump under 1e-9; the reach never overflowing the side
at any radius; and the crossing and continuity results of §2.

Updated — `apple.test.ts`'s "Apple's budget policy is its own" is re-pointed to "Apple's budget
policy is the reference family's, measured", asserting the radius kept, the reach at the budget and
the smoothing at `budget/r - 1`, with §5.84 as its reason and the old claim quoted so the history
survives. `render-path-conformance.test.ts`'s capsule rows flip: render radius 22 rather than
14.3916, reach 22, gap to the declared stadium **below 1e-9** rather than 3.1797 px at 1x and
6.3594 at 2x, and the `saturated` column read off the resolved corner with the contour builder
asserted to agree; the rounded-rectangle rows are untouched and still carry Apple's own 0.0137985 r
departure from a circular corner. Its author-exposure block now shows `DEFAULT_HOST_SHAPE`'s radius
12 kept at every height (7.85 / 10.4666 / 11.775 at heights 24/32/36 before) with the effective
smoothing 0 / 0.3333 / 0.5 / 0.5287 / 0.5287 instead. `morph.test.ts` gains an Apple-reference
capsule morphing into an Apple-reference rounded rectangle across the crossing: legal, reference
preserved, reach never overflowing, endpoints exact.

Workspace chain: `pnpm -r build` exit 0; `pnpm -r lint` exit 0; `pnpm -r test` exit 0 —
policy 23, motion 162, geometry 170, renderer-webgpu 396, core 302, platform-web 410, calibration
273, react 97. No test outside `packages/geometry` needed a change.

## 4. The goldens — no golden moved

`pnpm --filter @vitrea/renderer-webgpu test:golden` on a real adapter: **29 passed**, including
both the isolation proof's eleven pinned-byte scenes and the eleven sRGB-locked golden
comparisons. Byte-identical, exactly as G0 predicted (§5.84 §8): 0 of the 20 golden surfaces is a
capsule, 19 draw under the Figma reference, and the one Apple-reference surface —
`rim-two-references`'s 88 × 88 at r 26 — sits at 0.2955 of its short side, under the crossing.
Log beside this file as `goldens.txt`.

## 5. The Playwright suites

| suite | result |
| --- | --- |
| `platform-web --project=chromium` | 134 passed |
| `platform-web --project=chromium-gpu` | 9 passed |
| `@vitreajs/vitrea-react test:e2e` (three engines) | 105 passed, 3 skipped |
| `demo test:e2e` | 33 passed, **1 failed** |

The demo failure is `e2e/reference-panel.gpu.spec.ts` — "the live panel matches the calibration
harness's render of the same scene" — at a mean of 0.0298 in encoded luma against a tolerance of
0.02. The scene is `checkerboard__capsule-button__rest`, and the fixture it compares against
(`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.png`) is a byte copy of the
canonical GPU capture, which is the pre-fix render with the shoulders. Its own doc comment declares
this: "A recalibration that moves this scene's GPU capture moves this fixture with it — copy both
files again — or this test fails for the right reason: the demo would no longer be showing what
was measured." The live demo is now right and the fixture is stale by exactly this fix. **The
fixture and its `.cell.json` must be re-copied at G2**, after the canonical rebuild, and not
before: at G1 the canonical capture does not yet exist and the dry run's is scratch. No hit-test or
morph pin moved anywhere in the four suites.

## 6. The dry run

Six profiles — `apple-macos-26.5-{1x,2x}-{light,dark}-standard` and the two 1x light accessibility
profiles — GPU tier only, `--set calibration,validation`, `--alpha`, `--write-partial`, to
scratch. **85 cells, every run exit 0**, which is exactly G0's GPU-tier cell count on the same
sets. Script `g1-dryrun-run.sh`, driver log `g1-dryrun-driver.txt`, run log `g1-runs.txt`, tables
`g1-tables.py` / `g1-tables.txt`.

### (a) Declaration conformance — the defect is gone

Before is G0's bed-wide conformance matrix on the same instrument; after is this run.

| | before | after |
| --- | --- | --- |
| capsule cells, 1x — drawn px / declared | 5104 / 4872 (+232) | **4872 / 4872 (+0)** |
| capsule cells, 1x — `declaredIoUWeb` | 0.9545 | **1.0000** |
| capsule cells, 1x — `declaredContourMaxWeb` | 3.16 px | **0.00 px** |
| toolbar cells, 1x — drawn px / declared | 5280 / 4584 (+696) | **4584 / 4584 (+0)** |
| toolbar cells, 1x — `declaredIoUWeb` | 0.8682 | **1.0000** |
| capsule cells, 2x — drawn px / declared | 20402 / 19468 (+934) | 19468–19487 / 19468 (+0…+19) |
| capsule cells, 2x — `declaredIoUWeb` | 0.9542 | **0.9990–1.0000** |
| capsule cells, 2x — `declaredContourMaxWeb` | 6.40 px | **0.00–1.00 px** |
| toolbar cells, 2x — `declaredIoUWeb` | 0.8671 | **0.9969** |

The same numbers on every profile, both schemes and both accessibility profiles, as the defect
itself was. The 2x residual of up to 19 device px and 1.00 px of contour is the antialiased band at
the declared contour and is the same residual every rounded rectangle carries at 2x. **The worst
`declaredContourMaxWeb` over all 53 capsule and toolbar cells after the fix is 1.00 device px**,
which meets the wave's target (≤ 1 device px) and does not fire its stop (above 1 device px).

Every rounded-rectangle cell is **unmoved to the pixel**: `drawnAreaWeb` identical before and
after on all 32 of them, IoU 0.9990–1.0000 unchanged, contour max unchanged. `rrect-sm` at 1x is
still exactly 2000 of 2000.

### (b) Fidelity against Apple — 51 of 53 improve on ΔE, 49 of 53 on SSIM

Before is the canonical W19 bed (`packages/calibration/results/matrix.json`); after is this run.
Full table in `g1-tables.txt`.

| | improved | worsened | best | worst |
| --- | --- | --- | --- | --- |
| `oklabDeltaEMean` | 51 | 2 | **−0.00604** `checkerboard__toolbar-group__rest` 2x light | +0.0000004 `dark-solid__capsule-button__rest` 2x (both schemes) |
| `ssimMean` | 49 | 4 | **+0.03945** `photo__toolbar-group__rest` 1x reduced-transparency | **−0.00559** `photo__capsule-button__rest-tint-orange` 1x increased-contrast |

Representative movements at 1x light standard: `photo__capsule-button__rest` ΔE 0.0036 → 0.0024,
SSIM 0.9860 → 0.9987; `photo__toolbar-group__rest` ΔE 0.0064 → 0.0029, SSIM 0.9602 → 0.9981;
`checkerboard__toolbar-group__rest` ΔE 0.0080 → 0.0023, SSIM 0.9642 → 0.9969.

**The stop fired, on four cells, and this document does not tune it.** W20 Decision Log 2 ruling 4
stops the gate on "any capsule or toolbar cell worsening on OKLab ΔE or SSIM against Apple". Four
cells worsen on SSIM and two of those also on ΔE:

| profile | scene | ΔΔE | ΔSSIM |
| --- | --- | --- | --- |
| 1x light increased-contrast | `photo__capsule-button__rest-tint-orange` | −0.000882 | **−0.005594** |
| 1x light increased-contrast | `checkerboard__capsule-button__rest-tint-orange` | −0.001330 | **−0.000328** |
| 2x light standard | `dark-solid__capsule-button__rest` | +0.0000004 | −0.000014 |
| 2x dark standard | `dark-solid__capsule-button__rest` | +0.0000004 | −0.000014 |

The two `dark-solid` cells are the wave's own control: in the light scheme the material is nearly
invisible over that background on both sides (§5.83 read 0.0015 |ΔL| on the shoulders there), and
these movements are +4e-7 of ΔE and −1.4e-5 of SSIM. They fire the stop's letter at the fifth
decimal.

The two increased-contrast cells are real and are attributed to the region the axes read in, not
to a level. `g1-stop-attribution.py` / `.txt` reads the same captures and splits the surface into
the shoulders (the crescents the fix removes), a two-CSS-px rim band inside the declared contour
where SSIM's band term is computed, and the body inside that. Mean |ΔL| against Apple, linear
luminance:

| profile | scene | shoulders b→a | rim b→a | body b→a |
| --- | --- | --- | --- | --- |
| 1x inc-contrast | `photo__capsule-button__rest-tint-orange` | 0.4361 → **0.0970** | 0.3990 → 0.4686 | 0.0026 → 0.0026 |
| 1x inc-contrast | `checkerboard__capsule-button__rest-tint-orange` | 0.4102 → **0.1374** | 0.3999 → 0.4663 | 0.0032 → 0.0032 |
| 1x inc-contrast | `photo__capsule-button__rest` (SSIM improved) | 0.7507 → **0.1093** | 0.5741 → 0.5889 | 0.0927 → 0.0928 |
| 1x light standard | `photo__capsule-button__rest` (control) | 0.3817 → **0.0119** | 0.0564 → 0.0465 | 0.0357 → 0.0353 |
| 1x light standard | `photo__toolbar-group__rest` (control) | 0.4170 → **0.0165** | 0.0538 → 0.0404 | 0.0383 → 0.0387 |

The shoulders fall by three to seven times on every cell; the body does not move on any; and the
rim band improves on the standard profiles and worsens by 0.07 on increased contrast alone. The
reading beside it is `rimPeakLuminanceNative = 0` on both increased-contrast tinted cells — the
reader finds no rim at all in Apple's increased-contrast capture — while `rimPeakLuminanceWeb`
rises 0.2946 → 0.4077 and 0.2926 → 0.4002. The renderer did not draw a brighter rim: the rim
reading is taken along the DECLARED contour's normal, and before the fix that normal missed the rim
at the capsule's ends, where the rim sat three pixels inward at the clamped contour. The corrected
geometry puts the rim on the declared contour all the way round, so both the rim reading and SSIM's
band term now see the tier's full rim — against an Apple capture that has none under increased
contrast. That is the wave's own charter clause ("the capsule cells' material rows will move
because the region they are read in no longer holds shoulders — attributed, not fitted") reaching a
perceptual row, and it says the increased-contrast rim is a standing gap the defect had been
hiding, not a gap the fix opened. ΔE, ΔE p95 and ΔE max all improve on both cells (ΔE max by
0.0208 and 0.2485). **The disposition of the two cells is the user's, per the wave's stop
discipline; nothing was tuned here.**

Every capsule cell's `silhouetteIoU` (the bounded shape axis) is 0.99–1.00 after, except
`impulse__capsule-button__rest` at 0.113 and `checkerboard__capsule-button__rest` under increased
contrast at 0.617 — both of which read the same before the fix; that axis is bounded to the
declared region and is not what this wave changed.

### (c) The rounded rectangles, byte for byte — 32 of 32 identical

Every non-holdout rounded-rectangle GPU capture, on all six profiles, has **the same sha256** as
the canonical W19 capture. Zero differing pixels anywhere, so the tracker's one frame-timing pair
did not even move by its one code on this run.

The `glass-over-glass` and `rrect-lg` captures the brief also names are **holdout**
(`apps/reference-apple/scenes.json`'s `split`, with `hc-text`), and the same brief forbids reading
holdout at this gate. They are not compared here; G2 reads holdout once and compares them there.
Their exposure is nil by geometry regardless: their ratios are 0.185, 0.286 and 0.2125, all under
the crossing, so the resolver returns bit-for-bit what it returned before.

### The adopted-thresholds gate

`adopted-thresholds.test.ts` asserts the whole bed — both tiers, every profile's cell count,
holdout included — so it cannot read a GPU-only partial. `g1-merge-matrix.py` writes a scratch
matrix that is the canonical W19 bed with all 85 dry-run rows substituted in
(`/Users/new/.claude/jobs/5c70e47f/tmp/w20/g1/g1-merged.json`), and the gate is pointed at it with
`VITREA_MATRIX_PATH`. The canonical matrix was not touched.

**27 of 31 pass**, including every one of the twelve per-profile tier gates, the machine-checked
conditioning predicate with its exclusion list unchanged, and — the clause that matters here —
"proves every regression floor stands on a genuinely unmet bound": **the seven floors keep and
none moved.**

The four failures are all the same merge artefact and none is a bound: the CSS-tier coherence
row `interiorLevelRatioGpuOverCss` is recorded on the CSS cell against the GPU capture that was on
disk when the CSS cell was measured, so a W19 CSS row beside a W20 GPU row cross-checks a stale
ratio (`checkerboard__capsule-button__rest-tint-blue` at 1x light: 1.00839 recorded against 1.02048
derived). The bounded coherence assertions themselves pass. This is a **prediction for G2**: the
cross-tier coherence rows on the capsule cells will move when the CSS tier is re-run against the
corrected GPU capture, and G2's referee should expect them to.

## 7. By eye (contract X5)

`results/2026-09-05-w20-capsule-corner/sheets/g1-1x.png` and `g1-2x.png`, four rows each — the
capsule over photo, checkerboard and light-solid, and the toolbar over photo — four columns: Apple
native | GPU before (the canonical W19 capture) | GPU after | a signed linear-luminance difference
of after against native at full scale ±0.25. Zoom 3 at 1x and 2 at 2x, the W19 landing sheet's
zoom, which is the zoom the finding was made at.

Column 2 shows what the user's eye caught: rounded rectangles where the stadiums should be, and
rounded squares in the toolbar. Column 3 shows stadiums and circles that sit on Apple's own in
column 1. In column 4 the crescents at the ends are gone and what is left is the contour line
itself.

The `hc-text__capsule-button__rest` row the brief asked for is **absent from both sheets**: that
scene is holdout and was not captured at this gate. It belongs on G2's landing sheet.

## 8. What did not work, and what is left

- **The demo's reference-panel fixture is stale** and its e2e test is red until G2 re-copies it
  from the canonical capture. Declared by that spec's own doc comment; not fixable at G1.
- **The stop fired on four cells** (§6 (b)). Two are noise at the fifth decimal; two are the
  increased-contrast rim band becoming visible to the axes now that the contour is right. Reported,
  not tuned.
- **Holdout is unread**, so `glass-over-glass`, `rrect-lg` and `hc-text` have no after-reading of
  any kind at this gate — no byte comparison, no fidelity row, no sheet row.
- **The CSS tier was not re-run.** X3 is argued from the code (no CSS file moved) and is verified
  on captures at G2.
- **The `k` vector steps at the crossing** while the contour does not (§2). It is a switch between
  two fits of comparable accuracy (6.06e-4 r and 6.88e-4 r of contour deviation) and no bound
  covers the discontinuity itself; recorded here rather than measured further.
- **The first attempt at the crossing measurement did not finish**: an honest O(n²) Hausdorff over
  two 70 000-point polylines at 0.005 px spacing ran past two minutes. The test uses a
  one-pixel-bucket nearest-point index that stops only when the best distance found is inside the
  ring already scanned, which is exact and runs in half a second.
