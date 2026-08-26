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
  WEBGPU_AVAILABILITIES,
  classifyStateChange,
  resolveGlassGroupState,
  type CapabilityInputs,
  type DemotionReason,
  type GlassGroupState,
  type PlatformProbe,
} from "../src/index";

const workingPlatform: PlatformProbe = {
  webgpu: "available",
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

describe("CSS by choice — WebGPU not requested is not a fault (X2's K1 amendment)", () => {
  it("a dom group on a CSS-only root resolves healthy, not demoted", () => {
    const state = resolveGlassGroupState(withPlatform(healthyDom, { webgpu: "not-requested" }));

    expect(state).toEqual({
      configuredSource: "dom",
      activeRenderer: "css",
      samplingBackend: "css-backdrop",
      refraction: "none",
      analysis: "none",
      health: "ok",
    } satisfies GlassGroupState);
  });

  it("a texture group on a CSS-only root still samples the DOM behind it, healthy", () => {
    const state = resolveGlassGroupState(withPlatform(healthyTexture, { webgpu: "not-requested" }));

    expect(state).toEqual({
      configuredSource: "texture",
      activeRenderer: "css",
      samplingBackend: "css-backdrop",
      refraction: "none",
      analysis: "none",
      health: "ok",
    } satisfies GlassGroupState);
  });

  it("names no demotion reason at all — not even no-webgpu", () => {
    const state = resolveGlassGroupState(withPlatform(healthyDom, { webgpu: "not-requested" }));
    expect(state.demotionReason).toBeUndefined();
  });

  it("a tainted texture source still faults independently — the amendment is scoped to webgpu, not to every axis", () => {
    // K1 narrowly suppresses `no-webgpu`/`device-lost`; a per-source fact like
    // taint is unrelated to whether this root ever asked for WebGPU, so it
    // keeps reporting exactly as it always has (reason precedence already
    // tolerates a reported reason outranking the one actually holding a group
    // on the CSS tier — see the governor/taint precedence case below).
    const state = resolveGlassGroupState({
      ...withPlatform(healthyTexture, { webgpu: "not-requested" }),
      source: { taint: "tainted", textureCompatibility: "compatible" },
    });

    expect(state.health).toBe("demoted");
    expect(state.demotionReason).toBe("tainted-source");
    expect(state.activeRenderer).toBe("css");
    expect(state.samplingBackend).toBe("css-backdrop");
  });

  it("still reports a real, independent fault honestly — missing backdrop-filter is not about WebGPU", () => {
    const state = resolveGlassGroupState(
      withPlatform(healthyDom, { webgpu: "not-requested", backdropFilter: false }),
    );

    expect(state.demotionReason).toBe("no-backdrop-filter");
    expect(state.health).toBe("demoted");
    expect(state.activeRenderer).toBe("css");
  });

  it("requested-and-unavailable is unchanged: exactly today's demoted no-webgpu behavior", () => {
    const state = resolveGlassGroupState(withPlatform(healthyDom, { webgpu: "unavailable" }));

    expect(state).toEqual({
      configuredSource: "dom",
      activeRenderer: "css",
      samplingBackend: "css-backdrop",
      refraction: "none",
      analysis: "none",
      health: "demoted",
      demotionReason: "no-webgpu",
    } satisfies GlassGroupState);
  });
});

describe("demotion transitions — every reason in the enum", () => {
  it("no-webgpu: the whole group falls to the CSS tier, configuredSource intact", () => {
    const state = resolveGlassGroupState(withPlatform(healthyTexture, { webgpu: "unavailable" }));

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
    const state = resolveGlassGroupState(withPlatform(healthyDom, { webgpu: "unavailable" }));

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

  it("no-texture-supplied: a declared texture nobody handed pixels to samples nothing", () => {
    const state = resolveGlassGroupState({
      ...healthyTexture,
      source: { taint: "clean", textureCompatibility: "compatible", supply: "absent" },
    });

    // The loudest version of the pretence this file exists to prevent would be
    // gpu-texture / true / exact over a source with no pixels behind it.
    expect(state).toEqual({
      configuredSource: "texture",
      activeRenderer: "webgpu",
      samplingBackend: "none",
      refraction: "none",
      analysis: "none",
      health: "demoted",
      demotionReason: "no-texture-supplied",
    } satisfies GlassGroupState);
  });

  it("no-texture-supplied outranks taint and compatibility, which describe pixels that are not there", () => {
    const state = resolveGlassGroupState({
      ...healthyTexture,
      source: { taint: "tainted", textureCompatibility: "incompatible", supply: "absent" },
    });

    expect(state.demotionReason).toBe("no-texture-supplied");
  });

  it("treats an unstated supply as supplied, because core cannot see pixels either way", () => {
    expect(resolveGlassGroupState(healthyTexture).samplingBackend).toBe("gpu-texture");
    expect(
      resolveGlassGroupState({
        ...healthyTexture,
        source: { taint: "clean", textureCompatibility: "compatible", supply: "supplied" },
      }),
    ).toEqual(resolveGlassGroupState(healthyTexture));
  });

  it("device-lost: the renderer falls back while recovery runs", () => {
    const state = resolveGlassGroupState(withPlatform(healthyTexture, { deviceHealth: "lost" }));

    expect(state.activeRenderer).toBe("css");
    expect(state.demotionReason).toBe("device-lost");
  });

  it("probe-failed: a rejected proxy topology drops the group to the CSS tier", () => {
    const state = resolveGlassGroupState(
      withPlatform(healthyDom, { backdropProxyConformance: "fail" }),
    );

    // The CSS tier filters in place and uses no proxies, so the thing that
    // failed is not on its path — it still frosts, it just stops lensing.
    expect(state).toEqual({
      configuredSource: "dom",
      activeRenderer: "css",
      samplingBackend: "css-backdrop",
      refraction: "none",
      analysis: "none",
      health: "demoted",
      demotionReason: "probe-failed",
    } satisfies GlassGroupState);
  });

  it("no-backdrop-filter keeps WebGPU, because the CSS tier could not draw glass either", () => {
    const state = resolveGlassGroupState(withPlatform(healthyDom, { backdropFilter: false }));

    expect(state.activeRenderer).toBe("webgpu");
    expect(state.samplingBackend).toBe("none");
  });

  it("does not stack probe-failed on top of no-backdrop-filter", () => {
    // A proxy-topology verdict is meaningless where there is no filter to
    // apply. Raising both would demote the renderer (probe-failed does) while
    // leaving no CSS blur to draw with — the worst of both tiers.
    const state = resolveGlassGroupState(
      withPlatform(healthyDom, { backdropFilter: false, backdropProxyConformance: "fail" }),
    );

    expect(state.demotionReason).toBe("no-backdrop-filter");
    expect(state.activeRenderer).toBe("webgpu");
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
      withPlatform(healthyTexture, { webgpu: "unavailable" }),
      withPlatform(healthyDom, { backdropFilter: false }),
      { ...healthyTexture, source: { taint: "tainted", textureCompatibility: "compatible" } },
      { ...healthyTexture, source: { taint: "clean", textureCompatibility: "incompatible" } },
      {
        ...healthyTexture,
        source: { taint: "clean", textureCompatibility: "compatible", supply: "absent" },
      },
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
      broken: withPlatform(healthyTexture, { webgpu: "unavailable" }),
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
      reason: "no-texture-supplied",
      broken: {
        ...healthyTexture,
        source: { taint: "clean", textureCompatibility: "compatible", supply: "absent" },
      },
      repaired: healthyTexture,
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
    expect(DEMOTION_RECOVERY["no-texture-supplied"].trigger).toBe("source-replaced");
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
        resolveGlassGroupState(withPlatform(healthyTexture, { webgpu: "unavailable" })),
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
      ...withPlatform(healthyTexture, { webgpu: "unavailable" }),
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
  for (const webgpu of WEBGPU_AVAILABILITIES) {
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
                  for (const supply of ["supplied", "absent"] as const) {
                    all.push({
                      configuredSource: "texture",
                      platform,
                      source: { taint, textureCompatibility, supply },
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
  }
  return all;
}

describe("laws that hold across the whole input space", () => {
  const inputs = everyInput();

  it("sweeps every combination of every axis", () => {
    // 4 webgpu x 2 backdropFilter x 2 conformance x 2 deviceHealth x 3 governor
    // x 3 hint = 288 platform states; each yields 1 dom case and 8 texture cases
    // (taint x compatibility x supply).
    expect(inputs).toHaveLength(288 * 9);
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

  it("treats a CSS-tier fallback as a demotion, unless WebGPU was never requested or is still starting", () => {
    // X2's K1 amendment: a CSS-by-choice root lands on the CSS tier too, but
    // landing there by choice is not landing there by fault — and neither is
    // landing there for the frames before the GPU tier has answered.
    for (const input of inputs) {
      const state = resolveGlassGroupState(input);
      if (
        state.activeRenderer === "css" &&
        input.platform.webgpu !== "not-requested" &&
        input.platform.webgpu !== "pending"
      ) {
        expect(state.health).toBe("demoted");
      }
    }
  });

  it("never reports no-webgpu or device-lost while WebGPU is unrequested or pending", () => {
    for (const input of inputs) {
      if (input.platform.webgpu === "unavailable" || input.platform.webgpu === "available") {
        continue;
      }
      const state = resolveGlassGroupState(input);
      expect(state.demotionReason).not.toBe("no-webgpu");
      expect(state.demotionReason).not.toBe("device-lost");
    }
  });

  it("resolves a group on the CSS tier without a fault — by choice or while pending — to health ok", () => {
    for (const input of inputs) {
      if (input.platform.webgpu === "unavailable" || input.platform.webgpu === "available") {
        continue;
      }
      if (input.governor === "demote-tier") continue;
      if (input.configuredSource === "texture" && input.source.supply === "absent") continue;
      if (input.configuredSource === "texture" && input.source.taint === "tainted") continue;
      if (
        input.configuredSource === "texture" &&
        input.source.textureCompatibility === "incompatible"
      ) {
        continue;
      }
      if (!input.platform.backdropFilter) continue;
      if (input.platform.backdropProxyConformance === "fail") continue;

      const state = resolveGlassGroupState(input);
      expect(state.health).toBe("ok");
      expect(state.demotionReason).toBeUndefined();
      expect(state.activeRenderer).toBe("css");
    }
  });

  it("resolves pending exactly as not-requested does, on every other axis", () => {
    for (const input of inputs) {
      if (input.platform.webgpu !== "pending") continue;
      const asNotRequested = resolveGlassGroupState({
        ...input,
        platform: { ...input.platform, webgpu: "not-requested" },
      } as CapabilityInputs);

      expect(resolveGlassGroupState(input)).toEqual(asNotRequested);
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
          expect(input.platform.webgpu).toBe("unavailable");
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
        case "no-texture-supplied":
          expect(input.configuredSource).toBe("texture");
          expect(input.source?.supply).toBe("absent");
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

    // All 2592 input combinations collapse to 55 states: 35 for texture groups,
    // 20 for dom groups. Pinned so that adding a state has to be a deliberate
    // act rather than a side effect of touching the resolver.
    //
    // Was 43 (25 texture, 18 dom) on 720 combinations before X2's K1 amendment
    // (Decision Log #21c) added `webgpu: "not-requested"` alongside the prior
    // two-valued axis; that took it to 49 (29 texture, 20 dom) on 1080. Its 6 new
    // states were exactly the healthy, undemoted mirror of the 6 that already
    // existed at `webgpu: "unavailable"` with no other fault — same shape,
    // `health: "ok"` instead of `demoted`/`no-webgpu`, because choosing the CSS
    // tier is not a fault.
    //
    // `webgpu: "pending"` adds none at all, which is the whole claim being made
    // about it: it resolves identically to `"not-requested"`. The 6 states since
    // then are the `no-texture-supplied` family — a texture group whose pixels
    // never arrived, on either tier, with and without a hint to analyse.
    expect(distinct.size).toBe(55);
  });
});
