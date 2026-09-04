# W17 G2 — the landing (2026-09-05)

The CSS tier's interior level (claims §5.75; W17 Decision Log 7, the user's: "land as declared")
landed on `main`: the decision recorded in the spec, the merge `6c97c3a` (W17 G1, branch
`w17-g1-level` at `033ea6b` — one worker's seven commits: the mirror in the shader's order with
the inner shadow, the tint's lerp as a table in the sharp layer's linear-light filter over the
doctrine's floor, the declared boundary for the darks, contracts X6 and X7, three configurations,
the refuted region sweep, the toolbar residual's evidence, the holdout read once), then the
canonical rebuild and the bookkeeping below. The parent ran every step of G2.

## 1. The rebuild

`g2-rebuild.sh` (this directory, from W16's; its header comment corrected after the run, the
commands unchanged): workspace build at `6c97c3a` (one untracked path, this directory; nothing
tracked dirty), the W16 bed and its captures kept in scratch (`matrix-before-w17.json`,
`web-captures-before-w17` under `~/.claude/jobs/5c70e47f/tmp/w17/g2/`), `results/matrix.json`
removed, then the twelve per-profile runs — calibration, validation and holdout on every profile,
one renderer per run — to the canonical matrix and captures. `g2-runs.txt`: every run `exit=0`,
ALL RUNS DONE 01:19:45; 230 cells, 230 captures. GPU custody 01:14:58–01:19:45.

The holdout's CSS rows were read once, on frozen configuration 3 at G1 (contract X8, Decision
Log 6); the rebuild reproduces that reading (§2).

## 2. Against the W16 bed and the frozen configuration (`g2-verify.py`, `g2-verify.txt`)

- **GPU tier, every profile (115 cells): every row equal to the W16 bed's (worst |Δ| 0.000000)
  and every capture byte-identical, 115 / 115** — contract X3 on the canonical bed itself, the
  seventh whole-bed run in a row where it holds exactly.
