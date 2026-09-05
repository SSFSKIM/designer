/**
 * The render path against the declaration, for every shape the calibration bed
 * draws (W20 G0; claims §5.83).
 *
 * The renderer never calls `resolveShape`. `renderer-webgpu/src/instances.ts`
 * takes `surface.reference ?? "apple-continuous"` and calls
 * `resolveFromChannels(channels, reference, surface.family)`, which hands the
 * radius to `resolveCorner` and never reads the family — so a `capsule` is
 * resolved as a rounded rectangle whose radius the Apple reference's own budget
 * policy clamps to `min(halfW, halfH) / APPLE_REACH`. This file measures the
 * consequence for each declared shape rather than asserting the mechanism: what
 * radius and reach the two paths produce, whether the Apple contour reports
 * itself saturated, and how far the drawn contour lies from the geometry the
 * scene matrix declares.
 *
 * The declared shape is the CIRCULAR rounded rectangle of the declared radius —
 * for a capsule, the stadium. That is the same rule `calibration/src/
 * component-region.ts` rasterises its search region from and the same rule the
 * native harness lays out (`Capsule()` is a circular stadium by definition), so
 * a distance measured against it is a distance against the declaration both
 * sides were built from. For a rounded rectangle it is NOT zero even when the
 * render path is exactly right: Apple's `.continuous` corner is not a circular
 * arc, and the residual reported below is that curve's own departure, which is
 * why the rows carry the render-vs-spec distance beside it.
 *
 * The numbers asserted here are the ones the defect produces TODAY. W20 G1
 * flips them: after the fix a capsule resolves at its budget with reach equal to
 * the budget, `capsuleRenderRadius` becomes 22 rather than 14.39, and
 * `capsuleContourGap` collapses to the Apple-vs-circular residual the rounded
 * rectangles already show. Each assertion says which way it moves.
 */

import { describe, expect, it } from "vitest";

import { APPLE_REACH, APPLE_SATURATION_RADIUS_RATIO, buildAppleContour } from "../src/apple";
import { halfExtents, uniformRadii, type ShapeChannels, type Vec2 } from "../src/channels";
import { type Contour, segmentPoint } from "../src/contour";
import { resolveFromChannels, resolveShape, toContour, type ResolvedShape } from "../src/shape";
import { say } from "./harness/say";

/**
 * One surface as `apps/reference-apple/scenes.json` declares it, in points.
 *
 * `radius` is absent on a capsule for the same reason it is absent in the scene
 * matrix: half the short side is the definition, and a second copy of the rule
 * could disagree with the harness's.
 */
interface Declared {
  readonly label: string;
  readonly family: "capsule" | "fixed-rounded-rect";
  readonly size: Vec2;
  readonly radius?: number;
}

const BED: readonly Declared[] = [
  { label: "capsule-button", family: "capsule", size: [120, 44] },
  { label: "toolbar-group item", family: "capsule", size: [44, 44] },
  { label: "rrect-sm", family: "fixed-rounded-rect", size: [64, 32], radius: 8 },
  { label: "rrect-md", family: "fixed-rounded-rect", size: [160, 96], radius: 20 },
  { label: "rrect-ml", family: "fixed-rounded-rect", size: [224, 128], radius: 27 },
  { label: "rrect-lg", family: "fixed-rounded-rect", size: [280, 160], radius: 34 },
  { label: "glass-over-glass base", family: "fixed-rounded-rect", size: [220, 130], radius: 24 },
  { label: "glass-over-glass over", family: "fixed-rounded-rect", size: [120, 56], radius: 16 },
];

/**
 * The declared radius, by the scene matrix's own rule — half the short side for
 * a capsule, the stated number for a rounded rectangle.
 */
function declaredRadius(shape: Declared): number {
  return shape.radius ?? Math.min(shape.size[0], shape.size[1]) / 2;
}

/**
 * The channel vector `platform-web` builds for this surface.
 *
 * `registerHost` spreads one radius to the Vec4 (X8 rider 3) and defaults
 * `smoothing` to `DEFAULT_HOST_SHAPE.smoothing`, which is 0; the calibration
 * scene page passes no smoothing at all, so 0 is what the bed renders. The react
 * binding sends `smoothingFor(undefined)` — the Apple seed — instead, which
 * under the Apple reference is the same resolution: `resolveCorner` pins
 * smoothing at the seed there and reads the channel only on the Figma axis. The
 * radius a capsule carries is `capsuleRadius(w, h)`, half the short side, which
 * is the declared radius above.
 */
