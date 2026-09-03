# The W14 G1 runtime sweep — fitting the outer shadow's composite (2026-09-03)

The charter's G1 purpose executed on the amplitude law: `packages/calibration/scripts/sweep.ts`
turning the two-term composite's constants (claims §5.62 §4–§5, `MaterialOuterShadow` on
`w14-g1-shadow`) through the real renderer on the calibration cells, at both scales, in both
colour schemes and on both tiers, and read on the X7 affine pair rather than on the sweep's
own objective.

## Where it ran

Branch `w14-g1-shadow`, worktree `.claude/worktrees/w14-g1`, rebuilt with `pnpm -r build`
before the first point of the final pass so the captures carry the branch's shader and the
review fix-wave's commits. Every capture and every per-point matrix went to scratch
(`VITREA_WEB_CAPTURES=$TMP/w14/sweep/caps/<round>`, `sweep-work/` inside the worktree, copied
to `$TMP/w14/sweep/points/<round>/`); the main checkout's `results/matrix.json` and
`web-captures/` were read and never written.

**A first pass (rounds `r1`–`r15`) was discarded.** It ran while the review's fix-wave worker
was editing `material.ts`, `optics.ts`, `css-tier.ts` and the two profile documents in the same
worktree; one point failed with `rejectRetiredOuterShadowLeaves is not defined`, which is the
proof that the captures were reading a half-edited tree. Every number in `g1-sweep.md` comes
from the second pass (`f1`–`f17`), taken after the fix commit `99ea455` landed and the worktree
was rebuilt. The light-standard points of the two passes agree to the last printed digit, which
is the check that the fix wave did not move that profile's rendering; the discarded pass is
discarded anyway, because that check cannot be run for the dark and CSS points.

## The base

`g1-sweep-base.json` is the branch's light profile document
(`profiles/apple-macos-26.5-1x-light-standard.json`) reduced to its `patch` and
`cssTierMapping` sections, with the fingerprint (`resolvedMaterialSha256`), the provenance
comments and the `entries` stripped — exactly as W13 G1's `g1-sweep-base.json` was, and for
the same reason: the sweep re-derives the material at every point, so a fingerprint in the
base would be a stale assertion. `g1-sweep-base-dark.json` is the same reduction of the dark
document, which is a **difference** document over `DEFAULT_MATERIAL_PROFILE` and therefore
stands alone.

Two derived bases hold a fitted constant while another turns: `…-A010.json` is the light base
with `outerShadow.liftAmplitude` at the fitted 0.0100, and `…-dark-A0051.json` the dark base
with the lift's four constants written in (the committed dark document names only the
amplitude anchors, so a dark point would otherwise have taken the light default).

## What the sweep is ranked on, and what it is read on

`sweep.ts`'s built-in shadow objective is the mean of |Δ `meanDeparture`| over the whole
exterior. That is one number for a facet this wave splits into two terms, and it cannot see
the lift at all on a cell where the black term dominates the mean. Every table in
`g1-sweep.md` is therefore read out of the **point matrices** with `read.py` and `an.py`
beside this file (thirty lines over the schema, no state; `compare_bed.py` is the same for the
confirmation matrix against the W12 close bed), on the X7 pair:
per cell, `affineNative` / `affineWeb` at direction `below`, bands `3-6` and `6-12` —
`slopeALinear` (so 1 − a is the occlusion) and `interceptCLinear` (c, the lift, linear
luminance) — with `renderedLevelLinear` against `backdropMeanLinear` on the solids, and the
perceptual rows against the W12 close bed. The `0-3` band is read only to note it: it holds
the body's own edge (claims §5.62 §8).

The reference bed for every "(Δ)" in `g1-sweep.md` is the **X7 baseline on the W12 close
bed**, `$TMP/w14/x7/matrix-x7-baseline.json` (`results/2026-09-03-w14-shadow/g0/x7-baseline.md`
§1–§7) — the canonical `results/matrix.json` carries no affine pair, and this is the only bed
that has both the pair and the band-windowed SSIM rows for every cell.

## The axes

