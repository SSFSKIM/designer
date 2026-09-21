# By eye, at the fit — W31 G3

Four sheets, `native | WebGPU | CSS | OKLab ΔE × 8`, at 1x in both schemes, from
the canonical read's own capture tree. Written against G0's `eye.md`
(`results/2026-09-21-w31-g0-chroma-cut/eye.md`) cell for cell, because the
charter's "put the capture next to the native fixture and look" is only a
measurement if the two looks are comparable.

G0's three findings, in its own order, re-read.

## 1. "vitrea's is a flat warm grey" — gone on the WebGPU tier, exactly as recorded on the CSS tier

On `photo__rrect-lg__rest`, **1x dark**, G0 wrote: *the reference's dark body
over the photograph is a photograph seen through glass, with its hues in place;
vitrea's is a flat warm grey at almost the same level, and the difference panel
is saturated white across the whole interior.*

The WebGPU panel is no longer grey. The magenta-to-green diagonal the reference
carries runs through vitrea's body in the same places and in the same direction
— muted against the reference's, but a coloured body rather than a grey one, and
the material reads as glass rather than as a panel. The difference panel is no
longer saturated white across the interior: it has structure, with dark regions
where the two agree.

**The CSS panel is still flat grey**, and that is not a miss the sheets found —
it is the declined derivation looking exactly like its own measurement (§5.164
§5). On the dark sheets the third panel is the one G0 described and the second
one is not, which is the clearest statement of the residual this wave leaves.

## 2. "the flatness reads as the wrong MATERIAL, not as a wrong colour" — resolved on the WebGPU tier

G0: *the reference reads as a transparent slab and vitrea's as a painted panel
on top of the image. Level agreement is what makes it so visible — the eye has
nothing else to explain the flatness with.*

At the fit the WebGPU body reads as a slab on all four sheets. On **1x light
`photo__rrect-md__rest`** the first two panels are hard to tell apart at a
glance: the pink-to-green wash across the body is in both, at about the same
strength. That cell's `R` is 1.0486 and it looks it.

## 3. What the fit moved the residual TO, which is new

On the light sheets the ΔE × 8 panel has inverted: the interior is now mostly
dark and **the brightest band is the rim**, a bright outline all the way round
with the interior inside it nearly black. Before the fit the interior was the
bright part. So on the light scheme the body's chroma residual is no longer the
largest thing on the cell — the rim is — and a wave that wants this cell further
should read the rim rather than the body.

That is a statement about where to look next and not a regression:
`rimPeakLuminanceWeb` moved by −0.00005 and −0.00011 on the two `photo__rrect-md__rest`
rows (§5.164 §7), so the rim did not move; the interior fell away from it.

## 4. One thing the metrics carry that the eye now agrees with

G0 recorded a **hue ROTATION** over the magenta solid — *the reference's body is
a clean lighter PINK and the WebGPU body is a LAVENDER, desaturated and rotated
toward blue* — and noted `tintHueShift*` had never been read on those cells.
`mid-chroma-solid` is a probe scene and is not in this read (the canonical run
is calibration + validation + the pitch ladder), so **the rotation is not
re-read here and the finding stands open**. On the `photo` cells the restored
hues sit where the reference's do by eye, which is consistent with a rotation
that was the plate's and not a hue-mapping error, but this gate does not claim
that.

## The four sheets

| sheet | what it shows |
| --- | --- |
| `…1x-light…__photo__rrect-md__rest.png` | the two bodies nearly indistinguishable; ΔE bright only at the rim |
| `…1x-dark…__photo__rrect-md__rest.png` | the hue through the WebGPU body; the CSS body flat |
| `…1x-light…__photo__rrect-lg__rest.png` | the same at the holdout span |
| `…1x-dark…__photo__rrect-lg__rest.png` | the wave's own cell: hue restored on WebGPU, ΔE structured rather than saturated |