function channelsFor(shape: Declared, scale: number): ShapeChannels {
  return {
    center: [0, 0],
    size: [shape.size[0] * scale, shape.size[1] * scale],
    radii: uniformRadii(declaredRadius(shape) * scale),
    smoothing: 0,
    thickness: 8,
  };
}

/** The path the renderer takes: channels in, family carried but never read. */
function renderPath(shape: Declared, scale: number): ResolvedShape {
  return resolveFromChannels(channelsFor(shape, scale), "apple-continuous", shape.family);
}

/** The path the spec resolver takes, which is the one that makes a capsule exact. */
function specPath(shape: Declared, scale: number): ResolvedShape {
  const size: Vec2 = [shape.size[0] * scale, shape.size[1] * scale];
  return shape.family === "capsule"
    ? resolveShape({ family: "capsule", center: [0, 0], size, thickness: 8 })
    : resolveShape({
        family: "fixed-rounded-rect",
        center: [0, 0],
        size,
        radii: declaredRadius(shape) * scale,
        thickness: 8,
      });
}

/** Points per contour segment. Dense enough that the sampling is not the number. */
const SAMPLES_PER_SEGMENT = 512;

function samplePoints(contour: Contour): readonly (readonly [number, number])[] {
  const points: (readonly [number, number])[] = [];
  for (const segment of contour.segments) {
    for (let index = 0; index < SAMPLES_PER_SEGMENT; index += 1) {
      const point = segmentPoint(segment, index / SAMPLES_PER_SEGMENT);
      points.push([point.x, point.y]);
    }
  }
  return points;
}

/**
 * Exact signed distance to a circular rounded rectangle centred at the origin —
 * the declaration's own geometry, negative inside. The same closed form
 * `calibration/src/component-region.ts` uses, so the two instruments measure
 * against one shape.
 */
function declaredSignedDistance(
  x: number,
  y: number,
  halfW: number,
  halfH: number,
  radius: number,
): number {
  const qx = Math.abs(x) - (halfW - radius);
  const qy = Math.abs(y) - (halfH - radius);
  return Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - radius;
}

/** Max |signed distance| from a contour to the declared shape, in the contour's units. */
function contourGapToDeclared(contour: Contour, shape: Declared, scale: number): number {
  const { halfW, halfH } = halfExtents([shape.size[0] * scale, shape.size[1] * scale]);
  const radius = declaredRadius(shape) * scale;
  let worst = 0;
  for (const [x, y] of samplePoints(contour)) {
    worst = Math.max(worst, Math.abs(declaredSignedDistance(x, y, halfW, halfH, radius)));
  }
  return worst;
}

/** Max nearest-neighbour distance from one contour's samples to the other's. */
function contourGapBetween(a: Contour, b: Contour): number {
  const other = samplePoints(b);
  let worst = 0;
  for (const [x, y] of samplePoints(a)) {
    let nearest = Number.POSITIVE_INFINITY;
    for (const [ox, oy] of other) {
      const distance = (x - ox) * (x - ox) + (y - oy) * (y - oy);
      if (distance < nearest) nearest = distance;
    }
    worst = Math.max(worst, Math.sqrt(nearest));
  }
  return worst;
}

interface Row {
  readonly label: string;
  readonly family: string;
  readonly declared: number;
  readonly renderRadius: number;
  readonly renderReach: number;
  readonly specRadius: number;
  readonly specReach: number;
  readonly saturated: boolean;
  readonly ratio: number;
  readonly gapToDeclared: number;
  readonly gapRenderVsSpec: number;
}

function measure(shape: Declared, scale: number): Row {
  const render = renderPath(shape, scale);
  const spec = specPath(shape, scale);
  const { halfW, halfH } = halfExtents([shape.size[0] * scale, shape.size[1] * scale]);
  return {
    label: shape.label,
    family: shape.family,
    declared: declaredRadius(shape) * scale,
    renderRadius: render.corner.radius,
    renderReach: render.corner.reach,
    specRadius: spec.corner.radius,
    specReach: spec.corner.reach,
    // The Apple contour builder is the thing that reports saturation; the
    // resolver returns the clamped radius with no flag on it, which is a
    // separate half of why this went unseen for nineteen waves.
    saturated: buildAppleContour(halfW, halfH, declaredRadius(shape) * scale).saturated,
    ratio: declaredRadius(shape) / Math.min(shape.size[0], shape.size[1]),
    gapToDeclared: contourGapToDeclared(toContour(render), shape, scale),
    gapRenderVsSpec: contourGapBetween(toContour(render), toContour(spec)),
  };
}

