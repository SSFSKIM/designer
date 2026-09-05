# W19 probe bed — Apple's author-tint strength curve, read (2026-09-05)

The bed the charter's X10 custody rule governs: `apps/reference-apple/scenes-w19-probe.json` captured
on this machine at 1x by W9's protocol (claims §5.30 — a 6 s bare neutral reset before each cell, the
one stable order, the run refused unless the machine had been idle 45 s), ten runs taken, eight
attested, seven materialised by the majority byte-state per cell (`cli/materialize.ts
--frequency-settle`; `provenance.json`, `manifest.json`, `last-run-manifest.json`). Nothing here is
fitted to anything; the readings are §5 of `g0/g0-findings.md`.

## The runs

| run | idle at start / end (s) | audit | kept |
| --- | --- | --- | --- |
| w19-probe-1 | 2 671 / **7** | 8/12 | **no** — HID activity during the run; four checkerboard cells `presentedActive: false` |
| w19-probe-2 | 96 / 218 | 12/12 | yes |
| w19-probe-3 | 219 / 338 | 12/12 | yes |
| w19-probe-4 | 339 / 459 | 12/12 | yes |
| w19-probe-5 | 459 / 578 | 12/12 | yes |
| w19-probe-6 | 578 / 699 | 12/12 | yes |
| w19-probe-7 | 700 / 818 | 6/12 | **no** — six cells `presentedActive: false` with the machine idle throughout; the session denied the window activation |
| w19-probe-8 | 819 / 938 | 12/12 | yes |
| w19-probe-9 | 970 / 1 089 | 12/12 | yes (the replacement) |
| w19-probe-10 | 1 089 / 1 209 | 12/12 | attested, not needed — seven runs were taken before it |

Nine cells unanimous over the seven kept runs; three frequency-settled at a 6/7 majority
(`photo__capsule-button__rest-tint-orange-020`, `…-035` and `…-075`, one minority state each).
Materialise's own provenance block (`manifest.json` → `bedProvenance`): seven runs, 72.2 % confidence
at a one-in-six minority.

**The three recorded twins are byte-identical to the canonical fixtures captured 2026-08-31**
(`photo__capsule-button__rest-tint-orange`, `photo__capsule-button__rest-tint-orange-half`,
`checkerboard__capsule-button__rest-tint-orange`: sha256 equal, 0 px changed). The native capture path
reproduces to the byte across five days.

## The readings

Interior mean of linear luminance under the native silhouette, from `compare` on both web tiers
against this bed (scratch matrix; the captures under scratch). Standard light profile, 1x.

| cell | `s` | native | GPU | CSS | GPU − native | CSS − native | CSS − GPU |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `photo…orange-010` | 0.10 | 0.5511 | 0.5807 | 0.5122 | +0.0295 | −0.0389 | −0.0684 |
| `photo…orange-020` | 0.20 | 0.5191 | 0.5463 | 0.5055 | +0.0272 | −0.0135 | −0.0408 |
| `photo…orange-035` | 0.35 | 0.4783 | 0.4996 | 0.4875 | +0.0214 | +0.0092 | −0.0121 |
| `photo…orange-half` | 0.50 | 0.4385 | 0.4587 | 0.4579 | +0.0201 | +0.0193 | −0.0008 |
| `photo…orange-075` | 0.75 | 0.3908 | 0.4025 | 0.4052 | +0.0116 | +0.0143 | +0.0027 |
| `photo…orange` | 1.00 | 0.3524 | 0.3595 | 0.3594 | +0.0071 | +0.0071 | −0.0001 |
| `checkerboard…orange-010` | 0.10 | 0.5852 | 0.6347 | 0.6021 | +0.0495 | +0.0170 | −0.0325 |
| `checkerboard…orange-020` | 0.20 | 0.5481 | 0.5940 | 0.5824 | +0.0459 | +0.0343 | −0.0117 |
| `checkerboard…orange-035` | 0.35 | 0.5020 | 0.5386 | 0.5394 | +0.0366 | +0.0374 | +0.0008 |
| `checkerboard…orange-half` | 0.50 | 0.4578 | 0.4900 | 0.4919 | +0.0322 | +0.0341 | +0.0020 |
| `checkerboard…orange-075` | 0.75 | 0.4040 | 0.4232 | 0.4224 | +0.0193 | +0.0185 | −0.0008 |
| `checkerboard…orange` | 1.00 | 0.3603 | 0.3719 | 0.3703 | +0.0116 | +0.0100 | −0.0016 |

