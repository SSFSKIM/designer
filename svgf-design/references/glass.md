# Engineered glass

The flagship material. Read `filter-mechanics.md` first if any of the
mechanics here (filter region, sRGB, premultiplied alpha) are unfamiliar —
this file assumes it.

## What engineered glass is

Engineered glass is **computed refraction at the bezel, an optically flat
center, and a specular rim** — a per-pixel displacement map that bends
whatever sits behind the element only where the surface curves, leaves the
center untouched, and catches light along the edge the way a real lens does.
North stars: **Apple Liquid Glass** (visionOS/iOS-26 material system) and the
**kube.io engineered-optics method** (the canonical physics-grounded web
implementation this skill's generator ports).

Contrast this explicitly with **2021 glassmorphism**: `blur(14px)` on a
translucent white fill with a 1px white border, applied to every card, over
a gray page. That look has no optics — nothing bends, nothing has a rim,
every surface gets the same treatment regardless of what's behind it. It
reads as a filter someone left on, not a material. Engineered glass is the
opposite claim: refraction is *computed from the shape's own geometry*, it
appears on a small number of deliberately chosen surfaces, and the ground
beneath it is a design decision (see `grounds.md`), not an afterthought.

## The tier system

Three tiers, worst case to best, and every real page ships all three:

1. **Worst-case opaque base.** `@supports not (backdrop-filter: blur(1px))`
   — a solid, readable fill. No blur, no transparency, nothing that depends
   on a capability the browser doesn't have.
2. **Frost tier.** `@supports (backdrop-filter: blur(1px))` — CSS
   `backdrop-filter: blur(14px) saturate(160%)`. This is the tier Safari and
   Firefox actually render today; it must look designed on its own, not like
   a degraded fallback.
3. **Refraction tier.** The full engineered-optics look — `backdrop-filter:
   url(#svgf-glass-<w>-<h>)` pointing at a generated SVG filter. This is the
   tier that reads as true liquid glass, and today it only renders in
   Chromium.

**Both tiers share geometry and tokens** — same corner radius, same fill
color, same specular rim — so a browser landing on the frost tier isn't
seeing a lesser design, just a lesser-supported one.

The refraction tier is **capability-gated, never `@supports`-gated**. The
winning mechanism, verified in this repo's spike across Chromium, Safari,
and Firefox: a **layered no-op overlay** — `.svgf-glass-refract` is a
sibling element carrying the refraction filter, painted after the frost
layer. In Chromium it renders the full optics. In Safari and Firefox,
`backdrop-filter: url()` is unsupported, so the layer paints nothing and
harmlessly falls through to the frost layer underneath — a confirmed no-op,
not a broken one.

**Never gate the refraction tier with `@supports (backdrop-filter: url())`.**
Firefox and WebKit both return `true` for
`CSS.supports('backdrop-filter', 'url(#x)')` while rendering nothing — a
`@supports url()` false positive, verified directly against Firefox 140.0.2
and WebKit in this repo's spike: the property parses as syntactically valid
CSS but the engine never actually renders it. An `@supports` gate built on
that query would confidently ship broken glass in both engines. The no-op
overlay sidesteps the question entirely — it doesn't ask the browser what it
supports, it just lets rendering (or non-rendering) happen.

Two accessibility overrides sit on top of both tiers:

- **`prefers-reduced-transparency: reduce`** replaces the panel with a
  near-opaque fill and disables the frost/refract/tint children outright —
  this is Apple's own behavior for Liquid Glass, not a workaround invented
  here.
- **`prefers-contrast: more`** drops to a fully solid panel: no blur, no
  backdrop-filter, a hard border. Contrast-sensitive users get a plain panel,
  not a compromised glass one.

## Generating the optics

Never hand-write a displacement filter for glass. Generate it:

```bash
node svgf-design/scripts/make-glass-map.mjs --width 360 --height 72 --radius 36 --bezel 16 --strength 60 --shape pill
```

Flags:

| Flag | Controls |
|---|---|
| `--width` / `--height` | The element's CSS px size — the map is authored to exactly this geometry, not a percentage or a viewport unit. |
| `--radius` | Corner radius in px. Ignored for `--shape pill` (forced to `height / 2`). |
| `--bezel` | Width of the curved rim band, in px, where displacement happens. Inside this band the map is neutral (no bend); the bezel is the whole optic. |
| `--strength` | The `feDisplacementMap` `scale` value — how far the rim bends what's behind it. This is the one parameter safe to animate at runtime (see Motion below). |
| `--shape` | `pill` (radius forced to half the height), `squircle` (uses `--radius` as given), or `rect` (radius fixed at 4px). All three share the same rounded-rect signed-distance geometry. |

Running it prints a complete, self-contained snippet to stdout: the
`<svg><filter id="svgf-glass-<width>-<height>">` block (data-URI displacement
map via `feImage`, `feDisplacementMap`, `feGaussianBlur`, `feColorMatrix`,
all under `color-interpolation-filters="sRGB"`), the paired sibling-tier CSS,
and a trailing usage comment. Paste the whole thing — don't extract pieces.
The filter `id` encodes its exact pixel size (`svgf-glass-360-72` above) so
multiple glass elements at different sizes never collide and so it's obvious
at a glance which map belongs to which element.

The HTML structure is three sibling layers — `.svgf-glass-frost`,
`.svgf-glass-refract`, `.svgf-glass-tint` — under an unfiltered
`.svgf-glass` parent, with content on top:

```html
<div class="svgf-glass">
  <div class="svgf-glass-frost" aria-hidden="true"></div>
  <div class="svgf-glass-refract" aria-hidden="true"></div>
  <div class="svgf-glass-tint" aria-hidden="true"></div>
  <div class="svgf-glass-content">…</div>
</div>
```

**Sizing law.** Displacement maps are authored to a fixed pixel geometry and
don't auto-track element resize — `make-glass-map.mjs` generates each map at
**2×** the target pixel size specifically to keep the bezel gradient clean at
that fixed size, not to support arbitrary scaling. Size signature glass
chrome in px, generate one map per breakpoint width, and **regenerate beyond
roughly 20% stretch from the generated width**. This repo's spike measured
the actual tolerance directly: clean, symmetric rims through 30% stretch,
with visible asymmetric degradation (weaker frosting on the side that falls
outside the map's native span) only showing up at extreme stretch (~2.8×).
The ~20% rule stays the working bound — it's comfortably inside the measured
safe range, not a guess.

## Where glass may live

Glass belongs on **floating chrome** — toolbars, tab bars, bottom sheets,
command palettes, inspectors, transport controls — sitting over a rich,
changing ground. Pick the ground per `grounds.md`: **Authored SVG/gradient
grounds**, **Real photography**, or **Simulated product content**, chosen for
the surface's register, not by default.

The ban list, each one a rule on its own:

- **No glass over a blank or flat-gray ground.** Refraction with nothing to
  bend renders as a faint tint shift, not glass.
- **No glass card grids.** Glass is chrome, not a content-card default —
  repeating it across a grid of cards is exactly the 2021-glassmorphism
  failure this file opened by rejecting.
- **No glass-as-default-card.** A card surface never defaults to glass just
  because glass is available; it needs the same floating-over-rich-content
  justification any other glass surface needs.
- **Frost alone ships only as the Safari/Firefox fallback tier or a quiet
  supporting surface** — never as the intended, primary look on a surface
  that could have shipped full refraction.

## Legibility contract

- Text contrast comes from the **`.svgf-glass-tint` scrim layer**, never
  from the blur or the refraction. Blur and displacement are optical
  effects, not contrast tools — size the tint's opacity to hold the
  interface's normal text-contrast floor regardless of what's moving behind
  it.
- Focus rings are unaffected by any glass layer — they render on the content
  layer, above frost/refract/tint, exactly as they would on any other
  surface.
- Hit targets stay undistorted. The frost and refraction layers are visual
  only: `.svgf-glass-frost`, `.svgf-glass-refract`, and `.svgf-glass-tint`
  all carry `pointer-events: none` and `aria-hidden="true"`, so a displaced
  rim never shifts where a tap actually lands and never enters the
  accessibility tree as a phantom element.

## Motion

Refraction is alive for free — content scrolling beneath the glass moves
through the displacement map continuously, with zero animation code. Don't
add anything on top of that baseline motion.

For interaction-driven changes (hover, press, expand):

- **Morph between class toggles** — two precomputed states (e.g. a resting
  pill and an expanded panel), switched by adding/removing a class, each
  with its own generated map if the geometry actually changes size.
- Or **animate the `strength` value only** — it's the cheap attribute
  (`feDisplacementMap`'s `scale`), transitionable without regenerating the
  map or touching any other part of the chain.
- **No ambient loops.** Nothing pulses, drifts, or breathes on its own —
  glass is a material property, not a decoration that needs to prove it's
  there.
- **`prefers-reduced-motion` freezes any animated attribute** — the
  interaction still changes state (class toggle, `scale` value updates
  instantly), it just doesn't transition.

## Worked example

A floating transport toolbar over an authored ground, using the exact CLI
invocation from the Generating the optics section above. The ground is
`grounds.md`'s **Authored SVG/gradient grounds** copy-adapt block — three
radial hues plus a repeating diagonal-band layer, so the toolbar's rim has
real edges to bend.

```html
<body>
  <!-- (1) rich ground, structural geometry not just color — grounds.md
       "Authored SVG/gradient grounds"; satisfies the ban on blank grounds -->
  <div class="svgf-ground">
    <!-- page content scrolls under the toolbar -->
  </div>

  <!-- (2) generated by:
       node svgf-design/scripts/make-glass-map.mjs --width 360 --height 72
         --radius 36 --bezel 16 --strength 60 --shape pill
       pasted verbatim — filter id svgf-glass-360-72 encodes its exact size -->
  <svg width="0" height="0" aria-hidden="true" style="position:absolute">
    <filter id="svgf-glass-360-72" x="0" y="0" width="100%" height="100%"
            color-interpolation-filters="sRGB" primitiveUnits="userSpaceOnUse">
      <feImage href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAtA…9k="
               x="0" y="0" width="360" height="72" result="map"/>
      <feDisplacementMap in="SourceGraphic" in2="map" scale="60"
                         xChannelSelector="R" yChannelSelector="G" result="displaced"/>
      <feGaussianBlur in="displaced" stdDeviation="3" result="blurred"/>
      <feColorMatrix in="blurred" type="saturate" values="1.6"/>
    </filter>
  </svg>
  <style>
    /* (3) parent carries NO filter/backdrop-filter — sibling architecture,
       see The tier system above */
    .svgf-glass { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%);
      width: 360px; height: 72px; border-radius: 36px; overflow: hidden; }
    @supports not (backdrop-filter: blur(1px)) {
      .svgf-glass { background: rgb(22 26 44 / 92%); }   /* (4) worst-case tier */
    }
    .svgf-glass-frost { position: absolute; inset: 0; pointer-events: none; }
    @supports (backdrop-filter: blur(1px)) {
      .svgf-glass-frost {                                 /* (5) frost tier */
        -webkit-backdrop-filter: blur(14px) saturate(160%);
        backdrop-filter: blur(14px) saturate(160%);
      }
    }
    .svgf-glass-refract { position: absolute; inset: 0; pointer-events: none;
      -webkit-backdrop-filter: url(#svgf-glass-360-72);   /* (6) refraction tier —
      backdrop-filter: url(#svgf-glass-360-72); }             capability-gated overlay,
                                                                never @supports-gated */
    .svgf-glass-tint { position: absolute; inset: 0; pointer-events: none;
      background: rgb(22 26 44 / 40%); }        /* (7) legibility contract: contrast
                                                     lives here, not in the blur */
    .svgf-glass::after { content: ""; position: absolute; inset: 0; border-radius: inherit;
      pointer-events: none; z-index: 1;
      box-shadow: inset 0 1px 0 rgb(255 255 255 / 42%),
                  inset 0 -1px 0 rgb(255 255 255 / 8%),
                  inset 1px 0 0 rgb(255 255 255 / 16%); }     /* (8) specular rim */
    .svgf-glass-content { position: relative; z-index: 2; }   /* (9) real hit targets,
                                                                   unaffected by (3)–(8) */
    @media (prefers-reduced-transparency: reduce) {
      .svgf-glass { background: rgb(22 26 44 / 97%); }        /* (10) accessibility
      .svgf-glass-frost, .svgf-glass-refract, .svgf-glass-tint { display: none; } */
    }
  </style>

  <!-- (11) three sibling layers + content, per "Generating the optics" above -->
  <div class="svgf-glass" role="toolbar" aria-label="Playback">
    <div class="svgf-glass-frost" aria-hidden="true"></div>
    <div class="svgf-glass-refract" aria-hidden="true"></div>
    <div class="svgf-glass-tint" aria-hidden="true"></div>
    <div class="svgf-glass-content">
      <button aria-label="Previous track">⏮</button>
      <button aria-label="Play">▶</button>
      <button aria-label="Next track">⏭</button>
    </div>
  </div>
</body>
```

**What each numbered part satisfies:**

1. Rich, structural ground (`grounds.md`) — the ban on glass over blank
   grounds.
2. The exact generator output, pasted rather than hand-tuned — Generating
   the optics.
3–6. The tier system, in order: filter-free parent, worst-case fill,
   `@supports`-gated frost, capability-gated (never `@supports`-gated)
   refraction.
7. The tint layer carrying legibility, not the blur — Legibility contract.
8. The specular rim, CSS-only, cheap and cross-engine.
9. Content sits above every visual layer with real hit targets — Legibility
   contract's undistorted-hit-targets rule.
10. `prefers-reduced-transparency` — The tier system's accessibility
    overrides.
11. The five-element sibling structure from Generating the optics, with
    `role="toolbar"` and per-control `aria-label`s satisfying the "floating
    chrome" placement this section opened with, not a card.

No motion is shown here because the toolbar's only motion is the free
scrolling-content refraction described in Motion — nothing in this example
needs a transition to demonstrate the material.
