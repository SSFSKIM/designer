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
tenth of it in the dark one — against a reference that keeps 0.71 to 0.83 of its
own backdrop's in the light scheme and 0.90 to 0.97 in the dark one. It is a
mechanism the material did not have.

It has one now. After the body's composite the colour's CHROMATICITY is restored
toward the blurred backdrop's, carried to the colour's own linear luma, by a
fitted fraction per colour scheme and per window pose. The level does not move:
both ends of that mix carry the same linear luminance by construction, and
gamut is taken by scaling chroma toward the neutral at a held luma rather than
by clipping a channel. An author's tint still displaces the result exactly as it
did — the tint's shade law reads a luminance the restoration preserves.

**The CSS tier carries none of it.** The mirror was written — a gain on the one
`saturate()` that tier already has, at the alpha it actually solves — rendered
on the measured bed, and taken back out, because the measurement said to. On the
DARK scheme it bought nothing at all: the body's chroma-to-backdrop ratio read
0.2024 before and 0.2024 after, unchanged to four decimals and still unchanged
at the largest retention the leaf can hold, because that tier's converted alpha
leaves no backdrop underneath for a saturation to act on. On the LIGHT scheme it
bought a great deal and broke the wave's own level and structure stops doing it
— the level-growth stop on 10 of 26 cells and the structure stop on 13 —
because `saturate()` is a matrix on sRGB-encoded channels and stops preserving
luminance the moment one of them clips. So a page on the CSS tier draws the body
it drew before, and the residual is recorded rather than approximated.

What moves for an app:

- **Nothing in this package's own constants**, and no authored CSS constant. The
  renderer's defaults are unchanged and the CSS tier's `saturate()` is still
  1.8 / 1.4; what moved is the four macOS 27 profile documents the default
  material document is assembled from, and the module generated from them. Their
  digests are now `3dc24a74f17fd87e` (light), `8a43f54162606db4` (dark),
  `ab3ed65aa02869b1` (light receded) and `e1f42c5656ef392f` (dark receded).
- **A surface over a photograph, a gradient or any coloured backdrop now shows
  that backdrop's hues in its body** rather than a grey of the same lightness.
  The effect is largest where the plate left least of the backdrop to begin
  with — the dark scheme, whose body carried about a tenth of the backdrop's
  chroma — and an unfocused window gains a chroma law it never had, though on
  the dark scheme that endpoint is also the one the fit moved least.
- **A surface over a neutral backdrop is unchanged**, to the bit: a retention
  toward the backdrop's chromaticity is the identity where the backdrop has none.
- **Under Reduce Transparency or Increase Contrast, nothing changes at all.**
  Those preferences lift the material's occlusion, so the plate covers more of
  the backdrop and there is less of its chroma to restore; restoring the nominal
  fraction anyway gives back what the preference asked to have covered up, and
  measured on the accessibility beds it took the body's chroma to three times
  the reference's. Under an accessibility occlusion policy the retention is the
  identity, and those pages draw what 0.20.0 drew, to the byte.
- **`root.material`'s digests read differently**, because the fingerprint's
  definition changed and not because a page draws something else. A leaf whose
  value is its declared inert identity is now dropped from the digest, so the
  two frozen macOS 26.5 documents report the numbers they were sealed at —
  `b2b570e4adcea8fb` and `874be66ea501621b` — instead of the numbers an inert
  leaf had pushed them to. A page pinned to macOS 26.5 draws exactly what it
  drew; the name of that material's digest went back to its own.

An app reading `GlassGroupState.materialDocument` or `root.material` and
comparing a digest against a literal recorded under 0.19.0 or 0.20.0 has to
re-record it. The one other addition to the public surface is
`BODY_CHROMA_RETENTION`, exported beside the CSS tier's other mirrored constants
and **0** — the mirror of the renderer's default, and the constant that re-opens
the decline above if it ever leaves that value.