The interpolation test, per pixel and per channel, with Apple's own captures as both endpoints — the
untinted capsule from the canonical bed and the full-strength capsule from this bed
(`g0/native-ladder.ts`, `g0/parts/native-ladder.json`):

| cell | `s` | native | `D((1−s)·E(untinted) + s·E(s=1))` | residual | linear-light mix | residual |
| --- | --- | --- | --- | --- | --- | --- |
| `photo…orange-010` | 0.10 | 0.5511 | 0.5499 | −0.0012 | 0.5601 | +0.0089 |
| `photo…orange-020` | 0.20 | 0.5191 | 0.5184 | −0.0007 | 0.5371 | +0.0180 |
| `photo…orange-035` | 0.35 | 0.4783 | 0.4765 | −0.0017 | 0.5025 | +0.0242 |
| `photo…orange-half` | 0.50 | 0.4385 | 0.4406 | +0.0021 | 0.4679 | +0.0293 |
| `photo…orange-075` | 0.75 | 0.3908 | 0.3904 | −0.0005 | 0.4102 | +0.0194 |
| `checkerboard…orange-010` | 0.10 | 0.5852 | 0.5834 | −0.0017 | 0.5949 | +0.0097 |
| `checkerboard…orange-020` | 0.20 | 0.5481 | 0.5477 | −0.0004 | 0.5685 | +0.0204 |
| `checkerboard…orange-035` | 0.35 | 0.5020 | 0.5010 | −0.0010 | 0.5297 | +0.0277 |
| `checkerboard…orange-half` | 0.50 | 0.4578 | 0.4610 | +0.0032 | 0.4909 | +0.0331 |
| `checkerboard…orange-075` | 0.75 | 0.4040 | 0.4033 | −0.0007 | 0.4254 | +0.0215 |

## What the pixels say

1. **The renderer's law has Apple's shape.** `tintedMaterialColour` mixes the material and the author
   layer in ENCODED space (claims §5.36 finding 3, chosen from a single half-strength cell). Apple's
   own ladder fits that interpolation to −0.0017…+0.0032 on ten intermediate rungs across two
   backgrounds; a linear-light mix of the same two endpoints misses one-signed by +0.0089…+0.0331.
   The choice was right and it is now a curve rather than a point.
2. **The sub-unit gap to Apple is the material's level, faded in.** `GPU − native` runs +0.0295 →
   +0.0071 on the photo and +0.0495 → +0.0116 on the checkerboard as the strength rises from 0.1 to
   1.0. At low strength the composite is mostly the untinted material, whose level on this span is
   already +0.035 (photo) and +0.055 (checkerboard) over native (claims §5.55 §3). Scaled by
   `(1 − s)` that predicts +0.031 / +0.017 / +0.009 on the photo at 0.1 / 0.5 / 0.75 against the
   measured +0.0295 / +0.0201 / +0.0116. **The strength axis costs the renderer nothing of its own.**
3. **Something small survives at full strength.** +0.0071 on the photo and +0.0116 on the
   checkerboard at `s = 1`, where the material IS the tint and the level gap should have gone. That
   is the tint shade's own distance from Apple's fully-tinted material and it has no ledger entry.
4. **The CSS tier crosses Apple's curve where the renderer does not.** On the photo at `s = 0.1` the
   tier reads 0.0389 UNDER native while the renderer reads 0.0295 over it; the tier crosses at about
   `s = 0.3`. That is the composite defect W19 exists to close, seen against Apple rather than against
   the renderer.
