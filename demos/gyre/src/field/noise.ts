/**
 * The field function, in JavaScript.
 *
 * `shader.ts` carries the same function in GLSL, and the two are kept line for
 * line equivalent on purpose: the probe reads the field at a point through this
 * file, and the pixels under the probe are drawn by the other one. If they drifted,
 * the reading would describe a field the reader is not looking at.
 *
 * The noise is Ian McEwan and Stefan Gustavson's 2D simplex noise, whose hash is
 * polynomial arithmetic under mod 289 rather than `sin` of a large number. That is
 * what makes a CPU port match the GPU: every intermediate stays well inside the
 * range where single precision is exact enough, so the two evaluations agree to
 * better than the reading's displayed precision.
 */

import type { FieldLayer } from "./palettes";

const C_X = 0.211324865405187;
const C_Y = 0.366025403784439;
const C_Z = -0.577350269189626;
const C_W = 0.024390243902439;

function mod289(x: number): number {
  return x - Math.floor(x * (1 / 289)) * 289;
}

function permute(x: number): number {
  return mod289((x * 34 + 1) * x);
}

function fract(x: number): number {
  return x - Math.floor(x);
}

export function snoise(vx: number, vy: number): number {
  const s = (vx + vy) * C_Y;
  const ix = Math.floor(vx + s);
  const iy = Math.floor(vy + s);
  const t = (ix + iy) * C_X;
  const x0x = vx - ix + t;
  const x0y = vy - iy + t;
  const i1x = x0x > x0y ? 1 : 0;
  const i1y = x0x > x0y ? 0 : 1;
  const x1x = x0x + C_X - i1x;
  const x1y = x0y + C_X - i1y;
  const x2x = x0x + C_Z;
  const x2y = x0y + C_Z;
  const mix = mod289(ix);
  const miy = mod289(iy);
  const p0 = permute(permute(miy) + mix);
  const p1 = permute(permute(miy + i1y) + mix + i1x);
  const p2 = permute(permute(miy + 1) + mix + 1);
  let m0 = Math.max(0.5 - (x0x * x0x + x0y * x0y), 0);
  let m1 = Math.max(0.5 - (x1x * x1x + x1y * x1y), 0);
  let m2 = Math.max(0.5 - (x2x * x2x + x2y * x2y), 0);
  m0 = m0 * m0 * m0 * m0;
  m1 = m1 * m1 * m1 * m1;
  m2 = m2 * m2 * m2 * m2;
  const xx0 = 2 * fract(p0 * C_W) - 1;
  const xx1 = 2 * fract(p1 * C_W) - 1;
  const xx2 = 2 * fract(p2 * C_W) - 1;
  const h0 = Math.abs(xx0) - 0.5;
  const h1 = Math.abs(xx1) - 0.5;
  const h2 = Math.abs(xx2) - 0.5;
  const a0 = xx0 - Math.floor(xx0 + 0.5);
  const a1 = xx1 - Math.floor(xx1 + 0.5);
  const a2 = xx2 - Math.floor(xx2 + 0.5);
  m0 *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h0 * h0);
  m1 *= 1.79284291400159 - 0.85373472095314 * (a1 * a1 + h1 * h1);
  m2 *= 1.79284291400159 - 0.85373472095314 * (a2 * a2 + h2 * h2);
  const g0 = a0 * x0x + h0 * x0y;
  const g1 = a1 * x1x + h1 * x1y;
  const g2 = a2 * x2x + h2 * x2y;
  return 130 * (m0 * g0 + m1 * g1 + m2 * g2);
}

export function fbm(x: number, y: number): number {
  let value = 0;
  let amplitude = 0.5;
  let px = x;
  let py = y;
  for (let octave = 0; octave < 4; octave += 1) {
    value += amplitude * snoise(px, py);
    px = px * 2.02 + 17.3;
    py = py * 2.02 + 9.1;
    amplitude *= 0.5;
  }
  return value;
}

/**
 * The stream function's value at a point, 0..1, which the ramp colours and the
 * reading scales. `x` and `y` are field coordinates: the viewport's unit square,
 * with y up, already multiplied by the layer's aspect-corrected scale.
 */
export function fieldValue(layer: FieldLayer, x: number, y: number, time: number): number {
  const t = time * layer.rate;
  const qx = fbm(x + t * 0.05, y);
  const qy = fbm(x + 5.2, y + 1.3 - t * 0.04);
  const rx = fbm(x + layer.warp * qx + 1.7 + t * 0.07, y + layer.warp * qy + 9.2);
  const ry = fbm(x + layer.warp * qx + 8.3, y + layer.warp * qy + 2.8 - t * 0.06);
  // Eddies: the warped field itself.
  const v = fbm(x + 2 * rx, y + 2 * ry);
  const fine = fbm(x * 5 + 5 * rx, y * 5 + 5 * ry);
  // The jet: a meandering band across the middle of the box, and the front on
  // its axis. `d` is the signed distance from the axis in jet widths.
  const centre = layer.scale * (0.5 + 0.13 * Math.sin((x * 3.2) / layer.scale - t * 0.15) + 0.12 * ry);
  const d = (y - centre) / (0.11 * layer.scale);
  const jet = Math.exp(-d * d);
  const front = -Math.tanh(d * 0.7);
  const s =
    0.12 +
    0.3 * (v + 0.6) +
    layer.jet * jet * (0.85 + 0.3 * rx) +
    layer.front * (1 + front) +
    layer.detail * 4 * fine;
  return Math.min(1, Math.max(0, s));
}

export interface FieldSample {
  /** 0..1, the ramp position. */
  readonly speed: number;
  /** Compass bearing in degrees, 0 north, clockwise. */
  readonly bearing: number;
}

/**
 * Read the field at a viewport point. `u` and `v` are 0..1 across and up the
 * viewport; `aspect` is width over height, so the field is not stretched.
 */
export function sampleField(
  layer: FieldLayer,
  u: number,
  v: number,
  aspect: number,
  time: number,
): FieldSample {
  const x = u * aspect * layer.scale;
  const y = v * layer.scale;
  const speed = fieldValue(layer, x, y, time);
  const h = 0.004 * layer.scale;
  const dx = (fieldValue(layer, x + h, y, time) - fieldValue(layer, x - h, y, time)) / (2 * h);
  const dy = (fieldValue(layer, x, y + h, time) - fieldValue(layer, x, y - h, time)) / (2 * h);
  // Flow runs along the stream function's contours: the gradient turned a quarter.
  const vx = dy;
  const vy = -dx;
  const bearing = ((Math.atan2(vx, vy) * 180) / Math.PI + 360) % 360;
  return { speed, bearing };
}
