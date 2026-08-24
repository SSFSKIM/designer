import type { PlatformProbe } from "@vitrea/core";
import { describe, expect, it } from "vitest";

import { effectiveGroupState, type GroupStateInputs } from "../src/group-state";

const platform: PlatformProbe = {
  webgpu: "available",
  backdropFilter: true,
  backdropProxyConformance: "pass",
  deviceHealth: "ok",
};

const domGroup: GroupStateInputs = {
  configuredSource: "dom",
  platform,
  governor: "none",
  hint: "none",
  probe: "pass",
};

describe("the per-group probe verdict (S1 impact item 7)", () => {
  it("leaves a passing group exactly where core resolved it", () => {
    const state = effectiveGroupState(domGroup);

    expect(state).toMatchObject({
      configuredSource: "dom",
      activeRenderer: "webgpu",
      samplingBackend: "css-backdrop",
      refraction: "approximate",
      health: "ok",
    });
  });

  it("demotes a failing group to the CSS tier, naming probe-failed", () => {
    const state = effectiveGroupState({ ...domGroup, probe: "fail" });

    expect(state).toMatchObject({
      activeRenderer: "css",
      demotionReason: "probe-failed",
      health: "demoted",
      refraction: "none",
    });
    // The proxy path that failed is not on the CSS tier's path: it applies
    // backdrop-filter in place and uses no proxies at all.
    expect(state.samplingBackend).toBe("css-backdrop");
  });

  it("keeps configuredSource through a demotion", () => {
    expect(effectiveGroupState({ ...domGroup, probe: "fail" }).configuredSource).toBe("dom");
  });

  it("is per group: one failing group does not touch its neighbour", () => {
    const failing = effectiveGroupState({ ...domGroup, probe: "fail" });
    const passing = effectiveGroupState(domGroup);

    expect(failing.health).toBe("demoted");
    expect(passing.health).toBe("ok");
  });

  it("recovers when the offending style is removed and the probe re-passes", () => {
    const demoted = effectiveGroupState({ ...domGroup, probe: "fail" });
    const recovered = effectiveGroupState({ ...domGroup, probe: "pass" });

    expect(demoted.demotionReason).toBe("probe-failed");
    expect(recovered.demotionReason).toBeUndefined();
  });

  it("does not raise probe-failed on a texture group — the proxy is not on its path", () => {
    const state = effectiveGroupState({
      configuredSource: "texture",
      platform,
      source: { taint: "clean", textureCompatibility: "compatible" },
      governor: "none",
      hint: "none",
      probe: "fail",
    });

    expect(state).toMatchObject({
      activeRenderer: "webgpu",
      samplingBackend: "gpu-texture",
      refraction: "true",
      health: "ok",
    });
  });

  it("lets a scene-wide platform fault outrank the group's own verdict", () => {
    const state = effectiveGroupState({
      ...domGroup,
      platform: { ...platform, webgpu: "unavailable" },
      probe: "fail",
    });

    // no-webgpu explains the larger loss and comes first in core's precedence.
    expect(state.demotionReason).toBe("no-webgpu");
  });

  it("a CSS-only root's group resolves healthy, not demoted (X2's K1 amendment)", () => {
    const state = effectiveGroupState({
      ...domGroup,
      platform: { ...platform, webgpu: "not-requested" },
    });

    expect(state).toMatchObject({
      activeRenderer: "css",
      samplingBackend: "css-backdrop",
      refraction: "none",
      health: "ok",
    });
    expect(state.demotionReason).toBeUndefined();
  });
});
