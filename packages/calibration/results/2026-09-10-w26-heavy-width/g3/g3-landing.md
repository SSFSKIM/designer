# W26 G3 — the landing: the dark scheme held at 0.14.0, the canonical bed rebuilt, the referee, the gate

Findings, not spec text. The parent writes claims §5.126 and W26 Decision Log 11 from this file.

Everything here was run from the MAIN checkout at `/Users/new/Developer/GitHub/designer` on `main`
at **`bfd6489`** (W26 G2c CLOSED, Decision Log 10), because the canonical `results/matrix.json` and
`web-captures/` live on this machine and this wave's landing IS their rebuild. `git status` was
clean at the start. The scratch root is `/Users/new/.claude/jobs/5c70e47f/tmp/w26/g3/`; the 0.14.0
bed's matrix and captures were copied to `before/` before the rebuild overwrote them, and they are
the referee's "before" and the sheets' 0.14.0 column.

The configuration landed is Decision Log 10 (c)'s: **the light scheme takes `sizeHeavyTapSigma` 9 /
`sizeHeavyTapSigma2x` 9, the dark scheme names both 0, and the CSS tier is byte-identical to 0.14.0
on both schemes** (Decision Log 7 (f)).

---

## 1. Step 1 — the dark document names 0 / 0, and the fingerprint it lands on is not a new number

`packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json` names `sizeHeavyTapSigma: 0`
and `sizeHeavyTapSigma2x: 0` in its patch for the first time, with `$comment-w26-g3` carrying
Decision Log 10 (b)'s three signals, Decision Log 6 (c)'s no-small-values rule, and the narrowing of
6 (b) ("the three gain constants are inert") to the light scheme alone. Until this edit the patch
named neither constant and INHERITED the light default, which G2 landed at 9 / 9; `$comment-w26`
below it is the record of that inheritance and is kept as read.

| document | file sha256 | `resolvedMaterialSha256` | heavy width |
| --- | --- | --- | --- |
| `apple-macos-26.5-1x-light-standard.json` | `6a9600720477dd43…` | **`b2b570e4adcea8fb`** (unmoved) | 9 / 9 |
| `apple-macos-26.5-1x-dark-standard.json` | `950ce1c3e91715ee…` | `eee7294f409966d7` → **`874be66ea501621b`** | 0 / 0 |

**`874be66ea501621b` is not a new value.** It is exactly this document's W26 **G1** fingerprint —
the one it had when the two constants existed on the material at 0 and G1 measured the 33 renderer
goldens and all 36 re-rendered bed captures byte-identical to 0.14.0. So the dark scheme's resolved
material at the landing is bit-for-bit the material that proof was taken on, and the identity claim
has an arithmetic half before a single pixel is captured. The light document does not move; it
gained a `$comment-w26-g3` recording that its sibling did and that its own "one pair of anchors
serves both schemes" sentence was true of the family reader's widths and is not true of the bed.

`platform-web/src/dark-profile.ts` regenerated and **does** move this time (two lines), being a
mirror of the patch. `tuned-profiles.test.ts` and `dark-profile-export.test.ts` green.

**The renderer goldens: 33 / 33, and `W26_HASHES` does not move — by structure, not by luck.** No
golden scene draws this document. `renderer-webgpu` has no dependency edge to `platform-web`, the
golden harness renders through `DEFAULT_MATERIAL_PROFILE` and per-scene `materialProfile`
injections, and `tint-adaptation-dark` is a dark BACKDROP scene rather than the dark material. The
grep is empty and the suite is green; nothing was re-recorded, which is the right outcome to record
rather than an absence of work.

## 2. Step 2 — the dark draw proved byte-identical BEFORE anything canonical was touched

`g3-darkproof.sh`, `g3-sample.sh`, `g3-identity.py`; the readings in `g3-step2-dark.txt` and
`g3-step2-controls.txt`. Everything to scratch through `--out-matrix` and `VITREA_WEB_CAPTURES`, so
a failure here would have cost a scratch directory and nothing else.

| check | expectation | result |
| --- | --- | --- |
| **every dark GPU capture** — both scales, calibration + validation + holdout + probe, render and alpha — against the canonical 0.14.0 bytes | identical | **258 of 258 IDENTICAL, 0 moved, 0 missing** |
| control A: the light GPU bed against G2b's declared digests | identical | **52 of 52** |
| control B: the CSS bed (one light profile, one dark) against the canonical bytes | identical | **36 of 36** |

