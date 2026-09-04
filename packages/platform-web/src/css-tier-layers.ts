/**
 * The CSS tier's DOM — its three created layers, its raster ramp masks and its
 * reference-filter definitions (W16 G1; charter Decision Log 2 (a)–(c),
 * claims §5.71).
 *
 * `css-tier.ts` decides what the tier draws and stays pure, so the accessibility
 * mapping, the element model and the second scale are all testable without a
 * browser. Everything that needs a `Document`, a `<canvas>` or an `<svg>` is
 * here, and it holds no optical number of its own: the mask's profile is the
 * renderer's k(u) reconstructed from the three numbers `CssTierBody.ramp`
 * carries, and the filters' widths are the two the body resolved.
 *
 * Three things this module is careful about, all of them measured:
 *
 *  - **The mask sits on the filtered element itself, never on a wrapper.** A
 *    masked *ancestor* is a backdrop root and makes a descendant's
 *    `backdrop-filter` inert; on the element it composes exactly, and a uniform
 *    mask is bit-identical to the same `opacity` (claims §5.71 §1).
 *  - **The raster is the only exact carrier.** A gradient stack's corners read
 *    0.06–0.19 off the shader's k(u) because `mask-composite` multiplies alphas
 *    where the distance field takes a minimum, and a blurred SVG inset is an erf
 *    where the law is a straight ramp; the raster is exact to the mask channel's
 *    own eight bits, corners included (claims §5.71 §4).
 *  - **The layers carry no semantics.** `aria-hidden`, `pointer-events: none`,
 *    no tab stop, no `id`, and they are torn down with the host — so the plane
 *    sandwich's four-layer array, the hit-test map's "no `layer:` entries" and
 *    the one-focusable-element-per-surface rule are all unchanged by them.
 */

import {
  CSS_TIER_LAYER_ORDER,
  referenceFilterId,
  type CssTierBody,
  type CssTierLayer,
  type CssTierRamp,
  type CssTierRender,
} from "./css-tier";

/** The attribute the layers are found and asserted by. */
export const CSS_TIER_LAYER_ATTRIBUTE = "data-vitrea-css-layer";

export interface CssTierLayers {
  readonly elements: Readonly<Record<CssTierLayer, HTMLElement>>;
  /** Whether this host had `position` written for it, so release can take it back. */
  positionWritten: boolean;
  /** The declarations last written to each layer, serialised — the write cache. */
  applied: string | undefined;
  /** The mask last set on the heavy layer, by its cache key. */
  maskKey: string | undefined;
}

/**
 * The three children, created and attached.
 *
 * Created when the CSS tier first paints this host rather than at registration:
 * a host the WebGPU tier is drawing needs none of them, and this wave's binding
 * rule is that the GPU tier does not move by a byte — three empty positioned
 * children under every GPU-drawn host would be DOM that tier never asked for.
 * They are removed again the moment the tier steps aside, and on release.
 */
export function createCssTierLayers(host: HTMLElement): CssTierLayers {
  const doc = host.ownerDocument;
  const elements = {} as Record<CssTierLayer, HTMLElement>;
  for (const layer of CSS_TIER_LAYER_ORDER) {
    const element = doc.createElement("div");
    element.setAttribute(CSS_TIER_LAYER_ATTRIBUTE, layer);
    // Inert on every axis a user can reach: out of the accessibility tree, out
    // of the hit-test stack, and out of the tab order. The semantic host beneath
    // is the control; these are the material it is made of.
    element.setAttribute("aria-hidden", "true");
    elements[layer] = element;
    host.append(element);
  }
  return { elements, positionWritten: false, applied: undefined, maskKey: undefined };
}

/** Removes the layers and everything this module wrote on the host. */
export function destroyCssTierLayers(host: HTMLElement, layers: CssTierLayers): void {
  for (const layer of CSS_TIER_LAYER_ORDER) layers.elements[layer].remove();
  if (layers.positionWritten) host.style.removeProperty("position");
}

