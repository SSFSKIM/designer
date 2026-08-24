/**
 * X2 — the resolved-state machine.
 *
 * Two layers of test. The named transitions walk every `demotionReason` in the
 * spec's enum plus the recovery that clears it; the property block then sweeps
 * the whole input space and asserts the laws that must hold for all of them —
 * above all that `configuredSource` is never mutated.
 */

import { describe, expect, it } from "vitest";

import {
  DEMOTION_REASONS,
  DEMOTION_RECOVERY,
  GOVERNOR_PRESSURES,
  HINT_AVAILABILITIES,
  classifyStateChange,
  resolveGlassGroupState,
  type CapabilityInputs,
  type DemotionReason,
  type GlassGroupState,
  type PlatformProbe,
} from "../src/index";

const workingPlatform: PlatformProbe = {
  webgpu: true,
  backdropFilter: true,
  backdropProxyConformance: "pass",
  deviceHealth: "ok",
};

/** A texture group with everything working: the `texture` + `exact` primary state. */
const healthyTexture: CapabilityInputs = {
  configuredSource: "texture",
  platform: workingPlatform,
  source: { taint: "clean", textureCompatibility: "compatible" },
  governor: "none",
  hint: "none",
};

/** A dom group with everything working: the `dom` + `none` default state. */
const healthyDom: CapabilityInputs = {
  configuredSource: "dom",
  platform: workingPlatform,
  governor: "none",
  hint: "none",
};

const withPlatform = <T extends CapabilityInputs>(inputs: T, patch: Partial<PlatformProbe>): T => ({
  ...inputs,
  platform: { ...inputs.platform, ...patch },
});

describe("the three healthy primary states (§honesty core)", () => {
  it("texture + exact — a GPU-ownable source gets full refraction", () => {
    expect(resolveGlassGroupState(healthyTexture)).toEqual({
      configuredSource: "texture",
      activeRenderer: "webgpu",
      samplingBackend: "gpu-texture",
      refraction: "true",
      analysis: "exact",
      health: "ok",
    } satisfies GlassGroupState);
  });

  it("dom + hint — the CSS proxy blurs, the GPU approximates, the author supplies adaptation", () => {
    expect(resolveGlassGroupState({ ...healthyDom, hint: "author-hint" })).toEqual({
      configuredSource: "dom",
      activeRenderer: "webgpu",
      samplingBackend: "css-backdrop",
      refraction: "approximate",
      analysis: "hint",
      health: "ok",
    } satisfies GlassGroupState);
  });

  it("dom + none — arbitrary DOM's default: healthy, not demoted", () => {
    const state = resolveGlassGroupState(healthyDom);
    expect(state.analysis).toBe("none");
    expect(state.health).toBe("ok");
    expect(state.demotionReason).toBeUndefined();
  });

  it("treats an estimator provider as a hint, never as analysis", () => {
    expect(resolveGlassGroupState({ ...healthyDom, hint: "estimator" }).analysis).toBe("hint");
  });
});

