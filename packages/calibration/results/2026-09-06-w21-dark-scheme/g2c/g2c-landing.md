# W21 G2c — the landing completed, and its referee (2026-09-07)

Decision Log 4 ruled on what G2b diagnosed and G2c executed it: the CSS tier's form boundary
re-ruled as a comparison of the two forms' errors (4 (a)), its conversion anchored at the surface's
own backdrop (4 (b)), two regression floors on the nested pane at 2x (4 (c)), the predicate
re-derived (4 (d)). The CSS tier was re-captured for all six profiles into the canonical bed from
the main checkout and the gate is **GREEN**. Every number below cites the file beside it.

**The headline, in three sentences.** The ruling's own condition is met by measurement rather than
by argument: all **89** light captures on the CSS tier, four profiles and both scales, come back
**byte-identical to the W20 bed**, and every one of the GPU tier's 115 captures is byte-identical to
what G2 landed with the 52 dark ones still equal to `g1-digests.txt`. Twelve of the thirteen rows
that were red at G2 now meet their adopted bound — the eight cross-tier level ratios land between
0.98 and 1.07 against a 0.8…1.25 gate where they read 1.28 to 3.90, and the nested pane's cross-tier
ΔE halves through its bound — while the CSS tier's own OKLab ΔE against Apple falls from 0.01163 to
**0.00682** on calibration and from 0.04340 to **0.01999** on the holdout, better on every cell than
the W20 bed the wave started from. **Two things need the parent**: two of the four floors pinned are
rows Decision Log 4 (c) did not reach, and the landing costs nine dark cells a declaration-conformance
reading — both named below, neither absorbed.

---

## 1. The rebuild

`g2c-rebuild.sh` from the main checkout at `f7ee9fa`, the dark document unchanged at file digest
`ebfb0858…`. **Only the CSS tier ran.** The GPU tier is untouched by construction — Decision Log 4
(a) and (b) move `optics.ts`'s conversion and `css-tier.ts`'s form, neither of which the renderer
reads — so its captures stayed on disk and §2 (ii) proves nothing moved them, which also keeps every
dom cell's coherence axis measured against the GPU capture the bed already carried.

Twelve runs, 18:13:57–18:17:29 (`g2c-runs.txt`), the calibration and validation column before the
holdout column. Eleven exit 0 and one exit 1 — the increased-contrast CSS holdout run on
`hc-text__capsule-button__rest`, the cell the harness refuses to measure a conformance reading for,
the same refusal as at W19, W20, G2 and G2b (claims §5.79 §1, §5.86 §1). `results/matrix.json` was
NOT removed first: the dark document's hash is unchanged since G1, so a cell's key is unchanged and
each run replaced its own rows. **229 cells on the same keys**, no row lost and none new.

**This is the CSS tier's first holdout read at this configuration, and it was taken once.** The
configuration is new — the form boundary and the conversion both moved — so the holdout column was
read exactly once per profile in the same run order the wave has used throughout, after the
calibration and validation column, and no tuning followed it.

## 2. The referee (`g2c-verify.py`, `g2c-verify.txt`)

**(i) The measurement Decision Log 4 (a) makes of itself.** The ruling said a light capture that
moves voids it. **89 / 89 byte-identical to the W20 bed** — every CSS capture in all four light
profiles at both scales. Against the bed G2 landed it reads 88 / 89, and the one is the cell G2
already named and bounded: `photo__toolbar-group__rest__css.png` under
`apple-macos-26.5-1x-light-increased-contrast`, which G2 found differing from the W20 bed in 17 of
64 000 pixels by one code on one antialiased edge and recorded as a session byte-state of that cell
on this machine. It comes back to the **W20 bed's** bytes here, which settles the question G2 left
open: it is a session byte-state and not a material change, because a material change does not
reverse itself.

Why the light bed cannot move is arithmetic before it is measurement, and the capture reports say the
arithmetic held. Ten light cells draw the encoded form — `dark-solid__capsule-button` and
`impulse__capsule-button` and their tinted variants, five per light-standard scale — and every one is
at full backdrop adaptation, where the alpha is 1, the conversion is anchor-independent
(`cssTintAlpha` returns 1 and `cssTintColor` returns `E(tint)` whatever the anchor is) and the
encoded form's error is zero, so it stays the nearer drawing. The other 26 draw the linear form and
keep it. `g2c-verify.txt` (iv) reports the same ten, cell for cell, as G2's bed did.

