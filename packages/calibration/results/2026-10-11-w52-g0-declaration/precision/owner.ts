/** W52-DL3 clarification 1: prospective SOURCE comparators, not a status adapter.
 *
 * Not yet wired: the W52 G1 owner port must call these at the floating per-cell cap sites
 * in W50's owner/referee.ts. Bind all bounds from its unchanged source contracts. Keep its
 * population/missing-reading checks, original baselines and named-record resolution outside
 * this adapter. M2's directional products and L1's native reference equality remain exact.
 * X75, integer/integrity/support predicates and every aggregate retain their own source laws.
 */

/** Binary64 counterpart of precision/comparison.py, including the operand scale floor. */
export function epsilon(...operands: number[]): number {
  if (!operands.length || operands.some(value => !Number.isFinite(value))) {
    throw new Error('Comparison requires finite source operands');
  }
  let scale = 1;
  for (const value of operands) scale = Math.max(scale, Math.abs(value));
  // Read the exponent instead of log2: log2 can round a value just below a binade upward.
  // The scale floor excludes subnormals, so spacing is 2^(unbiased exponent - 52).
  const bits = new DataView(new ArrayBuffer(8));
  bits.setFloat64(0, scale);
  const exponent = ((bits.getUint32(0) >>> 20) & 0x7ff) - 1023;
  return 64 * 2 ** (exponent - 52);
}

/** Include every native/candidate/reference operand used to form the compared residual. */
export function lessEqual(value: number, bound: number, ...sources: number[]): boolean {
  return value <= bound + epsilon(value, bound, ...sources);
}

export interface M1Bounds { min: number; max: number }

/** M1 ratio window; missing/zero native ratios must be handled by the owner's exact selector. */
export function m1WithinBounds(native: number, candidate: number, bounds: M1Bounds): boolean {
  const ratio = candidate / native;
  const allowance = epsilon(ratio, native, candidate, bounds.min, bounds.max);
  return ratio >= bounds.min - allowance && ratio <= bounds.max + allowance;
}

export interface StructureCell {
  interiorStdDevWebReference: number;
  interiorStdDevWeb: number;
  structureDeltaFraction: number;
}
export type StructureVerdict = 'within' | 'named' | 'failure';

/** M2 source-compatible cell/signature with the source-bound tolerance passed explicitly.
 * `named` is a directional outcome, NOT permission: the port must still enforce the original
 * named-list membership and ruled-failure checks (including wouldRequireNewOwnerRecord).
 */
export function m2StructureVerdict(
  cell: StructureCell, native: number, tolerance: number,
): StructureVerdict {
  const reference = cell.interiorStdDevWebReference;
  const web = cell.interiorStdDevWeb;
  if (lessEqual(Math.abs(cell.structureDeltaFraction), tolerance, reference, web, native)) {
    return 'within';
  }
  const toward = (web - reference) * (native - reference) > 0;
  const beyond = (web - native) * (native - reference) > 0;
  return toward && (!beyond || lessEqual(Math.abs(web - native) / native,
    tolerance, reference, web, native)) ? 'named' : 'failure';
}

export interface L1Bounds { absolute: number; growth: number }

/** L1's original arithmetic and exact native-evidence check, with only its caps adapted.
 * The port retains MISSES for absolute misses and GROWTH_RULED for 0.5 growth misses;
 * 0.25 growth still has no named path. Missing means/records are not admitted here.
 */
export function l1Caps(
  native: number, candidate: number, nativeReference: number, reference: number,
  bounds: L1Bounds,
): {
  error: number; referenceError: number; growth: number;
  absoluteWithin: boolean; growthWithin: boolean;
} {
  epsilon(native, candidate, nativeReference, reference, bounds.absolute, bounds.growth);
  if (native !== nativeReference) throw new Error('Native L1 reading changed');
  const error = Math.abs(candidate - native);
  const referenceError = Math.abs(reference - nativeReference);
  const growth = error - referenceError;
  return { error, referenceError, growth,
    absoluteWithin: lessEqual(error, bounds.absolute, native, candidate),
    growthWithin: lessEqual(growth, bounds.growth,
      native, candidate, nativeReference, reference, error, referenceError),
  };
}
