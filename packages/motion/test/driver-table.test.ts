import { describe, expect, it } from "vitest";

import {
  INTERACTION_STATES,
  MOTION_CHANNELS,
  MOTION_DRIVER_BY_CHANNEL,
  NON_OVERSHOOTING_CHANNELS,
} from "../src/index";

describe("motion driver table (§Motion)", () => {
  it("assigns exactly one driver to every channel", () => {
    expect(Object.keys(MOTION_DRIVER_BY_CHANNEL).sort()).toEqual([...MOTION_CHANNELS].sort());
  });

  it("drives direct-manipulation channels with the interruptible spring", () => {
    expect(MOTION_DRIVER_BY_CHANNEL.position).toBe("interruptible-spring");
    expect(MOTION_DRIVER_BY_CHANNEL.pressCompression).toBe("interruptible-spring");
  });

  it("keeps materialization and disabled free of overshoot", () => {
    expect(NON_OVERSHOOTING_CHANNELS).toEqual(["materialization", "disabled"]);
  });

  it("ships the six v1 interaction states", () => {
    expect(INTERACTION_STATES).toEqual([
      "idle",
      "hover",
      "pressed",
      "focused",
      "disabled",
      "morphing",
    ]);
  });
});
