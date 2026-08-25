/**
 * Backdrop analysis and its temporal hysteresis.
 *
 * The property under test is the one §Foreground adaptation exists to guarantee:
 * **scrolling never pumps the material.** That comes from a specific detail of
 * `LowPassHysteresisDriver` — the band is measured against the *committed* value,
 * not the moving output — so these tests drive the composition rather than
 * re-testing motion's own driver, which C2's suite already pins.
 */

import { describe, expect, it } from "vitest";

import {
  adaptiveTint,
  createAdaptationState,
  readbackDue,
  statsFromBuffer,
  ZERO_STATS,
} from "../src/analysis";
import {
  ADAPTIVE_LUMINANCE_HIGH,
  ADAPTIVE_LUMINANCE_LOW,
  ADAPTIVE_TINT_DARK,
  ADAPTIVE_TINT_LIGHT,
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
  type MaterialProfile,
} from "../src/material";

const stats = (luminance: number, variance = 0.05, edge = 0.1) => ({
  luminance,
  variance,
  edgeDensity: edge,
  sampleCount: 4096,
});

describe("stats decoding", () => {
  it("reads the four floats the reduction writes", () => {
    expect(statsFromBuffer([0.3, 0.02, 0.15, 4096])).toEqual({
      luminance: 0.3,
      variance: 0.02,
      edgeDensity: 0.15,
      sampleCount: 4096,
    });
  });

  it("treats a short buffer as zeroes rather than as undefined", () => {
    expect(statsFromBuffer([])).toEqual(ZERO_STATS);
  });
});

describe("the adaptation state", () => {
  it("reports nothing observed until a reduction with samples arrives", () => {
    const state = createAdaptationState();
    expect(state.values.observed).toBe(false);

    // A reduction that took no samples is not an observation.
    state.observe({ ...stats(0.5), sampleCount: 0 });
    expect(state.values.observed).toBe(false);

    state.observe(stats(0.5));
    expect(state.values.observed).toBe(true);
  });

  it("jumps on reset, so a page load does not fade in from black", () => {
    const state = createAdaptationState();
    state.reset(stats(0.6));
    expect(state.values.luminance).toBeCloseTo(0.6, 12);
    expect(state.settled).toBe(true);
  });

  it("filters rather than following, so a change arrives over time", () => {
    const state = createAdaptationState();
    state.reset(stats(0));
    state.observe(stats(1));

    state.advance(16.7);
    const early = state.values.luminance;
    expect(early).toBeGreaterThan(0);
    expect(early).toBeLessThan(0.2);

    // Ten time constants: the filter is exponential, so "arrived" is asymptotic.
    for (let i = 0; i < 300; i += 1) state.advance(16.7);
    expect(state.values.luminance).toBeCloseTo(1, 4);
  });

  it("rejects jitter inside the band, which is what stops scroll pumping", () => {
    const state = createAdaptationState();
    state.reset(stats(0.5));

    // A 0.03 wobble is inside the 0.04 band and must not reach the filter at all.
    for (let i = 0; i < 50; i += 1) {
      state.observe(stats(i % 2 === 0 ? 0.53 : 0.47));
      state.advance(16.7);
    }
    expect(state.values.luminance).toBeCloseTo(0.5, 9);
  });

  it("measures the band from the committed value, not from the moving output", () => {
    // Against the output, a slow drift leaks through one small step at a time.
    const state = createAdaptationState();
    state.reset(stats(0));

    for (let i = 1; i <= 20; i += 1) {
      state.observe(stats(i * 0.01));
      state.advance(16.7);
    }
    // 20 steps of 0.01 crossed the band only four times, so the committed value is
    // far below the last observation.
    expect(state.values.luminance).toBeLessThan(0.12);
  });

  it("is frame-rate invariant, because the driver integrates in closed form", () => {
    const coarse = createAdaptationState();
    const fine = createAdaptationState();
    coarse.reset(stats(0));
    fine.reset(stats(0));
    coarse.observe(stats(1));
    fine.observe(stats(1));

    coarse.advance(33.4);
    fine.advance(16.7);
    fine.advance(16.7);

    expect(fine.values.luminance).toBeCloseTo(coarse.values.luminance, 12);
  });
});

