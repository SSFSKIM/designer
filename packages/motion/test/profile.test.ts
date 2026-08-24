import { describe, expect, it } from "vitest";

import {
  DEFAULT_MOTION_PROFILE,
  INTERACTION_STATES,
  MOTION_CHANNELS,
  MOTION_DRIVER_BY_CHANNEL,
  NON_OVERSHOOTING_CHANNELS,
  STATE_DRIVEN_CHANNELS,
  withProfileOverrides,
} from "../src/index";

describe("DEFAULT_MOTION_PROFILE — agreement with the binding table", () => {
  it("configures every channel with the driver the table names", () => {
    for (const channel of MOTION_CHANNELS) {
      expect(DEFAULT_MOTION_PROFILE.channels[channel].kind).toBe(
        MOTION_DRIVER_BY_CHANNEL[channel],
      );
    }
  });

  it("damps the critically-damped channels at or above critical", () => {
    for (const channel of MOTION_CHANNELS) {
      const config = DEFAULT_MOTION_PROFILE.channels[channel];
      if (config.kind !== "critically-damped") continue;
      expect(config.dampingRatio).toBeGreaterThanOrEqual(1);
    }
  });

  it("gives the interruptible springs a real response time", () => {
    for (const channel of MOTION_CHANNELS) {
      const config = DEFAULT_MOTION_PROFILE.channels[channel];
      if (config.kind !== "interruptible-spring") continue;
      expect(config.responseMs).toBeGreaterThan(0);
      expect(config.dampingRatio).toBeGreaterThan(0);
    }
  });

  it("leaves the non-overshooting channels on families that cannot overshoot", () => {
    for (const channel of NON_OVERSHOOTING_CHANNELS) {
      expect(["monotonic-ease", "step"]).toContain(DEFAULT_MOTION_PROFILE.channels[channel].kind);
    }
  });

  it("attacks glow faster than it decays", () => {
    const glow = DEFAULT_MOTION_PROFILE.channels.glow;
    if (glow.kind !== "attack-decay") throw new Error("glow must be attack-decay");
    expect(glow.attackMs).toBeLessThan(glow.decayMs);
  });

  it("gives the quality tier a long dwell, per §Performance's governor", () => {
    const tier = DEFAULT_MOTION_PROFILE.channels.qualityTier;
    if (tier.kind !== "hysteresis-cooldown") throw new Error("qualityTier must be hysteresis-cooldown");
    expect(tier.cooldownMs).toBeGreaterThan(1000);
    expect(tier.hysteresis).toBeGreaterThan(0);
  });

  it("records press compression as the 1–2% of parent acceptance #3", () => {
    expect(DEFAULT_MOTION_PROFILE.pressCompressionScale).toBeGreaterThanOrEqual(0.01);
    expect(DEFAULT_MOTION_PROFILE.pressCompressionScale).toBeLessThanOrEqual(0.02);
  });
});

describe("DEFAULT_MOTION_PROFILE — the state target table", () => {
  it("gives every state a target for every state-driven channel", () => {
    for (const state of INTERACTION_STATES) {
      const targets = DEFAULT_MOTION_PROFILE.stateTargets[state];
      expect(Object.keys(targets).sort()).toEqual([...STATE_DRIVEN_CHANNELS].sort());
    }
  });

  it("names no channel interaction state does not decide", () => {
    for (const state of INTERACTION_STATES) {
      for (const channel of Object.keys(DEFAULT_MOTION_PROFILE.stateTargets[state])) {
        expect(STATE_DRIVEN_CHANNELS).toContain(channel);
      }
    }
  });

  it("compresses only under a press", () => {
    for (const state of INTERACTION_STATES) {
      const expected = state === "pressed" ? 1 : 0;
      expect(DEFAULT_MOTION_PROFILE.stateTargets[state].pressCompression).toBe(expected);
    }
  });

  it("glows brightest under a press and not at all at rest or disabled", () => {
    const glow = (state: (typeof INTERACTION_STATES)[number]) =>
      DEFAULT_MOTION_PROFILE.stateTargets[state].glow ?? 0;

    expect(glow("pressed")).toBe(1);
    expect(glow("idle")).toBe(0);
    expect(glow("disabled")).toBe(0);
    expect(glow("hover")).toBeGreaterThan(glow("focused"));
    expect(glow("hover")).toBeLessThan(glow("pressed"));
  });

  it("marks the disabled channel in exactly one state", () => {
    for (const state of INTERACTION_STATES) {
      expect(DEFAULT_MOTION_PROFILE.stateTargets[state].disabled).toBe(
        state === "disabled" ? 1 : 0,
      );
    }
  });
});

