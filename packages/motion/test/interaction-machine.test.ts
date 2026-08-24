import { describe, expect, it } from "vitest";

import {
  DEFAULT_MOTION_PROFILE,
  INTERACTION_STATES,
  STATE_DRIVEN_CHANNELS,
  createInteractionMachine,
  withProfileOverrides,
  type InteractionFlags,
} from "../src/index";

const NO_FLAGS: InteractionFlags = {
  disabled: false,
  morphing: false,
  pressed: false,
  hovered: false,
  focused: false,
};

describe("InteractionMachine — construction", () => {
  it("starts at rest holding a driver per state-driven channel", () => {
    const machine = createInteractionMachine();

    expect(machine.state).toBe("idle");
    expect([...machine.channels].sort()).toEqual([...STATE_DRIVEN_CHANNELS].sort());
    expect(machine.settled).toBe(true);

    for (const channel of STATE_DRIVEN_CHANNELS) {
      expect(machine.value(channel)).toBe(DEFAULT_MOTION_PROFILE.stateTargets.idle[channel]);
      expect(machine.driver(channel).target).toBe(
        DEFAULT_MOTION_PROFILE.stateTargets.idle[channel],
      );
    }
  });

  it("seeds from any starting state without animating into it", () => {
    const machine = createInteractionMachine({ initialState: "disabled" });

    expect(machine.state).toBe("disabled");
    expect(machine.value("disabled")).toBe(1);
    expect(machine.value("lensStrength")).toBe(DEFAULT_MOTION_PROFILE.stateTargets.disabled.lensStrength);
    expect(machine.settled).toBe(true);
  });

  it("carries the extra channels a morph needs when asked for them", () => {
    const machine = createInteractionMachine({
      channels: [...STATE_DRIVEN_CHANNELS, "position", "size", "radius"],
    });

    expect(machine.channels).toContain("position");
    // Not state-driven, so it starts wherever it was placed and stays.
    expect(machine.value("position")).toBe(0);
    machine.advance(100);
    expect(machine.value("position")).toBe(0);
  });

  it("refuses to report a channel it does not carry", () => {
    const machine = createInteractionMachine();
    expect(() => machine.driver("position")).toThrow(/position/);
  });
});

describe("InteractionMachine — transitions", () => {
  it("retargets every state-driven channel to the destination's vector", () => {
    const machine = createInteractionMachine();
    expect(machine.transition("pressed")).toBe(true);
    expect(machine.state).toBe("pressed");

    for (const channel of STATE_DRIVEN_CHANNELS) {
      expect(machine.driver(channel).target).toBe(
        DEFAULT_MOTION_PROFILE.stateTargets.pressed[channel],
      );
    }
  });

  it("rejects an illegal transition and changes nothing", () => {
    const machine = createInteractionMachine({ initialState: "disabled" });

    expect(machine.canTransition("hover")).toBe(false);
    expect(machine.transition("hover")).toBe(false);
    expect(machine.state).toBe("disabled");
    expect(machine.driver("disabled").target).toBe(1);
  });

  it("lands the same targets whichever way it arrives", () => {
    const viaIdle = createInteractionMachine();
    viaIdle.transition("hover");

    const viaPress = createInteractionMachine();
    viaPress.transition("pressed");
    viaPress.advance(40);
    viaPress.transition("hover");

    for (const channel of STATE_DRIVEN_CHANNELS) {
      expect(viaPress.driver(channel).target).toBe(viaIdle.driver(channel).target);
    }
  });

  it("accepts a self-transition without disturbing anything", () => {
    const machine = createInteractionMachine();
    machine.transition("pressed");
    machine.advance(40);
    const value = machine.value("pressCompression");
    const velocity = machine.driver("pressCompression").velocity;

    expect(machine.transition("pressed")).toBe(true);
    expect(machine.value("pressCompression")).toBe(value);
    expect(machine.driver("pressCompression").velocity).toBe(velocity);
  });

  it("takes morph geometry from the caller, since the state table cannot know it", () => {
    const machine = createInteractionMachine({
      channels: [...STATE_DRIVEN_CHANNELS, "position", "radius"],
    });
    machine.advance(16.7);

    expect(machine.transition("morphing", { position: 240, radius: 32 })).toBe(true);
    expect(machine.driver("position").target).toBe(240);
    expect(machine.driver("radius").target).toBe(32);
    // Overrides retarget; they never place the channel.
    expect(machine.value("position")).toBe(0);
    expect(machine.driver("position").velocity).toBe(0);
  });

  it("lets an override win over the state table", () => {
    const machine = createInteractionMachine();
    machine.transition("pressed", { glow: 0.4 });
    expect(machine.driver("glow").target).toBe(0.4);
    expect(machine.driver("pressCompression").target).toBe(1);
  });

  it("ignores an override for a channel it does not carry", () => {
    const machine = createInteractionMachine();
    expect(machine.transition("morphing", { position: 240 })).toBe(true);
    expect(machine.state).toBe("morphing");
  });
});

