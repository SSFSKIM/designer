/**
 * Dev-mode errors. Geometry has no diagnostics channel of its own (it has no
 * dependency on core), so everything it refuses, it refuses by throwing — which
 * is the right severity for the two things it refuses: a shape the v1 evaluator
 * cannot express, and a morph between shapes whose corners are not on the same
 * reference curve. Both are authoring mistakes with no sensible fallback, and
 * inventing one would produce a shape the declared error bound does not cover.
 */

export type GeometryErrorCode =
  /** X8 rider 3: the v1 corner algebra is mirror-symmetric, so all four radii must match. */
  | "non-uniform-radii"
  /** A morph whose endpoints sit on different corner reference curves. */
  | "corner-reference-mismatch"
  /** A channel value the shape families cannot express (negative size, NaN). */
  | "invalid-channel";

export class GeometryError extends Error {
  readonly code: GeometryErrorCode;

  constructor(code: GeometryErrorCode, message: string) {
    super(message);
    this.name = "GeometryError";
    this.code = code;
  }
}
