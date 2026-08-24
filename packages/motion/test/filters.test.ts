import { describe, expect, it } from "vitest";

import {
  ExponentialDriver,
  LowPassHysteresisDriver,
  ThresholdCrossfadeDriver,
} from "../src/index";

describe("ExponentialDriver — asymmetric attack/decay (§Motion: glow)", () => {
  const config = { attackMs: 60, decayMs: 400, restDistance: 1e-4 };

  it("rises on the attack constant and falls on the decay constant", () => {
    const rising = new ExponentialDriver(config, 0);
    rising.retarget(1);
    rising.advance(config.attackMs);

    const falling = new ExponentialDriver(config, 1);
    falling.retarget(0);
    falling.advance(config.decayMs);

    // One time constant covers 1 - 1/e of the remaining distance, whichever
    // direction — the asymmetry is in how long that constant is, not the shape.
    const covered = 1 - 1 / Math.E;
    expect(rising.value).toBeCloseTo(covered, 12);
    expect(falling.value).toBeCloseTo(1 - covered, 12);
  });

  it("clears far more of the gap attacking than decaying in the same window", () => {
    const rising = new ExponentialDriver(config, 0);
    rising.retarget(1);
    rising.advance(100);

    const falling = new ExponentialDriver(config, 1);
    falling.retarget(0);
    falling.advance(100);

    const risingGap = 1 - rising.value;
    const fallingGap = falling.value;
    expect(risingGap).toBeLessThan(fallingGap / 3);
  });

  it("switches constant with direction, mid-flight, without moving the value", () => {
    const driver = new ExponentialDriver(config, 0);
    driver.retarget(1);
    driver.advance(30);

    const value = driver.value;
    const attackVelocity = driver.velocity;
    expect(attackVelocity).toBeCloseTo(((1 - value) * 1000) / config.attackMs, 12);

    driver.retarget(0);

    expect(driver.value).toBe(value);
    expect(driver.velocity).toBeCloseTo((-value * 1000) / config.decayMs, 12);
  });

  it("never overshoots its target", () => {
    const driver = new ExponentialDriver(config, 0);
    driver.retarget(1);
    for (let i = 0; i < 500; i += 1) {
      driver.advance(8);
      expect(driver.value).toBeLessThanOrEqual(1);
      expect(driver.value).toBeGreaterThanOrEqual(0);
    }
    expect(driver.settled).toBe(true);
  });
});

describe("LowPassHysteresisDriver — backdrop adaptation (§Motion, §Foreground)", () => {
  const config = { timeConstantMs: 300, hysteresis: 0.1, restDistance: 1e-4 };

  it("rejects input jitter inside the hysteresis band", () => {
    const driver = new LowPassHysteresisDriver(config, 0.5);
    expect(driver.settled).toBe(true);

    for (const jitter of [0.53, 0.47, 0.55, 0.45, 0.549]) {
      driver.retarget(jitter);
      driver.advance(16.7);
    }

    expect(driver.value).toBe(0.5);
    expect(driver.target).toBe(0.5);
    expect(driver.settled).toBe(true);
  });

  it("commits and low-passes toward an input that leaves the band", () => {
    const driver = new LowPassHysteresisDriver(config, 0.5);
    driver.retarget(0.9);

    expect(driver.target).toBe(0.9);
    expect(driver.settled).toBe(false);

    driver.advance(config.timeConstantMs);
    expect(driver.value).toBeCloseTo(0.5 + 0.4 * (1 - 1 / Math.E), 12);
    expect(driver.value).toBeLessThan(0.9);
  });

  it("re-arms the band around wherever it came to rest", () => {
    const driver = new LowPassHysteresisDriver(config, 0);
    driver.retarget(1);
    for (let i = 0; i < 400; i += 1) driver.advance(16.7);
    expect(driver.settled).toBe(true);
    expect(driver.value).toBeCloseTo(1, 6);

    driver.retarget(0.95);
    const held = driver.target;
    driver.advance(16.7);
    expect(held).toBe(1);
    expect(driver.value).toBeCloseTo(1, 6);
  });

  it("tracks a moving input continuously once committed", () => {
    const driver = new LowPassHysteresisDriver(config, 0);
    const seen: number[] = [];
    for (let i = 1; i <= 60; i += 1) {
      driver.retarget(i / 60);
      driver.advance(16.7);
      seen.push(driver.value);
    }

    for (let i = 1; i < seen.length; i += 1) {
      const previous = seen[i - 1] ?? 0;
      const current = seen[i] ?? 0;
      expect(current).toBeGreaterThanOrEqual(previous);
    }
    // Committed in band-sized steps, then smoothed: it follows the ramp but
    // always lags it, which is the whole point of the filter.
    expect(seen.at(-1)).toBeGreaterThan(0.5);
    expect(seen.at(-1)).toBeLessThan(1);
  });

  it("never overshoots the committed input", () => {
    const driver = new LowPassHysteresisDriver(config, 0);
    driver.retarget(1);
    for (let i = 0; i < 400; i += 1) {
      driver.advance(16.7);
      expect(driver.value).toBeLessThanOrEqual(1);
    }
  });
});

describe("ThresholdCrossfadeDriver — foreground light/dark (§Foreground adaptation)", () => {
  const config = { threshold: 0.5, hysteresis: 0.12, crossfadeMs: 200 };

  it("holds its phase across the dead band around the threshold", () => {
    const driver = new ThresholdCrossfadeDriver(config, 0);
    expect(driver.phase).toBe("low");

    for (const luminance of [0.5, 0.52, 0.55, 0.48, 0.559]) {
      driver.retarget(luminance);
      expect(driver.phase).toBe("low");
      expect(driver.target).toBe(0);
    }

    driver.retarget(0.57);
    expect(driver.phase).toBe("high");
    expect(driver.target).toBe(1);

    for (const luminance of [0.5, 0.46, 0.441]) {
      driver.retarget(luminance);
      expect(driver.phase).toBe("high");
    }

    driver.retarget(0.43);
    expect(driver.phase).toBe("low");
  });

  it("crossfades over the configured duration, then clamps", () => {
    const driver = new ThresholdCrossfadeDriver(config, 0);
    driver.retarget(1);

    driver.advance(config.crossfadeMs / 2);
    expect(driver.value).toBeCloseTo(0.5, 12);
    expect(driver.settled).toBe(false);

    driver.advance(config.crossfadeMs);
    expect(driver.value).toBe(1);
    expect(driver.settled).toBe(true);
    expect(driver.velocity).toBe(0);
  });

  it("reverses from the current mix when the phase flips mid-fade", () => {
    const driver = new ThresholdCrossfadeDriver(config, 0);
    driver.retarget(1);
    driver.advance(60);

    const mix = driver.value;
    expect(mix).toBeGreaterThan(0);
    expect(mix).toBeLessThan(1);

    driver.retarget(0);
    expect(driver.value).toBe(mix);
    expect(driver.target).toBe(0);

    driver.advance(30);
    expect(driver.value).toBeLessThan(mix);
    expect(driver.value).toBeGreaterThan(0);
  });

  it("keeps the mix inside [0, 1] under an adversarial input sequence", () => {
    const driver = new ThresholdCrossfadeDriver(config, 0);
    for (let i = 0; i < 300; i += 1) {
      driver.retarget(i % 7 === 0 ? 0.95 : 0.05);
      driver.advance(11);
      expect(driver.value).toBeGreaterThanOrEqual(0);
      expect(driver.value).toBeLessThanOrEqual(1);
    }
  });
});