describe("InteractionMachine — applyFlags", () => {
  it("follows the resolved state", () => {
    const machine = createInteractionMachine();

    expect(machine.applyFlags({ ...NO_FLAGS, hovered: true })).toBe(true);
    expect(machine.state).toBe("hover");

    expect(machine.applyFlags({ ...NO_FLAGS, hovered: true, pressed: true })).toBe(true);
    expect(machine.state).toBe("pressed");
  });

  it("routes out of disabled through rest, so the host never sees a stuck state", () => {
    const machine = createInteractionMachine({ initialState: "disabled" });

    expect(machine.applyFlags({ ...NO_FLAGS, hovered: true })).toBe(true);
    expect(machine.state).toBe("hover");
    // Passing through idle only retargets; nothing advanced in between, so the
    // detour is invisible in the values.
    expect(machine.driver("glow").target).toBe(DEFAULT_MOTION_PROFILE.stateTargets.hover.glow);
  });

  it("routes out of a morph into a press through rest as well", () => {
    const machine = createInteractionMachine();
    machine.transition("morphing");
    expect(machine.applyFlags({ ...NO_FLAGS, pressed: true })).toBe(true);
    expect(machine.state).toBe("pressed");
  });
});

describe("InteractionMachine — the interruption case (§Motion, parent acceptance #3)", () => {
  it("keeps press, release and re-press continuous with velocity carried at each redirect", () => {
    const machine = createInteractionMachine();
    const press = machine.driver("pressCompression");
    const trace: number[] = [];
    const frame = () => {
      machine.advance(4);
      trace.push(press.value);
    };

    machine.transition("pressed");
    for (let i = 0; i < 10; i += 1) frame();
    expect(press.value).toBeGreaterThan(0);
    expect(press.velocity).toBeGreaterThan(0);

    // Release, mid-press-animation.
    const atRelease = { value: press.value, velocity: press.velocity };
    machine.transition("hover");
    expect(press.value).toBe(atRelease.value);
    expect(press.velocity).toBe(atRelease.velocity);
    expect(press.target).toBe(0);

    for (let i = 0; i < 6; i += 1) frame();

    // Immediate re-press, mid-release-animation.
    const atRepress = { value: press.value, velocity: press.velocity };
    expect(atRepress.value).toBeGreaterThan(0);
    expect(atRepress.velocity).toBeLessThan(0);

    machine.transition("pressed");
    expect(press.value).toBe(atRepress.value);
    expect(press.velocity).toBe(atRepress.velocity);
    expect(press.target).toBe(1);

    for (let i = 0; i < 40; i += 1) frame();

    // A restart would show up as a step back toward 0, which is both a jump far
    // larger than one frame of travel and a visit to 0 the channel never makes.
    let largestJump = 0;
    for (let i = 1; i < trace.length; i += 1) {
      largestJump = Math.max(largestJump, Math.abs((trace[i] ?? 0) - (trace[i - 1] ?? 0)));
    }
    expect(largestJump).toBeLessThan(0.1);
    expect(Math.min(...trace)).toBeGreaterThan(0);
  });

  it("attacks glow on the press and decays it on the release", () => {
    const machine = createInteractionMachine();
    const glow = machine.driver("glow");
    const config = DEFAULT_MOTION_PROFILE.channels.glow;
    if (config.kind !== "attack-decay") throw new Error("glow must be attack-decay");

    machine.transition("pressed");
    machine.advance(30);
    const rising = glow.velocity;
    expect(rising).toBeCloseTo(((glow.target - glow.value) * 1000) / config.attackMs, 12);

    machine.transition("hover");
    const falling = glow.velocity;
    expect(falling).toBeLessThan(0);
    expect(falling).toBeCloseTo(((glow.target - glow.value) * 1000) / config.decayMs, 12);

    // Same driver, same gap: the release is slower by the ratio of the two
    // constants, which is the asymmetry the table asks for.
    expect(Math.abs(rising / falling)).toBeGreaterThan(1);
  });

  it("survives a redirect on every frame without drifting or exploding", () => {
    const machine = createInteractionMachine();
    const press = machine.driver("pressCompression");

    for (let i = 0; i < 400; i += 1) {
      machine.transition(i % 2 === 0 ? "pressed" : "hover");
      machine.advance(8);
      expect(Number.isFinite(press.value)).toBe(true);
      expect(press.value).toBeGreaterThanOrEqual(-0.2);
      expect(press.value).toBeLessThanOrEqual(1.2);
    }
  });
});

