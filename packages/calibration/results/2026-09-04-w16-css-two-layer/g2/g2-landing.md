# W16 G2 — the landing (2026-09-04)

The two-layer CSS body (claims §5.72; W16 Decision Log 3, the user's: "land as declared") landed
on `main`: the decision recorded at `c68aa9d`, the merge `595ac5e` (W16 G1, branch
`w16-g1-two-layer` at `b40bfbe` — the worker's element model, raster mask, reference filter,
effective-width conversion, area collapse, conformance field and tests at `af49e00`, then the
parent's dry-run artifacts and sheets), then the canonical rebuild and the bookkeeping below. The
parent ran every step of G2.

## 1. The rebuild

`g2-rebuild.sh` (this directory, from W15's): workspace build at `595ac5e` (one untracked path,
this directory; nothing tracked dirty), the W15 bed and its captures kept in scratch
(`matrix-before-w16.json`, `web-captures-before-w16` under `~/.claude/jobs/5c70e47f/tmp/w16/g2/`),
`results/matrix.json` removed, then the twelve per-profile runs — calibration, validation and
holdout on every profile, one renderer per run — to the canonical matrix and captures.
`g2-runs.txt` is the driver log: every run `exit=0`, ALL RUNS DONE 19:11:56; 230 cells, 230
captures. GPU custody 19:07:09–19:11:56, nothing else on the adapter.

The holdout's CSS rows were read once, at G1's second dry run (contract X8); the rebuild
reproduces that reading rather than re-reading it (§2). No cell on the bed can reach the area
collapse: the stage is 320 × 200 CSS px, 256 000 device px at 2x for the whole capture, under the
0.4 M-per-layer budget by a factor of 1.56 before any surface is smaller than its stage.

## 2. Against the W15 bed and the dry run (`g2-verify.py`, `g2-verify.txt`)

- **GPU tier, every profile (115 cells): every row equal to the W15 bed's (worst |Δ| 0.000000)
  and every capture byte-identical, 115 / 115** — contract X2 verified on the canonical bed
  itself, the holdout's GPU rows included.
- **CSS tier (115 cells): every row within 0.000008 of the second dry run's and 113 / 115
  captures byte-identical.** The two that differ are both 2x, both by 1 code with alpha untouched:
  `light-solid__capsule-button__rest` on 473 of 256 000 px and
  `photo__capsule-button__rest-tint-blue` on 1 203 — the CSS tier's frame timing on this machine
  (W15's landing saw one 2x solid cell by 2 codes; W16 Deferred said read it again here, and it
  recurred, so it is the harness's item in the tracker). No row moved past the fifth decimal.
- **The rows** (`g2-tables.md`: every checkerboard, `hc-text` and `photo` row at both scales
  beside the W15 bed and the dry run): the landed column is the dry run's to the digit.

## 3. The eight held rows, and what the landing does with each floor

`ssimMean`, CSS tier, checkerboard; the floor is one `FLOOR_EPSILON` (0.001) under the reading,
truncated, as every floor in the file sits.

| cell | dpr | W15 bed | dry run | landed | floor was | floor now |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` | 1x | 0.89626 | 0.90284 | **0.90284** | 0.8952 | **OFF** — meets ≥ 0.90 |
| `rrect-md` | 2x | 0.91738 | 0.91489 | 0.91489 | 0.9159 | **0.9138** — RE-PINNED by Decision Log 3 (the band) |
| `rrect-ml` | 1x | 0.85153 | 0.85925 | 0.85925 | 0.847 | 0.8582 — ratchet up |
| `rrect-ml` | 2x | 0.88080 | 0.87829 | 0.87829 | 0.8754 | 0.8772 — ratchet up (above the W11c pin 0.87649 even after the fall) |
| `glass-over-glass` | 1x | 0.85158 | 0.85286 | 0.85286 | 0.8489 | 0.8518 — ratchet up |
| `glass-over-glass` | 2x | 0.87089 | 0.86832 | 0.86832 | 0.8677 | 0.8677 — kept (the reading 0.86832 inside the epsilon of the W11c pin 0.86872) |
| `rrect-lg` | 1x | 0.84482 | 0.85126 | 0.85126 | 0.8361 | 0.8502 — ratchet up |
| `rrect-lg` | 2x | 0.87596 | 0.87089 | 0.87089 | 0.8686 | 0.8698 — ratchet up (above the W11c pin 0.8696) |

Decision Log 3 named the re-pin as 0.9159 → 0.9149, the reading itself; the file's rule puts
every floor one epsilon under its reading, so the floor is 0.9138 with `measured: 0.91489`
recorded beside it — the same construction as the seven others. Two of the three 2x floors the
decision said to "keep with their readings updated" ratchet UP instead: their readings, though
0.0025–0.0051 under the W15 bed, are above the W11c pins the file still held (the W13–W15 waves
did not touch the CSS tier, so the live rows had risen 0.0044 above their pins without anyone
ratcheting), and the file's epsilon check does not allow a floor more than 0.0012 under its
recorded reading. A floor going up needs no decision.

## 4. Adopted thresholds (`test/adopted-thresholds.test.ts`)

- **Floors:** the 1x `rrect-md` row REMOVED (0.89628 → 0.90284 against ≥ 0.90), the seven above
  re-recorded; `UNMET_ROWS` **8 → 7**, all seven the CSS tier's large spans at both scales. The
  seven are the only dom rows under any adopted bound on the bed (`g2-verify.txt`).
- **`PREDICATE_EXCLUDES` grows by two** (28 → 30 lines), the machine's output: the capsule under
  reduced transparency on the CSS tier, both cells, both by the `areaWeb` arm. The tier's
  reduced-transparency fold now reads lighter than the reference's interior by 0.056 (the
  checkerboard capsule, 0.9087 → 0.9458 against native 0.8903) and 0.070 (`hc-text`, 0.9308 →
  0.9628 against 0.8932) where the single blur read 0.018 and 0.038 lighter — the level
  conversion gap of §5.72 §4 seen on the fold — and the luminance-delta extractor loses the
  surface over the checkerboard's white squares and the text bars: recovery 1.000 → 0.915 with
  seven holes, and 0.982 → 0.853. Both cells still gate on every perceptual row and hold them
  (`ssimMean` 0.9829 / 0.9924 against ≥ 0.91, ΔE 0.0044 / 0.0029 against ≤ 0.04). The dry run's
  referee (`verify-dry.py`) did not run the predicate, so this was read at the landing — a W16
  Surprise. `rrect-md` under the same fold recovers 0.993 and stays gated.
- Calibration suite **257 passed** (18 files) on the rebuilt bed after these edits; the
  tier-coherence pins on the two layers over dpr {1, 1.5, 2, 3} are among them.

## 5. The stops, re-read at the landing (charter G2, with G1's numbers)

S1 met (§2). S2: every dom row inside its adopted bound or above its floor after the bookkeeping;
its "none of the eight held rows below the W15 bed's" clause fails on the four large 2x spans by
0.0025–0.0051, with the band as the mechanism (§5.72 §5: `ssimBand` down 0.020–0.028 while
`ssimInterior` rises) — the miss Decision Log 3 accepted, re-declared here rather than met. S3
met at 1x (±0.007) and missed at 2x on `rrect-ml` alone, by 0.0006 (−0.0156 against ±0.015) — as
at G1. S4 met on the four large spans and the thin spans, missed on `hc-text__capsule-button` by
0.0030 (0.9769 against its pre-W11c 0.9799; +0.0030 over the bed) — as at G1. S5 met (the solids
and tinted cells within 0.0004, the photo cells within 0.0008 and toward native in level). S6 met
(`tier-coherence` re-shaped and tighter, the cross-tier ΔE down on every profile). S7 met by
construction on the bed (§1) and by the collapse rule off it. S8: the sheets (§7) are the dry
run's bytes, which the user read before deciding; the decision is the eye's verdict.

## 6. The demo fixture

`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.{png,cell.json}` re-copied
from the canonical captures: both byte-identical to what was committed (the GPU tier did not move
and the capture metadata carries no timestamp), so nothing to commit; the demo's e2e suite is in
the chain below.

## 7. The sheets (`sheets/g2-1x.png`, `g2-2x.png`)

Both **byte-identical to G1's dry-run sheets** (`g1-1x.png` sha256 `82035a09…`, `g1-2x.png`
`73eaec77…`): the sheet's rows are the checkerboard spans, `hc-text` and `photo` `rrect-md`, none
of which is one of the two frame-timing cells, so the landing's captures reproduce the dry run's
on every panel. The user's reading of those sheets is Decision Log 3.

## 8. The workspace

`pnpm -r lint` clean; `pnpm -r test` green, **1755** tests; the browser suites on the landed tree, one at
a time on the adapter: platform-web Playwright **342 passed** (chromium, firefox, webkit,
chromium-gpu), react e2e **105 passed, 3 skipped** (three engines), demo e2e **34 passed** (the
reference panel's GPU spec among them). Logs under `~/.claude/jobs/5c70e47f/tmp/w16/g2/`.

## 9. Gaps carried out of this landing

- **The interior level, 0.06–0.09 over native on the checkerboards at both scales** (§5.72 §4):
  one encoded alpha cannot match the renderer's linear lerp in mean and slope; the exact
  two-equation conversion (configuration H) lands on the renderer's analytic composite, which its
  rendered interior exceeds by 0.023–0.058 (the lens, rim and highlight light). Closure: measure
  that excess per span and backdrop on the renderer's own captures and feed it to the
  `feComponentTransfer` solve whose arithmetic is written in `referenceBackdropLuminance`'s
  comment. Its own charter.
- **The same level on the reduced-transparency fold**, now 0.056–0.070 over native on the
  capsule, which costs the shape axis two cells (§4). Closes with the item above.
- **The rim band on the four large 2x spans** — the seven floors' mechanism; no CSS form draws
  a displacement field (W16 Deferred, unchanged).
- The 2x spread on `rrect-ml` by 0.0006 and the `hc-text` capsule's level by 0.0030 (S3, S4).
- The accessibility rows' moves inside their bounds: increased contrast `rrect-md` −0.0036,
  reduced transparency −0.0043.
- The CSS tier's frame timing on this machine, two 2x cells by 1 code (the tracker).
- The software rasteriser's joint area limit for two filtered elements (W16 Deferred).
