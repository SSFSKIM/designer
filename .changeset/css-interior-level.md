---
"@vitreajs/vitrea-web": minor
---

The CSS tier's interior now sits at the same level as the WebGPU tier's.

Since 0.6.0 the CSS tier has drawn the glass body the way the WebGPU tier does, but
its interior read lighter: 0.02 to 0.06 above the WebGPU tier and above Apple's on
structured backdrops, because the tint was laid over the blurred backdrop as an
encoded overlay while the renderer lerps toward the tint in linear light, and one
overlay alpha cannot match a linear lerp in both level and slope. Two smaller
defects sat underneath: the tier applied the size law's occlusion after the tone
response where the shader applies it before, and it did not carry the renderer's
inner shadow at all.

**What you see.** Behind a surface on a light or structured backdrop the CSS tier's
glass now reads at the same brightness as the WebGPU tier's and as macOS's, where
it used to read whiter. On Chromium the tint's lerp runs inside the linear-light
filter the tier already uses, exact per pixel, over a thin element-painted tint that
keeps the tier's contrast floor; the mirror computes its alpha in the shader's order
and carries the inner shadow. Measured against the WebGPU tier, the interior level
is within 0.01 on every light calibration cell but two, similarity rises on every
light checkerboard row, and cross-tier colour difference falls on the fitted
profiles. The reduced-transparency capsule that lost its silhouette in 0.6.0
conditions again.

**What does not change.** The WebGPU tier is byte-identical on every capture. Dark
composites keep the encoded overlay, because the filter's eight-bit linear
intermediate would posterize them; the group state reports which form drew as
`cssTint: "linear" | "encoded"`, beside `cssBody`. Firefox and WebKit keep the
encoded overlay at the corrected alpha. The host element, its children and the
accessibility tree are as in 0.6.0; the cost knee is unmoved.

**Known gaps, named.** Surfaces whose contour is a union of several shapes (a
toolbar group, glass over glass on a photo) still read 0.01 to 0.015 darker than
the WebGPU tier; the cause is measured to the box arrangement and not yet
attributed. Three light solids and one text cell now sit so close to their
background that the calibration's silhouette extractor cannot condition them; they
are named in the predicate list and still gate on every perceptual row.

Nothing in your code changes. The material profile is read as before; no new
constant is fitted. The mapping's declared reference backdrop level is no longer
read on the Chromium path.

Measured against macOS 26.5 and the WebGPU tier and recorded in
`c9a-fidelity-claims.md` §5.74 to §5.76.
