/**
 * `@vitrea/platform-web` — the browser layer.
 *
 * The only package allowed to touch the DOM (X4). core, geometry and motion are
 * pure and passive; everything browser-shaped lives here: host registration and
 * the `asChild` seam, the batched read protocol, X1's plane sandwich, the
 * per-group backdrop proxies, the three-layer conformance probe, the CSS-tier
 * renderer, the media-query policy feed, and the WebGPU lifecycle.
 *
 * The one entry point an app needs is `createGlassRoot`. Everything else is
 * exported because `vitrea-react` (C8) and the WebGPU renderer (C6) compose
 * against these pieces directly, and because a test should be able to reach the
 * decision that failed rather than the whole runtime.
 */

export * from "./backdrop-proxy";
export * from "./backdrop-tone";
export * from "./channels";
export * from "./css-tier";
export * from "./diagnostics";
export * from "./geometry-sync";
export * from "./group-state";
export * from "./host";
export * from "./layer-model";
export * from "./measure";
export * from "./media-policy";
export * from "./optics";
// Named rather than star-exported: `GlassPlane` is core's type, re-exported by
// `planes.ts` so a consumer has one plane vocabulary, and several modules below
// import it. A star export leaves a declaration bundler guessing which module
// owns the name.
export {
  createGlassLayerManager,
  GLASS_PLANES,
  paintOrderIndex,
  PLANE_PAINT_ORDER,
  POINTER_TRANSPARENT_LAYERS,
  type GlassLayerManager,
  type GlassLayerManagerOptions,
  type GlassPlane,
  type PlaneLayer,
  type PlaneLayers,
} from "./planes";
export * from "./probe";
export * from "./proxy-geometry";
export * from "./refraction";
export * from "./renderer-bridge";
export * from "./root";
export * from "./tint";
export * from "./webgpu";
