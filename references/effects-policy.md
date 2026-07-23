# Effects policy

This file governs the "craft pass" step of the workflow, alongside `references/motion.md` — add material effects (blur, glass, grain, glow, gradient, organic shape, displacement) only where they earn their place, in the same pass where motion is added, once a page's layout, tokens, and content are already in place. Material effects are earned when they clarify a product's spatial model, reinforce its brand/material world, or make interaction easier to understand. They are arbitrary when they merely add perceived sophistication to an otherwise ordinary layout.

A useful test is:

> **If I remove this effect, does the interface lose meaningful depth, hierarchy, brand expression, or interaction feedback?**
> If the answer is only "it looks less trendy," I remove it.

## When an effect is earned

An effect is earned when all — or nearly all — of these are true:

1. **It has a semantic role**
   It communicates containment, layering, focus, materiality, a changing state, atmosphere, or product identity.

2. **It fits the visual stance**
   A spatial operating system, music tool, fashion editor, immersive consumer app, or visualization product may support richer materials. A dense claims-processing portal usually does not.

3. **It supports the product type**
   For example:

   - Glass: floating controls over live visual content
   - Grain: a tactile, editorial, craft-oriented brand
   - Gradient: an atmospheric consumer product or a meaningful data field
   - Glow: a signal, selected state, or live/active object
   - Organic shape: a product related to creativity, wellbeing, biology, food, or movement
   - Refraction: an immersive, visual-first product where depth is part of the interaction model

4. **It is localized**
   Rich materials belong on a few intentional surfaces — hero media, floating controls, selected objects, a compact identity moment — not every card on every screen.

5. **It preserves legibility and affordance**
   Text contrast, focus rings, form readability, and touch targets cannot be sacrificed.

6. **It has a fallback**
   Effects depending on blur, filters, animation, or high-end GPU work need a solid, readable baseline for unsupported or reduced-motion contexts.

7. **It performs within the interface's interaction budget**
   Avoid expensive animated filters, large blur regions, and lots of simultaneously composited layers in a utility interface.

## Glass

### When glass is earned

Use glass when the UI genuinely sits **above a changing visual plane**, and the transparency helps preserve context.

Good use cases:

- Floating controls over a map, canvas, video, 3D scene, or photo-led workspace
- A media player with artwork or video as the visual ground
- A mobile bottom sheet that should retain location/context beneath it
- A spatial/immersive operating-system-like experience
- A premium consumer product where depth and layering are central to the brand expression
- A temporary overlay, command palette, inspector, or utility rail

Less suitable use cases:

- Dense financial tables
- Medical record systems
- Administrative forms
- Documentation
- Inventory systems
- Dashboards where the "background" is simply gray app chrome

Glass is not earned merely because a card can be made translucent.

### Shippable CSS: restrained frosted surface

```css
:root {
  --glass-fill: rgb(255 255 255 / 68%);
  --glass-border: rgb(255 255 255 / 62%);
  --glass-highlight: rgb(255 255 255 / 45%);
  --glass-shadow:
    0 1px 1px rgb(15 23 42 / 4%),
    0 12px 30px rgb(15 23 42 / 12%);
  --glass-blur: 18px;
}

.glass-panel {
  background:
    linear-gradient(
      135deg,
      rgb(255 255 255 / 78%) 0%,
      rgb(255 255 255 / 56%) 100%
    );
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  box-shadow: var(--glass-shadow);

  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(135%);
  backdrop-filter: blur(var(--glass-blur)) saturate(135%);
}

.glass-panel::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: inherit;
  box-shadow: inset 0 1px 0 var(--glass-highlight);
}

@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .glass-panel {
    background: rgb(255 255 255 / 94%);
  }
}

@media (prefers-contrast: more) {
  .glass-panel {
    background: #FFFFFF;
    border-color: #94A3B8;
    -webkit-backdrop-filter: none;
    backdrop-filter: none;
  }
}
```

### Practical rules

- Use `blur(12px–24px)` for most UI. Values above `32px` often add GPU cost without useful improvement.
- Use glass over **visually rich or changing ground**, not a blank solid background.
- Keep a reasonably opaque fill. Nearly transparent glass often fails contrast and feels cosmetic.
- Use it for a **small number of elevated surfaces**: one header, one command palette, one inspector, or one bottom sheet.
- Do not blur every list item or standard dashboard card.

## Gradients

### When gradients are earned