- **CSS tier (115 cells): every row within 0.000048 of frozen configuration 3's and 114 / 115
  captures byte-identical.** The one that differs, `photo__toolbar-group__rest` under increased
  contrast, by 1 code on 96 of 64 000 px with alpha untouched — the CSS tier's frame timing on
  this machine (the tracker's entry; W15 one cell, W16 two, W17 one). No row moved past the
  fifth decimal.
- **The form each group drew** is recorded per cell in the capture's `report__css.json`
  (`"cssTint": "linear"` on the light cells, `"encoded"` on the dark scheme and the near-black
  composites), beside W16's `cssBody`; the matrix schema does not carry it.

## 3. The eight rows W11c floored, and what the landing does with each floor

`ssimMean`, CSS tier, checkerboard; the floor one `FLOOR_EPSILON` (0.001) under the reading,
truncated, as every floor in the file sits. `rrect-md` at 1x has had no floor since W16 and
reads 0.9028 → **0.9122** against ≥ 0.90.

| cell | dpr | W16 bed | landed | floor was | floor now |
| --- | --- | --- | --- | --- | --- |
| `rrect-md` | 2x | 0.91489 | 0.91529 | 0.9138 | 0.9142 — ratchet |
| `rrect-ml` | 1x | 0.85925 | **0.87574** | 0.8582 | 0.8747 — ratchet |
| `rrect-ml` | 2x | 0.87829 | 0.87892 | 0.8772 | 0.8779 — ratchet |
| `glass-over-glass` | 1x | 0.85286 | **0.86095** | 0.8518 | 0.8599 — ratchet |
| `glass-over-glass` | 2x | 0.86832 | 0.86809 | 0.8677 | 0.8677 — kept (inside the epsilon) |
| `rrect-lg` | 1x | 0.85126 | **0.87021** | 0.8502 | 0.8692 — ratchet |
| `rrect-lg` | 2x | 0.87089 | 0.87222 | 0.8698 | 0.8712 — ratchet |

Six floors up, one kept, none down; no row meets its adopted bound, so `UNMET_ROWS` stays at 7 —
all seven the tier's large spans against the rim band it has no lens to draw, unchanged in kind.
The seven are the only dom rows under any adopted bound on the bed (`g2-verify.txt`).

## 4. Adopted thresholds (`test/adopted-thresholds.test.ts`)

- **Floors:** the seven above re-recorded (§3), with the W17 paragraph beside them.
- **`PREDICATE_EXCLUDES` moves by one out and four in** (30 → 33 lines), the machine's output:
  `checkerboard__capsule-button__rest` under reduced transparency LEAVES — its fold recovers
  0.9961 of its region with one body once the tier's level is the renderer's, the shape-axis
  loss W16 recorded and this wave set out to close; `light-solid__rrect-md__rest` at 2x,
  `light-solid__rrect-ml__rest` at both light scales and `hc-text__capsule-button__rest` at 2x
  JOIN, all `areaWeb`, one mechanism: a surface at the renderer's level sits within 0.004 of
  its own background (0.9315–0.9322 over 0.9337–0.9347 on the light solids), and the
  luminance-delta extractor separates the GPU tier there only by the rim and lens the CSS tier
  does not draw. Every one of the four still gates on its perceptual rows.
- Calibration suite **261 passed** (18 files) after the edits — 257 at W16 plus the branch's
  four coherence tests on the tier's composite (X7).

## 5. The stops, re-read at the landing

S1 met (§2). S2 met: every dom row inside its bound or above its floor after the bookkeeping;
the seven held rows at or above their W16 pins, six up. S3 (one-sided, Decision Log 4 (d)) fires
on `checkerboard__rrect-ml` at 2x by 0.0005 — as at G1. S4 fires on the two `toolbar-group`
scenes, `photo__glass-over-glass` and `hc-text__capsule-button` at 2x — as at G1, carried.
S5 (against the renderer, Decision Log 3) met except the two holdout cells 0.001–0.003 past
0.01 and the three ΔE rises of 0.0006–0.0010 — as at G1. S6 fires by +0.00012 on increased
contrast; falls on both light-standard profiles and reduced transparency; the dark profiles
unchanged on the encoded form. S7 one of two: the reduced-transparency `hc-text` capsule reads
0.9310 against 0.95 and stays excluded. S8 met (G1's cost run; nothing in the landing moved the
form). S9: the sheets (§7) are the dry run's panels; the user read them before deciding.

## 6. The demo fixture

`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.{png,cell.json}` re-copied
from the canonical captures: both byte-identical to what was committed (the GPU tier did not
move), nothing to commit; the demo's e2e suite is in the chain below.

## 7. The sheets (`sheets/g2-1x.png`, `g2-2x.png`)

The five panels are pixel-identical to G1's dry-run sheets on every row at both scales (the
sheet's cells are not the frame-timing cell); the only differing pixels are the banner rows
(40–45 at 1x, 40–59 at 2x), because `make-sheet.py`'s banner — copied from W16 and one wave
behind on the G1 sheets — was corrected before the landing sheets were made. On the G1 sheets
column 2 is the W16 bed and column 3 this candidate, as the G2 sheets say.

## 8. The workspace

`pnpm -r lint` clean; `pnpm -r test` green, **1 784** tests; the browser suites on the landed tree, one
at a time on the adapter: platform-web Playwright **342 passed** (chromium, firefox, webkit,
chromium-gpu), react e2e **105 passed, 3 skipped** (three engines), demo e2e **34 passed** after one
pin re-pointed with its reason (`site.spec.ts`: the tinted plate's declared white reads 254 on the
40 px plate because the inner shadow's keep folds into the pair per surface; the assertion is now
"achromatic within one code of white", which was the claim). Logs under
`~/.claude/jobs/5c70e47f/tmp/w17/g2/`.

## 9. Gaps carried out of this landing

- **The union-contour residual** — the two `toolbar-group` scenes (−0.0122 / −0.0040 and
  −0.0150 / −0.0101 against the GPU tier) and `photo__glass-over-glass` (−0.0119 / −0.0127):
  a broad interior offset at every depth with a bright contour band; the two derived residuals
  reach a third of it; the same capsule alone reads −0.0005. Separating the box from its
  neighbours needs a native fixture of a lone 46 px capsule against the three-up arrangement
  (`g1/toolbar-residual.md`). Its own charter.
- **The shape axis's four cells** and the fold's second cell (`hc-text__capsule-button` under
  reduced transparency, recovery 0.9310 against 0.95): the extractor's reach on a surface at the
  renderer's level over a near-tone backdrop. An instrument item — a second arm for the
  extractor (the rim's structure, or the GPU capture's own silhouette as a prior) — not a
  fidelity one.
- The three holdout cells 0.001–0.003 past the level clause (`hc-text__capsule-button` 2x,
  its orange-tinted twin at both scales, `mid-dark-solid__capsule-button` 2x); S3's one cell by
  0.0005; increased contrast's ΔE +0.00012.
- **The dark scheme on the encoded form**, by the declared boundary: its level within 0.011 of
  the GPU tier as it was, the eight-bit linear chain's quantum the reason. Closes only with a
  higher-precision filter intermediate the platform does not offer.
- The plain-`blur()` engines' level (E's, with the ordering fix), behind the conformance rows.
- The CSS tier's frame timing, one cell by 1 code (the tracker).
