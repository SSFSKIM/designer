/**
 * A glass root mounted from plain JavaScript. No framework, no build step of the
 * app's own beyond a bundler that can resolve an ESM package.
 *
 * This file is an **example first and a fixture second**. It is the code
 * `README.md`'s vanilla quickstart shows, kept here rather than in prose so that
 * the quickstart is executed on three engines every time the suite runs — a
 * README snippet that has never been run is a promise, not a fact. Nothing below
 * reaches past the published surface: every call is one a Vue, Svelte or
 * Web-Components adapter would make, in the order it would make it.
 *
 * The shape of a vitrea app, in the order it happens:
 *
 *  1. `createGlassRoot` builds the plane sandwich and starts the frame loop.
 *  2. `registerGroup` declares a sampling group — one backdrop read, shared by
 *     every surface in it.
 *  3. The app places its own element wherever it wants inside the plane's host
 *     layer. vitrea never creates or moves the app's DOM; that is the `asChild`
 *     contract, and it is why the label stays a real `<button>`.
 *  4. `registerHost` binds the element to the scene. The returned handle is how
 *     the app patches shape and interaction afterwards.
 *  5. `root.subscribe` joins the frame loop the root already runs, for whatever
 *     per-frame work the app has — rather than starting a second one.
 */

import {
  createGlassRoot,
  GLASS_CHANNEL_PROPERTIES,
  type GlassHostHandle,
  type GlassRoot,
  type VitreaDiagnostic,
} from "@vitreajs/vitrea-web";

/** What the spec reads back. A real app needs none of this. */
declare global {
  interface Window {
    v: VanillaProbe;
  }
}

interface VanillaProbe {
  readonly root: GlassRoot;
  readonly handle: GlassHostHandle;
  /** Frames observed through `root.subscribe`. */
  frames: number;
  /** Milliseconds accumulated from the tick's `deltaMs`. */
  elapsedMs: number;
  diagnostics: VitreaDiagnostic[];
  teardown(): void;
}

const diagnostics: VitreaDiagnostic[] = [];

// 1. The root. `container` and `zIndex` are the two placement knobs; everything
//    else defaults, and `renderer: "css"` is the default because the CSS tier is
//    what every engine can draw.
const root = createGlassRoot({
  devMode: true,
  diagnosticSink: (diagnostic) => diagnostics.push(diagnostic),
});

// 2. A sampling group. One group, one backdrop read, whatever the surface count.
root.registerGroup({ id: "controls" });

// 3. The app's own element, placed by the app.
const button = document.createElement("button");
button.type = "button";
button.id = "vanilla-button";
button.textContent = "Share";
button.style.cssText = "position:absolute;left:120px;top:220px;width:160px;height:44px";
button.className = "glass-host";
root.plane("base").hostLayer.append(button);

// 4. Bind it. `capsule` would be `shapeFamily: "capsule"`; this one is a fixed
//    rounded rect, so it names its own radii.
const handle = root.registerHost({
  host: button,
  groupId: "controls",
  plane: "base",
  shapeFamily: "fixed-rounded-rect",
  radii: [14, 14, 14, 14],
});

/*
 * Interaction, written the long way round on purpose.
 *
 * The channel custom properties are the seam: an app writes a 0..1 value and the
 * material reads it, on whichever tier is drawing. A framework binding wraps this
 * in its own event system — that is most of what `vitrea-react`'s
 * `interaction.ts` is — but nothing here is React's to own.
 */
let press = 0;
let pressTarget = 0;

button.addEventListener("pointerdown", () => (pressTarget = 1));
button.addEventListener("pointerup", () => (pressTarget = 0));
button.addEventListener("pointerleave", () => (pressTarget = 0));

// 5. Per-frame work, on the root's own loop.
const probe: VanillaProbe = {
  root,
  handle,
  frames: 0,
  elapsedMs: 0,
  diagnostics,
  teardown() {
    unsubscribe();
    handle.release();
    root.removeGroup("controls");
    root.destroy();
    button.remove();
  },
};

const unsubscribe = root.subscribe(({ deltaMs }) => {
  probe.frames += 1;
  probe.elapsedMs += deltaMs;

  // A first-order approach, which is all an example needs: the real motion
  // kernel lives in `@vitrea/motion` and the React bindings drive it from here.
  const step = deltaMs <= 0 ? 0 : Math.min(1, deltaMs / 90);
  press += (pressTarget - press) * step;
  button.style.setProperty(GLASS_CHANNEL_PROPERTIES.press, press.toFixed(4));
});

window.v = probe;
document.documentElement.setAttribute("data-vanilla-ready", "1");
