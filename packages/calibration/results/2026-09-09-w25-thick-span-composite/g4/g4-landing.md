# W25 G4 — the landing: the canonical bed rebuilt at the frozen configuration, the referee, the gate

Findings, not spec text. The parent writes the claims section and the Decision Log from this file.
Everything here was run from the MAIN checkout at `/Users/new/Developer/GitHub/designer` on `main`
at **`1d7987f`** (W25 G3 CLOSED; Decision Log 7 (d)), because the canonical `results/matrix.json`
and `web-captures/` live on this machine and this wave's landing IS their rebuild. The scratch root
is `/Users/new/.claude/jobs/5c70e47f/tmp/w25/g4/`; the 0.13.0 bed's matrix and captures were copied
to `before/` before the rebuild overwrote them, and they are the referee's "before" and the landing
sheets' "GPU before" column.

---

## 1. The rebuild (`g4-rebuild.sh`, `g4-runs.txt`)

`rm results/matrix.json` first — both documents' fingerprints moved this wave, the light one on the
jointly re-fitted pair and the dark one on the default it inherits, so every cell's key moves and
the old rows must not sit beside the new. Then the whole gated bed: six profiles × two tiers ×
(`calibration,validation`, then `holdout`), `--alpha --write-partial`, the GPU tier before the CSS
tier within each column, into the CANONICAL matrix and the CANONICAL `web-captures/` (no
`--out-matrix`, no `VITREA_WEB_CAPTURES`). **Then the probe set**, which is new to the canonical
bed this wave: `--set probe` on the four standard profiles on both tiers, same flags, same
destination, last — so a refusal there cannot cost the gated bed a capture.

The two documents were verified against `g3/g3b-digests.txt` before the first capture and are
reproduced in the referee's own output above the table it checked:

| document | file sha256 | `resolvedMaterialSha256` |
| --- | --- | --- |
| `profiles/apple-macos-26.5-1x-light-standard.json` | `602b9fc63cec6f84…` | **`9b7806cdefd1d1d6`** |
| `profiles/apple-macos-26.5-1x-dark-standard.json` | `d9be6210c9b5998b…` | **`eec7c2ea8dc89cae`** |

**32 runs, 01:12:25 → 01:29:58 — 17 min 33 s.** Every gated run exited 0 except one:

    01:18:44  apple-macos-26.5-1x-light-increased-contrast / css / holdout     exit=1

on `hc-text__capsule-button__rest` — *"contourCurvature: a 0.00px contour sampled 512 times at σ=3
carries no curvature"*. Pre-existing, predicted by the run script's own banner, reproduced at every
landing since W20. Recorded and continued.

**Six of the eight probe runs exited 1, and the refusals are the same instrument and the same two
cells the dry run's rung met.** `checkerboard-64__rrect-sm__rest` in both light profiles on both
tiers and `dark-solid__rrect-48__rest` at 1x in both schemes on the GPU tier read a 0.00 px contour
and are not written; `checkerboard-8__capsule-button__rest` is absent at 2x dark because G1 omitted
it from the bed by ruling (three settled reference appearances, no majority; claims §5.115 §2). So
the probe column lands 408 rows of a possible 416, and the GPU half of it is cell-for-cell what
G3b's rung read — see §2. The probe set is gated by nothing, so none of this reaches a bound.

GPU discipline held throughout: `pgrep` for the capture processes and `lsof -i :5189` clear before
every launch, one capture process at a time, the rebuild detached with a DONE marker and waited on
by a background until-loop; the goldens and both GPU e2e suites in the foreground.

## 2. The referee (`g4-verify.py`, `g4-referee.txt`)

