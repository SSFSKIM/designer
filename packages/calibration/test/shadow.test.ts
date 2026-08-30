import { describe, expect, it } from "vitest";

import { componentRegion, type ComponentRegion, type DeclaredComponent } from "../src/component-region";
import type { CalibrationImage } from "../src/image";
import { shadowField } from "../src/metrics/shadow";
import { normalCdf } from "../src/stats";
import { fromLinearLuminance, solidLuminance } from "./synthesise";

/**
 * A square canvas with a rounded rect in the middle, so the four directions have
 * room for a shadow that is not clipped by the frame.
 */
const CANVAS = { width: 200, height: 200 } as const;
const BODY: DeclaredComponent = { kind: "rrect", size: [80, 60], radius: 10 };

const REGION: ComponentRegion = componentRegion(BODY, {
  canvas: CANVAS,
  scale: 1,
  width: CANVAS.width,
  height: CANVAS.height,
});

const distanceTo = (region: ComponentRegion, x: number, y: number): number =>
  region.signedDistancePx[y * CANVAS.width + x] ?? 0;

/**
 * A synthetic shadow with a known description: a multiplicative occlusion that
 * decays exponentially with distance from the *same body shifted down by
 * `offsetY`*, which is what an offset drop shadow is.
 *
 * Ground truth, by construction:
 *
 *   - strength at the contour is `peak`;
 *   - the occlusion falls to the axis's 0.01 threshold at
 *     `λ · ln(peak / 0.01)` from the shifted contour, so the reach below the
 *     declared contour exceeds the reach above it by exactly `2 · offsetY`;
 *   - the decay length is `λ` in every direction, so the pooled profile — a mean
 *     of exponentials of one rate — decays at `λ` too.
 */
function shadowedRender(options: {
  readonly backdrop: number;
  readonly body: number;
  readonly peak: number;
  readonly decayPx: number;
  readonly offsetYPx: number;
}): CalibrationImage {
  const shifted = componentRegion(
    { kind: "rrect", size: [80, 60], radius: 10, offset: [0, options.offsetYPx] },
    { canvas: CANVAS, scale: 1, width: CANVAS.width, height: CANVAS.height },
  );
  return fromLinearLuminance(CANVAS.width, CANVAS.height, (x, y) => {
    if ((REGION.silhouette.mask[y * CANVAS.width + x] ?? 0) !== 0) return options.body;
    const outward = Math.max(0, distanceTo(shifted, x, y));
    return options.backdrop * (1 - options.peak * Math.exp(-outward / options.decayPx));
  });
}

