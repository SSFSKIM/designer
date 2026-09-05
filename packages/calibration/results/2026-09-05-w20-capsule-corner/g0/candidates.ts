/**
 * W20 G0 — the four candidate corner constructions, sampled as polylines for the pixel reader.
 *
 * The probe's question is what Apple draws for `RoundedRectangle(cornerRadius: r, style:
 * .continuous)` once `APPLE_REACH * r` no longer fits half the short side. It is answered by
 * putting Apple's own pixels next to curves the GEOMETRY PACKAGE can actually produce, so that
 * whatever wins is a policy G1 can adopt by name rather than a shape someone drew.
 *
 * The four, all built through the package's public API:
 *
 *   `vitrea-clamp`      `buildAppleContour(halfW, halfH, r)` — today's policy. The radius is
 *                       clamped to `budget / APPLE_REACH` and Apple's dump is applied at the
 *                       clamped radius, so the reach exactly fills the side.
 *   `shoulder-compress` `resolveCornerConstruction(halfW, halfH, r, APPLE_REACH - 1)` through
 *                       `buildReferenceContour`. The radius is kept (clamped only at the budget)
 *                       and the reference family's own budget clamp pulls the effective smoothing
 *                       down to `budget / r - 1`, reaching exactly 0 at the capsule limit. This is
 *                       the reference family's policy, which `corner.ts` calls exact on a stadium.
 *   `circular-arc`      the same construction at smoothing 0 — the plain circular rounded
 *                       rectangle at the requested radius. It is what `shoulder-compress`
 *                       degenerates to at the capsule limit and differs from it below.
 *   `apple-overflow`    Apple's dump scaled by the REQUESTED radius with the overflow allowed, by
 *                       assembling `APPLE_CORNER_DUMP` through `ringFromCorner` at
 *                       `reach = APPLE_REACH * r`. Above the ratio this reach exceeds the half
 *                       side and the ring's straight edges reverse, so the shape self-intersects:
 *                       it is the control that should fail, and it is here because a candidate
 *                       set with no failing member proves nothing about the reader.
 *
 * Below the saturation ratio all four agree except in the shoulder, which is the point of the
 * `r14` rungs: they measure the reader against a corner every candidate draws the same way.
 *
 * The capsule controls are emitted too, as `resolveShape`'s exact stadium — `Capsule()` is a
 * circular stadium by definition and this is the curve the reader must recover before any rung's
 * reading is worth anything.
 *
 * Output: JSON on stdout — one entry per component, each candidate a polyline in the CENTRED,
 * Y-UP frame in CSS px (which is device px at this probe's 1x). Point spacing is under 0.02 px, so
 * a nearest-point distance read off the polyline is exact well below the 0.5 px grid floor.
 *
 * Usage: `pnpm --filter @vitrea/geometry exec tsx <this file> > candidates.json`
 */

import {
  APPLE_CORNER_DUMP,
  APPLE_REACH,
  type Contour,
  type ContourSegment,
  type Point,
  buildAppleContour,
  buildReferenceContour,
  resolveCornerConstruction,
  resolveShape,
  ringFromCorner,
  segmentLength,
  segmentPoint,
  toContour,
// The geometry package is not a dependency of `@vitrea/calibration` — nothing in the harness has
// ever needed it — so it is imported by path rather than by name, from the source the package
// publishes. Adding a dependency to run one probe script would be a permanent edge in the graph
// for a spike's sake.
} from "../../../../geometry/src/index";

/** Point spacing on the emitted polylines, in CSS px. */
const STEP = 0.02;

/** Sample a contour into a polyline at roughly `STEP` spacing along each segment. */
function sample(c: Contour): [number, number][] {
  const out: [number, number][] = [];
  for (const s of c.segments) {
    const n = Math.max(2, Math.ceil(segmentLength(s, 64) / STEP));
    for (let i = 0; i < n; i++) {
      const p: Point = segmentPoint(s, i / n);
      out.push([p.x, p.y]);
    }
  }
  return out;
}

/**
 * Apple's dump at the requested radius with no clamp at all. `buildAppleContour` refuses to do
 * this — it clamps and reports `saturated` — so the corner is assembled here from the same dump
 * the package exports, which keeps the control honest: it is Apple's curve, only overflowing.
 */
