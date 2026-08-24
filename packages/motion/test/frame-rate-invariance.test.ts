import { describe, expect, it } from "vitest";

import {
  DEFAULT_MOTION_PROFILE,
  MOTION_CHANNELS,
  clampFrameDelta,
  createDriver,
  type DriverConfig,
  type MotionDriver,
} from "../src/index";

/**
 * The three schedules the acceptance names: one 33.4 ms step, two 16.7 ms
 * steps, four 8.35 ms steps. Same elapsed time, three cadences — 30 Hz, 60 Hz
 * and 120 Hz. A closed-form driver must land on the same state.
 */
const WINDOW_MS = 33.4;
const SCHEDULES = [
  { label: "30 Hz", step: 33.4, per: 1 },
  { label: "60 Hz", step: 16.7, per: 2 },
  { label: "120 Hz", step: 8.35, per: 4 },
] as const;

/**
 * Tolerance is float-arithmetic slack, not integrator slack.
 *
 * Measured across every case below — one, nine and thirty windows, plus the
 * dropped-frame comparison — the worst disagreement is 1.8e-15 in value and
 * 3.6e-15 in velocity, a few ULPs of double precision. The assertion sits three
 * orders above that, as headroom for engines whose `Math.exp` and `Math.sin`
 * round differently, and still twelve orders below anything a channel expresses.
 */
const TOLERANCE = 1e-12;

/**
 * Continuous drivers, each configured with a characteristic time far longer
 * than the horizon so every sample lands mid-flight — a driver that has already
 * clamped or settled would pass invariance trivially.
 */
const CONTINUOUS: readonly { readonly label: string; readonly config: DriverConfig }[] = [
  {
    label: "interruptible-spring (underdamped)",
    config: {
      kind: "interruptible-spring",
      responseMs: 1200,
      dampingRatio: 0.55,
      restDistance: 0,
      restVelocity: 0,
    },
  },
  {
    label: "interruptible-spring (critical)",
    config: {
      kind: "interruptible-spring",
      responseMs: 900,
      dampingRatio: 1,
      restDistance: 0,
      restVelocity: 0,
    },
  },
  {
    label: "interruptible-spring (overdamped)",
    config: {
      kind: "interruptible-spring",
      responseMs: 900,
      dampingRatio: 2.5,
      restDistance: 0,
      restVelocity: 0,
    },
  },
  {
    label: "critically-damped",
    config: {
      kind: "critically-damped",
      responseMs: 900,
      dampingRatio: 1,
      restDistance: 0,
      restVelocity: 0,
    },
  },
  {
    label: "attack-decay",
    config: { kind: "attack-decay", attackMs: 400, decayMs: 900, restDistance: 0 },
  },
  {
    label: "low-pass-hysteresis",
    config: {
      kind: "low-pass-hysteresis",
      timeConstantMs: 700,
      hysteresis: 0.04,
      restDistance: 0,
    },
  },
  {
    label: "threshold-crossfade",
    config: { kind: "threshold-crossfade", threshold: 0.5, hysteresis: 0.08, crossfadeMs: 700 },
  },
  {
    label: "monotonic-ease",
    config: { kind: "monotonic-ease", durationMs: 700, easing: "easeOutCubic" },
  },
];

function drive(config: DriverConfig, input: number, step: number, count: number): MotionDriver {
  const driver = createDriver(config, 0);
  driver.retarget(input);
  for (let i = 0; i < count; i += 1) driver.advance(step);
  return driver;
}

