/**
 * X1's plane law and the `GlassLayerManager` that realises it in the DOM.
 *
 * Plane *identity* is core's — it is part of the z-slot model, and core's
 * same-plane overlap check reasons about it. What lives here is a plane's DOM
 * realisation: the four-layer sandwich and its paint order.
 *
 * ```
 * page content
 *   ↓
 * backdrop-proxy layer   one masked, pointer-events:none proxy per sampling group
 *   ↓
 * optics canvas          glass bodies — inert here; C6 attaches to it
 *   ↓
 * semantic host DOM      real <button> etc.: text, icons, focus, IME, a11y tree
 *   ↓
 * highlight canvas       specular sweeps and press glow — inert here
 * ```
 *
 * That sandwich is *why* two glass surfaces may not overlap inside one plane:
 * there is no way to put one surface's body above another surface's label. S1
 * added a second, independent reason — sibling proxies provably chain, so an
 * overlap double-applies the material's own filter (measured 1.5625× for
 * `brightness(1.25)`) — which is why the rule is checked rather than assumed.
 *
 * Two constraints on this module's own CSS, and they are not stylistic. Nothing
 * it writes may carry a backdrop-root trigger — no `opacity`, `filter`, `mask`,
 * `clip-path`, `mix-blend-mode`, or a `will-change` naming any of them — because
 * the proxies live inside these elements and such a style would re-root their
 * backdrop and break the very topology the probe is there to defend. And the
 * canvases are inert: `pointer-events: none` and `aria-hidden`, so hit-testing
 * and the accessibility tree pass straight through to the host DOM.
 */

import { GLASS_PLANES, type GlassPlane } from "vitrea";

export { GLASS_PLANES, type GlassPlane };

/** Paint order within one plane, back to front (X1). */
export const PLANE_PAINT_ORDER = [
  "backdrop-proxy",
  "optics-canvas",
  "semantic-host",
  "highlight-canvas",
] as const;

export type PlaneLayer = (typeof PLANE_PAINT_ORDER)[number];

export function paintOrderIndex(layer: PlaneLayer): number {
  return PLANE_PAINT_ORDER.indexOf(layer);
}

/** Layers the compositor owns; everything else in the sandwich is app DOM. */
export const POINTER_TRANSPARENT_LAYERS: readonly PlaneLayer[] = PLANE_PAINT_ORDER.filter(
  (layer) => layer !== "semantic-host",
);

/** One plane's DOM. The canvases are handed to C6; the host layer to the app. */
export interface PlaneLayers {
  readonly plane: GlassPlane;
  readonly root: HTMLElement;
  readonly proxyLayer: HTMLElement;
  readonly opticsCanvas: HTMLCanvasElement;
  /** Where hosts live. The app places (or portals) its own elements in here. */
  readonly hostLayer: HTMLElement;
  readonly highlightCanvas: HTMLCanvasElement;
}

export interface GlassLayerManager {
  readonly root: HTMLElement;
  plane(plane: GlassPlane): PlaneLayers;
  readonly planes: readonly PlaneLayers[];
  /** Resize the canvas backing stores to the viewport at the given DPR. */
  resizeCanvases(width: number, height: number, devicePixelRatio: number): void;
  destroy(): void;
}

export interface GlassLayerManagerOptions {
  /** Where the glass root is attached. Defaults to `document.body`. */
  readonly container?: HTMLElement;
  /**
   * The glass root's stacking index. A `z-index` does **not** form a Backdrop
   * Root — Filter Effects 2 says so explicitly and S1's transform rows confirm
   * the neighbouring cases — so this is safe to set, and it has to be settable:
   * the planes are fixed overlays and an app with positioned content needs to
   * say where the glass sits relative to it.
   */
  readonly zIndex?: number;
  readonly document?: Document;
}

const DEFAULT_Z_INDEX = 1000;