**(ii) The GPU tier untouched.** **52 / 52** dark captures byte-identical to `g1/g1-digests.txt`, so
the wave's single holdout read on that tier still stands; and **115 / 115** GPU captures across the
whole bed byte-identical to the copy `g2c-rebuild.sh` took before the first run.

**(iii) The bed's shape.** 229 rows, 229 distinct cells, the same key set G2 landed. The partition
`adopted-thresholds.test.ts` asserts holds per profile: 72 / 72 / 26 / 26 / 17 / 16.

## 3. What landed, per cell

CSS tier, OKLab ΔE mean against Apple, W20 bed → G2 → G2c (`g2c-verify.txt` (iii)):

| profile | calibration (9) | validation (1) | holdout (3) |
| --- | --- | --- | --- |
| 1x dark | 0.01147 → 0.01163 → **0.00682** | 0.00362 → 0.00362 → 0.00362 | 0.03623 → 0.04340 → **0.01999** |
| 2x dark | 0.01166 → 0.01129 → **0.00699** | 0.00401 → 0.00401 → 0.00401 | 0.03676 → 0.04183 → **0.01992** |

Per cell at 1x, W20 → G2 → G2c: `photo__rrect-lg` (holdout) 0.06211 → 0.05867 → **0.01956**, a third
of what the wave inherited; `photo__rrect-md` 0.02217 → 0.02373 → **0.01093**;
`checkerboard__glass-over-glass` (holdout) 0.04074 → 0.07057 → **0.03975**; `checkerboard__rrect-md`
0.02125 → 0.04164 → **0.02001**; `checkerboard__capsule-button` 0.00946 → 0.01356 → **0.00787**;
`photo__capsule-button` 0.00963 → 0.01114 → **0.00795**; `mid-dark-solid__capsule-button` (holdout)
0.00583 → 0.00096 → **0.00066**; `dark-solid__rrect-md` 0.03065 → 0.00455 → 0.00453. The tinted and
collapsed cells move by at most 0.00005. **Every dark CSS cell is now better than the W20 bed**,
which is the thing G2's landing could not say.

The GPU tier's figures are G2's, unchanged and unre-rendered: calibration 0.00410 at both scales
against 0.00846 / 0.00860, holdout 0.01612 / 0.01596 against 0.02996 / 0.03017.

## 4. The gate (`g2c-gate.txt`)

`pnpm --filter @vitrea/calibration test`: **278 passed, 0 failed**. `adopted-thresholds.test.ts` 33
of 33. **No bound was widened.** `MATRIX_CELLS` and `MATRIX_PARTITION` unchanged and asserted green.

**The thirteen rows.** Twelve meet their adopted bound; the thirteenth is one of the floors. The
eight `interiorLevelRatioGpuOverCss` readings land at 0.98922 / 0.98426
(`checkerboard__capsule-button`), 1.05910 / 1.07357 (`photo__rrect-md`), 1.04197 / 1.04846
(`photo__rrect-lg`) and 0.98367 / 0.99463 (`photo__capsule-button`) against 0.8…1.25, from 2.07 /
2.00 / 1.50 / 1.52 / 1.49 / 1.50 / 1.28 / 1.28. The nested pane's `crossTierOklabDeltaEMean` reads
0.02941 and 0.02900 against ≤ 0.05, from 0.0624 and 0.0578; its dom `ssimMean` 0.85104 and 0.87960
against ≥ 0.83 and ≥ 0.85, from 0.80048 and 0.83543. The four dark dom cells the predicate skipped at
G2 read 1.0724 / 1.0098 (`checkerboard__rrect-md`) and 1.0458 / 1.0058
(`checkerboard__glass-over-glass`) where they read 3.90 / 3.33 / 2.47 / 2.28.

