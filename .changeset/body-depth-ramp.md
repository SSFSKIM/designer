---
"@vitreajs/vitrea-web": minor
---

The frost inside glass now sharpens toward the edge, the way Apple's does.

Vitrea blurred the content behind a surface at one mix of sharp and heavy
scatter across the whole surface, chosen by the surface's size. Apple's material
does not: measured through its own lens, the sharp share is highest just inside
the contour and fades toward the centre over a fixed distance, so the backdrop
reads crisply where the eye lands — at the rim, where the lens bends it — and
softens deeper in. This release carries that ramp.

**What you see at 1x.** Inside the contour the pattern behind a surface is
crisper than before and closer to Apple's, and the interior of a large platter
shows more of what is behind it: a 280 px card's centre used to be 17% softer
than Apple's and is now 12% crisper, with the band at the edge closer on every
size measured. Small controls change least; large surfaces most.

**What you see at 2x.** Nothing, in this release. On a Retina display Apple's
interior is heavier than vitrea's on every size, so the gap there is in the
body's deep value rather than in any ramp above it, and that is its own
measurement. The ramp's 2x anchors are carried in the profile and are inert.

**Both tiers carry it.** The WebGPU tier mixes per pixel by depth. The CSS tier
has one `backdrop-filter` blur per surface and mixes it at the ramp's average
over the surface, so a surface reads the same overall weight on either tier;
the CSS tier's width is the 1x law at every device scale.

**The body's widths are CSS pixels at every device scale, on both tiers.** A
reading that made them device-pixel quantities on the WebGPU tier was carried
into this wave, measured against Apple's heavier 2x interior, and withdrawn
before landing; the 2x body is unchanged from 0.3.0.

Nothing in your code changes. If you pass a material profile of your own, the
scattering facet gains eight named constants — the ramp's start at a thin and
a thick span and past the thickness knee, and its reach, each at 1x and 2x —
and a profile that does not name them gets the measured ones.

Measured against macOS 26.5 and recorded in `c9a-fidelity-claims.md` §5.61 and
§5.68.
