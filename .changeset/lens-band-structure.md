---
"@vitreajs/vitrea-web": minor
---

The refraction band at the edge of glass now has the shape of Apple's, not only
its strength.

Look closely at the rim of a Liquid Glass surface over a checkerboard and the
band is a set of crisp lobes: the rows behind it reversed and compressed, a
sharp fold where the bend is steepest, distinct lobes at the corners, a dark
line inside the rim. Vitrea's band had the magnitude of that bend without its
shape — the same depth of displacement spread as a smooth curve. This release
carries the shape, measured from Apple's own field rather than assumed from
its description.

**A steeper profile.** The displacement across the band is one steep power
along the material's own span law, so most of the bend sits in a narrow fold
just inside the contour with the interior nearly still, which is what produces
the reversed rows and the fold.

**An ovalized direction.** On thick surfaces the bend runs along a direction
blended toward the ellipse inscribed in the surface, so the band is magnified
along the edge and the corners carry their own lobes; on thin controls the
direction stays the rounded rectangle's. The change is a band between the two
spans, continuous through a morph.

WebGPU tier only, at 1x and 2x: the CSS tier has no lens (a `backdrop-filter`
cannot displace), and it is unchanged. Every checkerboard size measured moved
toward Apple's at both scales.

Nothing in your code changes. If you pass a material profile of your own, the
lens gains `lensProfileExponent`, `lensOvalization` and the two spans that
grade it; a profile that does not name them gets the measured values.

Measured against macOS 26.5 and recorded in `c9a-fidelity-claims.md` §5.49–§5.52
and §5.59.
