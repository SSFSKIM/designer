# SVG Filter Capability Atlas for UI Design

**Purpose.** Raw research for an Agent Skill that teaches coding agents to use SVG filters as a design material for sophisticated modern UI: Apple-Liquid-Glass-class refraction, gooey/organic effects, grain/texture, and lighting. Audience: an LLM agent that writes HTML/CSS/SVG.

**Verification status.** Compiled 2026-07-22. Browser-support claims were checked against 2025–2026 sources (WebKit Bugzilla, Mozilla Bugzilla, MDN BCD issues, the kube.io Liquid Glass article, and multiple 2025 Liquid Glass implementations). Anything not verified against a current source is marked **[uncertain]**. See §6 Uncertainty Ledger.

---

## 0. Mental model: how an SVG filter actually runs

Before the primitive atlas, the five facts that explain almost every surprise:

### 0.1 The pipeline (in / result chaining)

A `<filter>` is a directed graph of primitives. Each primitive:

- reads one input (`in`; some take a second, `in2`),
- writes an intermediate raster, optionally named via `result="name"`.

Valid `in` values: `SourceGraphic` (the element, rasterized, RGBA), `SourceAlpha` (its alpha channel only — black silhouette), any earlier `result` name, or (legacy, **do not use**) `BackgroundImage` / `BackgroundAlpha` / `FillPaint` / `StrokePaint` — these SVG 1.1 keywords were never interoperably implemented and were dropped from the Filter Effects Module Level 1 spec; `backdrop-filter` is the modern replacement for `BackgroundImage`.

Defaulting rules (memorize — they make short filters readable):

- First primitive with no `in` → `SourceGraphic`.
- Any later primitive with no `in` → the **result of the previous primitive**, whether or not it was named.
- `result` names are scoped to the filter and can be reused (last write wins).
- The output of the **last** primitive is the filter output.

### 0.2 The filter region

The filter renders into an offscreen surface whose size is the *filter region*:

- Defaults: `x="-10%" y="-10%" width="120%" height="120%"`, with `filterUnits="objectBoundingBox"` — i.e. 10% padding around the element's bounding box.
- Anything the filter draws outside this region is **hard-clipped**. Big blurs, long shadows, large displacement `scale`, and dilated outlines all get chopped by the default region. Fix by enlarging: `x="-50%" y="-50%" width="200%" height="200%"` (or absolute units with `filterUnits="userSpaceOnUse"`).
- `primitiveUnits` (default `userSpaceOnUse`) controls how *attribute values inside primitives* (e.g. `stdDeviation`, `baseFrequency`, `radius`, `dx/dy`) are interpreted. With `primitiveUnits="objectBoundingBox"` they become fractions of the bbox — occasionally useful for size-independent filters, but support/precision is flakier; most production filters keep the default.
- Each primitive can also take its own `x/y/width/height` subregion (used heavily by `feTile` and `feImage`).
- Zero-area bounding boxes (a horizontal `<line>`, an empty `<g>`) make `objectBoundingBox` filter regions collapse → the element disappears. Use `filterUnits="userSpaceOnUse"` for lines/paths with zero width or height.

When the filter is applied to an **HTML element** via CSS `filter: url(#id)`, the "bounding box" is the element's border box, and one user unit = 1 CSS px with the origin at the border box's top-left (Filter Effects spec behavior).

### 0.3 The color-space gotcha: `color-interpolation-filters`

Per spec, filter math runs in **linearRGB** by default (unlike CSS shorthand filter functions like `blur()`, which are defined to operate in sRGB). Consequences:

