# W24 G3 — the landing: the canonical bed rebuilt at the frozen configuration, the referee, the gate

Findings, not spec text. The parent writes the claims section and the Decision Log from this file.
Everything here was run from the MAIN checkout at `/Users/new/Developer/GitHub/designer` on `main`
at **`b3c5d28`** (the merge of `worktree-w24-g2`, W24 Decision Log 3 (i)), because the canonical
`results/matrix.json` and `web-captures/` live on this machine and this wave's landing IS their
rebuild. The scratch root is `/Users/new/.claude/jobs/5c70e47f/tmp/w24/g3/`; the 0.12.0 bed's matrix
and captures were copied to `before/` before the rebuild overwrote them, and they are the referee's
"before" and the landing sheets' "GPU before" column.

---

## 1. The rebuild (`g3-rebuild.sh`, `g3-runs.txt`)

`rm results/matrix.json` first — **both** documents' hashes moved this wave, the light one on the
lit edge's two constants and the collapse's two anchors and the dark one on the default it inherits,
so every cell's key moves and the old rows must not sit beside the new. Then the whole bed: six
profiles × two tiers × (`calibration,validation`, then `holdout`), `--alpha --write-partial`, the
GPU tier before the CSS tier within each column, into the CANONICAL matrix and the CANONICAL
`web-captures/` (no `--out-matrix`, no `VITREA_WEB_CAPTURES`).

The two documents were verified against `g2/g2-digests.txt` before the first capture and are
reproduced in the referee's own output above the table it checked:

| document | file sha256 | `resolvedMaterialSha256` |
| --- | --- | --- |
| `profiles/apple-macos-26.5-1x-light-standard.json` | `cecea9cd02a7784a…` | **`7968a7f8106b10a4`** |
| `profiles/apple-macos-26.5-1x-dark-standard.json` | `ef4af5aef2cdbe83…` | **`0d741cd19cd1243b`** |

**24 runs, 03:47:57 → 03:55:26 — 7 min 29 s.** Every run exited 0 except one:

    03:55:01  apple-macos-26.5-1x-light-increased-contrast / css / holdout     exit=1

on `hc-text__capsule-button__rest` — *"contourCurvature: a 0.00px contour sampled 512 times at σ=3
carries no curvature"*. Pre-existing, predicted by the run script's own banner, reproduced at every
landing since W20. Recorded and continued.

GPU discipline held throughout: `pgrep` for the capture processes and `lsof -i :5189` clear before
every launch, one capture process at a time, the rebuild detached with a DONE marker and waited on
by a background until-loop; the goldens and both GPU e2e suites in the foreground.

## 2. The referee (`g3-verify.py`, `g3-referee.txt`)

| check | result |
| --- | --- |
| **X3 — G2's declared digests, byte for byte** | **229 of 229 found and hashed, 228 identical, 1 MOVED, 0 missing** |
| the whole capture tree against the dry run's (alpha included) | 460 landed, 460 in the dry run, **458 identical, 2 moved** (the same cell's render and its alpha) |
| every matrix row against the dry run's | **15 322 rows compared, 8 differ** — all eight on that one cell |
| the bed's shape | **229 cells**, the partition exact; every (profile, tier, set) count equal to the 0.12.0 bed's |

**Every holdout capture reproduced.** The wave's one holdout read was spent at G2's dry run (X3) and
this rebuild reproduces those bytes rather than taking a second reading of them. The one capture
that did not reproduce is a **validation** cell in the `increased-contrast` profile, so the holdout
number the wave publishes stands on the render it was measured on.

### 2.1 The one capture that did not reproduce, diagnosed

`apple-macos-26.5-1x-light-increased-contrast / photo__toolbar-group__rest / __css.png` — the RENDER
capture, not only the conformance one — differs from the dry run's by **17 pixels of 64 000, at most
one code value, on the colour channels only**, none of them in the top rows, all of them inside the
photo toolbar's own soft edge. Its `__css__alpha.png` sibling moves with it by 19 pixels (max 4
codes, which is the un-premultiply of one alpha code, as W23 measured on this same file).