| check | result |
| --- | --- |
| **X3 — G3b's declared digests, byte for byte** | **229 of 229 found and hashed, 227 identical, 2 MOVED, 0 missing** |
| the gated capture tree against the dry run's (alpha included) | 460 landed, 460 in the dry run, **457 identical, 3 moved** (the same two cells, one with its alpha) |
| every gated matrix row against the dry run's | **15 322 rows compared, 13 differ** — all thirteen on those two cells |
| **the probe capture tree against G3b's rung `rPAIR`** | **414 of 414 identical, 0 moved**; the 414 CSS probe captures beside them have no reference, the rung having captured the GPU tier only |
| every probe matrix row against the rung's | **203 cells in common, 14 232 rows compared, 0 differ**; 205 CSS probe rows are new |
| the gated bed's shape | **229 cells**, the partition exact; every (profile, tier, set) count equal to the 0.13.0 bed's, with the probe counts added beside |

**Every holdout capture reproduced.** The wave's one holdout read was spent at G3b's dry run (X3)
and this rebuild reproduces those bytes rather than taking a second reading of them.

**The probe half is a proof of something else as well.** G3b's rung ran on the ladder's PATCHED copies
of the two documents (`sha256:479f9ad2` and `e13f8cf2`, carrying no `resolvedMaterialSha256` at all)
while this rebuild ran on the re-recorded ones on disk. The keys differ by construction; every one
of the 414 captures is byte-identical anyway, which is the evidence that the two documents resolve
to the same material and that the re-recording moved nothing but bookkeeping.

### 2.1 The two captures that did not reproduce, diagnosed

Both are CSS renders, both differ by at most one code on the colour channels, and they behave
differently under a re-capture — which is the point of taking one.

**(a) `1x-light-increased-contrast / photo__toolbar-group__rest / __css.png`** — 17 px of 64 000,
max one code, colour channels only, none in the top rows, all inside the photo toolbar's own soft
edge; its `__css__alpha.png` sibling moves with it by 19 px (max 4 codes, the un-premultiply of one
alpha code). **Re-captured to scratch under the same flags** (`recheck/`, one cell, `--alpha
--write-partial`), it reproduces the DRY RUN's declared bytes — `1a681782afcd9578…` for the render
and `fb25641867d138b6…` for the alpha — not the landed `211badd0e063dbdc…`. The rebuild's own
capture is the outlier. This is the **fifth** sighting of non-determinism on this one cell (W21 G2,
W23 G2, W24 G3 twice on the render path, now this).

**(b) `1x-dark-standard / checkerboard__glass-over-glass__rest / __css.png`, new** — **1 px** of
64 000, one code, colour only, at (279, 198): the bottom-right corner of the canvas, outside the
nested pane. Its alpha did not move. **Re-captured the same way it reproduces the LANDED bytes**
(`f4009cb0f724fa78…`), twice in this session, so here it is the dry run's `45f9b57967c2eb78…` that
is the odd reading and this session is self-consistent. Same class of flake, opposite verdict — and
worth the parent's eye because this cell is the nested pane, which carries four of the fourteen
floors.

Both landed files are **left as captured** — a recorded reading is not rewritten to what it should
have been — and `web-captures/` is gitignored, so what enters the commit is the matrix rows measured
on them.

**What the two flakes move in the committed matrix, in full: thirteen rows on two cells, twelve of
them in the sixth decimal or beyond.** The largest is `photo__toolbar-group__rest`'s
`perceptual.ssimMin`, −0.647530 → −0.647177 (|Δ| 0.00035); next is the same cell's `ssimOutside` at
3.2 × 10⁻⁶. On the nested pane the largest is `perceptual.unweightedMean` at 1.4 × 10⁻⁷ and its
`ssimMean` moves by 2.2 × 10⁻⁹. **No shape metric moved on either cell**, so none of the four
`checkerboard__glass-over-glass__rest` floors is measured on a moved number.

## 3. The gate, the predicate and the floors (`g4-gate.txt`, `g4-floors.txt`)

**The gate passes over the canonical matrix**, and its case count is 38 rather than the 37 the
dispatch expected because this landing added one assertion — see §3.1.

**The conditioning predicate does not move.** `PREDICATE_EXCLUDES` still names 31 cells and the
suite machine-checks that list against the predicate's own output over the landed bed, so there was
nothing to re-derive; `UNMET_ROWS` stays 14. `adopted-thresholds.test.ts` moved for the probe set
alone and for no number.

