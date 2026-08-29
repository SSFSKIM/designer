/**
 * The group field pass (§Geometry: "instances → group SDF/coverage field → one
 * optical pass").
 *
 * Three contract points are structural here rather than conventional, which is
 * the only way a shader can be held to them:
 *
 * 1. **X8 rider 2 — a concentric child renders as a LEVEL SET of its parent's
 *    field.** There is no second path. `Instance` carries the *parent's*
 *    `half/re/k` plus its own `inset`, and the evaluator always computes
 *    `field(p; parent params) + inset`. For an ordinary surface `inset` is 0 and
 *    the expression is the surface's own field. So the instantiated-shape path —
 *    whose offset error grows with inset and dominates the declared bound past
 *    about 4 px — is not expressible in this shader at all.
 * 2. **The families come from `@vitrea/geometry` verbatim.** `sd_rsupn` and
 *    `sd_rsup` are the fingerprinted strings that package owns, spliced in
 *    unchanged, so the cost figures and the f32 result transfer with them. What
 *    this module adds is their gradients and the union, which S2 did not price and
 *    which are therefore written to be as close to free as the algebra allows.
 * 3. **The gradient is analytic and costs no extra field evaluations.**
 *    `sd_rsupn_grad` is a port of `rsupnFieldAndGradient` — the ≤2.92° normal at
 *    the free normal's price. Family C's normal is the closed-form level-set
 *    normal (≤4.26°), which is the honest pairing: taking family C means taking
 *    family C's gradient too. Being a port, it moves when the value moves:
 *    `sd_rsupn` anchors its normalization at the contour radius, so this selects
 *    the same arm and differentiates the arm it selected. `test/wgsl-contract.test.ts`
 *    pins that pairing, because a normal computed from the unanchored form on top
 *    of an anchored depth is exactly the kind of half-applied edit no fingerprint
 *    would notice.
 *
 * The union mirrors `union.ts` exactly on the value — the same bulge cap applied
 * to `k`, the same separation gate, the same single clamp at the end of the fold.
 * `union_blend` returns that value **and the blend weight `h`**, because the pass
 * has more than a distance to fold: the gradient and the four per-surface optical
 * scalars have to travel through the same seam, and doing it with the same `h`
 * keeps one copy of the union's algebra instead of four. Blending the gradient by
 * `h` drops the union's term in `dk`, which makes it exact wherever `h` saturates
 * — everywhere except inside a real seam.
 */

import { WGSL_RSUP, WGSL_RSUPN } from "@vitrea/geometry";

/**
 * Instance layout — `@vitrea/geometry`'s `Shape` struct widened by the render
 * channels, 64 bytes, every member 4- or 8-byte aligned so the CPU packing is a
 * flat `Float32Array` with a 16-float stride.
 *
 * `centre/half/re/k0..k4` are the X8 channel vector's geometric half plus the
 * six derived floats. `inset` is rider 2's level-set offset. The rest are motion
 * driver outputs, sampled by the host and handed in as data (§Motion: this
 * package consumes driver outputs, never time).
 */
export const WGSL_INSTANCE_STRUCT = `struct Instance {
  centre : vec2f,   //  0  group-local CSS px
  half   : vec2f,   //  8  half-extents of the field's OWN shape (the parent's, for a concentric child)
  re     : f32,     // 16  corner reach
  k0     : f32,     // 20
  k1     : f32,     // 24
  k2     : f32,     // 28
  k3     : f32,     // 32
  k4     : f32,     // 36
  inset  : f32,     // 40  X8 rider 2: level-set offset. 0 for an ordinary surface.
  thick  : f32,     // 44  material thickness, CSS px
  press  : f32,     // 48  interaction channel value, 0..1
  glow   : f32,     // 52  interaction channel value, 0..1
  lensDepth : f32,  // 56  CPU-resolved lens depth in CSS px (material.ts), already scaled by the lensStrength channel
  tintK  : f32,     // 60  author tint strength, 0..1 — the seed itself is a group uniform
};`;

/** `FieldSample` mirrors geometry's, minus `kink`: the shader has no use for it. */
export const WGSL_FIELD_SAMPLE = `struct FieldSample {
  d : f32,
  g : vec2f,
};`;

/**
 * Family D's value and exact gradient in one pass — the port of
 * `rsupnFieldAndGradient`.
 *
 * The masks at the end are what extend the corner-sector chain rule to every
 * region: `mx`/`my` gate the clamped-coordinate terms, and the box-branch term
 * carries the derivative where `max(qx, qy) <= 0`. The `<=` there is not a
 * typo — at `m == 0` both clamped terms are masked off, so the box term has to
 * fire or the gradient reads (0, 0) on the corner-sector boundary. C3 found and
 * fixed exactly that bug while deriving this.
 */