**Re-captured a third time to scratch under the same flags** (`recheck/`, one cell, `--alpha
--write-partial`, everything else unchanged), it reproduces **the dry run's declared bytes** —
`24cda2a592c63b0c…` for the render and `fb25641867d138b6…` for the alpha — not the landed
`001eceb60e3bfc7c…`. So the dry-run session and this session's second capture agree, and the
rebuild's own capture is the outlier.

This is the **fourth** sighting of non-determinism on this one cell and the first on its render
path: W21 G2 and W23 G2 both read it on the `__alpha` conformance render, W23 by one code of alpha
in the other direction. The landed file is **left as captured** — a recorded reading is not rewritten
to what it should have been — and `web-captures/` is gitignored, so what enters the commit is the
matrix row measured on it.

**What the flake moves in the committed matrix, in full:** eight rows on that one cell, seven of
them in the sixth decimal or beyond (`oklabDeltaEMean` by 9e-8, `ssimMean` by 6e-7,
`crossTierOklabDeltaEMean` by 8e-8) and one larger — `ssimMin` −0.647479 → −0.647127, a move of
0.00035 on a minimum statistic that one pixel can set. No adopted bound, floor or predicate arm
reads any of them differently: the gate is 33 of 33 (§3), and the profile's `dom / validation` ΔE
mean rounds to 0.01538 on both the dry run and the landing.

The tracker's entry on this cell wants an addendum: the flake is now on the render path, at one code
on colour, on the profile whose accessibility policy composites an extra opaque layer.

## 3. The gate (`g3-gate.txt`, `g3-predicate.py/.txt`, `g3-floors.py/.txt`)

`adopted-thresholds.test.ts`: **five failures over the canonical matrix before the file was
re-derived — the same five, on the same assertions, that G2 read on its scratch matrix** — and
**33 of 33 after**. The whole calibration package is 280 / 280.

### 3.1 `PREDICATE_EXCLUDES` — 27 → 31, derived, four join and none leaves

The machine's own list off the LANDED matrix is **31 lines** and now equals the file's exactly
(`equal: True`). G2 predicted 31, and the three shape-cell counts that follow from it (35 → 36,
33 → 31, 12 → 13) moved with it as predicted. Every one of the four is the lit edge read through a
luminance-delta extractor.

| line | direction | the reading, 0.12.0 → landed |
| --- | --- | --- |
| `texture / cal / dark-solid__capsule-button__rest / 1x dark` | **JOINS by gaining an axis** | no shape axis → areaNative 25 / areaWeb 34 of a 4 872 region, 16 / 18 bodies, IoU 0.639; all four arms fire |
| `texture / cal / dark-solid__capsule-button__rest / 1x light` | **JOINS** | the same, byte for byte (one fixture, one capture) |
| `texture / cal / checkerboard__rrect-md__rest / 2x light` | **JOINS on topology** | bodiesWeb **1 → 2**; IoU 0.99674 → 0.99634 |
| `texture / cal / checkerboard__toolbar-group__rest / 2x light` | **JOINS on topology** | bodiesWeb **3 → 4**; IoU 0.98714 → **0.99026** |

Two mechanisms, both the same factor:

- **The lit arcs give a collapsed 1x capsule an outline it did not have.** These two are the 1x
  siblings of the cells W23 saw at 2x, one wave on: the symmetric cosine draws the north-west and
  south-east arcs brighter than W23's flat rim while every straight side is unchanged, and at 1x
  those arcs are what crosses the extractor's 0.02 threshold. What it recovers is the arcs alone —
  25 px native and 34 px web of a 4 872 px region, in 16 and 18 pieces — and the predicate refuses it
  on every arm. The cell moves out of `NO_SHAPE_AXIS_SCENES` and into the exclusion list; its
  fidelity is read on its perceptual rows as always (ΔE 0.00052 → 0.00047, `ssimMean` 0.99849 →
  0.99951).
