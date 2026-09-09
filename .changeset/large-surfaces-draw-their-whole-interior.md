---
"@vitreajs/vitrea-web": patch
---

Large surfaces no longer draw an opaque white rectangle across their deep
interior on the WebGPU tier in the reproduced Apple GPU case.

**What drew.** Large glass surfaces — a sidebar, a sheet, a large platter —
showed a hard white interior block on the tested Apple GPU path, on either
sampling backend. Two of the six Liquid Glass demos found it independently
on the same day and designed under it (a queue drawn at 296 px wide instead of
328, a permit platter held to 300 px tall).

**Why.** The outer shadow's falloff is the tanh form of the normal CDF, fed a
cubic in normalized inward distance from the shifted, spread shadow silhouette.
The reproduced failure is consistent with evaluating `tanh(t)` as
`(e^2t − 1) / (e^2t + 1)`, which gives inf / inf = NaN past `2t` ≈ 88.7;
this does not establish the implementation of every Metal compiler. The cubic
reaches that limit at normalized distance ≈10.060966. Multiplying by the shipped
sigma of 15.55 gives 156.448 px inside the shadow silhouette; subtracting spread
3.10 gives 153.348 px from the shifted glass contour. The downward offset of
7.95 makes straight-edge insets from the glass about 153.348 px left/right,
161.298 px top and 145.398 px bottom. Rounded contours depend on their actual
field distance, so this is not a universal equal-inset rectangle or size cutoff.
Inside the contour the pass multiplies the falloff by `1 − coverage` = 0, and
NaN × 0 is NaN, so the alpha left the pass as NaN, converted to 0 in the target,
and the premultiplied-over blend added the body onto the page instead of covering it.

**The fix.** The falloff's argument is clamped to ±8 σ before the cubic, in the
shader and in both CPU twins (`outerShadowFalloff` in the renderer's material.ts
and in vitrea-web's optics.ts). Past 8 σ the curve is 1 to f32 exactly — tanh(24.6)
rounds to 1.0 — and the CPU reach bisection already stopped there, so no pixel of
a healthy render moves: all 44 golden and GPU specs pass unchanged. A new GPU spec
(`e2e/gpu/deep-interior.spec.ts`) reads the centre of the fixture's 420 × 400
surface and fails on the old shader with alpha 0.
