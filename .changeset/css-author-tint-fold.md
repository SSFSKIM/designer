---
"@vitreajs/vitrea-web": minor
---

An author tint below full strength now draws the material it always meant to on
the CSS tier.

**What you see.** Give a glass surface a tint whose alpha is less than 1 —
`rgba(255, 149, 0, 0.2)`, say — and on Chromium the CSS tier drew a surface that
did not match the WebGPU tier drawing the same profile, by up to 0.068 of interior
level at strength 0.1 and with a hue shift on top of it. At full strength the two
tiers agreed exactly, which is why the ten strengths in between went unmeasured
for four releases. They agree now: the tier's composite is the renderer's own
expression, `(1 − s)·material + s·layer` in the page's own space, at every
strength. Measured over both seeds, six strengths, two backgrounds and two device
pixel ratios, the tier is within 0.005 of the WebGPU tier on every cell, and the
cross-tier colour difference falls by 0.003 to 0.032 of OKLab ΔE on every tinted
cell below full strength.

Two things were wrong and both are fixed by putting the right colour in one place.
The transfer table that carries the material inside the tier's filter was solved
against the tint-folded colour rather than the material's own, which on a
saturated seed drove the table past the end of its range on one channel — a
per-channel loss, inside the filter, that no downstream stage can undo. And the
author's layer was drawn at the author's own opacity over a table solved for a
different overlay, so the two composed to the intended material only where the
layer was opaque. The table is now solved on the untinted material, and the
author's layer is folded over the tier's contrast-floor overlay before it is
written.

**The contrast floor holds at every strength now.** The tier keeps a real element
paint under its filters so that an engine which reports support and renders no
filter still leaves a surface rather than nothing. A tint at strength 0.1 used to
replace that paint with one at alpha 0.1, well under the floor of 0.2668; the
folded overlay's alpha is 0.34 there and is never below the floor at any strength.

**What does not change.** The WebGPU tier is byte-identical. An untinted surface's
declarations are byte-identical, and so is a tinted surface at full strength. The
dark scheme and any surface whose composite puts it on the encoded form keep the
whole-material fold they had, as do Firefox and Safari, which have no reference
filter to carry the material in. No public API moves and no layer or filter
primitive is added — a tinted surface's filter is now the untinted surface's, so a
tinted group needs one definition fewer than before.

**The named gaps.** Under increased contrast the tinted composite sits within 0.006 of
the WebGPU tier at full strength; the untinted material on that profile sits 0.023 to
0.026 above it, which is the preference fold's own standing gap, unchanged by this
work. The tint's shade is read once per surface on this tier and per pixel on the
WebGPU tier. Over a photograph or a checkerboard that is worth under 0.003 of interior
level; over black text on white it is 0.013, because the WebGPU tier's shade darkens
under each glyph and this tier's does not. Both tiers sit above Apple's own capture
there, the WebGPU tier by 0.017, so the item is recorded against Apple and not only
across the tiers.
