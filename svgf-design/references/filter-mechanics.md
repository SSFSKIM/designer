# Filter mechanics

Shared primer. Every other `svgf-design` reference links here instead of
re-explaining these five facts. Read this once; it explains almost every
filter surprise you'll hit while building.

## The pipeline

A `<filter>` is a directed graph of primitives. Each primitive reads one
input (`in`; some take a second, `in2`) and writes an intermediate raster,
optionally named via `result="name"`.

Defaulting rules — memorize these, they're what makes short filters readable:

- First primitive with no `in` → `SourceGraphic`.
- Any later primitive with no `in` → the **result of the previous primitive**,
  named or not.
- `result` names are filter-scoped and reusable (last write wins).
- The **last** primitive's output is the filter's output.

Valid `in` values: `SourceGraphic`, `SourceAlpha` (alpha channel only, black
silhouette), any earlier `result` name. **Never use** the legacy
`BackgroundImage` / `BackgroundAlpha` / `FillPaint` / `StrokePaint` keywords —
they were never interoperably implemented and were dropped from the spec.
CSS `backdrop-filter` is the modern replacement for `BackgroundImage`; there
is no way to read "what's behind the element" from inside an SVG `<filter>`
anymore.

## The filter region

The filter renders into an offscreen surface sized by the *filter region*,
not by the element's visible bounds.

- Default: `x="-10%" y="-10%" width="120%" height="120%"`,
  `filterUnits="objectBoundingBox"` — 10% padding around the bbox.
- **Anything drawn outside this region is hard-clipped.** Big blurs, long
  shadows, large displacement `scale`, dilated outlines all get chopped by
  the default 10% pad. Fix by enlarging the region explicitly, e.g.
  `x="-50%" y="-50%" width="200%" height="200%"`, or by switching to
  absolute units with `filterUnits="userSpaceOnUse"`.
- `primitiveUnits` (default `userSpaceOnUse`) controls how attribute values
  *inside* primitives (`stdDeviation`, `baseFrequency`, `radius`, `dx`/`dy`)
  are interpreted — leave it at default unless you specifically need
  bbox-relative sizing; `objectBoundingBox` primitive units are flakier
  across engines.
- **Zero-area bboxes collapse `objectBoundingBox` regions and the element
  vanishes.** A horizontal `<line>`, an empty `<g>` — anything with zero
  width or height in its bounding box. Fix: `filterUnits="userSpaceOnUse"`
  on that filter.
- On HTML elements (CSS `filter: url(#id)`), the "bounding box" is the
  border box; 1 user unit = 1 CSS px, origin at the border box's top-left.

## The sRGB rule

**Command: put `color-interpolation-filters="sRGB"` on every `<filter>`** —
attribute on the `<filter>` element, or CSS `color-interpolation-filters:
sRGB`.

Why: filter math runs in **linearRGB by default** per spec (unlike CSS
shorthand functions like `blur()`, which are defined in sRGB). Mid-gray 128
in the PNG you authored is not the neutral value once converted to
linearRGB — turbulence noise, displacement-map grays, and blur falloff all
look different than authored. A displacement map built around "128 = no
shift" only behaves correctly in sRGB. Worse, engines disagree on the
default: Firefox honors `color-interpolation-filters` faithfully; WebKit has
long computed in sRGB regardless of what you set. `sRGB` is the only
setting that renders the same authored result across engines. Only opt into
linearRGB deliberately, for physically-motivated light blending in lighting
primitives — and accept Safari will diverge from it anyway.

## Premultiplied alpha

Filter intermediates are stored **premultiplied**. Primitives that need
straight RGBA (`feColorMatrix`, `feComponentTransfer`, the channel reads in
`feDisplacementMap`) un-premultiply first per spec — and fully transparent
pixels have **undefined RGB** once premultiplied.

- **Never ship a displacement map with transparent regions.** Its RGB is
  undefined there, so it displaces unpredictably. Keep displacement maps
  fully opaque (`a=255`) everywhere.
- Be suspicious of color fringes at anti-aliased edges after aggressive
  `feColorMatrix`/alpha-matrix chains — that's premultiplication rounding,
  not a bug in your values.

## What a filter does to the element

- The element and its descendants are rasterized to pixels as a group
  first — the filter never sees vectors, only pixels.
- `filter` (and `backdrop-filter`) on an element creates a **stacking
  context** and makes the element a **containing block for `position:
  fixed`/`absolute` descendants** — a `position: fixed` modal nested inside
  a filtered ancestor will scroll with the page instead of staying pinned.
- Filters flatten 3D: `transform-style: preserve-3d` in the subtree stops
  working.
- **NEVER nest a `backdrop-filter` refraction overlay inside a
  `backdrop-filter` frosted parent** — the parent becomes the *backdrop
  root* for its own descendants, so the child's refraction displaces the
  parent's already-flattened tint instead of the live page behind it.
- `filter="url(#missing)"` on an SVG element renders the element
  **invisible** in most engines (invalid reference = render nothing); the
  CSS equivalent on HTML is spec'd as a no-op in modern engines but has been
  historically inconsistent. Never ship a dangling `url(#…)` reference.
- The `<svg>` hosting your `<filter>` defs must stay renderable —
  `display: none` on it breaks filter resolution in some engines. Hide it
  with `width="0" height="0" style="position:absolute"` and
  `aria-hidden="true"` instead.

## Performance floor

- Prefer a CSS shorthand (`blur()`, `drop-shadow()`, `saturate()`…) over an
  equivalent SVG filter chain whenever one exists — browsers fast-path the
  shorthand harder.
- Keep the filter region tight and explicit; filter the smallest wrapper
  that needs it. **Never filter `<body>`.**
- Displacement maps: rebuild on resize only, debounced. Animate a cheap
  attribute (`scale`, `dx`, light position) on the existing chain instead of
  regenerating the map.
