---
"@vitreajs/vitrea-web": minor
---

Ship Apple's macOS 27 clearer glass as a second fixed material setting beside the default. The
new `macos27Glass025MaterialProfileDocument` is the macOS 27 material measured at the Glass
appearance slider's 0.25 position (`NSGlassTintAmount` 0.25). A page selects it with
`createGlassRoot({ materialProfileDocument: macos27Glass025MaterialProfileDocument })`, or the
same prop on `<GlassRoot>`. With no option a page still draws the slider's system default, 0.5,
and every existing endpoint fingerprint is unchanged.

The honesty-core readout now names the position that drew. `root.material.glassTintAmount` and
`GlassGroupState.materialDocument.glassTintAmount` read 0.5 or 0.25. The field is absent on the
selectable macOS 26.5 material, which predates the slider. Two positions are measured, so
there is no continuous slider, and switching documents means a new root.

The 0.25 documents are four patches over the same runtime default. They name exactly the 0.5
material's leaves and move the light tone response, transmission and scatter floors and the dark
thick tone row, where Apple's slider moved its body. Each move was gated against Apple's own
0.25 render and read once on its holdout, and every remaining miss is named in fidelity claims
§5.201. Those misses include the photo thin body, the dark scheme's smaller change, the light
receded checkers, and fine checkers at 2x, which the 0.25 body draws sharper than Apple's. The
fingerprints are `50430fa62c1120bd` / `b074fc6913a91c66` (active light/dark) and
`5d8680980b7aeb55` / `280f0fddf014e0f6` (receded).
