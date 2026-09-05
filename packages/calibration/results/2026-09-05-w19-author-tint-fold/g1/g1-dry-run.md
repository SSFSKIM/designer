# W19 G1 — the whole-bed dry run on the frozen configuration (Decision Log 3)

The fold was not touched. The whole canonical bed was captured on both tiers from this branch at
`485b824`, the holdout read once, and read against the W18 bed under Decision Log 3's rulings.

**Nothing on the bed moves except the one cell that should.** Every GPU capture is byte-identical
to the W18 bed and every GPU row is identical to six decimal places. Every CSS row on the bed is
unchanged to four decimal places except the tinted ones, whose interior means move by at most
0.0002 — and the only cell whose *appearance* changes is
`photo__capsule-button__rest-tint-orange-half`, the bed's one sub-unit strength, whose OKLab ΔE
against Apple falls from 0.0043 to 0.0032 at 1x and 0.0045 to 0.0033 at 2x, and against the GPU
tier from 0.0050 to 0.0034 and 0.0051 to 0.0035. The other eleven tinted scenes are at full
strength, where the fold is the opaque layer the tier already drew. The cross-tier ΔE mean falls
on both light-standard profiles and is flat on the other four. `adopted-thresholds.test.ts` passes
against the scratch matrix with no edit, so S2's bounds and floors and S7's predicate hold. All
four browser suites and the whole unit suite are green.

**Two stops read as FIRED by the referee and neither is this wave's**, both established by
measurement rather than argument:

- **S3** flagged two UNTINTED CSS captures as differing from the W18 bed by one 8-bit code. They
  differ on the **pre-fold code too**: the same two cells, captured from `ac9d258` on this machine
  in the same session, differ from the bed identically, while pre-fold and post-fold captures of
  those two cells are byte-identical to each other. It is the bed's provenance, not the fold (§3).
- **S4** flagged `hc-text__capsule-button__rest-tint-orange` at both scales, at **+0.0128 and
  +0.0117** — the bed's own numbers to four places, standing since W17 (claims §5.75 §4, the
  charter's Grounding Baseline). Its untinted twin reads +0.0105 / +0.0129 on the same profiles,
  so the tinted cell's gap is the untinted material's gap on that backdrop and not a tint gap (§4).

**The filter collapse is confirmed by count** (Decision Log 3 (5)): a page with an untinted and a
tinted surface in one group needs **three** `<filter>` definitions before the fold and **two**
after (§8).

## 0. What was captured, and where

**The bed.** The committed canonical bed, read where it lies: `VITREA_SCENES` and `VITREA_FIXTURES`
unset, `apps/reference-apple/scenes.json` and its fixtures as they stand on this branch (unchanged
from `main`). Twelve `compare.ts` runs — six profiles × two tiers, **the GPU tier first** so the
coherence axis of every `dom` cell computes against a `webgpu` capture already on disk — with
`--set calibration,validation,holdout`, which is where **X8's single holdout read** happens.

W18 G1's `run-dry.sh` unchanged, with the calibration package root and the scratch root as its
arguments. 2026-09-05 09:48:06Z–09:53:03Z, every run exit 0, **0 scenes fell back to the CSS tier
and 0 carry problems** on all twelve runs. Nothing canonical was written: `--out-matrix` and
`VITREA_WEB_CAPTURES` both under `/Users/new/.claude/jobs/5c70e47f/tmp/w19/g1/dry/`. The GPU was
idle before the run (`pgrep` and `lsof -i :5189` clear) and one process ran at a time.

**The matrix.** 229 cells — 115 `webgpu` and 114 `dom` — the same 229 keys the W18 bed carries,
none missing and none new. By set on the CSS tier: 69 calibration, 16 validation, 29 holdout; 33
of the 114 are tinted and 81 untinted.

