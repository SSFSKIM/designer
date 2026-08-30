---
"@vitreajs/vitrea-web": minor
---

A host with four different corner radii now says so, at registration.

Per-corner radii are still post-v1 (X8 rider 3: v1's corner algebra is
mirror-symmetric by construction). What changed is that the limit is honest at
the boundary that accepts it. `CornerRadii` is a Vec4 in every type along the
path and the CSS tier renders four radii correctly through `border-radius`, so
four different radii look supported right up until the WebGPU tier resolves the
shape against the first one — or `@vitrea/geometry` throws from inside a frame,
on a shape that no longer names the registration that produced it.

The new `non-uniform-radii` diagnostic fires in dev mode from `registerHost` and
from any `update` that patches radii, names both tiers' answers, and dedupes per
surface. It is a warning: the surface still draws, and taking a page down over a
corner would be the wrong trade for a limit the roadmap intends to lift.
