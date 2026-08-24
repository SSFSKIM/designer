/**
 * Group union: bounded smooth-min over member fields.
 *
 * §Geometry: group rendering goes through a per-group field pass (instances ->
 * group SDF/coverage field -> one optical pass), "which makes bounded smooth-min
 * proximity union within a group nearly free; union aesthetics (neck width, max
 * bulge, separation threshold) are **capped** and calibration-tuned so nothing
 * reads as jelly."
 *
 * The three tunables the spec names, and what each one actually does:
 *
 *  - **`neckWidth`** — the polynomial smooth-min's blend width `k`. Two members
 *    closer than about `k/2` grow a neck between them.
 *  - **`maxBulge`** — the cap. A quadratic smooth-min deviates from `min` by at
 *    most `k/4`, so capping the deviation caps `k` at `4 * maxBulge`; the total
 *    over an n-member fold is clamped once at the end, which makes the bound
 *    hold for any member count and any fold order.
 *  - **`separationThreshold`** — the gate. Without it, two members far apart
 *    still depress the field on the segment between them, because a smooth min
 *    of two equal values dips even when both are large. That depression is what
 *    reads as jelly. The gate switches blending off wherever the nearest member
 *    is farther than half the threshold, which is exactly where a neck could no
 *    longer form.
 *
 * Both gates are load-bearing and they catch different cases: `|a - b| >= k`
 * saturates the blend next to one member when the other is far, and the
 * separation gate kills the midpoint depression between two distant members.
 * With both, the union is EXACTLY `min` everywhere except near a real seam.
 */

import { clamp, smoothstep, type Vec2 } from "./channels";
import { rsupnField } from "./field";
import { fieldParams, type ResolvedShape } from "./shape";

export interface GroupUnionParams {
  /** Blend width in px. Larger means a wider, softer neck. */
  readonly neckWidth: number;
  /** Hard cap on how far the union may deviate from `min`, in px. */
  readonly maxBulge: number;
  /** Members whose gap exceeds this never blend, in px. */
  readonly separationThreshold: number;
}

/**
 * Advisory defaults, calibration-delegated in the same sense as §Geometry's
 * other union aesthetics: named here so the math has a definition, fitted by C7
 * against the reference. Chosen so the bulge cap is not already binding at the
 * default neck width — the cap is a guard against a raised `neckWidth`, not a
 * silent re-parameterization of the default.
 */
export const DEFAULT_GROUP_UNION: GroupUnionParams = {
  neckWidth: 8,
  maxBulge: 2,
  separationThreshold: 16,
};

/**
 * Two-member bounded smooth union.
 *
 * Commutative: swapping the arguments maps `h -> 1 - h` and leaves the
 * expression unchanged, which is asserted rather than assumed because a
 * non-commutative union would make a group's appearance depend on instance
 * buffer order.
 */
export function smoothUnion2(a: number, b: number, params: GroupUnionParams): number {
  const nearest = Math.min(a, b);

  // The bulge cap, applied to k rather than to the result: a quadratic
  // smooth-min's worst deviation is k/4, so this is the k that cannot exceed it.
  const capped = Math.min(params.neckWidth, 4 * params.maxBulge);

  // The separation gate. `nearest` is ~0 at a real seam and ~gap/2 at the
  // midpoint between two distant members, so gating on it switches off exactly
  // the blending that would otherwise invent material in empty space.
  const gate = 1 - smoothstep(0, params.separationThreshold * 0.5, Math.max(nearest, 0));
  const k = capped * gate;
  if (k <= 0) return nearest;

  const h = clamp(0.5 + (0.5 * (b - a)) / k, 0, 1);
  return b + h * (a - b) - k * h * (1 - h);
}

/**
 * n-member union.
 *
 * A left fold, which is what a shader iterating its group's instances does. The
 * final clamp is what makes the bulge cap a real bound rather than a per-step
 * one: without it an n-member fold could drift by up to `(n-1) * maxBulge`, and
 * "nothing reads as jelly" would stop being true at high member counts. With it,
 * `|union - min| <= maxBulge` holds for any n and any order — one `max` at the
 * end, which is also why it is free on the GPU.
 */
export function groupUnion(values: readonly number[], params: GroupUnionParams): number {
  if (values.length === 0) return Number.POSITIVE_INFINITY;
  let acc = values[0] as number;
  let nearest = acc;
  for (let i = 1; i < values.length; i++) {
    const v = values[i] as number;
    acc = smoothUnion2(acc, v, params);
    nearest = Math.min(nearest, v);
  }
  return Math.max(acc, nearest - params.maxBulge);
}

/**
 * The group field at a point: every member's field, unioned.
 *
 * Each member is evaluated in its own shape-local frame, which is what makes the
 * union independent of where the group happens to sit.
 */
export function groupUnionField(
  members: readonly ResolvedShape[],
  point: Vec2,
  params: GroupUnionParams = DEFAULT_GROUP_UNION,
): number {
  const values: number[] = [];
  for (const m of members) {
    const p = fieldParams(m);
    values.push(rsupnField(p, point[0] - m.channels.center[0], point[1] - m.channels.center[1]));
  }
  return groupUnion(values, params);
}

/** One member's field at a point, in the group's coordinate space. */
export function memberField(member: ResolvedShape, point: Vec2): number {
  const p = fieldParams(member);
  return rsupnField(p, point[0] - member.channels.center[0], point[1] - member.channels.center[1]);
}
