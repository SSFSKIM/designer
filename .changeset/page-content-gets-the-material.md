---
"@vitreajs/vitrea-web": minor
---

Derive the WebGPU material over ordinary page content from the same profile and backdrop-tone
law as the sampled path, rather than feeding a pre-converted flat tint into its response solve.
A DOM group's body, paint shade, rim and both shadow terms now follow the stated tone and each
member's span; only the final canvas layer is converted to encoded sRGB for browser compositing.
The CSS tier reads the same scalar derivation. Registered-texture rendering is unchanged.

This implements W27 child W27f G1 (claims §5.131). A correct author hint states the real backdrop
level. With neither a hint nor a measured tone, response and collapse remain unavailable; a
scalar hint also cannot reproduce structured-backdrop colour, local spread or refraction.
