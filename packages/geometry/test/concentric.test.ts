/**
 * The concentric resolver, and the property that makes X8 rider 2 true.
 *
 * The claim under test is that a concentric child's boundary sits within the
 * field's error budget of the PARENT's offset level set — that is why `thickness`
 * needs no error bound of its own. It is measured against the parent field
 * directly rather than argued from the construction, and measuring it turned up
 * something the rider does not say on its face: there are TWO ways to realize a
 * concentric child, and only one of them is inside the field's budget.
 *
 *   - `concentricField` — the parent field shifted by the inset. Its zero set IS
 *     the offset by construction, so the only error is the field's own, and it
 *     holds <= 0.18 px at every inset up to 8.
 *   - `resolveConcentric` — the child as a separately resolved shape, which a
 *     caller needs for bounds, hit-testing and IR export. Here the child's own
 *     reference contour is not the parent's true offset, because exact inward
 *     offsets of continuous-corner cubics leave the cubic family. That mismatch
 *     grows with inset (0.105 px at 1 px, 0.326 px at 8 px) and past ~4 px it
 *     dominates the field error entirely.
 *
 * Both are asserted, separately, with their measured numbers.
 */

import { describe, expect, it } from "vitest";

import {
  concentricField,
  concentricFieldAndGradient,
  DEFAULT_CONCENTRIC_MIN_RADIUS,
  MEASURED_BAND_PX,
  resolveConcentric,
  resolveThicknessInnerShape,
} from "../src/concentric";
import { rsupnField, rsupnFieldAndGradient } from "../src/field";
import { fieldParams, resolveShape, toContour } from "../src/shape";
import { segmentNormal, segmentPoint } from "../src/contour";
import { referenceContourFor } from "./harness/metrics";

const parentOf = (size: [number, number], radius: number, profile: number | "continuous" = 0.6) =>
  resolveShape({
    family: "fixed-rounded-rect",
    center: [0, 0],
    size,
    radii: radius,
    profile,
    thickness: 6,
  });

