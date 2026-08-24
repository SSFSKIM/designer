/**
 * S2's f32 cross-check fixture, typed.
 *
 * `test/fixtures/s2-f32-cross-check.json` is a verbatim port of
 * `spikes/s2-geometry-field/bench/f32-check.json`. Its `expected` column is f64
 * evaluation of exactly the arithmetic in `bench/shaders.wgsl`, and the S2
 * benchmark measured the real shader's f32 output against that column on a
 * metal-3 adapter: 4.08e-5 px max, 0.024% of the declared bound.
 *
 * That makes the column a two-for-one oracle. Reproducing it says (a) this
 * package's field is numerically the field S2 measured, and (b) the WGSL C6
 * ships computes the same function — a transcription error in either would show
 * up as a gross disagreement, not a rounding difference.
 */

import type { FieldParams } from "../../src/field";
import type { CornerCoefficients } from "../../src/coefficients";

import raw from "../fixtures/s2-f32-cross-check.json" with { type: "json" };

export interface CrossCheckShape {
  readonly half: readonly number[];
  readonly reach: number;
  readonly k: readonly number[];
  readonly spec: { readonly W: number; readonly H: number; readonly r: number; readonly smoothing: number };
}

export interface CrossCheckFixture {
  readonly note: string;
  readonly shapes: readonly CrossCheckShape[];
  /** flattened [shapeIndex, x, y] triples */
  readonly points: readonly number[];
  /** family D value at each point, f64 */
  readonly expected: readonly number[];
}

export const CROSS_CHECK: CrossCheckFixture = raw;

export function crossCheckParams(): FieldParams[] {
  return CROSS_CHECK.shapes.map((s) => ({
    halfW: s.half[0] as number,
    halfH: s.half[1] as number,
    reach: s.reach,
    k: s.k as unknown as CornerCoefficients,
  }));
}
