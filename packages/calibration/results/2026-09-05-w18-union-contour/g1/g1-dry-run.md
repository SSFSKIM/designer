# W18 G1 — the whole-bed dry run of the shadow's two carriers (branch `w18-g1-shadow`)

The charter's G1 child, run on the frozen configuration `6207287` under Decision Log 3's
re-declared stops. Nothing canonical was written: every capture and the matrix live under
`/Users/new/.claude/jobs/5c70e47f/tmp/w18/g1/dry/`, and the main checkout's `results/matrix.json`
and `web-captures/` were read and never touched. The holdout was read ONCE, in this run, on this
configuration (X8).

**The outcome.** S1, S2, S3, S6, S7, S8 and S9 are met. **S4 fires on five cells and S5 on one**,
and none of the five is a cell this wave was aimed at: the four cells S4 targets all meet their
clauses — `checkerboard__toolbar-group` **−0.0028** at 1x and **+0.0044** at 2x,
`photo__toolbar-group` **−0.0087** at 1x and **−0.0044** at 2x, against the bed's −0.0122 /
−0.0040 / −0.0150 / −0.0101 — reproducing the pre-check's numbers to the digit on the canonical
bed. What fires is the fold (q4's clause, measured here for the first time), two cells whose
cross-tier gap was already near or past 0.01 on the W17 bed, and one cell where the closed form
over-predicts by 0.0005 more than S5's clause allows.

## 0. What was captured

One configuration, the branch's own source (`6207287`; the pre-check commit added only results,
and the `sampledOuterShadowFactor` doc comment and the changeset were written after this run and
move no pixel). All six profiles, both tiers, `--set calibration,validation,holdout`, the GPU tier
FIRST so the cross-tier coherence rows compute against a capture already on disk.

| what | where |
| --- | --- |
| the runner | `run-dry.sh <calibrationPackageRoot> <scratchRoot> <renderer> <sets>` — the bed is an argument, no checkout's path is written in it |
| the referee | `verify-dry.py <matrix> <captures> --bed <bed root> --closed-form parts/closed-form-bed.json` |
| the run's log | `dry-runs.txt` |
| the referee's output | `dry-verify.txt` |
| the landing's own gate | `dry-gate.txt` (`adopted-thresholds.test.ts` through `VITREA_MATRIX_PATH`) |
| the sheets | `../sheets/g1-1x.png`, `../sheets/g1-2x.png` |

**The division of labour with the landing's gate.** X6: `adopted-thresholds.test.ts` runs against
the dry matrix, so **S2's bounds and floors and S7's conditioning predicate are that file's
verdict**. `verify-dry.py` owns what the test file cannot see — the GPU tier's byte identity, and
the stops that compare two runs or the two tiers.

**One run exited 1** — `1x-light-increased-contrast / css` — on a single cell that could not be
measured, `hc-text__capsule-button__rest`: `contourCurvature: a 0.00px contour sampled 512 times
at σ=3 carries no curvature`. §5 reads it: the cell was already degenerate on the W17 bed (web
silhouette 2293 px of a 4872 px region, in three bodies, IoU 0.470) and it is already named in
`PREDICATE_EXCLUDES`. The matrix therefore carries 229 cells where the bed carries 230.

## 1. S1 — the GPU tier does not move

**115 GPU captures byte-identical to the W17 bed, 0 differing, 0 not compared; worst GPU row |Δ|
0.000000** across `ssimMean`, `ssimBand`, `ssimInterior`, `ssimOutside`, `oklabDeltaEMean`,
`interiorStdDevWeb`, `interiorMeanWeb` and `silhouetteIoU`. X3 holds through the whole bed, on
every profile, at both scales. **Met.**

## 2. S4 — the level against the renderer

### The four cells the wave is aimed at

| cell | dpr | clause | W17 bed | dry | verdict |
| --- | --- | --- | --- | --- | --- |
| `checkerboard__toolbar-group` | 1 | 0.005 | −0.0122 | **−0.0028** | met |
| `checkerboard__toolbar-group` | 2 | 0.005 | −0.0040 | **+0.0044** | met |
| `photo__toolbar-group` | 1 | 0.01 (Decision Log 3 (3)) | −0.0150 | **−0.0087** | met; the charter's 0.005 missed by 0.0037, the bound's structure term its reason |
| `photo__toolbar-group` | 2 | 0.005 | −0.0101 | **−0.0044** | met |