function table(scale: number): readonly Row[] {
  return BED.map((shape) => measure(shape, scale));
}

function report(scale: number, rows: readonly Row[]): string {
  const header =
    `\n=== the render path at ${scale}x (device px) ===\n` +
    "shape                  r/min   declared  render r  render reach  spec r   sat  " +
    "gap→declared  gap render↔spec\n";
  return (
    header +
    rows
      .map(
        (row) =>
          `${row.label.padEnd(22)} ${row.ratio.toFixed(4)}  ` +
          `${row.declared.toFixed(2).padStart(8)}  ${row.renderRadius.toFixed(2).padStart(8)}  ` +
          `${row.renderReach.toFixed(2).padStart(12)}  ${row.specRadius.toFixed(2).padStart(6)}  ` +
          `${(row.saturated ? "YES" : " no").padStart(3)}  ` +
          `${row.gapToDeclared.toFixed(4).padStart(12)}  ${row.gapRenderVsSpec.toFixed(4).padStart(15)}`,
      )
      .join("\n")
  );
}

const ROWS_1X = table(1);
const ROWS_2X = table(2);

const row = (rows: readonly Row[], label: string): Row => {
  const found = rows.find((candidate) => candidate.label === label);
  if (found === undefined) throw new Error(`no row "${label}"`);
  return found;
};

describe("the render path against the declaration, on the calibration bed", () => {
  it("prints the conformance table at 1x and 2x", () => {
    // A report, not an assertion: the tables are the deliverable, and the
    // assertions below pin the entries a fix has to move.
    say(`${report(1, ROWS_1X)}\n${report(2, ROWS_2X)}`);
    expect(ROWS_1X).toHaveLength(BED.length);
    expect(ROWS_2X).toHaveLength(BED.length);
  });

  it("clamps every capsule and no rounded rectangle — the ratio decides, not the family", () => {
    const saturated = ROWS_1X.filter((candidate) => candidate.saturated).map((c) => c.label);
    expect(saturated).toEqual(["capsule-button", "toolbar-group item"]);
    // Both capsules sit at exactly one half; every rounded rectangle on the bed
    // is under Apple's saturation ratio, which is why the defect is a capsule
    // defect and not a bed-wide one.
    for (const candidate of ROWS_1X) {
      expect(candidate.ratio > APPLE_SATURATION_RADIUS_RATIO).toBe(candidate.saturated);
    }
  });

  it("draws the 120x44 capsule at 14.39 CSS px of 22 — W20 G1 makes this 22", () => {
    const capsule = row(ROWS_1X, "capsule-button");
    expect(capsule.declared).toBe(22);
    expect(capsule.renderRadius).toBeCloseTo(22 / APPLE_REACH, 6);
    expect(capsule.renderRadius).toBeCloseTo(14.3916, 4);
    // The spec resolver is already right, and nothing on the render path reaches it.
    expect(capsule.specRadius).toBe(22);
    expect(capsule.specReach).toBe(22);
  });

  it("puts the drawn capsule contour 3.15 px outside the declared stadium at 1x", () => {
    // A smaller radius in the same box is a FULLER shape, so the gap is outward
    // and it is largest on the diagonal. W20 G1 collapses this to zero: a
    // stadium's corner is a circular arc under either reference.
    expect(row(ROWS_1X, "capsule-button").gapToDeclared).toBeCloseTo(3.1797, 3);
    expect(row(ROWS_1X, "toolbar-group item").gapToDeclared).toBeCloseTo(3.1797, 3);
    expect(row(ROWS_1X, "capsule-button").gapRenderVsSpec).toBeCloseTo(3.1797, 2);
  });

  it("scales exactly with the backing scale, so the 2x rows are the 1x rows doubled", () => {
    // The clamp is a ratio, so it is scale-invariant — which is worth pinning,
    // because it says the 2x bed carries the same defect and not a worse one.
    for (const [index, at1x] of ROWS_1X.entries()) {
      const at2x = ROWS_2X[index] as Row;
      expect(at2x.renderRadius).toBeCloseTo(at1x.renderRadius * 2, 9);
      expect(at2x.renderReach).toBeCloseTo(at1x.renderReach * 2, 9);
      expect(at2x.gapToDeclared).toBeCloseTo(at1x.gapToDeclared * 2, 6);
    }
    expect(row(ROWS_2X, "capsule-button").renderRadius).toBeCloseTo(28.783, 3);
    expect(row(ROWS_2X, "capsule-button").gapToDeclared).toBeCloseTo(6.3594, 3);
  });

  it("resolves every rounded rectangle identically on both paths", () => {
    for (const candidate of ROWS_1X.filter((c) => c.family === "fixed-rounded-rect")) {
      expect(candidate.renderRadius).toBe(candidate.declared);
      expect(candidate.renderRadius).toBe(candidate.specRadius);
      expect(candidate.renderReach).toBe(candidate.specReach);
      expect(candidate.gapRenderVsSpec).toBe(0);
    }
  });

  it("reports Apple's own departure from a circular corner, so the capsule gap reads against it", () => {
    // The declared geometry is circular; Apple's `.continuous` corner is not. On
    // every rounded rectangle of the bed the whole gap to the declaration is
    // that departure, and it is a fixed fraction of the radius — 0.0137985 r, the
    // same number on all six shapes at both scales, because the curve is
    // similar in r. The capsule's gap is 0.14453 r: an order of magnitude
    // larger, and a clamp rather than a curve. Only the second is visible to
    // the shape axis, whose floor is the raster grid at ±0.5 px, and only the
    // second is the thing W20 G1 removes.
    const rrects = [...ROWS_1X, ...ROWS_2X].filter((c) => c.family === "fixed-rounded-rect");
    for (const candidate of rrects) {
      expect(candidate.gapToDeclared / candidate.declared).toBeCloseTo(0.0137985, 6);
    }
    for (const candidate of [...ROWS_1X, ...ROWS_2X].filter((c) => c.family === "capsule")) {
      expect(candidate.gapToDeclared / candidate.declared).toBeCloseTo(0.14453, 5);
    }
  });
});

