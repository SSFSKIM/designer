/**
 * What the renderer consumes each frame, and why it is declared here rather than
 * imported from `@vitrea/core`.
 *
 * The renderer sits **below** core in the dependency graph: core reaches it
 * through a dynamic import (X7's lazy seam), so importing core back would close a
 * cycle that neither `pnpm -r build` nor `tsc` can order. The types below are
 * therefore declared as the *minimal structural contract* the renderer reads, and
 * core's own types satisfy them without an adapter — `SceneResolution`,
 * `FrameContext` and `FrameParticipant` are assignable to the views here, which
 * `test/core-contract.test.ts` asserts against core's real modules.
 *
 * Two things genuinely do not come from core, and both are flagged as
 * parent-impact rather than papered over:
 *
 *  - **The corner reference.** `GlassNodeDescriptor` carries `shapeFamily` and
 *    the X8 channel vector but not which of the two corner references the shape
 *    is fit against (Decision Log #22a made those two separate references, not
 *    one axis). It defaults to `"apple-continuous"`, which is what the public
 *    `profile: "continuous"` — the default — resolves to.
 *  - **The concentric parent link.** X8 rider 2 binds the renderer to draw a
 *    concentric child as a level set *of its parent's field*, which needs to know
 *    which surface the parent is. core's node descriptor has no parent edge, so it
 *    arrives as a render input.
 *
 * Interaction values arrive as **numbers**, never as time. §Motion puts the
 * drivers on the CPU and the spec is explicit that this package consumes their
 * outputs; there is no clock anywhere in this package for the same reason there is
 * none in core.
 */

import type {
  CornerReference,
  GroupUnionParams,
  ShapeChannels,
  ShapeFamily,
} from "@vitrea/geometry";

import type { MaterialPolicyView, MaterialVariant, RefractionQuality } from "./material";

/** Viewport-space rectangle in CSS px. Matches core's `Rect`. */
export interface Rect {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

/** Motion-driver outputs for one surface. Every one is a value, never a time. */
export interface SurfaceChannels {
  /** `pressCompression`, 0..1. Scaled by motion's `pressCompressionScale`. */
  readonly press: number;
  /** `glow`, 0..1, from the fast-attack / slow-decay driver. */
  readonly glow: number;
  /** Specular sweep position, 0..1 around the contour. */
  readonly sweep: number;
  /** `lensStrength`, 0..1. Multiplies the resolved refraction scale. */
  readonly lensStrength: number;
  /** Press point in viewport CSS px. Defaults to the surface's centre. */
  readonly pressPoint?: readonly [number, number];
}

export const IDLE_CHANNELS: SurfaceChannels = {
  press: 0,
  glow: 0,
  sweep: 0,
  lensStrength: 1,
};

export interface SurfaceInput {
  readonly nodeId: string;
  readonly family: ShapeFamily;
  /** X8, in viewport CSS px. `centre` is the surface's centre, `size` its full extent. */
  readonly shape: ShapeChannels;
  /** Defaults to `"apple-continuous"` — see the module note. */
  readonly reference?: CornerReference;
  readonly variant?: MaterialVariant;
  readonly channels?: Partial<SurfaceChannels>;
  /**
   * X8 rider 2. When present this surface renders as `parentField + inset`, and
   * the parent must be declared in the same group — as a member, or as a
   * `fieldReferenceOnly` shape.
   */
  readonly concentricOf?: { readonly nodeId: string; readonly inset: number };
  /**
   * Declared so a concentric child can be a level set of it, but not itself
   * drawn.
   *
   * This exists because of what a union is: a concentric child's field is its
   * parent's plus a positive inset, so inside the parent the child is always the
   * larger value and `min` discards it. A child nested in the same union as its
   * parent is therefore invisible *by construction* — correct, and not what an
   * inset indicator inside a segmented control's track wants. There, the track
   * and the indicator are separate surfaces with separate material, and the
   * indicator's group needs the track's geometry only as the field its own
   * contour is offset from.
   */
  readonly fieldReferenceOnly?: boolean;
}

export interface GroupRenderInput {
  readonly groupId: string;
  readonly surfaces: readonly SurfaceInput[];
  /** The backdrop source to sample. Absent means the group draws with no backdrop. */
  readonly backdropSourceId?: string;
  /** X2's resolved refraction quality for this group. Half of the dual cap. */
  readonly refraction: RefractionQuality;
  /** True where X2 resolved `analysis: "exact"`; gates adaptive tint. */
  readonly analysisExact: boolean;
  readonly variant?: MaterialVariant;
  /** Overrides the calibration-delegated union defaults. */
  readonly union?: GroupUnionParams;
}

/** The whole frame's render input. */
export interface FrameRenderInput {
  readonly groups: readonly GroupRenderInput[];
  /** The other half of the dual cap. Defaults to the nominal policy. */
  readonly accessibility?: MaterialPolicyView;
}

/**
 * The structural view of core's `SceneResolution` the renderer reads, so a host
 * can hand core's own object straight through.
 */
export interface SceneResolutionView {
  readonly groups: readonly {
    readonly groupId: string;
    readonly state: {
      readonly refraction: RefractionQuality;
      readonly analysis: "exact" | "hint" | "none";
      readonly samplingBackend: "gpu-texture" | "css-backdrop" | "none";
    };
  }[];
  readonly accessibility: { readonly material: MaterialPolicyView };
}

/** The structural view of core's `BackdropRebuildRequest`. */
export interface RebuildRequestView {
  readonly sourceId: string;
  readonly epoch: number;
  readonly resolution: { readonly scale: number; readonly maxDimension: number };
  readonly groupIds: readonly string[];
}

/** The structural view of core's `FrameContext`. */
export interface FrameContextView {
  readonly frame: { readonly id: number; readonly timeMs: number };
  readonly phase: "collect" | "read" | "update" | "write" | "render";
  readonly resolution?: SceneResolutionView;
  consumeDirtyBackdropSources(): readonly RebuildRequestView[];
}

/** The structural view of core's `FrameParticipant`. */
export interface FrameParticipantView {
  readonly id: string;
  readonly write?: (context: FrameContextView) => void;
  readonly render?: (context: FrameContextView) => void;
}