- **The unlit arcs pinch a large 2x silhouette into one more piece.** `bodiesWeb` 1 → 2 and 3 → 4 on
  two `2x light` texture calibration cells. **This is the one place the landing loses gated coverage,
  and it is recorded rather than recovered.** Both cells meet every shape row the gate would have
  asked of them: `rrect-md` reads IoU 0.99634 (≥ 0.93), contour mean 0.236 (≤ 0.5) and p95 1 (≤ 3.0);
  `toolbar-group` reads 0.99026, 0.205 and 1.414 — and its IoU and contour mean IMPROVED against the
  0.12.0 bed (0.98714, 0.288). Both cells' ΔE means improve (0.00367 → 0.00364, 0.00243 → 0.00235).
  The predicate is doing what it exists to do; widening it to keep two passing cells in the gate is
  a construct no wave may touch to make a gate pass.

### 3.2 `NO_SHAPE_AXIS_SCENES` — the 1x texture lists empty

`dark-solid__capsule-button__rest` leaves the texture list in `1x-light-standard` and
`1x-dark-standard`, which are the two profiles that still carried it after W23 emptied the 2x ones.
The dom lists and the two accessibility profiles are unchanged. Derived in `g3-predicate.txt` §2,
and the same list is what the coherence rows check absence against (§3 there — unchanged).

### 3.3 The floors — 14 read, 12 held on their W23 numbers, **2 re-pinned by Decision Log 3 (d)**

Every one of the fourteen was re-read on the landed matrix (`g3-floors.txt`), and the landing
reproduces the dry run's readings on both of the two the parent ruled on.

| floor | bound / floor | 0.12.0 bed | **landed** | |
| --- | --- | ---: | ---: | --- |
| dom / cal / `checkerboard__rrect-md` / 2x light :: `ssimMean` | ≥ 0.92, ≥ 0.9142 | 0.915404 | **0.915393** | held |
| dom / cal / `checkerboard__rrect-ml` / 1x light :: `ssimMean` | ≥ 0.90, ≥ 0.8748 | 0.876105 | **0.876082** | held |
| dom / cal / `checkerboard__rrect-ml` / 2x light :: `ssimMean` | ≥ 0.92, ≥ 0.8779 | 0.878938 | **0.878938** | held, bit-identical |
| dom / hold / `checkerboard__glass-over-glass` / 1x light :: `ssimMean` | ≥ 0.90, ≥ 0.8604 | 0.863554 | **0.863549** | held |
| dom / hold / `checkerboard__glass-over-glass` / 2x light :: `ssimMean` | ≥ 0.92, ≥ 0.8677 | 0.868702 | **0.868700** | held |
| dom / hold / `checkerboard__rrect-lg` / 1x light :: `ssimMean` | ≥ 0.90, ≥ 0.8693 | 0.870582 | **0.870558** | held |
| dom / hold / `checkerboard__rrect-lg` / 2x light :: `ssimMean` | ≥ 0.92, ≥ 0.8712 | 0.872322 | **0.872328** | held |
| **dom / hold / `glass-over-glass` / 1x dark :: `silhouetteIoU`** | ≥ 0.93, ≥ 0.9090 | 0.910068 | **0.908039** | **BREACHED → re-pinned ≥ 0.9070** |
| dom / hold / same :: `contourDistanceMean` | ≤ 0.5, ≤ 1.0658 | 0.965791 | **1.033040** | held; floor kept where W23 pinned it |
| **dom / hold / same :: `contourDistanceP95`** | ≤ 3.0, ≤ 8.1 | 8.0 | **8.25** | **BREACHED → re-pinned ≤ 8.35** |
| texture / hold / `glass-over-glass` / 2x dark :: `silhouetteIoU` | ≥ 0.93, ≥ 0.9257 | 0.927080 | **0.927072** | held |
| dom / hold / same :: `silhouetteIoU` | ≥ 0.93, ≥ 0.9038 | 0.928777 | **0.928777** | held, bit-identical |
| dom / hold / same :: `contourDistanceMean` | ≤ 0.5, ≤ 1.8602 | 1.289214 | **1.289214** | held, bit-identical |
| dom / hold / same :: `contourDistanceP95` | ≤ 3.0, ≤ 13.1 | 10 | **10** | held, bit-identical |

