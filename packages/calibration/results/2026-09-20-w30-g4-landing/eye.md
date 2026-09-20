# W30 G4 — by eye: the span-graded shadow on the page and on the bed

*The sheets are `sheets/apple-macos-27.0-2x-{light,dark}-standard-glass0.5.png`,
composed by `sheet.py` from this gate's own `harness-captures.sh` run and
`demo-shot.mjs`. Two cells per scheme — `photo__capsule-button__rest` at a
casting span of 44 CSS px, where the law draws σ 2.13 against 0.19.0's 11.0, and
`photo__rrect-lg__rest` at 160, where it draws 17.37 against the same 11.0 —
as native | vitrea WebGPU | difference ×8, with the demo's size sweep beneath
them in the same scheme. Nothing here is a metric; every number quoted is from
the ledger and every observation is the eye's.*

## The operator is visible on a real page, in both schemes

The demo band is the site's material stage: three plates at 40, 68 and 112 CSS
px, one sampling group, one authored thickness of 8 px, over one backdrop, with
nothing differing but the size. Under 0.19.0 all three cast a shadow of one
width. They no longer do, and it reads as an obvious property of the picture
rather than as a measurement: the 112 px plate sits on a broad soft shadow that
reaches well below its own edge, the 68 px plate on a narrower one, and the 40 px
plate on a tight dark band that hugs its lower contour. The three are ordered and
the ordering is the operator. It reads the same way in the dark scheme, where the
shadow is what separates each plate from a ground only a little darker than it.

That is what the e2e case now asserts — the 112 px plate's blur exceeds the 40 px
plate's, one page, one group, one thickness (§5.159b §8) — and this is what the
assertion looks like.

## The thin caster's exterior is the wave's clean win, and the sheet says so by omission

At span 44, in both schemes, the ×8 difference is **confined to the body**. The
capsule's interior is a full-spectrum rainbow; outside its contour there is a
thin bright outline (the rim) and then a faint, low, dark haze reaching perhaps
twenty device pixels below and to the sides, an order of magnitude dimmer than
anything inside. §5.159 §8's reading of the same regime — "0.19.0 drew a broad
low haze reaching two to three times as far; the sealed material draws the band"
— survives on a different backdrop family and at a different scale.

Worth stating as the negative it is: **there is no strip.** §5.159 §6's undrawn
row of backdrop through a thin capsule, which stopped the wave at G3, is not
present on either scheme's span-44 panel, and the body is whole from contour to
contour. That is `tanh`'s clamp (§5.159b §2) photographed rather than asserted.

## What the sheet shows that this wave did not fit, and does not claim

**The chromatic transmission over a photograph, on both spans and both schemes,
is the largest residual on the sheet by a wide margin.** At span 160 the ×8
difference saturates across most of the panel's interior — vitrea's body passes
the photograph's colours at levels Apple's does not — and at span 44 the same
residual is present at a smaller area. In the dark scheme it is worse and it is
visible without amplification: put the native and the vitrea panels side by side
at span 160 and Apple's dark body carries the photograph's green and magenta
through it where vitrea's reads as a flat warm grey. This is W29 Decision Log
6 (c)'s deferred chromatic child, untouched by this wave by contract (X3), and
the wave's own charter names a fit that appeared to move it as a warning rather
than a result.

**The exterior residual at span 160 has structure.** Below the panel the ×8
difference is not a featureless haze: it carries visible level contours, a few
concentric bands following the panel's lower edge. The σ law moved the width and
the amplitude anchors moved the energy, and what is left is a difference in the
falloff's SHAPE at the largest span — which is the regime where `falloffSigmaWeb`
reads 20.27 against the native's 17.30 on this cell's 1x sibling. It is small
against the body's residual and it is not nothing, and no metric on the bed reads
a falloff's shape.

**The rim is a thin bright outline on every panel.** One to two device pixels,
present at both spans and both schemes, brighter at 160. It is the rim band
§5.153, §5.154 and §5.155 have each recorded by eye and none has closed.

**No ringing at any contour, on either scheme.** A signed second lobe is what a
negative `sizeHeavySecondShare` would have produced and what §5.159 §8 looked
for; none was fitted on either document, and the sheets show none — the exterior
falls monotonically away from the contour with no alternating band.

## What this reading is not

No native pixel was captured (X5): every native half is a W29 fixture on disk.
The vitrea halves are re-renders of the web side at the sealed documents, which
costs nothing and is not a canonical read — no row, no cell, no number under
`results/matrix.json` moved for this file. The demo band is a screenshot of the
running site at this gate's head, and the site draws the runtime's default
material, which is what makes it comparable with the harness band above it.