The constants act on separate regimes, so they were swept one or two at a time on the cells
that govern them, with `--scene` restricting each point to those cells. A point costs 5–8 s
that way, which is why the grids are as wide as they are.

    # f1 — the thin regime's mid plateau, four thin/mid cells
    VITREA_WEB_CAPTURES=<scratch> npx tsx scripts/sweep.ts --objective shadow \
      --axis outerShadow.thinOcclusionMid=0.30,0.33,0.36 \
      --scene checkerboard__rrect-sm__rest,checkerboard__capsule-button__rest,photo__capsule-button__rest,dark-solid__capsule-button__rest \
      --base g1-sweep-base.json --profile apple-macos-26.5-1x-light-standard --renderer webgpu

    # f2 — the thin regime's bright anchor, the one cell that carries it
    ... --axis outerShadow.thinOcclusionBright=0.10,0.127,0.15 \
        --scene light-solid__capsule-button__rest ...

    # f3 — span 96: the black anchor against the lift, 5 × 4
    ... --axis outerShadow.thickOcclusionAt96=0.319,0.349,0.379,0.409,0.439 \
        --axis outerShadow.liftAmplitude=0.005,0.0073,0.010,0.013 \
        --scene checkerboard__rrect-md__rest ...

    # f4 — span 128, the same pair, 5 × 4
    ... --axis outerShadow.thickOcclusionAt128=0.437,0.467,0.497,0.527,0.557 \
        --axis outerShadow.liftAmplitude=0.005,0.0073,0.010,0.013 \
        --scene checkerboard__rrect-ml__rest ...

    # f5 — the lift's span reach, both thick calibration spans
    ... --axis outerShadow.liftSpanFull=104,112,118,128,144 \
        --scene checkerboard__rrect-md__rest,checkerboard__rrect-ml__rest --base …-A010.json ...

    # f6 / f7 — the refinement grids at the fitted amplitude
    ... --axis outerShadow.liftSpanFull=112,118,124 --axis outerShadow.thickOcclusionAt96=0.360,0.370,0.380 ...
    ... --axis outerShadow.thickOcclusionAt128=0.437,0.447,0.457 ...

    # f8 / f9 — the same two refinements at 2x (--profile apple-macos-26.5-2x-light-standard)
    # f10 / f11 — f1 and f2 again with --renderer css
    # f12 / f13 / f14 — the dark bed: the lift's amplitude, then the thick anchor beside it,
    #                   then the thin plateau (--profile apple-macos-26.5-1x-dark-standard,
    #                   --base g1-sweep-base-dark.json)
    # f15 — the dark thick anchor at 2x
    # f16 / f17 — the dark thin plateau over three backdrops, GPU and CSS

`f16` and `f17` ran after the confirmation block's own GPU grab, because two earlier attempts
died on `capture-web.ts: Error: Port 5189 is already in use` — a vite server from the other
worker's run outliving it on the harness's fixed port. `pgrep -f 'compare.ts|sweep.ts'` does
not see that; `lsof -i :5189` does, and the grab script this pass used checks both.

The axes the brief named and this sweep does **not** carry:

- `outerShadow.reducedTransparencyOcclusion` was dropped at the coordinator's instruction
  mid-run: the review's fix wave re-forms it from a 0.7 multiplier on six anchors into one
  absolute flat amplitude, which is what claims §5.62 §5 measured. The accessibility profiles
  are read in the confirmation run only.
- `outerShadow.thickOcclusionAt160` has **no calibration cell**. Every span above 128 in the
  bed — `checkerboard__rrect-lg` (160), `checkerboard__glass-over-glass` (130),
  `photo__rrect-lg` (160) — is holdout, and `sweep.ts` cannot select holdout by construction.
  `g1-sweep.md` §4 says what was carried instead and why.

## Files

- `f<n>-<round>.out` — the sweep's own table per round (its two objectives, ΔE and whole-crop SSIM
  as checks). The per-point matrices and profile documents stay in scratch
  (`$TMP/w14/sweep/points/<round>/`, ~0.2–1.6 MB each) and are reproducible from the commands
  above; only the chosen documents are committed.
- `g1-sweep.md` — the tables this wave scores on, the chosen constants with their reasoning,
  the two rankings where they disagree, the confirmation, and what it asks of the declaration.
- `chosen-light.json`, `chosen-dark.json` — the profile documents at the chosen constants,
  fingerprints stripped for the same reason the bases are.
- `matrix-confirm.json` — the nine confirmation runs written into one matrix with
  `--write-partial`; `confirm-<tag>.out` is each run's own console output.

## The confirmation run

    npx tsx cli/compare.ts --profile <key> --material-profile <chosen-light|chosen-dark>.json \
      --renderer <webgpu|css> --set calibration,validation,holdout --write-partial \
      --out-matrix matrix-confirm.json

nine times: GPU at `apple-macos-26.5-{1x,2x}-light-standard`,
`apple-macos-26.5-{1x,2x}-dark-standard`, `apple-macos-26.5-1x-light-reduced-transparency` and
`apple-macos-26.5-1x-light-increased-contrast`; CSS at `{1x,2x}-light-standard` and
`1x-dark-standard`. The accessibility beds take the light document, which is what they have
always taken — there is no accessibility profile *document* in `profiles/`, only accessibility
fixture beds, and `compare` supplies the browser-side `--accessibility` overrides itself from
the profile key. **Holdout was read once, here, and nothing was fitted after reading it.**

## The GPU

`pgrep -f 'compare.ts|sweep.ts'` was clear before every round and the rounds ran back to back
as one block. The sweep held it 20:47:40–20:52:50 and released
it; the W13 ramp's re-sweep took it at 20:52:55 and held it to 21:21; the confirmation block
ran 21:24:03–21:28:44 and the GPU was **released at 21:28:44**. `g1-sweep.md` §11 carries the
same note.
