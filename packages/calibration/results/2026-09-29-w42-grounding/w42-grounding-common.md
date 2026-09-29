# W42 grounding — common rules (read first)

vitrea is a TypeScript runtime replicating Apple's macOS Liquid Glass on the web, calibrated
against Apple's own pixels. W41 (charter `docs/doperpowers/specs/2026-09-27-w41-archive-reread.md`,
ledger `docs/doperpowers/specs/c9a-fidelity-claims.md` §5.191–§5.193) identified **E3**, a body law
for the LIGHT scheme with the window UNFOCUSED ("receded", "inactive"):
y = F(L)·1 + g(L)·v, on encoded luma L, where F is a curve of seven neutral ordinates and g is a
piecewise-linear chroma gain with knots at 63/93/118. E3 closes at one code on uniform backdrops,
held-out cells included. It did not ship. On the canonical bed, applied per pixel to vitrea's
blurred backdrop, it read 210 codes on the light-inactive checkerboard body, where Apple and the
old group-level solve read 188. It failed L1 on every inactive checkerboard cell and amplified
texture on photo, hc-text and impulse. Apple's receded body over black-and-white structure is a
near-uniform grey. One arithmetic pointer, not a finding: native 189 ≈ F(128), the ENCODED mean of
black and white, while E3's 212 is F at the linear-light mean. hc-text does not fit that pointer.

The user chartered W42 on the unfocused body's blur. The first step is an offline read of
existing evidence, meaning your memo. A native capture with a structured holdout comes after it.
You write a grounding MEMO that the parent charters from. You do not write the charter, you do not
fit anything to closure, and you commit nothing.

## Evidence you may read
- Canonical native fixtures under `apps/reference-apple/fixtures/`, CALIBRATION and VALIDATION cells
  only. `apps/reference-apple/scenes.json` holds the split. **Never open a holdout cell's native
  pixels, and never open a `recorded` row's.** The canonical holdout is the referee for any future
  landing.
- vitrea's web captures:
  - pre-W41, the shipped material: the canonical tree `packages/calibration/web-captures/` on this
    machine;
  - E3 per pixel: G2's stage captures at `/Users/new/vitrea-w41/g2-captures/canonical-stage/`, plus
    G1's diagnostic canonical captures, which G1's evidence README locates.
- W41's evidence directories:
  - `packages/calibration/results/2026-09-27-w41-g1-identification/`: E3's coefficients in the
    candidate, the body readings, and spatial/ with S0–S2 on the gradient strips;
  - `packages/calibration/results/2026-09-29-w41-g2-landing/`: `stop/`, `referees/stop-reading/`,
    the sheets.
- The W39 archive, through its guarded Reader, as W41 G1 did. Its holdout is spent, so it may be
  read, but label anything from it as such.
- The shipped material: `packages/renderer-webgpu/src/material.ts` and `src/wgsl/` (blur, analysis
  pass, tone solve, scatter laws), and `packages/platform-web/src/optics.ts` and `css-tier.ts`.

Never run anything against `packages/calibration/results/matrix.json` or `results/generations/` except
read-only loads through `src/matrix-store.ts` or W40's Python adapter. `python3.12` has numpy and
PIL. Keep scratch under your memo's directory in `~/vitrea-w42/grounding/`.

## Reading discipline
These rules come from past waves' mistakes; apply them.
- A reader with a parametric kernel is not a measurement until it recovers a KNOWN kernel on a
  control, on at least two backdrops. Prove your reader on vitrea's own captures first, where the
  kernel is known from the code, before you read Apple's.
- A width read at one pitch is not a kernel. Read the same kind of cell at several spatial
  frequencies before you compare widths.
- A band statistic over a thin feature measures the mixture. Read features at their own scale.
- A raw mean over a structured backdrop shows the backdrop's layout. Separate the surface's own
  light from its transmission of the backdrop before you call something a blur.
- Censored channels (0 or 255) constrain only one side. Keep them one-sided.

## What a memo is
- Readings with their numbers: cell, scale, channel, region, value and the repeat bar.
- The structure you see.
- The candidate families you propose, with parameter counts and working spaces.
- What discriminates the families on the cells that exist, and what the existing evidence cannot
  identify.
- The shipped operators involved, and what the CSS tier could carry.
Exploratory fits are allowed as READINGS that size an effect; say so and give the residual. Never
present one as a proposed coefficient set. One code is the resolution. Write the memo to the path
in your brief: under about 250 lines, tables over prose. Hand back its path and a ten-line summary.
No commits, no pushes, no edits under the repository. Any sub-worker you spawn runs on the default
opus model.
