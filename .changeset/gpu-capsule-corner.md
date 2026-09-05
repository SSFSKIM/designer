---
"@vitreajs/vitrea-web": minor
---

Capsules draw round on the WebGPU tier. So does any rounded rectangle whose
radius is more than about a third of its short side.

**What you see.** A pill button, a circular icon button, a `rounded-full` control
— anything whose corner radius reaches half its height — drew on the WebGPU tier
with corners noticeably tighter than the stadium the layout describes, with four
small shoulders left over at the ends. A 120 × 44 capsule drew its corners at
14.39 CSS px rather than 22, and a 44 × 44 circle drew as a rounded square. The
CSS tier was never affected: it draws the DOM's own shape. Both tiers now draw the
same shape, and it is the one you asked for.

The cause was the corner reference's budget policy. Apple's `.continuous` corner
reaches 1.5287 times its radius along each edge, and when that reach no longer
fits half the short side, vitrea shrank the radius to make it fit. Apple does not:
it keeps the radius you asked for and compresses the shoulder, so the corner tends
to a plain circular arc as the radius approaches half the side, and a capsule is a
true stadium. That was measured against macOS 26.5 on a ten-rung ladder of radii
over two backgrounds, and vitrea's policy is now Apple's — the requested radius
kept up to half the short side, the reach clamped to the side, the corner's
smoothing whatever the side leaves. Below the crossing at 0.327083 of the short
side nothing changes at all, which is where every rounded rectangle in the
calibration bed sits.

The reach is what gives instead of the radius, so a surface above the crossing has
a slightly fuller corner than before as well as the right one, and its rim,
highlight, lens and tint follow the new contour. The two corner constructions meet
at the crossing within 0.0065 of the radius — 0.09 device px on a 44 px control —
so a morph or a resize that passes through it does not snap.

Recorded in `docs/doperpowers/specs/c9a-fidelity-claims.md` §5.83 (the finding) and
§5.84 (what Apple does above the ratio, measured).
