import { describe, expect, it } from "vitest";

import {
  DEFAULT_MOTION_PROFILE,
  INTERACTION_STATES,
  LEGAL_TRANSITIONS,
  canTransition,
  channelsMovedBy,
  resolveInteractionState,
  type InteractionFlags,
  type InteractionState,
} from "../src/index";

const NO_FLAGS: InteractionFlags = {
  disabled: false,
  morphing: false,
  pressed: false,
  hovered: false,
  focused: false,
};

/** The transitions the state graph refuses, and why (§Motion, v1 scope). */
const ILLEGAL: readonly (readonly [InteractionState, InteractionState])[] = [
  ["disabled", "hover"],
  ["disabled", "pressed"],
  ["disabled", "focused"],
  ["disabled", "morphing"],
  ["morphing", "pressed"],
];

describe("interaction state graph (§Motion)", () => {
  it("ships the six v1 states", () => {
    expect(INTERACTION_STATES).toEqual([
      "idle",
      "hover",
      "pressed",
      "focused",
      "disabled",
      "morphing",
    ]);
  });

  it("permits every pair except the five it names", () => {
    for (const from of INTERACTION_STATES) {
      for (const to of INTERACTION_STATES) {
        const illegal = ILLEGAL.some(([a, b]) => a === from && b === to);
        expect(canTransition(from, to)).toBe(!illegal);
      }
    }
  });

  it("always permits a state to itself", () => {
    for (const state of INTERACTION_STATES) {
      expect(canTransition(state, state)).toBe(true);
      expect(LEGAL_TRANSITIONS[state]).not.toContain(state);
    }
  });

  it("leaves disabled only through rest", () => {
    expect(LEGAL_TRANSITIONS.disabled).toEqual(["idle"]);
  });

  it("never lets a morph be pressed, but lets it be disabled or land at rest", () => {
    expect(LEGAL_TRANSITIONS.morphing).not.toContain("pressed");
    expect(LEGAL_TRANSITIONS.morphing).toContain("idle");
    expect(LEGAL_TRANSITIONS.morphing).toContain("disabled");
  });
});

describe("resolveInteractionState — collapsing overlapping host flags", () => {
  it("reads rest when nothing is set", () => {
    expect(resolveInteractionState(NO_FLAGS)).toBe("idle");
  });

  it("ranks disabled over everything, including a morph in flight", () => {
    expect(
      resolveInteractionState({
        disabled: true,
        morphing: true,
        pressed: true,
        hovered: true,
        focused: true,
      }),
    ).toBe("disabled");
  });

  it("ranks a morph over direct manipulation", () => {
    expect(resolveInteractionState({ ...NO_FLAGS, morphing: true, pressed: true })).toBe("morphing");
  });

  it("ranks a press over hover and focus", () => {
    expect(
      resolveInteractionState({ ...NO_FLAGS, pressed: true, hovered: true, focused: true }),
    ).toBe("pressed");
  });

  it("spends the material's one slot on hover rather than focus", () => {
    // Focus has its own affordance in the semantic host DOM (§rendering
    // contract), so the material shows the more immediate pointer feedback.
    expect(resolveInteractionState({ ...NO_FLAGS, hovered: true, focused: true })).toBe("hover");
    expect(resolveInteractionState({ ...NO_FLAGS, focused: true })).toBe("focused");
  });
});

describe("channelsMovedBy — the per-transition view of the state table", () => {
  const table = DEFAULT_MOTION_PROFILE.stateTargets;

  it("moves nothing on a transition to the same state", () => {
    for (const state of INTERACTION_STATES) {
      expect(channelsMovedBy(table, state, state)).toEqual([]);
    }
  });

  it("compresses and glows on a press, and releases both", () => {
    const down = channelsMovedBy(table, "hover", "pressed");
    expect(down).toContain("pressCompression");
    expect(down).toContain("glow");
    expect(down).toContain("lensStrength");

    const up = channelsMovedBy(table, "pressed", "hover");
    expect(up).toEqual(down);
  });

  it("does not compress on a hover", () => {
    expect(channelsMovedBy(table, "idle", "hover")).not.toContain("pressCompression");
  });

  it("moves the disabled channel on the way in and out", () => {
    expect(channelsMovedBy(table, "idle", "disabled")).toContain("disabled");
    expect(channelsMovedBy(table, "disabled", "idle")).toContain("disabled");
  });

  it("never fades a surface on an interaction change", () => {
    // materialization is mount/unmount, not interaction: no state change may
    // touch it, or every hover would re-run the appear animation.
    for (const from of INTERACTION_STATES) {
      for (const to of INTERACTION_STATES) {
        expect(channelsMovedBy(table, from, to)).not.toContain("materialization");
      }
    }
  });

  it("is symmetric in which channels move", () => {
    for (const from of INTERACTION_STATES) {
      for (const to of INTERACTION_STATES) {
        expect([...channelsMovedBy(table, from, to)].sort()).toEqual(
          [...channelsMovedBy(table, to, from)].sort(),
        );
      }
    }
  });
});