/**
 * Gives the host a containing block for the layers, once.
 *
 * An absolutely positioned child resolves against the nearest *positioned*
 * ancestor, so a statically positioned host would hand its layers to the plane's
 * host layer and paint the material over the whole viewport. Writing
 * `position: relative` unconditionally would be worse: an app that positions its
 * own glass host absolutely or fixed would have that overridden by an inline
 * declaration it cannot outrank, which is a layout bug vitrea would be causing.
 *
 * So the position is read once, at the moment the tier first paints this host,
 * and written only where it is `static`. One style read per host per
 * materialization, on the frame that already flushes style for the transition's
 * sake — not per frame, so the zero-read steady state is untouched.
 */
export function ensureCssTierContainingBlock(
  host: HTMLElement,
  layers: CssTierLayers,
  view: Window,
): void {
  if (layers.positionWritten) return;
  if (host.style.position !== "") return;
  if (view.getComputedStyle(host).position !== "static") return;
  host.style.setProperty("position", "relative");
  layers.positionWritten = true;
}

/**
 * Applies a resolved render to the three layers, and sets the heavy layer's
 * raster mask where the body asks for one.
 *
 * `withoutTransition` is the materialization path: the first write has to land
 * with the transition off, or the browser batches it with the element's initial
 * values and every surface fades in from transparent and unblurred.
 */
export function applyCssTierLayers(
  layers: CssTierLayers,
  render: CssTierRender,
  geometry: CssTierMaskGeometry,
  masks: CssTierMaskCache,
  withoutTransition = false,
): void {
  const declarations = render.layers;
  if (declarations === undefined) return;
  for (const layer of CSS_TIER_LAYER_ORDER) {
    const element = layers.elements[layer];
    if (withoutTransition) element.style.setProperty("transition", "none");
    for (const [property, value] of Object.entries(declarations[layer])) {
      if (withoutTransition && property === "transition") continue;
      element.style.setProperty(property, value);
    }
  }

  const heavy = layers.elements.heavy;
  const ramp = render.body.ramp;
  if (ramp === undefined) {
    if (layers.maskKey !== undefined) {
      heavy.style.removeProperty("mask-image");
      heavy.style.removeProperty("-webkit-mask-image");
      layers.maskKey = undefined;
    }
    return;
  }
  const key = maskCacheKey(geometry, ramp);
  if (layers.maskKey === key) return;
  const url = masks.get(key, geometry, ramp);
  heavy.style.setProperty("mask-image", `url("${url}")`);
  heavy.style.setProperty("-webkit-mask-image", `url("${url}")`);
  layers.maskKey = key;
}

/** The surface the mask is drawn for, in CSS px and its own device ratio. */
export interface CssTierMaskGeometry {
  readonly widthCssPx: number;
  readonly heightCssPx: number;
  readonly radiusCssPx: number;
  readonly devicePixelRatio: number;
}

function maskCacheKey(geometry: CssTierMaskGeometry, ramp: CssTierRamp): string {
  return [
    Math.round(geometry.widthCssPx * 100),
    Math.round(geometry.heightCssPx * 100),
    Math.round(geometry.radiusCssPx * 100),
    Math.round(geometry.devicePixelRatio * 1000),
    Math.round(ramp.contourShare * 10000),
    Math.round(ramp.deepShare * 10000),
    Math.round(ramp.reachDevicePx * 100),
  ].join(":");
}

/**
 * The heavy share at a depth, reconstructed from the three numbers the body
 * carries — the renderer's own straight ramp between them.
 *
 * `cssTierHeavyShareAt` is the law and this is its two-point form: the law is
 * `kDeep − A · max(0, 1 − u/R)`, which is linear in `u` over `[0, R]` and flat
 * beyond it, and the accessibility fold is affine in the share, so the folded law
 * is the folded endpoints joined by a line. `css-tier.test.ts` pins this against
 * `cssTierHeavyShareAt` over a sweep of depths rather than trusting the algebra.
 */
export function maskShareAt(uDevicePx: number, ramp: CssTierRamp): number {
  const reach = Math.max(ramp.reachDevicePx, 1e-6);
  const t = Math.min(Math.max(uDevicePx, 0) / reach, 1);
  return ramp.deepShare + (ramp.contourShare - ramp.deepShare) * (1 - t);
}

