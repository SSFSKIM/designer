# W19 G2 — the landing (2026-09-05)

The author tint folded over the contrast floor on the CSS tier's linear path (claims §5.81; W19
Decision Log 4 — landed on the parent's recommendation under the user's standing instruction, the
user's eye keeping its veto before `pnpm release`) landed on `main`: the decision recorded at
`496f260`, the merge `062313d` (the G1 branch `worktree-agent-a560cc39a6bdaa3ec` at `b303c33` — one
worker's two commits: the fold at `485b824` with its pins, X7, the tinted contrast-floor e2e and
the pre-check; the whole-bed dry run with the holdout read once), the changeset's two stale
readings corrected at `f9fe52c`, then the canonical rebuild and the bookkeeping below. The parent
ran every step of G2.

## 1. The rebuild

`g2-rebuild.sh` (this directory, from W18's): workspace build at `f9fe52c` (one untracked path,
this directory; nothing tracked dirty), the W18 bed and its captures kept in scratch
(`matrix-before-w19.json`, `web-captures-before-w19` under `~/.claude/jobs/5c70e47f/tmp/w19/g2/`),
`results/matrix.json` removed, then the twelve per-profile runs — calibration, validation and
holdout on every profile, one renderer per run, the GPU tier first — to the canonical matrix and
captures. `g2-runs.txt`: eleven runs `exit=0` and one `exit=1` — `1x-light-increased-contrast /
css`, on the one cell that cannot be measured (`hc-text__capsule-button__rest`, claims §5.79 §1;
`--write-partial` kept the profile's other eight dom cells, as at every landing since W18). Every
run reports 0 scenes fallen back and 0 problems. ALL RUNS DONE 10:22:27; **229 cells, 229
captures**, the W18 bed's 229 keys. GPU custody 10:17:36–10:22:27, the adapter clear before and
after.

The holdout's CSS rows were read once, on the frozen configuration at G1 (contract X8, Decision
Log 3); the rebuild reproduces that reading exactly (§2).

## 2. Against the W18 bed and the dry run (`g2-verify.py`, `g2-verify.txt`)

- **GPU tier, every profile (115 cells): every row equal to the W18 bed's (worst |Δ| 0.000000)
  and every capture byte-identical, 115 / 115** — contract X3 on the canonical bed itself, the
  ninth whole-bed run in a row where it holds exactly.
- **CSS tier (114 cells): every row equal to the dry run's (worst |Δ| 0.000000) and every capture
  byte-identical to the dry run's, 114 / 114** — the first landing whose rebuild reproduces its
  dry run to the byte.
- **Against the W18 bed's bytes:** untinted 79 / 81 — the two are the tracker's frame-timing pair,
  `hc-text__capsule-button__rest` at 2x light (746 px) and `checkerboard__glass-over-glass__rest`
  at 2x dark (6 408 px), one code each; three Chromium processes today (the dry run, its second
  run, this rebuild) agree with each other and differ from W18's landing captures, so the pair
  flips between landings and not within a day's runs (the tracker's entry amended). Tinted
  12 / 33 — exactly the twelve groups on the encoded form.
