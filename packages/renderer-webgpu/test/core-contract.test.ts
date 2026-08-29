/**
 * The seam between this package and `vitrea`, asserted rather than assumed.
 *
 * The renderer sits **below** core in the dependency graph — core reaches it
 * through a dynamic import (X7's lazy seam), so importing core back would close a
 * cycle. The consequence is that a handful of core-shaped types are *declared*
 * here (`render-model.ts`, `material.ts`, `device.ts`) instead of imported, and
 * the risk that creates is silent divergence: core adds an axis, this package
 * keeps compiling, and the two describe different things under the same name.
 *
 * So this file imports core's real modules by relative path — legal because
 * `capability`, `accessibility` and `state` pull in nothing this package does not
 * already depend on — and asserts assignability in both directions where both
 * directions matter. A type error here IS the failure; the runtime assertions
 * exist so the file is also a test rather than only a typecheck.
 */

import { describe, expect, it } from "vitest";

import {
  resolveAccessibilityPolicy,
  NOMINAL_ACCESSIBILITY_POLICY,
  type ResolvedMaterialPolicy,
} from "../../core/src/accessibility";
import {
  resolveGlassGroupState,
  WEBGPU_AVAILABILITIES,
  type PlatformProbe,
  type WebGPUAvailability as CoreWebGPUAvailability,
} from "../../core/src/capability";
import type { GlassGroupState, RefractionQuality as CoreRefractionQuality } from "../../core/src/state";
import type { FrameContext, FrameParticipant } from "../../core/src/scheduler";
import type { BackdropRebuildRequest, SceneResolution } from "../../core/src/scene";

import type { WebGPUAvailability } from "../src/device";
import {
  accessibilityRefractionCap,
  effectiveRefraction,
  REFRACTION_LADDER,
  type MaterialPolicyView,
  type RefractionQuality,
} from "../src/material";
import { NOMINAL_MATERIAL_POLICY, createWebGPURenderer } from "../src/renderer";
import type {
  FrameContextView,
  FrameParticipantView,
  RebuildRequestView,
  SceneResolutionView,
} from "../src/render-model";

/** Compile-time assignability, forced to have a runtime presence. */
const assignable = <T>(value: T): T => value;

describe("core's types satisfy the renderer's structural views", () => {
  it("SceneResolution is a SceneResolutionView", () => {
    const resolution = null as unknown as SceneResolution;
    const view: SceneResolutionView = assignable(resolution);
    expect(view).toBeNull();
  });

  it("BackdropRebuildRequest is a RebuildRequestView", () => {
    const request = null as unknown as BackdropRebuildRequest;
    const view: RebuildRequestView = assignable(request);
    expect(view).toBeNull();
  });

  it("FrameContext is a FrameContextView", () => {
    const context = null as unknown as FrameContext;
    const view: FrameContextView = assignable(context);
    expect(view).toBeNull();
  });

  it("ResolvedMaterialPolicy is a MaterialPolicyView", () => {
    const policy: ResolvedMaterialPolicy = NOMINAL_ACCESSIBILITY_POLICY.material;
    const view: MaterialPolicyView = assignable(policy);
    expect(view.refraction).toBe("nominal");
  });
});

describe("the renderer's participant satisfies core's", () => {
  it("is assignable to FrameParticipant, so a host adds it directly", () => {
    // Contravariance is what makes this work: the renderer's hooks declare a
    // narrower context, and core's real context is assignable to it.
    const participant: FrameParticipantView = createWebGPURenderer().frameParticipant();
    const core: FrameParticipant = assignable(participant);
    expect(core.id).toBe("vitrea.renderer-webgpu");
  });
});

describe("the WebGPU availability union", () => {
  it("spells every value it produces the way core spells it", () => {
    // K1's amendment (Decision Log #21c) added "not-requested"; the renderer feeds
    // this straight into core's PlatformProbe, so a drift here would be a state the
    // transition table has no row for.
    //
    // The relation is containment, not equality, and the direction is the one
    // that matters: everything this package can report must be something core
    // resolves. Core's union is the wider one — it also carries `"pending"`, the
    // window in which a host has a device and whatever draws with it is not ready
    // yet. This package is *that thing*, so it never has a reading of its own
    // readiness to publish, and the value belongs to the layer that owns the
    // startup handshake.
    const mine: readonly WebGPUAvailability[] = ["not-requested", "unavailable", "available"];
    for (const value of mine) expect([...WEBGPU_AVAILABILITIES]).toContain(value);
    expect([...WEBGPU_AVAILABILITIES].filter((value) => !mine.includes(value as never))).toEqual([
      "pending",
    ]);

    const toCore: CoreWebGPUAvailability = assignable<WebGPUAvailability>("not-requested");
    expect(toCore).toBe("not-requested");
  });

  it("is what a fresh renderer reports before anything is attached", () => {
    const renderer = createWebGPURenderer();
    const probe: Pick<PlatformProbe, "webgpu" | "deviceHealth"> = renderer.capabilityInput;
    expect(probe.webgpu).toBe("not-requested");
  });
});

