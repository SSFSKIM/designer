import { describe, expect, it } from "vitest";

import {
  EASINGS,
  EASING_NAMES,
  EaseDriver,
  MOTION_DRIVER_KINDS,
  StepDriver,
  createDriver,
  type EasingName,
} from "../src/index";

describe("EaseDriver — monotonic, no overshoot (§Motion: opacity/materialization)", () => {
  it("runs from 0 to exactly the target over the configured duration", () => {
    const driver = new EaseDriver({ durationMs: 220, easing: "easeOutCubic" }, 0);
    driver.retarget(1);
    expect(driver.settled).toBe(false);

    driver.advance(220);

    expect(driver.value).toBe(1);
    expect(driver.settled).toBe(true);
    expect(driver.velocity).toBe(0);
  });

  it.each([...EASING_NAMES])("never overshoots or reverses (%s)", (easing) => {
    const driver = new EaseDriver({ durationMs: 300, easing }, 0.2);
    driver.retarget(0.9);

    let previous = driver.value;
    for (let i = 0; i < 60; i += 1) {
      driver.advance(8);
      expect(driver.value).toBeGreaterThanOrEqual(previous - 1e-15);
      expect(driver.value).toBeLessThanOrEqual(0.9 + 1e-15);
      previous = driver.value;
    }
    expect(driver.value).toBe(0.9);
  });

  it.each([...EASING_NAMES])("descends monotonically too (%s)", (easing) => {
    const driver = new EaseDriver({ durationMs: 300, easing }, 1);
    driver.retarget(0);

    let previous = driver.value;
    for (let i = 0; i < 60; i += 1) {
      driver.advance(8);
      expect(driver.value).toBeLessThanOrEqual(previous + 1e-15);
      expect(driver.value).toBeGreaterThanOrEqual(-1e-15);
      previous = driver.value;
    }
    expect(driver.value).toBe(0);
  });

  it("re-anchors on the current value when redirected mid-ramp", () => {
    const driver = new EaseDriver({ durationMs: 300, easing: "easeOutCubic" }, 0);
    driver.retarget(1);
    driver.advance(120);

    const value = driver.value;
    expect(value).toBeGreaterThan(0);
    expect(value).toBeLessThan(1);

    driver.retarget(0);
    expect(driver.value).toBe(value);

    // Redirecting restarts the ramp from here, so the return trip is a full
    // duration and stays monotone — no overshoot past 0 on the way.
    for (let i = 0; i < 40; i += 1) {
      driver.advance(8);
      expect(driver.value).toBeGreaterThanOrEqual(-1e-15);
    }
    expect(driver.value).toBe(0);
  });

  it("treats a repeated retarget to the same target as a no-op", () => {
    const driver = new EaseDriver({ durationMs: 300, easing: "linear" }, 0);
    driver.retarget(1);
    driver.advance(150);
    const value = driver.value;

    driver.retarget(1);
    driver.advance(150);

    expect(value).toBeCloseTo(0.5, 12);
    expect(driver.value).toBe(1);
  });
});

describe("easing curves", () => {
  it.each([...EASING_NAMES])("is normalised and non-decreasing (%s)", (name: EasingName) => {
    const easing = EASINGS[name];
    expect(easing.at(0)).toBe(0);
    expect(easing.at(1)).toBe(1);

    let previous = 0;
    for (let i = 0; i <= 1000; i += 1) {
      const p = i / 1000;
      const value = easing.at(p);
      expect(value).toBeGreaterThanOrEqual(previous - 1e-15);
      expect(easing.slope(p)).toBeGreaterThanOrEqual(0);
      previous = value;
    }
  });

  it.each([...EASING_NAMES])("declares a slope that matches its own curve (%s)", (name: EasingName) => {
    const easing = EASINGS[name];
    const h = 1e-6;
    for (const p of [0.05, 0.25, 0.4, 0.6, 0.75, 0.95]) {
      const numeric = (easing.at(p + h) - easing.at(p - h)) / (2 * h);
      expect(easing.slope(p)).toBeCloseTo(numeric, 5);
    }
  });
});

describe("StepDriver — instant (§Motion: disabled)", () => {
  it("takes the target immediately with no velocity", () => {
    const driver = new StepDriver({ hysteresis: 0, cooldownMs: 0 }, 0);
    driver.retarget(1);

    expect(driver.value).toBe(1);
    expect(driver.target).toBe(1);
    expect(driver.velocity).toBe(0);
    expect(driver.settled).toBe(true);
  });
});

describe("StepDriver — hysteresis + cooldown (§Motion: quality tier)", () => {
  const config = { hysteresis: 0.5, cooldownMs: 2000 };

  it("ignores changes smaller than the hysteresis band", () => {
    const driver = new StepDriver(config, 2);
    driver.retarget(2.4);
    expect(driver.value).toBe(2);

    driver.retarget(2.6);
    expect(driver.value).toBe(2.6);
  });

  it("refuses a second change until the cooldown has elapsed", () => {
    const driver = new StepDriver(config, 2);
    driver.retarget(1);
    expect(driver.value).toBe(1);

    driver.advance(1900);
    driver.retarget(2);
    expect(driver.value).toBe(1);

    driver.advance(150);
    driver.retarget(2);
    expect(driver.value).toBe(2);
  });

  it("measures the cooldown in elapsed time, not frames", () => {
    const slow = new StepDriver(config, 0);
    const fast = new StepDriver(config, 0);
    slow.retarget(1);
    fast.retarget(1);

    for (let i = 0; i < 60; i += 1) slow.advance(33.4);
    for (let i = 0; i < 240; i += 1) fast.advance(8.35);

    slow.retarget(2);
    fast.retarget(2);
    expect(slow.value).toBe(2);
    expect(fast.value).toBe(2);
  });

  it("allows the very first change without waiting out a cooldown", () => {
    const driver = new StepDriver(config, 0);
    driver.retarget(5);
    expect(driver.value).toBe(5);
  });
});

describe("createDriver", () => {
  it("builds every driver kind the channel table names", () => {
    for (const kind of MOTION_DRIVER_KINDS) {
      const driver = createDriver(configFor(kind), 0);
      expect(driver.value).toBe(0);
      driver.advance(16.7);
      expect(Number.isFinite(driver.value)).toBe(true);
      expect(Number.isFinite(driver.velocity)).toBe(true);
    }
  });
});

function configFor(kind: (typeof MOTION_DRIVER_KINDS)[number]) {
  switch (kind) {
    case "interruptible-spring":
    case "critically-damped":
      return {
        kind,
        responseMs: 300,
        dampingRatio: kind === "critically-damped" ? 1 : 0.8,
        restDistance: 1e-3,
        restVelocity: 1e-2,
      } as const;
    case "attack-decay":
      return { kind, attackMs: 60, decayMs: 300, restDistance: 1e-3 } as const;
    case "low-pass-hysteresis":
      return { kind, timeConstantMs: 300, hysteresis: 0.05, restDistance: 1e-3 } as const;
    case "threshold-crossfade":
      return { kind, threshold: 0.5, hysteresis: 0.1, crossfadeMs: 200 } as const;
    case "monotonic-ease":
      return { kind, durationMs: 200, easing: "easeOutCubic" } as const;
    case "step":
    case "hysteresis-cooldown":
      return { kind, hysteresis: 0, cooldownMs: 0 } as const;
  }
}
