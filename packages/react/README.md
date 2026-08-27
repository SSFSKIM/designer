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
accessibility-mode profiles still uncaptured; and **no claim that the two tiers
are identical**, nor that the coherence figure above holds on Gecko or WebKit,
where nothing about `backdrop-filter` is measurable at all.

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
