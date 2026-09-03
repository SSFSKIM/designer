---
"@vitreajs/vitrea-web": minor
---

On Retina displays the glass body now matches Apple's at its own scale.

Every previous release fitted the body's blur at 1x and drew the same law at 2x,
where it was wrong three ways at once: the two blur widths were CSS-pixel
quantities where Apple's kernel is one kernel in device pixels, so on a Retina
display vitrea blurred twice as wide; the deep interior kept a share of sharp
backdrop that Apple's has let go of by mid-depth; and the depth ramp that
sharpens the rim at 1x could not act at 2x because the interior beneath it was
already sharper than Apple's contour. This release measures the 2x body on
Apple's own captures and gives every term its second scale.

**What you see at 2x.** Behind a surface the backdrop's structure now reads the
way it does on macOS: crisp at the rim, dissolving toward the centre, and
dissolving further on larger surfaces — the heavy blur is six device pixels on a
control and grows with the surface past the thickness knee, which is what keeps
a large platter's centre as soft as Apple's while a button stays legible. The
whole-crop similarity to Apple's captures rises on every checkerboard cell
measured, most on the mid and large spans, and the interior's spread of backdrop
structure lands within about 0.01 of Apple's on every calibration span.

**What you see at 1x.** Nothing. Every second-scale term is interpolated from
the 1x value and is inert below a device pixel ratio of one; the 1x captures are
byte-identical to the previous release, and a golden at 1x now pins that.

**Between 1x and 2x** (a 1.5x display, or a window mid-drag between monitors)
the terms interpolate linearly, so nothing jumps.

**The CSS tier is unchanged at every scale.** Its single `backdrop-filter` blur
keeps the 1x law; the measured shape of Apple's single-blur ceiling at 2x is
recorded and handed to the tier's own next design round.

Nothing in your code changes. If you pass a material profile of your own, the
scattering facet gains its second-scale constants — the heavy gain at 2x and its
top past the knee, the deep value's floor and span top at 2x, and the ramp's 2x
anchors, which were provisional before and are fitted now — and a profile that
does not name them gets the measured values.

Measured against macOS 26.5 and recorded in `c9a-fidelity-claims.md` §5.69 and
§5.70.