export const WGSL_RSUPN_GRAD = `fn sd_rsupn_grad(p : vec2f, half : vec2f, re : f32, k : vec4f, k4 : f32) -> FieldSample {
  let q  = abs(p) - half + vec2f(re, re);
  let c  = max(q, vec2f(0.0, 0.0));
  let r2 = max(dot(c, c), 1e-20);
  let inv = 1.0 / r2;
  let rho = sqrt(r2);
  let s2 = 2.0 * c.x * c.y * inv;
  let c2 = (c.x * c.x - c.y * c.y) * inv;

  // A = sum k_i s2^i, B = sum (i+2) k_i s2^i, C = sum (i+1)(i+2) k_i s2^i.
  var accA = k4;
  accA = accA * s2 + k.w;
  accA = accA * s2 + k.z;
  accA = accA * s2 + k.y;
  accA = accA * s2 + k.x;

  var accB = 6.0 * k4;
  accB = accB * s2 + 5.0 * k.w;
  accB = accB * s2 + 4.0 * k.z;
  accB = accB * s2 + 3.0 * k.y;
  accB = accB * s2 + 2.0 * k.x;

  var accC = 30.0 * k4;
  accC = accC * s2 + 20.0 * k.w;
  accC = accC * s2 + 12.0 * k.z;
  accC = accC * s2 + 6.0 * k.y;
  accC = accC * s2 + 2.0 * k.x;

  let R      = re * (1.0 + s2 * s2 * accA);
  let dRds2  = re * s2 * accB;
  let d2Rds2 = re * accC;
  let dRdt   = dRds2 * (2.0 * c2);

  let mm   = min(max(q.x, q.y), 0.0);
  let base = rho + mm - R;
  // Anchored at the contour radius, mirroring sd_rsupn: the normalization's
  // slope is read at the foot of the Newton step, never at a sample radius
  // inside the contour. See geometry's field.ts, "The normalization".
  let atRho = rho >= R;
  let w    = select(R, rho, atRho);
  let g    = select(dRdt / R, dRdt * inv * rho, atRho);
  let norm = sqrt(1.0 + g * g);
  let n    = 1.0 / norm;

  let ds2dcx = -2.0 * c.y * c2 * inv;
  let ds2dcy =  2.0 * c.x * c2 * inv;
  let dc2dcx =  2.0 * c.x * inv * (1.0 - c2);
  let dc2dcy = -2.0 * c.y * inv * (1.0 + c2);

  let drhodcx = c.x / rho;
  let drhodcy = c.y / rho;

  let dRdcx = dRds2 * ds2dcx;
  let dRdcy = dRds2 * ds2dcy;

  let dTermdcx = 2.0 * (d2Rds2 * ds2dcx * c2 + dRds2 * dc2dcx);
  let dTermdcy = 2.0 * (d2Rds2 * ds2dcy * c2 + dRds2 * dc2dcy);

  // w's derivative follows whichever of rho and R is larger. Exact across the
  // switch because the switch locus is rho == R, the contour, where base == 0
  // kills the only term the jump lives in.
  let dwdcx = select(dRdcx, drhodcx, atRho);
  let dwdcy = select(dRdcy, drhodcy, atRho);

  let dgdcx = dTermdcx / w - (dRdt * dwdcx) / (w * w);
  let dgdcy = dTermdcy / w - (dRdt * dwdcy) / (w * w);

  let n3 = n * n * n;
  let dddcx = (drhodcx - dRdcx) * n + base * (-g * n3 * dgdcx);
  let dddcy = (drhodcy - dRdcy) * n + base * (-g * n3 * dgdcy);

  let mx = select(0.0, 1.0, q.x > 0.0);
  let my = select(0.0, 1.0, q.y > 0.0);
  let inBox = max(q.x, q.y) <= 0.0;
  let dmmdqx = select(0.0, 1.0, inBox && q.x >= q.y);
  let dmmdqy = select(0.0, 1.0, inBox && q.y >  q.x);

  let sx = select(1.0, -1.0, p.x < 0.0);
  let sy = select(1.0, -1.0, p.y < 0.0);

  var out : FieldSample;
  out.d = base * n;
  out.g = vec2f((dddcx * mx + n * dmmdqx) * sx, (dddcy * my + n * dmmdqy) * sy);
  return out;
}`;