**The predicate, re-derived (Decision Log 4 (d)): 34 → 33 lines**, one row leaving and none joining.
The BODIES arm recovers on all four dom rows G2 added — one body again where there were two, two and
six — and only the 2x nested pane clears the AREA arm with it (107 239 of 112 416, 0.9540 against
0.95). The other three recover most of what they lost (0.809, 0.849, 0.891 of their regions, from
0.507, 0.507, 0.628) and still miss that arm, now for exactly the reason the GPU tier's texture row
misses it: a body that agrees with the reference sits inside the extractor's 0.02 threshold of its
own backdrop over the checkerboard's white squares. One mechanism where G2 recorded two.

**Four regression floors, on one cell at one scale** — `checkerboard__glass-over-glass__rest` in
`apple-macos-26.5-2x-dark-standard`, a holdout cell. `UNMET_ROWS` 7 → 11.

| tier | row | measured | floor | bound | ruled |
| --- | --- | --- | --- | --- | --- |
| texture | `silhouetteIoU` | 0.92673 | 0.9257 | ≥ 0.93 | Decision Log 4 (c) |
| dom | `silhouetteIoU` | 0.90482 | 0.9038 | ≥ 0.93 | Decision Log 4 (c) |
| dom | `contourDistanceMean` | 1.76018 | 1.8602 | ≤ 0.5 | **not reached by (c)** |
| dom | `contourDistanceP95` | 13.0 | 13.1 | ≤ 3.0 | **not reached by (c)** |

**Two of those four need the parent's ratification, and the reason they were not in the ruling is
worth stating exactly.** `adopted-thresholds.test.ts` stops a gate case at its first failed
assertion, so when G2b read the cell it saw the `silhouetteIoU` row and never reached the two
contour rows behind it; Decision Log 4 (c) named what G2b reported. They are the same instrument on
the same cell and the arithmetic says so rather than the prose: the dom silhouette the extractor
recovers at 2x carries **34 interior holes**, against the texture tier's 40 and the light bed's none,
and `contourDistance` measures every hole's boundary as contour. The same cell's texture contour —
one silhouette the holes do not perforate at the level the extractor can find — reads 0.0210 and 0.
The predicate admits the cell on area and bodies, which are the two arms it has; **holes are not
among them**, and this is the first cell on the bed where a silhouette passes both arms and is
perforated anyway. Recorded here rather than by widening the predicate, which is a construct no wave
may touch to make a gate pass. W10's precedent is exact and sits in the same list: two contour floors
pinned as "an instrument floor, ONE interior hole the luminance-delta extractor cut", removed at W11b
when the extractor gained a chroma arm.

The shape's own instrument disagrees with all four, which is what makes the mechanism nameable
rather than suspected. W20's conformance rows read the DRAWN coverage against the surface's
DECLARATION rather than against a luminance threshold, and on this cell's texture tier they read
`declaredIoUWeb` **0.99919** with a contour max and p95 of one device pixel at 2x (0.99893 / 1 / 0 at
1x). The tier draws the declared shape to a pixel; what the silhouette row measures is how much of
it a threshold can find against a checkerboard.

## 5. What the landing cost the conformance instrument

Nine dark dom cells LOSE their W20 declaration-conformance reading and two GAIN one; the dark dom
tier goes from 8 / 13 and 9 / 13 measured to 5 / 13 at both scales. **The light bed does not move at
all** (12 of 36 at both light-standard scales, 2 of 8 and 1 of 8 on the preference profiles — G2's
counts exactly).

Lost: `photo__rrect-md`, `photo__rrect-lg`, `photo__capsule-button` and
`mid-dark-solid__capsule-button` at both scales, and `checkerboard__capsule-button` at 2x. Gained:
`dark-solid__rrect-md` at both scales.

The harness says why in its own words: "declaration conformance NOT MEASURED: this tier's interior
alpha over a transparent page is 0.2667, under the 0.9 an alpha coverage rule needs." On the LINEAR
form the tier composites the material inside the sharp layer's filter and keeps only the contrast
floor as an element paint, so its alpha over the transparent conformance page is the floor overlay's
0.2667–0.2706. The seven cells that moved to that form join a refusal class that has always held 24
of the 36 light-standard dom cells for exactly this reason — the class is not new and neither is its
wording. `mid-dark-solid__capsule-button` keeps the encoded form and is lost for the other half of
the wave: its converted alpha moved 0.9061 → 0.8734 under Decision Log 4 (b)'s anchor and fell
through the 0.9 rule. `dark-solid__rrect-md` crosses the other way, 0.8940 → 0.9082, and is measured
for the first time.