**The readers.** `verify-dry.py` in this directory (W18 G1's, re-aimed at Decision Log 3's stops),
driven over `run-dry-readers.sh`, which runs `moved.ts` per profile for S3's pixel classification
and `predict.ts` (G0's, unchanged) per profile for S5. Both take the bed, the captures and the
output directory as arguments; re-running the committed script reproduces `dry-parts/` byte for
byte. `adopted-thresholds.test.ts` through `VITREA_MATRIX_PATH` for S2 and S7 (X6). The sheets by
`sheets/make-sheet.py`. The referee's whole output is `dry-verify.txt` and the gate's is
`dry-x6-gate.txt`, both committed beside the parts.

**Two control runs**, both on the GPU one at a time and both to scratch:

- `dry2` — the two 2x profiles captured a second time from **this** branch, to ask whether the
  capture is deterministic run to run. It is: 36 of 36 and 13 of 13 CSS captures byte-identical
  between the two runs.
- `prefold` — the same two profiles captured from **`ac9d258`** (`git checkout ac9d258 --
  packages/platform-web/src`, captured, then `git checkout HEAD --` and the tree verified clean).
  This is what settles S3.

## 1. S1 — the GPU tier

**115 of 115 GPU captures byte-identical to the W18 bed; 0 differing. Worst row |Δ| across
`ssimMean`, `ssimBand`, `ssimInterior`, `ssimOutside`, `oklabDeltaEMean`, `interiorStdDevWeb`,
`interiorMeanWeb` and `silhouetteIoU`: 0.000000.** X3 holds on the whole bed by capture. **S1 met.**

## 2. S2 and S7 — the landing's own gate (X6)

`VITREA_MATRIX_PATH=<dry matrix> npx vitest run test/adopted-thresholds.test.ts` — **31 tests
passed, no file edited.** Every adopted bound and every regression floor holds on the dry-run
matrix, and `PREDICATE_EXCLUDES` equals the machine's output on it. **S2 and S7 met.**

The referee prints the floors as a reading beside each row; no cell sits below its pinned floor,
and no `ssimMean` moved by more than 0.00077 anywhere on the bed (the largest,
`photo__rrect-lg__rest-tint-orange` at 1x, +0.00077 — a tinted cell moving up).

## 3. S3 — the CSS captures against the W18 bed

### 3a. The untinted captures, and the two that flagged

**79 of 81 untinted CSS captures byte-identical to the W18 bed.** Two differ:

| cell | profile | differing px | in region | in the eroded interior | worst code | interior mean move |
| --- | --- | --- | --- | --- | --- | --- |
| `hc-text__capsule-button__rest` | 2x light standard | 746 | 0 | 0 | **1** | 0.000000 |
| `checkerboard__glass-over-glass__rest` | 2x dark standard | 6408 | 155 | 155 | **1** | +0.0000015 |

Both are one-code differences and both move the interior mean by less than 2e−6. The referee stops
on them because the clause is byte identity, and that is the right default. **They are not the
fold**, and the evidence is a same-session control rather than an argument:

| comparison | 2x light standard | 2x dark standard |
| --- | --- | --- |
| this branch, run 1 vs run 2 | 36 / 36 identical | 13 / 13 identical |
| **pre-fold (`ac9d258`) vs the W18 bed** | 35 / 36 identical — **`hc-text__capsule-button__rest` differs** | 12 / 13 identical — **`checkerboard__glass-over-glass__rest` differs** |
| pre-fold vs post-fold, this machine | 27 / 36 identical; **all nine that differ are tinted** | 13 / 13 identical |

The pre-fold tree reproduces the same two differences against the bed, and pre-fold to post-fold
those two cells are byte-identical while only tinted captures move. So the difference is between
this machine or session and the one that recorded the W18 bed's `web-captures/`, worth one code on
two cells, and the fold does not touch an untinted surface — which is what the unit pins prove
independently over 190 declarations.

**[parent-impact]** The canonical `web-captures/` on the main checkout is one code away from what
this machine reproduces today on those two cells. It will matter at G2's rebuild, where those two
files will be rewritten with the reproducible bytes; it is worth a line so the change is
attributable when it appears.

### 3b. The full-strength tinted captures

Every one differs, and every one differs only on the contour ring — the transfer's floor colour
moves from the folded colour to the untinted one, and under an opaque layer that reaches the
screen only where the mask is antialiased (claims §5.80 §7 predicted exactly this).

| cell | profile | differing px | in region | in the eroded interior | worst code | interior mean move |
| --- | --- | --- | --- | --- | --- | --- |
| `checkerboard__capsule-button__rest-tint-blue` | 1x LS | 112 | 21 | **0** | 25 | −0.00007 |
| `checkerboard__capsule-button__rest-tint-orange` | 1x LS | 112 | 21 | **0** | 25 | −0.00005 |
| `hc-text__capsule-button__rest-tint-orange` | 1x LS | 105 | 20 | **0** | 21 | −0.00004 |
| `light-solid__capsule-button__rest-tint-orange` | 1x LS | 100 | 17 | **0** | 1 | −0.00001 |
| `photo__capsule-button__rest-tint-blue` | 1x LS | 116 | 21 | **0** | 34 | −0.00013 |
| `photo__capsule-button__rest-tint-orange` | 1x LS | 116 | 21 | **0** | 35 | −0.00010 |
| `photo__rrect-lg__rest-tint-orange` | 1x LS | 192 | 34 | **0** | 25 | −0.00002 |
| `photo__rrect-md__rest-tint-orange` | 1x LS | 112 | 20 | **0** | 26 | −0.00003 |
| `checkerboard__capsule-button__rest-tint-blue` | 2x LS | 224 | 40 | **0** | 27 | −0.00003 |
| `checkerboard__capsule-button__rest-tint-orange` | 2x LS | 218 | 40 | **0** | 27 | −0.00002 |
| `hc-text__capsule-button__rest-tint-orange` | 2x LS | 179 | 38 | **0** | 22 | −0.00002 |
| `light-solid__capsule-button__rest-tint-orange` | 2x LS | 214 | 36 | **0** | 2 | −0.00001 |
| `photo__capsule-button__rest-tint-blue` | 2x LS | 240 | 42 | **0** | 38 | −0.00006 |
| `photo__capsule-button__rest-tint-orange` | 2x LS | 240 | 42 | **0** | 37 | −0.00005 |
| `photo__rrect-lg__rest-tint-orange` | 2x LS | 399 | 61 | **0** | 26 | −0.00001 |
| `photo__rrect-md__rest-tint-orange` | 2x LS | 260 | 38 | **0** | 29 | −0.00001 |
| `checkerboard__capsule-button__rest-tint-orange` | 1x IC | 81 | 14 | **0** | 4 | −0.00003 |
| `photo__capsule-button__rest-tint-orange` | 1x IC | 111 | 17 | **0** | 4 | −0.00005 |
| `photo__capsule-button__rest-tint-orange` | 1x RT | 116 | 21 | **0** | 8 | −0.00005 |

**Not one differing pixel anywhere lies more than two device pixels inside the region**, and the
largest interior-mean move is 0.00013 against the clause's 0.0005. Six full-strength tinted cells —
three scenes at both light-standard scales — are **byte-identical** outright:
`dark-solid__capsule-button__rest-tint-blue`, `dark-solid__capsule-button__rest-tint-orange` and
`impulse__capsule-button__rest-tint-orange`, whose backdrops leave the folded and the untinted
floor colours equal to eight bits.

### 3c. The dark scheme: the encoded form untouched, proved by bytes

All six dark-scheme tinted captures are **BYTE-IDENTICAL** to the W18 bed:
`checkerboard__capsule-button__rest-tint-orange`, `dark-solid__capsule-button__rest-tint-orange`
and `photo__capsule-button__rest-tint-orange`, at 1x and at 2x. Those cells draw the `encoded`
form, which never reads `untintedOptics`.

**S3's verdict.** Met on every clause the wave is responsible for; the two flagged untinted cells
are the bed's provenance and are carried as `[parent-impact]` 1.

## 4. S4 — the bed's twelve tinted scenes

### 4a. The light-standard profiles: `CSS − GPU` within 0.005

| scene | 1x bed → dry | 2x bed → dry | inside 0.005 |
| --- | --- | --- | --- |
| `checkerboard__capsule-button__rest-tint-blue` | −0.0017 → −0.0017 | −0.0025 → −0.0025 | yes |
| `checkerboard__capsule-button__rest-tint-orange` | −0.0017 → −0.0017 | −0.0031 → −0.0031 | yes |
| `dark-solid__capsule-button__rest-tint-blue` (holdout) | −0.0003 → −0.0003 | −0.0001 → −0.0001 | yes |
| `dark-solid__capsule-button__rest-tint-orange` | −0.0007 → −0.0007 | −0.0003 → −0.0003 | yes |
| `hc-text__capsule-button__rest-tint-orange` (holdout) | +0.0128 → **+0.0128** | +0.0117 → **+0.0117** | **no** |
| `impulse__capsule-button__rest-tint-orange` | −0.0008 → −0.0008 | −0.0003 → −0.0003 | yes |
| `light-solid__capsule-button__rest-tint-orange` | −0.0004 → −0.0004 | −0.0008 → −0.0008 | yes |
| `photo__capsule-button__rest-tint-blue` | −0.0015 → −0.0015 | −0.0016 → −0.0016 | yes |
| `photo__capsule-button__rest-tint-orange` | −0.0002 → −0.0002 | −0.0000 → −0.0000 | yes |
| `photo__capsule-button__rest-tint-orange-half` (s = 0.5) | −0.0007 → −0.0007 | −0.0004 → −0.0004 | yes |
| `photo__rrect-lg__rest-tint-orange` (holdout) | −0.0028 → −0.0028 | −0.0032 → −0.0032 | yes |
| `photo__rrect-md__rest-tint-orange` | −0.0024 → −0.0024 | −0.0031 → −0.0031 | yes |

**Eleven of twelve at each scale, and the twelfth is unmoved.** `hc-text__capsule-button__rest-tint-orange`
reads the bed's own +0.0128 and +0.0117 to four places; it is the standing W17 reading the
charter's Grounding Baseline records ("standing since W17, §5.75 §4"). Its **untinted** twin
`hc-text__capsule-button__rest` reads +0.0105 at 1x and +0.0129 at 2x on the same profiles, so at
full strength the tinted cell is carrying the untinted material's own gap on that backdrop, which
is what ruling 1's algebra says a tinted cell does. It is not a tint gap and this wave neither
made it nor could move it.

### 4b. The fold profiles, by Decision Log 3 (1)

`(CSS − GPU)_tinted − (1 − s)·(CSS − GPU)_untinted`, within 0.01. Every fold-profile tinted cell on
the bed is at `s = 1`, so the second term is zero and the clause is the first term alone.

| profile | scene | CSS − GPU | (1 − s)·untinted | residual | inside 0.01 |
| --- | --- | --- | --- | --- | --- |
| increased contrast | `checkerboard__capsule-button__rest-tint-orange` | +0.0056 | +0.0000 | **+0.0056** | yes |
| increased contrast | `photo__capsule-button__rest-tint-orange` | +0.0055 | +0.0000 | **+0.0055** | yes |
| reduced transparency | `photo__capsule-button__rest-tint-orange` | +0.0002 | −0.0000 | **+0.0002** | yes |

**Met on all three**, and each is unmoved from the bed to four places. The untinted
increased-contrast capsules read +0.0259 and +0.0225 on the same profiles and stay W18 §5.79 §7's
item, exactly as ruling 1 says.

### 4c. The dark scheme

Gated by bytes in §3c and met.

**S4's verdict.** Met on eleven of twelve light-standard tinted scenes at both scales, on all three
fold-profile cells by ruling 1, and on all six dark cells by byte identity. The twelfth cell is the
standing W17 reading, unmoved, and is carried as `[parent-impact]` 2.

## 5. S5 — the bed's sub-unit rungs

The bed carries one sub-unit strength, `photo__capsule-button__rest-tint-orange-half` at `s = 0.5`,
on the two light-standard profiles. `c` is that cell's own decoration constant, read at `s = 1` on
the same backdrop and scale from `photo__capsule-button__rest-tint-orange`.

| profile | measured | predFold | c | miss | inside 0.005 | clamp today | clamp under the fold |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1x light standard | 0.45800 | 0.45734 | +0.00377 | **−0.00311** | yes | 4.0663 % | **0.0000 %** |
| 2x light standard | 0.45831 | 0.45766 | +0.00392 | **−0.00327** | yes | 4.6469 % | **0.0000 %** |

**S5 met on both.** The miss is negative and of the size Decision Log 3 (2) attributes to the
control's `α″`-dependence, and it is inside the clause here because `α″` at `s = 0.5` is 0.633,
not far from 1.

**The clamp share, to four places** (ruling 3): **0.0000 %** on both bed cells, against 4.0663 %
and 4.6469 % of masked channel samples under today's table. The stop reads "under 0.1 % of masked
channel samples" and it is met by a wide margin. No cell of the canonical bed reproduces the
pre-check's 0.0582 %, which was the 2x checkerboard capsule of the scratch ladder bed.

## 6. S6 — coherence

**The cross-tier OKLab ΔE mean, per profile, non-holdout cells:**

| profile | bed → dry | cells |
| --- | --- | --- |
| 1x light standard | 0.00606 → **0.00599** | 26 |
| 2x light standard | 0.00633 → **0.00627** | 26 |
| 1x light increased contrast | 0.00669 → 0.00669 | 7 |
| 1x light reduced transparency | 0.00385 → 0.00384 | 6 |
| 1x dark standard | 0.00405 → 0.00405 | 10 |
| 2x dark standard | 0.00413 → 0.00413 | 10 |

**Down on both light-standard profiles and flat on the other four; up on none.** The fall is
carried by the one sub-unit cell: `photo__capsule-button__rest-tint-orange-half` moves from
0.0050 to 0.0034 at 1x and 0.0051 to 0.0035 at 2x, and every other cell is flat to five places.

**The level ratio.** No cell leaves 0.97–1.03 that was inside it on the bed. Seventeen cells sit
outside the band and every one of them sits at the bed's own value to four places — the dark
scheme's near-black cells, where a ratio of levels near 0.05 is a large number for a small
difference (`dark-solid__rrect-md__rest` at 1.6071 / 1.8612, `checkerboard__rrect-md__rest` at
1.1944 / 1.1955), plus `photo__toolbar-group__rest` under reduced transparency at 1.0323 and
`hc-text__capsule-button__rest-tint-orange` at 0.9681. All standing, none this wave's. **S6 met.**

## 7. The tinted cells' ΔE, before and after

The measure the interior mean under-reports, on all 33 tinted CSS cells of the bed. **One cell
moves and it moves down in both measures; every other cell is flat to four places:**

| cell | native ΔE bed → dry | cross-tier ΔE bed → dry |
| --- | --- | --- |
| `photo__capsule-button__rest-tint-orange-half` @ 1x | 0.0043 → **0.0032** (−0.0012) | 0.0050 → **0.0034** (−0.0016) |
| `photo__capsule-button__rest-tint-orange-half` @ 2x | 0.0045 → **0.0033** (−0.0012) | 0.0051 → **0.0035** (−0.0016) |
| every other tinted cell, all six profiles | ±0.0000 | ±0.0000 |

That is the whole visible content of this change on the canonical bed, and it is a 27 % and 32 %
reduction in the cell's colour distance to Apple and to the renderer respectively. The bed simply
does not sample the strengths where the defect was large; G0's ladder does, and the pre-check
measured 0.0030 to 0.0323 of ΔE removed there.

## 8. The filter definitions (Decision Log 3 (5))

Measured in a real Chromium through the e2e harness: one group, two 120 × 44 surfaces over the
same backdrop, one untinted and one tinted `rgba(255, 149, 0, 1)`; the definitions counted off the
document. Run once on `ac9d258` and once on this branch, the tree restored and verified clean
between.

| | definitions | the ids |
| --- | --- | --- |
| before the fold | **3** | `…-b173-t…-2668-9961-9961-9961`, `…-b1369`, `…-b173-t…-2668-8863-5137-0` |
| after the fold | **2** | `…-b173-t…-2668-9961-9961-9961`, `…-b1369` |

The tinted surface's sharp-layer filter changes from a definition keyed on the **folded** colour
(0.8863, 0.5137, 0.0000 — the orange seed folded into the material) to one keyed on the
**untinted** colour (0.9961 on all three channels), which is the untinted surface's own definition,
and the two share it. The heavy step's definition (`-b1369`) carries no transfer and was always
shared. **A tinted group no longer needs a `<filter>` of its own**, as G0 §7 predicted.

## 9. S8 — the cost

Unchanged from the pre-check, and the fold was not touched since: no layer is created or
destroyed (`css-tier-layers.ts` is not in the diff and the tier still writes L1, L2 and L3); no
filter primitive is added (one `feGaussianBlur` and one `feComponentTransfer`, the table the same
length); L3 still carries one `background-color`, one `background-image` and one `box-shadow`
list. The only arithmetic added on the paint path is `foldedOverlay` — three multiply-adds and
three roundings per tinted surface per frame. W16 G0's knee harness was not run, per the
condition: it is run only if a layer or a primitive changed. §8's count is a saving on top.
**S8 met.**

## 10. S9 — the sheets (X5)

`sheets/g1-1x.png` (14 rows, 2076 × 2906) and `sheets/g1-2x.png` (14 rows, 2206 × 3746). Rows: the
six orange rungs over the photo and the six over the checkerboard from the ladder bed, then the
bed's `photo__capsule-button__rest-tint-orange-half` and `hc-text__capsule-button__rest-tint-orange`.
At 1x, column 1 is Apple — the W19 G0 native probe for a ladder rung, the canonical fixture for a
bed cell. At 2x there is no native ladder (the charter Deferred it) and the column is dropped on
every row, including the bed's, so that one banner describes the whole sheet; the banner says so
in capitals.

**The reading.** The defect is visible and its removal is visible, in the direction the metrics
said and in a channel they under-report. At strength 0.1 over the photo the pre-fold column is a
washed-out near-white with a cold pink cast where Apple's own capture and the GPU tier both carry
a warm one; the candidate carries the warm cast and sits between them. The same at 0.2 and 0.35,
diminishing as the strength rises. Over the checkerboard it is starker: at 0.1 and 0.2 the
pre-fold column reads a cold grey-white against native's warm cream, and the candidate matches
native and the GPU tier. At 0.75 and 1.0 the three web columns agree, which is the byte-level
result seen by eye. The two bed rows show no visible change, as their numbers say. The 2x sheet
reads the same on the web columns.

**One honest residual, named.** At strength 0.1 over the photo the candidate is still slightly
lighter and less saturated than Apple's own capture, and it agrees with the GPU tier while doing
so. That is the renderer's gap to Apple at low strength, already measured and recorded (claims
§5.80 §6: the tier crosses Apple's curve near strength 0.3, and the sub-unit gap is the thin-span
level faded in by `(1 − s)`). This wave's declared target is the renderer's composite (Decision
Log 1, q0 (a)), and against that target the columns agree.