The two controls point in opposite directions on purpose. A dark identity that held because the
whole capture path had drifted would look exactly like a dark identity that held because the
material did not move; control A says this checkout still reproduces the declaring child's bytes
where the material DID move, and control B says it still reproduces the canonical bytes where it did
not. **Zero movers anywhere, in any of the three.**

One expected refusal: `1x dark / webgpu / probe` exits 1 on `dark-solid__rrect-48__rest`
(*"contourCurvature: a 0.00px contour sampled 512 times at σ=3 carries no curvature"*), the
instrument's, pre-existing, and the same cell W25 G4 recorded.

## 3. Step 3 — the canonical rebuild

`g3-rebuild.sh`, `g3-runs.txt`. `rm results/matrix.json` first: a cell's key carries the material
document's file sha256 and BOTH documents' hashes moved this wave, so every key moves and the old
rows must not sit beside the new. Then the whole gated bed — six profiles × two tiers ×
(`calibration,validation`, then `holdout`), `--alpha --write-partial`, the GPU tier before the CSS
tier within each column so every dom cell's coherence axis is measured against a GPU capture already
on disk — into the CANONICAL matrix and the CANONICAL `web-captures/`. **Then** the probe set on the
four standard profiles on both tiers, last, so a refusal there could not cost the gated bed a
capture.

**32 runs, 14:17:27 → 14:35:25 — 17 min 58 s.** Every gated run exited 0 except
`1x-light-increased-contrast / css / holdout`, which exits 1 on `hc-text__capsule-button__rest` with
the 0.00 px contour — pre-existing, reproduced at every landing since W20. Six of the eight probe
runs exited 1 on the same two cells W25 G4 named (`checkerboard-64__rrect-sm__rest` in both light
profiles on both tiers, `dark-solid__rrect-48__rest` at 1x in both schemes on the GPU tier). **The
exit pattern is W25 G4's, run for run.**

GPU discipline held throughout: `g3-guard.sh` before every launch (`pgrep` for the capture processes
and `lsof -i :5189`), one capture process at a time, the long runs detached with a DONE marker and
waited on by a background until-loop. The guard reported the machine's idle Playwright CLI server
each time and did not refuse it, which is the exclusion G1c measured and every capture of this wave
was taken under.

## 4. The referee (`g3-referee.py`, `g3-referee.txt`)

This wave makes two claims pointing in opposite directions, so each is checked in both.

| # | column | expectation | result |
| --- | --- | --- | --- |
| 1 | light GPU vs **G2b's declared digests** | identical | **89 of 89 identical, 0 moved** |
| 1 | light GPU vs the canonical 0.14.0 bed | different | 131 of 193 differ; **the 62 that do not are exactly the flat and near-flat backdrops** |
| 2 | dark GPU vs **the canonical 0.14.0 bed** | identical | **258 of 258 identical, 0 moved** |
| 2 | dark GPU vs G2b's declared digests | different | 18 of 26 differ; **the 8 that do not are the flat solids** |
| 3 | every CSS capture vs the canonical 0.14.0 bed | identical | **644 of 644 identical, 0 moved** |
| 4 | the bed's shape | unchanged | **637 cells, every (profile, tier, set) partition equal, 0 cells added or lost** |
| 5 | `silhouetteIoU` vs `g3a/recompute-rows.json` on the cells whose captures did not move | equal | **423 of 423 agree to 5e-6; 0 cells still read a pre-correction value** |

**Not one capture moved that should not have, on any of the three columns — no flake this session.**
That is worth naming because it is unusual: W25 G4 landed with two, and `photo__toolbar-group` in
increased-contrast has now been seen to flake at the one-code level six times across five waves and
did not this time.

**Rows 1 and 2's "different" halves are the same measurement seen twice, and the unmoved cells in
each are the mechanism's own arithmetic rather than a leak.** A width can only be seen where the
backdrop has structure for it to blur: the 62 unmoved light cells and the 8 unmoved dark ones are
the `dark-solid` / `light-solid` / `mid-dark-solid` backdrops, whose flatness makes 13.418 and 9
device px the same picture, plus the `checkerboard-4` and `checkerboard-8` probe rows, whose pitch
both kernels wash completely flat. This reproduces G2's own attribution (*"the 22 GPU captures that
hold byte for byte are exactly the flat-solid backdrops"*) on a larger set.

