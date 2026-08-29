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

## The pieces

| What | Where |
| --- | --- |
| mounting, frames, registration | `createGlassRoot`, `GlassRoot` |
| per-element handle | `registerHost` → `GlassHostHandle` (`update`, `promoteTo`, `setOwnedTransform`, `release`) |
| planes | `root.plane(plane)` → `PlaneLayers`; `GLASS_PLANES` |
| interaction channels | `GLASS_CHANNEL_PROPERTIES` — write 0..1, the material reads |
| findings | `root.diagnostics`, `consoleDiagnosticSink()`, `VitreaDiagnostic` |
| capability answers | `root.capabilities(groupId)`, `root.accessibility`, `root.webgpu` |
| WebGPU | `renderer: "webgpu"`, `root.ready()`, `root.replaceDevice(device)` |

Everything else this package exports is exported because the React bindings and
the WebGPU renderer compose against it directly, and because a test should be
able to reach the decision that failed rather than the whole runtime. Those are
public but not the path an app takes.

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
