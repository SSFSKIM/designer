# W18 probe bed — the native pixels, read (2026-09-05)

The bed the charter's X10 custody rule governs: `apps/reference-apple/scenes-w18-probe.json`
captured on this machine at 1x by W9's protocol (claims §5.30 — a 6 s bare neutral reset before
each cell, the one stable order, the run refused unless the machine had been idle 45 s), eight runs
taken, seven attested, materialised by the majority byte-state per cell (`cli/materialize.ts
--frequency-settle`; `provenance.json`, `manifest.json`, `last-run-manifest.json`). Nothing here is
fitted to anything; the readings are the gap ledger's half of G0 (§5 of `g0/g0-findings.md`).

## The runs

| run | idle at start / end (s) | audit | kept |
| --- | --- | --- | --- |
| w18-probe-1 | 148 / 246 | 10/10 presentedActive, deterministic, materialRendered | yes |
| w18-probe-2 | 247 / 346 | 10/10 | yes |
| w18-probe-3 | 347 / 446 | 10/10 | yes |
| w18-probe-4 | 447 / 546 | 10/10 | yes |
| w18-probe-5 | 546 / 646 | 10/10 | yes |
| w18-probe-6 | 646 / **16** | 8/10 — both `glass-over-glass` cells `presentedActive: false` | **no** — HID activity during the run; the window lost key |
| w18-probe-7 | 106 / 206 | 10/10 | yes |
| w18-probe-8 | 241 / 341 | 10/10 | yes (the replacement) |

Seven cells unanimous over the seven kept runs; three frequency-settled:
`checkerboard__glass-over-glass` 6/7 (a 1/7 state in run 3), `photo__capsule-button` 5/7 (2/7 in
runs 1 and 3), `photo__capsule-sm` 5/7 (2/7 in runs 1 and 7). Materialise's own provenance block
(`manifest.json` → `bedProvenance`): seven runs, 72.2 % confidence at a one-in-six minority.

**The five recorded twins are byte-identical to the canonical fixtures captured 2026-08-31**
(`checkerboard__capsule-button`, both `toolbar-group` cells, both `glass-over-glass` cells: sha256
equal, 0 px changed). The native capture path reproduces to the byte across five days and a
re-granted Screen Recording permission.

## The readings

Interior mean and spread (population standard deviation) of linear luminance under the native
silhouette, from `compare` on both web tiers against this bed (scratch matrix; the captures under
scratch). Standard light profile, 1x.

| cell | native | GPU | CSS | GPU − nat | CSS − nat | CSS − GPU | sd native | sd GPU | sd CSS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `checkerboard__capsule-button` (120 × 44) | 0.6207 | 0.6783 | 0.6778 | +0.0576 | +0.0571 | −0.0005 | 0.1424 | 0.1385 | 0.1397 |
| `checkerboard__capsule-sm` (44 × 44) | 0.6216 | 0.6764 | 0.6687 | +0.0548 | +0.0471 | −0.0077 | 0.1503 | 0.1531 | 0.1379 |
| `checkerboard__toolbar-group-wide` (3 × 44, gap 40) | 0.6212 | 0.6762 | 0.6698 | +0.0550 | +0.0486 | −0.0063 | 0.1509 | 0.1451 | 0.1388 |
| `checkerboard__toolbar-group` (3 × 44, gap 12) | 0.6210 | 0.6763 | 0.6641 | +0.0553 | +0.0431 | −0.0122 | 0.1481 | 0.1424 | 0.1393 |
| `checkerboard__glass-over-glass` | 0.7231 | 0.7120 | 0.7078 | −0.0111 | −0.0153 | −0.0042 | 0.1321 | 0.1321 | 0.1133 |
| `photo__capsule-button` | 0.5832 | 0.6178 | 0.6183 | +0.0347 | +0.0351 | +0.0004 | 0.0461 | 0.0474 | 0.0385 |
| `photo__capsule-sm` | 0.5398 | 0.5871 | 0.5807 | +0.0473 | +0.0409 | −0.0063 | 0.0336 | 0.0258 | 0.0208 |
| `photo__toolbar-group-wide` | 0.6131 | 0.6374 | 0.6272 | +0.0242 | +0.0141 | −0.0101 | 0.0733 | 0.0766 | 0.0702 |
| `photo__toolbar-group` | 0.6012 | 0.6363 | 0.6213 | +0.0351 | +0.0201 | −0.0150 | 0.0618 | 0.0652 | 0.0629 |
| `photo__glass-over-glass` | 0.7064 | 0.6861 | 0.6742 | −0.0203 | −0.0322 | −0.0119 | 0.1234 | 0.1194 | 0.0967 |

The stack, taken apart on the native pixels with the declared rounded rectangles as masks (the
overlay 6 508 px, the base excluding it 21 592 px), beside G0 §4's web readings:

| cell | region | native | GPU | CSS |
| --- | --- | --- | --- | --- |
| `checkerboard__glass-over-glass` | overlay | **0.9088** | 0.8899 | 0.8435 |
| | base, overlay excluded | 0.6682 | 0.6593 | 0.6676 |
| `photo__glass-over-glass` | overlay | **0.8970** | 0.8739 | 0.8166 |
| | base, overlay excluded | 0.6489 | 0.6295 | 0.6313 |

## What the pixels say

1. **Apple's material is box-invariant at this span.** The lone 44 × 44 circle reads within 0.001
   of the 120 × 44 capsule (0.6216 against 0.6207) and the three-up reads the same at spacing 12
   as at 40 (0.6210 against 0.6212): the container's merge (`smoothness` 12, one backdrop over the
   row — `layer-dumps/`) changes nothing inside the members. The GPU tier is flat across the same
   four cells (0.6762–0.6783). Only the CSS tier moves with the box and the neighbours, which is
   what G0 attributed to the tier's own shadow.
2. **The renderer's level over native is +0.055 on every checkerboard thin-span cell** (§5.55 §3's
   item, unchanged by the box or the neighbours) and +0.024…+0.047 on the photo, patch by patch.
3. **The native overlay is near-white: 0.909 on the checkerboard and 0.897 on the photo** —
   +0.019 / +0.023 above the renderer's unsampled white at α 0.665 and +0.065 / +0.080 above the CSS
   tier's converted material. The renderer's overlay charter has its number.
4. **The spread names the remainder.** On the checkerboard the CSS tier frosts the small box
   about 0.015 harder than both references (0.1379 against 0.1503 native and 0.1531 GPU) and
   agrees with them on the capsule (0.1397 / 0.1424 / 0.1385); on the photo the circle reads
   0.0208 against 0.0336 / 0.0258. With the shadow out, what is left on the small box is a
   frosting difference, which G1's pre-check reads as such.

Scratch: runs under `/Users/new/.claude/jobs/5c70e47f/tmp/w18/probe/` (`drive.sh`, `drive-8.sh`,
`compare.sh`, the run snapshots, the web captures, `matrix-probe.json`).