## 11. X8 — the holdout, read once on this frozen configuration

Read in the same twelve runs through `--set calibration,validation,holdout`; 29 holdout rows on
the CSS tier. The six tinted holdout cells the acceptance names:

| cell | profile | CSS − GPU bed → dry |
| --- | --- | --- |
| `hc-text__capsule-button__rest-tint-orange` | 1x light standard | +0.0128 → +0.0128 |
| `hc-text__capsule-button__rest-tint-orange` | 2x light standard | +0.0117 → +0.0117 |
| `dark-solid__capsule-button__rest-tint-blue` | 1x light standard | −0.0003 → −0.0003 |
| `dark-solid__capsule-button__rest-tint-blue` | 2x light standard | −0.0001 → −0.0001 |
| `photo__rrect-lg__rest-tint-orange` | 1x light standard | −0.0028 → −0.0028 |
| `photo__rrect-lg__rest-tint-orange` | 2x light standard | −0.0032 → −0.0032 |

All six unmoved to four decimal places. No holdout row is below its bound or its floor (X6, §2).
The holdout has now been read once on `485b824` and must not be read again on it.

## 12. Suites

| suite | result |
| --- | --- |
| `pnpm -r lint` | clean |
| `pnpm -r test` | 1804 tests over 8 packages green (core 302, renderer-webgpu 396, platform-web 410, calibration 265, geometry 149, motion 162, react 97, policy 23) |
| `packages/platform-web` Playwright, all four projects | **355 passed** (chromium, firefox, webkit, chromium-gpu) |
| `packages/react` Playwright, three engines | **105 passed, 3 skipped** |
| `apps/demo` Playwright | **34 passed** |
| `adopted-thresholds.test.ts` against the dry matrix (X6) | **31 passed** |

