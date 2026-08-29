/**
 * vitrea — the platform-free heart of the runtime.
 *
 * One of the two published packages (X7). The internal @vitrea/* packages are
 * bundled into this artifact at build time, so this package's published
 * dependency list is empty.
 *
 * Pure and passive: no DOM, no Node built-ins (X4), no timers and no clocks.
 * Every probe result, media-query answer and layout rect arrives as plain data;
 * @vitreajs/vitrea-web owns the browser and drives the frames.
 *
 * The modules, roughly in dependency order:
 *
 * - `state`, `capability` — X2's resolved-state model and the transition table
 *   that produces it: what the app configured versus what it actually got.
 * - `diagnostics` — how core reports what it will not silently fix.
 * - `planes`, `frame` — the z-slot vocabulary and the frame-phase vocabulary.
 * - `backdrop-hint` (X6), `foreground`, `material`, `accessibility` — the four
 *   policy resolvers.
 * - `scene` — the three registries, their references, and the dirty-epoch
 *   bookkeeping behind the one-rebuild-per-dirty-source-per-frame invariant.
 * - `scheduler` — the frame-phase contract plus a reference implementation.
 * - `renderer-seam` — the lazy edge to the WebGPU renderer (X7).
 */

import { SHAPE_FAMILIES, type ShapeFamily } from "@vitrea/geometry";
import { INTERACTION_STATES, MOTION_DRIVER_BY_CHANNEL, type InteractionState } from "@vitrea/motion";

export * from "./accessibility";
export * from "./backdrop-hint";
export * from "./capability";
export * from "./diagnostics";
export * from "./foreground";
export * from "./frame";
export * from "./material";
export * from "./planes";
export * from "./scene";
export * from "./scheduler";
export * from "./state";
export {
  loadWebGPURenderer,
  loadWebGPURendererModule,
  type BackdropProvider,
  type CopyProviderOptions,
  type GlassRenderer,
  type VideoProviderOptions,
  type WebGPURendererModule,
} from "./renderer-seam";
export type {
  ShapeChannels,
  ShapeFamily,
  CornerProfile,
  // A scene-model field since Decision Log #23(c), so anyone registering a node
  // has to be able to name it.
  CornerReference,
  Vec2,
  CornerRadii,
} from "@vitrea/geometry";
export type { MotionChannel, MotionDriverKind, InteractionState } from "@vitrea/motion";

/**
 * The contract sets core owns, re-exported so a consumer never installs an
 * internal package. Reading these values here is also what makes the internal
 * packages part of core's bundle — the property X7's bundle test checks.
 */
export const VITREA_CONTRACTS: {
  readonly shapeFamilies: readonly ShapeFamily[];
  readonly interactionStates: readonly InteractionState[];
  readonly motionDrivers: typeof MOTION_DRIVER_BY_CHANNEL;
} = {
  shapeFamilies: SHAPE_FAMILIES,
  interactionStates: INTERACTION_STATES,
  motionDrivers: MOTION_DRIVER_BY_CHANNEL,
};

/** Renderer tiers in v1's ladder. WebGL2 is out of scope; SVG displacement is a reserved seam. */
export const RENDERER_TIERS = ["webgpu", "css"] as const;

export type RendererTier = (typeof RENDERER_TIERS)[number];
