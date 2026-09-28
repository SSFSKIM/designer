/**
 * Which way the Moon's lit limb points on the screen.
 *
 * The limb faces the Sun along the great circle from the Moon to the Sun, so its screen direction
 * is that circle's TANGENT at the Moon, carried through the projection. The chord between the two
 * projected points is not it: the Sun is usually far off the view, often below the horizon, and
 * a stereographic projection bends a long arc away from its own chord, so the chord could tilt
 * the lit side tens of degrees off the Sun's true bearing.
 */

import { project, type Vec3, type View } from "./projection";

/** How far along the tangent the second point is taken, radians: far below a pixel's error. */
const STEP = 0.002;

/**
 * The unit screen direction, y up (the disc shader's frame), in which the Moon's lit limb points;
 * `[1, 0]` when either point does not project or the Sun and the Moon coincide or oppose.
 */
export function limbDirection(sunDir: Vec3, moonDir: Vec3, view: View): readonly [number, number] {
  const along = sunDir[0] * moonDir[0] + sunDir[1] * moonDir[1] + sunDir[2] * moonDir[2];
  const tangent: Vec3 = [sunDir[0] - along * moonDir[0], sunDir[1] - along * moonDir[1], sunDir[2] - along * moonDir[2]];
  const length = Math.hypot(tangent[0], tangent[1], tangent[2]);
  if (length < 1e-9) return [1, 0];
  const nudged: Vec3 = [
    moonDir[0] + (STEP * tangent[0]) / length,
    moonDir[1] + (STEP * tangent[1]) / length,
    moonDir[2] + (STEP * tangent[2]) / length,
  ];
  const norm = Math.hypot(nudged[0], nudged[1], nudged[2]);
  const p0 = project(moonDir, view);
  const p1 = project([nudged[0] / norm, nudged[1] / norm, nudged[2] / norm], view);
  if (p0 === undefined || p1 === undefined) return [1, 0];
  const dx = p1[0] - p0[0];
  const dy = -(p1[1] - p0[1]);
  const n = Math.hypot(dx, dy);
  return n === 0 ? [1, 0] : [dx / n, dy / n];
}