/**
 * The signed distance into a rounded rectangle, in the same units as the box,
 * positive inside — the exact field, corners included.
 *
 * The corners are why this is not four gradients: `mask-composite: intersect`
 * multiplies alphas where the distance field takes a minimum, so a stack of
 * per-side gradients reads 0.06–0.19 low exactly where two sides meet, and the
 * ramp's whole point is that it is a function of the depth from the *contour*
 * (claims §5.71 §4).
 */
export function roundedRectDepth(
  x: number,
  y: number,
  halfWidth: number,
  halfHeight: number,
  radius: number,
): number {
  const r = Math.min(radius, Math.min(halfWidth, halfHeight));
  const qx = Math.abs(x) - (halfWidth - r);
  const qy = Math.abs(y) - (halfHeight - r);
  const outside = Math.hypot(Math.max(qx, 0), Math.max(qy, 0));
  const inside = Math.min(Math.max(qx, qy), 0);
  return r - (outside + inside);
}

/**
 * The raster masks, one per (size, radius, ratio, ramp), kept until the root is
 * destroyed.
 *
 * A surface's size, its radius and the display's ratio are all things that change
 * rarely and in steps, so a cache keyed on them turns a per-frame cost into a
 * per-resize one — and G0 measured the mask itself free per frame once its canvas
 * exists (claims §5.71 §7). The entries are data URLs rather than canvases so the
 * same surface at the same size on two roots shares one decode.
 */
export interface CssTierMaskCache {
  get(key: string, geometry: CssTierMaskGeometry, ramp: CssTierRamp): string;
  clear(): void;
}

export function createCssTierMaskCache(doc: Document, limit = 64): CssTierMaskCache {
  const entries = new Map<string, string>();
  return {
    get(key, geometry, ramp) {
      const hit = entries.get(key);
      if (hit !== undefined) return hit;
      const url = drawRampMask(doc, geometry, ramp);
      // A plain FIFO bound rather than an LRU: the working set is the surfaces on
      // screen, an app that resizes past the bound is redrawing anyway, and an
      // unbounded map on a continuously resizing surface would be a leak.
      if (entries.size >= limit) {
        const oldest = entries.keys().next();
        if (!oldest.done) entries.delete(oldest.value);
      }
      entries.set(key, url);
      return url;
    },
    clear() {
      entries.clear();
    },
  };
}

/**
 * The ramp, drawn at **device** resolution into a canvas and handed back as a
 * data URL.
 *
 * Device resolution because the law is a function of the depth in device pixels
 * and because a mask stretched from CSS pixels would carry the ratio's own
 * resampling into the band this wave exists to draw. The colour channels are
 * white and only the alpha carries the share, which is what `mask-mode: alpha`
 * reads; the layer's own `border-radius` clips the silhouette, so the field
 * outside the contour is held at the contour's value rather than faded, and the
 * one pixel where the two disagree is the antialiased boundary G0 measured at up
 * to one code value (claims §5.71 §1).
 */
function drawRampMask(
  doc: Document,
  geometry: CssTierMaskGeometry,
  ramp: CssTierRamp,
): string {
  const dpr = Math.max(geometry.devicePixelRatio, 1e-3);
  const width = Math.max(1, Math.round(geometry.widthCssPx * dpr));
  const height = Math.max(1, Math.round(geometry.heightCssPx * dpr));
  const canvas = doc.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext("2d");
  // A context is only null where the document cannot raster at all, and a body
  // that silently drew a flat mask there would be a wrong mix reported as the
  // right one. The caller's `share` already says `raster-mask`, so the honest
  // answer is to draw nothing and let the layer's own `opacity` stand.
  if (context === null) return "";

  const image = context.createImageData(width, height);
  const data = image.data;
  const halfWidth = width / 2;
  const halfHeight = height / 2;
  const radius = geometry.radiusCssPx * dpr;
  for (let row = 0; row < height; row += 1) {
    const y = row + 0.5 - halfHeight;
    for (let column = 0; column < width; column += 1) {
      const x = column + 0.5 - halfWidth;
      const depth = roundedRectDepth(x, y, halfWidth, halfHeight, radius);
      const alpha = maskShareAt(depth, ramp);
      const index = (row * width + column) * 4;
      data[index] = 255;
      data[index + 1] = 255;
      data[index + 2] = 255;
      data[index + 3] = Math.round(Math.min(Math.max(alpha, 0), 1) * 255);
    }
  }
  context.putImageData(image, 0, 0);
  return canvas.toDataURL("image/png");
}