/**
 * Family C's value and its closed-form level-set normal.
 *
 * The value is `sd_rsup` verbatim; the normal is
 * `normalize(rhoHat - (R'/rho) * thetaHat)`, which is free because every term is
 * already computed. It is identical to family D's gradient *on* the contour to
 * four decimal places — the normalization moves level sets only away from the
 * zero set — so rim lighting is indifferent between them and only refraction at
 * depth pays the 1.5–1.7× difference.
 */
export const WGSL_RSUP_GRAD = `fn sd_rsup_grad(p : vec2f, half : vec2f, re : f32, k : vec4f, k4 : f32) -> FieldSample {
  let q  = abs(p) - half + vec2f(re, re);
  let c  = max(q, vec2f(0.0, 0.0));
  let r2 = max(dot(c, c), 1e-20);
  let rho = sqrt(r2);
  let s2 = 2.0 * c.x * c.y / r2;

  var accA = k4;
  accA = accA * s2 + k.w;
  accA = accA * s2 + k.z;
  accA = accA * s2 + k.y;
  accA = accA * s2 + k.x;

  var accB = 6.0 * k4;
  accB = accB * s2 + 5.0 * k.w;
  accB = accB * s2 + 4.0 * k.z;
  accB = accB * s2 + 3.0 * k.y;
  accB = accB * s2 + 2.0 * k.x;

  let c2 = (c.x * c.x - c.y * c.y) / r2;
  let R  = re * (1.0 + s2 * s2 * accA);

  let sx = select(1.0, -1.0, p.x < 0.0);
  let sy = select(1.0, -1.0, p.y < 0.0);

  var out : FieldSample;
  out.d = rho + min(max(q.x, q.y), 0.0) - R;

  if (c.x <= 0.0 && c.y <= 0.0) {
    // Straight-edge and deep-interior: the normal is the axis the box branch is
    // measuring along.
    out.g = select(vec2f(0.0, sy), vec2f(sx, 0.0), q.x > q.y);
    return out;
  }

  let dRdt = re * s2 * accB * (2.0 * c2);
  let rhoHat = c / rho;
  let gg = dRdt / rho;
  let nx = rhoHat.x + gg * rhoHat.y;
  let ny = rhoHat.y - gg * rhoHat.x;
  let len = max(length(vec2f(nx, ny)), 1e-20);
  out.g = vec2f(sx * nx / len, sy * ny / len);
  return out;
}`;

/**
 * The bounded smooth union of `union.ts`, value for value.
 *
 * `separation * 0.5` is floored away from zero because WGSL's `smoothstep` is
 * undefined when its two edges coincide, where the TypeScript's own `smoothstep`
 * degrades to a step. A group configured with no separation threshold therefore
 * blends everywhere, which is the same thing the TypeScript does.
 */
export const WGSL_SMOOTH_UNION = `fn union_blend(a : f32, b : f32, u : vec3f) -> vec2f {
  let neck = u.x;
  let maxBulge = u.y;
  let sep = max(u.z * 0.5, 1e-6);

  let nearest = min(a, b);
  let capped = min(neck, 4.0 * maxBulge);
  let gate = 1.0 - smoothstep(0.0, sep, max(nearest, 0.0));
  let k = capped * gate;

  if (k <= 0.0) {
    return vec2f(nearest, select(0.0, 1.0, a <= b));
  }

  let h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
  return vec2f(b + h * (a - b) - k * h * (1.0 - h), h);
}`;

/**
 * The pass itself.
 *
 * Scoped to the group's bounds, never fullscreen: the target IS the group rect,
 * so the fullscreen triangle covers exactly the pixels the group can touch.
 * §Performance envelope prices the field at ~5% of the mobile budget on that
 * assumption, and a fullscreen field pass per group would multiply it by the
 * ratio of viewport area to group area.
 *
 * The output is one `rgba16float` texel per device pixel: signed field in CSS
 * px, the unit normal, and analytic coverage. Everything downstream — optics,
 * highlight, and any future pass — reads this and never re-evaluates the field.
 */