describe("the shadow axis", () => {
  const backdrop = solidLuminance(CANVAS.width, CANVAS.height, 0.6);

  it("recovers a synthetic shadow's strength, offset, reach and falloff", () => {
    const peak = 0.4;
    const decayPx = 8;
    const offsetYPx = 6;
    const render = shadowedRender({ backdrop: 0.6, body: 0.3, peak, decayPx, offsetYPx });
    const field = shadowField(render, backdrop, REGION);

    expect(field.backdropSupport).toBe(1);
    // The strength is a ring mean pooled over all four directions, so it cannot
    // exceed the built-in peak and sits a little under it: the ring above the
    // component is already `offsetY` px from the shifted contour and has decayed
    // by `e^(−6/8)` before it is averaged in.
    expect(field.strengthPeak ?? 0).toBeGreaterThan(peak * 0.75);
    expect(field.strengthPeak ?? 0).toBeLessThanOrEqual(peak);

    // The headline: the displacement the reach implies is the one built in.
    expect(field.offsetYPx ?? 0).toBeGreaterThan(offsetYPx - 2);
    expect(field.offsetYPx ?? 0).toBeLessThan(offsetYPx + 2);
    expect(Math.abs(field.offsetXPx ?? 99)).toBeLessThanOrEqual(1);
    expect(field.extentBelowPx ?? 0).toBeGreaterThan(field.extentAbovePx ?? 0);

    // Reach: 0.4·e^(−s/8) = 0.01 at s ≈ 29.5 px from the shifted contour, which
    // the left and right sectors see undisplaced.
    const sideways = ((field.extentLeftPx ?? 0) + (field.extentRightPx ?? 0)) / 2;
    expect(sideways).toBeGreaterThan(24);
    expect(sideways).toBeLessThan(35);

    // The decay length comes back, though the pooled profile of an *offset*
    // shadow is a mean of four differently-displaced exponentials rather than
    // one, so which family fits it best is not a fair question here — that is
    // what the equal-terms test below is for.
    expect(field.falloffLengthPx ?? 0).toBeGreaterThan(decayPx * 0.8);
    expect(field.falloffLengthPx ?? 0).toBeLessThan(decayPx * 1.2);
    expect(field.falloffResidual ?? 1).toBeLessThan(0.1);

    // The mass centroid describes the same displacement, inflated because only
    // the visible half of the field — the part not under the component — is in
    // it. Reported as its own quantity for exactly that reason.
    expect(field.centroidOffsetYPx ?? 0).toBeGreaterThan(0);
    expect(Math.abs(field.centroidOffsetXPx ?? 99)).toBeLessThan(1);
  });

  it("reads a render that casts no shadow as zero reach and an UNDEFINED offset", () => {
    // vitrea, today: the material stops at its contour and the surround is the
    // bare backdrop. Strength zero is a measurement; an offset is not, because
    // there is nothing whose displacement it could describe.
    const flat = fromLinearLuminance(CANVAS.width, CANVAS.height, (x, y) =>
      (REGION.silhouette.mask[y * CANVAS.width + x] ?? 0) !== 0 ? 0.3 : 0.6,
    );
    const field = shadowField(flat, backdrop, REGION);

    expect(field.meanDeparture).toBeCloseTo(0, 6);
    expect(field.strengthPeak ?? 1).toBeCloseTo(0, 6);
    expect(field.extentAbovePx).toBe(0);
    expect(field.extentBelowPx).toBe(0);
    expect(field.extentLeftPx).toBe(0);
    expect(field.extentRightPx).toBe(0);
    expect(field.offsetXPx).toBeUndefined();
    expect(field.offsetYPx).toBeUndefined();
    expect(field.centroidOffsetYPx).toBeUndefined();
    expect(field.falloffLengthPx).toBeUndefined();
    expect(field.falloffSigmaPx).toBeUndefined();
  });

  it("refuses a lone qualifying ring at the contour as reach, and so reports no offset", () => {
    // A one-pixel darkening ring hugging the contour is a body's own antialiased
    // edge, not a shadow, and it is the case the consecutive-pair rule exists to
    // reject. Crediting ring 0 with a phantom predecessor would report a 1 px
    // reach in all four directions and — worse — a defined offset of (0, 0),
    // which the doctrine reserves for a displacement that was actually measured.
    const haloOnly = fromLinearLuminance(CANVAS.width, CANVAS.height, (x, y) => {
      if ((REGION.silhouette.mask[y * CANVAS.width + x] ?? 0) !== 0) return 0.3;
      return distanceTo(REGION, x, y) < 1 ? 0.6 * 0.7 : 0.6;
    });
    const field = shadowField(haloOnly, backdrop, REGION);

    // The ring is real and the strength records it — at ring 0, which is what
    // says it is an edge.
    expect(field.strengthPeak ?? 0).toBeGreaterThan(0.25);
    expect(field.strengthPeakDistancePx).toBe(0);

    expect(field.extentAbovePx).toBe(0);
    expect(field.extentBelowPx).toBe(0);
    expect(field.extentLeftPx).toBe(0);
    expect(field.extentRightPx).toBe(0);
    expect(field.offsetXPx).toBeUndefined();
    expect(field.offsetYPx).toBeUndefined();
    // And nothing beyond that ring is left to fit a falloff to.
    expect(field.falloffSigmaPx).toBeUndefined();
    expect(field.falloffLengthPx).toBeUndefined();
  });

  /**
   * An un-offset surround whose occlusion follows `shape` of the distance from
   * the declared contour — so the pooled ring profile IS that shape, and the two
   * families are being asked a fair question.
   */
  const surroundWith = (amplitude: number, shape: (distance: number) => number): CalibrationImage =>
    fromLinearLuminance(CANVAS.width, CANVAS.height, (x, y) => {
      if ((REGION.silhouette.mask[y * CANVAS.width + x] ?? 0) !== 0) return 0.3;
      return 0.6 * (1 - amplitude * shape(Math.max(0, distanceTo(REGION, x, y))));
    });

  it("recovers the blur radius of a blurred-edge shadow — the shape a real one has", () => {
    // A filled body convolved with a Gaussian, which is what `box-shadow` and a
    // GPU shadow pass both produce, so σ is the parameter a renderer is given.
    const sigmaPx = 12;
    const field = shadowField(
      surroundWith(0.45, (d) => 1 - normalCdf(d / sigmaPx)),
      backdrop,
      REGION,
    );

    expect(field.falloffSigmaPx ?? 0).toBeGreaterThan(sigmaPx * 0.85);
    expect(field.falloffSigmaPx ?? 0).toBeLessThan(sigmaPx * 1.15);
    expect(field.falloffSigmaResidual ?? 1).toBeLessThan(0.05);
  });

  it("compares the two families on equal terms — each wins on its own profile", () => {
    // The reason both are reported. Same points, same objective, two free
    // parameters each, so neither can win on flexibility: whichever family a
    // profile is actually in is the one with the smaller residual. A test that
    // only ever showed the Gaussian winning would not distinguish "the bed's
    // shadows are Gaussian" from "this estimator always says Gaussian".
    const gaussian = shadowField(surroundWith(0.45, (d) => 1 - normalCdf(d / 12)), backdrop, REGION);
    expect(gaussian.falloffSigmaResidual ?? 1).toBeLessThan(gaussian.falloffResidual ?? 1);

    const exponential = shadowField(surroundWith(0.45, (d) => Math.exp(-d / 12)), backdrop, REGION);
    expect(exponential.falloffResidual ?? 1).toBeLessThan(exponential.falloffSigmaResidual ?? 1);
    expect(exponential.falloffLengthPx ?? 0).toBeGreaterThan(12 * 0.85);
    expect(exponential.falloffLengthPx ?? 0).toBeLessThan(12 * 1.15);
  });

  it("leaves every normalised figure absent over a backdrop with no light to remove", () => {
    // `dark-solid` is 0.0117 in linear light. A multiplicative occlusion of any
    // strength is analytically invisible there, so the axis reports its support
    // and refuses the ratio rather than reporting a shadow of zero.
    const dark = solidLuminance(CANVAS.width, CANVAS.height, 0.0117);
    const render = fromLinearLuminance(CANVAS.width, CANVAS.height, (x, y) =>
      (REGION.silhouette.mask[y * CANVAS.width + x] ?? 0) !== 0 ? 0.3 : 0.0117 * 0.7,
    );
    const field = shadowField(render, dark, REGION);

    expect(field.backdropSupport).toBe(0);
    expect(field.unmeasurableReason).toMatch(/not identifiable/);
    expect(field.strengthPeak).toBeUndefined();
    expect(field.extentBelowPx).toBeUndefined();
    expect(field.offsetYPx).toBeUndefined();
    // The absolute departure survives, because a difference is defined where a
    // ratio is not — and it is the figure the damage report quoted.
    expect(field.meanDeparture).toBeGreaterThan(0);
  });

  it("profiles from the DECLARED contour, so a material invisible against its backdrop still reports", () => {
    // The shape axis has nothing to work with here — the body is within the
    // extraction threshold of its own backdrop — but the shadow is still there,
    // and an axis that started from the extracted silhouette would have no
    // contour to start from.
    const render = shadowedRender({ backdrop: 0.6, body: 0.6, peak: 0.3, decayPx: 6, offsetYPx: 4 });
    const field = shadowField(render, backdrop, REGION);
    expect(field.extentBelowPx ?? 0).toBeGreaterThan(field.extentAbovePx ?? 0);
    expect(field.strengthPeak ?? 0).toBeGreaterThan(0.2);
  });
});