- Turbulence "gray" noise, displacement-map grays, and blur falloff all look different than the sRGB values you authored: mid-gray 128 in your PNG is *not* the neutral value once converted to linearRGB.
- A displacement map encoded around 128 = "no shift" **only behaves correctly if the filter runs in sRGB**.
- Browsers disagree historically: Firefox honors `color-interpolation-filters` faithfully; WebKit/Safari has long tended to compute in sRGB regardless (see fxtf-drafts #113 discussion: "Firefox takes the output as being whatever colour space is defined by color-interpolation-filters, while Opera and Safari assume it is sRGB").

**Rule for the Skill:** put `color-interpolation-filters="sRGB"` on every `<filter>` (attribute on the filter element, or CSS `color-interpolation-filters: sRGB`). It makes results match the colors you authored, and it's the only setting that behaves the same in all engines. Only deliberately use linearRGB when you want physically-correct light blending (lighting primitives can look better in linearRGB — but accept Safari divergence).

### 0.4 Premultiplied alpha

Intermediates are stored premultiplied; primitives that need straight RGBA (feColorMatrix, feComponentTransfer, feDisplacementMap channel reads) un-premultiply first per spec. Practical fallout: fully transparent pixels have *undefined* RGB, so a displacement map with transparent regions displaces unpredictably — always make displacement maps fully opaque (`a=255`), and be suspicious of color fringes at anti-aliased edges after aggressive alpha-matrix operations.

### 0.5 What applying a filter does to the element

- The element (and descendants) is rasterized as a group first; the filter sees pixels, not vectors.
- In CSS, `filter` (and `backdrop-filter`) on an element creates a **stacking context** and — a classic gotcha — makes the element a **containing block for `position: fixed` and `position: absolute` descendants**. A `position: fixed` modal inside a filtered ancestor scrolls with the page.
- Filters flatten 3D: `transform-style: preserve-3d` in the subtree stops working.
- `filter="url(#nonexistent)"` on an SVG element makes the element **invisible** (invalid filter reference = render nothing) in most engines; CSS `filter: url(#missing)` on HTML is treated as no filter in modern engines per Filter Effects spec, but historically inconsistent — never ship dangling references.
- The `<svg>` hosting your `<filter>` defs must be renderable: `display: none` on it breaks filter resolution in some engines. Hide it with `width="0" height="0" style="position:absolute"` and `aria-hidden="true"` instead.
- SPA gotcha: `url(#id)` is resolved against the document base URL. If the page has a `<base href>` (common with SPA routers), fragment-only references can resolve against the base URL and silently break. Fix: absolute-URL the reference (`url(/current/path#id)`), or remove `<base>`.

---

## 1. Primitive atlas

Every primitive in Filter Effects Level 1 / SVG 1.1, with UI-relevant parameter ranges. All are supported in current Chrome, Firefox, and Safari unless noted (quirks in §4).

### 1.1 `feGaussianBlur`

True Gaussian blur (spec allows triple-box approximation).

- `stdDeviation`: one number, or two (`x y`) for **anisotropic blur** — `stdDeviation="8 0"` is a horizontal motion-blur; `"0 8"` vertical. Ranges: `0.5–2` softening/AA, `3–6` soft shadows, `8–15` gooey pre-blur, `15–40` frosted glass backdrops.
- `in="SourceAlpha"` + offset + flood = the classic hand-rolled drop shadow.
- `edgeMode` (`duplicate | wrap | none`) is in the Filter Effects spec for blur/convolve; **[uncertain]** interop for feGaussianBlur — don't depend on it.
- Cost scales with region area and stdDeviation; it's the most GPU-optimized primitive (Chromium runs it on GPU).

### 1.2 `feOffset`

Shifts the input by `dx`, `dy` (user units; can be negative and fractional). Free. Building block for shadows, letterpress (offset SourceAlpha then `composite out`), and chromatic aberration (offset R/G/B channel-isolated copies by ±1–3px then re-merge).

### 1.3 `feFlood`

Fills the primitive subregion with `flood-color` + `flood-opacity`. Free. Used to colorize alpha shapes (`flood` → `composite in` with a silhouette), tint layers, and debug (flood a subregion to *see* it).

### 1.4 `feImage`

Injects an external raster/SVG as a layer. Key attributes: `href`, `x/y/width/height` (placement in the region), `preserveAspectRatio` (default `xMidYMid meet`).

- **Portable usage: data-URI raster images** (`href="data:image/png;base64,…"`). This is what production Liquid Glass implementations do for displacement maps.
- Referencing a *local element fragment* (`href="#someRect"`) is **not interoperable**: works in Chrome/Safari-ish, not Firefox (Bugzilla 455986, 1538554), with sizing disagreements between all three (fxtf-drafts #113). Avoid.
- Cross-origin images without CORS taint the filter → filter fails or renders nothing. Use same-origin or data URIs.
- Sizing quirk: when used inside filters applied to HTML, explicit `x/y/width/height` on `feImage` is effectively mandatory; the natural-size default differs across engines. **[uncertain]** exact per-engine default behavior — always size explicitly.

### 1.5 `feTile`

Tiles the *input's primitive subregion* across the feTile's subregion. The pattern-maker: draw one halftone dot / hatch cell with a small-subregion `feImage` or flood/composite combo, then `feTile` it across the element. Historic Safari bugs with feTile+feImage combos **[uncertain]** in current Safari — test.

### 1.6 `feMerge` / `feMergeNode`

Stacks any number of named results with normal (source-over) compositing; **last `feMergeNode` = topmost**. Zero-math layering. `feBlend mode="normal"` or `feComposite over` do the same for exactly two layers.

### 1.7 `feBlend`

Two-input blending. `mode`: SVG 1.1 gave `normal | multiply | screen | darken | lighten`; Filter Effects 1 extends to the full CSS blend-mode set (`overlay`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color`, `luminosity`) — supported in current engines (verify `hue/saturation/color/luminosity` in Safari if load-bearing **[uncertain]**).

- `screen` = add light (specular highlights over glass); `multiply` = add shadow/ink; `soft-light`/`overlay` = grain overlays.

### 1.8 `feComposite`

Porter–Duff compositing plus arithmetic. `operator`: `over | in | out | atop | xor | arithmetic`.

- `in`: keep input1 only where input2 is opaque → **masking** (colorize silhouettes, clip texture to a shape).
- `out`: keep input1 where input2 is transparent → **ring/outline** (dilated silhouette `out` original), inner shadows (offset alpha `out` original).
- `atop`: input1 drawn only over input2's alpha, input2 elsewhere → the gooey "keep children crisp" trick.
- `arithmetic`: `result = k1·i1·i2 + k2·i1 + k3·i2 + k4` per channel. This is the general-purpose mixer: `k2 k3` cross-fade two layers; `k1=1` multiply (apply a light map); `k4` lift. It's also how lyra.horse builds logic gates — feComposite+feBlend are Turing-complete.

### 1.9 `feColorMatrix`

5×4 matrix on straight RGBA. `type`:

- `matrix` — 20 values, rows = output R,G,B,A; columns = input R,G,B,A,1 (last column is a constant offset in 0–1 units).
- `saturate` — `values="0"` grayscale … `1` identity (values >1 oversaturate).
- `hueRotate` — degrees; fast but non-perceptual (a luminance-preserving approximation; reds/blues shift brightness).
- `luminanceToAlpha` — luma → alpha, RGB → 0. Turns any image into a mask (halftone input, lighting bump sources).

The single most important UI trick lives in the **alpha row**: `0 0 0 N -K` maps alpha `a → N·a − K`, i.e. a contrast-threshold on alpha. With a blur upstream this converts soft alpha into a hard blob edge (gooey, §2.2), rounds corners, and cleans fringes.

### 1.10 `feComponentTransfer` + `feFuncR/G/B/A`

Per-channel transfer functions — the "curves" tool. Each `feFunc*` has `type`:

- `identity` (default)
- `linear` — `slope`, `intercept`: `C' = slope·C + intercept`. Contrast/brightness per channel; `feFuncA slope="0.5"` halves opacity.
- `gamma` — `amplitude`, `exponent`, `offset`: `C' = amp·C^exp + off`. Midtone shaping.
- `table` — `tableValues="v0 v1 … vn"`: piecewise-linear remap; input 0→v0, 1→vn. **Duotone/tritone**: after grayscaling, set each channel's table to interpolate between shadow-color and highlight-color components (§2.8).
- `discrete` — step function, n equal bands: **posterize** (`tableValues="0 .25 .5 .75 1"` per channel → 5 levels) and **thresholding** (`tableValues="0 1"` on alpha or luma) for halftone/print looks.

### 1.11 `feMorphology`

Minimum (`erode`) / maximum (`dilate`) filter over a rectangle. `operator`, `radius` (one or two values, x y).

- `dilate` radius `1–4`: outlines, sticker borders, bolding thin glyphs.
- `erode` radius `0.5–2`: thin text, grunge-eat shapes (combine with turbulence displacement for eroded edges).
- The structuring element is a **box**, so radius ≳ 4–5 makes rounded shapes go chunky/square — for fat clean outlines prefer blur→alpha-threshold (blur + `feColorMatrix 0 0 0 N -K`) which stays round.
- Cost grows with radius (naively O(r²) per pixel); keep radii small.

### 1.12 `feConvolveMatrix`

General convolution. `order` (kernel size, e.g. `3`), `kernelMatrix` (row-major), `divisor` (default = sum of kernel, or 1 if sum is 0), `bias`, `targetX/Y`, `edgeMode` (`duplicate` default), `preserveAlpha` (`true` = convolve RGB only — usually what you want to avoid alpha fringes).

- Sharpen: `0 -1 0 -1 5 -1 0 -1 0`.
- Emboss: `-2 -1 0 -1 1 1 0 1 2` (combine with grayscale for classic relief).
- Edge detect: `-1 -1 -1 -1 8 -1 -1 -1 -1` (then threshold → sketch outlines).
- `kernelUnitLength` was removed/never interoperable — kernels are **device/user-pixel based**, so results vary with zoom/DPR. Expensive: order² multiplies per pixel; keep to 3×3 and small regions.

### 1.13 `feDisplacementMap`

The refraction primitive. Moves each pixel of `in` by an offset read from `in2` (the map):

```
P'(x,y) = P( x + scale · (XC(x,y) − 0.5),  y + scale · (YC(x,y) − 0.5) )
```

- `scale`: max displacement in user px (channel value 0 → −scale/2… actually 0→−0.5·scale, 255→+0.5·scale; neutral 128 ≈ 0). Ranges: `5–20` subtle refraction/wobble, `20–80` visible liquid-glass lensing, `100+` heavy distortion.
- `xChannelSelector`, `yChannelSelector`: `R|G|B|A` (default `A` — almost never what you want; set explicitly, conventionally `R`/`G`).
- It's a *gather* operation (reads source at displaced position), so the visual effect is the **inverse** of the encoded vector — kube.io accounts for this by encoding displacement as "where to sample from".
- **Must** pair with `color-interpolation-filters="sRGB"`, or your 128-neutral map is converted to linearRGB and everything drifts (§0.3).
- Map with transparency = undefined displacement (premultiplied alpha, §0.4) — keep maps opaque.
- `scale` is cheaply animatable (CSS/JS/SMIL) without rebuilding the map — this is how Liquid Glass hover/press states animate.
- Interop wart (fxtf-drafts #113): browsers disagree on subtleties (alpha handling of the map, output color space); solid opaque sRGB maps + explicit channel selectors is the portable subset.

### 1.14 `feTurbulence`

Procedural Perlin noise generator (ignores `in`; it's a source).

- `type`: `fractalNoise` (smooth, cloudy, values fill 0–1 — use for grain, clouds, paper, displacement fields) vs `turbulence` (default; abs-value ridged noise, darker, veiny — water caustics, marble, energy).
- `baseFrequency`: one value or two (`x y`) for anisotropic noise (e.g. `0.01 0.15` = horizontal streaks → brushed metal, wood grain). Meaningful ranges: `0.001–0.01` big soft waves (liquid distortion fields), `0.02–0.2` organic texture, `0.5–1.0` fine film grain (`0.65–0.9` typical for UI grain).
- `numOctaves`: detail layers, `1–5`. Each octave roughly doubles cost; >4 rarely visible. Grain: 2–4. Displacement fields: 1–2.
- `seed`: any number; changes the pattern. Discrete parameter — animating it *jumps* (which is exactly what squigglevision wants, §2.4).
- `stitchTiles="stitch"`: makes the noise tile seamlessly across the primitive subregion — essential for small tiled grain textures.
- Output is 4 independent noise channels (R,G,B,A) — a displacement consumer can read R for X and G for Y "for free". Note the alpha channel is noise too: raw turbulence is semi-transparent noise, which is why grain recipes often pipe through `feComponentTransfer`/`feColorMatrix` to shape alpha.
- **The most expensive primitive**: computed per-pixel on CPU in common paths; large animated turbulence maxes cores (reported repeatedly in 2025 threads). Prefer *static* turbulence, small regions, or bake to a tile.

### 1.15 `feDropShadow`

Shorthand for offset+blur+flood+composite+merge: `dx`, `dy`, `stdDeviation`, `flood-color`, `flood-opacity`. Cheaper to author than the manual chain, same cost to run. Unlike CSS `drop-shadow()`, it can sit *mid-chain* (e.g. shadow a gooey blob after threshold). Supported everywhere current.

### 1.16 `feDiffuseLighting` / `feSpecularLighting` + light sources

Lighting from a **height map**: the input's *alpha channel* is treated as a bump map (`surfaceScale` = height of alpha=1 in user px, default 1; can be negative to invert). Both compute per-pixel normals from that height field.

- `feDiffuseLighting`: matte light. `diffuseConstant` (kd, ≥0, default 1; 0.5–1.5 typical). Output is opaque RGB (light map) — combine with source via `feComposite arithmetic k1=1` (multiply) or `feBlend multiply`.
- `feSpecularLighting`: highlights. `specularConstant` (ks, 0.2–2), `specularExponent` (shininess 1–128: 5–10 soft sheen, 20–40 wet/glossy, 60–128 hard glassy pinpoints). Output has RGB = highlight and alpha = max(R,G,B), designed to be composited **over** the source (`feComposite operator="over"` / merge on top).
- `lighting-color`: the light's color (default white).
- Exactly one child light source:
  - `feDistantLight` — `azimuth` (deg in-plane; 225 ≈ light from top-left), `elevation` (deg above surface; 40–70 typical). Even lighting for embossing.
  - `fePointLight` — `x y z` position in user space (z = distance above; larger z = softer, broader). Local hotspot; move it with JS for cursor-tracking sheen.
  - `feSpotLight` — point + `pointsAtX/Y/Z`, `limitingConeAngle` (deg), own `specularExponent` (beam focus). Dramatic; cone edge is hard/aliased in some engines **[uncertain]** current smoothing behavior.
- Classic recipes: turbulence→lighting = embossed paper/stucco; blur(SourceAlpha)→specular→over = wet button/glass rim; see §2.5.
- Cost: similar class to convolution (per-pixel normal estimation) — medium-heavy; fine when static.

---

## 2. Recipe families for distinguished modern UI

Working sketches, tuned parameter guidance, and where each look belongs. All snippets assume the def-hosting SVG is inline, hidden (`width="0" height="0" position:absolute`), with `color-interpolation-filters="sRGB"` unless stated.

### 2.1 Liquid glass / refraction — the kube.io method (north star)

Reference: **kube.io/blog/liquid-glass-css-svg/** (studied in depth; the canonical physics-grounded web implementation of Apple's WWDC-2025 Liquid Glass).

**Core idea:** don't displace with noise — displace with a **computed lens profile**. Build a displacement map whose R/G channels encode, per pixel, where the "glass" refracts light from, derived from Snell's law (air n=1 → glass n=1.5), then run `feDisplacementMap` over the backdrop.

**Map encoding** (32-bit RGBA):

- R = X shift, G = Y shift, B ignored, A = 255. Neutral = 128 (`0→−1, 128→0, 255→+1` after `(v−0.5)·2`).
- Vectors are **normalized** so max magnitude = 1; the real max displacement in px becomes the filter's `scale`. This lets you animate `scale` (hover/press "melt") without regenerating the map.

```js
// per-pixel encode
const x = Math.cos(angle) * magnitude, y = Math.sin(angle) * magnitude;
rgba = { r: 128 + x * 127, g: 128 + y * 127, b: 128, a: 255 };
```

**Lens profiles** (surface height y as a function of distance x from the edge, both normalized):

- Convex circle: `y = √(1−(1−x)²)` — harsh edge transition when stretched.
- **Convex squircle** (Apple's look): `y = (1−(1−x)⁴)^(1/4)` — smooth flat-to-curve transition; "the bezel appears optically thinner than its physical size".
- Concave: `1 − convex(x)` — bowl; diverges light outward.
- Lip: `mix(convex, concave, smootherstep(x))` — raised rim with a shallow center dip (closest to iOS 26 controls).

Surface normal via finite differences (`derivative of the profile, rotated −90°`), then Snell → exit ray → intersection with backdrop plane → displacement vector. Displacement is radially symmetric around the edge, so compute a 1-D profile once and sweep it around the rounded-rect bezel.

**Filter chain:**

```html
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <filter id="liquid-glass" color-interpolation-filters="sRGB"
          x="0" y="0" width="100%" height="100%">
    <feImage href="data:image/png;base64,…MAP…" x="0" y="0"
             width="240" height="120" result="map"/>
    <feDisplacementMap in="SourceGraphic" in2="map"
        scale="60" xChannelSelector="R" yChannelSelector="G" result="refracted"/>
    <!-- optional: specular rim, a second feImage baked from surface normals -->
    <feImage href="data:image/png;base64,…SPECULAR…" x="0" y="0"
             width="240" height="120" result="spec"/>
    <feBlend in="refracted" in2="spec" mode="screen"/>
  </filter>
</svg>

<style>
.glass { backdrop-filter: url(#liquid-glass); border-radius: 32px; }
</style>
```

Notes from the article:

- The specular layer is "the most creative part" — a baked rim-light image (normal · light direction), tuned by opacity/saturation/blur; blended `screen`/`plus-lighter` over the refracted backdrop.
- Filter dimensions do **not** auto-track element size: the `feImage` must match the element's pixel size; every resize forces a map rebuild (the article flags this as the main cost — "nearly every tweak besides animating filter props like scale forces a full displacement map rebuild").
- `backdrop-filter: url(...)` is **Chromium-only today** (§3.2). Cross-browser fallback: layered `backdrop-filter: blur()+saturate()` glassmorphism.

**Other 2025–2026 implementations worth mining:**

- *Specy* — "Liquid Glass in the Browser" (specy.app/blog/posts/liquid-glass-in-the-web + Medium mirror): same displacement idea, notes the 8-bit map limits shifts to ±127px per axis, and that plain SVG displacement applies uniform bending unless you precompute physics per-pixel (JS canvas → data URI).
- *samasante/liquid-glass* (GitHub): headless React "lens" that avoids `backdrop-filter: url()` entirely — it applies `filter: url(...)` to a **clone of the live DOM** behind the lens, so refraction works in Safari/Firefox/Chrome. The portable-but-heavier architecture.
- *nikdelvin/liquid-glass* (GitHub): "pixel-perfect iOS 26" CSS+SVG components (containers, text, buttons).
- *Ekino France* (Medium) and *LogRocket* tutorials: turbulence-based approximations — `feTurbulence (baseFrequency≈0.001–0.01) → feGaussianBlur → feDisplacementMap scale≈70–150` gives a wobbly-glass look without computing a lens; cheaper to author, less "Apple".
- Standards: **w3c/svgwg issue #1142** proposes an interoperable backdrop displacement/refraction mechanism for exactly this use case — track it.

**Cheap static approximation** (no JS, good enough for many cards): encode the lens as two overlapping linear/radial gradients in an inline SVG data-URI (red horizontal ramp, green vertical ramp, flat 128 center) and use that as the map — refraction only at edges, neutral center. Several FreeFrontend/CodePen demos use this.

### 2.2 Gooey / metaball

Reference: CSS-Tricks "The Gooey Effect" (Lucas Bebber); Codrops "Creative Gooey Effects".

```html
<filter id="goo" color-interpolation-filters="sRGB">
  <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur"/>
  <feColorMatrix in="blur" type="matrix"
      values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" result="goo"/>
  <feComposite in="SourceGraphic" in2="goo" operator="atop"/>
</filter>
```

**How it works:** blur melts overlapping shapes' alpha into one soft field; the alpha row `N=18, K=-7` re-hardens it: `a' = 18a − 7`.

**Tuning math** (the part agents get wrong):

- Threshold: edge lands where `N·a − K·(scaled) = 0.5`-ish; effectively alpha cutoff ≈ `K/N` (here 7/18 ≈ 0.39). Lower cutoff (raise N or lower K) → blobs merge *sooner/further apart*; higher cutoff → later, tighter goo.
- Edge hardness: transition width ≈ `1/N` in alpha terms — N=18 fairly crisp, N≈10 soft/jelly, N≥30 razor (but aliased).
- Merge distance scales with `stdDeviation`: shapes bridge when their blurred fields overlap above the cutoff — roughly within `~2·stdDeviation·(1 − K/N)` px. Tune stdDeviation for reach, then N/K for edge.
- `21 -7` delays bridging vs `18 -7` (needs more overlap; can flicker during animation) — pick per motion speed.
- Final `feComposite atop` (instead of `feBlend`) redraws crisp originals only where goo exists — keeps icons/text inside blobs sharp. Use plain `feBlend in="SourceGraphic" in2="goo"` when you *want* the melted silhouette only.

**Usage notes:** apply to the **container**, give it bleed padding (blur eats edges), background must be transparent (it's alpha-driven). Side-use: the same blur+threshold rounds sharp corners of arbitrary unions ("squircle-ify" clusters). Resource-intensive on large areas (blur at stdDev 10+ over big regions). Great for: nav dots absorbing each other, loaders, liquid tab indicators, data-viz clustering (Visual Cinnamon's gooey scatter).

### 2.3 Grain / noise texture

References: CSS-Tricks "Grainy Gradients", freeCodeCamp grainy backgrounds, Codrops "Creating Texture with feTurbulence", Frontend Masters "Grainy Gradients".

The workhorse pattern — a **static** self-contained data-URI, no DOM defs needed:

```css
.grain::after {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n' color-interpolation-filters='sRGB'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  opacity: 0.05; mix-blend-mode: overlay;   /* or soft-light */
}
```

Guidance:

- `baseFrequency 0.6–0.9` = film grain; `0.2–0.4` = paper tooth; two values (`0.02 0.4`) = streaks.
- Desaturate for mono grain: add `feColorMatrix type="saturate" values="0"` inside the SVG (colored RGB noise reads as cheap otherwise).
- Opacity `0.03–0.08` over UI; `overlay`/`soft-light` keeps midtones honest, `multiply` darkens (moody), plain alpha on near-white backgrounds.
- To kill banding in gradients (its original purpose): grain layer over the gradient at ~5% is enough.
- `stitchTiles='stitch'` + a 200–400px tile = seamless and cheap; the filter runs **once at paint**, then it's just a cached background texture — this is the performance-safe way to ship turbulence.
- Alternative in-filter grain (when you need grain only inside a shape): `feTurbulence → feColorMatrix(saturate 0) → feComponentTransfer(feFuncA table shaping) → feComposite in SourceAlpha → feBlend soft-light over SourceGraphic`.

### 2.4 Squigglevision / animated displacement

References: CSS-Tricks "Squigglevision" (Greatest CSS Tricks), Camillo Visini "Simulating Hand-Drawn Motion with SVG Filters".

```html
<filter id="squiggle">
  <feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="3"
                seed="0" result="noise"/>
  <feDisplacementMap in="SourceGraphic" in2="noise" scale="4"
                     xChannelSelector="R" yChannelSelector="G"/>
</filter>
```

Animate by **stepping the seed** (2–5 frames at 8–15fps), not by smoothly animating `baseFrequency`:

```js
const f = document.querySelector('#squiggle feTurbulence');
let s = 0; setInterval(() => f.setAttribute('seed', s = (s + 1) % 5), 90);
```

(Or pre-declare 3–4 filters with different seeds and swap `filter:` classes — avoids re-evaluating turbulence parameters mid-frame in some engines.)

- `scale 2–5` = hand-drawn jitter; `10–30` = wobbly jelly; boiling-line look wants low fps (stepped), not 60fps smoothness.
- **Why to usually avoid in product UI:** every seed change re-runs turbulence + displacement over the whole region, on CPU in common paths — sustained multi-core burn and battery drain (2025 reports of feTurbulence "maxing cores"); it defeats layer caching; it's a vestibular-trigger (must gate behind `prefers-reduced-motion`); and it reads as "cartoon", rarely as "premium". Legit uses: brand moments, hero illustrations, loading vignettes — small regions, short durations, reduced-motion fallback to seed=constant.
- SMIL alternative (`<animate attributeName="seed" values="0;1;2;3" dur="0.4s" calcMode="discrete" repeatCount="indefinite"/>`) works without JS; SMIL is supported in current engines but deprecated-ish — fine for demos.

### 2.5 Specular / diffuse lighting — embossed, wet, lit materials

**Embossed paper / stucco** (texture from noise, lit):

```html
<filter id="emboss" color-interpolation-filters="linearRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="5" result="bump"/>
  <feDiffuseLighting in="bump" surfaceScale="2" diffuseConstant="1.1"
                     lighting-color="#fff" result="light">
    <feDistantLight azimuth="235" elevation="55"/>
  </feDiffuseLighting>
  <feComposite in="light" in2="SourceGraphic" operator="arithmetic"
               k1="1" k2="0" k3="0" k4="0"/>   <!-- multiply light onto source -->
  <feComposite in2="SourceAlpha" operator="in"/> <!-- clip to shape -->
</filter>
```

**Wet / glassy rim highlight** (the shape's own alpha as the bump):

```html
<filter id="wet">
  <feGaussianBlur in="SourceAlpha" stdDeviation="4" result="soft"/>
  <feSpecularLighting in="soft" surfaceScale="5" specularConstant="0.9"
                      specularExponent="30" lighting-color="#ffffff" result="spec">
    <fePointLight x="-40" y="-60" z="180"/>
  </feSpecularLighting>
  <feComposite in="spec" in2="SourceAlpha" operator="in" result="specClipped"/>
  <feMerge>
    <feMergeNode in="SourceGraphic"/><feMergeNode in="specClipped"/>
  </feMerge>
</filter>
```

Tuning: pre-blur of SourceAlpha controls bevel width (2–6px); `surfaceScale 3–8` bevel depth; `specularExponent` 20–40 wet plastic, 60+ glass glint. Move the `fePointLight` x/y from JS (`pointerush`) for cursor-tracking sheen on cards — cheap because only light position changes, though it still re-runs the lighting pass per frame over the region (keep regions small). This lighting pass is exactly the "specular" half of Liquid Glass when you can't bake a specular image (§2.1).

Color-space note: lighting looks physically nicer in `linearRGB`, but Safari computes sRGB regardless — decide per project whether cross-engine consistency (force sRGB) beats fidelity.

### 2.6 Edge / outline / morphology tricks

Reference: Codrops "Outline Text with feMorphology" (Sara Soueidan).

**Sticker border** (dilated silhouette in a color, behind the source):

```html
<filter id="sticker" x="-20%" y="-20%" width="140%" height="140%">
  <feMorphology in="SourceAlpha" operator="dilate" radius="3" result="fat"/>
  <feFlood flood-color="white" result="paint"/>
  <feComposite in="paint" in2="fat" operator="in" result="border"/>
  <feMerge><feMergeNode in="border"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
```

- Hollow **outline only**: `feComposite in="border" in2="SourceAlpha" operator="out"` before merging (ring = dilated − original).
- Inner outline: erode instead, `original − eroded`.
- Round fat borders (dilate goes boxy past ~4px): replace feMorphology with `feGaussianBlur stdDeviation="r/2"` + alpha-threshold matrix (`0 0 0 25 -10`) — gooey-style rounding.
- Rough/organic border: insert `feTurbulence + feDisplacementMap scale≈4` on the dilated silhouette before coloring.
- Multi-ring (sticker-on-sticker): repeat dilate at increasing radii, merge back-to-front.
- Letterpress/inset: `feOffset(SourceAlpha, 0 1) → feComposite out SourceAlpha → flood-colorize → merge over source`.

### 2.7 `feColorMatrix` color-grading recipes

All assume `color-interpolation-filters="sRGB"` (values below are authored for sRGB).

- **Duotone** (better via feComponentTransfer): grayscale first, then map:

```html
<filter id="duotone" color-interpolation-filters="sRGB">
  <feColorMatrix type="saturate" values="0"/>
  <feComponentTransfer>
    <feFuncR type="table" tableValues="0.09 0.98"/>  <!-- shadowR highlightR -->
    <feFuncG type="table" tableValues="0.11 0.87"/>
    <feFuncB type="table" tableValues="0.35 0.60"/>
  </feComponentTransfer>
</filter>
```

  (3+ tableValues per channel = tritone; values = channel/255.)
- **Tint via matrix** (single-step duotone-ish): put the target color's ratios in the R,G,B rows' luminance slots.
- **Channel mixer / swap**: identity matrix with rows permuted (R row `0 0 1 0 0` = blue into red) — cheap "alien" grades, chromatic effects when combined with per-channel offsets.
- **Hue-rotate**: `type="hueRotate" values="180"` — fast but non-perceptual (matrix approximation; brightness shifts on saturated colors). For brand-accurate recolors prefer duotone tables.
- **Luminance mask**: `type="luminanceToAlpha"` then composite — e.g. apply grain only to shadows, or drive a halftone.
- **Alpha shaping**: row 4 tricks — `0 0 0 N -K` threshold (goo), `0 0 0 0.5 0` uniform fade mid-chain.
- Note CSS shorthands (`sepia()`, `saturate()`, `hue-rotate()`) are themselves defined as feColorMatrix/feComponentTransfer equivalents (Filter Effects spec) — use CSS shorthands when they suffice (cheaper, interoperable), drop to SVG when you need them **mid-chain**.

### 2.8 Frosted glass vs `backdrop-filter` interplay

The layering that reads "expensive glass" (progressive enhancement ladder):

1. **Base (all browsers):** translucent fill + `backdrop-filter: blur(14px) saturate(1.6) brightness(1.05)`; `-webkit-backdrop-filter` for older Safari. Saturate is the secret — blur alone looks like fog, blur+saturate looks like Apple.
2. **Edge treatment (all):** 1px gradient border (`linear-gradient` on border-box, white 40% → transparent), inset top highlight (`box-shadow: inset 0 1px 0 rgba(255,255,255,.25)`), soft outer shadow.
3. **Texture (all):** §2.3 grain pseudo-element at 3–4% over the panel.
4. **Refraction (Chromium today):** swap/add `backdrop-filter: url(#liquid-glass)` (§2.1). Feature-detect:

```css
@supports (backdrop-filter: url(#x)) { /* Chromium path */ }
```

   **[caveat]** `@supports` validates syntax, not that SVG filters actually apply — Firefox parses `backdrop-filter: url()` but doesn't render SVG filters there **[uncertain: verify Firefox @supports result]**; a tiny runtime canvas probe or UA-class is the robust gate used by liquid-glass libraries.
5. Remember `backdrop-filter` samples the **backdrop root**: an ancestor with its own filter/opacity/transform can change what "behind" means; and the element itself must be (semi)transparent or you'll never see the result.
6. Text on glass: always add a scrim/tint layer for contrast (WCAG doesn't care how pretty the blur is); consider `prefers-contrast: more` → solid background.

### 2.9 Paper / print effects

**Halftone** (dot-screen; Chromium-safest of the family):

```html
<filter id="halftone" color-interpolation-filters="sRGB" x="0" y="0" width="100%" height="100%">
  <!-- 1. one dot cell -->
  <feFlood flood-color="black" result="ink"/>
  <feImage href="data:image/svg+xml,…radial-gradient dot 8x8…"
           x="0" y="0" width="8" height="8" result="cell"/>
  <feTile in="cell" result="screen"/>
  <!-- 2. luminance of source vs screen: arithmetic add then threshold -->
  <feColorMatrix in="SourceGraphic" type="saturate" values="0" result="gray"/>
  <feComposite in="gray" in2="screen" operator="arithmetic"
               k1="0" k2="1" k3="1" k4="-0.5" result="sum"/>
  <feComponentTransfer in="sum" result="dots">
    <feFuncR type="discrete" tableValues="0 1"/>
    <feFuncG type="discrete" tableValues="0 1"/>
    <feFuncB type="discrete" tableValues="0 1"/>
  </feComponentTransfer>
</filter>
```

  (Principle: gray + dot-ramp, threshold — where the image is dark, more of each dot survives. Interop of feImage+feTile varies (§1.4/§1.5); the hrvrts CodePen "Halftone Newspaper Effect" is labeled Chrome-only for a reason. A turbulence-based alternative — `feTurbulence(high freq) + arithmetic + discrete` — gives mezzotint/risograph rather than a regular dot screen, but is fully portable.)

- **Posterize / print-ink reduction**: `feComponentTransfer` with `discrete` tables (4–6 levels), optionally + grain (§2.3) = screenprint.
- **Rough / deckled edges**: `feTurbulence baseFrequency 0.05–0.1 → feDisplacementMap scale 5–15` on the shape; add `feMorphology erode 0.5` for ink-bleed thinning.
- **Paper surface**: §2.5 diffuse-lit fractalNoise at `baseFrequency 0.02–0.05`, very low contrast, multiplied under content.
- **Photocopy/ink**: `luminanceToAlpha → feComponentTransfer feFuncA discrete "0 1" → flood-colorize` = harsh 1-bit ink with turbulence-displaced edges.

---

## 3. Applying filters: HTML vs SVG

### 3.1 `filter: url(#id)` on HTML

- Works in **Chrome, Firefox, Safari** (long-standing). References an inline `<filter>` by fragment; can be mixed with shorthand functions in one declaration, applied **left to right**: `filter: url(#grain) saturate(1.2) blur(0.5px);` (each stage feeds the next).
- The element's border box = filter "bounding box"; user units = CSS px from its top-left (§0.2).
- External-file references (`filter: url(assets/filters.svg#goo)`) work in Firefox; Chromium support arrived late and has a history of cache/HMR flakiness **[uncertain — verify current Chromium status]**; Safari **[uncertain]**. **Recommendation: inline defs or data-URI** (`filter: url("data:image/svg+xml,…#f")` works in Chromium+Firefox; Safari data-URI filter refs historically broken **[uncertain]**).
- Keep the defs `<svg>` rendered (not `display:none`) — §0.5.
- **On text:** fine (outline/grain/displacement on headlines is a signature use), but the whole element rasterizes — subpixel AA is lost, and any displacement makes small body text smeary. Use on display type ≥ ~24px; apply to a wrapper, not `<body>`.
- **On video/canvas:** allowed; filter re-runs **every frame** — a grain url() filter on a fullscreen video is a per-frame full-screen turbulence+blend. Prefer an overlay element with a static grain background instead.
- **On the element vs its backdrop:** `filter` affects the element's own pixels only. Glass effects that must bend *what's behind* need `backdrop-filter` — or the samasante trick (filter a live clone of the background content placed under the lens).

### 3.2 `backdrop-filter: url(#id)` — the interop cliff (verified 2026-07)

- **Chromium: supported.** The only engine where SVG-filter backdrops (true Liquid Glass) ship today. Note the filter region does *not* auto-fit the element — size feImage/maps to the element in px (kube.io).
- **Firefox: not supported.** `backdrop-filter` shipped in 103 for shorthand functions only; SVG `url()` ignored (MDN BCD issue #24110; Mozilla Connect open idea; chriskirknielsen CodePen repro).
- **Safari: not supported yet, fix in flight.** WebKit bug **245510** ("backdrop-filter: url(#some-svg-filter) doesn't work") is still **NEW/open as of 2026-07-16**, but has two PRs (#68614 implementation + #68613 accelerated-path prerequisite) passing WebKit test queues, with animated-backdrop follow-up in development. No shipping Safari version announced. Ironically, Safari 26 (the OS Liquid Glass release) did not include it — Apple's own web UIs fall back to blur.
- Practical stance for the Skill: treat `backdrop-filter: url()` as **progressive enhancement on a Chromium base**, always ship the §2.8 blur+saturate fallback, and expect Safari to join within the 2026 cycle (watch 245510). For must-work-everywhere refraction, filter the content itself (`filter: url()` on a background clone/image) instead of the backdrop.
- `-webkit-backdrop-filter` is still needed for older Safari with shorthand functions; unprefixed since Safari 18 **[uncertain: exact unprefix version — 16.x per some sources]**.

### 3.3 Filters inside SVG documents

- `filter="url(#id)"` attribute or CSS on any SVG element/group. Same primitives, plus `objectBoundingBox` units behave more predictably than on HTML.
- SMIL (`<animate>`, `<animateTransform>`) can animate most primitive attributes (`stdDeviation`, `scale`, `dx`, light positions, `seed` discretely) without JS — not available for filters applied to HTML via CSS (there you animate via JS setting attributes on the shared `<filter>`, which live-updates all consumers).
- CSS custom properties do **not** cascade into SVG filter attribute values (attributes aren't CSS) — parametrization requires JS attribute writes, or multiple pre-declared filter variants.

### 3.4 Stacking & combining

- `filter: url(#a) url(#b) contrast(1.1)` — chains run in order; each `url()` cost is a full pass.
- `filter` + `backdrop-filter` on the same element is legal (glass backdrop + grain on own pixels).
- Blend the filtered element with its surroundings via `mix-blend-mode` (applies after filtering).
- A parent with `filter` isolates blending (creates a stacking context/backdrop root) — a `mix-blend-mode` child stops blending with the page. Same for `backdrop-filter` sampling (§2.8 point 5).

---

## 4. Support, performance, accessibility

### 4.1 Per-engine quirk sheet (2025–2026)

| Area | Chromium | Firefox | Safari/WebKit |
|---|---|---|---|
| Core primitives (blur, offset, flood, merge, blend, composite, colormatrix, componenttransfer, morphology, convolve, dropshadow, turbulence, displacement, lighting) | ✅ | ✅ | ✅ |
| `backdrop-filter: url(#f)` | ✅ | ❌ (BCD #24110) | ❌ open bug 245510, patches in review (2026-07) |
| `color-interpolation-filters: linearRGB` | ✅ honored | ✅ honored | ⚠️ historically computes sRGB regardless (fxtf #113) — force sRGB for parity |
| `feImage` → element fragment (`#el`) | ⚠️ inconsistent | ❌ (bugs 455986, 1538554) | ⚠️ inconsistent sizing |
| `feImage` → data-URI/raster | ✅ | ✅ | ✅ (size it explicitly) |
| `feDisplacementMap` edge cases | ⚠️ 50%-gray & alpha handling diverge from spec (fxtf #113 — all engines) | ⚠️ same | ⚠️ same; also historic mobile-Safari displacement rendering bugs **[uncertain if current]** |
| External file filter refs (`url(file.svg#f)`) | ⚠️ **[uncertain]** | ✅ | **[uncertain]** — inline to be safe |
| SMIL animation of filter attrs | ✅ | ✅ | ✅ (deprecated-but-working everywhere) |
| Filters on cross-origin iframes | 🔒 being **disabled** (blink-dev Intent to Ship, post SVG-clickjacking) | 🔒 restricted (Bugzilla 2004487) | 🔒 expected to follow **[uncertain]** |

That last row: lyra.horse's Dec-2025 "SVG Filters — Clickjacking 2.0" showed filters over cross-origin iframes can visually rewrite embedded UI (demonstrated against Google Docs) and that feBlend+feComposite are Turing-complete (logic gates in filters). Browsers responded by disabling filter effects on cross-origin iframes/plugins. **Design consequence: never build UI that relies on filtering an iframe; it is now or soon a no-op.**

### 4.2 Cost model (ranking, not benchmarks)

Cost ≈ `(filter region area in device px) × (per-pixel primitive cost) × (updates per second)`. Region area and animation frequency dominate everything.

Per-pixel primitive ranking:

- **Near-free:** feOffset, feFlood, feMerge, feBlend, feComposite (Porter-Duff), feColorMatrix, feComponentTransfer.
- **Moderate:** feGaussianBlur (stdDev- and area-dependent; best GPU acceleration), feDropShadow, feImage (decode once, then cheap), feTile.
- **Heavy:** feMorphology (radius-dependent), feDisplacementMap (incoherent gather), feComposite arithmetic (still cheap-ish but breaks some fast paths), lighting primitives.
- **Heaviest:** feConvolveMatrix (order²), **feTurbulence** (per-pixel procedural noise × numOctaves — documented 2025 cases of animated turbulence saturating CPU cores).

Rules for the Skill:

1. If a CSS shorthand exists (`blur()`, `drop-shadow()`, `saturate()`…), use it — browsers fast-path these harder than equivalent SVG chains.
2. Never animate feTurbulence continuously in product UI; bake noise to a tile (§2.3) or step it briefly (§2.4).
3. Shrink the region: explicit tight `x/y/width/height`, filter the smallest wrapper possible, never `<body>`.
4. Animating a *cheap attribute* of an existing chain (`scale`, `dx`, light `x/y`, `flood-opacity`) ≪ rebuilding maps/markup. Design animations around attribute-only changes (kube.io's normalized-map/scale trick is the archetype).
5. Displacement maps: rebuild on resize only, debounced; cache per size.
6. `will-change: filter` / `backdrop-filter` promotes a layer — helps steady-state, wastes memory if overused.
7. Test on a mid-tier Android; Chromium's GPU path hides costs your users will feel elsewhere.

### 4.3 Accessibility & resilience

- **`prefers-reduced-motion: reduce`** → freeze squigglevision (fixed seed), stop displacement/scale animations, keep static styling. Filters that *move* are motion.
- **`prefers-reduced-transparency: reduce`** (shipping in Safari/Chromium **[uncertain: Firefox]**) → replace glass with near-opaque panels; Apple does exactly this for Liquid Glass.
- **`prefers-contrast: more` / `forced-colors: active`** → drop decorative filters, use solid backgrounds and system colors; in forced-colors mode backdrop blur over unknown user colors is a contrast lottery.
- Text over glass/grain: maintain WCAG contrast with a tint/scrim layer independent of the filter (the blurred backdrop is not a reliable contrast provider).
- Filters are purely visual — never encode state *only* in a filter (e.g. gooey merge indicating selection) without an ARIA/text equivalent.
- Fallback pattern:

```css
.glass { background: rgba(28,28,30,0.92); }              /* worst case */
@supports (backdrop-filter: blur(1px)) {
  .glass { background: rgba(28,28,30,0.55); backdrop-filter: blur(14px) saturate(1.6); }
}
/* Chromium refraction layer gated by runtime probe, not @supports (§2.8) */
@media (prefers-reduced-transparency: reduce) { .glass { background: rgb(28,28,30); backdrop-filter: none; } }
```

---

## 5. Resource inventory

Specs & references:

- **W3C Filter Effects Module Level 1** — drafts.fxtf.org/filter-effects/ — normative source for primitive math (composite arithmetic formula, color-space rules, shorthand≡matrix equivalences).
- **SVG 1.1 Filters chapter** — www.w3.org/TR/SVG11/filters.html — legacy definitions (feImage element refs, BackgroundImage) that explain interop scar tissue.
- **MDN `<filter>` + per-primitive pages** — developer.mozilla.org — attribute tables + live BCD support data; check BCD before trusting any niche attribute.
- **w3c/fxtf-drafts issue #113** — github.com/w3c/fxtf-drafts/issues/113 — the definitive catalog of feDisplacementMap interop divergence.
- **w3c/svgwg issue #1142** — github.com/w3c/svgwg/issues/1142 — proposal for interoperable backdrop refraction ("liquid glass" standardization); track for the future API.
- **WebKit bug 245510** — bugs.webkit.org/show_bug.cgi?id=245510 — Safari `backdrop-filter: url()` status; patches in review 2026-07.
- **MDN BCD issue #24110** — github.com/mdn/browser-compat-data/issues/24110 — documents Firefox/Safari lack of SVG filters in backdrop-filter.

Playgrounds & tools:

- **Yoksel's SVG Filters playground** — yoksel.github.io/svg-filters/ — visual node-style filter builder; mine it for chain prototyping and copy-paste primitive markup.
- **frontend-hero.com/css-noise-generator** (and similar) — parameterized grain data-URI generation; mine the encoding pattern.

Tutorial canon:

- **kube.io "Liquid Glass in the Browser: Refraction with CSS and SVG"** — kube.io/blog/liquid-glass-css-svg/ — **north star**: Snell's-law displacement maps, squircle bezel profiles, normalized-vector/scale animation trick, Chromium backdrop caveat.
- **Sara Soueidan, Codrops "SVG Filter Effects" series (2019, 6 parts)** — tympanus.net/codrops (SVG Filters 101 → Outline Text with feMorphology → Poster Image with feComponentTransfer → Duotone → Creating Texture with feTurbulence → Moving Forward) + index at sarasoueidan.com/blog/svg-filters-series/ — the best pedagogical walkthrough of chaining and each primitive's mental model.
- **Dirk Weber, Smashing Magazine** — "The Art of SVG Filters and Why It Is Awesome" (2015; typography effects, lighting, texture) and **"A Deep Dive Into the Wonderful World of SVG Displacement Filtering" (2021)** — smashingmagazine.com/2021/09/deep-dive-wonderful-world-svg-displacement-filtering/ — displacement-map authoring and animation techniques beyond noise.
- **Lucas Bebber, CSS-Tricks "The Gooey Effect"** — css-tricks.com/gooey-effect/ — canonical goo filter + atop trick + tuning notes; companion Codrops "Creative Gooey Effects" (menus, pagination demos).
- **CSS-Tricks "Grainy Gradients"** (+ Frontend Masters follow-up, freeCodeCamp grainy backgrounds) — the static-turbulence-tile grain pattern and banding fix.
- **CSS-Tricks "Squigglevision"** (Greatest CSS Tricks) + **camillovisini.com "Simulating Hand-Drawn Motion with SVG Filters"** — stepped-seed boiling-line technique.
- **utilitybend "Revisiting SVG filters"** — utilitybend.com — modern practical duotone/noise recipes with CSS integration.
- **CSS-Tricks "Using SVG to Create a Duotone Effect on Images"** — feComponentTransfer duotone with code.
- **vincent de oliveira (iamvdo)** — "Advanced CSS filters" article + "Faking backdrop-filter using SVG filter" CodePen — pre-backdrop-filter background-refraction hacks; still the model for filter-the-clone fallbacks.

Liquid-glass implementations (2025–2026) to mine:

- **specy.app/blog/posts/liquid-glass-in-the-web** (+ Medium) — displacement bit-depth limits, physics precomputation.
- **github.com/samasante/liquid-glass** — cross-browser lens via `filter:url()` on a live DOM clone (the Safari/Firefox-compatible architecture).
- **github.com/nikdelvin/liquid-glass** — component library (containers/text/buttons), pure CSS+SVG.
- **dev.to/maxgeris "Recreating Apple's Liquid Glass…"**, **LogRocket "How to create Liquid Glass effects with CSS and SVG"**, **Medium/ekino-france "Liquid Glass in CSS (and SVG)"** — turbulence-approximation and gradient-map variants; good for cheap tiers.
- **css-tricks.com "Getting Clarity on Apple's Liquid Glass"** — design-language context and web-fallback discussion.

Depth awareness / security:

- **lyra.horse/blog/2025/12/svg-clickjacking/** — SVG filters as computation (logic gates from feBlend/feComposite, Turing completeness), cross-origin iframe attacks; mine for: how far filter chains can be pushed, and why iframe filtering is being disabled (Bugzilla 2004487; blink-dev Intent to Ship "Disable SVG filters on plugins and cross-origin/restricted iframes").

Notable CodePens:

- codepen.io/SARFEX/pen/oyrdjW — animated SVG metaballs/goo.
- codepen.io/hrvrts/pen/bWbomW — halftone newspaper via feImage/feTile (Chrome-only; shows the technique and the interop wall).
- codepen.io/chriskirknielsen/pen/PwwwvMX — minimal repro of Firefox's missing backdrop-filter url() (useful as a live support probe).
- codepen.io/iamvdo/pen/VLOGdw — faked backdrop-filter via SVG (historical technique).
- **visualcinnamon.com gooey data-viz posts** — goo applied to D3 scatter/clusters; parameter intuition at scale.

---

## 6. Uncertainty ledger

Claims to re-verify before the Skill states them as fact:

1. **Safari `backdrop-filter: url()` ship date** — patches passing WebKit queues as of 2026-07; not shipped in any released Safari as of writing. Re-check bug 245510 / Safari release notes at distillation time.
2. **Firefox `@supports (backdrop-filter: url(#x))`** result — whether it parses (and thus false-positives) was not directly tested; use runtime probe regardless.
3. **External file filter references** (`filter: url(file.svg#f)`) in current Chromium and Safari — historically broken/flaky; not re-verified 2026. Inline defs sidestep it.
4. **feImage element-fragment references** current behavior per engine — 2017-era data (Chrome/Safari yes-with-quirks, Firefox no); Firefox bugs still open. Data-URI path is the safe recommendation either way.
5. **Extended feBlend modes (hue/saturation/color/luminosity) in Safari** — believed supported; verify if a recipe depends on them.
6. **`prefers-reduced-transparency` in Firefox** — support status not verified.
7. **Safari linearRGB handling today** — the "computes sRGB regardless" behavior is documented historically (fxtf #113); modern WebKit may have partially fixed it. Forcing sRGB remains correct advice either way.
8. **Exact Safari version that unprefixed `backdrop-filter`** (16.x vs 18) — cosmetic detail; keep the `-webkit-` prefix in fallback code regardless.
9. **feMorphology large-radius performance and box-shape artifacts** — behavior well known, exact thresholds anecdotal.
10. The gooey merge-distance formula in §2.2 is a working approximation (blur field overlap heuristics), not spec math — present it as tuning intuition, not law.
