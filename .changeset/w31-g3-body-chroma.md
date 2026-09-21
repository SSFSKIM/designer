---
"@vitreajs/vitrea-web": minor
---

Carry the backdrop's hues through the body, and stop a leaf added at its
identity from moving every profile document's digest.

Over a photograph Apple's macOS 27 material shows the picture through the glass
— green and magenta are visible in the plate without amplification — and
vitrea's body rendered a flat warm grey at almost the right level. That is not a
constant fitted wrong. The body is a neutral plate composited over the blurred
backdrop, so what a photograph's hues survive the composite at is
`1 − sizedAlpha` — about half the backdrop's chroma in the light material and a
tenth of it in the dark one — against a reference that keeps 0.90 to 0.97 of its
own backdrop's. It is a mechanism the material did not have.

It has one now. After the body's composite the colour's CHROMATICITY is restored
toward the blurred backdrop's, carried to the colour's own linear luma, by a
fitted fraction per colour scheme and per window pose. The level does not move:
both ends of that mix carry the same linear luminance by construction, and
gamut is taken by scaling chroma toward the neutral at a held luma rather than
by clipping a channel. An author's tint still displaces the result exactly as it
did — the tint's shade law reads a luminance the restoration preserves — and the
CSS tier carries the same operator through the one `saturate()` it already has.

What moves for an app:

- **Nothing in this package's own constants**, and no authored CSS constant. The
  renderer's defaults are unchanged and the CSS tier's `saturate()` is still
  1.8 / 1.4; what moved is the four macOS 27 profile documents the default
  material document is assembled from, and the module generated from them.
- **A surface over a photograph, a gradient or any coloured backdrop now shows
  that backdrop's hues in its body** rather than a grey of the same lightness.
  The effect is largest in the dark scheme, where the plate is most opaque and
  the loss was worst, and on an unfocused window, which had no chroma law at
  all.
- **A surface over a neutral backdrop is unchanged**, to the bit: a retention
  toward the backdrop's chromaticity is the identity where the backdrop has none.
- **`root.material`'s digests read differently**, because the fingerprint's
  definition changed and not because a page draws something else. A leaf whose
  value is its declared inert identity is now dropped from the digest, so the
  two frozen macOS 26.5 documents report the numbers they were sealed at —
  `b2b570e4adcea8fb` and `874be66ea501621b` — instead of the numbers an inert
  leaf had pushed them to. A page pinned to macOS 26.5 draws exactly what it
  drew; the name of that material's digest went back to its own.

An app reading `GlassGroupState.materialDocument` or `root.material` and
comparing a digest against a literal recorded under 0.19.0 or 0.20.0 has to
re-record it. Nothing else in the public surface moves.
