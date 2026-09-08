# W23 G2 — the landing: the canonical bed rebuilt at the frozen configuration, the referee, the gate

Findings, not spec text. The parent writes the claims section and the Decision Log from this file.
Everything here was run from the MAIN checkout at `/Users/new/Developer/GitHub/designer` on `main`
at **`ab1ea4b`** (the merge of G3's branch, W23 Decision Log 4 (f)), because the canonical
`results/matrix.json` and `web-captures/` live on this machine and this wave's landing IS their
rebuild. The scratch root is `/Users/new/.claude/jobs/5c70e47f/tmp/w23/g2/`; the 0.11.0 bed's matrix
and captures were copied to `before/` before the rebuild overwrote them, and they are the referee's
"before" and the landing sheets' "GPU before" column.

---

## 1. The rebuild (`g2-rebuild.sh`, `g2-runs.txt`)

`rm results/matrix.json` first — **both** documents' hashes moved this wave, the light one on G1's
law and G3's composition and the dark one on the dark amplitude law, so every cell's key moves and
the old rows must not sit beside the new. Then the whole bed: six profiles × two tiers ×
(`calibration,validation`, then `holdout`), `--alpha --write-partial`, the GPU tier before the CSS
tier within each column, into the CANONICAL matrix and the CANONICAL `web-captures/` (no
`--out-matrix`, no `VITREA_WEB_CAPTURES`).

The two documents were verified against `g3-digests.txt` before the first capture and are reproduced
in the referee's own output above the table it checked:

| document | file sha256 | `resolvedMaterialSha256` |
| --- | --- | --- |
| `profiles/apple-macos-26.5-1x-light-standard.json` | `a94be1ff34d6f319…` | **`c426a37744c38cce`** |
| `profiles/apple-macos-26.5-1x-dark-standard.json` | `f4cf35d3f324cde0…` | **`bf5752ac1b152238`** |

**24 runs, 00:49:17 → 00:56:13 — 6 min 56 s.** Every run exited 0 except one:

    00:55:49  apple-macos-26.5-1x-light-increased-contrast / css / holdout     exit=1

on `hc-text__capsule-button__rest` — *"contourCurvature: a 0.00px contour sampled 512 times at σ=3
carries no curvature"*. Pre-existing, predicted by the run script's own banner, reproduced at G3 §6
and on the canonical bed before it. Recorded and continued.

GPU discipline held throughout: `pgrep` for the capture processes and `lsof -i :5189` clear before
every launch, one capture process at a time, the rebuild detached with a DONE marker and waited on
by a background until-loop.

## 2. The referee (`g2-verify.py`, `g2-referee.txt`)

| check | result |
| --- | --- |
| **X3 — G3's declared digests, byte for byte** | **229 of 229 found and hashed, 229 identical, 0 moved, 0 missing** |
| the whole capture tree against the dry run's (alpha included) | 460 landed, 460 in the dry run, **459 identical, 1 moved** |
| every matrix row against the dry run's | **15 218 rows compared, 0 differ** |
| the bed's shape | **229 cells**, the partition exact; every (profile, tier, set) count equal to the 0.11.0 bed's |

The holdout was read once, at G3's dry run, on the configuration that lands (contract X3), and this
rebuild reproduces those bytes rather than taking a second reading of them. It does: all 229.

**The one moved file, diagnosed.**
`apple-macos-26.5-1x-light-increased-contrast / photo__toolbar-group__rest / __css__alpha.png` is a
declaration-conformance render, carries no declared digest, and differs from the dry run's by **19
pixels of 64 000, ALPHA by exactly one code on every one of them**, at interior pixels of the
toolbar's own soft edge. The rgb differences that come with them (51→55 at α 15/14, 225→229 at
α 51/50) are the un-premultiply of that one alpha code, which is where the "max code delta 4" in the
referee's output comes from — not four codes of light. Nothing measured moved with it: the 15 218-row
comparison includes that cell's four `--alpha` conformance rows and finds none differing, and the
cell's RENDER capture is one of the 229 that reproduce their declared digest exactly.

Re-captured a third time to scratch under the same flags (`recheck/`), it reproduces **the landed
bytes**, `fb25641867d138b6…`, not the dry run's `f5c2b670209a9287…`. So this session's two captures
agree with each other and disagree with G3's session by one code of alpha — a session byte-state on
the conformance path, the **third** sighting and on the same cell as W21 G2's. The tracker's entry
gets an addendum rather than a new claim; the landed file is left as captured, and `web-captures/`
is gitignored and not part of the commit either way.

