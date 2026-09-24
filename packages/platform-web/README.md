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
| how far apart two groups must sit | `samplingPaddingFor({ members, material, profile?, cssTierMapping? })` — omit `profile` for the default document, pass it as `undefined` for an endpoint that has none |
| which measured material draws | `materialProfileDocument`, `macos27MaterialProfileDocument`, `macos26MaterialProfileDocument`, `root.material` |
| colour scheme | `colorScheme: "light" \| "dark" \| "auto"`, `root.setColorScheme` |
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

`"light"` is the default. The scheme picks one endpoint out of the material
document the root selected — under the default document that is the macOS 27
light or dark patch, and under `macos26MaterialProfileDocument` it is the macOS
26.5 pair, whose dark half is the exported `darkMaterialProfile` and whose light
half is the renderer's own constants. `"auto"` follows `prefers-color-scheme` and
re-derives both tiers when the system flips. `root.colorScheme` reports which of
the two is actually drawing, and `root.setColorScheme(...)` changes it on a live
root — a scheme change is a material change, not a reason to tear a root down.

An app that resolves its own scheme somewhere vitrea cannot see can name the
endpoint directly (`materialProfile: macos27DarkMaterialProfile`), and an app
that wants a scheme's material with a tuning of its own can do both: the scheme
selects the base and `materialProfile` merges over it, leaf by leaf. Take the
endpoint from the document the root is drawing — a macOS 26.5 patch over the
macOS 27 base is neither measured material.

### Which macOS the material is measured against, and how to choose

Every optical number in this package is measured against Apple's own material on
a Mac, and macOS 27 changed that material under every app — the body's level over
a dark backdrop, the rim's amplitude and width, the outer shadow, how much of a
backdrop's structure survives, and what a surface becomes when its window loses
focus. **From 0.19.0 a page draws the macOS 27 material by default.**

That default is a *selection*, not a rewritten constant. The renderer's own
`DEFAULT_MATERIAL_PROFILE` still holds the macOS 26.5 light material, and every
shipped material is a patch over it, so both macOS 26.5 documents keep the
fingerprints they were recorded with while what a page draws moves.

```ts
import { createGlassRoot, macos26MaterialProfileDocument } from "@vitreajs/vitrea-web";

createGlassRoot({ container });                                      // macOS 27
createGlassRoot({ container, materialProfileDocument: macos26MaterialProfileDocument });
```

`@vitreajs/vitrea-react` takes the same value as a prop:
`<GlassRoot materialProfileDocument={macos26MaterialProfileDocument}>`.

**A document is one value, and it carries four patches and a mapping.** That is
what makes the option worth having: a material lands on two tiers and in two
window poses, and the parts have to travel together.

| what a document holds | why it is in there |
| --- | --- |
| the active patch, per colour scheme | the material is measured per scheme, and only one scheme's numbers can be the renderer's defaults |
| the receded difference, per colour scheme | an unfocused window's material is its own measurement — its rim collapses, its tint keeps its shade and loses its chroma, and its body carries its own backdrop tone response. On **neither** generation does a receded surface cast an exterior shadow: from 0.22.0 the macOS 27 endpoints' six occlusion anchors, `liftAmplitude` and `reducedTransparencyOcclusion` are 0, as the macOS 26.5 endpoints' always were (claims §5.168 §4) |
| `cssTierMapping` | what that same material costs as one `backdrop-filter` plus an `rgba()` overlay — macOS 27 sets `blurSigmaScale` to 2.2 against the module default of 1, which is the CSS tier's whole share of the 27 diffusion refit |

The two shipped documents and the calibration documents they are generated from:

