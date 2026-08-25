/**
 * The field itself: the properties that hold by construction, and the cross-check
 * that says this TypeScript computes the same function as the WGSL C6 ships.
 *
 * The cross-check fixture is S2's own `bench/f32-check.json`, ported verbatim.
 * Those `expected` values are f64 evaluation of the *identical arithmetic* as
 * `bench/shaders.wgsl`, and the S2 benchmark measured the real shader's f32
 * output against them on a metal-3 adapter at 4.08e-5 px worst case. So
 * reproducing this column to machine precision is transitive evidence that the
 * shader and this file agree — much stronger than any hash of the source text.
 *
 * ## The column is a two-sided oracle now, and that is deliberate
 *
 * The normalization's anchor moved (see `field.ts`, "The normalization"): inside
 * the level set it reads the slope at the contour radius instead of at the sample
 * radius. The fixture is NOT rewritten to agree with the new code — it is S2's
 * measurement — so the assertions below state which half of it still pins the
 * shipped arithmetic, and exactly how the other half is allowed to differ.
 */

import { describe, expect, it } from "vitest";

import {
  centralGradient,
  type FieldParams,
  rsupField,
  rsupLevelSetNormal,
  rsupnField,
  rsupnFieldAndGradient,
  cornerSupport,
} from "../src/field";
import { APPLE_RSUPN, FIGMA_RSUPN_TABLE, coefficientsAt, ZERO_COEFFICIENTS } from "../src/coefficients";
import type { Vec2 } from "../src/channels";
import { fieldParams, resolveShape, toContour } from "../src/shape";
import { CROSS_CHECK, crossCheckParams } from "./harness/cross-check";
import { exactSignedDistance } from "./harness/truth";

const circular = (halfW: number, halfH: number, r: number): FieldParams => ({
  halfW,
  halfH,
  reach: r,
  k: ZERO_COEFFICIENTS,
});

const smoothed = (halfW: number, halfH: number, r: number, sEff: number): FieldParams => ({
  halfW,
  halfH,
  reach: (1 + sEff) * r,
  k: coefficientsAt(FIGMA_RSUPN_TABLE, sEff).k,
});

describe("the WGSL cross-check: this field is the shader's function", () => {
  const params = crossCheckParams();

  /**
   * Which side of the level set each fixture point is on. `rsupField` IS the
   * numerator the normalization divides — family C's value is family D's `base` —
   * so the split needs no re-derivation of the corner algebra.
   */
  const split = (): { outward: number[]; inward: number[] } => {
    const outward: number[] = [];
    const inward: number[] = [];
    for (let i = 0; i < CROSS_CHECK.expected.length; i++) {
      const p = params[CROSS_CHECK.points[i * 3] as number] as FieldParams;
      const x = CROSS_CHECK.points[i * 3 + 1] as number;
      const y = CROSS_CHECK.points[i * 3 + 2] as number;
      (rsupField(p, x, y) >= 0 ? outward : inward).push(i);
    }
    return { outward, inward };
  };

  const at = (i: number): { p: FieldParams; x: number; y: number; expected: number } => ({
    p: params[CROSS_CHECK.points[i * 3] as number] as FieldParams,
    x: CROSS_CHECK.points[i * 3 + 1] as number,
    y: CROSS_CHECK.points[i * 3 + 2] as number,
    expected: CROSS_CHECK.expected[i] as number,
  });

  it("reproduces S2's f64 reference column EXACTLY on and outside the level set", () => {
    // Zero, not a tolerance. The anchor's changed arm is selected only where
    // `rho < R`, and the arm that survives is spelled as the same product in the
    // same order, so nothing here moved by even a last bit. This is the half of
    // the fixture where the declared bound's worst case lives and where S2's
    // on-hardware f32 measurement was taken, so it is the half that has to stay
    // pinned for the shader's function — and its precision — to still be pinned.
    const { outward } = split();
    let worst = 0;
    for (const i of outward) {
      const { p, x, y, expected } = at(i);
      worst = Math.max(worst, Math.abs(rsupnField(p, x, y) - expected));
    }
    expect(outward.length).toBe(2926);
    expect(worst).toBe(0);
  });

  it("is deeper than the column inside the level set, and never shallower", () => {
    // The other half of the fixture, and the whole content of the fix: inside the
    // corner sector S2's arithmetic collapsed the field toward zero, and the
    // anchored arithmetic does not. One-sidedness is the claim that makes this a
    // repair rather than a different approximation — a point can only be reported
    // DEEPER than before, never nearer the surface.
    const { inward } = split();
    let deeperCount = 0;
    let worstDeeper = 0;
    let shallower = 0;
    for (const i of inward) {
      const { p, x, y, expected } = at(i);
      const got = rsupnField(p, x, y);
      const d = Math.abs(got) - Math.abs(expected);
      if (d > 0) {
        deeperCount++;
        worstDeeper = Math.max(worstDeeper, d);
      } else if (d < -1e-12) {
        shallower++;
      }
    }
    expect(inward.length).toBe(2609);
    expect(shallower).toBe(0);
    // measured: 1000 points, worst 36.4814 px — the collapse that painted a
    // hook-shaped crease one corner reach in from every corner of a thick plate.
    expect(deeperCount).toBe(1000);
    expect(worstDeeper).toBeGreaterThan(36);
    expect(worstDeeper).toBeLessThan(37);
  });

  it("covers all three smoothing regimes and both branches of the algebra", () => {
    expect(CROSS_CHECK.shapes.map((s) => s.spec.smoothing)).toEqual([0, 0.5, 1]);
    expect(CROSS_CHECK.expected.length).toBe(5535);
  });
});