describe("demotion transitions — every reason in the enum", () => {
  it("no-webgpu: the whole group falls to the CSS tier, configuredSource intact", () => {
    const state = resolveGlassGroupState(withPlatform(healthyTexture, { webgpu: false }));

    expect(state).toEqual({
      configuredSource: "texture",
      activeRenderer: "css",
      samplingBackend: "css-backdrop",
      refraction: "none",
      analysis: "none",
      health: "demoted",
      demotionReason: "no-webgpu",
    } satisfies GlassGroupState);
  });

  it("no-webgpu on a dom group too — acceptance #5's exact report", () => {
    const state = resolveGlassGroupState(withPlatform(healthyDom, { webgpu: false }));

    expect(state.activeRenderer).toBe("css");
    expect(state.demotionReason).toBe("no-webgpu");
    expect(state.configuredSource).toBe("dom");
  });

  it("no-backdrop-filter: a dom group loses its only sampling path", () => {
    const state = resolveGlassGroupState(withPlatform(healthyDom, { backdropFilter: false }));

    expect(state).toEqual({
      configuredSource: "dom",
      activeRenderer: "webgpu",
      samplingBackend: "none",
      refraction: "none",
      analysis: "none",
      health: "demoted",
      demotionReason: "no-backdrop-filter",
    } satisfies GlassGroupState);
  });

  it("tainted-source: WebGPU keeps drawing, it just has nothing to sample", () => {
    const state = resolveGlassGroupState({
      ...healthyTexture,
      source: { taint: "tainted", textureCompatibility: "compatible" },
    });

    expect(state.activeRenderer).toBe("webgpu");
    expect(state.samplingBackend).toBe("none");
    expect(state.refraction).toBe("none");
    expect(state.demotionReason).toBe("tainted-source");
  });

  it("incompatible-texture: a view that fails the declared requirements demotes sampling", () => {
    const state = resolveGlassGroupState({
      ...healthyTexture,
      source: { taint: "clean", textureCompatibility: "incompatible" },
    });

    expect(state.demotionReason).toBe("incompatible-texture");
    expect(state.samplingBackend).toBe("none");
  });

  it("device-lost: the renderer falls back while recovery runs", () => {
    const state = resolveGlassGroupState(withPlatform(healthyTexture, { deviceHealth: "lost" }));

    expect(state.activeRenderer).toBe("css");
    expect(state.demotionReason).toBe("device-lost");
  });

  it("probe-failed: S1's conformance probe rejects the proxy topology", () => {
    const state = resolveGlassGroupState(
      withPlatform(healthyDom, { backdropProxyConformance: "fail" }),
    );

    expect(state.demotionReason).toBe("probe-failed");
    expect(state.samplingBackend).toBe("none");
    expect(state.configuredSource).toBe("dom");
  });

  it("governor: a tier switch under pressure is a demotion", () => {
    const state = resolveGlassGroupState({ ...healthyTexture, governor: "demote-tier" });

    expect(state.activeRenderer).toBe("css");
    expect(state.demotionReason).toBe("governor");
  });

  it("governor: degrading WITHIN the tier is not a demotion at all", () => {
    const degraded = resolveGlassGroupState({ ...healthyTexture, governor: "degrade-in-tier" });

    expect(degraded).toEqual(resolveGlassGroupState(healthyTexture));
    expect(degraded.health).toBe("ok");
  });

  it("covers every reason the spec enumerates", () => {
    const cases: readonly CapabilityInputs[] = [
      withPlatform(healthyTexture, { webgpu: false }),
      withPlatform(healthyDom, { backdropFilter: false }),
      { ...healthyTexture, source: { taint: "tainted", textureCompatibility: "compatible" } },
      { ...healthyTexture, source: { taint: "clean", textureCompatibility: "incompatible" } },
      withPlatform(healthyTexture, { deviceHealth: "lost" }),
      withPlatform(healthyDom, { backdropProxyConformance: "fail" }),
      { ...healthyTexture, governor: "demote-tier" },
    ];

    const observed = new Set(cases.map((input) => resolveGlassGroupState(input).demotionReason));

    expect(observed).toEqual(new Set(DEMOTION_REASONS));
  });
});

