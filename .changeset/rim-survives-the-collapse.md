---
"@vitreajs/vitrea-web": minor
---

Glass on a black background is visible again, and the rim on a coloured surface
keeps that colour.

**The rim is a law of the surface's own level, not a constant.** vitrea drew the
same rim amplitude on every surface — +0.060…0.078 of linear light — where
Apple's renderer draws +0.10…0.26 depending on how bright the surface itself
sits. The rim is now affine in the material's own level, solved on vitrea's own
rendered ladder against the reference on both colour schemes' solid backdrops,
and the gain's sign is opposite in the two schemes because the reference's is:
a light surface's rim falls as the surface brightens and a dark surface's rises.
Read at the contour on every untinted surface over a solid backdrop, at both
device pixel ratios in both schemes, vitrea's rim is now within 0.02 of Apple's
per side against a miss of up to 0.19 before (claims §5.100–§5.101).

**A surface that the collapse takes keeps a rim.** Over a near-black backdrop
the tone response drives the whole of the surface's presence to zero — the
inner shadow, the rim and the specular with it — so glass on black rendered as
nothing at all, which was the user finding this work started from: Apple's own
material shows a clear outline there and vitrea's showed none. The rim now
carries an absolute floor through the collapse, so a collapsed surface's body
stays where the tone response puts it and its edge stays drawn. On every
collapsed cell of the bed, in both schemes at both scales, the contour rim lands
inside 0.005 of the reference's where it previously read exactly 0.0000.

**The rim's band is graded across the scales,** so a 2x surface's rim is the
same width in CSS pixels as a 1x surface's rather than twice it.

**The rim on a painted surface is spent in the paint's own chromaticity.** Every
luminance measurement the bed carries was met on the tinted surfaces and the rim
was still the wrong colour: Apple lifts an orange button's green channel and
leaves its blue at 0, and vitrea added white over the paint, which turns an
orange edge peach and a blue edge lilac. The rim's light is now spent in the
paint's own hue, normalised by the paint's luminance so the rim keeps its
amount and takes only its colour. Over 52 tinted sides of both beds the contour
row's OKLab distance from the reference falls from 0.0371 to 0.0088 on the
yellow-blue axis and from 0.0520 to 0.0203 on the red-green one (§5.103).

**Increased contrast: the strong border now substitutes the whole rim.** Under
the accessibility policy the border is the surface's edge, and the rim's width
anchors, its level gain and its collapsed floor were being drawn underneath it.
The policy now replaces all of them, so the strong border is one line and not a
line over a rim, and a painted surface's border keeps the border's own colour
rather than the paint's.

**The CSS tier derives the same law from the same profile document.** Its inset
border reads the rim's amplitude through the profile's own mirror, takes the
collapsed floor off the profile it was given, re-resolves when the material
profile is replaced at runtime, and converts amplitude to border alpha per
material variant instead of at one shared ratio.

On the calibration bed the OKLab colour difference against Apple's captures
improves on the WebGPU tier in both schemes at both scales (light 0.00330 →
0.00324 and 0.00333 → 0.00329; dark 0.00404 → 0.00395 and 0.00403 → 0.00397),
and on the held-out scenes — read once, after the constants were frozen — the
two light holdouts improve to 0.00901 and 0.00898.

Two honest limits. On the dark bed's coloured surfaces vitrea draws 0.031 of
contour rim where the reference draws +0.127: the composition is right and the
dark scheme's rim AMOUNT is short, which no colour can compensate for, and it
needs a reference bed with more than one fittable dark solid cell to solve. And
on the CSS tier the coloured rim moves the wrong way on the red-green axis —
one inset shadow of one colour cannot be a coloured light added per pixel. Both
are recorded with their evidence rather than smoothed over.

Recorded in `docs/doperpowers/specs/c9a-fidelity-claims.md` §5.99 (the finding),
§5.100 (the rim read at the contour), §5.101 (the law landed) and §5.103–§5.104
(the rim beneath the paint).
