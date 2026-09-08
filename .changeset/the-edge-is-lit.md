---
"@vitreajs/vitrea-web": minor
---

A surface's edge is now lit from one direction, and a collapsed surface still
shows what is behind it.

**The rim is lit, not drawn.** vitrea drew the same edge brightness the whole way
round a surface. Apple's does not: on a dark capsule the top-left and
bottom-right arcs are five times brighter than the top-right and bottom-left,
and the four straight sides sit between them. Three waves of instruments missed
it for an exact reason — a light on the 45° diagonal projects equally on all four
straight sides, so every per-side reader saw a flat rim and so did the
reference's. The variation lives in the corner arcs. The rim's amplitude is now
modulated by a symmetric cosine about that diagonal (`rimLitAxis`,
`rimLitExponent`), fitted over 285 angular bins of 19 untinted solid reference
rows in both colour schemes at both device pixel ratios: the symmetric form
reaches 0.148 of normalised RMS against 0.288 for a one-sided Lambert and 0.312
for the flat rim that shipped. The factor is exactly 1 wherever the normal is
horizontal or vertical, so no amplitude fitted on a straight side moves — the
straight spans shift by at most 0.00029 of linear light — and the corners are
the only thing that changes. Read around the whole contour, the worst angular
bin error falls on every untinted solid cell of both beds and is halved or better
on ten of twelve (2x light `dark-solid__rrect-md` 0.2020 → 0.0844, 2x dark
0.0292 → 0.0112).

**A collapsed surface keeps a share of its backdrop's structure.** Over a very
dark backdrop the material collapses onto that backdrop's MEAN colour — one
number for the whole surface — which is why glass over fifteen white dots on
black passed none of them through. Apple's collapsed material is a dark glass
that still transmits what is beneath it, blurred. The collapse's target now
lerps from the group mean toward the per-pixel blurred backdrop the refraction
path already samples (`collapseTransmission`, `collapseTransmission2x`; two
anchors because the reference's transmitted width is invariant in neither CSS
nor device pixels). Through the collapsed capsule the centre dot's peak now
reads +0.0067 at 1x and +0.0256 at 2x against Apple's +0.0066 and +0.0254, where
vitrea passed exactly 0.0000 before. The transmission stands down under Reduce
Transparency and Increase Contrast, where the collapse keeps its previous
behaviour.

**The rim's one-sided specular term is retired on both tiers.** It is now
measured to have the wrong shape and not merely the wrong gain: it cannot reach
both ends of a diagonal whose two corners the reference draws equal to a
thousandth, and it degenerated in every fit trying to become symmetric. Both
shipped profiles already carried `specularGain` 0, so nothing measured moves —
but the `clear` variant's structural 0.45, which was never fitted against a
reference, stops drawing, so a `clear` surface no longer paints that specular
highlight. `specularGain` and `specularPower` remain on the material profile and
in both profile documents; nothing reads them.

**The CSS tier derives what its two layers can carry from the same profile
document.** Its rim band integrates the lit factor over the corner arcs (the
band integral lands at 0.956–0.977 of what it was over 80 renders) and its
collapse carries the transmission as an alpha reduction with the tint re-solved.
Two honest limits, both measured rather than inferred: one inset shadow cannot
vary its brightness around a contour, so the CSS tier's rim stays one number;
and on every collapsed cell this bed can see, the tier's anchored colour
conversion is degenerate over a backdrop whose tone equals the tint, returns
alpha 1 and discards the transmission, so those captures are byte-identical.

On the calibration bed the OKLab colour difference against Apple's captures
improves on the WebGPU tier in every profile (light 0.00324 → 0.00321 and
0.00329 → 0.00326; dark 0.00395 → 0.00393 and 0.00397 → 0.00395), and on the
held-out scenes — read once, after the constants were frozen — every WebGPU
group improves or holds (light 0.00901 → 0.00898, dark 0.01331 → 0.01325).

Two gaps are recorded rather than smoothed over. The exponent depends on the
scale — the 2x rows want 1.30–1.45 and the 1x rows 0.85–1.10, and one constant
ships at 1.15 — and the reference's angular profile keeps a floor at the null
that a single power law takes to zero. Both are in the ledger with their numbers.

Recorded in `docs/doperpowers/specs/c9a-fidelity-claims.md` §5.108 (the angular
read and the two fits) and §5.109 (both mechanisms landed, the clauses ruled and
the bed rebuilt).