describe("exactness properties", () => {
  it("is exact along the straight edges, for any smoothing", () => {
    // The corner algebra is gated on max(q, 0), so away from the corners the
    // field must reduce to the exact half-plane distance. This is why the
    // approximation lives entirely inside the corner sector.
    for (const sEff of [0, 0.3, 0.7, 1]) {
      const p = smoothed(100, 40, 12, sEff);
      for (const y of [0, 5, 10, 15]) {
        for (const dx of [-8, -3, 0, 3, 8]) {
          expect(rsupnField(p, p.halfW + dx, y), `sEff=${sEff} dx=${dx}`).toBeCloseTo(dx, 9);
          expect(rsupField(p, p.halfW + dx, y), `rsup sEff=${sEff} dx=${dx}`).toBeCloseTo(dx, 9);
        }
      }
    }
  });

  it("is the exact circular rounded-rect distance at smoothing 0", () => {
    const p = circular(60, 45, 18);
    // Analytic rounded-box distance, derived independently of the field.
    const analytic = (x: number, y: number): number => {
      const qx = Math.abs(x) - (p.halfW - p.reach);
      const qy = Math.abs(y) - (p.halfH - p.reach);
      return Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - p.reach;
    };
    // 9 decimals, not machine precision, for one specific and documented
    // reason: the field's `max(r2, 1e-20)` guard makes rho exactly 1e-10 rather
    // than 0 in the deep interior, where the independent formula has a true 0.
    // That is the guard doing its job — it is what keeps rho == 0 from producing
    // a NaN without costing a branch — and 1e-10 px is six orders of magnitude
    // under the declared bound.
    for (let x = -80; x <= 80; x += 3.7) {
      for (let y = -60; y <= 60; y += 2.9) {
        expect(rsupnField(p, x, y)).toBeCloseTo(analytic(x, y), 9);
        expect(rsupField(p, x, y)).toBeCloseTo(analytic(x, y), 9);
      }
    }
  });

  it("is the exact stadium distance at the capsule limit", () => {
    // A capsule's corner radius equals the budget, so its effective smoothing is
    // forced to 0 and the shape is a true stadium — every family is exact on it.
    const halfW = 90;
    const halfH = 24;
    const p = circular(halfW, halfH, halfH);
    const stadium = (x: number, y: number): number =>
      Math.hypot(Math.max(Math.abs(x) - (halfW - halfH), 0), y) - halfH;
    for (let x = -110; x <= 110; x += 2.3) {
      for (let y = -40; y <= 40; y += 1.7) {
        expect(rsupnField(p, x, y), `(${x},${y})`).toBeCloseTo(stadium(x, y), 12);
      }
    }
  });

  it("is symmetric under both mirrors", () => {
    const p = smoothed(70, 45, 20, 0.62);
    for (const [x, y] of [
      [51, 33],
      [70, 0],
      [0, 45],
      [83, 51],
      [12, 7],
    ] as const) {
      const v = rsupnField(p, x, y);
      expect(rsupnField(p, -x, y)).toBeCloseTo(v, 14);
      expect(rsupnField(p, x, -y)).toBeCloseTo(v, 14);
      expect(rsupnField(p, -x, -y)).toBeCloseTo(v, 14);
    }
  });

  it("gets the sign right inside and outside", () => {
    const p = smoothed(70, 45, 20, 0.62);
    expect(rsupnField(p, 0, 0)).toBeLessThan(0);
    expect(rsupnField(p, 60, 30)).toBeLessThan(0);
    expect(rsupnField(p, 200, 0)).toBeGreaterThan(0);
    expect(rsupnField(p, 0, 90)).toBeGreaterThan(0);
    // the far corner, outside on both axes
    expect(rsupnField(p, 100, 70)).toBeGreaterThan(0);
    // and the value is a plausible distance out there
    expect(rsupnField(p, 170, 0)).toBeCloseTo(100, 9);
  });

  it("is continuous across the corner-sector boundary", () => {
    // The sector boundary is where q.y crosses 0. A jump there would read as a
    // hard seam in the rim, even though the algebra switches branch.
    const p = smoothed(80, 50, 16, 0.75);
    const yBoundary = p.halfH - p.reach;
    for (const x of [p.halfW - 4, p.halfW, p.halfW + 4]) {
      const below = rsupnField(p, x, yBoundary - 1e-7);
      const above = rsupnField(p, x, yBoundary + 1e-7);
      expect(Math.abs(above - below), `x=${x}`).toBeLessThan(1e-5);
    }
  });

  it("stays finite in the deep interior, where rho is zero", () => {
    // The r2 clamp is the field's only guard; without it the deep interior is
    // 0/0. A NaN here would be invisible until it reached a shader.
    const p = smoothed(30, 30, 9, 0.5);
    const v = rsupnField(p, 0, 0);
    expect(Number.isFinite(v)).toBe(true);
    expect(v).toBeCloseTo(-(p.halfH - p.reach) - p.reach, 9);
  });
});