## 3. The gate (`g2-gate.txt`, `g2-predicate.py`, `g2-predicate.txt`, `g2-floors.py`, `g2-floors.txt`)

`adopted-thresholds.test.ts`: **33 of 33 pass** over the canonical matrix, and the whole calibration
package is **280 / 280**. G3 read nine failures on its scratch matrix; eight were the bookkeeping
below and the ninth was a fidelity row hidden behind one of them.

### 3.1 `PREDICATE_EXCLUDES` — 29 → 27, derived, one mechanism in both directions

The machine's own list off the LANDED matrix — the four arms the test reads,
`silhouetteAreaNative` / `Web` against 0.95 × `componentRegionArea` and `silhouetteBodiesNative` /
`Web` against `componentRegionBodies` — is **27 lines** and now equals the file's exactly
(`equal: True`). Four leave and two join, and every one of the six is the rim:

| line | direction | the reading, 0.11.0 → landed |
| --- | --- | --- |
| `dom / cal / dark-solid__rrect-md__rest / 1x dark` | **LEAVES** | areaWeb 205 / region 15 024, 9 bodies → **no shape axis at all** |
| `dom / cal / dark-solid__rrect-md__rest / 2x dark` | **LEAVES** | areaWeb 849 / 60 064, 3 bodies → **no shape axis at all** |
| `dom / hold / checkerboard__glass-over-glass__rest / 1x dark` | **LEAVES, admitted** | areaWeb 25 069 → **26 912** against a floor of 26 695; IoU 0.84448 → 0.91007 |
| `dom / hold / hc-text__capsule-button__rest / 2x light` | **LEAVES, admitted** | bodiesWeb **2 → 1**; IoU 0.99825 → 0.99178 |
| `texture / cal / dark-solid__capsule-button__rest / 2x dark` | **JOINS** | no shape axis → areaNative 457 / areaWeb 456 of a 19 468 region, **60 bodies** |
| `texture / cal / dark-solid__capsule-button__rest / 2x light` | **JOINS** | the same, byte for byte (the two schemes' fixtures are identical on this cell) |

The mechanism is one thing read from both sides. **A rim on a surface that drew nothing gives the
extractor an outline where it had none** — so at 2x the collapsed capsule's GPU cell gains a shape
axis, of the rim ALONE, which the predicate immediately refuses; it moves from "no axis to gate" to
"an axis named in the exclusion list", and its fidelity is read on its perceptual rows as before.
**And a CSS body that lands closer to its own backdrop takes an outline away** — the dark
`dark-solid__rrect-md` dom cell, the degenerate one the 2026-09-01 predicate extension was adopted
for, recovered 1.4 % of its region before and recovers nothing now, while that profile's dom
calibration ΔE mean falls 0.00682 → 0.00633 (1x) and 0.00699 → 0.00658 (2x). Two cells changed which
construct names them and two cells JOINED the shape gate meeting every bound they newly carry.

### 3.2 `NO_SHAPE_AXIS_SCENES` becomes per TIER

It was one list per profile while the two tiers agreed on which scenes vanish into their backdrop,
and this landing separated them: `dark-solid__capsule-button__rest` leaves the texture list at 2x in
both schemes, `dark-solid__rrect-md__rest` joins the dom list in both dark profiles. The count
assertion at `adopted-thresholds.test.ts` compares the list against the artifact on EACH tier
separately, so the constant had to carry the tier. Derived in `g2-predicate.txt` §2, and the same
list is what the coherence rows check absence against (§3 there).

### 3.3 One fidelity row, and it is the landing's one decision for the parent

Admitting `dom / holdout / checkerboard__glass-over-glass__rest / 1x dark` put a cell into the shape
gate that no bed has ever gated, and **three of its four shape rows miss their adopted bound**:

| row | bound | 0.11.0 (behind the predicate) | **landed** | 2x twin's pinned floor |
| --- | --- | --- | --- | --- |
| `silhouetteIoU` | ≥ 0.93 | 0.84448 | **0.91007** | 0.9038 (measured 0.90482) |
| `contourDistanceMean` | ≤ 0.5 | 1.2903 | **0.96579** | 1.8602 (measured 1.76018) |
| `contourDistanceP95` | ≤ 3.0 | 10 | **8** | 13.1 (measured 13.0) |
| `ssimMean` | ≥ 0.85 | 0.86707 | 0.87362 | — (meets) |

This is the 1x sibling of the cell W21 G2c pinned four instrument floors on, on exactly the same
three rows, with exactly the same mechanism: the dom silhouette carries **13 interior holes** against
the reference's own 14, and `contourDistance` measures every hole's boundary as contour, while the
same tier's conformance row on the texture side reads `declaredIoUWeb` 0.99886 with a contour max of
one device pixel and a p95 of zero. The tier draws the declared shape to a pixel; the silhouette rows
measure how much of it a luminance threshold can find against a checkerboard, and the reference is
perforated there too.

**Three floors were pinned at their first reading** and `UNMET_ROWS` moved 11 → 14. Nothing was
widened, nothing was lowered, and no existing floor moved. The precedent is exact and is in the
file: W21's own dom row is described there as "a row the bed could not read at all a moment ago —
the predicate excluded that cell until the CSS tier's level came right, so 0.90482 is the FIRST
reading of it, pinned where it was first read rather than lowered from anything." Every one of these
three reads BETTER than the 2x twin's pin and better than its own reading behind the predicate.

**This is the parent's call, and it is flagged rather than assumed.** W21's equivalent was taken as
"the parent's recommendation under the user's standing instruction" and recorded in that wave's
Decision Log; this one is prepared the same way — pinned, commented at length, and reported — so the
decision is concrete and reversible in one edit. The alternative on offer was to widen the
conditioning predicate so the cell stays out, which is a construct no wave may touch to make a gate
pass.

### 3.4 The floors — 14 read, 14 held, none inert, none re-pinned, none widened

The eleven standing floors were all re-read on the landed matrix and all hold; **none went inert** —
every one still misses the adopted bound it narrows.

| floor | bound | 0.11.0 bed | **landed** |
| --- | --- | ---: | ---: |
| dom / cal / `checkerboard__rrect-md` / 2x light :: `ssimMean` | ≥ 0.92, floor ≥ 0.9142 | 0.915232 | **0.915404** |
| dom / cal / `checkerboard__rrect-ml` / 1x light :: `ssimMean` | ≥ 0.90, floor ≥ 0.8748 | 0.875656 | **0.876105** |
| dom / cal / `checkerboard__rrect-ml` / 2x light :: `ssimMean` | ≥ 0.92, floor ≥ 0.8779 | 0.878912 | **0.878938** |
| dom / hold / `checkerboard__glass-over-glass` / 1x light :: `ssimMean` | ≥ 0.90, floor ≥ 0.8604 | 0.862768 | **0.863554** |
| dom / hold / `checkerboard__glass-over-glass` / 2x light :: `ssimMean` | ≥ 0.92, floor ≥ 0.8677 | 0.868461 | **0.868702** |
| dom / hold / `checkerboard__rrect-lg` / 1x light :: `ssimMean` | ≥ 0.90, floor ≥ 0.8693 | 0.869928 | **0.870582** |
| dom / hold / `checkerboard__rrect-lg` / 2x light :: `ssimMean` | ≥ 0.92, floor ≥ 0.8712 | 0.872256 | **0.872322** |
| **texture / hold / `glass-over-glass` / 2x dark :: `silhouetteIoU`** | ≥ 0.93, floor ≥ 0.9257 | 0.927320 | **0.927080** |
| **dom / hold / same :: `silhouetteIoU`** | ≥ 0.93, floor ≥ 0.9038 | 0.904935 | **0.928777** |
| **dom / hold / same :: `contourDistanceMean`** | ≤ 0.5, floor ≤ 1.8602 | 1.760176 | **1.289214** |
| **dom / hold / same :: `contourDistanceP95`** | ≤ 3.0, floor ≤ 13.1 | 13.0 | **10.0** |

The four in bold are W21's instrument floors on the 2x dark nested pane. The three dom rows moved
further this landing than in any wave since they were pinned — IoU **+0.0238**, contour mean
**−0.471**, p95 **−3** — and it is the instrument again from the other side: the rim gives the
extractor the overlay's boundary, so the perforated silhouette closes up. The dom `silhouetteIoU` is
now 0.0012 under its adopted bound and is the nearest any of the four has come to going inert. The
texture row fell 0.00024 and stays 0.0014 over its floor. The seven CSS-tier `ssimMean` rows all
rose, by 0.00003–0.00079.

With the three new pins the file reads **14 floors, 14 held, 0 broken** (`g2-floors.txt`).

### 3.5 What did NOT move

No adopted bound was widened or moved. The cell counts per profile and tier are unchanged. The
coherence rows' constants are unchanged. `tier-coherence.test.ts` passes over the landed matrix
unmodified.

## 4. The bed at the landing — ΔE mean per profile, tier and set (`g2-referee.txt` (v))

Every one of the twenty-four columns reproduces G3's dry-run figures, because the captures are the
same bytes. The GPU tier improves in every scheme at both scales on calibration and validation, and
on the light holdouts.

| profile | tier | calibration | validation | holdout |
| --- | --- | ---: | ---: | ---: |
| 1x light standard | webgpu | 0.00330 → **0.00324** | 0.00261 → **0.00246** | 0.00914 → **0.00901** |
| 2x light standard | webgpu | 0.00333 → **0.00329** | 0.00263 → **0.00250** | 0.00906 → **0.00898** |
| 1x dark standard | webgpu | 0.00404 → **0.00395** | 0.00291 → **0.00251** | 0.01326 → 0.01331 |
| 2x dark standard | webgpu | 0.00403 → **0.00397** | 0.00329 → **0.00294** | 0.01301 → 0.01317 |
| 1x light increased-contrast | webgpu | 0.00793 → 0.00793 | 0.00862 → 0.00862 | 0.02042 → 0.02042 |
| 1x light reduced-transparency | webgpu | 0.00172 → 0.00172 | 0.00113 → **0.00112** | 0.00341 → 0.00345 |
| 1x light standard | css | 0.00699 → 0.00709 | 0.00544 → 0.00552 | 0.01581 → **0.01577** |
| 2x light standard | css | 0.00727 → 0.00739 | 0.00563 → 0.00571 | 0.01618 → **0.01617** |
| 1x dark standard | css | 0.00682 → **0.00633** | 0.00362 → 0.00364 | 0.01732 → **0.01731** |
| 2x dark standard | css | 0.00699 → **0.00658** | 0.00401 → 0.00403 | 0.01724 → 0.01741 |
| 1x light increased-contrast | css | 0.01300 → 0.01300 | 0.01531 → 0.01531 | 0.04557 → 0.04557 |
| 1x light reduced-transparency | css | 0.00442 → 0.00448 | 0.00473 → **0.00454** | 0.00752 → **0.00751** |

The two dark GPU holdouts rise by +0.00005 and +0.00016, which is the reading G1 and G3 both
recorded and G3 §6 published. The increased-contrast columns are unchanged to five places at both
tiers: the strong border substitutes the whole rim there, which is the fix wave's own claim
(Decision Log 4 (d)) read from the bed.

The parent's clauses are not re-derived here. Every capture is byte-identical to the dry run G3
measured them on, so clauses 1–8 stand at G3's numbers exactly (`g3-findings.md` §6); clause 9 is
the sheets below and the user's eye.

## 5. The demo

The demo reads the matrix at BUILD time — `apps/demo/src/site/calibration.ts` imports
`packages/calibration/results/matrix.json` directly and every figure on the page is keyed by the
cell that produced it, with no number of its own anywhere in `apps/demo/src` — so the Calibration
section follows this rebuild with no edit, and `pnpm -r build` rebuilt it against the landed matrix.
`apps/demo/vite.config.ts` copies only `apps/reference-apple/fixtures/`, which this wave does not
touch.

One file had to move, the one the tracker names as hand-kept.
`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.png` is a byte copy of the
harness's own capture, kept beside the spec because `web-captures/` is not committed, and
`reference-panel.gpu.spec.ts` compares the live reference panel against it. It was **375 px / max 26
code values** from the landed capture — the rim band, at the law's new amplitude. It and its
`.cell.json` were re-copied from
`web-captures/apple-macos-26.5-1x-light-standard/checkerboard__capsule-button__rest/`; the cell
record now names the document the capture was actually taken at (`sha256:a94be1ff34d6`, where the
committed copy still said `9360d73bd071`). The demo suite is 39 / 39 after the copy.

## 6. The changeset

`.changeset/rim-survives-the-collapse.md`, `"@vitreajs/vitrea-web": minor` — the three published
packages are a `fixed` group, so core and react bump with it, and the cut is **0.12.0**. It states
what a consumer of 0.11.0 gets, in the repo's changeset voice: the rim as a law of the surface's own
level with the gain's sign opposite in the two schemes; the absolute floor that keeps a rim through
the collapse, which is the user finding the wave started from; the band graded across the scales;
the rim on a painted surface spent in the paint's own chromaticity; the increased-contrast strong
border substituting the whole rim; and the CSS tier deriving all of it from the same profile
document. It closes with the two honest limits — the dark bed's rim amount and the CSS tier's
coloured rim on the red-green axis — and cites §5.99–§5.104.

## 7. The chain (`g2-chain.txt`)

| step | result |
| --- | --- |
| `pnpm -r build` | green (the demo with it) |
| `pnpm -r lint` | green, twice |
| `pnpm -r test` | **1 891 tests over 130 files, all passing** — the same total the parent read on the merged tree |
| `@vitrea/renderer-webgpu test:golden` | **31 / 31** |
| `@vitreajs/vitrea-web test:e2e:gpu` | **9 / 9 after one spec fix**, below |
| `packages/platform-web` Playwright, all four projects | **376 passed** |
| `@vitreajs/vitrea-react test:e2e` | 1 failed (firefox `morph.spec.ts:191`), 104 passed, 3 skipped — the tracker's standing flake; 27 / 27 on a confirmation repeat |
| `demo test:e2e` | **39 passed**, after the harness fixture was re-copied |

**One spec asserted the composition G3 refuted, and it is the second thing this landing changed.**
`packages/platform-web/e2e/gpu/tint-gpu.spec.ts:82` required the rim on an orange surface to raise
the BLUE channel the paint leaves at zero — the white rim's own signature, written when that was
what vitrea drew. G3 measured that against Apple's captures and found the reference lifts an
orange's green channel and leaves its blue at 0. The spec now reads the rim as the reference draws
it: `rim.g` > `centre.g` + 8 (152 against 139) and `rim.b` ≤ `centre.b` + 1 (0 against 0), with the
existing `channelDelta` arm untouched, and the doc comment carries the reason. **This suite is not in
the set the parent ran on the merged tree at Decision Log 4**, which is why the landing is where it
surfaced — and it is the wave's own claim being asserted from the other side, not a regression.

## 8. By eye (X6), and the sheets

`sheets/g2-1x.png` (693 301 bytes) and `sheets/g2-2x.png` (1 092 231 bytes), **28 rows each**:
native | GPU BEFORE (the 0.11.0 bed, copied to scratch before the rebuild) | GPU LANDED (the
canonical bed) | CSS LANDED, both schemes, every untinted solid, the four tinted capsules, and the
black-on-black and tinted cells again at 4× per CSS px cropped to the top edge. G3's
`sheets/make-sheet.py` with its banner and inputs re-aimed at the canonical bed.

The gate's own eye, before the user's: on the 2x dark `dark-solid__capsule-button__rest` top edge at
4× and 3× brightness, the native panel shows the outline, **the GPU-before panel shows nothing at
all**, the GPU-landed panel shows the outline at the reference's own weight, and the CSS-landed
panel shows it fainter. That is the user's finding, closed, in one picture.

**S8 / clause 9 remains the user's and is open.** The sheets are not yet sent.

## 9. Gaps, blocks and notes for the ledger

1. **Three new instrument floors and `UNMET_ROWS` 11 → 14** (§3.3). The parent's decision, prepared
   and flagged. They are first readings of rows the bed could not read, all three better than the 2x
   twin's pins, and they come off by the instrument or by the nested pane's own charter — where the
   other four already wait.
2. **A conformance capture moved by one code of alpha between the dry run and the landing, for the
   third time** (§2), on the same cell as W21 G2's sighting. The re-capture reproduces the LANDED
   bytes, not the dry run's, which is the same shape as W21's and confirms it as a session state.
   The tracker's entry gets an addendum; a determinism claim on the conformance path is still not
   made.
3. **A spec asserted the refuted composition and no gate caught it before this one** (§7). The
   platform-web Playwright suites are not in the set a child's chain runs, so a claim the wave
   itself overturned survived G1, G3 and the merge. Worth a tracker line: the e2e suites that read
   the rim belong in a child's chain when the child moves the rim.
4. **The CSS tier's calibration means rise at 1x and 2x light** (+0.00010, +0.00012) while the dark
   ones fall by 0.0005 and every GPU column improves. That is the CSS-only residual G3 recorded
   (Decision Log 4 (c)): one inset shadow of one colour where the renderer adds a coloured light per
   pixel. Recorded, not chartered.
5. **Nothing else moved.** No adopted bound widened, no existing floor re-pinned or removed, the
   partition unchanged, 229 cells, and every published number in this file is the dry run's own,
   because the bytes are.