/**
 * The same clamp, reached from the two public doors an application uses.
 *
 * `packages/react/src/surface.tsx` registers `shapeFamily: capsule ? "capsule" :
 * "fixed-rounded-rect"` with `capsuleRadius(w, h)` — half the short side — so
 * every `<GlassSurface capsule>` lands on the row above. `DEFAULT_HOST_SHAPE`
 * (`platform-web/src/host.ts`) is radius 12, which saturates on any host under
 * 12 / APPLE_SATURATION_RADIUS_RATIO ≈ 36.7 px short-side: the ordinary control
 * heights are exactly where it bites.
 */
describe("the exposure for authors", () => {
  const DEFAULT_HOST_RADIUS = 12;

  it("clamps the default host shape below a 36.7 px short side", () => {
    const heights = [24, 32, 36, 40, 48];
    const rows = heights.map((height) => {
      const resolved = resolveFromChannels(
        {
          center: [0, 0],
          size: [200, height],
          radii: uniformRadii(DEFAULT_HOST_RADIUS),
          smoothing: 0,
          thickness: 8,
        },
        "apple-continuous",
      );
      return { height, radius: resolved.corner.radius, excess: DEFAULT_HOST_RADIUS - resolved.corner.radius };
    });
    say(
      `\n=== DEFAULT_HOST_SHAPE radius 12, 200 x h ===\n` +
        rows
          .map(
            (entry) =>
              `h ${String(entry.height).padStart(3)}  drawn r ${entry.radius.toFixed(4).padStart(8)}` +
              `  clamped by ${entry.excess.toFixed(4)} CSS px`,
          )
          .join("\n"),
    );
    expect(rows.map((entry) => Number(entry.radius.toFixed(4)))).toEqual([
      7.85, 10.4666, 11.775, 12, 12,
    ]);
    // The threshold, stated as the number an author can check a design against.
    expect(DEFAULT_HOST_RADIUS / APPLE_SATURATION_RADIUS_RATIO).toBeCloseTo(36.688, 3);
  });
});