export const WGSL_FIELD_PASS = `struct FieldUniforms {
  /// screen.xy = target size in device px, screen.z = CSS px per device px,
  /// screen.w = coverage ramp width in CSS px
  screen : vec4f,
  /// neckWidth, maxBulge, separationThreshold, unused
  unionP : vec4f,
  counts : vec4u,
};

// Per-surface optical scalars ride through the union in 'aux': the group is one
// field but its members are not one size, and carrying them per pixel is what
// lets a 40 px button and a 320 px platter share a field pass and still lens by
// their own depth — parent acceptance #2 inside a GlassEffectContainer.
//   aux = (lensDepthPx, glow, thicknessPx, tintStrength)
//
// The fourth slot carried the press channel until W3 and no shader ever read
// it — press compression is resolved on the CPU, as a transform on the surface's
// own size (instances.ts). It now carries the author tint's strength, which does
// need to be per pixel: one control tinted inside a toolbar of plain ones is the
// composition Apple's guidance describes, and the group is one optics pass. The
// press value is still packed into the instance buffer, unchanged, for a future
// consumer that wants it per pixel; it simply no longer rides here.

@group(0) @binding(0) var<uniform> fu : FieldUniforms;
@group(0) @binding(1) var<storage, read> instances : array<Instance>;

struct Member {
  d   : f32,
  g   : vec2f,
  aux : vec4f,
};

fn eval_instance(i : u32, p : vec2f) -> Member {
  let s = instances[i];
  let k = vec4f(s.k0, s.k1, s.k2, s.k3);
  // X8 rider 2 in one line: the child is the parent's field, shifted. There is
  // no branch and no second path, so no caller can opt into the instantiated
  // shape whose offset error the rider rules out.
  let f = FIELD_FN(p - s.centre, s.half, s.re, k, s.k4);
  var m : Member;
  m.d = f.d + s.inset;
  m.g = f.g;
  m.aux = vec4f(s.lensDepth, s.glow, s.thick, s.tintK);
  return m;
}

struct FieldOut {
  @location(0) field : vec4f,
  @location(1) aux   : vec4f,
};

@fragment
fn fs_field(in : FullscreenOut) -> FieldOut {
  // GROUP-LOCAL CSS px. The instance buffer's centres were already made relative
  // to the group's rect on the CPU (f32 loses resolution at large magnitudes, so
  // a field evaluated at viewport y = 40000 would quantise its own corner), and
  // adding the origin back here would offset every shape by it twice.
  let p = in.uv * fu.screen.xy * fu.screen.z;

  var out : FieldOut;
  let count = fu.counts.x;
  if (count == 0u) {
    // Large but FINITE: rgba16float overflows to +Inf past ~65504, and NaN
    // coverage downstream is not reliably zero.
    out.field = vec4f(65000.0, 0.0, -1.0, 0.0);
    out.aux = vec4f(0.0);
    return out;
  }

  var acc = eval_instance(0u, p);
  var nearest = acc.d;
  for (var i = 1u; i < count; i = i + 1u) {
    let s = eval_instance(i, p);
    let blend = union_blend(acc.d, s.d, fu.unionP.xyz);
    let h = blend.y;
    acc.d = blend.x;
    acc.g = mix(s.g, acc.g, h);
    acc.aux = mix(s.aux, acc.aux, h);
    nearest = min(nearest, s.d);
  }
  // One clamp at the end of the fold, so |union - min| <= maxBulge holds for any
  // member count and any order rather than per blend step.
  acc.d = max(acc.d, nearest - fu.unionP.y);

  let len = max(length(acc.g), 1e-6);
  let normal = acc.g / len;
  let coverage = clamp(0.5 - acc.d / max(fu.screen.w, 1e-6), 0.0, 1.0);

  out.field = vec4f(acc.d, normal.x, normal.y, coverage);
  out.aux = acc.aux;
  return out;
}`;

/** The field module for one family. `FIELD_FN` is bound at assembly time. */
export function fieldPassSource(family: "rsupn" | "rsup"): string {
  const kernels = family === "rsupn" ? [WGSL_RSUPN, WGSL_RSUPN_GRAD] : [WGSL_RSUP, WGSL_RSUP_GRAD];
  const fn = family === "rsupn" ? "sd_rsupn_grad" : "sd_rsup_grad";
  return [
    WGSL_INSTANCE_STRUCT,
    WGSL_FIELD_SAMPLE,
    ...kernels,
    WGSL_SMOOTH_UNION,
    WGSL_FIELD_PASS.replace("FIELD_FN", fn),
  ].join("\n\n");
}

/**
 * Both families' value kernels plus both gradients, with no pass around them.
 *
 * This is what the f32 cross-check compiles: Decision Log #20 makes family C's
 * shipping conditional on its WGSL going through the same check family D passed,
 * and a check that compiled a *different* string from the one the renderer ships
 * would prove nothing. So the pass source above and the harness below are both
 * assembled from these same constants.
 */
export const WGSL_FIELD_KERNELS = [
  WGSL_INSTANCE_STRUCT,
  WGSL_FIELD_SAMPLE,
  WGSL_RSUPN,
  WGSL_RSUP,
  WGSL_RSUPN_GRAD,
  WGSL_RSUP_GRAD,
  WGSL_SMOOTH_UNION,
].join("\n\n");