describe("the derivation", () => {
  it("insets every side and drops the radius by the same amount", () => {
    const parent = parentOf([200, 120], 30);
    const { shape } = resolveConcentric(parent, { inset: 8 });
    expect(shape.channels.size).toEqual([184, 104]);
    expect(shape.channels.radii).toEqual([22, 22, 22, 22]);
    expect(shape.channels.center).toEqual(parent.channels.center);
  });

  it("inherits the profile, because concentricity governs radii and not the curve", () => {
    // The research explicitly refuted that conflation, so the child is the same
    // KIND of corner as the parent, only smaller.
    for (const profile of [0, 0.4, 0.8] as const) {
      const parent = parentOf([300, 200], 50, profile);
      const { shape } = resolveConcentric(parent, { inset: 10 });
      expect(shape.channels.smoothing, `profile ${profile}`).toBe(parent.channels.smoothing);
      expect(shape.corner.reference).toBe(parent.corner.reference);
    }
  });

  it("inherits the Apple reference too, not just the Figma axis", () => {
    const parent = parentOf([300, 200], 50, "continuous");
    const { shape } = resolveConcentric(parent, { inset: 10 });
    expect(shape.corner.reference).toBe("apple-continuous");
    expect(shape.corner.k).toEqual(parent.corner.k);
  });

  it("defaults thickness to the parent's, and takes an override", () => {
    const parent = parentOf([200, 120], 30);
    expect(resolveConcentric(parent, { inset: 4 }).shape.channels.thickness).toBe(6);
    expect(resolveConcentric(parent, { inset: 4, thickness: 2 }).shape.channels.thickness).toBe(2);
  });

  it("puts the level-set child EXACTLY on the parent's offset, at the field's own accuracy", () => {
    // X8 rider 2 as written. `concentricField` is the parent field shifted by the
    // inset, so its zero set IS the parent's -inset level set by construction —
    // there is no second approximation. What remains is the parent field's own
    // value error at that depth, measured here against the parent's TRUE contour
    // distance, and it must sit inside the declared band bound.
    for (const inset of [1, 2, 4, 8]) {
      for (const profile of [0, 0.4, 0.6, 0.8, 1] as const) {
        const parent = parentOf([320, 220], 60, profile);
        const parentRef = referenceContourFor(parent);

        // Walk the parent's true offset curve: points at exact distance -inset
        // from the reference contour, found by offsetting along the inward normal.
        let worst = 0;
        for (const seg of parentRef.segments) {
          for (let t = 0; t <= 1; t += 0.01) {
            const b = segmentPoint(seg, t);
            const n = segmentNormal(seg, t);
            const q = { x: b.x - n.x * inset, y: b.y - n.y * inset };
            // At a true offset point the level-set field must read 0.
            worst = Math.max(worst, Math.abs(concentricField(parent, inset, q.x, q.y)));
          }
        }
        // the declared band bound, 0.170 px for |d| <= 8
        expect(worst, `inset ${inset}, profile ${profile}`).toBeLessThan(0.18);
      }
    }
  });

  it("costs more when the child is instantiated as its own resolved shape", () => {
    // The second approximation, measured rather than waved at. §Geometry warns
    // that exact inward offsets of continuous-corner cubics leave the cubic
    // family, so the child's own reference contour is NOT the parent's true
    // offset. Past about 4 px of inset at high smoothing, that mismatch — not the
    // pseudo-SDF — is the dominant error term, and it exceeds the field's budget.
    //
    // Recorded as a bound so the cost is a known quantity: a caller that needs a
    // separately instantiated child knows what it is paying, and a caller that
    // does not should render `concentricField` instead.
    const measured: { inset: number; worst: number }[] = [];
    for (const inset of [1, 2, 4, 8]) {
      let worst = 0;
      for (const profile of [0, 0.4, 0.6, 0.8, 1] as const) {
        const parent = parentOf([320, 220], 60, profile);
        const { shape } = resolveConcentric(parent, { inset });
        const parentField = fieldParams(parent);
        for (const seg of toContour(shape).segments) {
          for (let t = 0; t <= 1; t += 0.01) {
            const q = segmentPoint(seg, t);
            worst = Math.max(worst, Math.abs(rsupnField(parentField, q.x, q.y) - -inset));
          }
        }
      }
      measured.push({ inset, worst });
    }

    // measured: 0.105 / 0.132 / 0.190 / 0.326 px at inset 1 / 2 / 4 / 8
    expect(measured[0]!.worst).toBeLessThan(0.12);
    expect(measured[1]!.worst).toBeLessThan(0.15);
    expect(measured[2]!.worst).toBeLessThan(0.21);
    expect(measured[3]!.worst).toBeLessThan(0.35);

    // and it grows with inset, which is the signature of a family mismatch rather
    // than of the field's (inset-independent) band error
    for (let i = 1; i < measured.length; i++) {
      expect(measured[i]!.worst).toBeGreaterThan(measured[i - 1]!.worst);
    }
  });

  it("has the level-set path beat the resolved-shape path wherever they differ", () => {
    // The claim that decides which one C6 renders.
    const inset = 8;
    const parent = parentOf([320, 220], 60, 1);
    const parentRef = referenceContourFor(parent);
    const { shape } = resolveConcentric(parent, { inset });
    const parentField = fieldParams(parent);

    let levelSet = 0;
    for (const seg of parentRef.segments) {
      for (let t = 0; t <= 1; t += 0.01) {
        const b = segmentPoint(seg, t);
        const n = segmentNormal(seg, t);
        levelSet = Math.max(
          levelSet,
          Math.abs(concentricField(parent, inset, b.x - n.x * inset, b.y - n.y * inset)),
        );
      }
    }

    let resolved = 0;
    for (const seg of toContour(shape).segments) {
      for (let t = 0; t <= 1; t += 0.01) {
        const q = segmentPoint(seg, t);
        resolved = Math.max(resolved, Math.abs(rsupnField(parentField, q.x, q.y) - -inset));
      }
    }

    expect(levelSet).toBeLessThan(resolved);
  });

  it("shifts the level set without touching its gradient", () => {
    // An offset is a constant added to the field, so the normal at the inner
    // surface is the parent's normal at the parent's accuracy. That is why
    // thickness needs no gradient bound either.
    const parent = parentOf([320, 220], 60, 0.6);
    const direct = rsupnFieldAndGradient(fieldParams(parent), 140, 90);
    const shifted = concentricFieldAndGradient(parent, 5, 140, 90);
    expect(shifted.value).toBeCloseTo(direct.value + 5, 15);
    expect(shifted.gx).toBe(direct.gx);
    expect(shifted.gy).toBe(direct.gy);
  });

  it("is exact on the straight edges at any inset", () => {
    // The field is exact against straight edges by construction, so the level-set
    // offset there is not an approximation at all. Only the corner is.
    const parent = parentOf([320, 220], 60, 0.6);
    const parentField = fieldParams(parent);
    for (const inset of [1, 4, 8, 20]) {
      const { shape } = resolveConcentric(parent, { inset });
      const halfW = shape.channels.size[0] / 2;
      expect(rsupnField(parentField, halfW, 0), `inset ${inset}`).toBeCloseTo(-inset, 9);
    }
  });

  it("is exact for a circular parent, where the offset really is in the family", () => {
    // An inward offset of a circular arc is a circular arc of radius r - t, so at
    // smoothing 0 the level-set approximation is not an approximation.
    const parent = parentOf([320, 220], 60, 0);
    const parentField = fieldParams(parent);
    const { shape } = resolveConcentric(parent, { inset: 8 });
    let worst = 0;
    for (const seg of toContour(shape).segments) {
      for (let t = 0; t <= 1; t += 0.01) {
        const p = segmentPoint(seg, t);
        worst = Math.max(worst, Math.abs(rsupnField(parentField, p.x, p.y) - -8));
      }
    }
    expect(worst).toBeLessThan(1e-9);
  });
});