/**
 * BEYOND THE MEASURED BAND.
 *
 * S2 declared the bound for |d| <= 8 px and said nothing about deeper, which was
 * honest and, for a while, sufficient. It stopped being sufficient the moment a
 * caller read the field at depth: the optics scale their lens by the material's
 * thickness, so an 18 px plate reads the field over d in [0, -26 px], more than
 * three times the measured band.
 *
 * What was down there before the normalization's anchor moved: `g = R'/rho`
 * diverging as `rho` falls toward the corner sector's vertex at
 * `(halfW - re, halfH - re)`, `1/sqrt(1 + g^2)` collapsing toward 0 with it, and
 * the field reporting a point 39 px inside a plate as 9 px inside — a false
 * near-surface region in two lobes meeting on the corner diagonal. On the public
 * demo it painted a hook-shaped crease one corner reach in from every corner of
 * the 18 px plate, and left the 5 px plate clean, because the collapsed region
 * only becomes visible once the lens reaches it.
 *
 * These are not a second declared bound — the fit was never optimised out here.
 * They are a floor: a guarantee that the field degrades gracefully with depth
 * rather than folding, so the optics can read it as deep as a real material
 * thickness goes. Every figure below is the measured worst case over the shape
 * set, with the pre-fix figure recorded beside it.
 */
