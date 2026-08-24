/**
 * The Contour IR, and the integrity checks that make it usable as ground truth.
 *
 * The four properties that matter are the ones S2 leaned on when it called these
 * figures load-bearing rather than plausible: the ring closes, it is G1, at
 * smoothing 0 it degenerates to a shape an independent formula also describes,
 * and the sign of the distance agrees with an independent inside test.
 */

import { describe, expect, it } from "vitest";

import { uniformRadii, type Vec2 } from "../src/channels";
import {
  contourArea,
  contourCurvatureBreaks,
  contourGap,
  contourLength,
  contourTangentBreak,
  contourToCubics,
  segmentPoint,
} from "../src/contour";
import { resolveFromChannels, resolveShape, toContour } from "../src/shape";
import { exactSignedDistance, insideByRayCast } from "./harness/truth";
import { referenceContourFor } from "./harness/metrics";

const figmaShape = (size: Vec2, radius: number, smoothing: number) =>
  resolveFromChannels(
    { center: [0, 0], size, radii: uniformRadii(radius), smoothing, thickness: 0 },
    "figma-smoothing",
  );

const SMOOTHINGS = [0, 0.2, 0.4, 0.6, 0.8, 1];

describe("ring integrity", () => {
  it("closes to 1e-9 at every smoothing", () => {
    for (const s of SMOOTHINGS) {
      const c = referenceContourFor(figmaShape([240, 160], 40, s));
      expect(contourGap(c), `smoothing ${s}`).toBeLessThan(1e-9);
    }
  });

  it("is G1 to 1e-15 radians — the joins were derived, not merely butted together", () => {
    for (const s of SMOOTHINGS) {
      const c = referenceContourFor(figmaShape([240, 160], 40, s));
      expect(contourTangentBreak(c), `smoothing ${s}`).toBeLessThan(1e-14);
    }
  });

  it("is G1 but NOT G2, and reports the curvature step rather than hiding it", () => {
    // S2 is explicit that nothing in the kernel may assume G2: the cubic meets
    // the circular arc with a curvature step of 0.39-0.57 / r. Smoothing 1.0 is
    // the only curvature-continuous member, because the arc vanishes there.
    const breaks = (s: number): number =>
      Math.max(...contourCurvatureBreaks(referenceContourFor(figmaShape([240, 160], 40, s)), 40));
    expect(breaks(0.4)).toBeGreaterThan(0.3);
    expect(breaks(0.4)).toBeLessThan(0.6);
    expect(breaks(0.8)).toBeGreaterThan(0.3);
    // smoothing 1.0 has no arc at all, so there is no cubic/arc join to break at
    expect(breaks(1)).toBeLessThan(1e-9);
    // smoothing 0 is the OPPOSITE extreme and the worst case: a plain circular
    // corner steps straight from zero curvature on the edge to 1/r on the arc,
    // for a normalized break of exactly 1. That full-magnitude step is the defect
    // continuous corners exist to remove, so it belongs here as a measured
    // baseline rather than as an expectation of smoothness.
    expect(breaks(0)).toBeCloseTo(1, 9);
  });

  it("degenerates to a plain circular rounded rectangle at smoothing 0", () => {
    // Two implementations of the same shape agreeing is the strongest single
    // check available: the exact solver against the closed-form rounded-box
    // distance. S2 used exactly this to certify its ground truth.
    const shape = figmaShape([240, 160], 40, 0);
    const c = referenceContourFor(shape);
    const closedForm = (x: number, y: number): number => {
      const qx = Math.abs(x) - (120 - 40);
      const qy = Math.abs(y) - (80 - 40);
      return Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - 40;
    };
    let worst = 0;
    for (let x = -150; x <= 150; x += 7) {
      for (let y = -110; y <= 110; y += 5) {
        worst = Math.max(worst, Math.abs(exactSignedDistance(c, { x, y }).d - closedForm(x, y)));
      }
    }
    expect(worst).toBeLessThan(1e-9);
  });

  it("gets the sign right, checked against independent ray casting", () => {
    const c = referenceContourFor(figmaShape([200, 120], 30, 0.6));
    let checked = 0;
    for (let x = -130; x <= 130; x += 11) {
      for (let y = -90; y <= 90; y += 7) {
        const r = exactSignedDistance(c, { x, y });
        if (Math.abs(r.d) < 1e-3) continue;
        expect(r.d < 0, `(${x},${y})`).toBe(insideByRayCast(c, { x, y }, 512));
        checked++;
      }
    }
    expect(checked).toBeGreaterThan(300);
  });

  it("encloses less area as smoothing rises, since the corner cuts in further", () => {
    let prev = Number.POSITIVE_INFINITY;
    for (const s of SMOOTHINGS) {
      const area = contourArea(referenceContourFor(figmaShape([240, 160], 40, s)));
      expect(area, `smoothing ${s}`).toBeLessThan(prev);
      prev = area;
    }
    // and never more than the un-rounded rectangle
    expect(prev).toBeLessThan(240 * 160);
  });

  it("has a perimeter between the inscribed rounded rect and the bounding box", () => {
    const c = referenceContourFor(figmaShape([240, 160], 40, 0.6));
    expect(contourLength(c)).toBeGreaterThan(2 * (240 - 80) + 2 * (160 - 80));
    expect(contourLength(c)).toBeLessThan(2 * 240 + 2 * 160);
  });
});

