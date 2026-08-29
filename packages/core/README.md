# vitrea

**A production-oriented, reference-calibrated material compositor for semantic web
controls.**

vitrea replicates Apple's Liquid Glass material and interaction system — WWDC25's
`glassEffect`, `GlassEffectContainer`, `interactive()`, `glassEffectID` — on the
web, in TypeScript. Not a blur preset: real-time size-parameterized lensing,
per-element adaptation of tint and foreground to the live backdrop,
container-scoped sampling, and shape-to-shape morphing.

This is not the first WebGPU glass demo, and it does not claim to be. Prior art
exists and is good at what it does. What vitrea is built for is the part the
demos leave out: explicit backdrop contracts, shared sampling groups, coherent
cross-element morphing, adaptive accessibility, progressive fidelity tiers that
report what they actually resolved to, and fidelity numbers backed by a versioned
harness that diffs against native captures instead of against a screenshot
somebody eyeballed.

The label on every glass control stays real DOM. A `GlassButton` is a `<button>`:
selectable, focusable, IME-capable, and announced by a screen reader as a button.

---

## Install

```bash
npm install @vitreajs/vitrea @vitreajs/vitrea-react
```

The library is called vitrea and publishes under the npm scope `@vitreajs`.
`@vitreajs/vitrea` is the framework-agnostic runtime, `@vitreajs/vitrea-react`
the declarative surface. These two are the only published packages: the
geometry kernel, the motion kernel, the DOM host layer and the WebGPU renderer
are internal and bundled into them at publish time, so an app installs two
packages and gets zero transitive runtime dependencies beyond React itself.

