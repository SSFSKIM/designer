---
"@vitreajs/vitrea-web": minor
---

A thick surface's edge is now brightest at two corners and faintest at the other
two, grading along the straight sides between them, the way Apple's does.

**The rim grades corner to corner.** vitrea drew one edge brightness along the
whole of a straight side. Apple's does not: measured by position rather than by
direction, the top edge of a thick dark panel falls from 0.0442 to 0.0158 of
linear light along its own length, and the four sides' slopes are exactly
antisymmetric — top against bottom, left against right — which is the signature
of a field that peaks at two opposite corners rather than of a light that shines
from one side. The rim's amplitude now carries that field: the product of the two
normalised coordinates across the surface, `+1` at the top-left and bottom-right
corners and `−1` at the other two, riding the same size ramp as the rest of the
thick material, so a capsule and any surface below 32 px keeps a flat rim by
construction (`rimAlongSideSlope`).

**And W24's lit edge was re-fitted with it.** The two terms multiply one
amplitude and peak on the same diagonal, so the exponent that shipped in 0.13.0
had absorbed part of the grading and the pair had to be fitted together: 46
rendered candidates over the plane, read on 54 rows / 864 angular bins and 58
rows / 220 straight sides of the untinted solids at both device pixel ratios in
both colour schemes, with the held-out scenes never opened. `rimLitExponent`
1.15 → **0.85** and `rimAlongSideSlope` 0 → **0.10**. The lower exponent is what
keeps a faint rim at the two dim corners, where the previous law drew none and
Apple's keeps a shallow floor: on the 1x light dark panel the null reads 0.0095
against Apple's 0.0366 where 0.13.0 read 0.0044, and the two bright corners come
in toward the reference from the outside (0.1422 → 0.1374 against 0.1222, and
0.1438 → 0.1387 against 0.1274). Over the 28 thick solid rows the mean angular
bin error falls 0.17527 → 0.17208 and the corner-to-corner range error 0.43269 →
0.37472, sixteen rows improving against twelve.

**Three mechanisms ship inert, with their constants named, because the bed said
what the missing lever is.** The wave set out to close the thick surface's haze
and measured, on a new fixture set built for it, that Apple's blur is two
components and that what separates a thick surface from a thin one is the heavy
component's SHARE — 0.47 against vitrea's 0.23 at 1x. Raising the share is
implemented (`sizeScatterHeavyShareThick1x`, `sizeScatterHeavyShareThick2x`) and
ships at 0, because vitrea's heavy component is 13.3 device px wide where Apple's
is 19.5 and its width is not adjustable: it is a mip-chain level, and every check
off the three rows that identify the share runs the other way — more of a
too-narrow blur is more of the wrong thing. A level term above the size law's
knee (`sizeToneLevelFar`) ships at 0 for a different reason: its sign depends on
which backdrops are counted. Both are the next wave's, and the constants are on
the profile so that the wave that fits a continuous heavy width has them.

**The reference harness gained a declared probe fixture set**, and it is what
made those measurements possible: 52 scenes — coarse checkerboards and an
impulse backdrop over four spans, and a solid span sweep from 32 to 160 px — at
both scales in both colour schemes, captured from Apple's own material at one
sitting. It is captured routinely, read by fits and cited by claims, and gated
by nothing: the adopted-threshold suite drops it from every count, bound, floor
and conditioning exclusion, and asserts that it does. The calibration package
gained the three width readers those fixtures are read by and
`materialize --omit`, which leaves a hole in the bed with its reason written into
the provenance rather than publishing a cell whose reference appearance three
runs disagreed about.

**The CSS tier takes the exponent and cannot take the field.** Its derived
interior band integrates the lit factor around the contour — the integral runs
0.89686 of `2π` at the new exponent against 0.90741 at the old — so 33 of 85
derived captures move. The field integrates to exactly zero around a contour and
one inset shadow cannot grade along a side, so this tier's rim stays one number:
a recorded residual, not a chartered one.

On the calibration bed every group holds to five decimals in both schemes at both
scales, and on the held-out scenes — read once, after the constants were frozen —
every group holds and one improves (2x light CSS 0.01617 → 0.01616). What the
change does not close is measured too: the reader that grades along a side still
reads 0.375 of Apple's grading missing, which is the rim's own amplitude at the
corner arcs and a three-term fit for a later wave.

Recorded in `docs/doperpowers/specs/c9a-fidelity-claims.md` §5.113 (the kernel's
two components and the field), §5.115 (the probe set on the reference) and
§5.116 (the joint fit, the four declines, the dry run and the holdout).
