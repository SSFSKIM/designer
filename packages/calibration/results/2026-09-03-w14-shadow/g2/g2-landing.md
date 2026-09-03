# W14 G2 — the landing (2026-09-03)

The outer shadow's two-term composite (claims §5.66) landed on `main`: merge `4923219`
(W14 G1, branch `w14-g1-shadow` at `c27b372`), then the canonical rebuild and the bookkeeping
below. The landing worker (a subagent) ran steps 1–2 and was cut off twice by a server-side
overload; the parent carried steps 3–9 by hand from the state it left, which is recorded here.

## 1. The rebuild

`g2-rebuild.sh` (this directory) from W12's `x1-rebuild.sh`: workspace build at `4923219`,
the W12 close bed and captures kept in scratch (`matrix-before-g2.json`, `web-captures-before-g2`
under `~/.claude/jobs/5c70e47f/tmp/w14/g2/`), `results/matrix.json` removed, then the twelve
per-profile runs to the canonical matrix and captures. `g2-runs.txt` is the driver log: every
run `exit=0`, ALL RUNS DONE 22:19:23; 230 cells, 230 captures, every one byte-identical over
two loads. GPU custody: 22:14:27–22:19:23.

## 2. The twelve rows against the declaration (`g2-verify.py`)

Every GPU-tier `ssimMean` and `ssimOutside` on the checkerboard cells at both scales, and
every CSS-tier band reading, reproduces claims §5.66 §4 and §3 within **0.00005** (the
declaration is written to four decimals; the largest delta is rounding). The landing captures of
`checkerboard__rrect-lg` and `light-solid__capsule-button` at 1x are byte-identical to the dry
run's, so the landing sheets (`sheets/g2-*.png`) are the dry run's pictures and the user's
reading of those (claims §5.65 §7) stands as S7.

## 3. Adopted thresholds (`test/adopted-thresholds.test.ts`)

- The suite passed on the rebuilt bed **before any edit**: no row fell below a floor or a bound,
  and `PREDICATE_EXCLUDES` equals the machine's output unchanged.
- **Three floors REMOVED by fix**: the 2x texture-tier `ssimMean` floors on
  `checkerboard__rrect-ml` (0.91579 → 0.97461), `glass-over-glass` (0.92114 → 0.97616) and
  `rrect-lg` (0.91128 → 0.96796) against ≥ 0.93. `UNMET_ROWS` 11 → **8**.
- **`ssimOutside` adopted on all twelve tables** (Decision Log 1 q3), by the file's rule for a
  `≥` row — 0.02 below the worst measurement over every gated cell, floored to the hundredth:
  texture / dom — 1x light 0.84 / 0.82, 2x light 0.87 / 0.72, reduced transparency 0.84 / 0.83,
  increased contrast 0.69 / 0.61, 1x dark 0.83 / 0.78, 2x dark 0.86 / 0.82. The worst rows are
  `photo__rrect-lg` under increased contrast, `photo__toolbar-group` / `checkerboard__rrect-lg`
  on the standard light profiles, and `dark-solid__rrect-md` on the dark profiles (the un-keyed
  thick law's recorded gap). `FLOOR_EPSILON` gains `ssimOutside: 0.001`.
- **X7's pair adopted**, GPU tier, light-standard 1x and 2x, band `3-6` below, within 20%
  (S3's tolerance): the light-solid capsule's occlusion ratio web/native (1.013 / 1.008) and the
  lift `c` ratio on the four thick checkerboard cells (1.001 / 1.003 / 0.949 / 0.916 at 1x,
  1.002 / 0.980 / 0.935 / 0.899 at 2x). 31 tests, up from 27.
- `dark-solid__capsule-button`'s `ssimBand` (S1's named miss, −0.0188 / −0.0474) is not an
  adopted row and fails nothing; carried by name (Decision Log 6).

## 4. Goldens, behind the isolation proof

The proof on the merged tree: 12 of 13 pass. `placed-checkerboard` with the shadow declined
did not reproduce its W12 G2b hash. **Attributed by measurement, not re-recorded blind**: the
declined scene was rendered in a build of the pre-merge commit (`1c865fe`, a temporary
worktree) and in this tree and the readbacks diffed — **1 of 96 000 pixels differs, by 1 of 255**
in RGB, at (290, 141), fully covered, on a smooth interior gradient (217 for 218); the default
renders differ across 48 434 pixels by up to 7 codes of alpha, which is the shadow. The optics
pass now composes body, black term and lift in one expression, and the reordering flips a value
on a rounding boundary. Pinned as `W14_HASHES` in `isolation.spec.ts` with that record;
`goldens:regen`; nine goldens moved; `scenes.spec.ts`'s cover-fit hash re-recorded with its
reason (the cover-fit render casts the shadow like the placed one); golden suite **26 passed**.

## 5. The demo fixture

`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.{png,cell.json}` re-copied
from the canonical captures (the `.cell.json` is the capture's `cell__webgpu.json`);
`reference-panel.gpu.spec.ts` 1 passed.

## 6. The workspace

`pnpm -r lint` clean; `pnpm -r test` green — packages/calibration 255;packages/core 302;packages/geometry 149;packages/motion 162;packages/platform-web 344;packages/policy 23;packages/react 97;packages/renderer-webgpu 373;
