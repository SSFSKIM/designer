# The W13 G1 runtime sweep, third round — the depth ramp's span-graded start (2026-09-03)

The first round swept the ramp as first implemented — a start and a reach per scale,
replacing W11c's span-graded scatter share — and refuted the form in the renderer
(`../sweep/`, claims §5.63). The second round swept the form that refutation asked for —
the span law restored UNDERNEATH the ramp as its deep value, the ramp a near-contour
excursion above it — and refuted that one too, arithmetically (`../sweep-2/`, claims
§5.64). This round sweeps the third form, which W13 Decision Log 4 declared: everything
the second form had, plus a **start that grades with span**.

## The form under the sweep

With `u` the depth inside the contour in DEVICE px and `span` the surface's shorter
border-box extent in CSS px:

    kDeep(span) = sizeScatterFloor + (1 - sizeScatterFloor)
                  * smoothstep(sizeSpanMin, sizeScatterSpanMax, span)      [W11c, unchanged]
    sDeep(span) = 1 - kDeep(span)
    s0(span)    = startThin + (startThick - startThin) * sizeThickness(span)   [NEW]
    s(u, span)  = sDeep + max(0, s0(span) - sDeep) * max(0, 1 - u / U(dpr))
    kScatter    = clamp(floor + ((1 - s) - floor) * fold, 0, 1)            [unchanged]

`sizeThickness` is the material's OWN thin/thick curve — smoothstep(`sizeSpanMin` 32,
`sizeSpanMax` 96), the knee at 64 the face's tone response and the outer shadow already
blend across — so the grading introduces no new span statistic. The second form's four
constants become six: `sizeScatterRampStartThin1x`, `…Thick1x`, `…Thin2x`, `…Thick2x`,
`sizeScatterRampReach1xPx`, `…Reach2xPx`, the reaches keeping their names and their
device-px units.

**Why the start had to grade.** The second form's excursion is `max(0, s0 - sDeep(span))`
with one start per scale, and the bed makes those two requirements disjoint at 1x:
`rrect-sm`'s span is exactly `sizeSpanMin`, so its deep sharp share is exactly
`1 - sizeScatterFloor` = 0.600 and no start at or below 0.600 can touch it, while
`rrect-ml`'s band only improves below a start near 0.583. The reach cannot bridge them —
it sets how much of a surface the excursion covers, never which surfaces it touches
(`../sweep-2/g1-sweep-2.md` §3). G0 read the reference's start as strongly graded by span
(1x: 0.637 / 0.642 on the thin cells against 0.512 / 0.501 / 0.410 on the thick ones), so
the start is given exactly that grading.

## Where it ran

Branch `w13-g1-ramp` (`f77b5f1`, main merged in at `b397ec8`), worktree
`.claude/worktrees/w13-g1`, rebuilt with `pnpm -r build` before the first point so the
captures carry the span-graded shader. Every capture and every per-point matrix was
written to scratch (`VITREA_WEB_CAPTURES=$TMP/web-captures-<name>`, `sweep-work/` inside
the worktree); the main checkout's `results/matrix.json` and `web-captures/` were read and
never written.

**The shared GPU.** It takes one capture at a time and the W14 shadow sweep holds it
between rounds. `pgrep -f 'compare.ts|sweep.ts'` was clear before the first point; the GPU
was taken at **21:45 KST on 2026-09-03**, released at **22:05** while the W14 shadow
wave's CSS-fold `compare.ts` held it, re-taken at **22:07** once `pgrep` was clear again,
and released for good at **22:10** when the confirmation run's fourth profile finished.

## The base

`g1-sweep-3-base.json` is the branch's light profile document
(`profiles/apple-macos-26.5-1x-light-standard.json`) at the third form, reduced to its
`patch` and `cssTierMapping` sections — the fingerprint (`resolvedMaterialSha256`), the
provenance comments and the entries stripped, exactly as the two earlier rounds' bases
were. The sweep re-derives the material per point, so a fingerprint in the base would be a
stale assertion.