describe("frame-rate invariance (§Motion: closed-form integration)", () => {
  describe.each(CONTINUOUS)("$label", ({ config }) => {
    it("lands on the same state over one 33.4 ms window at 30/60/120 Hz", () => {
      const samples = SCHEDULES.map(({ step, per }) => drive(config, 0.9, step, per));
      const [reference] = samples;
      expect(reference).toBeDefined();
      if (reference === undefined) return;

      for (const sample of samples) {
        expect(Math.abs(sample.value - reference.value)).toBeLessThan(TOLERANCE);
        expect(Math.abs(sample.velocity - reference.velocity)).toBeLessThan(TOLERANCE);
      }
      // The window must actually be mid-flight, or the assertion is vacuous.
      expect(reference.value).toBeGreaterThan(0);
      expect(reference.settled).toBe(false);
    });

    it("stays in agreement over nine windows (300.6 ms)", () => {
      const windows = 9;
      const samples = SCHEDULES.map(({ step, per }) => drive(config, 0.9, step, per * windows));
      const [reference] = samples;
      expect(reference).toBeDefined();
      if (reference === undefined) return;

      for (const sample of samples) {
        expect(Math.abs(sample.value - reference.value)).toBeLessThan(TOLERANCE);
        expect(Math.abs(sample.velocity - reference.velocity)).toBeLessThan(TOLERANCE);
      }
      expect(reference.settled).toBe(false);
    });

    it("resolves a dropped frame identically to the frames it replaced", () => {
      const dropped = drive(config, 0.9, 200, 1);
      const stepped = createDriver(config, 0);
      stepped.retarget(0.9);
      // 200 ms as twelve 16.666… ms frames.
      for (let i = 0; i < 12; i += 1) stepped.advance(200 / 12);

      expect(Number.isFinite(dropped.value)).toBe(true);
      expect(Math.abs(dropped.value - stepped.value)).toBeLessThan(TOLERANCE);
      expect(Math.abs(dropped.velocity - stepped.velocity)).toBeLessThan(TOLERANCE);
    });

    it("keeps a 200 ms step inside the envelope it started in", () => {
      const driver = drive(config, 0.9, 200, 1);
      expect(driver.value).toBeGreaterThanOrEqual(-1e-12);
      expect(driver.value).toBeLessThanOrEqual(0.9 + 1e-12);
      expect(Number.isFinite(driver.velocity)).toBe(true);
    });
  });

  it("holds for every channel's shipped configuration", () => {
    for (const channel of MOTION_CHANNELS) {
      const config = DEFAULT_MOTION_PROFILE.channels[channel];
      if (config.kind === "step" || config.kind === "hysteresis-cooldown") continue;

      const samples = SCHEDULES.map(({ step, per }) => drive(config, 0.9, step, per));
      const [reference] = samples;
      expect(reference).toBeDefined();
      if (reference === undefined) continue;

      for (const sample of samples) {
        expect(Math.abs(sample.value - reference.value)).toBeLessThan(TOLERANCE);
        expect(Math.abs(sample.velocity - reference.velocity)).toBeLessThan(TOLERANCE);
      }
    }
  });

  it("splits the window evenly, so the schedules really are comparable", () => {
    for (const { step, per } of SCHEDULES) {
      expect(step * per).toBeCloseTo(WINDOW_MS, 12);
    }
  });
});

describe("capped-step rule (§Motion: dropped frames)", () => {
  it("caps a stall at the frame policy's ceiling", () => {
    const { maxDeltaMs } = DEFAULT_MOTION_PROFILE.frame;
    expect(clampFrameDelta(200, DEFAULT_MOTION_PROFILE.frame)).toBe(maxDeltaMs);
    expect(clampFrameDelta(1e9, DEFAULT_MOTION_PROFILE.frame)).toBe(maxDeltaMs);
  });

  it("passes ordinary frame deltas through untouched", () => {
    expect(clampFrameDelta(16.7, DEFAULT_MOTION_PROFILE.frame)).toBe(16.7);
    expect(clampFrameDelta(8.35, DEFAULT_MOTION_PROFILE.frame)).toBe(8.35);
  });

  it("normalises deltas that a clock cannot legitimately produce", () => {
    expect(clampFrameDelta(0, DEFAULT_MOTION_PROFILE.frame)).toBe(0);
    expect(clampFrameDelta(-16.7, DEFAULT_MOTION_PROFILE.frame)).toBe(0);
    expect(clampFrameDelta(Number.NaN, DEFAULT_MOTION_PROFILE.frame)).toBe(0);
  });

  it("sits in the band that neither clips jitter nor completes an animation", () => {
    // Above two dropped 60 Hz frames, so ordinary jitter passes through; below
    // the slowest channel's time constant, so a returning tab resumes an
    // animation mid-flight rather than finding it already over.
    const { maxDeltaMs } = DEFAULT_MOTION_PROFILE.frame;
    expect(maxDeltaMs).toBeGreaterThan(2 * 16.7);

    const glow = DEFAULT_MOTION_PROFILE.channels.glow;
    if (glow.kind !== "attack-decay") throw new Error("glow must be attack-decay");
    expect(maxDeltaMs).toBeLessThan(glow.decayMs);
  });
});
