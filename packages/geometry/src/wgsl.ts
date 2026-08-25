/**
 * The WGSL source of truth for the field, as exported string constants. C6
 * consumes these.
 *
 * These are the shaders S2 actually benchmarked
 * (`spikes/s2-geometry-field/bench/shaders.wgsl`, results.json generatedAt
 * 2026-08-24T14:29:14.670Z on a metal-3 adapter), carried here unchanged in
 * their arithmetic so the cost figures and the f32 precision result transfer
 * with them:
 *
 *   - `sd_rsupn` — 0.02640 ns/eval/px; f32 vs f64 agreement 4.08e-5 px, which is
 *     0.024% of the declared 0.17 px bound. That check does double duty: it also
 *     validates the port, because `rsupnField` in `field.ts` is a line-for-line
 *     mirror, so a transcription slip would show as a gross disagreement rather
 *     than a rounding difference.
 *   - `sd_rsup` — 0.00970 ns/eval/px, the governor's first within-tier step.
 *     Unchanged since S2 measured it, character for character.
 *
 * `sd_rsupn` has moved once since: its normalization is now anchored at the
 * contour radius (see `field.ts`, "The normalization"), which adds one divide and
 * one `select` and leaves the selected arm identical on and outside the level set.
 * The f32 result above has been re-established on hardware for the anchored
 * shader — 4.007e-5 px worst case over 5535 points on an `apple/metal-3` adapter,
 * against S2's 4.08e-5 — by `renderer-webgpu`'s `e2e/gpu/cross-check.spec.ts`,
 * which reads this string's own output back off the device. The cost figure is
 * S2's and now carries the added divide as an unmeasured delta; the renderer's
 * `@bench` suite is what holds the envelope.
 *
 * **C6 action item, spec Decision Log #20:** family C's WGSL is
 * inspection-verified only. Its cost number is a cost number and does not depend
 * on the port being bit-accurate, but `sd_rsup` must go through the f32
 * cross-check before it ships as a governor tier. Extending
 * `spikes/s2-geometry-field/bench/make-f32-check.ts` to emit a third expected
 * column is the whole job.
 *
 * `test/wgsl-sync.test.ts` holds these and the TypeScript in step: it fingerprints
 * both, so editing either one alone fails the suite with a message saying to
 * re-run the cross-check.
 */

/**
 * Instance data layout. The last six scalars — `re` and `k0..k4` — are the
 * derived floats C6's instance buffer widens by. They are computed CPU-side from
 * `{ size, radii, smoothing }` (see `shape.ts`'s `fieldParams`), so they are a
 * buffer layout change and not an API or channel change. During a morph they are
 * recomputed per frame, which is trivial at v1's surface counts but should batch
 * with the existing geometry sync rather than happen per draw.
 */
export const WGSL_SHAPE_STRUCT = `struct Shape {
  centre : vec2f,
  half   : vec2f,
  re     : f32,
  k0     : f32,
  k1     : f32,
  k2     : f32,
  k3     : f32,
  k4     : f32,
  _pad   : f32,
};`;

/**
 * Family D — the v1 field. Radial-support field with a degree-5 corner
 * correction in `s2 = sin(2*theta)`, plus the first-order |grad| normalization.
 *
 * No transcendentals: `s2` and `cos(2*theta)` both come out of the clamped
 * corner vector by division. Cost over a plain rounded box is one extra divide,
 * one rsqrt, and about a dozen fused multiply-adds. Branchless in the corner
 * algebra — the only guard is the clamp on the squared corner radius, which
 * keeps the deep-interior case from producing NaN without costing a branch, and
 * is why the straight-edge region needs no special case.
 */
export const WGSL_RSUPN = `fn sd_rsupn(p : vec2f, half : vec2f, re : f32, k : vec4f, k4 : f32) -> f32 {
  let q  = abs(p) - half + vec2f(re, re);
  let c  = max(q, vec2f(0.0, 0.0));
  let r2 = max(dot(c, c), 1e-20);
  let inv = 1.0 / r2;
  let s2 = 2.0 * c.x * c.y * inv;             // sin(2*theta)
  let c2 = (c.x * c.x - c.y * c.y) * inv;     // cos(2*theta)

  // R(theta) = re * (1 + s2^2 * poly(s2)), Horner
  var acc = k4;
  acc = acc * s2 + k.w;
  acc = acc * s2 + k.z;
  acc = acc * s2 + k.y;
  acc = acc * s2 + k.x;
  let R = re * (1.0 + s2 * s2 * acc);

  // dR/d(s2) * d(s2)/dtheta, same Horner shape with the differentiated weights
  var dac = 6.0 * k4;
  dac = dac * s2 + 5.0 * k.w;
  dac = dac * s2 + 4.0 * k.z;
  dac = dac * s2 + 3.0 * k.y;
  dac = dac * s2 + 2.0 * k.x;
  let dRdt = re * s2 * dac * (2.0 * c2);

  let base = sqrt(r2) + min(max(q.x, q.y), 0.0) - R;
  // The normalization is a Newton step to the zero set, so its slope is read at
  // the FOOT of the step: at the contour radius R, never at a sample radius
  // inside it. On and outside the level set the selected arm is bit-for-bit the
  // product S2 benchmarked; inside the corner sector the anchor is what stops
  // R'/rho diverging toward the sector vertex and collapsing the field into a
  // false near-surface region. See field.ts, "The normalization".
  let g = select(dRdt / R, dRdt * inv * sqrt(r2), sqrt(r2) >= R);
  return base * inverseSqrt(1.0 + g * g);
}`;

/**
 * Family C — family D minus the |grad| normalization. The two share a zero level
 * set and a coefficient table, so the gap between them is exactly the price of
 * the normalization: 29% of the field's total cost, in exchange for degrading the
 * bound from 0.170 px / 2.91 degrees to 0.574 px / 4.26 degrees and the eikonal
 * defect from 2.7% to 7.9%.
 *
 * Dropping the normalization is one branch and one uniform, which is what makes
 * this a cleaner within-tier governor step than reducing refraction resolution.
 * See the module note: this one still needs C6's f32 cross-check.
 */
export const WGSL_RSUP = `fn sd_rsup(p : vec2f, half : vec2f, re : f32, k : vec4f, k4 : f32) -> f32 {
  let q  = abs(p) - half + vec2f(re, re);
  let c  = max(q, vec2f(0.0, 0.0));
  let r2 = max(dot(c, c), 1e-20);
  let s2 = 2.0 * c.x * c.y / r2;
  var acc = k4;
  acc = acc * s2 + k.w;
  acc = acc * s2 + k.z;
  acc = acc * s2 + k.y;
  acc = acc * s2 + k.x;
  let R = re * (1.0 + s2 * s2 * acc);
  return sqrt(r2) + min(max(q.x, q.y), 0.0) - R;
}`;

/** Struct plus both families, ready to concatenate into a pipeline's module. */
export const WGSL_FIELD_MODULE = [WGSL_SHAPE_STRUCT, WGSL_RSUPN, WGSL_RSUP].join("\n\n");

/**
 * FNV-1a over the UTF-16 code units, as a zero-padded hex string.
 *
 * A drift tripwire, not a security primitive — and deliberately hand-rolled: a
 * pure package may not import `node:crypto`, and this only has to notice that a
 * string changed.
 */
export function fingerprint(text: string): string {
  let h = 0x811c9dc5;
  for (let i = 0; i < text.length; i++) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h.toString(16).padStart(8, "0");
}