describe("depth behaviour beyond the measured band", () => {
  /** The demo hero's own plates, plus the shapes that set the worst cases. */
  const DEPTH_SHAPES = [
    { size: [336, 168] as Vec2, radius: 26, profile: "continuous" as const },
    { size: [136, 72] as Vec2, radius: 14, profile: "continuous" as const },
    { size: [136, 72] as Vec2, radius: 10.8, profile: 1 },
    { size: [136, 72] as Vec2, radius: 10.8, profile: "continuous" as const },
    { size: [240, 90] as Vec2, radius: 13.5, profile: 1 },
  ];

  interface Probe {
    depth: number;
    reported: number;
    x: number;
    y: number;
    label: string;
  }

  /** Every interior grid point of one corner quadrant, with its exact depth. */
  const probeQuadrant = (spec: (typeof DEPTH_SHAPES)[number], step = 0.5): Probe[] => {
    const shape = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: spec.size,
      radii: spec.radius,
      profile: spec.profile,
    });
    const p = fieldParams(shape);
    const contour = toContour(shape);
    const label = `${spec.size.join("x")} r=${spec.radius} ${spec.profile}`;
    const out: Probe[] = [];
    for (let x = 0; x <= p.halfW; x += step) {
      for (let y = 0; y <= p.halfH; y += step) {
        const t = exactSignedDistance(contour, { x, y }).d;
        if (t > 0) continue;
        const depth = -t;
        // The shape's own medial axis is where no field is a distance; stay off it.
        if (depth > Math.min(p.halfW, p.halfH) * 0.9) continue;
        out.push({ depth, reported: -rsupnField(p, x, y), x, y, label });
      }
    }
    return out;
  };

  const probes = DEPTH_SHAPES.flatMap((s) => probeQuadrant(s));

  it("holds a graceful error envelope out to four times the measured band", () => {
    // measured, this shape set: 0.411 / 1.174 / 2.349 / 4.436 px.
    // before the anchor moved:  0.710 / 3.206 / 11.873 / 17.535 px.
    // The 16 px row is the one that matters most: 11.9 px of error at a depth a
    // 12 px-thick plate reads is not a degraded field, it is a wrong one.
    const ceilings: [number, number][] = [
      [8, 0.5],
      [12, 1.3],
      [16, 2.6],
      [24, 4.9],
      [32, 6.0],
    ];
    for (const [ceiling, bound] of ceilings) {
      let worst = 0;
      let at = "";
      for (const q of probes) {
        if (q.depth > ceiling) continue;
        const e = Math.abs(q.reported - q.depth);
        if (e > worst) {
          worst = e;
          at = `${q.label} @(${q.x}, ${q.y}) depth ${q.depth.toFixed(2)}`;
        }
      }
      expect(worst, `depth <= ${ceiling} px, worst at ${at}`).toBeLessThan(bound);
    }
  });

  it("never reports an interior point as materially nearer the surface than it is", () => {
    // The property the artifact violated, stated directly and without reference
    // to any particular thickness: if the field says a pixel is D px inside, it
    // really is at least about D px inside. A lens sized to any depth then reads
    // a region that genuinely belongs to it.
    //
    // measured: 0.411 px worst overshoot. Before the anchor moved: 28.12 px.
    let worst = 0;
    let at = "";
    for (const q of probes) {
      const overshoot = q.depth - q.reported;
      if (overshoot > worst) {
        worst = overshoot;
        at = `${q.label} @(${q.x}, ${q.y}): truth ${q.depth.toFixed(2)} px, field ${q.reported.toFixed(2)} px`;
      }
    }
    expect(worst, at).toBeLessThan(0.5);
  });

  it("keeps the 18 px demo plate's whole lens band honest", () => {
    // The regression in the terms the defect appeared in. The hero plate is
    // 336x168 with radius 26 and thickness 18, which the renderer resolves to a
    // 26.40 px lens depth, so refraction is nonzero exactly where the field reads
    // shallower than 26.40 px. Before the anchor moved, 102.58 px^2 per corner
    // qualified on the field's say-so while being 30-40 px deep in truth — the
    // hooks. The 5 px plate's own band caught 2.32 px^2, which is why it read
    // clean and the thick plate did not.
    const LENS_DEPTH_PX = 26.3965;
    let falseArea = 0;
    const step = 0.25;
    for (const q of probeQuadrant(DEPTH_SHAPES[0] as (typeof DEPTH_SHAPES)[number], step)) {
      if (q.reported < LENS_DEPTH_PX && q.depth > LENS_DEPTH_PX) falseArea += step * step;
    }
    expect(falseArea).toBe(0);
  });

  it("turns its own switch into no seam at all: the gradient is continuous across rho == R", () => {
    // The anchor introduces one new locus, `rho == R`, and a jump in the gradient
    // across it would be a crease — trading the hooks for a thin ring inside every
    // corner. It cannot happen, and the reason is worth asserting rather than
    // arguing: the locus IS the contour, `base == 0` there, and the value is
    // `base * n`, so the discontinuity in `dn` is multiplied by zero.
    //
    // Crossed head-on: for each angle across the corner sector, the point at
    // radius exactly `R(theta)` from the sector's centre, sampled either side.
    for (const spec of DEPTH_SHAPES) {
      const shape = resolveShape({
        family: "fixed-rounded-rect",
        center: [0, 0],
        size: spec.size,
        radii: spec.radius,
        profile: spec.profile,
      });
      const p = fieldParams(shape);
      const cxc = p.halfW - p.reach;
      const cyc = p.halfH - p.reach;
      const label = `${spec.size.join("x")} r=${spec.radius} ${spec.profile}`;
      let worstTurn = 0;
      let worstStep = 0;
      for (let a = 1; a <= 89; a += 0.25) {
        const th = (a * Math.PI) / 180;
        const R = cornerSupport(p, Math.sin(2 * th));
        const eps = 1e-6;
        const sample = (r: number): { dir: number; v: number } => {
          const s = rsupnFieldAndGradient(p, cxc + r * Math.cos(th), cyc + r * Math.sin(th));
          return { dir: Math.atan2(s.gy, s.gx), v: s.value };
        };
        const inside = sample(R - eps);
        const outside = sample(R + eps);
        let dd = outside.dir - inside.dir;
        while (dd > Math.PI) dd -= 2 * Math.PI;
        while (dd < -Math.PI) dd += 2 * Math.PI;
        worstTurn = Math.max(worstTurn, (Math.abs(dd) * 180) / Math.PI);
        worstStep = Math.max(worstStep, Math.abs(outside.v - inside.v));
        // and the locus really is the zero set, which is why the above holds
        expect(Math.abs(inside.v), `${label} @ ${a} deg`).toBeLessThan(1e-4);
      }
      // measured: < 1e-3 deg of turn and < 1e-5 px of step, i.e. nothing.
      expect(worstTurn, `${label}: gradient turn across rho == R`).toBeLessThan(0.01);
      expect(worstStep, `${label}: value step across rho == R`).toBeLessThan(1e-4);
    }
  });
});

