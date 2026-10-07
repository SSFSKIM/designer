---
"@vitreajs/vitrea-web": patch
---

Fix the dark 0.25 unfocused body's excess opacity on both WebGPU and CSS tiers: backdrop structure
was suppressed at short sides >=140 CSS px and absent at >=160 CSS px.

Reduce the receded `tintAlphaFar1x` and `tintAlphaFar2x` deltas from 0.20 to 0.10, with `tintAlpha`
held at 0.8 and every other leaf unchanged. The thick receded body now resolves `alphaBase` 0.9
instead of 1.0, restoring backdrop transmission on both tiers.

One measured case, a 32 px checkerboard under a large unfocused surface at 2x, is much improved
but still draws slightly less backdrop texture than it did before 0.28.0; its existing W48
exception remains (W49a Decision Log 10).
