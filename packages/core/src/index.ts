/**
 * @vitrea/core — skeleton (C1).
 *
 * One of the two published packages (X7). The internal @vitrea/* packages are
 * bundled into this artifact at build time, so this package's published
 * dependency list is empty.
 *
 * Pure: no DOM, no Node built-ins (X4). Browser access lives in
 * @vitrea/platform-web.
 */

import { SHAPE_FAMILIES, type ShapeFamily } from "@vitrea/geometry";
import { INTERACTION_STATES, MOTION_DRIVER_BY_CHANNEL, type InteractionState } from "@vitrea/motion";

export * from "./capability";
export * from "./diagnostics";
export * from "./planes";
export * from "./state";
export { loadWebGPURenderer, type GlassRenderer } from "./renderer-seam";
export type { ShapeChannels, ShapeFamily, CornerProfile, Vec2, CornerRadii } from "@vitrea/geometry";
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
