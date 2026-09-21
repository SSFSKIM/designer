---
"@vitreajs/vitrea-web": minor
---

**The outer shadow's exterior is fitted as a whole, and a receded window stops casting one.**

Three things move in the four macOS 27 profile documents, and they are the material a page draws by
default.

**The outset.** `spreadPx` — the distance the shadow's silhouette is grown by before it is blurred —
was 3.10 CSS px in every document that carried it, inherited from the macOS 26.5 default and never
fitted on the macOS 27 bed. Apple's own outset measures about half a pixel (W32 G0). It ships at
**0.50** on the light document and **1.80** on the dark one, which are the two beds' own readings:
the dark bed refuses the light bed's value by 2.7 times the noise bar at span 160. `offsetPx` stays
at 7.95 — a rendered coordinate step over Apple's own interval moves the fit's objective by
4 × 10⁻⁷, so the displacement needed nothing.

**The amplitudes, re-solved against what the shadow does between 3 and 48 CSS px** rather than over
the whole exterior. The six occlusion anchors and the σ law's slope on the dark document move with
the outset. What a page sees: the shadow's transmission now tracks Apple's to within a mean of
**0.0006 to 0.0039** of a unit of backdrop light across every band, span, colour scheme and scale —
against 0.0039 to 0.0089 at 0.21.0, and inside the shape clause on all twelve bed × span rows where
four were inside before.

**A receded window draws no outer shadow.** Apple's unfocused window removes no light at all from 3
CSS px outward — measured on 121 of 121 non-holdout inactive cells, 153 with the holdout, and 235 of
235 on the frozen macOS 26.5 bed — while vitrea drew the ACTIVE shadow there, because both receded
documents carried their active document's anchors leaf for leaf. The receded documents' amplitudes
are **0** from 0.22.0. Visibly: the shadow now fades out when a window loses focus, which is what the
reference does, and the group clip in the inactive pose shrinks with it because
`outerShadowReachPx` returns 0 at zero amplitude.

Every document's `resolvedMaterialSha256` moves, as a fit must, and
`root.material.resolvedMaterialSha256` reports the new one. An app that pinned a digest, or that
passes `materialProfileDocument` of its own, is unaffected except in what it reads back. The CSS
tier follows the same three lengths through the mirror `tier-coherence` pins, so a page on the CSS
tier gets the new outset too.
