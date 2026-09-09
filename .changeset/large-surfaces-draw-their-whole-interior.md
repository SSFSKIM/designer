---
"@vitreajs/vitrea-web": patch
---

A surface larger than about 307 px in both dimensions no longer draws an opaque
white rectangle across its interior on the WebGPU tier.

**What drew.** On Apple GPUs every glass surface deeper than ~153 px from all
four edges — a sidebar, a sheet, a large platter — showed a hard white block
inset that far from each edge, on either sampling backend, at any radius,
smoothing or thickness. Two of the six Liquid Glass demos found it independently
on the same day and designed under it (a queue drawn at 296 px wide instead of
328, a permit platter held to 300 px tall).

**Why.** The outer shadow's falloff is the tanh form of the normal CDF, fed a
cubic in depth over sigma. Metal evaluates `tanh(x)` as `(e^2x − 1) / (e^2x + 1)`,
which is inf / inf = NaN once `2x` passes ~88.7; at the shipped sigma of 15.55 px
the cubic crossed that line at 10.07 σ, 153 px of depth. Inside the contour the
pass multiplies the falloff by `1 − coverage` = 0, and NaN × 0 is NaN, so the
alpha left the pass as NaN, converted to 0 in the target, and the premultiplied-
over blend added the body onto the page instead of covering it.

**The fix.** The falloff's argument is clamped to ±8 σ before the cubic, in the
shader and in both CPU twins (`outerShadowFalloff` in the renderer's material.ts
and in vitrea-web's optics.ts). Past 8 σ the curve is 1 to f32 exactly — tanh(24.6)
rounds to 1.0 — and the CPU reach bisection already stopped there, so no pixel of
a healthy render moves: all 44 golden and GPU specs pass unchanged. A new GPU spec
(`e2e/gpu/deep-interior.spec.ts`) reads the centre of the fixture's 420 × 400
surface and fails on the old shader with alpha 0.
