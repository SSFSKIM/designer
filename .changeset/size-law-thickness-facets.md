---
"@vitreajs/vitrea-web": minor
---

Large surfaces now read as thicker glass, the way the reference does.

Apple derives five separate facets from a surface's thickness and size; vitrea
implemented one of them (lensing depth). The remaining four are now coupled to
the same curve, so a wide surface refracts deeper, scatters more softly, occludes
more of its backdrop and casts a deeper inner shadow than a small one cut from
the same material.

**This changes how your existing surfaces look**, and the change is by design. It
is larger the wider the surface is: below about 32 CSS px on the shorter side
nothing moves, and above about 96 px the facets are at full strength. A row of
small controls will look essentially as it did; a large panel will look
noticeably deeper.

One mechanism drives all four, not four independent knobs — a single smoothstep
between those two spans, with each facet taking a gain on it. That is deliberate:
the reference has one size law, and two curves would have been two mechanisms it
does not have.

Nothing new to call. `thickness` on a surface still means what it meant, and the
span the law reads is the surface's own measured box. If you need the old
behaviour for a specific surface, the gains are reachable through the material
profile seam.
