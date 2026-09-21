# W31 G0 — what the sheets show, before any fit exists

Six sheets in this directory, panels left to right: **native | WebGPU | CSS |
OKLab ΔE × 8** (the difference panel is native against the WEBGPU capture, the
tier this wave fits). 1x, both schemes. The web panels are the SCRATCH capture
tree (`/tmp/w31-g0-captures`), disclosed as such; they reproduce the committed
0.20.0 rows bit for bit on `interiorMeanWeb` and `ssimMean`
(`reproduction-check.md`), so what is on the page is what shipped.

Written before the leaf exists, which is the only time it means anything.

## Hue, not level

**`photo__rrect-lg__rest`, dark.** The reference's body is a *photograph seen
through glass*: the backdrop's broad green-to-magenta diagonal passes through it
at a lower level and a lower contrast, but with its hues intact and in place —
you can point at where the green ends and the magenta begins, inside the body,
without looking outside it. vitrea's body is a flat warm grey with a faint
lavender wash, and it has no hues to point at. The two bodies are at almost the
same level (0.1814 native against 0.1627) and they do not look like the same
material at all.

> **2026-09-21, the review closure (claims §5.161 §11, finding N11 (iii)):
> 0.1627 is the `dom` row's `interiorMeanWeb` and the panel described is the
> **WebGPU** one, which reads 0.1635.** Both are `photo__rrect-lg__rest` on the
> 1x dark macOS 27 profile against the same native 0.1814, so the sentence's
> point — the two bodies sit at almost the same level and still do not look like
> the same material — is unchanged at either figure, and the |Δ| it rests on is
> 0.0179 rather than 0.0187. Corrected beside because the panel and the number
> should name the same tier.

The difference panel is the part that decides where the work is: it is
saturated white across essentially the whole interior and dark only in the two
narrow bands where the backdrop happens to be near-neutral. This is not a rim
finding or an edge finding. The residual is interior-wide and it is chromatic.

**`photo__rrect-md__rest`, light.** The same thing, smaller. The reference's
body carries a pink-to-green sweep with visible structure; vitrea's is a paler,
flatter version of the same sweep — the hues are *there* and they are weak. So
the light scheme has the residual too, which the numbers say as well: ratio (ii)
0.794 native against roughly half that on the web side. It is milder than the
dark scheme's for the obvious reason — the light plate's alpha is 0.49 against
the dark plate's 0.905, so five times more of the backdrop survives it — and it
is the same defect.

**`mid-chroma-solid__capsule-button__rest`, light.** Over a saturated magenta
solid the reference's body is a clean lighter PINK: the same hue, lifted. The
WebGPU body is a *lavender* — desaturated and rotated toward blue, which is
worse than merely pale. The CSS body is noticeably closer to the reference's
pink than the WebGPU body is. **On this cell the derived tier beats the fidelity
target**, and the reason is on the page rather than hypothetical: that tier's
`backdrop-filter` carries `saturate(1.8)` and the renderer carries no
counterpart at all.

**`mid-chroma-solid__capsule-button__inactive`, dark.** The starkest of the six
and a different failure. The reference's receded body over the magenta solid is
BRIGHTER and MORE saturated than the backdrop — a vivid pink plate. vitrea's is
a dark dull purple, well below the backdrop's level and most of the way to
neutral. This is the recede's worst cell's population (W29 §5.154 §8) and the
sheet says it is missing a level as well as a hue, which the chroma lever alone
will not close.

## What the eye sees that the metrics do not

1. **A hue ROTATION, not only an attenuation.** On `mid-chroma-solid` light the
   web body is not a desaturated version of the reference's pink — it is a
   different hue. A retention that scales chroma toward the backdrop's
   chromaticity would fix the direction as well as the amount, but the ledger
   should record that the two are separate defects and that `tintHueShift*` is
   already in the row and was never read on these cells.

2. **The flatness reads as the wrong MATERIAL, not as a wrong colour.** The
   difference between the two dark photo panels is not "one is greyer". The
   reference reads as a transparent slab and vitrea's reads as a painted panel
   sitting on top of the image. Level agreement is what makes that so visible:
   the eye has nothing else to explain the flatness with.

3. **The CSS tier is not uniformly behind.** On the saturated solid it is ahead
   of the WebGPU tier; on the dark photo cells the two look alike. Any claim
   that the derived tier trails the target is a claim about which cell.

## Deliberately not looked for

Nothing about the rim, the shadow's width, the lens or the corner. Those are
other waves' and looking for them on a sheet built to show chroma is how a
finding gets attributed to the wrong operator.
