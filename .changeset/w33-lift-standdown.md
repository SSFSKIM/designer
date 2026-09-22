---
"@vitreajs/vitrea-web": minor
---

Stand down the exterior lift on the macOS 27 material, and compensate its thick-shadow anchors.

Apple’s macOS 27 exterior over a black backdrop pixel is zero on 67 light and 50 dark
cells: 1,546,726 and 1,099,348 pixels respectively. The WebGPU material now declares
`liftAmplitude: 0` instead of adding blurred backdrop light where Apple adds none.
The three thick anchors are re-solved on the rendered 3–48 px window: light
0.0961 / 0.1797 / 0.2717 → 0.0870 / 0.1650 / 0.2518; dark
0.1051 / 0.2228 / 0.3504 → 0.1038 / 0.2188 / 0.3443. The CSS tier derives the
anchor compensation from the same profile; it did not paint the WebGPU lift.

The 232-cell non-holdout black-floor bed now reads zero, including the four hc-text
cells that previously exceeded one byte. C1, B1, B3 and the thin per-cell stop pass.
The post-seal holdout records five unchanged base-edge pixels on four composite
cells admitted by an overlay-only exterior mask; that referee-domain correction
is recorded separately, not hidden by widening the zero target (claims §5.172).

Rule-2 resolved digests and document file SHA-256 prefixes:

| endpoint | resolved digest | file SHA-256, first 12 |
| --- | --- | --- |
| light active | `dcbccbd9feac9881` | `6e509c7f76cc` |
| dark active | `e59f9106bcd7c966` | `eab099cc6698` |
| light receded | `f34dcc03e2774db3` | `45acb6d916b9` |
| dark receded | `6b6237b7ae241638` | `4e68f81869f6` |

`macos26MaterialProfileDocument` is unaffected: the frozen macOS 26.5 documents keep
their measured lifts, bytes and digests. Both macOS 27 receded documents are
unchanged. No contour leaf was added and no rim term changed (W33 Decision Log 3).
