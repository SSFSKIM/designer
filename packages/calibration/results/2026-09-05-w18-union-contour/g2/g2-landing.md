# W18 G2 — the landing (2026-09-05)

The CSS tier's outer shadow out of its own sampled backdrop (claims §5.78; W18 Decision Log 4,
the user's: "land it as declared") landed on `main`: the decision recorded in the spec at
`37065ab`, the merge `079d446` (W18 G1, branch `w18-g1-shadow` at `2d11305` — one worker's three
commits: the two carriers behind a pure planner, the group state's `cssShadow` form, the sampled
bound in `optics.ts`, contract X7's paint-order pin, the pre-check on G0's separation bed, the
whole-bed dry run with the holdout read once, the sheets), then the canonical rebuild and the
bookkeeping below. The parent ran every step of G2.

## 1. The rebuild

`g2-rebuild.sh` (this directory, from W17's): workspace build at `079d446` (one untracked path,
this directory; nothing tracked dirty), the W17 bed and its captures kept in scratch
(`matrix-before-w18.json`, `web-captures-before-w18` under `~/.claude/jobs/5c70e47f/tmp/w18/g2/`),
`results/matrix.json` removed, then the twelve per-profile runs — calibration, validation and
holdout on every profile, one renderer per run, the GPU tier first — to the canonical matrix and
captures. `g2-runs.txt`: eleven runs `exit=0` and one `exit=1` — `1x-light-increased-contrast /
css`, on the one cell that cannot be measured (`hc-text__capsule-button__rest`: `contourCurvature:
a 0.00px contour sampled 512 times at σ=3 carries no curvature`; `--write-partial` kept the
profile's other eight dom cells, as at the dry run). ALL RUNS DONE 07:18:56; **229 cells, 229
captures** where the W17 bed carried 230. GPU custody 07:14:04–07:18:56.

The holdout's CSS rows were read once, on the frozen configuration at G1 (contract X8, Decision
Log 3); the rebuild reproduces that reading (§2).

## 2. Against the W17 bed and the dry run (`g2-verify.py`, `g2-verify.txt`)

- **GPU tier, every profile (115 cells): every row equal to the W17 bed's (worst |Δ| 0.000000)
  and every capture byte-identical, 115 / 115** — contract X3 on the canonical bed itself, the
  eighth whole-bed run in a row where it holds exactly.
- **CSS tier (114 cells): every row within 0.000028 of the dry run's and 112 / 114 captures
  byte-identical.** The two that differ, `checkerboard__glass-over-glass__rest` on the 2x dark
  profile (6 408 of 256 000 px) and `hc-text__capsule-button__rest` at 2x light (746 px), by 1
  code with alpha untouched — the CSS tier's frame timing on this machine (the tracker's entry;
  W15 one cell, W16 two, W17 one, W18 two). No row moved past the fifth decimal.
- **The carrier each group drew** is recorded per group in the capture's `report__css.json`
  (`page.groups[].state.cssShadow`), which the matrix schema does not carry: `group` on the six
  `toolbar-group` groups (both scenes on the two light-standard profiles, `photo` under reduced
  transparency and increased contrast), `layer` on the other 114, `host` on none — no bed scene
  clips its host's overflow.

## 3. The seven rows held by floor, and what the landing does with each

`ssimMean`, CSS tier, checkerboard; the floor one `FLOOR_EPSILON` (0.001) under the reading,
truncated, as every floor in the file sits. `rrect-md` at 1x has had no floor since W16 and reads
0.91218 → 0.91214 against ≥ 0.90.

