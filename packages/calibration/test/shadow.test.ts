import { describe, expect, it } from "vitest";

import { srgbByteToLinear } from "../src/color";
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

  /**
   * The same shadow in two windows. Built on one body slid down the canvas, so
   * the shadow, the backdrop and the region's own geometry are identical between
   * the two reads and the only thing that changes is how much room the frame
   * leaves below it.
   */
  const slidDown = (offsetYPx: number) => {
    const region = componentRegion(
      { kind: "rrect", size: [80, 60], radius: 10, offset: [0, offsetYPx] },
      { canvas: CANVAS, scale: 1, width: CANVAS.width, height: CANVAS.height },
    );
    const render = fromLinearLuminance(CANVAS.width, CANVAS.height, (x, y) => {
      if ((region.silhouette.mask[y * CANVAS.width + x] ?? 0) !== 0) return 0.3;
      const outward = Math.max(0, distanceTo(region, x, y));
      return 0.6 * (1 - 0.45 * Math.exp(-outward / 6));
    });
    return { region, field: shadowField(render, backdrop, region) };
  };

  it("reads a shadow's true reach through a window that holds it", () => {
    // 0.45·e^(−s/6) crosses the 0.01 threshold at 6·ln(45) ≈ 22.8 px, and the
    // frame is 70 px away below and 60 px either side, so nothing is clipped.
    const { field } = slidDown(0);

    expect(field.truncatedSides).toEqual([]);
    expect(field.clearanceBelowPx).toBeGreaterThan(69);
    expect(field.extentBelowPx ?? 0).toBeGreaterThan(20);
    expect(field.extentBelowPx ?? 0).toBeLessThan(26);
    expect(field.offsetYPx).toBeDefined();
  });

  it("refuses the same reach when the canvas cuts in, rather than reporting the window", () => {
    // The identical shadow with the body slid to 8 px off the bottom edge. The
    // walk is still well above threshold when the capture ends, so what it would
    // report below is the frame's size — the reading vitrea's own bed produced
    // on `photo__rrect-lg__rest`, where a 20 px margin read σ ≈ 8% low.
    const { field } = slidDown(62);

    expect(field.clearanceBelowPx).toBeGreaterThan(7);
    expect(field.clearanceBelowPx).toBeLessThan(9);
    expect(field.truncatedSides).toEqual(["below"]);
    expect(field.extentBelowPx).toBeUndefined();
    // The pair that side belongs to goes with it: half a difference is not a
    // displacement when one of the two terms is the frame.
    expect(field.offsetYPx).toBeUndefined();

    // The three sides the window still holds are measurements, and they stay.
    expect(field.extentAbovePx ?? 0).toBeGreaterThan(20);
    expect(field.extentLeftPx ?? 0).toBeGreaterThan(20);
    expect(field.offsetXPx).toBeDefined();
  });
});

/**
 * The affine pair beside the occlusion ratio (W14 X7).
 *
 * Every render here is built from *exact* sRGB byte values, so the fit's ground
 * truth is not approximate: a two-level backdrop gives the least-squares line
 * two points, the black squares read `c` and the white squares read `a + c`, and
 * a recovery that is off by more than float noise is the estimator being wrong
 * rather than the raster being coarse. That is the same construction claims
 * §5.62 read the reference through, so the two are comparable readings.
 */