**The holdout is not read twice.** X3 spends this wave's one holdout read at G2's dry run; what this
rebuild does with those cells is reproduce their bytes, and row 1 checks every light holdout capture
against `g2b-digests.txt` while row 2 checks every dark one against the canonical bed's.

**Row 5 is the check that the rebuild carries G3a's instrument rather than merely running after
it.** The correction to `silhouetteIoU` lives in `cli/measure.ts` and only a capture run can put it
into the matrix; on all 423 cells whose captures did not move, the landed column equals G3a's
independently computed corrected column exactly.

### 4.1 The bed's per-group ΔE (`g3-delta-e.py`, `g3-delta-e.txt`)

Byte identity showing up in the metrics, and G2b's table reproduced on the bytes that ship: **all
twelve dark groups and all eighteen CSS groups are unchanged to five decimals.** Six light GPU
groups move, every one of them by +0.00001 … +0.00035, and the worst group is
`2x-light-standard / webgpu / holdout` at **+0.00035** — the 160-span rows at dpr 2, which is the
span grading one width per source gives up (Decision Log 2 (f)). No group anywhere worsens by more
than that and no calibration group rises by more than +0.00001.

## 5. Step 4 — the gate, the predicate and the floors

**`adopted-thresholds.test.ts` over the canonical matrix: 38 of 38 green** (`g3-gate.txt`). The file
had 39 cases before this landing and has 38 after, because one of them was written to delete itself
— see §5.2.

### 5.1 `PREDICATE_EXCLUDES` is re-derived to 32, and the cell is NOT the one the dry run named