Use gradients when they encode one of the following:

**A. Atmospheric identity** — Useful for consumer, creative, music, beauty, culture, entertainment, or emerging-technology products where atmosphere is part of the brand.

**B. Spatial depth** — Useful behind floating controls, visual workspaces, onboarding, or a hero where a flat field would weaken the depth model.

**C. Meaningful data** — Useful for heatmaps, intensity fields, range selections, progress, time-of-day, or environmental data — provided the gradient is labeled and accessible.

**D. Material change** — Useful when showing a surface transition: light across metal, a translucent pane, a color-shifting object, or a simulated environmental field.

Do not use a gradient merely to make a hero feel "premium."

### Shippable CSS: quiet editorial atmospheric field

```css
.hero-atmosphere {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  background:
    radial-gradient(
      90% 110% at 8% 4%,
      rgb(217 186 144 / 42%) 0%,
      rgb(217 186 144 / 0%) 64%
    ),
    radial-gradient(
      78% 100% at 96% 20%,
      rgb(103 137 124 / 28%) 0%,
      rgb(103 137 124 / 0%) 62%
    ),
    linear-gradient(
      135deg,
      #F6F0E7 0%,
      #EEE5D8 48%,
      #E7E0D7 100%
    );
}

.hero-atmosphere > * {
  position: relative;
  z-index: 1;
}
```

This is appropriate for a calm editorial or craft-commerce hero because it creates atmosphere without turning the whole page into a visibly synthetic "mesh gradient" product.

### Shippable CSS: data-intensity gradient

```css
.usage-scale {
  background: linear-gradient(
    90deg,
    #D9F0EC 0%,
    #8FD0C1 30%,
    #4F9E8D 58%,
    #E9B44C 78%,
    #C95742 100%
  );
  border: 1px solid rgb(29 42 54 / 18%);
  border-radius: 9999px;
  height: 10px;
}

.usage-scale-labels {
  display: flex;
  justify-content: space-between;
  color: #4C5B64;
  font-size: 12px;
  line-height: 16px;
}
```

This is earned when the colors represent a documented numeric scale, such as consumption intensity or risk. It should not be the only way the user learns the state; labels, values, or patterns should remain available.

## Grain

### When grain is earned

Use grain when the visual stance has a legitimate tactile, analog, printed, photographic, or material reference.

Good fits:

- Editorial brands
- Artisan commerce
- Food, beverage, fragrance, hospitality
- Film, music, and cultural products
- Archival interfaces
- Campaign sites with intentional physicality
- Backgrounds that would otherwise look unnaturally flat or digitally sterile

Poor fits:

- Dense data products
- Forms-heavy enterprise tools
- Medical, financial, legal, or accessibility-critical core workflows
- Small, repetitive UI surfaces where texture creates visual fatigue

Grain should sit **behind content**, remain subtle, and never interfere with reading. It is surface atmosphere, not information.

### Shippable CSS: static SVG noise texture

```css
.textured-surface {
  position: relative;
  background: #F4EEE4;
  isolation: isolate;
}

.textured-surface::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.055;
  mix-blend-mode: multiply;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.78' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.85'/%3E%3C/svg%3E");
  background-size: 180px 180px;
}

.textured-surface > * {
  position: relative;
  z-index: 1;
}

@media (prefers-contrast: more) {
  .textured-surface::after {
    display: none;
  }
}
```

### Practical values

- Opacity: `0.025–0.08` for backgrounds
- Do not animate the noise
- Use a fixed repeated tile, generally `128px–256px`
- Use only on a page or major section — not on every card
- Disable it in high-contrast contexts

## Glow

### When glow is earned

Use glow to communicate **energy, activation, focus, liveness, or depth**, not just to make controls feel futuristic.

Good fits:

- A selected object in a visual workspace
- A live-recording indicator
- Music/audio tools
- Developer or infrastructure monitoring with a meaningful active signal
- Gaming, social, or expressive consumer tools
- A focused object in a dark, immersive interface
- A visual brand with emitted-light material logic

Poor fits:

- Every CTA
- Every dashboard metric
- Default form inputs
- Serious high-density tools with no luminous visual metaphor
- Multiple different glow colors competing for attention

### Shippable CSS: selected "live" control