Absent, not a conformance failure: the gate asserts no coverage on this axis and nothing there went
red. It is recorded because a measurement the bed used to carry and now does not is a gap, and the
wave's rule is that no gap is accepted silently.

## 6. Which form each surface drew (Decision Log 4 (a))

Off the capture's own report, not off the rule. The dark bed draws **5 of 13 `encoded` at each
scale** — `dark-solid__capsule-button` and its tinted twin, `dark-solid__rrect-md`,
`impulse__capsule-button`, `mid-dark-solid__capsule-button` — and the other eight `linear`. Every one
of the five sits over a SOLID backdrop, which is the point the encoded conversion is exact at and
therefore the nearer drawing; `impulse` is the cell W17 measured the chain drawing 0.0037 as 0, and
it keeps the form that does not. The light bed draws the identical set G2 landed.

That the partition falls out of "whichever is nearer" without a threshold, and falls exactly where a
threshold would have had to be placed by hand, is the ruling working.

## 7. The chain (`g2c-chain.txt`)

Build clean; lint clean; **1 857 unit tests passed, 0 failed** (policy 23, motion 162, geometry 170,
renderer-webgpu 396, core 302, platform-web 425, calibration 278, react 101). platform-web Playwright
**376 passed** on four projects; react **105 passed** on three engines; demo **39 passed**, including
the reference-panel GPU spec against the committed fixture.

**No browser spec had to be updated** — the e2e suites read what the group state reports rather than
which form it names, which is the honesty core doing what it is for. Three unit files pinned the old
boundary and were updated with their reason, not loosened: `interior-level.test.ts` (the chain's
reach and the comparison of errors are now two separate cases), `w19-fold-cases.ts` (the encoded
row's `optics` and `interior` must describe ONE material for the row to be a boundary case rather
than a contradiction — every recorded declaration in `w19-pre-fold-declarations.json` still matches
byte for byte) and `author-tint-fold.test.ts` (contract X9's claim restated over the surface's own
untinted conversion).

**The renderer goldens were not run, and that is a statement.** `git diff` over `renderer-webgpu`,
`core`, `geometry`, `motion`, `policy` and `react` is empty, the renderer's 396 unit tests pass
unchanged, and §2 (ii) shows every one of its captures byte-identical — so no golden hash can have
moved.

## 8. The demo

`apps/demo/src/site/calibration.ts` imports `results/matrix.json` at build time, so the demo's
figures follow the rebuild with no edit. Its e2e fixture
`checkerboard__capsule-button__rest__webgpu.png` is byte-identical to the canonical capture
(`755f6fab…`, a light-standard GPU cell, unmoved) and its `.cell.json` matches field for field.
Nothing to re-copy.

## 9. By eye (contract X5)

`../sheets/g2-1x.png` and `g2-2x.png` regenerated with the CSS column from the landed captures;
thirteen rows each, four panels wide — Apple's fixture, the GPU tier on the W20 bed, the GPU tier
landed, the CSS tier landed — whole canvas at zoom 2 (1x) and 1 (2x).

What the eye reads, and it agrees with the numbers. The CSS panel now sits beside the GPU panel
rather than beside the background: over the checkerboard the board reads through the surface at the
GPU tier's strength where G2's CSS panel was a near-black slab, and `photo__rrect-md`,
`photo__rrect-lg` and the nested pane follow. The solids and `impulse` are indistinguishable across
panels 1, 3 and 4, and the tinted rows across all four.

One difference the metrics do not catch and the eye does, recorded rather than claimed away: over the
checkerboard the CSS panel still carries a little more high-frequency board structure than the GPU
panel. That is not this wave's — the CSS body is one `blur()` at the law's mixed σ where the
renderer's is a two-component scatter (claims §5.42 §5, §5.73) — but it is now the *visible* residual
on these cells, where before it was hidden under a level error four times larger.

## 10. One paragraph the parent can lift into claims

