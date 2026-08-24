import { describe, expect, it } from "vitest";

import { GLASS_ROOT_ACCESSIBILITY_DEFAULTS, SUPPORTED_PLANES } from "../src/index";

describe("@vitrea/react bindings surface", () => {
  it("defers every accessibility axis to the system by default", () => {
    expect(GLASS_ROOT_ACCESSIBILITY_DEFAULTS).toEqual({
      reducedMotion: "system",
      reducedTransparency: "system",
      increasedContrast: "system",
    });
  });

  it("exposes the platform's planes without the app installing platform-web", () => {
    expect(SUPPORTED_PLANES).toEqual(["base", "overlay"]);
  });
});