Run one at a time on the shared adapter. Reduce Transparency and Increase Contrast were off; the
`chromium-gpu` projects ran on the real adapter (`channel: "chromium"`), no fallback.

## 13. What contradicts Decision Log 3

Nothing in its rulings. Ruling 1's re-declared fold clause is met on all three bed cells; ruling 2's
S5 clause is met on both bed cells; ruling 3's clamp-share stop is met at 0.0000 %; ruling 5's
filter collapse is confirmed by count. The two stops the referee raised are §3a's bed provenance
and §4a's standing W17 reading, both established as not this wave's by measurement.

One clause of the charter's own acceptance is worth stating precisely rather than left implied:
"every untinted CSS-tier capture byte-identical to the W18 bed" holds for 79 of 81 as written, and
holds for **81 of 81** when the comparison is against a capture of the pre-fold code taken on this
machine — which is the comparison that isolates the wave. The parent may prefer to record the
clause the second way.

## 14. `[parent-impact]`

1. **The W18 bed's `web-captures/` is one code from reproducible on two cells.**
   `hc-text__capsule-button__rest` at 2x light standard and
   `checkerboard__glass-over-glass__rest` at 2x dark standard differ by one 8-bit code from what
   this machine captures today on both the pre-fold and post-fold trees; the interior means move
   by 0.0 and 1.5e−6. G2's canonical rebuild will rewrite those two files, and the line makes it
   attributable rather than a surprise. Nothing in the matrix moves with them.