```css
.live-control {
  color: #F8FAFC;
  background: #263A82;
  border: 1px solid rgb(161 180 255 / 72%);
  border-radius: 10px;
  box-shadow:
    inset 0 1px 0 rgb(255 255 255 / 14%),
    0 0 0 1px rgb(92 111 255 / 18%),
    0 0 18px rgb(92 111 255 / 26%),
    0 0 42px rgb(92 111 255 / 14%);
  transition:
    background-color 160ms cubic-bezier(0.2, 0, 0, 1),
    border-color 160ms cubic-bezier(0.2, 0, 0, 1),
    box-shadow 160ms cubic-bezier(0.2, 0, 0, 1);
}

.live-control:focus-visible {
  outline: 3px solid #F4C95D;
  outline-offset: 3px;
}
```

Glow remains an enhancement; the selected state is also clear through fill, label, border, and focus behavior.

## Organic shapes

### When organic forms are earned

Use organic shapes when they relate to the product's subject matter or stance:

- Wellness, movement, creativity, youth, food, biology, gardening, ecology
- A brand with soft, human, handmade, playful, or fluid identity
- An onboarding or campaign experience that needs a compositional counterweight
- A visual system derived from natural forms, collage, or physical materials

Avoid them in:

- Precision systems
- Serious operator dashboards
- Products where geometry communicates reliability and exactness
- Interfaces where organic forms would compete with dense content

The important distinction is between a **designed organic form** and a random CSS blob added to an empty hero.

### Shippable CSS: deliberate organic backdrop

```css
.organic-field {
  position: absolute;
  width: 420px;
  aspect-ratio: 1;
  right: -110px;
  top: 48px;
  pointer-events: none;
  opacity: 0.9;
  background:
    radial-gradient(circle at 28% 30%, #FFE5A7 0 14%, transparent 14.5%),
    radial-gradient(circle at 68% 72%, #BCE8D7 0 20%, transparent 20.5%),
    #CFC3FF;
  border-radius: 58% 42% 51% 49% / 42% 55% 45% 58%;
  transform: rotate(-12deg);
}

@media (max-width: 700px) {
  .organic-field {
    width: 260px;
    right: -104px;
    top: 76px;
    opacity: 0.58;
  }
}
```

This is appropriate behind a single onboarding message in a playful habit app because it provides a stable visual identity and frames the content. It would be inappropriate behind every dashboard panel.

### Shippable SVG: controlled organic path

For a brand illustration or a hero composition, prefer an explicit SVG path over unpredictable random generation:

```svg
<svg
  viewBox="0 0 560 500"
  fill="none"
  xmlns="http://www.w3.org/2000/svg"
  aria-hidden="true"
>
  <path
    d="M116 82C192 5 337 25 422 96C506 166 504 292 426 378C350 462 200 481 112 404C21 324 40 159 116 82Z"
    fill="#CFC3FF"
  />
  <path
    d="M204 102C247 75 316 86 353 127C390 167 379 229 337 267C295 305 224 314 181 276C137 238 161 129 204 102Z"
    fill="#FFE5A7"
  />
</svg>
```

The shape is chosen and reviewable. It is not random decoration generated by code at runtime.

## Displacement and refraction

### When displacement/refraction is earned

This is the most specialized category. Use it only when the product's visual model is explicitly immersive or material:

- A spatial or visual creative tool
- A media experience
- A high-end campaign or editorial site
- A weather, water, optics, glass, or scientific visualization context
- A product whose brand identity explicitly uses liquid, lens, prism, or refractive materials
- A highly controlled hero/transition — not core transactional UI

Do not use it for ordinary cards, forms, tables, or navigation. It can be expensive, visually distracting, and difficult to make accessible.

### Shippable SVG: subtle static liquid-glass refraction

```svg
<svg
  width="0"
  height="0"
  aria-hidden="true"
  focusable="false"
  xmlns="http://www.w3.org/2000/svg"
>
  <filter id="liquid-glass" x="-20%" y="-20%" width="140%" height="140%">
    <feTurbulence
      type="fractalNoise"
      baseFrequency="0.012 0.018"
      numOctaves="2"
      seed="18"
      result="noise"
    />
    <feDisplacementMap
      in="SourceGraphic"
      in2="noise"
      scale="7"
      xChannelSelector="R"
      yChannelSelector="G"
    />
  </filter>
</svg>
```

```css
.liquid-glass-art {
  border-radius: 28px;
  overflow: hidden;
  filter: url("#liquid-glass");
  transform: translateZ(0);
}
```

