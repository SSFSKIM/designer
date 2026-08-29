/**
 * The group's probe now lives in the scene (Decision Log #23(c)).
 *
 * What this replaces: `stateFor` used to fold the group's own proxy-audit
 * verdict into a copy of the scene-wide probe every time it was asked, while
 * `scene.resolve()` — which had no per-group probe to read — resolved the same
 * group against the scene-wide answer alone. Two answers about one group, and
 * which one a consumer saw depended on which door they came through.
 *
 * These pin the collapse: the root publishes one probe per group into the scene,
 * recomposes it whenever the scene-wide facts move, and reads it back rather
 * than folding again.
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { foldProbeVerdict } from "../src/group-state";
import { createGlassRoot, type GlassRoot } from "../src/root";
import type { MediaMatcher } from "../src/media-policy";
import type { PlatformProbe } from "@vitreajs/vitrea";

class StubResizeObserver {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

const matcher: MediaMatcher = () => ({
  matches: false,
  media: "(prefers-reduced-motion: reduce)",
  addEventListener: () => {},
  removeEventListener: () => {},
});

let roots: GlassRoot[] = [];
let containers: HTMLElement[] = [];

function root(): GlassRoot {
  const container = document.createElement("div");
  document.body.append(container);
  containers.push(container);
  const created = createGlassRoot({
    container,
    autoStart: false,
    matcher,
    diagnosticSink: () => {},
  });
  roots.push(created);
  return created;
}

beforeEach(() => {
  (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
});

afterEach(() => {
  for (const instance of roots) instance.destroy();
  for (const container of containers) container.remove();
  roots = [];
  containers = [];
});

/** A group with one host, audited once, so its probe has been published. */
function audited(instance: GlassRoot, groupId: string): void {
  instance.registerGroup({ id: groupId });
  const host = document.createElement("button");
  instance.plane("base").hostLayer.append(host);
  instance.registerHost({ host, groupId, plane: "base" });
  instance.runFrame(16);
  instance.revalidateProbe();
}

const probeOf = (instance: GlassRoot, groupId: string): PlatformProbe => {
  const published = instance.scene.glassGroup(groupId)?.platform;
  if (published === undefined) throw new Error(`no probe published for "${groupId}"`);
  return published;
};

describe("the group's probe reaches the scene", () => {
  it("publishes one per group when the audit runs", () => {
    const instance = root();
    audited(instance, "g1");

    expect(instance.scene.glassGroup("g1")?.platform).toBeDefined();
  });

  /*
   * The reason the override is *re-published* rather than merged in core. A
   * group's probe is a derivative of the scene-wide one, so a scene-wide change
   * — a device lost, WebGPU settling — has to rebuild every override. Writing a
   * stale one directly is how that failure would look from the outside, and
   * `revalidateProbe` recomposing it is the guard.
   */
  it("recomposes an override from the current scene-wide facts", () => {
    const instance = root();
    audited(instance, "g1");
    const settled = instance.capabilities("g1");

    // What a stale override would look like from the outside: an answer about a
    // device and an engine this page does not have.
    instance.scene.setPlatformProbe(
      {
        webgpu: "unavailable",
        backdropFilter: false,
        backdropProxyConformance: "fail",
        deviceHealth: "lost",
      },
      "g1",
    );
    expect(instance.capabilities("g1")).toMatchObject({ samplingBackend: "none" });

    instance.revalidateProbe();

    // Back to the truth about this page, not the fiction written over it.
    expect(instance.capabilities("g1")).toEqual(settled);
  });

  /*
   * `capabilities()` reads the scene rather than folding for itself. Written
   * from the scene side on purpose: if `stateFor` still did its own fold, a
   * probe placed here would be ignored and the assertion would not move.
   */
  it("answers capabilities() from the scene's per-group probe", () => {
    const instance = root();
    audited(instance, "g1");
    audited(instance, "g2");

    expect(instance.capabilities("g1")).toMatchObject({ health: "ok" });

    instance.scene.setPlatformProbe(foldProbeVerdict(probeOf(instance, "g1"), "fail"), "g1");

    expect(instance.capabilities("g1")).toMatchObject({
      health: "demoted",
      demotionReason: "probe-failed",
    });
    // One group, alone. This is the property the whole per-group probe exists
    // for, and the one a scene-wide-only probe could not express.
    expect(instance.capabilities("g2")).toMatchObject({ health: "ok" });
  });
});

describe("foldProbeVerdict", () => {
  const healthy: PlatformProbe = {
    webgpu: "not-requested",
    backdropFilter: true,
    backdropProxyConformance: "pass",
    deviceHealth: "ok",
  };

  it("narrows on a failing verdict and touches nothing else", () => {
    expect(foldProbeVerdict(healthy, "fail")).toEqual({
      ...healthy,
      backdropProxyConformance: "fail",
    });
  });

  it("leaves a passing verdict alone", () => {
    expect(foldProbeVerdict(healthy, "pass")).toEqual(healthy);
  });

  /*
   * A group's own chain being intact says nothing about a page-level audit that
   * failed, so `pass` must never raise the scene-wide answer back up. Otherwise
   * a per-group refinement would silently become a per-group override.
   */
  it("never widens: a passing group cannot undo a failing scene-wide probe", () => {
    const failing: PlatformProbe = { ...healthy, backdropProxyConformance: "fail" };

    expect(foldProbeVerdict(failing, "pass").backdropProxyConformance).toBe("fail");
  });
});