function appleOverflowContour(halfW: number, halfH: number, radius: number): Contour {
  const pts: Point[] = APPLE_CORNER_DUMP.map(([u, w]) => ({
    x: halfW - (u as number) * radius,
    y: halfH - (w as number) * radius,
  }));
  pts.reverse();
  const corner: ContourSegment[] = [];
  for (let i = 0; i + 3 < pts.length; i += 3) {
    corner.push({
      kind: "cubic",
      p0: pts[i] as Point,
      p1: pts[i + 1] as Point,
      p2: pts[i + 2] as Point,
      p3: pts[i + 3] as Point,
    });
  }
  const reach = APPLE_REACH * radius;
  return {
    segments: ringFromCorner(halfW, halfH, reach, corner),
    closed: true,
    winding: "clockwise-y-up",
    corner: {
      radius,
      smoothingEff: APPLE_REACH - 1,
      reach,
      a: 0,
      b: 0,
      c: 0,
      d: 0,
      arcSectionLength: 0,
      arcMeasure: (50 * Math.PI) / 180,
      budget: Math.min(halfW, halfH),
    },
    center: [0, 0],
  };
}

interface Entry {
  component: string;
  kind: "rrect" | "capsule";
  size: [number, number];
  radius: number;
  ratio: number;
  saturated: boolean;
  candidates: Record<string, [number, number][]>;
  notes: Record<string, unknown>;
}

const RUNGS: [string, number, number, number][] = [
  ["rrect-120x44-r14", 120, 44, 14],
  ["rrect-120x44-r16", 120, 44, 16],
  ["rrect-120x44-r18", 120, 44, 18],
  ["rrect-120x44-r20", 120, 44, 20],
  ["rrect-120x44-r22", 120, 44, 22],
  ["rrect-44x44-r14", 44, 44, 14],
  ["rrect-44x44-r18", 44, 44, 18],
  ["rrect-44x44-r22", 44, 44, 22],
];

const CAPSULES: [string, number, number][] = [
  ["capsule-120x44", 120, 44],
  ["capsule-44x44", 44, 44],
];

const entries: Entry[] = [];

for (const [component, w, h, r] of RUNGS) {
  const halfW = w / 2;
  const halfH = h / 2;
  const budget = Math.min(halfW, halfH);
  const apple = buildAppleContour(halfW, halfH, r);
  const compress = resolveCornerConstruction(halfW, halfH, r, APPLE_REACH - 1);
  const circular = resolveCornerConstruction(halfW, halfH, r, 0);
  entries.push({
    component,
    kind: "rrect",
    size: [w, h],
    radius: r,
    ratio: r / Math.min(w, h),
    saturated: apple.saturated,
    candidates: {
      "vitrea-clamp": sample(apple),
      "shoulder-compress": sample(buildReferenceContour(halfW, halfH, compress)),
      "circular-arc": sample(buildReferenceContour(halfW, halfH, circular)),
      "apple-overflow": sample(appleOverflowContour(halfW, halfH, r)),
    },
    notes: {
      budget,
      appleReach: APPLE_REACH,
      "vitrea-clamp": { radius: apple.corner.radius, reach: apple.corner.reach },
      "shoulder-compress": {
        radius: compress.radius,
        smoothingEff: compress.smoothingEff,
        reach: compress.reach,
        arcMeasureDeg: (compress.arcMeasure * 180) / Math.PI,
      },
      "circular-arc": { radius: circular.radius, reach: circular.reach },
      "apple-overflow": { radius: r, reach: APPLE_REACH * r },
    },
  });
}

for (const [component, w, h] of CAPSULES) {
  const shape = resolveShape({ family: "capsule", center: [0, 0], size: [w, h] });
  entries.push({
    component,
    kind: "capsule",
    size: [w, h],
    radius: Math.min(w, h) / 2,
    ratio: 0.5,
    saturated: false,
    candidates: { stadium: sample(toContour(shape)) },
    notes: {
      radius: shape.corner.radius,
      smoothingEff: shape.corner.smoothingEff,
      reach: shape.corner.reach,
    },
  });
}

process.stdout.write(`${JSON.stringify({ step: STEP, entries })}\n`);
