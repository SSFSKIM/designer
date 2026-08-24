import { describe, expect, it } from "vitest";

import {
  DEFAULT_MOTION_PROFILE,
  DEFORMATION_CHANNELS,
  INTERACTION_STATES,
  MOTION_CHANNELS,
  MOTION_DRIVER_BY_CHANNEL,
  POSITIONAL_CHANNELS,
  STATE_DRIVEN_CHANNELS,
  createDriver,
  createInteractionMachine,
  withProfileOverrides,
  withReducedMotion,
  type MotionChannel,
  type MotionProfile,
} from "../src/index";

const REDUCED = withReducedMotion(DEFAULT_MOTION_PROFILE);

/** Peak value while a channel travels 0 → 1 under a given profile. */
function peakOf(profile: MotionProfile, channel: MotionChannel): number {
  const driver = createDriver(profile.channels[channel], 0);
  driver.retarget(1);
  let peak = driver.value;
  for (let i = 0; i < 500; i += 1) {
    driver.advance(8);
    peak = Math.max(peak, driver.value);
  }
  return peak;
}

describe("withReducedMotion — a driver-configuration transform (§Accessibility)", () => {
  it("leaves the binding driver table alone", () => {
    // Reduced Motion changes constants, never which family drives a channel.
    // The table is binding; the numbers are not.
    for (const channel of MOTION_CHANNELS) {
      expect(REDUCED.channels[channel].kind).toBe(MOTION_DRIVER_BY_CHANNEL[channel]);
    }
  });

  it("damps every spring to at least critical", () => {
    for (const channel of MOTION_CHANNELS) {
      const config = REDUCED.channels[channel];
      if (config.kind !== "interruptible-spring" && config.kind !== "critically-damped") continue;
      expect(config.dampingRatio).toBeGreaterThanOrEqual(
        DEFAULT_MOTION_PROFILE.reducedMotion.minDampingRatio,
      );
    }
  });

  it("removes overshoot from channels that had it, and only from those", () => {
    // Vacuity guard: the base profile must actually overshoot somewhere, or
    // "removes overshoot" asserts nothing.
    expect(peakOf(DEFAULT_MOTION_PROFILE, "pressCompression")).toBeGreaterThan(1);

    for (const channel of MOTION_CHANNELS) {
      expect(peakOf(REDUCED, channel)).toBeLessThanOrEqual(1 + 1e-12);
    }
  });

  it("zeroes the deformation channels in every state", () => {
    expect(DEFORMATION_CHANNELS.length).toBeGreaterThan(0);
    for (const state of INTERACTION_STATES) {
      for (const channel of DEFORMATION_CHANNELS) {
        expect(REDUCED.stateTargets[state][channel]).toBe(0);
      }
    }
    // And the base profile does deform, so the assertion above has content.
    expect(DEFAULT_MOTION_PROFILE.stateTargets.pressed.pressCompression).toBe(1);
  });

  it("keeps the optical channels responding, so a control still gives feedback", () => {
    for (const state of INTERACTION_STATES) {
      expect(REDUCED.stateTargets[state].glow).toBe(
        DEFAULT_MOTION_PROFILE.stateTargets[state].glow,
      );
      expect(REDUCED.stateTargets[state].lensStrength).toBe(
        DEFAULT_MOTION_PROFILE.stateTargets[state].lensStrength,
      );
    }
  });

  it("shortens the positional channels rather than stopping them", () => {
    const factor = DEFAULT_MOTION_PROFILE.reducedMotion.morphResponseFactor;
    expect(factor).toBeLessThan(1);

    for (const channel of POSITIONAL_CHANNELS) {
      const base = DEFAULT_MOTION_PROFILE.channels[channel];
      const reduced = REDUCED.channels[channel];
      if (base.kind !== "interruptible-spring") throw new Error("positional must be a spring");
      // Still a spring: continuity survives the policy, elasticity does not.
      expect(reduced.kind).toBe(base.kind);
      if (reduced.kind !== "interruptible-spring") throw new Error("kind must survive");
      expect(reduced.responseMs).toBeCloseTo(base.responseMs * factor, 12);
    }
  });

  it("does not shorten channels that are not positional", () => {
    const base = DEFAULT_MOTION_PROFILE.channels.lensStrength;
    const reduced = REDUCED.channels.lensStrength;
    if (base.kind !== "critically-damped" || reduced.kind !== "critically-damped") {
      throw new Error("lensStrength must be critically damped");
    }
    expect(reduced.responseMs).toBe(base.responseMs);
  });

  it("preserves positional continuity: a mid-flight redirect still carries velocity", () => {
    for (const channel of POSITIONAL_CHANNELS) {
      const driver = createDriver(REDUCED.channels[channel], 0);
      driver.retarget(100);
      driver.advance(60);

      const value = driver.value;
      const velocity = driver.velocity;
      expect(velocity).toBeGreaterThan(0);

      driver.retarget(0);
      expect(driver.value).toBe(value);
      expect(driver.velocity).toBe(velocity);
    }
  });

  it("says whether it has been applied, rather than leaving callers to guess", () => {
    expect(DEFAULT_MOTION_PROFILE.reducedMotionApplied).toBe(false);
    expect(REDUCED.reducedMotionApplied).toBe(true);
    expect(withProfileOverrides(REDUCED, { frame: { maxDeltaMs: 40 } }).reducedMotionApplied).toBe(
      true,
    );
  });

  it("is idempotent, so applying the policy twice cannot compound it", () => {
    // The damping floor is naturally idempotent; the response factor is not, so
    // a second pass would halve the morph again.
    expect(withReducedMotion(REDUCED)).toEqual(REDUCED);
  });

  it("leaves the profile it was given untouched", () => {
    const snapshot: unknown = JSON.parse(JSON.stringify(DEFAULT_MOTION_PROFILE));
    withReducedMotion(DEFAULT_MOTION_PROFILE);
    expect(DEFAULT_MOTION_PROFILE).toEqual(snapshot);
  });

  it("reads its two constants from the profile, so calibration can retune the policy", () => {
    const tuned = withReducedMotion(
      withProfileOverrides(DEFAULT_MOTION_PROFILE, {
        reducedMotion: { minDampingRatio: 1.6, morphResponseFactor: 0.5 },
      }),
    );

    const position = tuned.channels.position;
    if (position.kind !== "interruptible-spring") throw new Error("kind must survive");
    expect(position.dampingRatio).toBe(1.6);
    expect(position.responseMs).toBeCloseTo(
      (DEFAULT_MOTION_PROFILE.channels.position.kind === "interruptible-spring"
        ? DEFAULT_MOTION_PROFILE.channels.position.responseMs
        : 0) * 0.5,
      12,
    );
  });
});

