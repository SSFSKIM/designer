import { describe, expect, it } from "vitest";

import { DEMOTION_REASONS, isHealthy, type GlassGroupState } from "../src/index";

const noWebGpu: GlassGroupState = {
  configuredSource: "texture",
  activeRenderer: "css",
  samplingBackend: "css-backdrop",
  refraction: "approximate",
  analysis: "none",
  health: "demoted",
  demotionReason: "no-webgpu",
};

describe("GlassGroupState (X2)", () => {
  it("enumerates every demotion reason the spec names", () => {
    expect([...DEMOTION_REASONS]).toEqual([
      "no-webgpu",
      "no-backdrop-filter",
      "tainted-source",
      "incompatible-texture",
      "device-lost",
      "probe-failed",
      "governor",
    ]);
  });

  it("keeps configuredSource intact through a demotion", () => {
    expect(noWebGpu.configuredSource).toBe("texture");
    expect(noWebGpu.activeRenderer).toBe("css");
    expect(isHealthy(noWebGpu)).toBe(false);
  });

  it("calls a group healthy only when no reason is attached", () => {
    expect(
      isHealthy({
        configuredSource: "dom",
        activeRenderer: "webgpu",
        samplingBackend: "css-backdrop",
        refraction: "approximate",
        analysis: "hint",
        health: "ok",
      }),
    ).toBe(true);
  });
});