| document | profile documents |
| --- | --- |
| `macos27MaterialProfileDocument` (the default) | `packages/calibration/profiles/apple-macos-27.0-1x-{light,dark}-standard-glass0.5{,-receded}.json` |
| `macos26MaterialProfileDocument` | `…/apple-macos-26.5-1x-light-standard.json` (the identity with the renderer's own constants), `…/apple-macos-26.5-1x-dark-standard.json`, and the receded endpoints fitted into `src/receded-profile.ts` |

The individual patches are exported by name as well —
`macos27LightMaterialProfile`, `macos27DarkMaterialProfile`,
`macos27RecededMaterialProfile`, `macos27CssTierMapping`, `darkMaterialProfile`,
`recededMaterialProfile` — for an app composing a material of its own over one
of them. `materialProfile` and `cssTierMapping` still take a patch each and merge
over whatever the document selected, which is the shape to reach for when tuning
one leaf rather than choosing a reference.

**What drew is a readout, not an assumption.** `root.material` and every group's
resolved state name the endpoint that actually drew — its profile key, its
`resolvedMaterialSha256`, and whether an app merged a patch of its own over it:

```ts
root.material;
// { name: "apple-macos-27.0-glass0.5", platform: "macOS 27.0",
//   profileKey: "apple-macos-27.0-1x-dark-standard-glass0.5-receded",
//   resolvedMaterialSha256: "7c454858a3cbad5b", tuned: false }
```

**The four digests moved again at 0.22.0, and this time the shadow's EXTERIOR
did** (claims §5.168). `spreadPx` — the distance the shadow's silhouette is grown
by before it is blurred — was 3.10 CSS px inherited from the macOS 26.5 default
and had never been fitted on the macOS 27 bed; it ships at **0.50** on the light
document and **1.80** on the dark one, which are the two beds' own readings, with
`offsetPx` unmoved at 7.95 because a rendered coordinate step over Apple's own
interval moves the fit's objective by 4 × 10⁻⁷. The six occlusion anchors are
re-solved against what the shadow does between 3 and 48 CSS px, and the dark
document's σ slope moves inside B1's window. **And the two RECEDED documents'
amplitude is 0**: Apple's unfocused window removes no light at all from 3 CSS px
outward, on 121 of 121 non-holdout inactive cells and 235 of 235 on the frozen
macOS 26.5 bed, where vitrea had been drawing the active shadow leaf for leaf. So
a window that loses focus drops its shadow and `outerShadowReachPx` returns 0 in
that pose — **fading out on the CSS tier**, where the `box-shadow` carries a
transition, and in one frame on the WebGPU tier, whose two poses are fixed
endpoints rather than an interpolation. W32's four digests were
`40a6dec2dc34c748` (light), `bd1814fac34f9b30` (dark), `f34dcc03e2774db3` (light
receded) and `6b6237b7ae241638` (dark receded).

W33 G1b's lift stand-down and thick-anchor compensation (claims §5.172) move the
active digests to `dcbccbd9feac9881` (light) and `e59f9106bcd7c966` (dark).
The receded digests above and both frozen macOS 26.5 digests are unchanged; the
prior readings remain here as history.

W36 G1's black-only seal (claims §5.179) carries `be13dae45098fc89` (light active),
`2a4323f33df8d799` (dark active), `b0d0d8dacc6a03af` (light receded) and
`7c454858a3cbad5b` (dark receded). A separate identity-gated response below encoded
input 0.003 closes the measured black fallback without moving the old middle or
impulse response. Thick black is extrapolated from thin; the grey/chroma and rim
gaps remain. The two frozen macOS 26.5 digests stay unchanged.


**0.23.0 carries that declaration, not a new rim model** (claims §5.173).
`liftAmplitude` is 0 on all four macOS 27 endpoints; the frozen 26.5 active
material keeps 0.01 / 0.0051. “Zero over black” for the leaf means a uniformly
black source: its 40 px blurred input can lift locally black pixels beside light.
The active `thickOcclusionAt96/128/160` anchors compensate at
**0.0870 / 0.1650 / 0.2518** light and **0.1038 / 0.2188 / 0.3443** dark;
the six receded anchors remain zero. C1 passes on all twelve strata, with a
near/far trade rather than unchanged 3–6 bands. X1 now gates the WebGPU black
floor at zero on 218 non-holdout standard single-shape cells, both poses; the
CSS tier and composites are not claimed by that row. Apple's contour term is
present but unidentified here and remains undrawn under W33 Decision Log 3;
§5.171 records the native capture needed to separate its geometry and colour.


**That digest moved at 0.21.0, and one of the two reasons is not a rendering
change.** The four macOS 27 documents were refitted — `3dc24a74f17fd87e` (light),
`8a43f54162606db4` (dark), `ab3ed65aa02869b1` (light receded) and
`e1f42c5656ef392f` (dark receded) — and, separately, **the fingerprint's own
definition changed.** From 0.21.0 a leaf whose resolved value equals its declared
inert identity is dropped before hashing, so adding an operator at its identity
moves no document's digest at all. The visible consequence is that the two frozen
macOS 26.5 documents report the numbers they were sealed at —
`b2b570e4adcea8fb` and `874be66ea501621b` — instead of the numbers an inert leaf
had pushed them to at 0.20.0, **while drawing exactly what they drew**. An app
comparing a digest against a literal recorded under 0.19.0 or 0.20.0 has to
re-record it; a digest is a name for a material and this release renamed some of
them without repainting them.

The `-glass0.5` in a macOS 27 key is that release's appearance slider,
`NSGlassTintAmount`, at the position a Mac ships with; the material was measured
there. The documents themselves stay in the repository rather than in the
published tarball — a published package that loaded a calibration file would be
shipping a data dependency for numbers that never move between releases — and
`packages/platform-web/src/macos27-profile.ts` is generated from them by
`scripts/generate-macos27-profile.mjs`, pinned leaf for leaf by
`packages/calibration/test/macos27-profile-export.test.ts`.

**Upgrading to 0.19.0 changes what your page looks like.** That is the point of
the release, and it is the one thing to know before taking it: surfaces over dark
backdrops are no longer nearly invisible, the rim and the outer shadow are
different, and CSS-tier visitors get a wider blur. Pin
`macos26MaterialProfileDocument` to keep exactly what 0.18.0 drew.

**0.20.0 moves the outer shadow again, and this time by the size of the surface.**
On macOS 27 a wider surface casts a wider-blurred shadow; on macOS 26.5 it did
not, which is a measurement and not an absence. So the macOS 27 documents carry a
line in the casting span rather than one width, and the effect is two-sided: a
44 px control's blur falls from 22 CSS px to 4.3 and a 160 px panel's rises from
22 to 34.7. What a layout feels is the sampling geometry moving with it — a
group's shadow reach falls about a third at a small caster and rises about a
third at a large one, and keeps rising above the bed — so a control packed
against a neighbour reads as further from it and a large panel near a viewport
edge reaches further. `macos26MaterialProfileDocument` is unaffected: that
material's σ is span-invariant and its three new leaves are zero, which is where
its own measurement puts them.

**0.21.0 gives the body the backdrop's colour, on the WebGPU tier.** Over a
photograph, a gradient or any coloured backdrop, a surface used to render a grey
of about the right lightness: the body is a neutral plate composited over the
blurred backdrop, so what a backdrop's hues survived at was `1 − alpha` — about
half of them in the light material and a tenth in the dark one — against a
reference that keeps 0.71 to 0.83 and 0.90 to 0.97 of its own. Now the composited
colour's chromaticity is restored toward the blurred backdrop's by a fitted
fraction per colour scheme and per window pose.

**The after, in the same statistic as the before, because they were not the same
one** (2026-09-21, review closure; claims §5.165 §9, finding R5). The reference
figures above are a measured MEAN — the body's per-pixel chroma over the
backdrop's — and the light material's "about half" is not: it is `1 − alpha`, the
fraction the plate transmits, where the same measurement read **0.24 to 0.33**
before the fit. Measured the same way after it, the body keeps **0.51 to 0.57**
of the backdrop's chroma on a focused light window and **0.58 to 0.66** on an
unfocused one, **0.35 to 0.37** and **0.22 to 0.23** on the dark scheme's, against
the reference's 0.71–0.83 and 0.90–0.97. What the fit was judged on is a
different statistic again — the chroma-to-structure SPREAD ratio, in which the
blur cancels and which is what the eye reads as colour in the body — so these
means are the record's other column and not the bound.

**The level does not move**: both ends of that mix carry the same linear
luminance by construction, and gamut is taken by scaling chroma toward the
neutral at a held luma rather than by clipping a channel. An author's tint still
displaces the result exactly as it did, because the tint's shade law reads a
luminance the restoration preserves. Over a NEUTRAL
backdrop nothing changes, to the bit — restoring toward a chromaticity that is
not there is the identity.

Three things to know before taking it.

- **The CSS tier carries none of it**, and that is a measurement rather than an
  omission. The mirror was written — a gain on the one `saturate()` that tier
  already has, at the alpha it actually solves — rendered on the measured bed and
  taken back out. On the dark scheme it bought **nothing**, unchanged to four
  decimals even at the largest retention the leaf can hold, because that tier's
  converted alpha leaves no backdrop underneath for a saturation to act on; on
  the light scheme it bought a great deal and broke the material's own level and
  structure stops, because `saturate()` is a matrix on sRGB-encoded channels and
  stops preserving luminance the moment one clips. So a CSS-tier visitor draws
  the body they drew at 0.20.0, and `BODY_CHROMA_RETENTION` is exported beside
  the tier's other mirrored constants at **0** — the constant that re-opens the
  decline if it ever leaves that value.
- **Under an accessibility OCCLUSION lift the retention stands down entirely.**
  A lift sends the plate's alpha to `alpha + lift*(1 - alpha)`, so the plate
  covers more of the backdrop and restoring the nominal fraction of its
  chromaticity gives back what the preference asked to have covered up. **Reduce
  Transparency** raises that occlusion and stands the operator down; those pages
  draw what 0.20.0 drew, to the byte. **Increase Contrast alone does not** — it
  raises no occlusion of its own, and macOS 27 decoupled the two switches — so a
  page under Increase Contrast by itself draws the retention at full value. That
  is not a regression against 0.20.0, which had no operator; it is a combination
  the wave's bed does not measure, and it is recorded as an open gap rather
  than claimed either way.
- **The fidelity target is the WebGPU tier**, which is where the fit was judged
  and where the two adopted gate rows are stated. A page that resolves to the CSS
  tier gets the same geometry, the same level and the same shadow, and a
  colourless body.

**0.22.0 fits the shadow's exterior as a whole, and takes it off a receded
window.** Until this release the shadow had one fitted length — the blur's σ,
graded by the casting span since 0.20.0 — and its other two were the macOS 26.5
default's, carried unexamined onto the macOS 27 bed. Measured against Apple's own
render, vitrea's exterior was 2.66 to 3.77 CSS px too wide at every thick span on
every bed, and a green σ bound was consistent with that, because the bound
compares a blur leaf in closed form to a FIT of Apple's render and the fit
absorbs whatever else Apple's shadow is besides a blur. So the exterior is fitted
against what it actually draws: the transmission it applies at each distance from
the contour, per band and per direction, inside each capture's own clearance.

What moves, and what a page sees. **The outset falls 3.10 → 0.50 CSS px on the
light material and → 1.80 on the dark one** — Apple's own outset measures about
half a pixel — and the offset stays at 7.95. The six occlusion anchors are
re-solved against the 3–48 CSS px window, and the dark material's σ slope moves
inside its bound, which re-derives its thin knee: **a 44 px control on the dark
material now blurs its shadow at a σ of 2.72 CSS px where 0.21.0 drew 2.07.** The
shadow's transmission tracks Apple's to a mean of 0.0009 to 0.0039 of a unit of
backdrop light at the thick spans against 0.0039 to 0.0089 before, and to 0.00004
to 0.00023 at the thin ones. The rendered blur is still 1.27 to 2.77 CSS px wider
than Apple's fitted blur — halved and not closed, and recorded rather than
claimed. `macos26MaterialProfileDocument` is untouched by all of it.

**And a receded window draws no outer shadow.** Apple's unfocused window removes
no light at all from 3 CSS px outward: on 121 of 121 non-holdout inactive cells
the native transmission reads exactly 1.000000 in every band and the capture is
byte-identical to the backdrop from 2 device px out, and the same holds on all
235 frozen macOS 26.5 cells. vitrea had been drawing the ACTIVE shadow there,
because both receded documents carried their active document's anchors leaf for
leaf. Their amplitudes are 0 from 0.22.0, so a window that loses focus drops its
shadow and a group's clip shrinks with it in that pose — **fading out on the CSS
tier**, where the `box-shadow` carries a transition, and in one frame on the
WebGPU tier, whose two poses are fixed endpoints rather than an interpolation.
What Apple's recede does have is one device pixel of dark stroke at the contour,
a rim term vitrea does not draw and which is named as an open gap.

The demo site shows the macOS 27 pair only. A document is selected at
construction — a page drawing one has surfaces measured against it — so a single
root cannot present both beds at once, and the site has one root.

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

The receded differences the pose below selects come out of the root's material document, one per
colour scheme, and they are exported by name as well so an app can reach an endpoint directly — a
preview that is never a window, a harness that captures the receded appearance.
`macos27RecededMaterialProfile.light` and `.dark` are what a default root applies;
`recededMaterialProfile.light` and `.dark` are the macOS 26.5 endpoints, which
`macos26MaterialProfileDocument` selects. Reaching for one by hand means merging it over that
scheme's material yourself; through the runtime it is just
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