The list is machine-checked against the predicate's own output over the landed bed, and it reads
**32**, one more than the 31 the file carried. The entering cell is
**`texture / holdout / checkerboard__rrect-lg__rest / apple-macos-26.5-2x-light-standard`**, which
is G2b's prediction and **not** the `dom / calibration / checkerboard__capsule-button__rest /
1x-light-reduced-transparency` that the file's own W26 G2 paragraph describes. That paragraph is the
reading at the configuration the parent then rejected (the CSS tier taking the width too); it is
kept as read and a new paragraph sits beside it. Under the ruled configuration the CSS tier is
byte-identical on all 644 captures, so the reduced-transparency dom capsule never moves and never
enters.

The entering cell joins on the **bodies** arm: `silhouetteBodiesWeb` **1 → 3** against a native 1 and
a region of 1 (`silhouetteHolesWeb` 4 → 7 beside it, native 0; the area arm is nowhere near — 174 847
px² of a 175 240 px² region, 0.9978 against 0.95). It is the largest span on the bed over the
coarsest committed checkerboard at the scale where the heavy component narrows most, so less blur
leaves more of the backdrop's structure inside the surface and the extractor's 0.02 linear-luminance
rule pinches it into two more pieces — **the same degeneracy Decision Log 8 diagnosed on the nested
pane**, on a different cell.

**Every row it takes out of the shape gate is met at the landed bed**: `silhouetteIoU` 0.99807
(≥ 0.93), contour mean 0.204 (≤ 0.5), p95 1 (≤ 3.0), max 2. Its real cost is on its perceptual rows,
which are still gated and which record it rather than hide it: ΔE mean **0.00795 → 0.01145**, the
wave's worst single holdout cell (+0.00350).

### 5.2 G3a's bridging construct is deleted, as designed

`W26_CORRECTED_SILHOUETTE_IOU`, `CORRECTED_READING_ROUNDING`, `gatedReading` and the case *"keeps the
stated silhouette readings honest, and names them for deletion once the bed carries them"* are gone,
and the gate loop reads `reading` again. The construct's own test asserted its entries were STILL
NEEDED and went red the moment the matrix carried the corrected reading, which is the only ending it
was allowed to have; the three cells now read 0.97319, 0.99980 and 0.98289 from the matrix itself. A
comment stands where it stood, saying what it was and that the referee checked the whole column (423
of 423) rather than the three. That is the 39th case removed, and no other assertion was restated.

### 5.3 The eleven floors, every one re-read (`g3-floors.py`, `g3-floors.txt`)

**11 read, 0 breached, 0 re-pinned, and not one moved** — every reading identical to the 0.14.0
bed's to five decimals. Eleven, not W25's fourteen: G3a's correction lifted three off by fix. All
eleven are `dom`-tier rows, and the CSS tier is byte-identical this wave, so that exact identity is
what the ruling predicts rather than a coincidence. The floor the dry run breached
(`texture / holdout / checkerboard__glass-over-glass__rest / 2x dark :: silhouetteIoU`, 0.90362
against 0.9257) no longer exists: it came off by fix at G3a and the cell reads **0.99980** at the
landed bed.

## 6. The demo

The demo reads the matrix at BUILD time (`apps/demo/src/site/calibration.ts` imports
`results/matrix.json` directly), so the Calibration section follows this rebuild with no edit.

**The hand-kept harness fixture moved and was re-copied.**
`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.png` was **1 480 px / max 1 code**
from the landed capture, and the moved pixels are contained in the bounding box (100, 78)–(218, 121)
— the capsule's own 120 × 44 box and nothing outside it, which is the heavy component's interior
work on a thin surface. It and its `.cell.json` were re-copied from
`web-captures/apple-macos-26.5-1x-light-standard/checkerboard__capsule-button__rest/`; the cell
record now names the document the capture was taken at (`sha256:6a9600720477`, where the committed
copy still said `602b9fc63cec`, the W25 document).

## 7. The chain (`g3-chain.txt`)

| step | result |
| --- | --- |
| `pnpm -r build` | green (the demo with it) |
| `pnpm -r lint` | green |
| `pnpm -r test` | **1 955 tests over 132 files, all passing** (one fewer than W25 G4's 1 926 + this wave's additions, because §5.2's self-deleting case is gone) |
| `adopted-thresholds.test.ts` over the canonical matrix | **38 / 38** |
| `@vitrea/renderer-webgpu test:golden` | **33 / 33** |
| `@vitreajs/vitrea-web test:e2e:gpu` | **9 / 9** |
| `@vitreajs/vitrea-web test:e2e` | **376 / 376** (chromium, firefox, webkit, chromium-gpu) |
| `@vitreajs/vitrea-react test:e2e` | **105 / 105** (three engines) |
| `demo test:e2e` | **39 / 39** |

Every e2e suite in the foreground, one at a time, behind `g3-guard.sh`. **`demo test:e2e` is
39 / 39 where W25 G4 landed at 38 / 39** — the red there was `color-scheme.spec.ts:90`, a load
transient older than that wave, fixed in the spec at W25 G4's own close; it stays green here.

## 8. The sheets, for the user's eye

`sheets/g3-1x.png` and `sheets/g3-2x.png`, 29 rows each, from `sheets/make-sheet.py` — G2's
instrument with the "after" column pointed at the canonical `web-captures/` this landing rebuilt and
a banner that says what the dark rows are for.

Four panels: **1** Apple native · **2** the GPU tier at 0.14.0 · **3** the GPU tier as landed ·
**4** the CSS tier as landed. In the light rows panel 3 is σ 9 / 9 and panels 2 and 3 differ; **in
the dark rows panel 3 is σ 0 / 0 and panels 2, 3 and 4 are byte-identical**, which the referee proves
on all 258 dark GPU captures and which the sheet prints anyway, because "we did not change it" is a
claim the eye should be able to check too. The rows are the light thick rrects and the coarse
checkerboards, the nested pane's base at 2× per CSS px, and the impulse centre dot at 4× per CSS px
on the 1x sheet.

## 9. What this landing did NOT do

- **It did not re-read the holdout.** X3's one read was spent at G2; every holdout capture here is
  refereed against a declared digest and none is treated as a fresh measurement.
- **It did not touch the CSS tier's heavy width.** Decision Log 7 (f) declined clause 7 and the
  residual — the renderer's 9 device px against the mirror's 13.800 CSS px at dpr 1 and
  4.455 → 6.121 across spans 96 → 160 at dpr 2 — is pinned as an assertion in
  `tier-coherence.test.ts` and chartered in the tracker, not closed here.
- **It did not answer why the dark scheme prefers a width its own reference does not have.** The
  dark thick body — width, level and transmission read together, the nested pane's two layers read
  separately, the dark panes' 1.3–1.6 codes — is the dark wave's, chartered in the tracker
  (Decision Log 10 (c)).
- **It did not re-pin any floor.** None needed it.
