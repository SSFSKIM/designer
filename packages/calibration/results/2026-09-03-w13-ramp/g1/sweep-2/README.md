# The W13 G1 runtime sweep, second round — the re-formed depth ramp (2026-09-03)

The first round swept the ramp as it was first implemented: a start and a reach per
scale, replacing W11c's span-graded scatter share. It could not reach the wave's stops at
any of 81 points and named the mechanism rather than a bad neighbourhood (`../sweep/`,
§4 and §7). This round sweeps the form §7 asked for — the span law kept UNDERNEATH the
ramp as its deep value, the ramp a near-contour excursion above it.

## The form under the sweep

With `u` the depth inside the contour in DEVICE px:

    kDeep(span) = sizeScatterFloor + (1 - sizeScatterFloor)
                  * smoothstep(sizeSpanMin, sizeScatterSpanMax, span)      [W11c, restored]
    s(u, span)  = (1 - kDeep) + max(0, s0(dpr) - (1 - kDeep)) * max(0, 1 - u / U(dpr))
    kScatter(u) = clamp(sizeScatterFloor + ((1 - s) - sizeScatterFloor) * fold, 0, 1)

`s0` is `sizeScatterRampStart1x` / `2x`, `U` is `sizeScatterRampReach1xPx` / `2xPx` in
device px, and `U` is now where the excursion vanishes into the deep value rather than
where a line from the start would hit zero. `sizeScatterSpanMax` 256 is back in the
profile, the material, the uniforms and `capture-web.ts`'s `MATERIAL_PATCH_KEYS`;
`sizeScatterFloor` 0.4 stays.

## Where it ran

Branch `w13-g1-ramp` (`2752301`, main merged in at `a686662`), worktree
`.claude/worktrees/w13-g1`, rebuilt with `pnpm -r build` before the first point so the
captures carry the re-formed shader. Every capture and every per-point matrix was written
to scratch (`VITREA_WEB_CAPTURES=$TMP/web-captures-<name>`, `sweep-work/` inside the
worktree); the main checkout's `results/matrix.json` and `web-captures/` were read and
never written. The GPU is shared and takes one capture at a time: every round waited on
`pgrep -f 'compare.ts|sweep.ts'` showing nothing but its own processes.

## The base

`g1-sweep-2-base.json` is the branch's light profile document
(`profiles/apple-macos-26.5-1x-light-standard.json`) reduced to its `patch` and
`cssTierMapping` sections — the fingerprint (`resolvedMaterialSha256`), the provenance
comments and the entries stripped, exactly as `g1-sweep-base.json` was for the first
round. The sweep re-derives the material per point, so a fingerprint in the base would be
a stale assertion.

## The axes

The wave's declared grid was start {0.55, 0.65, 0.75, 0.85} x reach {100, 150, 200, 300}
at 1x and start {0.25, 0.35, 0.45, 0.55} x reach {100, 200, 300} at 2x. Both were EXTENDED
before the first point, on a reading of the form's own projection that the declared grid
would have spent its whole budget outside the region the form lives in. The declared
points are all kept as a subset; §2 of `g1-sweep-2.md` states the reading and the extension.

    # 1x, 32 points
    VITREA_WEB_CAPTURES=<scratch> npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStart1x=0.55,0.65,0.75,0.85 \
      --axis sizeScatterRampReach1xPx=20,30,50,80,100,150,200,300 \
      --base g1-sweep-2-base.json --profile apple-macos-26.5-1x-light-standard --renderer webgpu

    # 2x, 36 points
    VITREA_WEB_CAPTURES=<scratch> npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStart2x=0.25,0.35,0.45,0.55,0.65,0.75 \
      --axis sizeScatterRampReach2xPx=20,40,60,100,200,300 \
      --base g1-sweep-2-base.json --profile apple-macos-26.5-2x-light-standard --renderer webgpu

    # 1x refinement, 6 points (the two thresholds of section 3, measured rather than
    # interpolated from the grid)
    VITREA_WEB_CAPTURES=<scratch> npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStart1x=0.575,0.61 \
      --axis sizeScatterRampReach1xPx=50,80,100 \
      --base g1-sweep-2-base.json --profile apple-macos-26.5-1x-light-standard --renderer webgpu

Two of the 32 1x grid points — start 0.55 at reaches 150 and 300 — failed on a port
collision (`capture-web.ts: Error: Port 5189 is already in use`, then an exit 137) and the
sweep skipped them rather than scoring partial runs, so the 1x grid is 30 points. Both sit
at the start where the ramp is already inert on three of the five calibration cells at
every reach, so no reading in this document rests on them; they were not re-run, because
the shared GPU was owed back to the W14 shadow sweep.

The 1x axis pair moves only the 1x anchors and the 2x pair only the 2x anchors
(`scatterRampStart` / `scatterRampReachDevicePx` return the anchor exactly at dpr 1 and
dpr 2), so each grid is that scale's own fit and neither disturbs the other. There is one
profile *document* per scale in the repository and the `--profile` key selects the fixture
bed, which is why both grids pass the same `--base`.

## Files

- `<name>.out` — the sweep's own table (its interior objective, the shadow objective, dE
  and whole-crop SSIM as checks), one per grid: `1x-grid`, `2x-grid`, `1x-refine`.
- `<name>.tables.txt` — the same points scored on the rows this wave turns on
  (`interiorStdDev` against native, `ssimBand` / `ssimInterior` / `ssimMean` against the
  W12 close, the S1/S4 stops per point), produced by `report2.py`.
- `g1-sweep-2.md` — the reading: the span the law really takes, the two structural
  thresholds, the 1x and 2x verdicts, and the paper section on the third form.
- `paper.py`, `paper.txt`, `paper-fit.txt` — the paper section's computation and its
  output: the projection table on the real spans, the excursion G0 implies per cell and
  scale, the third form at its G0-pinned constants, and the fit of a 2x deep curve to
  G0's contour readings. No GPU.
- `g1-sweep-2-base.json` — the base profile document every point patched.
- `tab.py`, `report2.py`, `run-sweep.sh` — the readers and the driver, copied beside the
  results they produced (the first round's, re-pointed).
- The per-point matrices and profiles stay in scratch
  (`~/.claude/jobs/5c70e47f/tmp/w13/sweep-2/points-<name>/`) and are reproducible from
  the commands above.

**There is no confirmation run and no `matrix-confirm.json`.** The form cannot meet S4 at
1x by construction (§3) and cannot raise any 2x band row at all (§5), so reading holdout
for it would have spent the once-per-frozen-configuration read on a configuration that
will not land. Holdout was not read. `rrect-lg` and `glass-over-glass` appear in this
document only where the paper section computes their projection, which reads no fixture.

## The reference point

Every table's `main` row is the **W12 close bed with the X6 band rows**,
`results/2026-09-03-w13-ramp/g0/matrix-x6-baseline.json`, not the canonical
`results/matrix.json`: the canonical matrix predates X6 and carries no `ssimBand`. Its
`ssimMean` and `interiorStdDev` agree with the canonical matrix cell for cell, which is
the check that the two beds are the same bed.
