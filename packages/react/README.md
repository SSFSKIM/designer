# vitrea-react

**React bindings for [vitrea](https://www.npmjs.com/package/@vitreajs/vitrea) — a
production-oriented, reference-calibrated material compositor for semantic web
controls.**

vitrea replicates Apple's Liquid Glass material on the web: real-time
size-parameterized lensing, per-element backdrop adaptation, container-scoped
sampling, and shape-to-shape morphing. This package is the declarative surface —
components and hooks — and it is thin by policy. It maps React lifecycle and JSX
onto the runtime and owns no material, no geometry and no motion of its own, so a
later Vue, Svelte or Web-Components adapter duplicates nothing but the lifecycle.

The important consequence of that thinness is what your markup stays. A
`GlassButton` renders a real `<button>`: selectable text, real focus, working IME,
announced by a screen reader as a button. The glass is drawn on canvases above and
below it, never instead of it.

---

## Install

```bash
npm install @vitreajs/vitrea @vitreajs/vitrea-react
```

The library is called vitrea and publishes under the npm scope `@vitreajs`.
`@vitreajs/vitrea` is this package's one declared dependency and React is a
peer (`>=19`). Everything else — the DOM host layer, the geometry kernel, the
motion kernel, the WebGPU renderer — is internal and bundled in at publish
time. There is no state library, no animation library, and no accessibility
library in here.

In v1 this package is also the **only** way to render glass in a browser: `vitrea`
itself contains no DOM code by design, and the host layer ships bundled inside
this artifact.

---

## Quickstart

```tsx
import { GlassRoot, GlassGroup, GlassToolbar, GlassButton } from "@vitreajs/vitrea-react";

export function App() {
  return (
    <GlassRoot renderer="webgpu">
      {/* Your page. Ordinary DOM, and it stays ordinary DOM. */}
      <YourPage />

      <GlassToolbar
        aria-label="Actions"
        groupProps={{ hint: { tone: "dark", luminance: 0.18 } }}
        style={{ position: "fixed", bottom: 32, left: "50%", transform: "translateX(-50%)" }}
      >
        <GlassButton onClick={share}>Share</GlassButton>
        <GlassButton onClick={save}>Save</GlassButton>
      </GlassToolbar>
    </GlassRoot>
  );
}
```

Three things are happening there, and each is a deliberate contract rather than a
convenience:

`GlassRoot` owns the whole lifecycle — one runtime, one scheduler, the managed
planes — and is the only component that does. Note that glass surfaces render
nothing for exactly one commit while the root is built in an effect; your own page
content renders immediately, because gating the app's content on vitrea's schedule
would be the wrong trade.

`GlassToolbar` creates its own **sampling group** for its members (pass
`group={false}` to put them in the group already in scope instead). A group is
the sampling unit: one backdrop proxy, one blur, shared between members. It also
handles arrow-key roving focus for its items, wherever in the DOM they have been
portalled to.

`hint` is how you tell the runtime what is behind a group. vitrea does not
automatically pixel-analyse arbitrary DOM and never claims to — the hint (or an
estimator provider) is the one mechanism, and it is documented as a hint
everywhere it appears.

**The hint also decides how the material itself looks over a dark backdrop.**
Apple's Liquid Glass stops being a lighter thing in front of a dark enough
backdrop and takes that backdrop's own tone; vitrea now does the same, so the
tone you declare is the tone a small surface settles into. The threshold is low —
nothing happens above roughly a fifth of the luminance range — and the effect is
size-gated: a 44 px control over a near-black backdrop disappears into it, while
a large panel over the same backdrop keeps most of its own appearance. Measured
against the reference rather than styled;
`docs/doperpowers/specs/c9a-fidelity-claims.md` §5.8 has the numbers.

Where you register a **texture** backdrop, vitrea measures that source's average
tone from the pixels you handed over and needs no hint for this. Where it has
neither, the material does not adapt at all, on either tier — it will not guess a
backdrop it has not been shown.

### Surfaces outside a control

```tsx
<GlassGroup id="hero" hint={{ tone: "light" }}>
  <GlassSurface radius={20} thickness={10}>
    <h1>Anything you like in here</h1>
  </GlassSurface>
</GlassGroup>
```

`GlassSurface` takes `asChild` when you want to register your own element rather
than have it render a `<div>` — which is how the menu is composed, over whichever
accessible menu primitive your app already uses. This package deliberately takes
no dependency on one.

**A surface has no intrinsic size**, and this is the one thing about it that
surprises people. vitrea declares neither position nor size for a host: it
measures the box your CSS produced, once per frame, and fits the material to it.
The element is portalled into its plane's host layer, which is a
`position: absolute; inset: 0` overlay, so a surface places itself the way any
overlay child does. Give it your own width, height and positioning — a
`<GlassSurface>` with no styles of its own is as tall as its content and nothing
more. Position and size are never props, because a measured rect is the single
source of truth that lets press compression and morph deformation be composed
transforms rather than shape changes.

### Colouring a surface: `tint`

```tsx
<GlassToolbar aria-label="Document actions">
  <GlassButton onClick={publish} tint="#ff9500">Publish</GlassButton>
  <GlassButton onClick={duplicate}>Duplicate</GlassButton>
  <GlassButton onClick={remove}>Delete</GlassButton>
</GlassToolbar>
```

`tint` takes **any CSS colour** — a hex, an `rgb()`, a named colour, an
`oklch()`, whatever your design tokens are already written in. It is the
supported way to colour glass, and it exists because the obvious alternative is a
documented failure: a background colour on the host element is a solid fill, and
Apple names exactly that — *"it is completely opaque and breaks the visual
character of Liquid Glass."*

**The colour you pass is a seed, not a fill.** Apple's material "generates a
range of tones that are mapped to content brightness underneath the tinted
element", and vitrea does the same: the seed is read through a tone curve against
the backdrop the surface is already sampling, so one orange settles to a deep
amber over dark content and a bright wash over light content, and the backdrop
keeps coming through either way. On the WebGPU tier that happens per pixel,
inside the optics pass, against the same lens-displaced sample the material
refracts. On the CSS tier — which has one colour per element to work with — the
tone is resolved at one backdrop level and converted through the same mapping the
material's own tint goes through, so the two tiers stay derived from one document
instead of holding two sets of numbers.

**A tint changes what colour the material is, never how opaque it is.** That
separation is deliberate, and it is what keeps the accessibility story intact:
opacity is the material's occlusion, which is the axis *Reduce Transparency*
lifts and where a system-level glass preference lands. A tinted surface under an
accessibility preference therefore gets *more of the author's colour*, not a
different one.

The colour's own **alpha is the tint's strength** — `rgb(255 149 0 / 50%)` is a
half-strength orange, the same way `Color.orange.opacity(0.5)` is in SwiftUI — so
subtlety is expressed in the colour rather than in a second prop. `tint={null}`
clears a tint inherited from the group.

Three things worth knowing before you reach for it:

- **Tint sparingly.** Apple's guidance is to colour one element that benefits
  from emphasis — a primary action, a status indicator — and explicitly not the
  backgrounds of several controls at once: *"when every element is tinted,
  nothing stands out."*
- **A group carries one seed.** A `GlassGroup` is one sampling region and one
  optics pass, which is exactly enough for the composition above (one coloured
  control among plain ones) and not enough for two different hues in one group.
  Asking for two raises a dev-mode warning naming the fix, which is to give the
  second surface its own group.
- **The ink follows the tint.** vitrea publishes `--vitrea-foreground` against
  the material it is actually drawing, so a dark tint gets the light ink without
  you declaring anything — including on a group with no backdrop hint at all,
  wherever the tint decides the answer for every possible backdrop.

Under **forced colours** the tint goes with the rest of the material: there is no
glass to colour, and the surface takes the platform's palette.

**What is measured, and what is not.** The tint is implemented on both tiers and
visually verified on both — that a tinted surface takes the colour, that its
untinted neighbour in the same group does not, and that the backdrop still
transmits through it rather than being replaced by paint. **It carries no
fidelity number.** Every constant in the tone curve is an advisory default, and
the tinted native captures that would fit them are a scheduled extension of the
capture harness, not something this release measured. When those land, the curve
becomes a data change and the claim below gains a tint section; until then, treat
the tint's *appearance* as designed rather than as calibrated.

### Where a surface belongs: the controls layer

`GlassSurface` will glass whatever element you hand it, and there is one place it
should not go. Apple states it as a prohibition rather than as advice — **"Don't
use Liquid Glass in the content layer"** — because the material's whole job is to
separate what you can act on from what you are reading, and glass on both sides
of that line collapses it. The same rule read the other way is why `GlassToolbar`
is deliberately *not* a glass surface: stacking the material on itself is a
failure Apple names outright ("avoid applying the material to both layers.
Instead, use fills, transparency, and vibrancy for the top elements"), so the
toolbar is a plain container and the platter you see is its members' fields
merging.

In practice: glass on the button, not on the row it sits in; glass on the
toolbar's controls, not on the toolbar and its controls; and never on a list or a
table, which is the case Apple calls out by name and the one `asChild` makes
easiest to get wrong.

Two dev-mode diagnostics now say so instead of leaving it to the docs:

- **`glass-inside-glass`** — a surface registered inside another surface's
  subtree. It names both nodes and tells you to keep the material on whichever of
  the two is the control, giving the other a fill, a translucency or a vibrant
  foreground. Not the same finding as core's `same-plane-overlap`: that one is
  geometric and about the paint sandwich, this one is structural and still fires
  when the nesting crosses planes.
- **`glass-in-content-layer`** — a surface registered on an element whose
  resolved ARIA role is a list or table structure (`<ul>`, `<li>`, `<tr>`,
  `role="row"`, and so on). An explicit `role` wins over the tag's implicit one,
  so `<ul role="menu">` is a controls-layer container and says nothing; the
  message names that escape.

Both run once per registration, in `devMode` only, and never from a frame — a
production build pays nothing for them. Both arrive on the diagnostics channel
like every other finding, so `useGlassDiagnostics` puts them on screen if you
want them there rather than in the console.

### A texture backdrop

`backdrop={{ kind: "texture", id }}` moves a group onto the GPU texture path, and
it is deliberately two steps: the prop **declares** the source, and the root
handle **supplies** the pixels. `@vitreajs/vitrea` is platform-free and may not
hold an `HTMLImageElement`, so the declaration cannot carry one.

```tsx
import { GlassGroup, GlassSurface, useGlassRoot } from "@vitreajs/vitrea-react";

function Hero() {
  const root = useGlassRoot();

  return (
    <>
      {/* Declare. `configuredSource` stays "texture" through any demotion. */}
      <GlassGroup id="hero" backdrop={{ kind: "texture", id: "hero" }}>
        <GlassSurface radius={26} thickness={18}>…</GlassSurface>
      </GlassGroup>

      {/* Supply. The id joins the two halves; the order does not matter, and
          `setBackdropTexture` marks the source dirty itself. */}
      <img
        src="/hero.jpg"
        alt=""
        onLoad={(event) =>
          root?.setBackdropTexture("hero", { kind: "image", image: event.currentTarget })
        }
      />
    </>
  );
}
```

`{ kind: "canvas", canvas }` and `{ kind: "video", video }` are the other two
forms — a video and a live canvas are re-imported every frame that samples them,
a decoded image once — and `undefined` withdraws a source's pixels. Declaring a
texture and never supplying one is not a silent hole: the group reports
`health: "demoted"` with `demotionReason: "no-texture-supplied"` and goes on
drawing tint, rim and glow.

**Where the texture is placed.** The renderer maps the source over the **whole
viewport**, cover-fit — filling it, with the overflow cropped symmetrically, the
same geometry as `object-fit: cover` on a `position: fixed; inset: 0` element.
Not over the group, and not over the surface. So if your app also paints that
image — the usual case, since the picture is on the page and the glass sits on it
— the two mappings have to agree. An `<img>` sized to a region under a texture
mapped to the viewport samples a different crop of the same file, and the
mismatch shows up as the glass revealing the wrong part of the picture, which
reads convincingly like a lensing artefact rather than a registration error.
Paint your copy viewport-sized and `object-fit: cover`.

### Seeing what actually resolved

```tsx
function TierReadout() {
  const state = useGlassCapabilities("hero");
  if (state === undefined) return null;
  return (
    <p>
      configured {state.configuredSource}, drawing on {state.activeRenderer},
      sampling {state.samplingBackend}, refraction {state.refraction}
      {state.health === "demoted" ? ` — demoted: ${state.demotionReason}` : ""}
    </p>
  );
}
```

Asking for the GPU tier is not the same as getting it, and this hook is how you
find out which happened. Choosing the CSS tier is **not** a fault: a root that
never requested WebGPU resolves to `activeRenderer: "css"` with `health: "ok"`
and no demotion reason. Every real demotion names both a reason and its recovery
condition. The full model is documented in
[`@vitreajs/vitrea`'s README](https://www.npmjs.com/package/@vitreajs/vitrea).

---

## What this package exports

**Components** — `GlassRoot`, `GlassGroup`, `GlassSurface`, `GlassMorph`,
`GlassButton`, `GlassIconButton`, `GlassToolbar`, `GlassSegmentedControl`,
`PlanePortal`.

**Hooks** — `useGlassCapabilities`, `useGlassAccessibility`,
`useGlassDiagnostics`, `useGlassMotionProfile`, `useGlassTicker`, `useGlassRoot`,
`useToolbarItem`.

**Composition helpers** — `renderAsChild`, `composeRefs`, `mergeSlotProps` for
`asChild` seams; `radiiFor`, `smoothingFor`, `capsuleRadius`,
`cornerReferenceFor`, `assertSharedCornerReference` for shapes.

**Frames** — `createGlassTicker`, the rAF loop the bindings drive their motion
from. One per tree, whatever the surface count; its `advance()` steps time by
hand, which is the path a test with no animation frames takes.

**Constants and defaults** — `DEFAULT_CLEAR_DIMMING` (the one-liner that
satisfies the clear variant's dimming requirement — the runtime refuses a clear
surface without a policy rather than inventing a scrim),
`APPLE_LIKE_SMOOTHING` (the Apple-matching corner on the interpolable smoothing
axis — a `GlassMorph` pair needs it, because `"continuous"` and the numeric axis
are separate fits to different curves and an interpolated corner between the two
has no measured error bound; authoring this number at both ends keeps the morph
on one axis), `DEFAULT_GLASS_MOTION_PROFILE`,
`GLASS_ROOT_ACCESSIBILITY_DEFAULTS`, `SUPPORTED_PLANES`,
`GLASS_CHANNEL_PROPERTIES`.

**DOM attribute names** — `TOOLBAR_ITEM_ATTRIBUTE` (`data-vitrea-toolbar-item`,
which marks an item's owning toolbar wherever the item has been portalled to) and
`PLANE_MOUNT_ATTRIBUTE` (`data-vitrea-mount`). Both are public because tests and
dev tooling read them.

### Contract limits worth knowing before you design around it

- All glass lives inside `GlassRoot`'s managed planes. v1 ships exactly two —
  base and one overlay — and menus portal internally to the overlay plane.
  Interleaving glass with foreign stacking contexts is out of contract.
- Two glass surfaces must not overlap **within one plane**: it is a dev-mode
  error, because the paint sandwich cannot place one surface's body above another
  surface's DOM label. Overlap *across* planes is the supported case, and is what
  `GlassMorph` uses.
- Corner radii are uniform in v1. The API keeps its four-component shape; a
  non-uniform set is a dev-mode error.
- Mixing `regular` and `clear` variants inside one group raises a dev-mode
  warning, mirroring Apple's own guidance.
- One `tint` seed per group. Two different tint colours inside one `GlassGroup`
  raise a dev-mode warning: a group is one optics pass, so the WebGPU tier draws
  them all in the first surface's colour while the CSS tier honours each. Per
  surface, tint *strength* is unrestricted — one coloured control among plain
  ones is the supported composition.

---

## Styling a glass host

A glass host is your element. The runtime writes to it every frame — the tint,
the border, the blur, and a set of custom properties — but it never takes the
element's styling away from you.

The properties it publishes, on every host, on **both** tiers:

| Property | What it carries |
| --- | --- |
| `--vitrea-foreground` | The ink the runtime resolved as readable on the material this group is drawing. |
| `--vitrea-tint` | The tint colour, with its alpha. |
| `--vitrea-occlusion` | That alpha on its own, `0`–`1`. |
| `--vitrea-border-color` | The rim colour. |
| `--vitrea-blur` | The frost radius, in CSS px, after accessibility policy. |

Read them the way the demo does, with your own value as the fallback so a tier
that published nothing degrades to your design rather than to nothing:

```css
.my-panel__label {
  color: var(--vitrea-foreground, var(--my-ink));
}
```

**Your own `color` rule on the host wins.** The runtime's ink reaches the host
through a single zero-specificity rule (`:where([data-vitrea-node])`) installed
first in the document's `<head>`, so any selector of yours that names the
element — a class, an id, an attribute, a tag — overrides it, and so does an
equally weak one by source order. Up to 0.1.1 the ink was written as an inline
`color` instead, which meant an application rule on a glass host parsed,
cascaded, and silently never applied; that is fixed.

Two properties the runtime does own outright, and which you should style around
rather than on:

- **`background`** on the host — the CSS tier writes the shorthand every frame,
  so a `background-image` of yours is clobbered. Put it on a pseudo-element.
- **`transform`** on the host, while a press or a morph is running.

---

## Fidelity

The material is tuned against real ScreenCaptureKit captures of Apple's
`glassEffect` on macOS 26.5, not against recollection. The complete record —
what was measured, what could not be, and every gap left open — is
[`docs/doperpowers/specs/c9a-fidelity-claims.md`](https://github.com/SSFSKIM/designer/blob/main/docs/doperpowers/specs/c9a-fidelity-claims.md).

The claim, as that document words it:

> **Reference-calibrated against macOS 26.5 captures.** vitrea's WebGPU texture
> tier — its own shader math over a GPU-owned backdrop — was calibrated against
> 30 ScreenCaptureKit captures of Apple's `glassEffect` material on macOS 26.5,
> in the cell *Chromium 151, `gpu-texture` backend, Apple Metal-3 adapter, sRGB,
> 1× scale*. Across the six scenes held out of tuning, the rendered result
> reaches a silhouette IoU of 0.9924 mean / 0.9612 worst, a contour distance of
> 0.18 px mean / 0.56 px worst-cell-mean, SSIM 0.9475 mean / 0.9007 worst, and
> OKLab ΔE 0.0320 mean / 0.0548 worst. Tuning improved every one of those axes
> over the untuned defaults. It is not pixel-identical to Apple's material and
> two named gaps remain open.

And for the CSS tier, which is what most visitors will actually see:

> **No cross-engine pixel-wise fidelity claim is made for the dom tier, and none
> can be. On Chromium, in the same cell with `renderer: css` and
> `samplingBackend: css-backdrop`: OKLab ΔE 0.0091 mean / 0.0240 worst and SSIM
> 0.9700 mean / 0.9304 worst over the 12 light calibration cells, ΔE 0.0108 /
> 0.0273 over the 6 validation cells, and ΔE 0.0291 mean / 0.0560 worst with SSIM
> 0.9373 / 0.9205 on the six scenes held out of all tuning. Silhouette IoU 0.9424
> mean over the calibration cells and 0.9684 on holdout, with a 1.06 px mean
> contour distance.**

This tier does not hold a material of its own — it **converts** the one the root
carries — so retuning the material moves both tiers at once. And on demotion:

> On Chromium, a group that demotes from the WebGPU texture tier to the CSS tier
> keeps the same material to within 1.3% of its interior level in the mean and 11%
> on the worst measured cell, at a cross-tier OKLab ΔE of 0.0063 mean / 0.0124
> worst over the fitted sets and 0.0188 / 0.0313 over the held-out ones. It is
> **not** the same rendering — refraction is absent on the CSS tier by contract
> (`refraction: "none"`) — but the material's opacity, tint and frost do not
> change visibly on demotion.

Not claimed, explicitly: **never "pixel-identical to Apple"** — every figure is
scoped to one native profile and one web cell; **no press-state claim**, because
Apple's `Glass.interactive(true)` opts the material into responding to press
input rather than posing it pressed, and the native "pressed" captures are
byte-identical to their rest counterparts; **no adopted pass/fail thresholds**,
only proposals awaiting a human gate; **1× scale only**, with both
accessibility-mode profiles still uncaptured; **no fidelity claim for the author
tint**, whose tone curve is advisory until the tinted native captures are taken
(see `tint` above — implemented and visually verified on both tiers, measured on
neither); and **no claim that the two tiers are identical**, nor that the
coherence figure above holds on Gecko or WebKit, where nothing about
`backdrop-filter` is measurable at all.

---

## Browser support

| Engine | WebGPU (texture tier) | CSS tier |
| --- | --- | --- |
| **Chromium** (Chrome, Edge) | Default-on from 113 desktop, 121 Android | Yes — backdrop-proxy sampling equivalence measured byte-exact |
| **Safari / WebKit** | Default-on from Safari 26 | Yes, manually verified: automated capture cannot observe `backdrop-filter` on this engine |
| **Firefox / Gecko** | Default-on from 141 Windows, 145 ARM Mac; **still flagged on Linux** | Yes, manually verified: same capture blindness |

Where WebGPU is missing, every group resolves to the CSS tier with
`demotionReason: "no-webgpu"`, renders presentable glass, and logs no errors. The
CSS tier is a hard requirement of the design, not a courtesy — which is why it has
its own renderer rather than a degraded code path.

### One known engine defect: Chromium 152 and a rounded, clipping ancestor

Chromium 152 drops `backdrop-filter` entirely on an element with
`clip-path: path()` when an ancestor has `overflow` other than `visible`
**together with** a `border-radius`. All three ingredients are required; every
basic-shape `clip-path` is unaffected. vitrea's GPU-tier backdrop proxies are
exactly that shape, so this can reach a real page.

**With the default mount it cannot**: `GlassRoot`'s planes are `position: fixed`
children of `<body>`, above any rounded, clipping container. It becomes
reachable only if you pass your own `container` and that container sits inside
one — a rounded card, modal or scroll area. There the proxies lose their frost
silently: the engine logs nothing, and no readback path in a page can observe
`backdrop-filter` output at all.

So the runtime says it for you. In dev mode, a group whose proxy chain has that
shape on Chromium 152 or newer emits `engine-known-defect` — a **warning**, never
a demotion, because nothing here is measurable and demoting on a structural match
would trade a possibly-unfrosted GPU tier for a certainly-lower one. The message
names the ancestor, the three workarounds (mount at the default; remove either
the radius or the overflow from that ancestor; or use a geometry a basic shape
can express) and the verified repro. The bug report is drafted at
[`spikes/s1-proxy-topology/chrome152-regression/`](https://github.com/SSFSKIM/designer/blob/main/spikes/s1-proxy-topology/chrome152-regression/REPORT.md).

---

## Testing your app

**Trust the readout; check the launcher.** `useGlassCapabilities()` reports what
resolved, so a `demotionReason: "no-webgpu"` means that session really had no
WebGPU. The environment is the part worth checking, because Playwright's bundled
headless shell resolves WebGPU to a SwiftShader adapter while `channel: "chromium"`
— the full browser binary — resolves it to real hardware. A suite that never asks
for the channel runs green on the CSS tier and every readout in it honestly says
`no-webgpu`: nothing looks broken, it is simply the other tier.

```ts
// playwright.config.ts
projects: [
  {
    name: "chromium-gpu",
    use: {
      channel: "chromium",
      launchOptions: {
        args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"],
      },
    },
  },
],
```

Serve the page over `http://localhost` while you are at it: `navigator.gpu` is
undefined outside a secure context, and on `file://` or `data:` URLs its absence
reads exactly like "no WebGPU on this machine". A test that means to assert the
GPU tier should fail when no adapter answers rather than skip.

**What is in the DOM depends on the tier.** `[data-vitrea-proxy]` elements exist
only for a group resolved to `activeRenderer: "webgpu"` with
`samplingBackend: "css-backdrop"` — the GPU tier sampling arbitrary DOM — and
there is one per group *per plane* it has members on. A GPU-tier group on a
texture backdrop has none, because there is nothing in the page to filter. And on
the CSS tier there are no proxy elements at all: that tier applies
`backdrop-filter` in place, on each glass host element, which is what keeps a
host's own text and icons above its filter without any layering. So assert the
CSS tier by reading a host's computed `backdrop-filter`, `background-color` and
`border-color`, and assert the tier itself with `useGlassCapabilities()`.

---

## Accessibility

Each preference resolves to a declared consequence, and the strictest active one
wins:

| Preference | What changes |
| --- | --- |
| `prefers-reduced-motion` | No overshoot, no deformation, no shimmer travel; morphs become non-elastic. Direct-manipulation positional continuity is kept — reduced motion is not no motion. |
| `prefers-reduced-transparency` | More frost, less refraction, higher occlusion. |
| `prefers-contrast: more` | Stronger borders, near-monochrome foregrounds, reduced ambient tint. |
| `forced-colors: active` | System colours, borders, **no glass**. |

The first three are overridable per root; the fourth is not, and its absence is
enforced in the type system rather than merely documented — an operating-system
colour mandate is not an app's to switch off.

```tsx
<GlassRoot reducedTransparency={true} increasedContrast="system" />
```

`"system"` follows the media query, a boolean overrules it. Note that
`prefers-reduced-transparency` is not Baseline: on an engine that cannot answer
the query, `"system"` silently resolves to false and the user's preference is
lost, so the runtime emits a diagnostic saying exactly that. Setting it
explicitly is load-bearing.

One obligation this package hands you: content portalled into a plane leaves its
original DOM position, so if it was inside a landmark region you own
re-establishing the landmark. A landmark/`role` seam on `GlassMorph` is deferred
post-v1 API work, and this is the documented behaviour until then.

---

## License

Apache License 2.0. See [`LICENSE`](https://github.com/SSFSKIM/designer/blob/main/LICENSE).

"Liquid Glass" is the name of Apple Inc.'s design language, referenced here
descriptively to say what this library replicates. vitrea is not affiliated with,
endorsed by, or sponsored by Apple Inc. See [`NOTICE`](https://github.com/SSFSKIM/designer/blob/main/NOTICE).