describe("recovery transitions", () => {
  const recoveries: readonly {
    readonly reason: DemotionReason;
    readonly broken: CapabilityInputs;
    readonly repaired: CapabilityInputs;
  }[] = [
    {
      reason: "no-webgpu",
      broken: withPlatform(healthyTexture, { webgpu: false }),
      repaired: healthyTexture,
    },
    {
      reason: "no-backdrop-filter",
      broken: withPlatform(healthyDom, { backdropFilter: false }),
      repaired: healthyDom,
    },
    {
      reason: "tainted-source",
      broken: {
        ...healthyTexture,
        source: { taint: "tainted", textureCompatibility: "compatible" },
      },
      repaired: healthyTexture,
    },
    {
      reason: "incompatible-texture",
      broken: {
        ...healthyTexture,
        source: { taint: "clean", textureCompatibility: "incompatible" },
      },
      repaired: healthyTexture,
    },
    {
      reason: "device-lost",
      broken: withPlatform(healthyTexture, { deviceHealth: "lost" }),
      repaired: healthyTexture,
    },
    {
      reason: "probe-failed",
      broken: withPlatform(healthyDom, { backdropProxyConformance: "fail" }),
      repaired: healthyDom,
    },
    {
      reason: "governor",
      broken: { ...healthyTexture, governor: "demote-tier" },
      repaired: healthyTexture,
    },
  ];

  for (const { reason, broken, repaired } of recoveries) {
    it(`${reason} clears when its named trigger fires, returning to a healthy state`, () => {
      const demoted = resolveGlassGroupState(broken);
      expect(demoted.demotionReason).toBe(reason);

      const recovered = resolveGlassGroupState(repaired);
      expect(recovered.health).toBe("ok");
      expect(recovered.demotionReason).toBeUndefined();
      expect(recovered.configuredSource).toBe(demoted.configuredSource);

      expect(classifyStateChange(demoted, recovered)).toEqual({ kind: "recovered", from: reason });
    });
  }

  it("names a recovery trigger for every reason", () => {
    expect(Object.keys(DEMOTION_RECOVERY).sort()).toEqual([...DEMOTION_REASONS].sort());
  });

  it("names the right trigger for each reason, and is honest that no-webgpu has none", () => {
    expect(DEMOTION_RECOVERY["no-webgpu"].trigger).toBe("none");
    expect(DEMOTION_RECOVERY["no-backdrop-filter"].trigger).toBe("probe-repassed");
    expect(DEMOTION_RECOVERY["tainted-source"].trigger).toBe("source-replaced");
    expect(DEMOTION_RECOVERY["incompatible-texture"].trigger).toBe("source-replaced");
    expect(DEMOTION_RECOVERY["device-lost"].trigger).toBe("device-restored");
    expect(DEMOTION_RECOVERY["probe-failed"].trigger).toBe("probe-repassed");
    expect(DEMOTION_RECOVERY.governor.trigger).toBe("pressure-released");
  });

  it("calls a group's first resolution initial, not a change", () => {
    expect(classifyStateChange(undefined, resolveGlassGroupState(healthyTexture))).toEqual({
      kind: "initial",
    });
    expect(
      classifyStateChange(
        undefined,
        resolveGlassGroupState(withPlatform(healthyTexture, { webgpu: false })),
      ),
    ).toEqual({ kind: "initial", reason: "no-webgpu" });
  });

  it("classifies the other three change kinds", () => {
    const healthy = resolveGlassGroupState(healthyTexture);
    const demoted = resolveGlassGroupState(withPlatform(healthyTexture, { deviceHealth: "lost" }));
    const otherDemotion = resolveGlassGroupState({
      ...healthyTexture,
      source: { taint: "tainted", textureCompatibility: "compatible" },
    });

    expect(classifyStateChange(healthy, healthy)).toEqual({ kind: "unchanged" });
    expect(classifyStateChange(healthy, demoted)).toEqual({
      kind: "demoted",
      reason: "device-lost",
    });
    expect(classifyStateChange(demoted, otherDemotion)).toEqual({
      kind: "changed",
      reason: "tainted-source",
    });
  });
});

describe("reason precedence when several faults hold at once", () => {
  it("names the platform fault before a per-source one", () => {
    const state = resolveGlassGroupState({
      ...withPlatform(healthyTexture, { webgpu: false }),
      source: { taint: "tainted", textureCompatibility: "compatible" },
    });

    expect(state.demotionReason).toBe("no-webgpu");
  });

  it("names taint before texture incompatibility — an unreadable source makes format moot", () => {
    const state = resolveGlassGroupState({
      ...healthyTexture,
      source: { taint: "tainted", textureCompatibility: "incompatible" },
    });

    expect(state.demotionReason).toBe("tainted-source");
  });

  it("names the governor last, so pressure never masks a real fault", () => {
    const state = resolveGlassGroupState({
      ...withPlatform(healthyDom, { backdropProxyConformance: "fail" }),
      governor: "demote-tier",
    });

    expect(state.demotionReason).toBe("probe-failed");
  });

  it("reports the governor when pressure is the only thing holding the group down", () => {
    const state = resolveGlassGroupState({ ...healthyDom, governor: "demote-tier" });

    expect(state.demotionReason).toBe("governor");
  });
});

/** Every combination of every input axis. */
function everyInput(): readonly CapabilityInputs[] {
  const all: CapabilityInputs[] = [];
  for (const webgpu of [true, false]) {
    for (const backdropFilter of [true, false]) {
      for (const backdropProxyConformance of ["pass", "fail"] as const) {
        for (const deviceHealth of ["ok", "lost"] as const) {
          for (const governor of GOVERNOR_PRESSURES) {
            for (const hint of HINT_AVAILABILITIES) {
              const platform: PlatformProbe = {
                webgpu,
                backdropFilter,
                backdropProxyConformance,
                deviceHealth,
              };
              all.push({ configuredSource: "dom", platform, governor, hint });
              for (const taint of ["clean", "tainted"] as const) {
                for (const textureCompatibility of ["compatible", "incompatible"] as const) {
                  all.push({
                    configuredSource: "texture",
                    platform,
                    source: { taint, textureCompatibility },
                    governor,
                    hint,
                  });
                }
              }
            }
          }
        }
      }
    }
  }
  return all;
}