## The axes

    # 1x, 36 points
    VITREA_WEB_CAPTURES=<scratch> npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStartThin1x=0.60,0.64,0.68 \
      --axis sizeScatterRampStartThick1x=0.50,0.52,0.56 \
      --axis sizeScatterRampReach1xPx=40,60,80,120 \
      --base g1-sweep-3-base.json --profile apple-macos-26.5-1x-light-standard --renderer webgpu

    # 1x refinement at the thin edge, 8 points (the grid's optimum sat on it)
    VITREA_WEB_CAPTURES=<scratch> npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStartThin1x=0.72,0.76 \
      --axis sizeScatterRampStartThick1x=0.52,0.54 \
      --axis sizeScatterRampReach1xPx=80,120 \
      --base g1-sweep-3-base.json --profile apple-macos-26.5-1x-light-standard --renderer webgpu

    # 2x, 4 points — a VERIFICATION of the clamp, not a fit
    VITREA_WEB_CAPTURES=<scratch> npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStartThin2x=0.46,0 \
      --axis sizeScatterRampStartThick2x=0.17,0 \
      --axis sizeScatterRampReach2xPx=100 \
      --base g1-sweep-3-base.json --profile apple-macos-26.5-2x-light-standard --renderer webgpu

    # the confirmation, once, per profile
    npx tsx cli/compare.ts --profile <key> --material-profile chosen-{light,dark}.json \
      --renderer webgpu --set calibration,validation,holdout --write-partial \
      --out-matrix matrix-confirm.json

The 2x four are the chosen anchors, a zeroed pair, and the two mixed pairs. If the clamp
holds, all four render identically; if any differs, the form is wrong about the clamp and
the round says so. All four are identical over 20 cells and 107 axes — §4 of
`g1-sweep-3.md`.

The 1x axes move only the 1x anchors and the 2x axes only the 2x anchors
(`scatterRampStart` returns each anchor exactly at dpr 1 and dpr 2), so each scale's run
is its own and neither disturbs the other. There is one profile *document* per scale in
the repository and `--profile` selects the fixture bed, which is why every run passes the
same `--base`.

**At 2x nothing is swept, because the form predicts there is nothing to sweep.** Every one
of G0's 2x start readings sits BELOW its cell's deep sharp share, so `max(0, s0 - sDeep)`
is zero on the whole bed and the wave's 2x stop is a **null**: every 2x row unchanged from
the branch's pre-ramp state, which is candidate A's device-pixel widths. That is a
prediction to verify by capture, not an exemption, so the 2x run is a verification of the
clamp rather than a fit.

`rrect-lg` is HOLDOUT at both scales and was not read until the single confirmation run.

## Files

- `confirm.tables.txt`, `confirm-report.py` — the confirmation run's rows, every profile
  and every fixture set, against the W12 close.
- `<name>.out` — the sweep's own table (its interior objective, the shadow objective, ΔE
  and whole-crop SSIM as checks), one per grid.
- `<name>.tables.txt` — the same points scored on the rows this wave turns on
  (`interiorStdDev` against native, `ssimBand` / `ssimInterior` / `ssimMean` /
  `ssimOutside` against the W12 close, the S1/S4 stops per point), produced by
  `report3.py`.
- `g1-sweep-3.md` — the reading: the 1x fit, the 2x null verified, the stops with numbers,
  the confirmation run.
- `paper3.py`, `paper3.txt` — the third form's closed-form projection on the real spans,
  per grid corner and at the chosen constants. No GPU. Written BEFORE the first capture,
  so the grid's inert region is a prediction the measurement then confirms.
- `g1-sweep-3-base.json` — the base profile document every point patched.
- `chosen-light.json`, `chosen-dark.json` — the profile documents at the chosen constants,
  used for the confirmation run. The dark one is a DIFFERENCE document and the committed
  dark profile does not name the ramp constants, so the six are added to the copy; that
  and the stripped fingerprint are the only differences from the committed document.
- `matrix-confirm.json` — the four confirmation runs (1x and 2x, light and dark) over
  `calibration,validation,holdout`, written into one matrix with `--write-partial`.
- `tab.py`, `report3.py` — the readers, copied beside the results they produced.
- The per-point matrices and profiles stay in scratch
  (`~/.claude/jobs/5c70e47f/tmp/w13/sweep-3/points-<name>/`) and are reproducible from the
  commands above.

## The reference point

Every table's `main` row is the **W12 close bed with the X6 band rows**,
`results/2026-09-03-w13-ramp/g0/matrix-x6-baseline.json`, not the canonical
`results/matrix.json`: the canonical matrix predates X6 and carries no `ssimBand`. Its
`ssimMean` and `interiorStdDev` agree with the canonical matrix cell for cell, which is
the check that the two beds are the same bed.

**One asymmetry to hold while reading the 2x deltas.** At 1x the branch equals `main`
exactly wherever the ramp is inert — the widths are device-pixel quantities and dpr 1
leaves them where they were — so a 1x delta IS the ramp. At 2x the branch already differs
from the W12 close before the ramp acts, because it carries candidate A's device-pixel
widths: that pedestal is `rrect-sm` +0.0246, capsule +0.0246, toolbar +0.0044, `rrect-md`
−0.0152, `rrect-ml` −0.0191 on `ssimBand` (`../sweep-2/g1-sweep-2.md` §5). Every 2x number
is the widths plus whatever the ramp added, and this round's finding is that the ramp adds
exactly nothing.
