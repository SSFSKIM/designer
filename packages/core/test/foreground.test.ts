/**
 * §Foreground adaptation — mode-vs-state legality.
 *
 * `sampled-async` requires `analysis: "exact"`, exactly. An illegal combination
 * resolves to the nearest legal mode and says so: the honesty doctrine forbids
 * both silently pretending and silently doing nothing.
 */

import { describe, expect, it } from "vitest";

import {
  FOREGROUND_MODES,
  SAMPLED_ASYNC_DEFAULTS,
  SAMPLED_ASYNC_RATE_LIMITS,
  createDiagnosticsChannel,
  defaultForegroundAdaptation,
  resolveForegroundAdaptation,
  resolveGlassGroupState,
  type AnalysisQuality,
  type CapabilityInputs,
  type ForegroundAdaptation,
  type GlassGroupState,
} from "../src/index";

const workingPlatform = {
  webgpu: true,
  backdropFilter: true,
  backdropProxyConformance: "pass",
  deviceHealth: "ok",
} as const;

/** A state with the given analysis quality, resolved rather than hand-written. */
function stateWithAnalysis(analysis: AnalysisQuality): GlassGroupState {
  const inputs: Record<AnalysisQuality, CapabilityInputs> = {
    exact: {
      configuredSource: "texture",
      platform: workingPlatform,
      source: { taint: "clean", textureCompatibility: "compatible" },
      governor: "none",
      hint: "none",
    },
    hint: {
      configuredSource: "dom",
      platform: workingPlatform,
      governor: "none",
      hint: "author-hint",
    },
    none: {
      configuredSource: "dom",
      platform: workingPlatform,
      governor: "none",
      hint: "none",
    },
  };

  const state = resolveGlassGroupState(inputs[analysis]);
  if (state.analysis !== analysis) throw new Error(`fixture drift: got ${state.analysis}`);
  return state;
}

const sampled = (
  rateHz: number = SAMPLED_ASYNC_DEFAULTS.rateHz,
  hysteresis: number = SAMPLED_ASYNC_DEFAULTS.hysteresis,
): ForegroundAdaptation => ({ mode: "sampled-async", rateHz, hysteresis });

describe("mode vocabulary", () => {
  it("ships exactly the three modes the spec names, most adaptive first", () => {
    expect([...FOREGROUND_MODES]).toEqual(["sampled-async", "author-hint", "fixed"]);
  });
});

describe("legal combinations pass through untouched", () => {
  it("keeps sampled-async where analysis is exact", () => {
    const resolved = resolveForegroundAdaptation(sampled(8, 0.1), stateWithAnalysis("exact"));

    expect(resolved.adaptation).toEqual({ mode: "sampled-async", rateHz: 8, hysteresis: 0.1 });
    expect(resolved.downgraded).toBeUndefined();
  });

  it("keeps author-hint where a hint mechanism exists", () => {
    const resolved = resolveForegroundAdaptation({ mode: "author-hint" }, stateWithAnalysis("hint"));

    expect(resolved.adaptation).toEqual({ mode: "author-hint" });
    expect(resolved.downgraded).toBeUndefined();
  });

  it("keeps author-hint where analysis is exact — a richer state still serves it", () => {
    const resolved = resolveForegroundAdaptation(
      { mode: "author-hint" },
      stateWithAnalysis("exact"),
    );

    expect(resolved.adaptation).toEqual({ mode: "author-hint" });
    expect(resolved.downgraded).toBeUndefined();
  });

  it("keeps fixed everywhere — it asks nothing of the state", () => {
    for (const analysis of ["exact", "hint", "none"] as const) {
      const resolved = resolveForegroundAdaptation({ mode: "fixed" }, stateWithAnalysis(analysis));
      expect(resolved.adaptation).toEqual({ mode: "fixed" });
      expect(resolved.downgraded).toBeUndefined();
    }
  });
});