describe("withReducedMotion — through the state machine", () => {
  it("presses without deforming, but still lights and lenses", () => {
    const machine = createInteractionMachine({ profile: REDUCED });
    machine.transition("pressed");
    for (let i = 0; i < 100; i += 1) machine.advance(8);

    expect(machine.value("pressCompression")).toBe(0);
    expect(machine.value("glow")).toBeGreaterThan(0.9);
    expect(machine.value("lensStrength")).toBeCloseTo(
      REDUCED.stateTargets.pressed.lensStrength ?? 0,
      6,
    );
  });

  it("never overshoots any state-driven channel across the whole state graph", () => {
    for (const from of INTERACTION_STATES) {
      for (const to of INTERACTION_STATES) {
        const machine = createInteractionMachine({ profile: REDUCED, initialState: from });
        const bounds = STATE_DRIVEN_CHANNELS.map((channel) => {
          const start = REDUCED.stateTargets[from][channel] ?? 0;
          const end = REDUCED.stateTargets[to][channel] ?? 0;
          return { channel, low: Math.min(start, end), high: Math.max(start, end) };
        });

        if (!machine.transition(to)) continue;

        for (let i = 0; i < 200; i += 1) {
          machine.advance(8);
          for (const { channel, low, high } of bounds) {
            expect(machine.value(channel)).toBeGreaterThanOrEqual(low - 1e-9);
            expect(machine.value(channel)).toBeLessThanOrEqual(high + 1e-9);
          }
        }
      }
    }
  });

  it("still redirects an interrupted press continuously", () => {
    const machine = createInteractionMachine({
      profile: REDUCED,
      channels: [...STATE_DRIVEN_CHANNELS, "position"],
    });
    const position = machine.driver("position");

    machine.transition("morphing", { position: 200 });
    for (let i = 0; i < 10; i += 1) machine.advance(4);

    const value = position.value;
    const velocity = position.velocity;
    expect(value).toBeGreaterThan(0);
    expect(velocity).toBeGreaterThan(0);

    machine.transition("idle", { position: 0 });
    expect(position.value).toBe(value);
    expect(position.velocity).toBe(velocity);
  });
});