Use this on a **non-essential hero artwork or visual ornament**, not on text or an interactive control. Distorting text harms legibility and distorting controls can make hit targets feel disconnected from their visual boundaries.

### More practical alternative: CSS glass, not true refraction

For most product UI, a conventional translucent surface with backdrop blur is preferable:

```css
.prismatic-sheet {
  background:
    linear-gradient(
      140deg,
      rgb(255 255 255 / 74%) 0%,
      rgb(190 219 255 / 36%) 42%,
      rgb(238 205 255 / 32%) 100%
    );
  border: 1px solid rgb(255 255 255 / 66%);
  box-shadow:
    inset 0 1px 0 rgb(255 255 255 / 58%),
    0 18px 44px rgb(37 38 74 / 16%);
  -webkit-backdrop-filter: blur(20px) saturate(145%);
  backdrop-filter: blur(20px) saturate(145%);
}
```

This produces a legible, stable glass-like surface without distorting the content behind it.

## SVG filter primitives: positions

SVG filters are legitimate tools. The important question is not whether they are "allowed"; it is whether they are serving the interaction and visual system without harming performance, accessibility, or maintainability.

### `feTurbulence`

**Yes, usually static only.**
Useful for subtle grain, paper texture, cloud-like visual fields, or a background material.

```svg
<filter id="paper-grain">
  <feTurbulence
    type="fractalNoise"
    baseFrequency="0.72"
    numOctaves="3"
    stitchTiles="stitch"
    seed="24"
  />
  <feColorMatrix
    type="matrix"
    values="
      0 0 0 0 0.18
      0 0 0 0 0.15
      0 0 0 0 0.12
      0 0 0 0.13 0
    "
  />
</filter>
```

Use it as a background-only texture at low opacity. Do not animate it continuously in standard UI.

### `feDisplacementMap`

**Rarely, and only for non-essential artwork.**
Useful for a static refractive hero illustration, water-like distortion, or a highly specific campaign effect.

```svg
<filter id="soft-displace" x="-10%" y="-10%" width="120%" height="120%">
  <feTurbulence
    type="turbulence"
    baseFrequency="0.01"
    numOctaves="2"
    seed="11"
    result="texture"
  />
  <feDisplacementMap
    in="SourceGraphic"
    in2="texture"
    scale="5"
    xChannelSelector="R"
    yChannelSelector="B"
  />
</filter>
```

Do **not** put displacement filters on body text, navigation, primary buttons, tables, or anything whose visual boundary must remain exact.

### `feGaussianBlur` + `feColorMatrix` for "goo"

**Very rarely.**
This can work in a playful, expressive consumer experience — such as a single animated completion illustration, a nonessential loading motif, or a campaign graphic. It is usually too loud and too computationally expensive for product UI.

```svg
<svg
  viewBox="0 0 320 140"
  xmlns="http://www.w3.org/2000/svg"
  aria-hidden="true"
>
  <defs>
    <filter id="goo" color-interpolation-filters="sRGB">
      <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
      <feColorMatrix
        in="blur"
        mode="matrix"
        values="
          1 0 0 0 0
          0 1 0 0 0
          0 0 1 0 0
          0 0 0 22 -9
        "
        result="goo"
      />
      <feComposite in="SourceGraphic" in2="goo" operator="atop" />
    </filter>
  </defs>

  <g filter="url(#goo)">
    <circle cx="96" cy="70" r="36" fill="#7E6BEA" />
    <circle cx="156" cy="70" r="36" fill="#FFB94D" />
    <circle cx="216" cy="70" r="36" fill="#82D7B2" />
  </g>
</svg>
```

This would be an illustration, not a structural component style.

### `feSpecularLighting`

**Almost never for interface components.**

It can create a convincing embossed, wet, or lit material, but it is difficult to control across displays, can make text harder to read, and often looks like a novelty effect when applied to UI chrome.

It might work for:

- A one-off 3D-ish badge or seal
- A decorative product visualization
- A game or music visualizer
- A non-interactive hero material study

Do not use it for buttons, cards, inputs, or navigation.

```svg
<filter id="soft-specular" x="-20%" y="-20%" width="140%" height="140%">
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
```

### `feDropShadow`

**Yes, commonly — but gently.**
For SVG icons, marks, floating objects, and illustrations, it can be better than trying to fake a shadow with duplicate paths.