describe("laws that hold across the whole input space", () => {
  const inputs = everyInput();

  it("sweeps every combination of every axis", () => {
    // 2 webgpu x 2 backdropFilter x 2 conformance x 2 deviceHealth x 3 governor
    // x 3 hint = 144 platform states; each yields 1 dom case and 4 texture cases.
    expect(inputs).toHaveLength(144 * 5);
  });

  it("never mutates configuredSource — the property the honesty core exists for", () => {
    for (const input of inputs) {
      expect(resolveGlassGroupState(input).configuredSource).toBe(input.configuredSource);
    }
  });

  it("is deterministic", () => {
    for (const input of inputs) {
      expect(resolveGlassGroupState(input)).toEqual(resolveGlassGroupState(input));
    }
  });

  it("keeps health and demotionReason in agreement", () => {
    for (const input of inputs) {
      const state = resolveGlassGroupState(input);
      expect(state.health === "demoted").toBe(state.demotionReason !== undefined);
    }
  });

  it("grants exact analysis only where a GPU texture is actually sampled", () => {
    for (const input of inputs) {
      const state = resolveGlassGroupState(input);
      if (state.analysis === "exact") {
        expect(state.samplingBackend).toBe("gpu-texture");
        expect(state.activeRenderer).toBe("webgpu");
        expect(state.configuredSource).toBe("texture");
      }
    }
  });

  it("ties true refraction to GPU-texture sampling, both ways", () => {
    for (const input of inputs) {
      const state = resolveGlassGroupState(input);
      expect(state.refraction === "true").toBe(state.samplingBackend === "gpu-texture");
    }
  });

  it("never claims any refraction without a shader running", () => {
    for (const input of inputs) {
      const state = resolveGlassGroupState(input);
      if (state.refraction !== "none") expect(state.activeRenderer).toBe("webgpu");
    }
  });

  it("treats a CSS-tier fallback as a demotion, always", () => {
    for (const input of inputs) {
      const state = resolveGlassGroupState(input);
      if (state.activeRenderer === "css") expect(state.health).toBe("demoted");
    }
  });

  it("reports no hint-derived analysis where the app supplied no hint mechanism", () => {
    for (const input of inputs) {
      const state = resolveGlassGroupState(input);
      if (input.hint === "none") expect(state.analysis).not.toBe("hint");
    }
  });

  it("names only an applicable fault as the reason", () => {
    for (const input of inputs) {
      const state = resolveGlassGroupState(input);
      if (state.demotionReason === undefined) continue;

      switch (state.demotionReason) {
        case "no-webgpu":
          expect(input.platform.webgpu).toBe(false);
          break;
        case "device-lost":
          expect(input.platform.deviceHealth).toBe("lost");
          break;
        case "tainted-source":
          expect(input.configuredSource).toBe("texture");
          expect(input.source?.taint).toBe("tainted");
          break;
        case "incompatible-texture":
          expect(input.source?.textureCompatibility).toBe("incompatible");
          break;
        case "no-backdrop-filter":
          expect(input.configuredSource).toBe("dom");
          expect(input.platform.backdropFilter).toBe(false);
          break;
        case "probe-failed":
          expect(input.configuredSource).toBe("dom");
          expect(input.platform.backdropProxyConformance).toBe("fail");
          break;
        case "governor":
          expect(input.governor).toBe("demote-tier");
          break;
      }
    }
  });

  it("collapses the free tuple to a small enumerated set of legal states", () => {
    const distinct = new Set(inputs.map((input) => JSON.stringify(resolveGlassGroupState(input))));

    for (const encoded of distinct) {
      const state = JSON.parse(encoded) as GlassGroupState;
      expect(["texture", "dom"]).toContain(state.configuredSource);
      expect(["webgpu", "css"]).toContain(state.activeRenderer);
      expect(["gpu-texture", "css-backdrop", "none"]).toContain(state.samplingBackend);
      expect(["true", "approximate", "none"]).toContain(state.refraction);
      expect(["exact", "hint", "none"]).toContain(state.analysis);
      expect(["ok", "demoted"]).toContain(state.health);
      if (state.demotionReason !== undefined) {
        expect([...DEMOTION_REASONS]).toContain(state.demotionReason);
      }
    }

    // All 720 input combinations collapse to 45 states: 25 for texture groups,
    // 20 for dom groups. Pinned so that adding a state has to be a deliberate
    // act rather than a side effect of touching the resolver.
    expect(distinct.size).toBe(45);
  });
});