describe("withProfileOverrides — every constant is replaceable", () => {
  it("replaces one constant and leaves its siblings alone", () => {
    const patched = withProfileOverrides(DEFAULT_MOTION_PROFILE, {
      channels: { pressCompression: { responseMs: 111 } },
    });

    const config = patched.channels.pressCompression;
    if (config.kind !== "interruptible-spring") throw new Error("kind must survive a field patch");
    expect(config.responseMs).toBe(111);

    const base = DEFAULT_MOTION_PROFILE.channels.pressCompression;
    if (base.kind !== "interruptible-spring") throw new Error("unexpected base kind");
    expect(config.dampingRatio).toBe(base.dampingRatio);
  });

  it("replaces a driver configuration outright when the kind changes", () => {
    const patched = withProfileOverrides(DEFAULT_MOTION_PROFILE, {
      channels: {
        pressCompression: { kind: "monotonic-ease", durationMs: 90, easing: "easeOutQuad" },
      },
    });

    const config = patched.channels.pressCompression;
    expect(config.kind).toBe("monotonic-ease");
    // Nothing of the spring survives — half a spring merged onto an ease would
    // type-check and mean nothing.
    expect(Object.keys(config).sort()).toEqual(["durationMs", "easing", "kind"]);
  });

  it("overrides frame policy, reduced-motion tunables and the press scale", () => {
    const patched = withProfileOverrides(DEFAULT_MOTION_PROFILE, {
      frame: { maxDeltaMs: 32 },
      reducedMotion: { morphResponseFactor: 0.4 },
      pressCompressionScale: 0.022,
    });

    expect(patched.frame.maxDeltaMs).toBe(32);
    expect(patched.reducedMotion.morphResponseFactor).toBe(0.4);
    expect(patched.reducedMotion.minDampingRatio).toBe(
      DEFAULT_MOTION_PROFILE.reducedMotion.minDampingRatio,
    );
    expect(patched.pressCompressionScale).toBe(0.022);
  });

  it("overrides one state's targets without disturbing the others", () => {
    const patched = withProfileOverrides(DEFAULT_MOTION_PROFILE, {
      stateTargets: { hover: { glow: 0.9 } },
    });

    expect(patched.stateTargets.hover.glow).toBe(0.9);
    expect(patched.stateTargets.hover.lensStrength).toBe(
      DEFAULT_MOTION_PROFILE.stateTargets.hover.lensStrength,
    );
    expect(patched.stateTargets.pressed).toEqual(DEFAULT_MOTION_PROFILE.stateTargets.pressed);
  });

  it("leaves the default profile untouched, so a patch cannot leak", () => {
    const snapshot: unknown = JSON.parse(JSON.stringify(DEFAULT_MOTION_PROFILE));
    withProfileOverrides(DEFAULT_MOTION_PROFILE, {
      frame: { maxDeltaMs: 1 },
      channels: { glow: { attackMs: 1 } },
      stateTargets: { idle: { glow: 1 } },
    });
    expect(DEFAULT_MOTION_PROFILE).toEqual(snapshot);
  });

  it("composes, so a calibration profile can land on top of an app's own", () => {
    const once = withProfileOverrides(DEFAULT_MOTION_PROFILE, {
      channels: { glow: { attackMs: 40 } },
    });
    const twice = withProfileOverrides(once, { channels: { glow: { decayMs: 900 } } });

    const config = twice.channels.glow;
    if (config.kind !== "attack-decay") throw new Error("kind must survive composition");
    expect(config.attackMs).toBe(40);
    expect(config.decayMs).toBe(900);
  });

  it("covers every channel, so nothing falls out of the patched profile", () => {
    const patched = withProfileOverrides(DEFAULT_MOTION_PROFILE, {});
    expect(Object.keys(patched.channels).sort()).toEqual([...MOTION_CHANNELS].sort());
    expect(patched).toEqual(DEFAULT_MOTION_PROFILE);
  });
});
