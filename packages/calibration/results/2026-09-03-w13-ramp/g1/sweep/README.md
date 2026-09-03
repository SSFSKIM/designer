# The W13 G1 runtime sweep — fitting the depth ramp's four constants (2026-09-03)

The binding rule "a measured ramp, then a form; **the runtime is the fitting instrument**"
(W13 Design) executed: `packages/calibration/scripts/sweep.ts` turning the four PROVISIONAL
ramp constants through the real GPU renderer on the calibration cells, at both scales.

## Where it ran

Branch `w13-g1-ramp` (`eb12219`), worktree `.claude/worktrees/w13-g1`, built with
`pnpm -r build` before the first point so the captures carry the branch's renderer.
Every capture and every per-point matrix was written to scratch
(`VITREA_WEB_CAPTURES=$TMP/web-captures-<name>`, `sweep-work/` inside the worktree); the
main checkout's `results/matrix.json` and `web-captures/` were read and never written.

## The base

`g1-sweep-base.json` is the branch's light profile document
(`profiles/apple-macos-26.5-1x-light-standard.json`) reduced to its `patch` and
`cssTierMapping` sections — the fingerprint (`resolvedMaterialSha256`), the provenance
comments and the entries stripped, exactly as `g3-sweep-base.json` was for W12 G3
(`results/2026-09-03-w12-lens/g3/referee/sweep/README.md`). The sweep re-derives the
material per point, so a fingerprint in the base would be a stale assertion.

## The axes

Two-dimensional grids rather than coordinate descent, because a point costs ~22 s at 1x
and ~35 s at 2x and the full product is affordable: the start and the reach trade off
against each other (a longer reach at a fixed start is a flatter ramp), and a
coordinate-descent path through that valley reports one section of a surface as if it
were the surface. The coordinate-descent reading is recoverable from the grid by
holding a column, and is reported beside it in `g1-sweep.md`.

    # 1x, 30 points
    VITREA_WEB_CAPTURES=<scratch> npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStart1x=0.40,0.50,0.60,0.70,0.80 \
      --axis sizeScatterRampReach1xPx=60,80,110,150,200,300 \
      --base g1-sweep-base.json --profile apple-macos-26.5-1x-light-standard --renderer webgpu

    # 1x flat limit, 12 points (the 1x optimum ran to the grid's long-reach edge)
    VITREA_WEB_CAPTURES=<scratch> npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStart1x=0.50,0.60,0.65,0.70 \
      --axis sizeScatterRampReach1xPx=300,450,600 \
      --base g1-sweep-base.json --profile apple-macos-26.5-1x-light-standard --renderer webgpu

    # 1x S1 frontier, 4 points (the start between the two that clear S1)
    VITREA_WEB_CAPTURES=<scratch> npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStart1x=0.55 \
      --axis sizeScatterRampReach1xPx=200,300,450,600 \
      --base g1-sweep-base.json --profile apple-macos-26.5-1x-light-standard --renderer webgpu

    # 2x flat limit, 9 points (the 2x optimum ran to the grid's high-start edge)
    VITREA_WEB_CAPTURES=<scratch> npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStart2x=0.55,0.65,0.75 \
      --axis sizeScatterRampReach2xPx=200,350,500 \
      --base g1-sweep-base.json --profile apple-macos-26.5-2x-light-standard --renderer webgpu

    # 2x, 30 points
    VITREA_WEB_CAPTURES=<scratch> npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStart2x=0.15,0.25,0.35,0.45,0.55 \
      --axis sizeScatterRampReach2xPx=40,60,80,100,140,200 \
      --base g1-sweep-base.json --profile apple-macos-26.5-2x-light-standard --renderer webgpu

The 1x axis pair moves only the 1x anchors and the 2x pair only the 2x anchors
(`scatterRampStart` / `scatterRampReachDevicePx` return the anchor exactly at dpr 1 and
dpr 2), so each grid is that scale's own fit and neither disturbs the other. There is
one profile *document* per scale in the repository and the `--profile` key selects the
fixture bed, which is why both grids pass the same `--base`.

## Files

- `<name>.out` — the sweep's own table (its interior objective, the shadow objective,
  ΔE and whole-crop SSIM as checks), one per grid: `1x-startA` (the charter's first
  coordinate-descent step, the start at the provisional reach 110), `1x-grid`, `1x-flat`,
  `1x-frontier`, `2x-grid`, `2x-flat`. 81 distinct points.
- `g1-sweep.md` — the tables this wave scores on (`interiorStdDev` against native,
  `ssimBand` / `ssimInterior` / `ssimMean` against the W12 close, the S1/S3/S4 stops
  per point), the two rankings, and the recommendation.
- `chosen-1x.json`, `chosen-2x.json` — the profile documents at the chosen constants.
- `matrix-confirm.json` — the four confirmation runs (1x and 2x, light and dark) over
  `calibration,validation,holdout`, written into one matrix with `--write-partial`.
- The 81 per-point matrices and profiles stay in scratch
  (`~/.claude/jobs/5c70e47f/tmp/w13/sweep/points-<name>/`) — ~1.6 MB each and
  reproducible from the commands above; only the chosen points are committed.

## The reference point

Every table's `main` row is the **W12 close bed with the X6 band rows**,
`results/2026-09-03-w13-ramp/g0/matrix-x6-baseline.json`, not the canonical
`results/matrix.json`: the canonical matrix predates X6 and carries no `ssimBand`.
Its `ssimMean` and `interiorStdDev` agree with the canonical matrix cell for cell,
which is the check that the two beds are the same bed.