/**
 * The root's `<svg>` of reference-filter definitions — one per distinct σ, in
 * linear light (claims §5.71 §2).
 *
 * `color-interpolation-filters="linearRGB"` is SVG's own default and is the whole
 * of the difference: the `sRGB` sibling of this filter is bit-for-bit
 * `blur()`, which was the control G0 measured the space against. `backdrop-filter`
 * only renders a reference filter in Chromium, so this is built lazily and only
 * for a root whose engine's conformance row says so.
 *
 * The `<svg>` is a sibling of the plane roots rather than a child of one, so the
 * sandwich's four-layer array is untouched; it is zero-sized and `aria-hidden`,
 * and a `<defs>` subtree paints nothing.
 */
export interface CssTierFilterDefs {
  /** Ensures a `<filter>` exists for this σ and returns nothing. */
  ensure(sigmaCssPx: number): void;
  dispose(): void;
}

export function createCssTierFilterDefs(
  doc: Document,
  parent: Element,
  prefix: string,
): CssTierFilterDefs {
  const NS = "http://www.w3.org/2000/svg";
  const svg = doc.createElementNS(NS, "svg");
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("width", "0");
  svg.setAttribute("height", "0");
  svg.setAttribute("focusable", "false");
  svg.setAttribute("data-vitrea-css-filters", "");
  svg.setAttribute("style", "position:absolute;width:0;height:0;pointer-events:none");
  const defs = doc.createElementNS(NS, "defs");
  svg.append(defs);
  parent.append(svg);

  const built = new Set<string>();
  return {
    ensure(sigmaCssPx) {
      const id = referenceFilterId(prefix, sigmaCssPx);
      if (built.has(id)) return;
      const filter = doc.createElementNS(NS, "filter");
      filter.setAttribute("id", id);
      // The filter region has to cover the blur's own reach or the engine clips
      // the kernel at the default -10%/120% box and the layer's edge reads dark.
      // 3σ is the same truncation `SAMPLING_PADDING_SIGMA_MULTIPLE` states, in
      // the only unit a filter region takes.
      filter.setAttribute("x", "-50%");
      filter.setAttribute("y", "-50%");
      filter.setAttribute("width", "200%");
      filter.setAttribute("height", "200%");
      filter.setAttribute("color-interpolation-filters", "linearRGB");
      const blur = doc.createElementNS(NS, "feGaussianBlur");
      blur.setAttribute("in", "SourceGraphic");
      blur.setAttribute("stdDeviation", String(Math.round(sigmaCssPx * 100) / 100));
      filter.append(blur);
      defs.append(filter);
      built.add(id);
    },
    dispose() {
      built.clear();
      svg.remove();
    },
  };
}

/**
 * The filtered device-pixel area one surface costs per frame, for the root's
 * cost budget (`CSS_TIER_TWO_LAYER_AREA_BUDGET_DEVICE_PX`).
 *
 * The area is counted **once** per surface rather than once per layer: G0's cost
 * table is indexed by the surface area at two blurs, so the threshold and this
 * function are in the same unit by construction.
 */
export function filteredAreaDevicePx(
  widthCssPx: number,
  heightCssPx: number,
  devicePixelRatio: number,
): number {
  return widthCssPx * heightCssPx * devicePixelRatio * devicePixelRatio;
}

/** The widths a root has to have `<filter>` definitions for, given a body. */
export function referenceFilterSigmas(body: CssTierBody): readonly number[] {
  if (body.filter !== "reference-filter") return [];
  if (body.form === "collapsed") return [body.sharpSigmaCssPx];
  return [body.sharpSigmaCssPx, body.heavyStepSigmaCssPx];
}