W21 G2c completed the landing on the CSS tier under Decision Log 4, re-capturing all six profiles on
that tier into the canonical bed from the main checkout and leaving the GPU tier unrendered. The
ruling's own condition was met by measurement: all 89 light CSS captures return byte-identical to the
W20 bed, and the one cell that differs from G2's landing is the increased-contrast toolbar group G2
recorded as a session byte-state, which reverts here to the W20 bytes and is thereby settled as one.
Every GPU capture is byte-identical to G2's, the 52 dark ones still equal to `g1-digests.txt`. The
CSS tier's OKLab ΔE mean against Apple falls to 0.00682 / 0.00699 on calibration against G2's
0.01163 / 0.01129 and the W20 bed's 0.01147 / 0.01166, and to 0.01999 / 0.01992 on the holdout — read
once at this configuration — against 0.04340 / 0.04183 and 0.03623 / 0.03676, with every dark CSS
cell better than the bed the wave inherited and the worst of them, the large panel over a photograph,
at a third of it. Twelve of the thirteen rows red at G2 meet their adopted bound: the eight
cross-tier interior-level ratios land between 0.98 and 1.07 against 0.8…1.25 where they read 1.28 to
3.90, the nested pane's cross-tier ΔE reads 0.02941 and 0.02900 against ≤ 0.05, and its dom
`ssimMean` 0.85104 and 0.87960. `PREDICATE_EXCLUDES` is re-derived from the landed artifact at 33
lines, one CSS row recovering as the tier's level came right and three still missing the area arm for
the reason the GPU tier's texture row misses it — one instrument mechanism where G2 recorded two. Four
regression floors are pinned on the 2x nested pane, two ruled by Decision Log 4 (c) and two the
ruling did not reach because the gate case stops at its first assertion; all four are the
luminance-delta extractor reading a silhouette with 34 interior holes, against a conformance row that
reads the same tier's drawn shape at `declaredIoUWeb` 0.99919 with a one-pixel contour. The landing
also costs nine dark dom cells their declaration-conformance reading and gains two, because the
linear form composites the material inside the filter rather than as an element paint — the same
refusal that has always held 24 of 36 light-standard dom cells, named rather than absorbed. The gate
is green with no bound widened; the chain is 1 857 unit tests, 376 / 105 / 39 browser, and no
renderer golden re-run because no renderer file moved.

## 11. The two claims rows, drafted in §5.27's form for the parent to lift

> **`checkerboard__glass-over-glass__rest`, `apple-macos-26.5-2x-dark-standard`, both tiers —
> `silhouetteIoU`, and the dom tier's two contour rows.** The adopted bounds are texture ≥ 0.93 and
> dom ≥ 0.93 on `silhouetteIoU`, dom ≤ 0.5 on `contourDistanceMean` and dom ≤ 3.0 on
> `contourDistanceP95`. The bed measures 0.92673, 0.90482, 1.76018 and 13.0. **What stops being
> claimed is a shape claim on this one cell at this one scale in the dark profile**, and only as the
> luminance-delta extractor reads it. What is NOT withdrawn is the claim about the drawn shape: W20's
> conformance rows read the same tier's coverage against the surface's own declaration and report
> `declaredIoUWeb` 0.99919 with a contour max and p95 of one device pixel (0.99893 / 1 / 0 at 1x), so
> vitrea draws the declared geometry to a pixel here. The mechanism is the instrument's contrast, in
> its third place in three waves (W17, W18, and here): a body that agrees with the reference sits
> nearer its own backdrop, so the set a 0.02 luminance threshold recovers is smaller and, over a
> checkerboard, perforated — 34 interior holes on the dom silhouette against the light bed's none,
> whose boundaries the contour rows then measure. The texture row moved when the GPU tier landed the
> dark material at G2 (0.95088 → 0.92673, while that tier's own ΔE on the cell fell 0.0274 → 0.0177);
> the three dom rows are G2c's, and the dom cell had no reading at all before this landing because
> the predicate excluded it. They come off by the instrument — an arm that separates a surface from
> its backdrop by something other than luminance, as W11b's chroma arm did — or by the nested pane's
> own charter, where the tone axis stands down over a glass backdrop (W9 Deferred, W21 Deferred).
