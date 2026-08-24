/**
 * X8 — the shape channel set, and the vocabulary every other module speaks.
 *
 * `{ center, size, radii, smoothing, thickness }`. Every channel is numeric,
 * which is what makes v1's morphs parametric rather than crossfaded: capsule
 * <-> rounded rect, button <-> menu platter, indicator slides.
 *
 * Two conventions worth stating once, because mixing them up is the easiest way
 * to get corner math subtly wrong:
 *
 *  - `size` is the FULL width and height. Corner math works in half-extents
 *    (`halfW`, `halfH`), which is what the pseudo-SDF families are written in.
 *  - `smoothing` here is the value the author wrote. The budget clamp
 *    (§corner.ts) is applied at derivation and lands in `ResolvedCorner`, so
 *    shrinking a shape and growing it back is lossless (X8 rider 1).
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
 * `smoothing: 0`, `"continuous"` is the calibration-determined Apple-matching
 * corner (§apple.ts). Authoring a number instead puts the shape on the Figma
 * smoothing axis, which is the interpolable authoring family.
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

export const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;

export const clamp = (x: number, lo: number, hi: number): number => Math.min(Math.max(x, lo), hi);

/** Hermite ramp, 0 below `edge0` and 1 above `edge1`. C1 at both ends. */
export function smoothstep(edge0: number, edge1: number, x: number): number {
  if (edge1 <= edge0) return x < edge0 ? 0 : 1;
  const t = clamp((x - edge0) / (edge1 - edge0), 0, 1);
  return t * t * (3 - 2 * t);
}

/**
 * Interpolate the whole channel set. Total by construction: there is no channel
 * that needs a special case, which is the property X8 exists to guarantee.
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

/**
 * The channel set as a flat vector, in a fixed order. Exists so continuity
 * tests can sweep "every channel" without enumerating them by hand — a channel
 * added to X8 and not added here shows up as a length mismatch.
 */
export const SHAPE_CHANNEL_COUNT = 10;

export function flattenShapeChannels(c: ShapeChannels): number[] {
  return [
    c.center[0],
    c.center[1],
    c.size[0],
    c.size[1],
    c.radii[0],
    c.radii[1],
    c.radii[2],
    c.radii[3],
    c.smoothing,
    c.thickness,
  ];
}

/** Half-extents, which is the frame all corner and field math works in. */
export function halfExtents(size: Vec2): { halfW: number; halfH: number } {
  return { halfW: Math.max(size[0], 0) / 2, halfH: Math.max(size[1], 0) / 2 };
}

export const uniformRadii = (r: number): CornerRadii => [r, r, r, r];
