# Lighting (specular / diffuse)

The smallest family. Read `filter-mechanics.md` first for the sRGB rule and
the filter-region rule — this file assumes both and adds a color-space
tradeoff specific to lighting primitives.

## Role

Lighting mostly **serves glass**. The specular rim on `.svgf-glass::after` —
the three inset `box-shadow`s documented in `glass.md` — is CSS, not an
`feSpecularLighting` pass, and that is deliberate: it is the rim highlight
for the flagship material, not a separate family competing with it. Standalone
`feDiffuseLighting`/`feSpecularLighting`, run as their own filter over their
own artwork, are reserved for a narrow set of uses (locked decision 7): a
one-off 3D-ish badge or seal, a decorative material study, a non-interactive
hero material. They are not a general-purpose highlight tool — `effects-policy.md`
already calls this **"almost never for interface components,"** and that
verdict stands; this file is the deep chapter for the cases where it is
earned, not a reversal of it.

## The two paths to a highlight

**CSS inset-shadow specular** — what `glass.md` ships. Three stacked inset
`box-shadow`s (`inset 0 1px 0`, `inset 0 -1px 0`, `inset 1px 0 0`, each
white at its own opacity) fake a rim catching light from one direction.
Cheap: no extra raster pass, no height map. Controllable: each shadow is an
independent, easily-tuned value. Cross-engine: renders identically in every
browser that does inset `box-shadow` at all, with no linearRGB/sRGB
divergence to worry about.

**True `feSpecularLighting` over a `SourceAlpha` blur** — the shape's own
alpha, blurred, becomes a height map; a real light source (`feDistantLight`,
`fePointLight`, `feSpotLight`) computes per-pixel normals against it and
produces a physically-derived highlight. Richer: the falloff curves with the
actual silhouette instead of following straight edges, and a `fePointLight`
gives a true hotspot that moves believably as its position changes. The
cost is `filter-mechanics.md`'s **sRGB rule** in its sharpest form:
lighting math looks nicer in `linearRGB` — that's the physically correct
space for combining light — but Safari computes lighting primitives in
sRGB regardless of what `color-interpolation-filters` says. Author in
`sRGB` for cross-engine stability and accept the fidelity you're leaving on
the table, or author in `linearRGB` for the nicer falloff and accept that
Safari will render a visibly different (flatter, more washed) result than
Chromium and Firefox. This file's recipes stay in `sRGB` — stability over
fidelity — and say so at the point of the tradeoff.

**When to use which:** chrome reaches for CSS; artwork reaches for
primitives. A toolbar, a card, a button, any surface a pointer can land on —
CSS. A badge, a seal, a hero material study nobody clicks — primitives. If
you're unsure which side of that line something is on, ask whether it's
interactive; interactive always routes to CSS.

## Complete recipes

Both filters below carry `color-interpolation-filters="sRGB"` and explicit
region attributes, per `filter-mechanics.md`.

### (a) Embossed seal / badge

The soft-specular chain: blur `SourceAlpha` to build the height map, run
`feSpecularLighting` with a low, even `feDistantLight`, clip the highlight to
the shape's own silhouette, then blend a modest fraction of it back over the
source with `feComposite operator="arithmetic"`.

```html
<svg viewBox="0 0 120 120" width="120" height="120"
     xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Embossed seal badge">
  <defs>
    <filter id="seal-emboss" color-interpolation-filters="sRGB"
            x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="2" result="blur" />
      <feSpecularLighting
        in="blur"
        surfaceScale="3"
        specularConstant="0.45"
        specularExponent="18"
        lighting-color="#FFFFFF"
        result="specular"
      >
        <feDistantLight azimuth="225" elevation="50" />
      </feSpecularLighting>
      <feComposite
        in="specular"
        in2="SourceAlpha"
        operator="in"
        result="specularClip"
      />
      <feComposite
        in="SourceGraphic"
        in2="specularClip"
        operator="arithmetic"
        k1="0"
        k2="1"
        k3="0.34"
        k4="0"
      />
    </filter>
  </defs>
  <circle cx="60" cy="60" r="48" fill="#8A6A2F" filter="url(#seal-emboss)" />
</svg>
```

The last `feComposite` computes `result = k2·SourceGraphic + k3·specularClip`
— `k2="1"` keeps the badge's own color at full strength, `k3="0.34"` adds
back 34% of the clipped highlight on top. Raise `k3` toward 0.5 for a
shinier wax-seal read; drop it toward 0.2 for a near-flat, barely-lit metal.
`specularExponent="18"` is a soft sheen (5–10 softer still, 20–40 reads
wetter/glossier); `azimuth="225" elevation="50"` is light from the upper
left at a moderate height — match this to whatever direction the rest of
the page's drop shadows already imply.

### (b) Wet / lit hero material with an interaction-positioned light

`fePointLight` gives a true movable hotspot. The light's `x`/`y` swap
between two **precomputed states** — resting and hovered/pressed — via a
direct attribute set on pointer enter/leave. This is a discrete swap, never
a per-frame animation: the filter graph doesn't re-run continuously, it
re-renders once with a new light position, exactly like any other attribute
change.

```html
<div class="lit-material" data-lit-state="rest">
  <svg viewBox="0 0 320 180" width="320" height="180"
       xmlns="http://www.w3.org/2000/svg" role="img"
       aria-label="Lit material study">
    <defs>
      <filter id="wet-hero" color-interpolation-filters="sRGB"
              x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur in="SourceAlpha" stdDeviation="4" result="soft" />
        <feSpecularLighting
          in="soft"
          surfaceScale="5"
          specularConstant="0.9"
          specularExponent="30"
          lighting-color="#FFFFFF"
          result="spec"
        >
          <fePointLight id="wet-hero-light" x="-40" y="-60" z="180" />
        </feSpecularLighting>
        <feComposite in="spec" in2="SourceAlpha" operator="in" result="specClipped" />
        <feMerge>
          <feMergeNode in="SourceGraphic" />
          <feMergeNode in="specClipped" />
        </feMerge>
      </filter>
    </defs>
    <rect x="20" y="20" width="280" height="140" rx="16" fill="#1E4B8F" filter="url(#wet-hero)" />
  </svg>
</div>
```

```js
const light = document.getElementById("wet-hero-light");
const host = document.querySelector(".lit-material");
const REST = { x: -40, y: -60 };
const HOVER = { x: 200, y: -20 };
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

host.addEventListener("pointerenter", () => {
  if (reduceMotion) return; // resting state holds — no light move at all
  light.setAttribute("x", HOVER.x);
  light.setAttribute("y", HOVER.y);
});
host.addEventListener("pointerleave", () => {
  light.setAttribute("x", REST.x);
  light.setAttribute("y", REST.y);
});
```

`stdDeviation="4"` on the `SourceAlpha` blur sets bevel width;
`surfaceScale="5"` sets bevel depth; `specularExponent="30"` is wet-plastic
(60+ would read as harder glass glint). `z="180"` on the light keeps the
hotspot broad and soft — lower it for a tighter, harder glint. Under
`prefers-reduced-motion: reduce`, the pointer handlers simply return early
on enter, so the light never leaves its resting `x="-40" y="-60"` — the
material stays lit, it just doesn't track the pointer.

## Bans

- **Never use lighting primitives on buttons, cards, inputs, or navigation
  chrome.** That surface belongs to the CSS inset-shadow path above, full
  stop — this is the same line `effects-policy.md` already draws.
- **One light direction per page.** Whatever azimuth/elevation (or
  equivalent point-light angle) a lit material uses, it must agree with the
  page's existing shadow system — one sun, not competing light sources
  scattered across the surface.