**No other floor breached, and none went inert** — every one still misses the adopted bound it
narrows. Eleven of the twelve held rows moved by less than 0.00003 or not at all.

**The two re-pins, exactly as Decision Log 3 (d) directs.** Both are on `dom / holdout /
checkerboard__glass-over-glass__rest / apple-macos-26.5-1x-dark-standard`, and the canonical readings
reproduce the dry run's to the last decimal (0.9080394320082565 and 8.25), so the numbers the parent
ruled on are the numbers pinned, by the file's own epsilons:

| row | W23's pin, kept in the comment | **W24's pin** |
| --- | --- | --- |
| `silhouetteIoU` | measured 0.91007, floor 0.9090 | measured **0.90804**, floor **0.9070** |
| `contourDistanceP95` | measured 8.0, floor 8.1 | measured **8.25**, floor **8.35** |

Nothing was rewritten: W23's numbers stay written beside them in the comment, with the reason. The
cell's interior level moved 0.00005 linear — a fiftieth of a code — and its ΔE +0.00005; the same
change swung the 2x sibling's three rows the other way by ten times, which is what says the rows are
the extractor's threshold and not the material's. `UNMET_ROWS` stays **14**. The re-pin is a
decision taken on the parent's recommendation under the user's standing instruction, reversible in
one edit and the user's to undo.

### 3.4 What did NOT move

No adopted bound was widened or moved. The cell counts per profile and tier are unchanged. The
coherence rows' constants are unchanged. `tier-coherence.test.ts` passes over the landed matrix
unmodified (part of the 280).

## 4. The bed at the landing — ΔE mean per profile, tier and set (`g3-referee.txt` (v))

Every column reproduces G2's dry-run figures, because the captures are the same bytes.

| profile | tier | calibration | validation | holdout |
| --- | --- | ---: | ---: | ---: |
| 1x light standard | webgpu | 0.00324 → **0.00321** | 0.00246 → **0.00241** | 0.00901 → **0.00898** |
| 2x light standard | webgpu | 0.00329 → **0.00326** | 0.00250 → **0.00248** | 0.00898 → **0.00895** |
| 1x dark standard | webgpu | 0.00395 → **0.00393** | 0.00251 → **0.00244** | 0.01331 → **0.01325** |
| 2x dark standard | webgpu | 0.00397 → **0.00395** | 0.00294 → 0.00297 | 0.01317 → **0.01311** |
| 1x light increased-contrast | webgpu | 0.00793 → 0.00793 | 0.00862 → 0.00862 | 0.02042 → 0.02042 |
| 1x light reduced-transparency | webgpu | 0.00172 → **0.00171** | 0.00112 → **0.00110** | 0.00345 → **0.00343** |
| 1x light standard | css | 0.00709 → 0.00709 | 0.00552 → 0.00552 | 0.01577 → **0.01576** |
| 2x light standard | css | 0.00739 → **0.00738** | 0.00570 → **0.00569** | 0.01617 → 0.01617 |
| 1x dark standard | css | 0.00633 → 0.00633 | 0.00364 → 0.00364 | 0.01731 → 0.01735 |
| 2x dark standard | css | 0.00658 → **0.00657** | 0.00403 → 0.00403 | 0.01741 → **0.01739** |
| 1x light increased-contrast | css | 0.01300 → 0.01301 | 0.01531 → 0.01538 | 0.04557 → 0.04561 |
| 1x light reduced-transparency | css | 0.00448 → **0.00447** | 0.00454 → 0.00454 | 0.00751 → 0.00751 |

Every GPU group of the bed improves or holds, on all three sets, in both schemes at both scales. The
`increased-contrast / css / validation` rise of +0.00007 is the single cell §2.1 diagnoses, and it
reads the same on the dry run.

