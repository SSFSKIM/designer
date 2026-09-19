# vitrea-web

**The browser host for [vitrea](https://www.npmjs.com/package/@vitreajs/vitrea) —
mount a glass root from any framework, or none.**

vitrea replicates Apple's Liquid Glass material on the web: real-time
size-parameterized lensing, per-element backdrop adaptation, container-scoped
sampling, and shape-to-shape morphing. `@vitreajs/vitrea` is the pure runtime and
holds no DOM code by design. This package is the half that touches the browser —
element registration, the plane sandwich, per-group backdrop proxies, the
conformance probe, the CSS-tier renderer, and the WebGPU lifecycle — and it is
what turns the runtime into pixels.

If you are writing React, install
[`@vitreajs/vitrea-react`](https://www.npmjs.com/package/@vitreajs/vitrea-react)
instead; it depends on this package and gives you components. Reach for this one
when you are writing plain JavaScript, or an adapter for Vue, Svelte, Angular or
Web Components. It is the same `createGlassRoot` the React bindings themselves
are built on: there is no privileged path.

---

## Install

```bash
npm install @vitreajs/vitrea-web
```

`@vitreajs/vitrea` is this package's one declared dependency and is installed for
you. There are no others — the geometry kernel, the motion kernel and the WebGPU
renderer are internal and bundled in at publish time.

**TypeScript.** The published declarations resolve on their own, with no `types`
entry and nothing extra installed, including with `skipLibCheck: false`. The two
WebGPU names the surface uses are declared inside the artifact and *merge* with
your own WebGPU types (TypeScript 6's DOM lib, `@types/web`, or `@webgpu/types`)
rather than competing with them.

---

## Quickstart

```ts
import { createGlassRoot, GLASS_CHANNEL_PROPERTIES } from "@vitreajs/vitrea-web";

// 1. The root builds the plane sandwich and starts a frame loop.
const root = createGlassRoot();

// 2. A sampling group: one backdrop read, shared by every surface in it.
root.registerGroup({ id: "controls" });

// 3. Your element, placed by you. vitrea never creates or moves your DOM.
const button = document.createElement("button");
button.textContent = "Share";
button.style.cssText = "position:absolute;left:120px;top:220px;width:160px;height:44px";
root.plane("base").hostLayer.append(button);

// 4. Bind it to the scene. The handle is how you patch it afterwards.
const handle = root.registerHost({
  host: button,
  groupId: "controls",
  shapeFamily: "fixed-rounded-rect",
  radii: [14, 14, 14, 14],
});

// 5. Per-frame work joins the loop the root already runs.
const stop = root.subscribe(({ deltaMs }) => {
  // advance your own springs, write the material's channels
  button.style.setProperty(GLASS_CHANNEL_PROPERTIES.press, "0");
});

// Teardown, in the order things were built.
stop();
handle.release();
root.removeGroup("controls");
root.destroy();
```

A complete, runnable version of exactly this — with interaction wired up — is
[`e2e/fixtures/vanilla.ts`](./e2e/fixtures/vanilla.ts). It is executed against
Chromium, Firefox and WebKit on every run of this package's suite, so the
snippet above is a tested path rather than a promise.

---

## What you get, and what stays yours

**Yours.** Every element. `registerHost` binds an element you created and placed;
it never wraps, replaces or reparents it. That is why a glass button is a real
`<button>` — focusable, IME-capable, announced as a button — with the material
drawn on canvases above and below it rather than instead of it. The one property
vitrea takes ownership of on a registered host is `transform`, and it says so
(`host-inline-transform` fires in dev mode if you had one).

**Ours.** The plane sandwich (`root.plane(...)` hands you the layer to append
into), the per-group backdrop proxies, the batched layout read — the steady state
performs no layout reads at all — the tier decision, and everything the material
writes.

## Material presence without a framework

```js
const surface = root.registerHost({ host: button, groupId: "controls", present: true });
surface.update({ present: false }); // Animate the glass to identity; the button stays.
surface.update({ present: true });  // Reverse from the current material value.
```

`present` defaults to `true` and is independent of hover, press, focus and disabled
state. An initially absent surface starts at identity. Changes use the motion
kernel's monotonic 220 ms ease; Reduced Motion steps to the destination on both
tiers. That ease is the kernel's built-in default and this root takes no motion
profile of its own, so it is the same ramp for every app; retuning it means
publishing the channel yourself, below. `release()` still tears down
synchronously, so animate out by changing presence before deciding when to remove
your content.

The root publishes `--vitrea-materialization` in `[0, 1]` on the host, consumed by
both tiers. A custom motion binding can publish that channel directly instead of
using `present`. It scales optical material terms, **not element opacity**: at 0
the glass is absent while your element, geometry, semantics and published
foreground tokens remain. Never fade
the host or its ancestors as a substitute — doing so cuts off backdrop sampling.
Content visibility, pointer handling and contrast over the uncovered page remain
the app's responsibility. The timing is authored and has no measured native
reference; the tier-specific optical limits are recorded in claims §5.132.

## Tint without a framework

```ts
import { glassTint } from "@vitreajs/vitrea";

// A group's seed is core's parsed tint, not a string, and rides the group's
// material profile — so the profile's `variant` comes with it.
root.registerGroup({
  id: "controls",
  material: { variant: "regular", tint: glassTint([1, 0.584, 0]) },
});

// A surface takes any CSS colour the engine parses, and overrides its group.
const handle = root.registerHost({ host: button, groupId: "controls", tint: "#ff9500" });

handle.update({ tint: "rgb(255 149 0 / 50%)" }); // the colour's alpha IS the strength
handle.update({ tint: null });                   // untinted, even under a tinted group
handle.update({ tint: undefined });              // drop the override, inherit again
```

A surface that declares no `tint` inherits the group's seed; `null` clears an
inherited one, the way `Glass.tint(nil)` does. In a patch the distinction is the
key's presence, as it is for the other overrides on `update()`: `{ tint: undefined }`
removes this surface's override, while an absent `tint` key leaves it alone.
Strength 0 is not a tint — the material is byte-identical to an untinted one.

The surface path takes a string because that is what an app already has; the group
path takes `glassTint([r, g, b], strength)`, sRGB channels in 0..1. To hand a group
a CSS colour instead, parse it the way the React binding does —
`createTintParser(document)` once per document, then
`resolveTintDeclaration(colour, parse, groupId, root.diagnostics)`. A colour neither
parser resolves leaves the surface **untinted** and reports `tint-unparseable` rather
than guessing at it; outside a browser (jsdom, SSR) only the numeric syntaxes
resolve, so write `#rrggbb`, `#rrggbbaa`, `rgb()` or `rgba()` there.

A group is one optics pass carrying one seed, so a group tint plus a member that
overrides it is two: dev mode reports `tint-mixing`, and the tiers disagree there —
WebGPU paints them all with the first surface's colour while the CSS tier honours
each. Give a second colour its own group. The tint is a seed the material tone-maps
against the backdrop it is already sampling, not a fill, and it never moves the
material's own opacity; the foreground tokens below are published against the tinted
material, so the ink follows the colour without the app deciding it again.

## Foreground tokens and ownership without a framework

Every registered host publishes `--vitrea-foreground` and its `-secondary`,
`-tertiary` and `-quaternary` levels. The primary is Apple's automatic macOS label
ink through the vibrant operator; secondary is raised where the primary can hold
WCAG 4.5, while tertiary and quaternary deliberately carry no body-text floor.
Use the tokens directly when the app owns its content.

Set `vibrant: true` on `registerHost` or `handle.update()` when vitrea owns the
label. This does not change the token value. It raises the runtime's `color` rule
from the zero-specificity `:where([data-vitrea-node])` path to
`[data-vitrea-vibrant]`, so it survives a reset such as `button { color: … }`;
set it back to `false` to return to the token path. An application rule that names
the element still wins. Presence 0 removes the vibrant marker so identity leaves
content exactly as the app wrote it.

## The pieces

| What | Where |
| --- | --- |
| mounting, frames, registration | `createGlassRoot`, `GlassRoot` |
| per-element handle | `registerHost` → `GlassHostHandle` (`update`, `promoteTo`, `setOwnedTransform`, `release`) |
| planes | `root.plane(plane)` → `PlaneLayers`; `GLASS_PLANES` |
| interaction channels | `GLASS_CHANNEL_PROPERTIES` — write 0..1, the material reads |
| findings | `root.diagnostics`, `consoleDiagnosticSink()`, `VitreaDiagnostic` |
| capability answers | `root.capabilities(groupId)`, `root.accessibility`, `root.webgpu`, `root.colorScheme`, `root.windowActivation` |
| how far apart two groups must sit | `samplingPaddingFor({ members, material })` |
| colour scheme | `colorScheme: "light" \| "dark" \| "auto"`, `root.setColorScheme`, `darkMaterialProfile` |
| window activation | `windowActivation: "auto" \| "active" \| "inactive"`, `root.setWindowActivation`, `setWindowActivation(root, value)`, `recededMaterialProfile` |
| WebGPU | `renderer: "webgpu"`, `root.ready()`, `root.replaceDevice(device)` |

Everything else this package exports is exported because the React bindings and
the WebGPU renderer compose against it directly, and because a test should be
able to reach the decision that failed rather than the whole runtime. Those are
public but not the path an app takes.

---

## Colour scheme

The material is measured per colour scheme, so a dark page needs the dark
material rather than the light one dimmed. Ask for it at the root:

```ts
const root = createGlassRoot({ colorScheme: "auto" }); // "light" | "dark" | "auto"
```

`"light"` is the default, and it is the material the renderer's own constants
are: nothing moves for an app that upgrades into this option. `"dark"` selects
`darkMaterialProfile`, the patch recorded in vitrea's own calibration profile for
Apple's dark-mode material, and `"auto"` follows `prefers-color-scheme` and
re-derives both tiers when the system flips. `root.colorScheme` reports which of
the two is actually drawing, and `root.setColorScheme(...)` changes it on a live
root — a scheme change is a material change, not a reason to tear a root down.

An app that resolves its own scheme somewhere vitrea cannot see can pass the
patch directly (`materialProfile: darkMaterialProfile`), and an app that wants
the dark material with a tuning of its own can do both: the scheme selects the
base and `materialProfile` merges over it, leaf by leaf.

### Which macOS the material is measured against

Everything above is measured against **macOS 26.5**, and that is what the package
draws today. macOS 27 changed the material under every app — the body's level over
a dark backdrop, the rim's amplitude and width, and how much of a backdrop's
structure survives it — and vitrea is refit to it as **patch documents beside the
26.5 ones rather than as a new default**:

| document | what it is |
| --- | --- |
| `packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json` | the identity with the renderer's own constants — "light 26.5" is the absence of a patch |
| `…/apple-macos-26.5-1x-dark-standard.json` | `darkMaterialProfile`, the patch selected by `colorScheme: "dark"` |
| `…/apple-macos-27.0-1x-light-standard-glass0.5.json` | the macOS 27 light material, serving both scales and both light accessibility states |
| `…/apple-macos-27.0-1x-dark-standard-glass0.5.json` | the macOS 27 dark material |

All four are patches over the same renderer default. **A document is two options,
not one**, because a material lands on two tiers: its `patch` is the renderer's
material and goes to `materialProfile`, and its sibling `cssTierMapping` is what
that same material costs to express as `backdrop-filter` plus an overlay and goes
to `cssTierMapping`. Pass only the first and a page draws the 27 material on the
GPU tier while its CSS-tier visitors keep the 26.5 blur:

```ts
import doc from "…/profiles/apple-macos-27.0-1x-light-standard-glass0.5.json"
  with { type: "json" };

const root = createGlassRoot({
  materialProfile: doc.patch,
  cssTierMapping: doc.cssTierMapping,
});
```

The 26.5 documents have the same shape — the light one is the identity, so its
`patch` changes nothing, and the dark one is what `colorScheme: "dark"` already
selects for you.

**No option takes a whole document today.** Reading one into a root is part of the
runtime seam below, so until that lands the two fields are handed over by hand,
and `@vitreajs/vitrea-react`'s `<GlassRoot>` surfaces **neither** of them —
`cssTierMapping` deliberately, since it is calibration's seam rather than an
application knob, and `materialProfile` not yet — so a React app cannot select a 27
document at all before that change.

**What this release does not yet do is select one for you**: the package still
draws the 26.5 material by default, and the runtime seam that makes the 27 material
a page's default lands in the next change. The documents are in the repository
rather than in the published tarball, because a published package that loaded a
calibration file would be shipping a data dependency for numbers that never move
between releases.

The `-glass0.5` in the key is macOS 27's appearance slider, `NSGlassTintAmount`, at
the position a Mac ships with; the material was measured there. The 27 documents
name no new **renderer** constant — the same optical fields the 26.5 ones carry, at
their own values — but they do set one CSS-tier key the 26.5 documents never do:
`cssTierMapping.blurSigmaScale`, at **2.2** against the shipped default of 1. It is
the CSS tier's half of the 27 diffusion refit — the one constant measured to move
that tier's worst cell at all — and it is why the document's `cssTierMapping` has
to be passed alongside its `patch`. The 27 dark document carries a `cssTierMapping` section for
the same reason where the 26.5 dark document has none. Each document also records a
`resolvedMaterialSha256` over the material it resolves to, pinned in
`packages/calibration/test/tuned-profiles.test.ts`.

**A backdrop hint and the colour scheme are different things.** A group's
`hint: { tone, luminance }` states the tone of what is BEHIND the surface, which
is what the adaptation and the foreground decision read; the scheme states which
material the surface is made of. A dark page can legitimately hand a light hint
to a surface sitting over a white card.

**Ordinary page content uses the profile material too.** A WebGPU group over DOM content resolves
`samplingBackend: "css-backdrop"`: its proxy supplies the browser's blur and the canvas draws
the profile's body, tint shade, rim and shadow at the group's known backdrop tone, with each
member's own size law. This is approximate refraction, not texture sampling or a lens. A real
`hint: { tone: "dark", luminance: measuredLevel }` can supply the tone; without a hint or another
measured tone, vitrea does not guess what arbitrary page content looks like, so tone response
and dark-backdrop collapse remain unavailable. A scalar level cannot describe a page's local
colour or texture either. Registered image, canvas and video backdrops retain the sampled path.

The page's own background is still the page's: vitrea does not write your tokens,
so an app offering "follow the system" reads `prefers-color-scheme` for its own
colours as well as passing `"auto"` here.

`recededMaterialProfile.light` and `.dark` are the measured differences the pose below selects, and
they are exported so an app can reach the endpoint directly — a preview that is never a window, a
harness that captures the receded appearance. Select the entry for the resolved scheme and merge it
over that scheme's material; for example,
`createGlassRoot({ colorScheme: "dark", windowActivation: "inactive" })`.

---

## Window activation

Apple's Liquid Glass recedes when its window loses focus, and vitrea models that as a pose of the
**root**: a window is active or it is not, once per document, so no individual surface carries the
answer and it is not a seventh interaction state.

```ts
const root = createGlassRoot({ windowActivation: "auto" }); // "auto" | "active" | "inactive"
```

`"auto"` is the default and follows the window's own focus. `"active"` and `"inactive"` pin the
pose and win over what the window is doing, which is what a preview pane, a screenshot or a capture
harness needs. `root.setWindowActivation(value)` moves a live root and takes effect on its next
frame; `setWindowActivation(root, value)` is the same call as a free function, for a caller holding
a root rather than writing against its methods. `root.windowActivation` reports which pose is
actually drawing — `"active"` or `"inactive"`, with `"auto"` already folded.

What feeds `"auto"` is `document.hasFocus()` on the window the root was created for, re-read
whenever that window fires `focus` or `blur`. Visibility is a separate fact: a document behind
another window can remain `"visible"` while unfocused, so `visibilitychange` does not select this
pose. A `blur` event dispatched by page script cannot invent the answer either: the event says a
reading is stale, and `document.hasFocus()` supplies it. Unfocused test documents (including
jsdom) recede under `"auto"`; deterministic material tests should explicitly select their pose.

The pose is a material change and travels the same path every other one does — the receded
difference for the resolved colour scheme, merged and applied through `applyMaterialProfile`, so the
CSS tier re-derives its declarations and the WebGPU tier takes new uniforms. Two frozen endpoints,
with no intermediate profile document: the existing CSS transitions carry the visual transit,
while the GPU takes the selected endpoint on its next frame. It is merged **over** an app's own `materialProfile`, so where the two name the same
constant the recede wins for as long as it is on.

The endpoints remove the outer shadow and the bright rim and retain an author's tint strength as an
achromatic shade. The native reference is macOS 26.5, with 1x-only light accessibility evidence, and
it is a fitted endpoint rather than a pixel-match guarantee: photo chroma, intermediate dark levels
and large-surface scattering remain measured gaps (claims §5.130, §5.145–§5.147). In particular a
full-strength neutral tint loses background colour that the native inactive material can retain.

---

## Frames

The root owns a cadence: five scene phases per frame, driven by
`requestAnimationFrame`. `autoStart: false` turns that off and `root.runFrame(t)`
steps it by hand, which is what the calibration harness and every test in here
do.

`root.subscribe(listener)` joins that loop and returns its unsubscribe. Listeners
run **after** the frame, so they observe a settled scene and may register, patch
and measure like any other caller. Use it rather than starting a second
`requestAnimationFrame` of your own: two loops mean two wake-ups per frame and no
declared ordering between them. `deltaMs` is `0` on the first frame and should be
capped by whatever integrates it — a backgrounded tab delivers an arbitrarily
large first step on return.

A listener that throws is reported as `frame-listener-failed` and unsubscribed.
One adapter's bad frame must not stop the material drawing.

---

## Diagnostics

Dev mode is on by default and findings go to the console. They are written to name
what to do, not just what is wrong — a host placed outside its plane, a sampling
padding below 3σ of its own blur, glass nested inside glass, an engine version
with a recorded defect and its workarounds.

```ts
const root = createGlassRoot({
  devMode: process.env.NODE_ENV !== "production",
  diagnosticSink: ({ origin, diagnostic }) => report(origin, diagnostic.code, diagnostic.message),
});
```

Findings are deduplicated by code and subject, so a condition that persists across
frames is reported once. Structural mistakes — an unknown id, a duplicate id, a
still-referenced source — are not diagnostics: those throw, because continuing
past them would leave a half-built scene.

---

## License

Apache-2.0. See [LICENSE](./LICENSE) and [NOTICE](./NOTICE).