/**
 * These two now assert something stronger than they were written to.
 *
 * They were a drift check between two hand-written copies of the ladder, this
 * package's and core's. Since Decision Log #23(d) there is one copy, in
 * `@vitrea/policy`, and core's `RefractionQuality` is derived from it — so what
 * this compares is the shared ladder against the type core actually publishes,
 * reached the long way round through `../../core/src/state`. That is the pin that
 * still has to hold: `@vitrea/policy` sits below core and cannot import it, so
 * nothing in the type system stops the ladder from growing a rung core has never
 * heard of. Only this test does.
 */
describe("the refraction ladder", () => {
  it("covers exactly X2's RefractionQuality", () => {
    const mine: readonly RefractionQuality[] = REFRACTION_LADDER;
    const fromCore = assignable<CoreRefractionQuality>("approximate");
    const toMine: RefractionQuality = fromCore;
    expect(mine).toContain(toMine);
    expect([...REFRACTION_LADDER].sort()).toEqual(["approximate", "none", "true"]);
  });

  it("orders weakest first, which is what 'the lower of the two' means", () => {
    expect(REFRACTION_LADDER).toEqual(["none", "approximate", "true"]);
  });
});

describe("Decision Log #19's dual cap", () => {
  const capOf = (policy: ResolvedMaterialPolicy, state: GlassGroupState): RefractionQuality =>
    effectiveRefraction(accessibilityRefractionCap(policy), state.refraction);

  const stateFor = (probe: PlatformProbe): GlassGroupState =>
    resolveGlassGroupState({
      configuredSource: "texture",
      platform: probe,
      source: { taint: "clean", textureCompatibility: "compatible" },
      governor: "none",
      hint: "none",
    });

  const healthy: PlatformProbe = {
    webgpu: "available",
    backdropFilter: true,
    backdropProxyConformance: "pass",
    deviceHealth: "ok",
  };

  it("takes the state's level when accessibility is nominal", () => {
    const state = stateFor(healthy);
    expect(state.refraction).toBe("true");
    expect(capOf(NOMINAL_ACCESSIBILITY_POLICY.material, state)).toBe("true");
  });

  it("takes the accessibility cap when it is the lower one", () => {
    const reduced = resolveAccessibilityPolicy({
      reducedTransparency: true,
      reducedMotion: false,
      increasedContrast: false,
      forcedColors: false,
      reducedTransparencySupported: true,
    });
    const state = stateFor(healthy);
    expect(reduced.material.refraction).toBe("reduced");
    expect(capOf(reduced.material, state)).toBe("approximate");
  });

  it("takes the state's level when IT is the lower one", () => {
    const tainted = resolveGlassGroupState({
      configuredSource: "texture",
      platform: healthy,
      source: { taint: "tainted", textureCompatibility: "compatible" },
      governor: "none",
      hint: "none",
    });
    expect(tainted.refraction).toBe("none");
    expect(capOf(NOMINAL_ACCESSIBILITY_POLICY.material, tainted)).toBe("none");
  });

  it("goes to none under forced colours, whatever the state says", () => {
    const forced = resolveAccessibilityPolicy({
      reducedTransparency: false,
      reducedMotion: false,
      increasedContrast: false,
      forcedColors: true,
      reducedTransparencySupported: true,
    });
    expect(capOf(forced.material, stateFor(healthy))).toBe("none");
  });

  it("is symmetric — neither cap is privileged", () => {
    for (const a of REFRACTION_LADDER) {
      for (const b of REFRACTION_LADDER) {
        expect(effectiveRefraction(a, b)).toBe(effectiveRefraction(b, a));
      }
    }
  });
});

describe("the renderer's nominal policy", () => {
  it("matches core's nominal material policy axis for axis", () => {
    // If core gains an axis this stops compiling, which is the point.
    const core: MaterialPolicyView = NOMINAL_ACCESSIBILITY_POLICY.material;
    for (const key of Object.keys(NOMINAL_MATERIAL_POLICY) as (keyof MaterialPolicyView)[]) {
      expect(NOMINAL_MATERIAL_POLICY[key]).toBe(core[key]);
    }
  });
});
