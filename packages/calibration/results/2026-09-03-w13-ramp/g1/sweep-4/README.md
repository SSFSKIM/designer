# The W13 G1 runtime sweep, fourth round — the far start on the W14 bed (2026-09-03)

The first three rounds are `../sweep/`, `../sweep-2/` and `../sweep-3/` (claims §5.63, §5.64,
§5.67). This round fits the fourth form's one new constant, re-verifies the 2x null under it,
and takes the single confirmation on the **W14 bed** — the re-run X8 requires of the second
wave to land. `g1-sweep-4.md` is the reading.

## Where it ran

Branch `w13-g1-ramp` at `7de3d76` for the sweeps; the fitted far start landed after them in `762c290` and `51c232d` (branch HEAD `51c232d`) (main merged in at `c97d343` with W14 landed; the fourth form
and the five review findings in `7de3d76`), worktree `.claude/worktrees/w13-g1`, rebuilt with
`pnpm -r build` before the first point so the captures carry the fourth form's shader and W14's
landed shadow. Every capture and per-point matrix went to scratch
(`VITREA_WEB_CAPTURES=$T/web-captures-<name>`, `sweep-work/` inside the worktree, copied to
`$T/points-<name>/` after each run, `T=~/.claude/jobs/5c70e47f/tmp/w13/sweep-4`); the main
checkout's `results/matrix.json` and `web-captures/` were read and never written.

**The shared GPU** takes one capture at a time. `pgrep -f 'compare.ts|sweep.ts'` and
`lsof -i :5189` were clear before every round; custody, KST, 2026-09-03/04:

    GPU taken 23:18:29 KST for the 1x startFar sweep (pgrep/lsof clear)
    1x sweep done 23:20:18 KST
    GPU taken 23:21:47 KST for the 1x far refinement (pgrep/lsof clear)
    1x refinement done 23:22:53 KST
    GPU taken 23:23:47 KST for the 2x null check (pgrep/lsof clear)
    2x null done 23:25:42 KST
    GPU taken 23:26:05 KST for the confirmation (pgrep/lsof clear)
    confirmation done, GPU released 23:28:07 KST


## The reference bed

Every table's `main(W14 bed)` row is the canonical `results/matrix.json` at `8eebae4` (copied to
`$T/matrix-w14-bed.json`), which carries X6's band rows. This is the first W13 round read
against it rather than the W12 close; the W14 landing reproduced the W12 rows it did not
touch to five decimals, so the inside-the-contour rows are the same numbers.

## The base and the chosen documents

`g1-sweep-4-base.json` is the branch's light profile document at `7de3d76` reduced to its
`profileKey`, `schemaVersion`, `$comment`, `patch` and `cssTierMapping` sections — the fingerprint
and the entries stripped, as in every earlier round — and it carries W14's landed shadow
constants, so every point renders the landed shadow. `chosen-light.json` / `chosen-dark.json`
(`make-chosen.py 0.20`) are the two documents with the chosen eight ramp constants applied and
the fingerprint stripped; the dark one is a difference document and gains the eight explicitly.

## The commands

    # 1x, 5 points, then the refinement downward, 3 points
    VITREA_WEB_CAPTURES=$T/web-captures-1x-far npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStartFar1x=0.30,0.35,0.40,0.45,0.52 \
      --base $T/g1-sweep-4-base.json --profile apple-macos-26.5-1x-light-standard --renderer webgpu
    VITREA_WEB_CAPTURES=$T/web-captures-1x-far-refine npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStartFar1x=0.15,0.20,0.25 \
      --base $T/g1-sweep-4-base.json --profile apple-macos-26.5-1x-light-standard --renderer webgpu

    # 2x, 4 points — a VERIFICATION of the null, not a fit
    VITREA_WEB_CAPTURES=$T/web-captures-2x-null npx tsx scripts/sweep.ts \
      --axis sizeScatterRampStartThin2x=0.46,0 --axis sizeScatterRampStartFar2x=0.15,0 \
      --base $T/g1-sweep-4-base.json --profile apple-macos-26.5-2x-light-standard --renderer webgpu

    # the confirmation, once, four profiles into one matrix (run-confirm.sh)
    VITREA_WEB_CAPTURES=$T/web-captures-confirm npx tsx cli/compare.ts --profile <key> \
      --material-profile chosen-{light,dark}.json --renderer webgpu \
      --set calibration,validation,holdout --write-partial --out-matrix $T/matrix-confirm.json

`rrect-lg` and `glass-over-glass` are HOLDOUT and were not read until the confirmation.

## Files

- `paper4.py`, `paper4.txt`, `paper4-chosen.txt` — the closed-form projection on the real
  spans, per far value, written before the first capture.
- `<name>.out` — the sweep's own table; `<name>.tables.txt` — the same points on the rows this
  wave turns on, against the W14 bed (`report4.py`, sweep-3's reader re-pointed; `tab.py`).
- `2x-null.identity.txt` — `null-check.py` over the four 2x points: the maximum difference over
  every measurement of every cell.
- `confirm.tables.txt` — the confirmation's rows against the W14 bed (`confirm-report.py`);
  `matrix-confirm.json` — the four runs in one matrix.
- `g1-sweep-4.md` — the reading.
