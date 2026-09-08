# W22 G2 — the landing: the canonical bed rebuilt at the frozen configuration, the referee, the gate

Findings, not spec text. The parent writes the claims section and the Decision Log from this file.
Everything here was run from the MAIN checkout at `/Users/new/Developer/GitHub/designer` on `main`
at `e45fe8c` (the merge of G1's `08ade69`), because the canonical `results/matrix.json` and
`web-captures/` live on this machine and this wave's landing IS their rebuild. The scratch root is
`/Users/new/.claude/jobs/5c70e47f/tmp/w22/g2/`; the W21 bed's captures were copied to
`../g2-before/` before the rebuild so "before" survives it.

---

## 1. The rebuild (`g2-rebuild.sh`, `g2-rebuild.log`)

`rm results/matrix.json` first — G1 moved the LIGHT document's hash
(`resolvedMaterialSha256` b1ff51ad15273736 → **f6c54a1ea236447a**, file sha256 **9360d73bd071…**),
so every light cell's key moves and the old rows must not sit beside the new. Then the whole bed:
six profiles × two tiers × (`calibration,validation`, then `holdout`), `--alpha --write-partial`,
the GPU tier before the CSS tier within each column, into the CANONICAL matrix and the CANONICAL
`web-captures/` (no `--out-matrix`, no `VITREA_WEB_CAPTURES`). The dark document did not move
(`ebfb08586af0…` / `d86f480c0e136627`).

**24 runs, 13:24:19 → 13:31:40 — 7 min 21 s.** Every run exited 0 except one:

    13:31:15  apple-macos-26.5-1x-light-increased-contrast / css / holdout     exit=1

on `hc-text__capsule-button__rest` — *"contourCurvature: a 0.00px contour sampled 512 times at σ=3
carries no curvature"*. Pre-existing, predicted by G1 §3, and the bed carries no `dom` cell for that
scene and profile either way. Recorded and continued, exactly as the run script's banner says.

GPU discipline held throughout: `pgrep` for the capture processes and `lsof -i :5189` clear before
every launch, one capture process at a time, the rebuild detached with a DONE marker and waited on
by a background until-loop.

## 2. The referee (`g2-verify.py`, `g2-referee.txt`)

| check | result |
| --- | --- |
| **X5 — G1's declared digests, byte for byte** | **229 of 229 found and hashed, 229 identical, 0 moved, 0 missing** |
| the whole capture tree against the dry run's (alpha included) | 460 landed, 460 in the dry run, **459 identical, 1 moved** |
| every matrix row against the dry run's | **15 216 rows compared, 0 differ** |
| the bed's shape | **229 cells**, the partition exact; every (profile, tier, set) count equal to the W21 bed's |

Both profile documents' digests are reproduced in the referee's own output above the table it
checked, so the bytes and the constants they were rendered at are in one artifact.

`g1-digests.txt` names **229** captures, one per cell — `grep -c png` and the strict two-field parse
agree. G1 §3 and claims §5.96 say 230; that count includes the file's own `sha256 / capture` column
header, and the correct figure is recorded here beside the first reading rather than in place of
it.

**The one moved file, diagnosed** (`g2-referee.txt`'s tail).
`apple-macos-26.5-1x-dark-standard / checkerboard__glass-over-glass__rest / __css__alpha.png` is a
declaration-conformance render, carries no declared digest, and differs by **two pixels of 64 000,
alpha only, by one code value, at x = 279, y = 19 and y = 198** — the canvas edge, outside the
surface, rgb identical. Nothing measured moved with it (the 15 216-row comparison includes that
cell's four `--alpha` conformance rows and finds none differing). Re-captured a third time to
scratch under the same flags it reproduces the DRY RUN's bytes exactly, and the render capture
beside it is `a7070449926fb91f…` on all three runs — so two of three captures at this configuration
agree byte for byte and the third differs by one code value of alpha at two edge pixels. A session
byte-state on the conformance render, of the shape W21's landing recorded on its increased-contrast
toolbar cell. The landed file is left as captured; `web-captures/` is gitignored and is not part of
the commit either way.

## 3. The gate (`g2-gate.txt`, `g2-predicate.py`, `g2-floors.py`)

`adopted-thresholds.test.ts`: **33 of 33 pass** over the canonical matrix, with the four
`PREDICATE_EXCLUDES` lines G1 §8 named removed and the reason recorded in the file's own comment
(W22 Decision Log 4 (e); claims §5.96 §6).

**The predicate is a derivation, and here it is.** The machine's own list off the LANDED matrix —
the same four arms the test reads, `silhouetteAreaNative` / `Web` against 0.95 × `componentRegionArea`
and `silhouetteBodiesNative` / `Web` against `componentRegionBodies` — is **29 lines**, and equals
`PREDICATE_EXCLUDES` exactly (`equal: True`). Four lines leave the W21 bed's list and none joins:

    LEAVES  texture / calibration / checkerboard__rrect-md__rest         / apple-macos-26.5-2x-light-standard
    LEAVES  texture / calibration / checkerboard__rrect-ml__rest         / apple-macos-26.5-2x-light-standard
    LEAVES  texture / holdout     / checkerboard__glass-over-glass__rest / apple-macos-26.5-2x-light-standard
    LEAVES  texture / holdout     / checkerboard__rrect-lg__rest         / apple-macos-26.5-2x-light-standard

and the arm that let go is the BODIES arm, read on both beds:

| cell (2x light, texture) | region | areaWeb W21 → landed | bodiesWeb W21 → landed | IoU | contour mean | P95 |
| --- | ---: | --- | --- | --- | --- | --- |
| `checkerboard__rrect-md__rest` | 60 064 / 1 | 59 937 → 60 034 | **2 → 1** | 0.99792 → 0.99953 | 0.1335 → 0.0302 | 1 → 0 |
| `checkerboard__rrect-ml__rest` | 112 200 / 1 | 112 031 → 112 164 | **3 → 1** | 0.99861 → 0.99981 | 0.1202 → 0.0164 | 1 → 0 |
| `checkerboard__glass-over-glass__rest` | 112 416 / 1 | 112 183 → 112 401 | **3 → 1** | 0.99750 → 0.99803 | 0.1068 → 0.0031 | 1 → 0 |
| `checkerboard__rrect-lg__rest` | 175 240 / 1 | 175 015 → 175 197 | **4 → 1** | 0.99885 → 0.99993 | 0.1199 → 0.0075 | 1 → 0 |

`silhouetteAreaNative` is bit-identical on all four (the native fixtures did not move); the whole
movement is on the web side. The resting specular band had been fragmenting vitrea's own silhouette
and the predicate refuses a mask in pieces, so the bed had been excluding four cells for a defect in
the RENDERER rather than one in the extractor. The gate now covers four cells more, each meeting
every bound it newly carries, and no bound was widened to take them.

**`UNMET_ROWS` stays 11 and every floor was re-read on the landed matrix. 11 held, 0 broken, none
inert** — each landed reading still misses the adopted bound its floor narrows, so no floor comes
off and none was re-pinned or moved.

| floor | bound it misses | floor | W21 bed | **landed** |
| --- | --- | ---: | ---: | ---: |
| dom / cal / `checkerboard__rrect-md` / 2x light :: `ssimMean` | ≥ 0.92 | ≥ 0.9142 | 0.915209 | **0.915232** |
| dom / cal / `checkerboard__rrect-ml` / 1x light :: `ssimMean` | ≥ 0.90 | ≥ 0.8748 | 0.875848 | **0.875656** |
| dom / cal / `checkerboard__rrect-ml` / 2x light :: `ssimMean` | ≥ 0.92 | ≥ 0.8779 | 0.878934 | **0.878912** |
| dom / hold / `checkerboard__glass-over-glass` / 1x light :: `ssimMean` | ≥ 0.90 | ≥ 0.8604 | 0.861410 | **0.862768** |
| dom / hold / `checkerboard__glass-over-glass` / 2x light :: `ssimMean` | ≥ 0.92 | ≥ 0.8677 | 0.868108 | **0.868461** |
| dom / hold / `checkerboard__rrect-lg` / 1x light :: `ssimMean` | ≥ 0.90 | ≥ 0.8693 | 0.870387 | **0.869928** |
| dom / hold / `checkerboard__rrect-lg` / 2x light :: `ssimMean` | ≥ 0.92 | ≥ 0.8712 | 0.872200 | **0.872256** |
| **texture / hold / `checkerboard__glass-over-glass` / 2x dark :: `silhouetteIoU`** | ≥ 0.93 | ≥ 0.9257 | 0.926728 | **0.927320** |
| **dom / hold / same :: `silhouetteIoU`** | ≥ 0.93 | ≥ 0.9038 | 0.904819 | **0.904935** |
| **dom / hold / same :: `contourDistanceMean`** | ≤ 0.5 | ≤ 1.8602 | 1.760176 | **1.760176** |
| **dom / hold / same :: `contourDistanceP95`** | ≤ 3.0 | ≤ 13.1 | 13.0 | **13.0** |

The four in bold are W21's, on the 2x dark nested pane, re-read here for the first time on a bed
that carries W22 G3's fix. Two improve (+0.00059, +0.00011), two are bit-identical, all four still
miss their bound. Their landed values are recorded beside the W21 numbers in the file's own comment;
the `measured` and `floor` fields are untouched. The other seven move by ±0.0014 at most and every
one of the four whose reading fell (`rrect-ml` 1x, `rrect-lg` 1x, `rrect-ml` 2x) stays above its
floor with room — the smallest margin on the bed is `rrect-lg` 1x at +0.00063 over ≥ 0.8693.

## 4. The chain (`g2-chain.txt`)

| step | result |
| --- | --- |
| `pnpm -r build` | green (this is also the demo's build; see §5) |
| `pnpm -r lint` | green |
| `pnpm -r test` | **1 880 tests over 130 files, all passing** — 23 policy, 162 motion, 170 geometry, 399 renderer-webgpu, 302 core, 444 platform-web, 279 calibration, 101 react; `adopted-thresholds` and `tier-coherence` among them, over the canonical matrix |
| `@vitrea/renderer-webgpu test:golden` | **29 / 29** |
| `packages/platform-web` Playwright, all four projects | **376 passed** |
| `@vitreajs/vitrea-react test:e2e` | 1–3 failing cases per run, a DIFFERENT one each run, all from `press.spec.ts` / `morph.spec.ts` — the tracker's standing Firefox intermittent; see below |
| `demo test:e2e` | **39 passed**, after the harness fixture was re-copied (§5) |

**The react e2e result is recorded as a distribution, not claimed green.** Three consecutive runs of
this one unchanged tree failed 3, then 1, then 1 case, and no case failed twice: chromium
`press.spec.ts:93` + firefox `morph.spec.ts:191` + firefox `press.spec.ts:138`, then chromium
`morph.spec.ts:222`, then firefox `morph.spec.ts:284`. Each failing case passes on repeat
(`morph.spec.ts --project=chromium --repeat-each=3`: 27 passed). That is exactly the tracker's entry
"`packages/react`'s press and morph specs are flaky on Firefox", whose own re-measurement over four
runs of an unchanged tree read 0, 2, 4, 4. Every affected case asserts a driver output AT A MOMENT,
and nothing this wave moved is in a press or a morph: the shimmer amplitude, `specularGain` and the
backdrop-stack tone reach the optics and highlight passes, not the geometry or the press channel.

## 5. The demo

The demo reads the matrix at BUILD time — `apps/demo/src/site/calibration.ts` imports
`packages/calibration/results/matrix.json` directly and every figure on the page is keyed by the
cell that produced it — so the Calibration section's numbers follow this rebuild with no edit, and
`pnpm -r build` (above) rebuilt it against the landed matrix. `apps/demo/vite.config.ts` copies only
`apps/reference-apple/fixtures/`, which this wave does not touch.

One file did have to move. `apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.png`
is a byte copy of the harness's own capture, kept beside the spec because `web-captures/` is not
committed, and `reference-panel.gpu.spec.ts` compares the live reference panel against it — its doc
comment says in terms that a recalibration moving that scene's GPU capture moves this fixture with
it. It was byte-identical to the W21 bed and **178 px / max 46 code values** from the landed capture
(the rim band, `specularGain` 0.55 → 0). Both it and its `.cell.json` were re-copied from
`web-captures/apple-macos-26.5-1x-light-standard/checkerboard__capsule-button__rest/`; the cell
record now names the document the capture was actually taken at (`sha256:9360d73bd071`, where the
committed copy still said `16c2f2805f87`). The demo suite is green after the copy.

## 6. The bed at the landing — ΔE mean per profile, tier and set (`g2-referee.txt` (v))

Every one of the twenty-four columns reproduces claims §5.96 §3's "after" to the decimal it states.

| profile | tier | calibration | validation | holdout | §5.96 §3 |
| --- | --- | ---: | ---: | ---: | --- |
| 1x light standard | webgpu | 0.00330 | 0.00261 | 0.00914 | matches |
| 2x light standard | webgpu | 0.00333 | 0.00263 | 0.00906 | matches |
| 1x dark standard | webgpu | 0.00404 | 0.00291 | **0.01326** | matches |
| 2x dark standard | webgpu | 0.00403 | 0.00329 | **0.01301** | matches |
| 1x light increased-contrast | webgpu | 0.00793 | 0.00862 | 0.02042 | matches |
| 1x light reduced-transparency | webgpu | 0.00172 | 0.00113 | 0.00341 | matches |
| 1x light standard | css | 0.00699 | 0.00544 | 0.01581 | matches |
| 2x light standard | css | 0.00727 | 0.00563 | 0.01618 | matches |
| 1x dark standard | css | 0.00682 | 0.00362 | **0.01732** | matches |
| 2x dark standard | css | 0.00699 | 0.00401 | **0.01724** | matches |
| 1x light increased-contrast | css | 0.01300 | 0.01531 | 0.04557 | matches |
| 1x light reduced-transparency | css | 0.00442 | 0.00473 | 0.00752 | matches |

Cell counts: 20 / 6 / 10 on each light-standard tier, 9 / 1 / 3 on each dark tier, 6 / 1 / 2 and
5 / 1 / 2 on the two accessibility profiles (dom 6 / 1 / 1 under increased contrast, the cell the
bed lost at W18). 229 in all.

## 7. The changeset

`.changeset/resting-surfaces-settle.md`, `"@vitreajs/vitrea-web": minor` — the three published
packages are a `fixed` group, so core and react bump with it. It states the three things a consumer
of 0.11.0 gets: the resting band gated on a shimmer amplitude with `--vitrea-shimmer` as the new
channel (claims §5.94), the light material's rim specular fitted to 0 with the CSS tier's derived
interior level following it (§5.96), and a group stacked over other glass handed that glass's
composite tone (§5.95).

## 8. By eye (X6), and the sheets

`../sheets/g2-1x.png` (522 532 bytes) and `../sheets/g2-2x.png` (1 036 366 bytes), thirteen rows
each: native | GPU BEFORE (the W21 bed, copied to scratch before the rebuild) | GPU LANDED | CSS
LANDED, every untinted solid in both schemes, both stacked scenes in both schemes, and the dark
`impulse` capsule, whole canvas at W21's zoom. Both sent to the MacBook by Taildrop.
`make-sheet.py` gained one line for it: column 3's label is now per gate, so a G2 sheet says it is
the canonical bed rather than a dry run.

What the landed columns show, against G1's dry-run sheets: the same pictures. The resting band is
absent from every left edge, the dark nested pane's overlay is darker than its base on both tiers as
Apple's is, and `dark-solid__rrect-md` in light is symmetric and uniformly fainter than native — the
deferred collapsed rim, visible. **S7 remains the user's and is open.**

## 9. Gaps, blocks and notes for the ledger

1. **One conformance capture is not byte-reproducible** (§2): two pixels of alpha at the canvas edge
   on the 1x dark nested pane's `__css__alpha.png`, one code value, no measured row affected, and it
   reproduces the dry run's bytes on a third capture. A session byte-state, the second of its shape
   after W21's. Nothing is committed from `web-captures/`, so it costs the record nothing — but two
   landings in a row have now seen one, which is worth a tracker line rather than a claim of
   determinism the bed cannot make on the conformance path.
2. **The react e2e suite cannot be read as a pass/fail at a landing** (§4). The tracker already
   carries the entry and its fix shape (bracket the trajectory, then put the suite in CI); this
   landing adds a fourth distribution to it, 3 / 1 / 1, and one chromium failure where the entry
   says chromium passes every time.
3. **The demo's harness fixture is a hand-copied byte copy** (§5) kept current by a doc comment. It
   went stale between the landing and the copy, and only the 0.02 tolerance kept the spec green
   while it was — a recalibration that moved the cell further would have failed the demo suite for a
   reason that reads like a demo bug. A tracker line: the copy could be a script the rebuild runs.
4. **Nothing else moved.** No adopted bound widened, no floor re-pinned or removed, `UNMET_ROWS`
   unchanged, the partition unchanged, and the ΔE table equal to the declaration.
