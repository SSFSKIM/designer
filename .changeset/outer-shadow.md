---
"@vitreajs/vitrea-web": minor
---

Glass surfaces now cast an outer shadow.

The reference material casts one and vitrea rendered zero across its entire
footprint — by canvas coverage, the largest visible gap the project had measured.
Every glass surface now sits on the page instead of being pasted onto it.

**This changes how every existing surface looks.** The shadow is drawn on both
tiers from the same profile constants: a `box-shadow` on the CSS tier, and
field-derived occlusion outside the component on the WebGPU tier.

Two properties are worth knowing because they are what makes it read as a shadow
rather than as a grey halo:

- **It darkens, it does not paint.** The shadow multiplies what is behind it
  rather than laying grey over it, so it takes a lot from a bright ground and
  almost nothing from a dark one — the same behaviour a real shadow has, and
  measured against the reference rather than assumed.
- **It is coupled to the size law.** A larger, thicker surface casts a deeper
  shadow, on the same single thickness curve the other size-derived facets ride.

It respects the accessibility policies, and it goes away with the glass under
forced colours rather than surviving as decoration on a flattened surface.

Cost, stated because it is not free: on the mobile bench the facet measures
2.79× frame time. A dedicated low-resolution shadow pass is the known optimisation
and has not been built yet — the current GPU path rasterises the enlarged rect at
full resolution to feed the blur.