**The fourteen regression floors, every one re-read** (`g4-floors.txt`): **0 breached, 0 re-pinned,
and not one moved** — every reading is identical to the 0.13.0 bed's and to G3b's dry run's, to
five decimals. Thirteen are `dom`-tier rows whose readings are set by the band's level rather than
the rim's shape; the fourteenth, `texture / holdout / checkerboard__glass-over-glass__rest /
2x-dark`'s `silhouetteIoU`, holds at 0.92707 against its 0.92570 floor.

### 3.1 What moved in the gate's own file, and why it had to

Decision Log 7 (d) has the canonical matrix carry the probe rows and the gate ignore them by test.
As the file stood, the second half of that was written as *"the matrix holds no probe row at all"* —
true while `compare`'s default set was the only thing that ever wrote the file, and false the moment
this rebuild ran. The change is the smallest one that keeps the promise the file makes:

* the file now reads the matrix once and **drops `fixtureSet === "probe"` before anything selects
  from it**, so every count, partition, bound, floor and conditioning exclusion still runs over the
  frozen bed and no assertion had to be restated;
* the existing guard keeps its meaning against the gated view, by both names (the set label and the
  declared scene list);
* **a second guard is added for the direction that would rot silently**: the file on disk now
  carries probe rows, so the first guard would also pass if the drop had removed the wrong rows or
  the rows had never been captured. The new case asserts that every row the drop removes is a probe
  row of a declared probe scene and that the two views differ by exactly those rows.

That is the 38th case. The other 37 are unchanged and all pass.

## 4. The demo

The demo reads the matrix at BUILD time — `apps/demo/src/site/calibration.ts` imports
`packages/calibration/results/matrix.json` directly and every figure on the page is keyed by the
cell that produced it — so the Calibration section follows this rebuild with no edit, and
`pnpm -r build` rebuilt it against the landed matrix.

**The hand-kept harness fixture moved and was re-copied.**
`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.png` is a byte copy of the
harness's own capture, kept beside the spec because `web-captures/` is not committed. It was **178
px / max 5 code values** from the landed capture — the capsule's corner arcs, which is where the
re-fitted exponent draws, and the thin capsule's straight sides are untouched as X5 requires. It and
its `.cell.json` were re-copied from
`web-captures/apple-macos-26.5-1x-light-standard/checkerboard__capsule-button__rest/`; the cell
record now names the document the capture was taken at (`sha256:602b9fc63cec`, where the committed
copy still said `cecea9cd02a7`, the W24 document).

**One demo source file had to move, and the reason is the probe set rather than the material.** The
page's scene picker reads `scenes.json` — the same file the probe set is declared in — so it has
been offering the 52 probe scenes since G1 merged, with an empty readout beside each because the
matrix had no rows for them. This rebuild gave them rows, and the page then showed a probe scene's
figures from the **dark** profile in the light scheme, because the instrument refuses
`checkerboard-64__rrect-sm__rest` in both light profiles (§1) and the primary-cell rule fell through
to the only cell there was. The public page's evidence is the frozen bed, so
`apps/demo/src/site/scenes.ts` now keeps `split.probe` out of `REFERENCE_SCENES`, with the reason in
a doc comment. The suite is **38 / 39** after it; the one red is diagnosed in §6 and is not this
landing's.

## 5. The changeset

`.changeset/the-rim-grades-along-the-side.md`, `"@vitreajs/vitrea-web": minor` — the three published
packages are a `fixed` group, so core and react bump with it, and the cut is **0.14.0**. In plain
words and in the repo's changeset voice: the rim now grades corner to corner along a thick panel's
straight sides (`rimAlongSideSlope`) with the measurement that found it, and W24's lit edge re-fitted
jointly with it (`rimLitExponent` 1.15 → 0.85, naming that the lower exponent is what keeps a faint
rim at the two dim corners where the previous law drew none); the three mechanisms that ship inert
with their constants named (`sizeScatterHeavyShareThick1x` / `2x`, `sizeToneLevelFar`) and the
measured reason — the heavy blur component is 13.3 device px against Apple's 19.5 and its width is a
mip level, not a parameter; the reference harness's declared probe set (52 scenes at both scales in
both schemes) and the calibration package's width readers and `materialize --omit`; what the CSS
tier takes (the exponent, through the band's arc integral 0.90741 → 0.89686 of 2π) and what it
cannot (the field integrates to zero around a contour); and the numbers as G3b read them, including
the 0.375 of Apple's along-side grading still missing. `pnpm changeset version` was NOT run; that is
the parent's.

## 6. The chain (`g4-chain.txt`)

| step | result |
| --- | --- |
| `pnpm -r build` | green (the demo with it) |
| `pnpm -r lint` | green |
| `pnpm -r test` | **1 926 tests over 131 files, all passing** (re-run after every edit) |
| `@vitrea/renderer-webgpu test:golden` | **33 / 33** (foreground) |
| `@vitreajs/vitrea-web test:e2e:gpu` | **9 / 9** (foreground) |
| `demo test:e2e` | **38 / 39** — one red, below |
| `adopted-thresholds.test.ts` over the canonical matrix | **38 / 38** (37 unchanged plus §3.1's) |

**The one red is not this landing's.** `color-scheme.spec.ts:90`, *"auto follows the system, in both
directions, without a reload"*: after light → dark → light the material reads occlusion 0.815 /
`rgba(255,255,255,0.815)` where the same page read 0.667 / `rgba(254,254,254,0.667)` on the way out,
so the runtime does not return to the material it left. **Reproduced on clean `main` at `1d7987f`
with this landing's files stashed**, and Reduce Transparency and Increase Contrast both read 0 on
this machine, so it is neither the material this wave lands nor the machine's accessibility state.
Left untouched; a finding for the parent.

## 7. By eye (`sheets/g4-1x.png`, `sheets/g4-2x.png`)

G3's sheet script against the canonical bed, four panels now the ruling is made — native | GPU at
the 0.13.0 bed | GPU landed | CSS landed — 37 rows each, both schemes, the thick rrects and the
photo and checkerboard thick cells, the nested pane with its base cropped at 2×, the impulse rrect
with its centre dot at 4×, the probe set's `dark-solid` span sweep 32 → 160 in both schemes, and
**the rim's corners at 4× per CSS px, TL | BR | TR | BL**, which is the row to read: that strip is
the whole of what this wave draws. The probe rows' before column is G3's inert rung `r0` (the 0.13.0
material on the same fixtures), because no canonical capture of the probe set existed before this
rebuild; their after and CSS columns are the rebuild's own. **The user's veto stands over all of it
(X6, S8).**

## 8. What the parent should carry forward

1. **A second capture flake cell** (§2.1 b), on the nested pane at 1x dark, one pixel by one code —
   and this one's re-capture agrees with the LANDING rather than with the dry run, which is the
   opposite verdict to the toolbar cell's five sightings. Tracker addendum with all three digests.
2. **The gate's case count is 38** and the file moved for the probe set alone (§3.1). If the parent
   wants the count to read 37 the two guard cases fold into one, but the second direction is the one
   that rots silently.
3. **The demo page and `scenes.json` are coupled** (§4): anything declared in that file reaches the
   public scene picker unless it is filtered there. The probe set is filtered now; the next declared
   set will need the same line, or the filter needs inverting to an allow-list of the gated sets.
4. **`color-scheme.spec.ts:90` is red on `main`** (§6) and predates this wave.
5. **Two probe cells are unreadable by the contour instrument** in the light profiles and one at 1x
   in both schemes (§1) — the same refusal as the increased-contrast holdout cell that has been
   exiting 1 since W20. If the probe set is to be a fitting ground for a width law, that instrument's
   refusal on a flat-cornered dark square is worth a look in W26.
