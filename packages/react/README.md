# vitrea-react

**React bindings for [vitrea](https://www.npmjs.com/package/vitrea) — a
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
npm install vitrea vitrea-react
```

`vitrea` is this package's one declared dependency and React is a peer (`>=19`).
Everything else — the DOM host layer, the geometry kernel, the motion kernel, the
WebGPU renderer — is internal and bundled in at publish time. There is no state
library, no animation library, and no accessibility library in here.

In v1 this package is also the **only** way to render glass in a browser: `vitrea`
itself contains no DOM code by design, and the host layer ships bundled inside
this artifact.

---

## Quickstart

```tsx
import { GlassRoot, GlassGroup, GlassToolbar, GlassButton } from "vitrea-react";

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
[`vitrea`'s README](https://www.npmjs.com/package/vitrea).

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

**Constants and defaults** — `DEFAULT_CLEAR_DIMMING` (the one-liner that
satisfies the clear variant's dimming requirement — the runtime refuses a clear
surface without a policy rather than inventing a scrim),
`DEFAULT_GLASS_MOTION_PROFILE`, `GLASS_ROOT_ACCESSIBILITY_DEFAULTS`,
`SUPPORTED_PLANES`, `GLASS_CHANNEL_PROPERTIES`.

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
> can be. A Chromium-only measurement now exists and is stated as such: on the 18
> light calibration and validation cells, the CSS tier reaches SSIM 0.9544 mean /
> 0.9040 worst and OKLab ΔE 0.0275 mean / 0.0727 worst — about 3.2× the texture
> tier's ΔE in the same cells. Its shape axis is not comparable to the texture
> tier's, and it is UNTUNED.**

Not claimed, explicitly: **never "pixel-identical to Apple"** — every figure is
scoped to one native profile and one web cell; **no press-state claim**, because
Apple's `Glass.interactive(true)` opts the material into responding to press
input rather than posing it pressed, and the native "pressed" captures are
byte-identical to their rest counterparts; **no adopted pass/fail thresholds**,
only proposals awaiting a human gate; **1× scale only**, with both
accessibility-mode profiles still uncaptured; and **no tier-coherence claim**,
since the CSS tier is untuned.

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