2. **`hc-text__capsule-button__rest-tint-orange` is outside S4's 0.005 at both scales and unmoved
   (+0.0128 / +0.0117).** Standing since W17 (§5.75 §4) and carried in the charter's Grounding
   Baseline. The dry run adds one attribution the ledger did not have: the cell's untinted twin
   reads +0.0105 / +0.0129 on the same profiles, so the gap is the untinted material's on that
   backdrop and not the tint's, which is what ruling 1's algebra predicts for a full-strength cell.
   It belongs with the `hc-text` untinted item rather than with the tint pathway.
3. **The filter collapse, measured: 3 → 2 definitions** on a page with one untinted and one tinted
   surface in a group (§8). A claim for the parent to write, with the two id strings as its
   evidence.
4. **The bed samples the strength axis at one point and that point is the defect's zero crossing.**
   The dry run makes this concrete: 33 tinted cells, 32 of them at full strength, and the whole
   visible content of this wave on the canonical bed is one cell's ΔE falling by 0.0012. Decision
   Log 3 (6) already recommends the two extra rungs as a small child after the cut; the dry run
   is the argument for it.
5. **The 1x sheet's residual to Apple at strength 0.1** (§10) is the renderer's, already in claims
   §5.80 §6 and in the charter's Deferred as the tint shade's own gap. Named again only because
   it is the one thing a reader of the sheet will see and should not attribute to this wave.