**TypeScript.** The published declarations resolve on their own, on any
TypeScript version, with no `types` entry and nothing extra installed —
including with `skipLibCheck: false`. The WebGPU type names the artifacts use
are declared inside them, and they merge with your own WebGPU types
(TypeScript 6's DOM lib, `@types/web`, or `@webgpu/types`) rather than
competing with them.

### Which package you actually import from

| You are… | Install | Import |
| --- | --- | --- |
| writing a React app | `@vitreajs/vitrea @vitreajs/vitrea-react` | `@vitreajs/vitrea-react` for components, `@vitreajs/vitrea` for types |
| reading the resolved capability state | either | `@vitreajs/vitrea` |
| writing a Vue/Svelte/WC adapter | `@vitreajs/vitrea` | not yet supported — see below |

**One honest limit up front.** `vitrea` contains no DOM code at all, by design
(the purity law: the core, geometry and motion packages never touch `window`,
`document` or `HTMLElement`). The browser host layer — element registration,
plane management, backdrop proxies, the CSS-tier renderer, the WebGPU lifecycle —
ships bundled *inside* `vitrea-react`. So in v1 the only way to render glass in a
browser is through the React bindings. `vitrea` on its own gives you the scene
model, the capability and tier resolver, the material and accessibility policy,
and the frame-scheduler contract; it does not give you a mounted root. A
framework-agnostic host entry point is post-v1 work, not a thing you can reach
today by installing `vitrea` alone.

---

## Quickstart

```tsx
import { GlassRoot, GlassGroup, GlassToolbar, GlassButton, useGlassCapabilities } from "@vitreajs/vitrea-react";

export function App() {
  return (
    <GlassRoot renderer="webgpu">
      {/* Your page. Ordinary DOM, and it stays ordinary DOM. */}
      <YourPage />

      {/* A toolbar creates its own sampling group; `hint` tells the runtime what
          is behind it, because vitrea never pretends to analyse arbitrary DOM. */}
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

Surfaces that are not toolbar members go in an explicit group. A group is the
sampling unit — one backdrop proxy, one blur, shared between its members:

```tsx
<GlassGroup id="hero" hint={{ tone: "light" }}>
  <GlassSurface radius={20} thickness={10}>
    <h1>Anything you like in here</h1>
  </GlassSurface>
</GlassGroup>
```

**A surface has no intrinsic size.** vitrea declares neither position nor size
for one: it measures the box your CSS produced, once per frame, and fits the
material to it. The element itself is portalled into its plane's host layer,
which is a `position: absolute; inset: 0` overlay, so a surface places itself the
way any overlay child does — give it your own width, height and positioning, and
it will be exactly as big as you made it. This is also why press compression and
morph deformation are composed transforms rather than shape changes: a transform
cannot dirty the rect it is animating.

### Glass is a controls-layer material

There is one placement rule, and Apple states it as a prohibition rather than as
advice: **"Don't use Liquid Glass in the content layer."** The material exists to
separate the things you can act on from the things you are reading; putting it on
both collapses that distinction. Apple names both failure modes: "including it in
the content layer can result in unnecessary complexity and a confusing visual
hierarchy", and, for stacking, "avoid applying the material to both layers.
Instead, use fills, transparency, and vibrancy for the top elements."

So: glass on the toolbar, not on the article you are reading through it. Glass on
the row's button, not on the row. And glass on the control, never on the control *and* its
container. Lists and tables are the case Apple calls out by name, and they are
the case a web glass library gets wrong most often, because `asChild` will glass
a `<tr>` as readily as a `<button>`.

vitrea now checks the two compositions that are decidable from structure, at
registration, in dev mode only:

| code | fires when | what it tells you |
| --- | --- | --- |
| `glass-inside-glass` | a registered host sits inside another registered host's subtree | which pair, and to keep the material on whichever of the two is the control while the other takes a fill, a translucency or a vibrant foreground |
| `glass-in-content-layer` | a host is registered on an element whose resolved ARIA role is a list or table structure | which element and which role, and either to move the glass onto the control the row holds or — if it really is a controls-layer container — to give it the role it means, at which point the check stands down |

Both are advisory findings on the diagnostics channel rather than throws, and
both are `devMode`-only: the check runs once per `registerHost` call and never
from a frame, so a production build pays nothing for it. What vitrea does *not*
check is the rest of the rule — whether anything is actually scrolling under a
surface, whether a non-interactive label has been glassed, whether glass and
content intersect at rest. Those need judgement or a per-frame observation, and a
diagnostic that fires on a correct page is worse than no diagnostic.

And to see what the runtime actually resolved to, rather than what you asked for:

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

Run the demo app in this repository to see all of it working, including the
side-by-side native reference pairs:

```bash
pnpm install && pnpm -r build
pnpm --filter demo dev     # http://localhost:5173, add ?renderer=css to force the tier
```

---

## The capability model: the honesty contract, as a feature

Most glass libraries have one quality knob and fail quietly when the platform
cannot honour it. vitrea separates what your app **configures** from what the
runtime **resolves**, and the resolved state is a closed set of legal
combinations rather than a free product of axes — because a free product admits
states that are meaningless (a registered GPU texture with no WebGPU; a
CORS-tainted video reported as exact analysis).

Every group reports:

```ts
interface GlassGroupState {
  configuredSource: "texture" | "dom";      // what you declared — never mutated
  activeRenderer:  "webgpu" | "css";        // what is actually drawing
  samplingBackend: "gpu-texture" | "css-backdrop" | "none";
  refraction:      "true" | "approximate" | "none";
  analysis:        "exact" | "hint" | "none";
  health:          "ok" | "demoted";
  demotionReason?: "no-webgpu" | "no-backdrop-filter" | "tainted-source"
                 | "incompatible-texture" | "no-texture-supplied" | "device-lost"
                 | "probe-failed" | "governor";
}
```

Three properties are worth knowing, because they are the reason the model exists:

**`configuredSource` survives demotion.** You can always see what you asked for
next to what you got. Nothing silently rewrites your intent.

**Every demotion names a reason and a recovery.** `device-lost` recovers when a
device is restored; `tainted-source` when the source is replaced;
`probe-failed` when the probe re-passes. `no-webgpu` names its recovery as
`"none"` — honestly unrecoverable inside the session, rather than implying a
retry that will never succeed.

**Choosing the CSS tier is not a fault.** A root that never requested WebGPU
resolves its groups to `activeRenderer: "css"` with `health: "ok"` and no
demotion reason. Labelling deliberate intent as a fault would invert the whole
point.

### The three healthy configurations

| Configuration | What you get |
| --- | --- |
| **texture + exact** — you register an image, video or canvas as the group's backdrop | Full refraction. Edge lensing visibly bends the backdrop; a larger surface lenses deeper than a small one over the same content. Luminance, variance and edge-density analysis run on the GPU. |
| **dom + hint** — arbitrary page content, plus a `hint` (or an estimator provider) | The browser compositor does the blur through a masked backdrop proxy; the GPU renders rim lensing, tint, glow and morphs. Adaptation comes from your hint. |
| **dom + none** — arbitrary page content, no hint (the default) | Fixed regular material, geometry-driven rim and specular, foreground from tokens or `color-scheme`. |

vitrea does not automatically pixel-analyse arbitrary DOM, and never claims to.
There is a built-in best-effort estimator that reads known background colours and
images where CORS permits, and it is documented as an estimator every place it
appears — not as pixel analysis, because that is not what it is.

### Registering a texture backdrop

The texture path is two steps, and it is two because of the purity law above:
`vitrea` may not hold an `HTMLImageElement`, so it cannot be the thing you hand
pixels to. The group **declares** the source; the root **supplies** it.

```tsx
import { GlassGroup, GlassSurface, useGlassRoot } from "@vitreajs/vitrea-react";

function Hero() {
  const root = useGlassRoot();

  return (
    <>
      {/* 1. Declare. `configuredSource` stays "texture" through any demotion. */}
      <GlassGroup id="hero" backdrop={{ kind: "texture", id: "hero" }}>
        <GlassSurface radius={26} thickness={18}>…</GlassSurface>
      </GlassGroup>

      {/* 2. Supply. The id is what joins the two halves; the order does not
             matter, and `setBackdropTexture` marks the source dirty itself, so
             handing the pixels over is the whole wiring. */}
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

The other two forms are `{ kind: "canvas", canvas }` and `{ kind: "video", video }`.
A video and a live canvas are re-imported on every frame that samples them; a
decoded image is imported once. Passing `undefined` withdraws a source's pixels.

Declaring a texture and never supplying one is not a silent hole: the group
resolves to `health: "demoted"` with `demotionReason: "no-texture-supplied"` and
keeps drawing tint, rim and glow. The readout names the missing half.

**Where the texture is placed.** The renderer maps the source over the **whole
viewport**, cover-fit — it fills the viewport and the overflow is cropped
symmetrically, the same geometry as `object-fit: cover` on a
`position: fixed; inset: 0` element. Not over the group, and not over the
surface.

This matters whenever your app paints the same image itself, which is the usual
case: the picture is on the page and the glass sits on top of it. The two
mappings have to agree. An `<img>` sized to a region, under a texture mapped to
the viewport, samples a different crop of the same file — and the mismatch
appears as the glass showing the wrong part of the picture, which reads
convincingly like a lensing artefact rather than a registration error. Paint your
copy viewport-sized and `object-fit: cover`, or accept that the two will differ.

### Tiers degrade within themselves before they switch

The quality governor first reduces refraction resolution, adaptation cadence and
edge analysis *inside* the current tier. Switching tiers happens only with long
hysteresis and a cooldown, and never mid-interaction. Intra-tier degradation is
not a state change, so it does not churn your readouts.

---

## Fidelity

vitrea's material is tuned against real captures of Apple's material, not against
recollection. `apps/reference-apple` is a SwiftUI harness running the actual
`glassEffect` API; `packages/calibration` captures both sides over identical
pre-rendered raster backgrounds and diffs them on shape, material, motion and
perceptual axes, keyed by native profile × web cell.

The full record is
[`docs/doperpowers/specs/c9a-fidelity-claims.md`](https://github.com/SSFSKIM/designer/blob/main/docs/doperpowers/specs/c9a-fidelity-claims.md).
The claims, in the words that document states them:

### The texture tier

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

### The CSS (dom) tier

> **No cross-engine pixel-wise fidelity claim is made for the dom tier, and none
> can be. On Chromium, in the same cell with `renderer: css` and
> `samplingBackend: css-backdrop`: OKLab ΔE 0.0091 mean / 0.0240 worst and SSIM
> 0.9700 mean / 0.9304 worst over the 12 light calibration cells, ΔE 0.0108 /
> 0.0273 over the 6 validation cells, and ΔE 0.0291 mean / 0.0560 worst with SSIM
> 0.9373 / 0.9205 on the six scenes held out of all tuning. Silhouette IoU 0.9424
> mean over the calibration cells and 0.9684 on holdout, with a 1.06 px mean
> contour distance.**

This tier does not hold a material of its own: it **converts** the one the root
carries, through a mapping whose single fitted constant is tuned against the
cross-tier difference rather than against the fixtures. That is a deliberate
trade, recorded rather than hidden — a CSS tier fitted independently against
Apple is free to drift from the GPU tier the moment either is retuned, while a
converted one inherits the GPU tier's fidelity by construction. The price is now
0.0099 against Apple where an independent fit reached 0.0094.

> **Tier coherence, and only in this wording.** On Chromium, a group that demotes
> from the WebGPU texture tier to the CSS tier keeps the same material to within
> 1.3% of its interior level in the mean and 11% on the worst measured cell, at a
> cross-tier OKLab ΔE of 0.0063 mean / 0.0124 worst over the fitted sets and
> 0.0188 / 0.0313 over the held-out ones. It is **not** the same rendering —
> refraction is absent on the CSS tier by contract (`refraction: "none"`) — but
> the material's opacity, tint and frost do not change visibly on demotion.

Exact coherence is unreachable, and the arithmetic says so before any capture
does: the renderer applies its transfer function *after* the blend and the page
applies it *before*, so matching the two composites needs a different CSS alpha at
every backdrop level (0.761 at linear 0.05, 0.635 at 0.8). One scalar is exact at
one level and necessarily wrong either side of it. What remains is a property of
`backdrop-filter`, not a residual anyone can tune away.

The cross-engine absence is not laziness. Gecko and WebKit render
`backdrop-filter` as a complete no-op in every automatable capture path — headless
and headed Playwright, retail `--screenshot`, WebDriver BiDi, WKWebView
`takeSnapshot` — while rendering it correctly live. A screenshot comparison on
those engines measures a blank image. Their visual behaviour is verified by a
manual self-scoring page instead, and that is a release gate rather than a CI
check.

### What is *not* claimed

- **Never "pixel-identical to Apple."** Every figure above is scoped to one
  native profile and one web cell, and says so.
- **No press-state fidelity claim.** Apple's `Glass.interactive(true)` opts the
  material into *responding* to press input rather than posing it pressed, and
  Apple exposes no declarative pressed pose — so the native "pressed" captures
  are byte-identical to their rest counterparts (verified by SHA-256, all four).
  Those cells compare vitrea's pressed pose against Apple's rest pose. They were
  also excluded from the tuning decision.
- **No adopted pass/fail thresholds.** The thresholds in the claims document are
  *proposals for a human gate*, not self-certification.
- **1× only.** The capture machine reports `backingScaleFactor` 1.0, so every
  figure is a 1× figure. The two accessibility-mode profiles have no captures at
  all yet; macOS exposes those display modes as read-only, so each needs its own
  capture run.
- **The glass-over-glass cells are a mixed-backend claim.** Natively the upper
  `glassEffect` samples the lower one's rendered output; on the web that
  relationship *is* the plane sandwich, so those cells resolve to
  `gpu-texture + css-backdrop` with `refraction: "approximate"` even on the GPU
  tier. They are counted in the holdout numbers, and they are the two lowest
  SSIM figures in that set.
- **Tier coherence is a Chromium measurement of a material's level**, on one
  profile, at 1×. It does not say the two tiers are identical, and it does not
  hold on Gecko or WebKit — nothing measurable does there.
- **No fidelity claim for the author tint.** `GlassSurface`'s `tint` prop is
  implemented on both tiers and visually verified on both, but every constant in
  the tone curve that turns an author's colour into "a range of tones mapped to
  content brightness underneath" is an advisory default. The tinted native
  captures that would fit them are a scheduled extension of the capture harness;
  until they exist the tint's appearance is designed, not calibrated.

---

## Browser support

Two tiers, and the CSS tier is a hard requirement rather than a courtesy —
WebGPU is not everywhere, and pretending otherwise is what the capability model
exists to prevent.

| Engine | WebGPU (texture tier) | CSS tier |
| --- | --- | --- |
| **Chromium** (Chrome, Edge) | Default-on from 113 on desktop, 121 on Android | Yes. Byte-exact backdrop-proxy sampling equivalence, measured across 122 capture variants |
| **Safari / WebKit** | Default-on from Safari 26 | Yes, manually verified — automated capture cannot observe `backdrop-filter` on this engine |
| **Firefox / Gecko** | Default-on from 141 on Windows, 145 on ARM Mac; **still flagged on Linux** | Yes, manually verified — same automated-capture blindness |

Where WebGPU is missing, every group resolves to `activeRenderer: "css"` with
`demotionReason: "no-webgpu"`, renders presentable CSS-tier glass, and logs no
errors. Asking for the GPU tier is not the same as getting it, and
`useGlassCapabilities()` is how you find out which happened.

### Contract limits you should know before designing around it

- All glass lives inside `GlassRoot`'s managed planes. v1 ships exactly two —
  base and one overlay — and menus portal internally to the overlay plane.
  Arbitrary interleaving with foreign stacking contexts is out of contract.
- Two glass surfaces must not overlap **within one plane**. This is a dev-mode
  error rather than an assumption: the paint sandwich cannot place one surface's
  body above another surface's DOM label. Overlap across planes is the supported
  case and is what the morph uses.
- Glass hosts must not sit beneath an ancestor whose `filter`, `opacity`, `mask`
  or `clip` changes the backdrop root. The relevant CSS specification explicitly
  lacks working-group consensus here, so engines may legitimately differ — which
  is why a startup conformance probe validates the proxy topology and demotes a
  group to the CSS tier when sampling proves non-equivalent, rather than trusting
  a support query.
- v1 corner radii are uniform. The `radii` API keeps its four-component shape,
  but a non-uniform set is a dev-mode error; per-corner algebra is post-v1.
- **One author tint seed per group.** A tint is declared per surface and its
  strength is honoured per surface, but a group is one optics pass and carries
  one seed, so two *different* tint colours in one group raise a dev-mode warning
  and the WebGPU tier draws them all in the first surface's colour. One coloured
  control among plain ones — Apple's own guidance for tinting — is the supported
  composition.

---

## Testing your app

### The readout is trustworthy; the environment may not be

`useGlassCapabilities()` reports what resolved. If it says
`demotionReason: "no-webgpu"`, that session genuinely had no WebGPU — the
readout is not the thing to doubt. What is worth doubting is the environment,
because one browser-automation default removes WebGPU without removing anything
you would notice.

**Playwright's bundled headless shell hands back a software adapter.** This repo
measures three different answers on one machine depending on how Chromium is
launched: the default headless shell resolves to a SwiftShader adapter, while
`channel: "chromium"` — the full browser binary — resolves to real hardware. A
suite that never asks for the channel runs entirely green on the CSS tier, and
every readout in it honestly says `no-webgpu`, which is what makes this the worst
kind of failure: nothing is broken, it is just the other tier, and the
instrumentation agrees with the wrong answer.

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

Two further requirements are not optional. `navigator.gpu` is undefined outside a
secure context, so serve the page over `http://localhost` — on `file://` and
`data:` URLs the absence reads exactly like "no WebGPU on this machine". And a
test that means to assert the GPU tier should **fail** when no adapter answers
rather than skip, and fail rather than quietly accept a software one; otherwise
it asserts nothing.

### What is in the DOM differs by tier

The backdrop-proxy elements are not a general debugging landmark. A
`[data-vitrea-proxy]` element exists only where the GPU tier is sampling
arbitrary DOM:

| Resolved state | What the runtime puts in the DOM |
| --- | --- |
| `activeRenderer: "webgpu"`, `samplingBackend: "css-backdrop"` | one `[data-vitrea-proxy]` per group **per plane** it has members on |
| `activeRenderer: "webgpu"`, `samplingBackend: "gpu-texture"` | no proxy — the backdrop is a GPU texture, so there is nothing in the page to filter |
| `activeRenderer: "css"` | no proxies at all: the CSS tier applies `backdrop-filter` **in place**, on each glass host element |

So "find the proxy" is an assertion about one resolved state, not about the
dom-backdrop path in general — and its absence on the CSS tier is the design
rather than a fault, which is also why `probe-failed` can demote to that tier at
all: the very thing that failed is not on its path. To assert the CSS tier, read
the host element's own computed `backdrop-filter`, `background-color` and
`border-color`. To assert which tier you are on, read `useGlassCapabilities()`.

---

## Accessibility

Accessibility is policy in `vitrea`, applied by the host layer through media
queries, with per-root prop overrides. It is resolved, not bolted on: each
preference has a declared consequence for the material or the motion, and the
strictest active preference wins.

| Preference | What changes |
| --- | --- |
| `prefers-reduced-motion` | No elastic overshoot, no deformation, no shimmer travel. Morphs become non-elastic interpolation. Direct-manipulation positional continuity is preserved — reduced motion is not *no* motion. |
| `prefers-reduced-transparency` | More frost, less refraction, higher occlusion. |
| `prefers-contrast: more` | Stronger borders, near-monochrome foregrounds, reduced ambient tint. |
| `forced-colors: active` | System colours, borders, **no glass** — every optical axis goes with it. |

The first three are overridable per root:

```tsx
<GlassRoot reducedTransparency={true} increasedContrast="system" />
```

`forced-colors` deliberately has **no** override prop, and its absence is
enforced in the type system: an operating-system colour mandate is not an app's
to switch off.

`prefers-reduced-transparency` is not Baseline across engines. On a platform that
cannot answer the query, leaving it on `"system"` silently resolves it to false
and the user's preference is lost — so vitrea emits a diagnostic saying exactly
that. The explicit override is load-bearing, not a courtesy.

One documented obligation on your side: content that vitrea portals into a plane
leaves its original DOM position, so if that content was inside a landmark
region, you own re-establishing the landmark. A `role`/landmark seam on the morph
component is deferred post-v1 API work.

---

## License

Apache License 2.0. See [`LICENSE`](https://github.com/SSFSKIM/designer/blob/main/LICENSE).

"Liquid Glass" is the name of Apple Inc.'s design language, referenced here
descriptively to say what this library replicates. vitrea is not affiliated with,
endorsed by, or sponsored by Apple Inc. See [`NOTICE`](https://github.com/SSFSKIM/designer/blob/main/NOTICE).
