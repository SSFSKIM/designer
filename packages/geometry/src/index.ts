/**
 * @vitrea/geometry — skeleton (C1).
 *
 * Holds the shape-channel contract (X8) so downstream packages can type against
 * it before C3 lands the Contour IR, the pseudo-SDF families and the morph
 * solver. Pure math: no DOM, no Node built-ins (X4).
 */

export type Vec2 = readonly [x: number, y: number];

/** Corner radii, clockwise from top-left. */
export type CornerRadii = readonly [
  topLeft: number,
  topRight: number,
  bottomRight: number,
  bottomLeft: number,
];

/** The v1 shape families (§Geometry). Not "Apple's taxonomy" — vitrea's supported set. */
export const SHAPE_FAMILIES = ["fixed-rounded-rect", "capsule", "concentric-rounded-rect"] as const;

export type ShapeFamily = (typeof SHAPE_FAMILIES)[number];

/**
 * Public sugar over the internal numeric corner profile: `"circular"` is
 * `smoothing: 0`, `"continuous"` is the calibration-determined value.
 */
export type CornerProfile = "continuous" | "circular";

/**
 * X8 — the shape channel set. Every channel is numeric, which is what makes
 * v1's parametric morphs total: capsule <-> rounded rect, button <-> platter.
 */
export interface ShapeChannels {
  readonly center: Vec2;
  readonly size: Vec2;
  readonly radii: CornerRadii;
  /** 0 = circular arc corners, 1 = maximum continuous-curvature smoothing. */
  readonly smoothing: number;
  /** Material thickness, in CSS px, driving lensing depth and shadow. */
  readonly thickness: number;
}

const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;

/**
 * Interpolate the whole channel set. C3 replaces the easing/solver story; the
 * property that every channel interpolates is the contract, not this code.
 */
export function lerpShapeChannels(a: ShapeChannels, b: ShapeChannels, t: number): ShapeChannels {
  return {
    center: [lerp(a.center[0], b.center[0], t), lerp(a.center[1], b.center[1], t)],
    size: [lerp(a.size[0], b.size[0], t), lerp(a.size[1], b.size[1], t)],
    radii: [
      lerp(a.radii[0], b.radii[0], t),
      lerp(a.radii[1], b.radii[1], t),
      lerp(a.radii[2], b.radii[2], t),
      lerp(a.radii[3], b.radii[3], t),
    ],
    smoothing: lerp(a.smoothing, b.smoothing, t),
    thickness: lerp(a.thickness, b.thickness, t),
  };
}