/** Applied as a style string so the whole rule set is readable in one place. */
const ROOT_STYLE = "position:fixed;inset:0;pointer-events:none;color-scheme:light dark";
const PLANE_STYLE = "position:absolute;inset:0;pointer-events:none";
const LAYER_STYLE = "position:absolute;inset:0;pointer-events:none";
/** The host layer passes pointers through its gaps; each host opts itself back in. */
const HOST_LAYER_STYLE = "position:absolute;inset:0;pointer-events:none";
const CANVAS_STYLE = "position:absolute;inset:0;width:100%;height:100%;pointer-events:none";

export function createGlassLayerManager(
  options: GlassLayerManagerOptions = {},
): GlassLayerManager {
  const doc = options.document ?? document;
  const container = options.container ?? doc.body;

  const root = doc.createElement("div");
  root.setAttribute("data-vitrea-root", "");
  root.setAttribute("style", `${ROOT_STYLE};z-index:${options.zIndex ?? DEFAULT_Z_INDEX}`);

  const canvas = (layer: PlaneLayer, plane: GlassPlane): HTMLCanvasElement => {
    const element = doc.createElement("canvas");
    element.setAttribute("data-vitrea-layer", layer);
    element.setAttribute("data-vitrea-plane", plane);
    // Inert: out of the hit-test stack and out of the accessibility tree. The
    // glass body is decoration; the semantic host beneath it is the control.
    element.setAttribute("aria-hidden", "true");
    element.setAttribute("style", CANVAS_STYLE);
    return element;
  };

  const div = (layer: PlaneLayer, plane: GlassPlane, style: string): HTMLElement => {
    const element = doc.createElement("div");
    element.setAttribute("data-vitrea-layer", layer);
    element.setAttribute("data-vitrea-plane", plane);
    element.setAttribute("style", style);
    return element;
  };

  const layersFor = (plane: GlassPlane): PlaneLayers => {
    const planeRoot = doc.createElement("div");
    planeRoot.setAttribute("data-vitrea-plane-root", plane);
    planeRoot.setAttribute("style", PLANE_STYLE);

    const proxyLayer = div("backdrop-proxy", plane, LAYER_STYLE);
    const opticsCanvas = canvas("optics-canvas", plane);
    const hostLayer = div("semantic-host", plane, HOST_LAYER_STYLE);
    const highlightCanvas = canvas("highlight-canvas", plane);

    // DOM order *is* paint order here: nothing in this subtree sets z-index, so
    // the sandwich cannot be reordered by a stylesheet reaching in.
    planeRoot.append(proxyLayer, opticsCanvas, hostLayer, highlightCanvas);

    return { plane, root: planeRoot, proxyLayer, opticsCanvas, hostLayer, highlightCanvas };
  };

  const planes = GLASS_PLANES.map(layersFor);
  root.append(...planes.map((layers) => layers.root));
  container.append(root);

  const byPlane = new Map(planes.map((layers) => [layers.plane, layers]));

  return {
    root,
    planes,
    plane(plane) {
      const layers = byPlane.get(plane);
      // GLASS_PLANES is the full domain and every one was built above, so this
      // cannot miss — but the type says `| undefined`, and a thrown error beats
      // a non-null assertion that hides a real regression later.
      if (layers === undefined) throw new Error(`No DOM was built for plane "${plane}".`);
      return layers;
    },
    resizeCanvases(width, height, devicePixelRatio) {
      const backingWidth = Math.max(1, Math.round(width * devicePixelRatio));
      const backingHeight = Math.max(1, Math.round(height * devicePixelRatio));
      for (const layers of planes) {
        for (const element of [layers.opticsCanvas, layers.highlightCanvas]) {
          // Effect-texture resolution is decoupled from DOM DPR by contract
          // (§Performance envelope); this is the identity case, and the governor
          // is what moves it.
          if (element.width !== backingWidth) element.width = backingWidth;
          if (element.height !== backingHeight) element.height = backingHeight;
        }
      }
    },
    destroy() {
      root.remove();
    },
  };
}