Every one is the pre-check's number on the canonical bed. The carrier each group resolved is on
the capture's own report and reads `group` on all four (`cssShadow`, printed per row in
`dry-verify.txt`).

### The fold, measured for the first time (q4's clause, 0.01)

| cell | W17 bed | dry | moved | verdict |
| --- | --- | --- | --- | --- |
| `photo__toolbar-group` @ reduced transparency | −0.0320 | **−0.0281** | +0.0038 | **FIRES**; the bed's largest cross-tier miss improves by a tenth of itself and stays 2.8× the clause |
| `photo__toolbar-group` @ increased contrast | +0.0096 | **+0.0139** | +0.0043 | **FIRES**; the cell was inside 0.01 on the bed and leaves it |

Both moves are the carriers' own: +0.0038 and +0.0043 are the same order as the light-standard
cells' +0.0057…+0.0094, and the shadow's amplitude under reduced transparency is a single absolute
occlusion (`reducedTransparencyOcclusion` 0.197) rather than the two-regime law, so the share it
takes out is smaller. Under increased contrast the tier was ABOVE the renderer already, so the
removal of a darkening moves it further above. **This is the first measurement of q4's clause and
it is missed on both profiles; neither is closed by this mechanism.**

### Everything else on the light-standard profiles

Three more cells fire, and the 0.01 table below places all of them:

| profile | scene | bed | dry | verdict |
| --- | --- | --- | --- | --- |
| 1x light | `checkerboard__toolbar-group` | −0.0122 | −0.0028 | **left the 0.01 clause** |
| 1x light | `photo__toolbar-group` | −0.0150 | −0.0087 | **left the 0.01 clause** |
| 2x light | `photo__toolbar-group` | −0.0101 | −0.0044 | **left the 0.01 clause** |
| 1x light | `hc-text__capsule-button__rest` | +0.0091 | **+0.0105** | NEW miss (moved +0.0015) |
| 2x light | `checkerboard__capsule-button__rest` | +0.0095 | **+0.0102** | NEW miss (moved +0.0007) — predicted and named by Decision Log 3 (5) |
| 2x light | `hc-text__capsule-button__rest` | +0.0119 | +0.0129 | standing (moved +0.0010) |
| IC | `photo__toolbar-group` | +0.0096 | +0.0139 | NEW miss |
| — | fourteen other cells | | | standing on both runs, unmoved to the fourth decimal |

`hc-text__capsule-button__rest` at 1x is the one NEW miss Decision Log 3 did not predict. It is
the 120 × 44 capsule over the `hc-text` background, whose backdrop mean is 0.6008 and whose
material sits at 0.766 — the tier was +0.0091 above the renderer on the bed and the shadow's own
share there is +0.0015. At 2x the same cell was already outside the clause (+0.0119 → +0.0129). It
is the same family as `checkerboard__capsule-button` at 2x: the remainder Decision Log 3 (2)
carries as a bound, with its sign positive on this backdrop, and the shadow's removal takes the
cell the last thousandth over a line it was already against.

**The full list of cells outside W17's 0.01 cross-tier clause on either run is in
`dry-verify.txt`'s own table**: three left it, three are new (two named above and the fold's IC
cell), and seventeen are standing and unmoved.

## 3. S5 — every cell moves by its own derived share

The closed form is `parts/closed-form-bed.json`, computed under the light-standard document and
the nominal policy, so it predicts the light-standard cells and no others. The dark, reduced
transparency and increased contrast cells are reported with their measured move and gated on
their other adopted metrics; the tinted cells are gated against their OWN derived share, W17 G1's
rule — `(1 − s)` of the untinted base cell's measured move — because the form carries no author
tint and comparing a tinted cell against it would compare a measurement with a number for a
different surface.

**Twenty-one of twenty-two single-member light cells are inside the clause, and the twenty-second
misses by 0.0005.**

