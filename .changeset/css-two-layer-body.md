---
"@vitreajs/vitrea-web": minor
---

The CSS tier now draws the glass body the way the WebGPU tier does.

Every previous release drew the CSS tier's body as one `backdrop-filter` blur on
the host element at a single width, the area average of the material's law. Apple's
body is two components — a sharp one that keeps the backdrop legible and a heavy
one that dissolves it — mixed by a ramp that fades the sharp share from the rim
inward, and the WebGPU tier has drawn it that way since 0.3.0. On the CSS tier
one blur cannot carry a sharp component, so behind a mid or large surface the
backdrop's structure read 30 to 60 percent flatter than Apple's.

**What you see.** The CSS tier creates three children inside your host element,
below its content: a sharp filtered layer, a heavy filtered layer over it whose
share follows the material's depth ramp as a raster mask, and the tint with the
press glow and the rim above both. Behind a surface the backdrop's structure now
reads the way it does on macOS and on the WebGPU tier: crisp at the rim,
dissolving toward the centre. On Chromium the two blurs run through an SVG filter
in linear light, which is the space Apple blurs in; on other engines they are
plain `blur()` filters. The whole-crop similarity to Apple's captures rises on
every checkerboard cell at 1x, holdout included, and the interior's spread of
backdrop structure lands within 0.007 of Apple's at 1x and 0.016 at 2x on every
calibration span.

**What does not change.** The WebGPU tier is byte-identical on every capture. The
host element keeps its box, its radius, its outer shadow and its tokens; the
children are absolutely positioned, `aria-hidden`, and take no pointer events, so
layout, hit testing and the accessibility tree are as before. Both blur widths are
device-pixel quantities through the live ratio, as the WebGPU tier's are, and take
the renderer's effective kernel width measured on its own captures.

**Two things to know.** The CSS tier's interior reads lighter than Apple's and the
WebGPU tier's on structured backdrops by 0.06 to 0.09 in level: an encoded CSS
overlay cannot match the renderer's linear composite in both mean and slope with
one alpha, and the conversion that closes it needs a renderer measurement that is
its own item. And a group whose two filtered layers would cover more than 0.4
million device pixels per frame collapses to one layer, the previous single-blur
form, which `GlassGroupState.cssBody` reports as `"collapsed"`; below that budget
it reports `"two-layer"`. The conformance table gains `maskOnBackdropFilter`,
and the mask and the linear-light filter are gated on it: an engine that has not
been verified draws two plain blurs at flat opacity.

Nothing in your code changes. If you read the host's `backdropFilter` style in a
test, read the first child's instead.

Measured against macOS 26.5 and recorded in `c9a-fidelity-claims.md` §5.71 to
§5.73.