The parent's clauses are not re-derived here. Every capture but one is byte-identical to the dry run
G2 measured them on, and that one is a validation cell whose eight moved rows are listed in full
above, so clauses 1–7 stand at G2's numbers (`g2/g2-dryrun.md`); clause 8 is the sheets below and the
user's eye.

## 5. The demo

The demo reads the matrix at BUILD time — `apps/demo/src/site/calibration.ts` imports
`packages/calibration/results/matrix.json` directly and every figure on the page is keyed by the cell
that produced it — so the Calibration section follows this rebuild with no edit, and `pnpm -r build`
rebuilt it against the landed matrix.

One file had to move, the one the tracker names as hand-kept.
`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.png` is a byte copy of the
harness's own capture, kept beside the spec because `web-captures/` is not committed, and
`reference-panel.gpu.spec.ts` compares the live reference panel against it. It was **211 px / max 34
code values** from the landed capture — the lit arcs. It and its `.cell.json` were re-copied from
`web-captures/apple-macos-26.5-1x-light-standard/checkerboard__capsule-button__rest/`; the cell
record now names the document the capture was actually taken at (`sha256:cecea9cd02a7`, where the
committed copy still said `a94be1ff34d6`). The demo suite is **39 / 39** after the copy.

## 6. The changeset

`.changeset/the-edge-is-lit.md`, `"@vitreajs/vitrea-web": minor` — the three published packages are a
`fixed` group, so core and react bump with it, and the cut is **0.13.0**. It states what a consumer
of 0.12.0 gets, in plain words and in the repo's changeset voice: the rim lit by a symmetric cosine
about the top-left ↔ bottom-right diagonal (`rimLitAxis`, `rimLitExponent`) with the reason no
instrument saw it for three waves; the collapse keeping a share of its backdrop's structure
(`collapseTransmission`, `collapseTransmission2x`) with the centre dot's peak beside Apple's; and
the retirement of the rim's one-sided specular term on both tiers, **naming that the `clear` variant
no longer draws its structural specular highlight** while `specularGain` and `specularPower` stay on
the profile unread. It closes with the CSS tier's two measured limits and the two recorded gaps (the
exponent's scale dependence, the reference's floor at the null), and cites §5.108–§5.109.
`pnpm changeset version` was NOT run; that is the parent's.

## 7. The chain (`g3-chain.txt`)

| step | result |
| --- | --- |
| `pnpm -r build` | green (the demo with it) |
| `pnpm -r lint` | green |
| `pnpm -r test` | **1 893 tests over 130 files, all passing** |
| `@vitrea/renderer-webgpu test:golden` | **33 / 33** (foreground) |
| `@vitreajs/vitrea-web test:e2e:gpu` | **9 / 9** |
| `demo test:e2e` | **39 / 39**, after the harness fixture was re-copied |
| `adopted-thresholds.test.ts` over the canonical matrix | **33 / 33** after the re-derivation |

**Nothing went red.**

## 8. By eye (`sheets/g3-1x.png`, `sheets/g3-2x.png`)

G2's sheet script run against the canonical bed: native | GPU before (the 0.12.0 bed from `before/`)
| GPU landed | CSS landed, both schemes, the solids, the impulse cells and the tinted capsules — 31
rows each — with the dark capsules and rrects repeated at 4× per CSS px cropped to the whole surface
so the ARCS are visible, and the impulse capsule's centre dot at 4× beside them. Panel 3 is now the
canonical capture this rebuild wrote, so the two sheets are comparable to G2's panel for panel.
**The user's veto stands over all of it (X6, S8).**

## 9. What the parent should carry forward

1. **The capture flake is now on the render path** (§2.1), fourth sighting, same cell, one code on
   colour. Tracker addendum with the three digests and the recheck's verdict.
2. **Two calibration cells left the shape gate meeting every row it would have asked** (§3.1) — the
   only coverage this landing loses, and it is the extractor's topology arm, not a fidelity move.
3. **Two floors re-pinned** (§3.3) at the canonical readings the parent ruled on, W23's numbers kept
   beside, the user's to undo.