```svg
<filter id="icon-shadow" x="-30%" y="-30%" width="160%" height="160%">
  <feDropShadow
    dx="0"
    dy="5"
    stdDeviation="5"
    flood-color="#172033"
    flood-opacity="0.18"
  />
</filter>
```

Use one coherent shadow, not stacks of several unrelated effects.

## Worked contrasts

### An effect that improved a design: mobile video-editing workspace

The app's main surface is a live video preview. The timeline, inspector, and transport controls need to overlay it without severing the user's connection to the visual content.

**Before: opaque utility slab**

```css
.transport-controls {
  position: absolute;
  right: 16px;
  bottom: 16px;
  width: min(360px, calc(100vw - 32px));
  padding: 12px;
  color: #F8FAFC;
  background: #15202B;
  border: 1px solid #314152;
  border-radius: 16px;
}
```

Why it was weaker: the controls feel detached from the video canvas, the solid panel creates a heavy black slab, it hides too much of the preview, and the composition reads as "a dashboard placed over a video," not one spatial workspace.

**After: glass transport surface**

```css
.transport-controls {
  position: absolute;
  right: 16px;
  bottom: 16px;
  width: min(360px, calc(100vw - 32px));
  padding: 12px;
  color: #F8FAFC;

  background:
    linear-gradient(
      135deg,
      rgb(17 27 40 / 76%) 0%,
      rgb(17 27 40 / 58%) 100%
    );
  border: 1px solid rgb(226 232 240 / 24%);
  border-radius: 16px;
  box-shadow:
    inset 0 1px 0 rgb(255 255 255 / 10%),
    0 14px 32px rgb(0 0 0 / 24%);

  -webkit-backdrop-filter: blur(18px) saturate(125%);
  backdrop-filter: blur(18px) saturate(125%);
}

.transport-controls:focus-within {
  border-color: rgb(148 201 255 / 72%);
}
```

Why the glass is earned here: there is meaningful, changing visual content beneath it, the blur preserves the spatial relationship with the preview, the surface remains opaque enough for controls and labels to be legible, the panel is a localized, floating utility object — not a default treatment applied to every UI region — and a solid fallback still works.

### An effect to remove: B2B delivery-performance dashboard

The interface includes order metrics, late-delivery exceptions, and a dense operations table.

**Before: decorative animated gradient behind the dashboard**

```css
.dashboard-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at 20% 10%, #B2A4FF 0%, transparent 35%),
    radial-gradient(circle at 80% 20%, #7BE7D0 0%, transparent 38%),
    linear-gradient(135deg, #F5F3FF, #E7F9F5);
  background-size: 160% 160%;
  animation: drift 12s ease-in-out infinite alternate;
}

@keyframes drift {
  from { background-position: 0% 0%; }
  to { background-position: 100% 100%; }
}
```

Why it is arbitrary: the product is operational and data-dense, so the gradient adds no semantic information; it lowers the perceived seriousness and clarity of alerts and metrics; it creates subtle contrast variation behind white cards; animation consumes attention without communicating a state change; and it makes the same dashboard feel closer to a marketing page than a working tool.

**After: stable precision surface**

```css
.dashboard-shell {
  min-height: 100vh;
  background: #F4F6F7;
}

.dashboard-grid {
  background-image:
    linear-gradient(rgb(22 32 36 / 4%) 1px, transparent 1px),
    linear-gradient(90deg, rgb(22 32 36 / 4%) 1px, transparent 1px);
  background-size: 32px 32px;
  background-position: -1px -1px;
}

.dashboard-panel {
  background: #FFFFFF;
  border: 1px solid #C7D0D2;
  border-radius: 6px;
  box-shadow: none;
}
```

Why removing the effect improved the design: the page becomes calmer and easier to scan, metrics and alerts regain visual priority, the subtle grid supports the "operational system" stance without competing with content, the product feels more trustworthy and less decorative, and the visual treatment now has a role — it reinforces measurement, structure, and precision.

## The three questions

Use rich material effects when the design has a real answer to all three questions:

1. **What does this effect mean in this product?**
2. **Why is it placed on this surface rather than everywhere?**
3. **What remains if the effect is unsupported, reduced, or removed?**

If the answers are strong, glass, grain, gradients, glow, organic forms, and even carefully controlled SVG filters can produce an excellent, sophisticated interface.

If the answers are weak, the same effects become generic visual noise.

---

This policy is deliberately conservative. A companion skill for SVG-filter material design extends it where the product genuinely earns richer materials.