| cell | dpr | W17 bed | landed | floor was | floor now |
| --- | --- | --- | --- | --- | --- |
| `rrect-md` | 2x | 0.91529 | 0.91521 | 0.9142 | 0.9142 — kept (inside the epsilon) |
| `rrect-ml` | 1x | 0.87574 | 0.87585 | 0.8747 | 0.8748 — ratchet |
| `rrect-ml` | 2x | 0.87892 | 0.87893 | 0.8779 | 0.8779 — kept |
| `glass-over-glass` | 1x | 0.86095 | **0.86141** | 0.8599 | 0.8604 — ratchet |
| `glass-over-glass` | 2x | 0.86809 | 0.86811 | 0.8677 | 0.8677 — kept |
| `rrect-lg` | 1x | 0.87021 | 0.87039 | 0.8692 | 0.8693 — ratchet |
| `rrect-lg` | 2x | 0.87222 | 0.87220 | 0.8712 | 0.8712 — kept |

Three floors up, four kept, none down; no row meets its adopted bound, so `UNMET_ROWS` stays at
7 — all seven the tier's large spans against the rim band it has no lens to draw, unchanged in
kind. The rows moved by the shadow's share of a large span's interior, which is small (the
shadow's reach is σ 15.55 px against a 224–280 px span). The seven are the only dom rows under
any adopted bound on the bed (`g2-verify.txt`).

## 4. Adopted thresholds (`test/adopted-thresholds.test.ts`)

- **Floors:** the seven above re-recorded at the canonical readings (§3), with the W18 paragraph
  beside them.
- **`PREDICATE_EXCLUDES` 33 → 29 lines**, four out and none in, the machine's output. Three are
  the light solids W17 admitted — `light-solid__rrect-md__rest` at 2x, `light-solid__rrect-ml__rest`
  at both light scales — and the arm that held them was the **bodies** arm, not the area arm W17's
  paragraph names (corrected beside, W17's text left as written): on the W17 bed their web
  silhouettes recovered 0.994–0.998 of the region but in two or three bodies against the region's
  one. The tier's sampled shadow, offset downward, darkened the body's lower rows toward the
  background (the bottom two rows of `rrect-ml` at 1x read 0.923 in linear light against the
  centre's 0.933) and the luminance-delta extractor cut the silhouette there; with the shadow
  outside the sampled region those rows lift by 0.0013–0.0023, the centre does not move (the
  interior mean +0.0003…+0.0008), and the silhouette is one body again at 0.9997–0.9999. The
  fourth line, `hc-text__capsule-button__rest` under increased contrast, comes off because the bed
  lost the cell (§1); it does not condition.
- **The cell counts are per tier now.** `GatedProfile.cellsPerTier` served both tiers with one
  number; the increased-contrast profile's dom tier carries eight cells to the texture tier's nine,
  so the field is `cells: { texture, dom }` on every profile, `MATRIX_PARTITION` reads 17 for that
  profile and `MATRIX_CELLS` 229, each with the row's name beside it.
- Calibration suite **264 passed** (18 files) after the edits — 261 at W17 plus the branch's
  coherence tests on the paint order (X7).

## 5. The stops, re-read at the landing

Every CSS row is within 0.00003 of the dry run's, so every reading in `g1-dry-run.md` stands on
the canonical bed. S1 met (§2). S2 met: every dom row inside its bound or above its floor after
the bookkeeping; the seven held rows at or above their W17 pins, three up. S3 met (the spans'
spread unmoved to the sixth decimal; the one standing W17 miss on `checkerboard__rrect-ml` at 2x
is the W17 bed's). S4: the four cells the wave is for met — `checkerboard__toolbar-group`
−0.0028 / +0.0044, `photo__toolbar-group` −0.0087 / −0.0044 against the renderer, from −0.0122 /
−0.0040 / −0.0150 / −0.0101 — and the fold's clause fires on both profiles as at G1
(`photo__toolbar-group` under reduced transparency −0.0320 → −0.0281, under increased contrast
+0.0096 → +0.0139); two capsule cells cross W17's 0.01 line by a thousandth
(`checkerboard__capsule-button` 2x +0.0102, `hc-text__capsule-button` 1x +0.0105), three leave it
in the good direction, seventeen stand unmoved. S5 as at G1: twenty-one of twenty-two
single-member light cells inside 0.002 of their derived share, `checkerboard__rrect-sm` 1x by
0.0005. S6 met: the cross-tier ΔE down on four profiles, flat on two. S7 met: the list goes down
by four and up by none. S8 met at the pre-check; nothing in the landing moved the form. S9: the
sheets (§7) are the dry run's panels; the user read them before deciding.

## 6. The demo fixture

`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.{png,cell.json}` compared with
the canonical captures: both byte-identical to what was committed (the GPU tier did not move),
nothing to commit; the demo's e2e suite is in the chain below.

## 7. The sheets (`sheets/g2-1x.png`, `g2-2x.png`)

The five panels are pixel-identical to G1's dry-run sheets on every row at both scales (the
sheet's cells are not the frame-timing cells); the only differing pixels are the banner rows (8–41
at 1x, 8–54 at 2x), because `make-sheet.py`'s banner now says which gate the third column is from
— "W18 candidate" at G1, "W18 landed, canonical" at G2 — rather than being labelled one gate
behind (W17's lesson, applied before the landing sheets were made).

## 8. The workspace

`pnpm -r lint` clean; `pnpm -r test` green, **1 792** tests across eight packages; the browser
suites on the landed tree, one at a time on the adapter: platform-web Playwright **354 passed**
(chromium, firefox, webkit, chromium-gpu), react e2e **105 passed, 3 skipped** (three engines),
demo e2e **34 passed**. The renderer's golden suite not re-run and stated: the renderer is
untouched by this wave and byte-identical on 115 / 115 canonical captures. Logs under
`~/.claude/jobs/5c70e47f/tmp/w18/g2/` (`chain.txt`, `lint.log`, `unit.log`, `pw-*.log`).

## 9. Gaps carried out of this landing

- **The fold's two cells** — `photo__toolbar-group` under reduced transparency −0.0281 and under
  increased contrast +0.0139 against the 0.01 clause. The carriers moved each by +0.004; the rest
  is the occlusion's single absolute value (`reducedTransparencyOcclusion` 0.197) against the
  two-regime law on the tier's side, and the drawn border's share under increased contrast —
  each its own measurement against the renderer's declined render on that profile.
- **The box-limited filter's remainder (M2)**, bounded and not derived: −0.0044…−0.0069 per
  44 px box over structure at 1x, sign-flipped at 2x; the two capsule cells over 0.01 by a
  thousandth (`checkerboard__capsule-button` 2x +0.0102, `hc-text__capsule-button` 1x +0.0105)
  are its family. Decision Log 3's square-box sweep is its shape.
- **The stack** — the overlay's term is the renderer's unsampled white on DOM-sourced groups
  (0.042–0.057; the native overlay 0.909 / 0.897 above both tiers), the renderer's charter; the
  base's shadow composite over a glassed body (+0.0081 / +0.0108 on the checkerboard base, 0.0054
  of it by G0's decline), the tier's, with the conversion re-derived at the glassed body's level
  as its shape. `photo__glass-over-glass` stays −0.0118 / −0.0128.
- **The unmeasurable cell** — `hc-text__capsule-button` under increased contrast: an instrument
  item. `cli/compare.ts` aborts a profile's run on a contour it cannot sample where it should
  write the cell with its shape axis marked unmeasurable and its perceptual rows kept; until then
  the bed carries 229 and the profile's dom tier eight.
- **S5's cell** (`checkerboard__rrect-sm` 1x by 0.0005) and the closed form's one-signed
  over-prediction; **the IoU of five fragmentary cells** moved 0.0021–0.0121 (the extractor's
  reach, W17's instrument item; two of the five now condition).
- The renderer's own items, not imported — the thin-span level, the union's kind against
  Apple's, the overlay route; the 2x native probe (the user's session); the plain-`blur()`
  engines' level; the darks on the encoded form; the CSS tier's frame timing (the tracker, two
  cells this wave).