describe("the analytic gradient", () => {
  it("is the true derivative: second-order convergence against central differences", () => {
    // The correctness proof for the closed form, and it does not rest on a
    // hand-picked tolerance. Central differencing has O(h^2) truncation error,
    // so if the closed form really is the derivative of the same expression, the
    // disagreement must fall by ~100x for every 10x reduction in h. If the
    // closed form were wrong by any fixed amount, the disagreement would instead
    // flatten out at that amount.
    //
    // Points within a few steps of a branch boundary (`qx == 0`, `qy == 0`) are
    // excluded: there the difference straddles the boundary and is wrong by O(h)
    // while the closed form is exact. The next test pins those directly.
    const params = crossCheckParams();

    const worstAtStep = (frac: number): { worst: number; checked: number } => {
      let worst = 0;
      let checked = 0;
      for (let i = 0; i < CROSS_CHECK.expected.length; i++) {
        const p = params[CROSS_CHECK.points[i * 3] as number] as FieldParams;
        const x = CROSS_CHECK.points[i * 3 + 1] as number;
        const y = CROSS_CHECK.points[i * 3 + 2] as number;
        const h = frac * Math.max(p.reach, 1);
        const qx = Math.abs(x) - (p.halfW - p.reach);
        const qy = Math.abs(y) - (p.halfH - p.reach);
        if (Math.abs(qx) < 8 * h || Math.abs(qy) < 8 * h) continue;
        const cd = centralGradient(rsupnField, p, x, y, h);
        if (cd.kink) continue;
        const an = rsupnFieldAndGradient(p, x, y);
        // Same expression in the same order: the value must not drift a single bit.
        expect(an.value).toBe(rsupnField(p, x, y));
        worst = Math.max(worst, Math.hypot(an.gx - cd.gx, an.gy - cd.gy));
        checked++;
      }
      return { worst, checked };
    };

    const coarse = worstAtStep(1e-5);
    const fine = worstAtStep(1e-6);

    expect(fine.checked).toBeGreaterThan(4000);
    // measured: 1.243e-6 and 1.240e-8, a ratio of 100.2
    expect(coarse.worst).toBeLessThan(5e-6);
    expect(fine.worst).toBeLessThan(5e-8);
    expect(coarse.worst / fine.worst).toBeGreaterThan(20);
  });

  it("is exact on the corner-sector boundary, where differencing is not", () => {
    // `qx == 0` with `qy < 0` is the case that caught a real mask bug: both
    // clamped-coordinate terms are masked off there, so the box-branch term has
    // to carry the whole derivative. The field is C1 across it — the straight
    // edge's distance and the box branch's distance have the same slope — so the
    // gradient is (1, 0) and nothing else.
    const p = smoothed(96, 24, 8, 0);
    const boundaryX = p.halfW - p.reach;
    const boundaryY = p.halfH - p.reach;
    // qy < 0: inside the box branch in y, so the gradient is purely along x.
    for (const y of [0, 4, 12, boundaryY - 1e-9]) {
      const at = rsupnFieldAndGradient(p, boundaryX, y);
      expect(Math.hypot(at.gx, at.gy), `y=${y}`).toBeCloseTo(1, 12);
      expect(at.gx, `y=${y}`).toBeCloseTo(1, 12);
    }
    // qy > 0: past the sector boundary in y, so it is the y edge that governs.
    for (const y of [boundaryY + 1, boundaryY + 4]) {
      const at = rsupnFieldAndGradient(p, boundaryX, y);
      expect(Math.hypot(at.gx, at.gy), `y=${y}`).toBeCloseTo(1, 12);
      expect(at.gy, `y=${y}`).toBeCloseTo(1, 12);
      expect(at.gx, `y=${y}`).toBeCloseTo(0, 12);
    }
    // and the mirror image, so the sign masks are right on both sides
    const mirrored = rsupnFieldAndGradient(p, -boundaryX, 4);
    expect(mirrored.gx).toBeCloseTo(-1, 12);
  });

  it("has unit magnitude on the straight edges and near the contour", () => {
    const p = smoothed(100, 40, 12, 0.6);
    const edge = rsupnFieldAndGradient(p, p.halfW, 0);
    expect(Math.hypot(edge.gx, edge.gy)).toBeCloseTo(1, 12);
    expect(edge.gx).toBeCloseTo(1, 12);
    expect(edge.gy).toBeCloseTo(0, 12);
  });

  it("points outward, so the sign convention is a distance and not its negative", () => {
    const p = smoothed(70, 45, 20, 0.62);
    const right = rsupnFieldAndGradient(p, 90, 0);
    expect(right.gx).toBeGreaterThan(0);
    const left = rsupnFieldAndGradient(p, -90, 0);
    expect(left.gx).toBeLessThan(0);
    const up = rsupnFieldAndGradient(p, 0, 70);
    expect(up.gy).toBeGreaterThan(0);
  });

  it("flags the interior medial-axis seam rather than reporting a normal there", () => {
    const p = smoothed(30, 30, 9, 0.5);
    expect(rsupnFieldAndGradient(p, 2, 2).kink).toBe(true);
    expect(rsupnFieldAndGradient(p, 33, 4).kink).toBe(false);
  });

  it("agrees with the free level-set normal on the contour and diverges off it", () => {
    // S2's finding: the two are the same where the rim sits, because the
    // normalization only moves level sets away from the zero set. That is why
    // the free normal is a legitimate governor-tier choice and not a defect.
    const p = smoothed(100, 100, 42, 0.5);
    const angle = (ax: number, ay: number, bx: number, by: number): number => {
      const la = Math.hypot(ax, ay);
      const lb = Math.hypot(bx, by);
      const c = Math.min(1, Math.max(-1, (ax * bx + ay * by) / (la * lb)));
      return (Math.acos(c) * 180) / Math.PI;
    };

    // Walk out along the corner diagonal to the zero level set rather than
    // guessing a point: the whole claim is about behaviour ON the contour.
    let lo = 0;
    let hi = 200;
    for (let i = 0; i < 80; i++) {
      const mid = (lo + hi) / 2;
      if (rsupnField(p, mid, mid) < 0) lo = mid;
      else hi = mid;
    }
    const t = (lo + hi) / 2;
    expect(Math.abs(rsupnField(p, t, t))).toBeLessThan(1e-9);

    const onContour = rsupnFieldAndGradient(p, t, t);
    const free = rsupLevelSetNormal(p, t, t);
    expect(angle(onContour.gx, onContour.gy, free[0], free[1])).toBeLessThan(0.05);
    // and it is a unit vector wherever it is defined
    expect(Math.hypot(free[0], free[1])).toBeCloseTo(1, 12);

    // How far the two part company OFF the contour is a matrix-wide maximum, not
    // a per-point guarantee, so it is asserted in the error-bound regression
    // suite (`test/error-bound.test.ts`) rather than here.
  });
});