describe("the radius floor", () => {
  it("floors the derived radius rather than letting the corner go sharp", () => {
    const parent = parentOf([200, 120], 10);
    const result = resolveConcentric(parent, { inset: 9 });
    // 10 - 9 = 1, below the advisory floor
    expect(result.shape.corner.radius).toBe(DEFAULT_CONCENTRIC_MIN_RADIUS);
    expect(result.radiusFloored).toBe(true);
  });

  it("reports when it did NOT floor, so a caller can tell a pure offset apart", () => {
    const parent = parentOf([200, 120], 30);
    const result = resolveConcentric(parent, { inset: 8 });
    expect(result.radiusFloored).toBe(false);
    expect(result.shape.corner.radius).toBe(22);
  });

  it("takes an explicit floor, and never exceeds the child's own budget", () => {
    const parent = parentOf([200, 40], 18);
    // a floor of 40 cannot be honoured: the child's short side is 40 - 2*8 = 24,
    // so its budget is 12.
    const result = resolveConcentric(parent, { inset: 8, minRadius: 40 });
    expect(result.shape.corner.radius).toBe(12);
    expect(result.shape.corner.budget).toBe(12);
  });

  it("collapses cleanly when the inset eats the whole shape", () => {
    const parent = parentOf([40, 20], 10);
    const result = resolveConcentric(parent, { inset: 30 });
    expect(result.shape.channels.size).toEqual([0, 0]);
    expect(result.shape.corner.radius).toBe(0);
    expect(Number.isFinite(rsupnField(fieldParams(result.shape), 0, 0))).toBe(true);
  });
});

describe("the thickness channel", () => {
  it("derives the inner surface from thickness, which is why it needs no own bound", () => {
    const parent = parentOf([320, 220], 60, 0.6);
    const inner = resolveThicknessInnerShape(parent);
    expect(inner.shape.channels.size).toEqual([320 - 12, 220 - 12]);
    expect(inner.beyondMeasuredBand).toBe(false);
  });

  it("flags a thickness past the band S2 actually measured", () => {
    // 8 px is the measured band. Beyond it the bound is not claimed, and saying so
    // is the difference between a contract and an assumption.
    expect(MEASURED_BAND_PX).toBe(8);
    const parent = parentOf([320, 220], 60, 0.6);
    expect(resolveConcentric(parent, { inset: 8 }).beyondMeasuredBand).toBe(false);
    expect(resolveConcentric(parent, { inset: 8.1 }).beyondMeasuredBand).toBe(true);
  });
});
