import { describe, expect, it } from "vitest";

import { DEMOTION_REASONS, isHealthy, resolveGlassGroupState, type GlassGroupState } from "../src/index";

/**
 * Resolved rather than hand-written, so the shape test can never drift from the
 * transition table in `capability.test.ts`. This is acceptance #5's state.
 */
const noWebGpu: GlassGroupState = resolveGlassGroupState({
  configuredSource: "texture",
  platform: {
    webgpu: false,
    backdropFilter: true,
    backdropProxyConformance: "pass",
    deviceHealth: "ok",
  },
  source: { taint: "clean", textureCompatibility: "compatible" },
  governor: "none",
  hint: "none",
});

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