describe("family C, the governor's first step", () => {
  it("shares family D's zero level set", () => {
    // Same coefficient table, same R(theta) — the normalization divides by a
    // strictly positive factor, so it cannot move the zero set.
    const p = smoothed(120, 80, 30, 0.7);
    for (const [x, y] of [
      [120, 0],
      [0, 80],
      [104, 64],
      [111, 71],
    ] as const) {
      const c = rsupField(p, x, y);
      const d = rsupnField(p, x, y);
      expect(Math.sign(c) === Math.sign(d) || Math.abs(c) < 1e-9).toBe(true);
      if (Math.abs(c) < 1e-9) expect(Math.abs(d)).toBeLessThan(1e-9);
    }
  });

  it("drifts from a unit gradient where family D does not", () => {
    // The eikonal defect is the whole reason D exists: refraction strength is
    // read off the field's slope, so a field whose gradient magnitude drifts is
    // not usable as a distance even where its zero set is right.
    const p = smoothed(120, 80, 30, 0.8);
    const h = 1e-3 * p.reach;
    let worstC = 0;
    let worstD = 0;
    for (let t = 0.05; t < 1; t += 0.05) {
      const x = p.halfW - p.reach + p.reach * Math.cos((t * Math.PI) / 2);
      const y = p.halfH - p.reach + p.reach * Math.sin((t * Math.PI) / 2);
      worstC = Math.max(worstC, Math.abs(centralGradient(rsupField, p, x, y, h).magnitude - 1));
      worstD = Math.max(worstD, Math.abs(centralGradient(rsupnField, p, x, y, h).magnitude - 1));
    }
    expect(worstD).toBeLessThan(worstC);
  });
});

describe("the Apple-direct coefficients", () => {
  it("are a distinct fit from anything on the Figma smoothing axis", () => {
    // Decision Log #20 rejected routing `profile: "continuous"` through Figma at
    // smoothing 0.66. If this ever stops being true, the two references have
    // been conflated somewhere.
    const nearest = coefficientsAt(FIGMA_RSUPN_TABLE, 0.528665).k;
    const gap = Math.max(...APPLE_RSUPN.k.map((v, i) => Math.abs(v - (nearest[i] as number))));
    expect(gap).toBeGreaterThan(0.1);
  });

  it("fit closer to their own reference than the Figma family fits Apple's", () => {
    expect(APPLE_RSUPN.contourDevPerR).toBeLessThan(0.00196015);
  });
});