describe("illegal combinations resolve to the nearest legal mode", () => {
  it("sampled-async on a hint state falls to author-hint, one step down", () => {
    const diagnostics = createDiagnosticsChannel();
    const resolved = resolveForegroundAdaptation(sampled(), stateWithAnalysis("hint"), {
      subject: "g1",
      diagnostics,
    });

    expect(resolved.adaptation).toEqual({ mode: "author-hint" });
    expect(resolved.downgraded).toEqual({ from: "sampled-async", to: "author-hint" });
    expect(diagnostics.reported[0]).toMatchObject({
      code: "foreground-mode-illegal",
      severity: "warning",
      subjects: ["g1"],
    });
    expect(diagnostics.reported[0]?.message).toContain("analysis: exact");
  });

  it("sampled-async on a state with no analysis falls all the way to fixed", () => {
    const resolved = resolveForegroundAdaptation(sampled(), stateWithAnalysis("none"));

    expect(resolved.adaptation).toEqual({ mode: "fixed" });
    expect(resolved.downgraded).toEqual({ from: "sampled-async", to: "fixed" });
  });

  it("author-hint with no hint mechanism falls to fixed", () => {
    const resolved = resolveForegroundAdaptation({ mode: "author-hint" }, stateWithAnalysis("none"));

    expect(resolved.adaptation).toEqual({ mode: "fixed" });
    expect(resolved.downgraded).toEqual({ from: "author-hint", to: "fixed" });
  });

  it("reports the illegal mode once per group, not once per frame", () => {
    const diagnostics = createDiagnosticsChannel();
    const state = stateWithAnalysis("none");

    for (let frame = 0; frame < 5; frame += 1) {
      resolveForegroundAdaptation(sampled(), state, { subject: "g1", diagnostics });
    }

    expect(diagnostics.reported).toHaveLength(1);
  });

  it("downgrades a demoted group's mode too — a lost device takes exact analysis with it", () => {
    const demoted = resolveGlassGroupState({
      configuredSource: "texture",
      platform: { ...workingPlatform, deviceHealth: "lost" },
      source: { taint: "clean", textureCompatibility: "compatible" },
      governor: "none",
      hint: "none",
    });

    expect(demoted.analysis).toBe("none");
    expect(resolveForegroundAdaptation(sampled(), demoted).adaptation).toEqual({ mode: "fixed" });
  });
});

describe("sampled-async parameter validation", () => {
  it("clamps a per-frame rate down to the low-frequency ceiling", () => {
    const diagnostics = createDiagnosticsChannel();
    const resolved = resolveForegroundAdaptation(sampled(60, 0.1), stateWithAnalysis("exact"), {
      subject: "g1",
      diagnostics,
    });

    expect(resolved.adaptation).toEqual({
      mode: "sampled-async",
      rateHz: SAMPLED_ASYNC_RATE_LIMITS.maxHz,
      hysteresis: 0.1,
    });
    expect(diagnostics.reported[0]).toMatchObject({ code: "foreground-rate-clamped" });
  });

  it("clamps a non-positive rate up to the floor", () => {
    const resolved = resolveForegroundAdaptation(sampled(0, 0.1), stateWithAnalysis("exact"));

    expect(resolved.adaptation).toEqual({
      mode: "sampled-async",
      rateHz: SAMPLED_ASYNC_RATE_LIMITS.minHz,
      hysteresis: 0.1,
    });
  });

  it("clamps hysteresis into its open range, so a threshold can never pump", () => {
    const raised = resolveForegroundAdaptation(sampled(4, 0), stateWithAnalysis("exact"));
    const lowered = resolveForegroundAdaptation(sampled(4, 5), stateWithAnalysis("exact"));

    expect(raised.adaptation).toEqual({
      mode: "sampled-async",
      rateHz: 4,
      hysteresis: SAMPLED_ASYNC_RATE_LIMITS.minHysteresis,
    });
    expect(lowered.adaptation).toEqual({
      mode: "sampled-async",
      rateHz: 4,
      hysteresis: SAMPLED_ASYNC_RATE_LIMITS.maxHysteresis,
    });
  });

  it("keeps the readback well below one frame at 60Hz — the spec's 'never per-frame'", () => {
    expect(SAMPLED_ASYNC_RATE_LIMITS.maxHz).toBeLessThan(30);
    expect(SAMPLED_ASYNC_DEFAULTS.rateHz).toBeLessThanOrEqual(SAMPLED_ASYNC_RATE_LIMITS.maxHz);
    expect(SAMPLED_ASYNC_DEFAULTS.hysteresis).toBeGreaterThan(
      SAMPLED_ASYNC_RATE_LIMITS.minHysteresis,
    );
  });
});

describe("defaults per resolved state", () => {
  it("adapts by default where it honestly can", () => {
    expect(defaultForegroundAdaptation(stateWithAnalysis("exact"))).toEqual(sampled());
  });

  it("uses the hint where that is all there is", () => {
    expect(defaultForegroundAdaptation(stateWithAnalysis("hint"))).toEqual({ mode: "author-hint" });
  });

  it("uses fixed tones for arbitrary DOM", () => {
    expect(defaultForegroundAdaptation(stateWithAnalysis("none"))).toEqual({ mode: "fixed" });
  });

  it("never produces a default that its own resolver would downgrade", () => {
    for (const analysis of ["exact", "hint", "none"] as const) {
      const state = stateWithAnalysis(analysis);
      const resolved = resolveForegroundAdaptation(defaultForegroundAdaptation(state), state);
      expect(resolved.downgraded).toBeUndefined();
    }
  });
});