- **The form each group drew**, off the capture's `report__css.json` (`page.groups[].state.cssTint`,
  which the matrix schema does not carry): `linear` on 82 groups (21 on tinted scenes), `encoded`
  on 38 (12 on tinted scenes: the dark scheme's six, and the light scheme's `dark-solid` blue and
  orange and `impulse` orange at both scales — the boundary puts the light capsules over dark
  backdrops on the encoded form, which never reads `untintedOptics`; this corrects the dry-run
  report's "floor colours equal to eight bits", beside claims §5.81 §4). `cssShadow`: `group` on
  the six `toolbar-group` groups, `layer` on 114, as at W18.

## 3. The seven rows held by floor

`ssimMean`, CSS tier, checkerboard; every capture byte-identical to the dry run's and to the W18
bed's, so every reading is the W18 bed's to five places:

| cell | dpr | W18 bed | landed | floor |
| --- | --- | --- | --- | --- |
| `rrect-md` | 1x | 0.91214 | 0.91214 | no floor since W16; ≥ 0.90 met |
| `rrect-md` | 2x | 0.91521 | 0.91521 | 0.9142 kept |
| `rrect-ml` | 1x | 0.87585 | 0.87585 | 0.8748 kept |
| `rrect-ml` | 2x | 0.87893 | 0.87893 | 0.8779 kept |
| `glass-over-glass` | 1x | 0.86141 | 0.86141 | 0.8604 kept |
| `glass-over-glass` | 2x | 0.86811 | 0.86811 | 0.8677 kept |
| `rrect-lg` | 1x | 0.87039 | 0.87039 | 0.8693 kept |
| `rrect-lg` | 2x | 0.87220 | 0.87220 | 0.8712 kept |

Seven kept, none ratcheted, none down; `UNMET_ROWS` stays at 7. `adopted-thresholds.test.ts`
against the canonical matrix: **31 / 31 with no literal edited**; a comment in the floors block
records the landing. `PREDICATE_EXCLUDES` unchanged — the gate proves it equal to the machine's
output.

## 4. The wave's stops, re-read on the canonical bed

Every number is the dry run's (claims §5.81), because every CSS capture is the dry run's byte for
byte: S3's nineteen full-strength linear cells differ from the W18 bed on the contour only
(interior means within 0.00013); S4's twelve light-standard tinted scenes at their bed values
(eleven inside 0.005; `hc-text__capsule-button__rest-tint-orange` +0.0128 / +0.0117 standing —
the shade's granularity, claims §5.81 §5), the fold profiles +0.0056 / +0.0055 / +0.0002; S5's
`orange-half` captures byte-identical to the dry run's (−0.00311 / −0.00327, the clamp share
0.0000 %); S6's cross-tier ΔE mean 0.00606 → 0.00599 at 1x and 0.00633 → 0.00627 at 2x light
standard, 0.00385 → 0.00384 under reduced transparency, flat on the other three. The one cell
that moves: `photo__capsule-button__rest-tint-orange-half`, OKLab ΔE against Apple 0.0043 →
0.0032 (1x) and 0.0045 → 0.0033 (2x), across the tiers 0.0050 → 0.0034 and 0.0051 → 0.0035; every
other tinted cell flat to four places.

## 5. The sheets, and the demo fixture

`sheets/g2-1x.png` and `g2-2x.png` — the G1 script with column 3 the canonical capture (the
banner says "W19 landed, canonical"). Read by the parent: identical to G1's sheets to the eye, as
the bytes say — the cold, washed-out low-strength rungs replaced by the warm cast Apple and the
renderer carry; the bed's two rows unmoved; the `hc-text` row's text through the GPU tier's tint
and not the CSS tier's, the granularity item, seen.

`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.png` is byte-identical to the
landed GPU capture (sha256 `4d9ac2ac…`); nothing to commit.

## 6. The chain

`chain.sh` (scratch), 10:23:09–10:25:50, the browser suites one at a time on the adapter, Reduce
Transparency and Increase Contrast off: `pnpm -r lint` clean; `pnpm -r test` green on all eight
packages (122 test files); `packages/platform-web` Playwright **355 passed** across chromium,
firefox, webkit and chromium-gpu on the real adapter; react **105 passed, 3 skipped**; demo
**34 passed**. The renderer's golden suite not re-run: the renderer is byte-identical by capture.

## 7. The hashes, after the push

The push rebased the local history over `origin/main` and flattened the merge, so the hashes
above are the pre-push labels: the fold `485b824` is `4e7e75b` on `main`, the dry run `b303c33` is
`8cb1d3c`, the changeset correction `f9fe52c` is `1abda3e`, the merge `062313d` does not exist
(the branch's two commits sit linearly after `496f260`, unchanged). The trees are identical; the
landing is `0089cae` and the recomposition `4ab7ff4` (claims §5.82, correction beside).
