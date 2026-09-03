# The G3 runtime sweep (2026-09-03)

`scripts/sweep.ts` run from the `w12-g3-candidate-a` worktree (the candidate's device-pixel
body widths built in), sweeping the one new constant through the real renderer:

    VITREA_WEB_CAPTURES=<scratch> npx tsx scripts/sweep.ts \
      --axis sizeScatterScaleTerm=0,0.05,0.1,0.15,0.2,0.35 \
      --base g3-sweep-base.json --profile apple-macos-26.5-2x-light-standard --renderer webgpu

`g3-sweep-base.json` is the candidate branch's light profile document with its fingerprint
stripped (the sweep re-derives the material per point). `profile-N.json` / `matrix-N.json` are
the six points in the axis order above; `g3-sweep.out` is the sweep's own table. Claims §5.58.