describe("the adaptive tint", () => {
  /*
   * The mechanism is tested against a profile with two DISTINCT ends, not against
   * the shipped default.
   *
   * C9a measured that the reference material does not invert its tint against the
   * backdrop — it keys on the colour scheme instead — so the calibrated default
   * sets both ends to the same colour and the crossover is deliberately inert.
   * Asserting a monotone run across the band on the default would therefore be
   * asserting that vitrea still does the thing the fixtures say it should not,
   * and the test would be pinning the miscalibration rather than the code.
   *
   * The interpolation itself is still real, still reachable by any profile that
   * wants it, and still has to be right — hence an explicit profile here, and a
   * separate check below that the default is the inert one on purpose.
   */
  const CROSSFADING: MaterialProfile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
    adaptiveTintDark: [1, 1, 1],
    adaptiveTintLight: [0.02, 0.02, 0.03],
  });

  it("runs from the dark-backdrop tint to the light-backdrop tint", () => {
    for (let channel = 0; channel < 3; channel += 1) {
      expect(adaptiveTint(0, CROSSFADING)[channel]).toBeCloseTo(
        CROSSFADING.adaptiveTintDark[channel] as number,
        12,
      );
      expect(adaptiveTint(1, CROSSFADING)[channel]).toBeCloseTo(
        CROSSFADING.adaptiveTintLight[channel] as number,
        12,
      );
    }
  });

  it("crosses over inside the declared band, monotonically", () => {
    const low = adaptiveTint(CROSSFADING.adaptiveLuminanceLow, CROSSFADING);
    const mid = adaptiveTint(
      (CROSSFADING.adaptiveLuminanceLow + CROSSFADING.adaptiveLuminanceHigh) / 2,
      CROSSFADING,
    );
    const high = adaptiveTint(CROSSFADING.adaptiveLuminanceHigh, CROSSFADING);

    expect(low[0]).toBeGreaterThan(mid[0]);
    expect(mid[0]).toBeGreaterThan(high[0]);
  });

  it("is continuous, so the tint cannot snap at a threshold", () => {
    // The material's tint is continuous and can just follow the smoothed
    // luminance; the DOM foreground is the discrete one, and motion owns that.
    const epsilon = 1e-6;
    const before = adaptiveTint(CROSSFADING.adaptiveLuminanceLow - epsilon, CROSSFADING);
    const after = adaptiveTint(CROSSFADING.adaptiveLuminanceLow + epsilon, CROSSFADING);
    expect(Math.abs(after[0] - before[0])).toBeLessThan(1e-5);
  });

  it("is inert under the shipped default, which is the calibrated behaviour", () => {
    expect(ADAPTIVE_TINT_DARK).toEqual(ADAPTIVE_TINT_LIGHT);
    // Constant across and beyond the band: no backdrop can move the default tint.
    const samples = [0, ADAPTIVE_LUMINANCE_LOW, ADAPTIVE_LUMINANCE_HIGH, 1].map((luminance) =>
      adaptiveTint(luminance),
    );
    for (const sample of samples) expect(sample).toEqual(ADAPTIVE_TINT_DARK);
  });
});

describe("readback cadence", () => {
  it("fires immediately when nothing has been read yet", () => {
    expect(readbackDue(undefined, 0, 15)).toBe(true);
  });

  it("holds off until the period has elapsed", () => {
    expect(readbackDue(0, 30, 15)).toBe(false);
    expect(readbackDue(0, 66.7, 15)).toBe(true);
  });

  it("never fires when the governor turned adaptation off", () => {
    expect(readbackDue(undefined, 1000, 0)).toBe(false);
    expect(readbackDue(0, 1e9, 0)).toBe(false);
  });

  it("respects a cadence the governor lowered", () => {
    expect(readbackDue(0, 200, 4)).toBe(false);
    expect(readbackDue(0, 260, 4)).toBe(true);
  });
});
