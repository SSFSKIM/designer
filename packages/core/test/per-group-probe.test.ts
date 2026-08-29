/**
 * The per-group platform probe (Decision Log #21(a) → #23(c)).
 *
 * `PlatformProbe` is mostly scene-wide and rightly so — one device per root,
 * one engine, one `backdrop-filter` answer. `backdropProxyConformance` is the
 * exception S1 measured: the backdrop-root audit is per group, "not per
 * document, because different groups can sit under different ancestors", so a
 * group whose proxy chain has been re-rooted must demote alone.
 *
 * Until this setter existed the browser layer could not say that through the
 * scene, and worked around it by bypassing `resolve()` and calling core's pure
 * resolver itself with the verdict folded in — which meant the scene and the
 * host could give two different answers about one group. These tests pin the
 * shape that retired the bypass, and the last one pins the property that made
 * the bypass necessary in the first place: one failing group does not touch its
 * neighbour.
 */

import { describe, expect, it } from "vitest";

import type { PlatformProbe } from "../src/capability";
import { createGlassScene, GlassSceneError } from "../src/scene";

const HEALTHY: PlatformProbe = {
  webgpu: "not-requested",
  backdropFilter: true,
  backdropProxyConformance: "pass",
  deviceHealth: "ok",
};

const REROOTED: PlatformProbe = { ...HEALTHY, backdropProxyConformance: "fail" };

function scene() {
  const instance = createGlassScene({ devMode: false, platform: HEALTHY });
  instance.registerBackdropSource({ id: "dom", kind: "dom" });
  instance.setPlatformProbe(HEALTHY);
  return instance;
}

const stateOf = (instance: ReturnType<typeof scene>, groupId: string) =>
  instance.resolve().groups.find((group) => group.groupId === groupId)?.state;

describe("setPlatformProbe(probe, groupId)", () => {
  it("resolves a group against its own probe, and leaves its neighbour alone", () => {
    const instance = scene();
    instance.registerGlassGroup({ id: "rerooted", backdropSourceId: "dom" });
    instance.registerGlassGroup({ id: "healthy", backdropSourceId: "dom" });

    instance.setPlatformProbe(REROOTED, "rerooted");

    expect(stateOf(instance, "rerooted")).toMatchObject({
      health: "demoted",
      demotionReason: "probe-failed",
    });
    expect(stateOf(instance, "healthy")).toMatchObject({ health: "ok" });
  });

  it("falls back to the scene-wide probe for a group that has none", () => {
    const instance = scene();
    instance.registerGlassGroup({ id: "g1", backdropSourceId: "dom" });

    const before = stateOf(instance, "g1");
    instance.setPlatformProbe(REROOTED);

    expect(before).toMatchObject({ health: "ok" });
    expect(stateOf(instance, "g1")).toMatchObject({ demotionReason: "probe-failed" });
  });

  /*
   * Replace, not merge — the same rule `setGovernorPressure` follows. A merge
   * would be a second precedence rule sitting beside `REASON_PRECEDENCE`, and
   * the caller that knows a group's verdict is the same caller that holds the
   * scene-wide probe it was derived from, so composing belongs there.
   */
  it("replaces rather than merges: the group's probe wins whole", () => {
    const instance = scene();
    instance.registerGlassGroup({ id: "g1", backdropSourceId: "dom" });

    instance.setPlatformProbe({ ...HEALTHY, backdropFilter: false }, "g1");
    expect(stateOf(instance, "g1")).toMatchObject({
      samplingBackend: "none",
      demotionReason: "no-backdrop-filter",
    });

    // The scene-wide probe still says the engine has `backdrop-filter`; the
    // group's own answer is not widened back by it.
    instance.setPlatformProbe({ ...HEALTHY, deviceHealth: "lost" });
    expect(stateOf(instance, "g1")).toMatchObject({
      samplingBackend: "none",
      demotionReason: "no-backdrop-filter",
    });
  });

  it("keeps the scene-wide setter's meaning: no groupId, every group", () => {
    const instance = scene();
    instance.registerGlassGroup({ id: "a", backdropSourceId: "dom" });
    instance.registerGlassGroup({ id: "b", backdropSourceId: "dom" });

    instance.setPlatformProbe(REROOTED);

    expect(stateOf(instance, "a")).toMatchObject({ demotionReason: "probe-failed" });
    expect(stateOf(instance, "b")).toMatchObject({ demotionReason: "probe-failed" });
  });

  it("refuses a group it does not know, rather than recording an orphan", () => {
    const instance = scene();

    expect(() => instance.setPlatformProbe(REROOTED, "never-registered")).toThrow(GlassSceneError);
  });

  it("forgets the override with the group", () => {
    const instance = scene();
    instance.registerGlassGroup({ id: "g1", backdropSourceId: "dom" });
    instance.setPlatformProbe(REROOTED, "g1");
    instance.removeGlassGroup("g1");

    instance.registerGlassGroup({ id: "g1", backdropSourceId: "dom" });

    // A re-registered group is a new group: it starts on the scene-wide answer,
    // not on a verdict about a chain that no longer exists.
    expect(stateOf(instance, "g1")).toMatchObject({ health: "ok" });
  });
});