| class | clause | worst | cell |
| --- | --- | --- | --- |
| single-member light | 0.002 | **−0.0025** | `checkerboard__rrect-sm__rest` @ 1x (moved +0.0006 against the form's +0.0031) — **FIRES** |
| `light-solid` | 0.0035 | −0.0033 | `light-solid__rrect-md__rest` @ 1x (moved +0.0002 against +0.0036) |
| the two `toolbar-group` cells | above the form by ≤ 0.005 | +0.0047 | `photo__toolbar-group` @ 1x |
| author-tinted | 0.002 | −0.0001 | every tinted cell moves within a ten-thousandth of `(1 − s)` × its base |
| dark, both scales | — | ±0.0001 | every dark cell moves by 0.0000 or 0.0001; the shadow is multiplicative and inert over black |

**One systematic reading the table makes plain: the form over-predicts on every single-member cell
of the canonical bed.** Every one of the forty-two single-member misses is negative, from −0.0001
to −0.0033, and the largest are on the small boxes over the solid and over the checkerboard. The
same over-prediction is in G0's own residual table (−0.0014 on `checkerboard__capsule-button`) and
in the pre-check (−0.0015 on the same twin). It is one-signed and it is the model's, not the
measurement's: the form clamps a shadow's blur at the canvas and integrates the coverage on the
device grid, and both err toward more shadow than the engine paints.

**The stack cells are recorded, not compared** (Decision Log 3 (4)): the form's largest residual
is on the stack (+0.0274, G0 §6) because the overlay's shadow lands on the base's rendered body
and is composited over it rather than sampled into its backdrop, and the form models only the
sampled path. Measured: `checkerboard__glass-over-glass` moves −0.0001 at 1x and −0.0000 at 2x,
`photo__glass-over-glass` +0.0000 and −0.0001.

**The other adopted metrics.** Five cells move a metric by more than 0.002 and all five are
`silhouetteIoU` on a cell whose web silhouette is fragmentary: `hc-text__capsule-button` at 2x
(−0.0081), `light-solid__rrect-md` and `-ml` at 2x (+0.0021, +0.0051), `checkerboard__capsule-button`
at IC (−0.0121) and `hc-text__capsule-button` at RT (−0.0035). Two of them are the cells that
newly CONDITION (§5). No `ssimMean`, `ssimBand`, `oklabDeltaEMean` or cross-tier ΔE moves by more
than 0.002 anywhere on the bed.

## 4. S3 and S6

**S3 met.** Not one calibration span's interior spread moves farther from native than the W17 bed
had it; the largest move on any of the ten spans is +0.0000007. One standing reading is printed:
`checkerboard__rrect-ml__rest` at 2x sits −0.0081 from native against the renderer's −0.0025,
which is W17's one-sided rule missed — and the same cell read −0.0081 on the W17 bed, so it is not
this wave's.

**S6 met.** The cross-tier OKLab ΔE mean is down or flat on every profile:

| profile | bed | dry |
| --- | --- | --- |
| 1x light standard | 0.00607 | **0.00606** |
| 2x light standard | 0.00633 | 0.00633 |
| 1x increased contrast | 0.00669 | 0.00669 |
| 1x reduced transparency | 0.00389 | **0.00385** |
| 1x dark standard | 0.00406 | **0.00405** |
| 2x dark standard | 0.00414 | **0.00413** |

No cell leaves W17's 0.97–1.03 level-ratio band. One cell is outside it on both runs
(`hc-text__capsule-button__rest-tint-orange` at 1x, bed 0.9678 → dry 0.9680, moving toward 1).
Seven cells move farther from 1 by 0.0006 to 0.0019 and stay well inside the band; the worst
light-cell ratio is 0.9680. `tier-coherence.test.ts` passes with X7's paint-order block added.

## 5. S2 and S7 — the landing's own gate

`dry-gate.txt`. **Twenty-six of thirty-one assertions pass, and not one of the five failures is a
bound, a floor or a metric.** All five are the bookkeeping the landing has to update:

- **Three cells LEFT `PREDICATE_EXCLUDES`** — `light-solid__rrect-md__rest` at 2x and
  `light-solid__rrect-ml__rest` at both scales now satisfy the conditioning predicate where they
  did not on the W17 bed, so the gate covers three more cells than the file expects (34 against 33
  at 1x, 33 against 31 at 2x). **S7 is met: the list goes DOWN, never up**, and the newly gated
  cells pass every bound.
- **One cell left the matrix** — `dom / holdout / hc-text__capsule-button__rest /
  ...1x-light-increased-contrast`, which could not be measured (§0) and is already in
  `PREDICATE_EXCLUDES`; its line comes off that list too, and the profile's cell count drops 18 →
  17.
- **Every floor row is at or above its pin.** No cell of the seven held rows fell; no 1x
  checkerboard row fell more than 0.002 below the bed (the largest fall anywhere is −0.0004 on
  `checkerboard__toolbar-group` at 2x). **S2 met.**

The four lines the landing removes from `PREDICATE_EXCLUDES` and the three count constants are
G2's bookkeeping, and they are recorded here rather than edited on this branch.

## 6. S8 and S9

**S8 met at the pre-check** and not re-run: carrier B adds no element to a single-member group and
the knee was measured unmoved with EVERY surface in a group of three, which is more than any bed
scene asks for (`g1-precheck.md` §6).

**S9, by eye** (`../sheets/g1-1x.png`, `../sheets/g1-2x.png`; five panels — native, the W17 bed,
this candidate, the GPU tier, and the candidate's signed difference from native). On the three-up
at both scales the candidate's three circles read plainly brighter than the bed's and the gaps
between them are cleaner, while **the shadow is still on the page**: the soft darkening below and
around each circle has the same reach and the same weight as the bed's, and no shadow lies on any
member's body. The pre-check measured that directly — a ring one device pixel outside every
contour out to 40 CSS px reads 0.47505 against the bed's 0.47473 and 0.50287 with the shadow
declined. The two stack rows are indistinguishable between the bed and the candidate, which is the
measurement (±0.0001). On the checkerboard three-up the candidate now sits slightly ABOVE native,
which is the wave's declared target: the renderer is +0.0553 over native there and the tier is now
+0.0525 where it was +0.0431.

## 7. The suites

| suite | result |
| --- | --- |
| `pnpm -r build` | clean |
| `pnpm -r lint` | clean |
| `pnpm -r test` (8 packages) | 1 792 tests, all passing |
| `packages/platform-web` Playwright, all four projects | **354 passed** (chromium, firefox, webkit, chromium-gpu) |
| `@vitreajs/vitrea-react` e2e, three engines | 105 passed |
| `demo` e2e | 34 passed, after one expectation moved (below) |
| `renderer-webgpu` goldens | **not run, and stated:** the renderer is untouched by this branch and its captures are byte-identical on all 115 GPU cells of the bed, so the goldens cannot have moved |

The demo's `every surface writes a real shadow: black, downward, blurred` read the shadow off the
host's computed `box-shadow` and now asks the SURFACE for its shadow — the host, then its overlay
layer, then the group's caster for that node id — because which element carries it is exactly what
this wave changes. The assertions it makes (pure black, downward, blur over offset, non-negative
spread) are unchanged, because the shadow is unchanged.

## 8. What contradicts Decision Log 3

**Nothing in its decisions; two things in what it expected to find.**

1. **q4's clause is missed on both fold profiles**, and Decision Log 3 (3) expected it to be
   measured rather than assumed. Reduced transparency improves from −0.0320 to −0.0281 and
   increased contrast worsens from +0.0096 to +0.0139. The fold is not closed by this mechanism
   and this wave has no second one for it.
2. **One NEW cell leaves W17's 0.01 clause that the pre-check did not predict** —
   `hc-text__capsule-button__rest` at 1x, +0.0091 → +0.0105. Decision Log 3 (5) predicted one
   (`checkerboard__capsule-button` at 2x, +0.0102, measured exactly) and named the mechanism; this
   is the same mechanism on a different backdrop, and it is named here with its number.

And one thing the gate reports that no stop covers: **a bed cell became unmeasurable**. It was
already the most degenerate cell in the matrix and it is already excluded from every bound, so
nothing is gated on it — but the bed loses a row, and that is recorded rather than absorbed.

## 9. What is in this directory (added by the dry run)

| file | what it is |
| --- | --- |
| `run-dry.sh` | the runner; the bed and the scratch root are arguments |
| `verify-dry.py` | the referee against the W17 bed, under Decision Log 3's clauses |
| `dry-runs.txt`, `dry-verify.txt`, `dry-gate.txt` | the run's log, the referee's output, the landing gate's output |
| `../sheets/make-sheet.py`, `../sheets/g1-{1,2}x.png` | X5's by-eye sheets, W17's script with its rows and banner re-aimed |