describe("InteractionMachine — advancing time", () => {
  it("applies the capped-step rule and reports what it used", () => {
    const machine = createInteractionMachine();
    expect(machine.advance(16.7)).toBe(16.7);
    expect(machine.advance(200)).toBe(DEFAULT_MOTION_PROFILE.frame.maxDeltaMs);
    expect(machine.advance(-5)).toBe(0);
    expect(machine.advance(Number.NaN)).toBe(0);
  });

  it("advances every channel it carries by the same clamped delta", () => {
    const profile = withProfileOverrides(DEFAULT_MOTION_PROFILE, { frame: { maxDeltaMs: 20 } });
    const capped = createInteractionMachine({ profile });
    const stepped = createInteractionMachine({ profile });

    capped.transition("pressed");
    stepped.transition("pressed");
    capped.advance(500);
    stepped.advance(20);

    for (const channel of STATE_DRIVEN_CHANNELS) {
      expect(capped.value(channel)).toBe(stepped.value(channel));
    }
  });

  it("reports settled only once every channel it carries has arrived", () => {
    const machine = createInteractionMachine();
    machine.transition("pressed");
    expect(machine.settled).toBe(false);

    let elapsed = 0;
    while (!machine.settled && elapsed < 20_000) {
      machine.advance(8);
      elapsed += 8;
    }

    expect(machine.settled).toBe(true);
    expect(elapsed).toBeLessThan(20_000);
    for (const channel of STATE_DRIVEN_CHANNELS) {
      expect(machine.driver(channel).settled).toBe(true);
    }
  });

  it("reaches each state's targets from each state it can legally leave", () => {
    for (const from of INTERACTION_STATES) {
      for (const to of INTERACTION_STATES) {
        const machine = createInteractionMachine({ initialState: from });
        if (!machine.transition(to)) continue;
        for (let i = 0; i < 600; i += 1) machine.advance(8);
        for (const channel of STATE_DRIVEN_CHANNELS) {
          expect(machine.value(channel)).toBeCloseTo(
            DEFAULT_MOTION_PROFILE.stateTargets[to][channel] ?? 0,
            3,
          );
        }
      }
    }
  });
});