describe("the shadow axis's affine pair", () => {
  /** A pitch-8 checkerboard of two exact bytes, as linear luminance. */
  const checker = (darkByte: number, lightByte: number): CalibrationImage =>
    fromLinearLuminance(CANVAS.width, CANVAS.height, (x, y) =>
      srgbByteToLinear((Math.floor(x / 8) + Math.floor(y / 8)) % 2 === 0 ? darkByte : lightByte),
    );

  /**
   * A render whose exterior takes one exact byte over the backdrop's dark
   * squares and another over its light ones — an affine map of the backdrop with
   * `c = linear(overDark)` and `a = linear(overLight) − linear(overDark)` when
   * the backdrop's own dark square is black.
   */
  const affineOver = (overDarkByte: number, overLightByte: number): CalibrationImage =>
    fromLinearLuminance(CANVAS.width, CANVAS.height, (x, y) => {
      if ((REGION.silhouette.mask[y * CANVAS.width + x] ?? 0) !== 0) return 0.3;
      const onDark = (Math.floor(x / 8) + Math.floor(y / 8)) % 2 === 0;
      return srgbByteToLinear(onDark ? overDarkByte : overLightByte);
    });

  const bandOf = (field: ReturnType<typeof shadowField>, direction: string, label: string) =>
    field.affine.find((s) => s.direction === direction && s.ringLabel === label);

  it("recovers a and c exactly from a render that is an affine map of its backdrop", () => {
    const backdrop = checker(0, 255);
    const cTrue = srgbByteToLinear(30);
    const aTrue = srgbByteToLinear(220) - cTrue;
    const field = shadowField(affineOver(30, 220), backdrop, REGION);

    expect(field.affine.length).toBeGreaterThan(0);
    for (const sample of field.affine) {
      if (sample.slopeALinear === undefined) continue;
      expect(sample.slopeALinear).toBeCloseTo(aTrue, 10);
      expect(sample.interceptCLinear ?? 99).toBeCloseTo(cTrue, 10);
      expect(sample.rSquared ?? 0).toBeCloseTo(1, 10);
    }
    // The lift is the reading the ratio cannot make: the same render's occlusion
    // is a ratio over the light squares alone and says nothing about the light
    // sitting on the black ones.
    expect(bandOf(field, "below", "0-3")?.interceptCLinear ?? 0).toBeGreaterThan(0);
  });

  it("reads a pure multiply as c = 0 and a = 1 − occlusion", () => {
    // A black multiply is inert over black, so the fit's intercept is zero to
    // the last digit and its slope is the transmission the occlusion ratio
    // reports as its complement. This is X4's recovery in miniature: it is what
    // vitrea's own W8 shadow must read back as.
    const transmission = srgbByteToLinear(200);
    const backdrop = checker(0, 255);
    const field = shadowField(affineOver(0, 200), backdrop, REGION);

    const band = bandOf(field, "all", "0-3");
    expect(band?.interceptCLinear ?? 99).toBeCloseTo(0, 12);
    expect(band?.slopeALinear ?? 0).toBeCloseTo(transmission, 12);
    // And the axis's own ratio agrees: the light squares are the only ones above
    // the backdrop floor, and they lost exactly 1 − transmission of their light.
    expect(field.strengthPeak ?? 0).toBeCloseTo(1 - transmission, 10);
    expect(band?.slopeALinear ?? 0).toBeCloseTo(1 - (field.strengthPeak ?? 0), 10);
  });

  it("leaves the pair ABSENT over a solid backdrop and reports the level instead", () => {
    const solid = solidLuminance(CANVAS.width, CANVAS.height, 0.6);
    const render = fromLinearLuminance(CANVAS.width, CANVAS.height, (x, y) =>
      (REGION.silhouette.mask[y * CANVAS.width + x] ?? 0) !== 0 ? 0.3 : 0.6 * 0.8,
    );
    const field = shadowField(render, solid, REGION);

    const band = bandOf(field, "below", "0-3");
    expect(band).toBeDefined();
    expect(band?.slopeALinear).toBeUndefined();
    expect(band?.interceptCLinear).toBeUndefined();
    expect(band?.rSquared).toBeUndefined();
    expect(band?.unidentifiableReason).toBe("flat-backdrop");
    // What a constant backdrop does identify, reported rather than dropped: the
    // level and the backdrop it sits over. Their ratio is a + c/bg, and nothing
    // in the band splits it.
    // To two decimals: both images are 8-bit, and 0.48 linear is between codes.
    expect(band?.renderedLevelLinear ?? 0).toBeCloseTo(0.6 * 0.8, 2);
    expect(band?.backdropMeanLinear ?? 0).toBeCloseTo(0.6, 2);
    expect(band?.backdropStdDevLinear ?? 1).toBeLessThan(0.001);
  });

  it("fits in LINEAR light, so an encoded lift reads an order of magnitude smaller", () => {
    // The composite a tier actually paints: the ENCODED backdrop keeps 1 − α of
    // itself and an encoded lift of 0.039 is added on top — claims §5.60 §3's
    // number, in the space it was read in. Over a black square that lift decodes
    // to about 0.0030 linear, a factor of thirteen, because it sits where sRGB's
    // transfer function is steepest (claims §5.62's third Surprise). A fit run
    // on the encoded values would return the 0.039; this one must not.
    const encodedLift = 0.039;
    const overDarkByte = Math.round(encodedLift * 255);
    const overLightByte = Math.round((1 * (1 - 0.13) + encodedLift) * 255);
    const field = shadowField(
      affineOver(overDarkByte, overLightByte),
      checker(0, 255),
      REGION,
    );

    const band = bandOf(field, "below", "0-6");
    const c = band?.interceptCLinear ?? 0;
    expect(c).toBeCloseTo(srgbByteToLinear(overDarkByte), 12);
    expect(c).toBeGreaterThan(0.002);
    expect(c).toBeLessThan(0.004);
    expect(encodedLift / c).toBeGreaterThan(8);
  });

  it("keeps the pair where the occlusion ratio is absent, which is where a lift shows alone", () => {
    // A near-black backdrop with contrast: every normalised figure goes, because
    // there is no light to remove — and the lift is measured cleanly, because a
    // multiply removes nothing from a black pixel and whatever light is there
    // came from a term that is not one. This is the case W14 X7 exists for.
    const backdrop = checker(0, 60);
    const field = shadowField(affineOver(10, 65), backdrop, REGION);

    expect(field.backdropSupport).toBe(0);
    expect(field.unmeasurableReason).toBeDefined();
    expect(field.strengthPeak).toBeUndefined();

    const band = bandOf(field, "below", "0-3");
    expect(band?.interceptCLinear ?? 0).toBeCloseTo(srgbByteToLinear(10), 12);
    expect(band?.rSquared ?? 0).toBeCloseTo(1, 10);
  });

  it("cuts its bands in CSS px, so a 2x capture's bands are twice as wide in device px", () => {
    const backdrop = checker(0, 255);
    const render = affineOver(30, 220);
    const atOneX = shadowField(render, backdrop, REGION, { scale: 1 });
    const atTwoX = shadowField(render, backdrop, REGION, { scale: 2 });

    const one = bandOf(atOneX, "below", "0-3")?.sampleCount ?? 0;
    const two = bandOf(atTwoX, "below", "0-3")?.sampleCount ?? 0;
    expect(one).toBeGreaterThan(0);
    // 0–3 CSS px is 0–6 device px at 2x, so it holds about twice the pixels. Not
    // exactly twice: the annulus grows outward, so the outer ring is longer.
    expect(two / one).toBeGreaterThan(1.8);
    expect(two / one).toBeLessThan(2.4);
    // The pair itself does not move — the same map fitted over more of it.
    expect(bandOf(atTwoX, "below", "0-3")?.slopeALinear ?? 0).toBeCloseTo(
      bandOf(atOneX, "below", "0-3")?.slopeALinear ?? 1,
      10,
    );
  });
});