describe("the IR is authoring and interchange, not the render form", () => {
  it("carries winding, closure and corner metadata so a consumer need not infer them", () => {
    const c = toContour(resolveShape({ family: "fixed-rounded-rect", center: [10, 20], size: [200, 100], radii: 24, profile: 0.6 }));
    expect(c.closed).toBe(true);
    expect(c.winding).toBe("clockwise-y-up");
    expect(c.corner.radius).toBe(24);
    expect(c.center).toEqual([10, 20]);
  });

  it("applies the centre to the segments, so the ring is where the shape is", () => {
    const centred = toContour(
      resolveShape({ family: "fixed-rounded-rect", center: [0, 0], size: [200, 100], radii: 24, profile: 0.6 }),
    );
    const moved = toContour(
      resolveShape({ family: "fixed-rounded-rect", center: [70, -30], size: [200, 100], radii: 24, profile: 0.6 }),
    );
    for (let i = 0; i < centred.segments.length; i++) {
      const a = segmentPoint(centred.segments[i]!, 0.37);
      const b = segmentPoint(moved.segments[i]!, 0.37);
      expect(b.x).toBeCloseTo(a.x + 70, 9);
      expect(b.y).toBeCloseTo(a.y - 30, 9);
    }
  });

  it("exports pure cubics for Bezier-only consumers, exactly enough to be dull", () => {
    // One cubic per arc, via the (4/3)tan(sweep/4) handle identity — the same
    // identity Apple's own .continuous path uses for its mid-corner arc, which S2
    // measured matching to 1.5e-7. It holds because a corner arc never sweeps more
    // than 90 degrees.
    const shape = figmaShape([240, 160], 40, 0.4);
    const withArcs = referenceContourFor(shape);
    const cubics = contourToCubics(withArcs);

    expect(withArcs.segments.some((s) => s.kind === "arc")).toBe(true);
    expect(cubics.segments.some((s) => s.kind === "arc")).toBe(false);
    expect(cubics.segments.length).toBe(withArcs.segments.length);

    // Measured GEOMETRICALLY — radial deviation from the arc — not by comparing
    // the two curves at equal parameter. The cubic's parameterization is not
    // uniform in angle, so a pointwise-in-t comparison reports parameterization
    // drift (~1.6e-3 here) and says nothing about whether the shapes agree.
    let worst = 0;
    for (let i = 0; i < withArcs.segments.length; i++) {
      const orig = withArcs.segments[i]!;
      if (orig.kind !== "arc") continue;
      const approx = cubics.segments[i]!;
      for (let t = 0; t <= 1; t += 0.01) {
        const b = segmentPoint(approx, t);
        const radial = Math.hypot(b.x - orig.center.x, b.y - orig.center.y);
        worst = Math.max(worst, Math.abs(radial - orig.radius) / orig.radius);
      }
    }
    // relative to the arc radius; a single cubic over <= 90 degrees is this good
    expect(worst).toBeLessThan(3e-4);
  });

  it("emits no arc where the shape has no arc", () => {
    // smoothing 1.0 consumes the whole corner with shoulder cubics; smoothing 0
    // is all arc and no shoulders.
    const full = referenceContourFor(figmaShape([240, 160], 40, 1));
    expect(full.segments.some((s) => s.kind === "arc")).toBe(false);
    const none = referenceContourFor(figmaShape([240, 160], 40, 0));
    expect(none.segments.some((s) => s.kind === "cubic")).toBe(false);
  });
});
