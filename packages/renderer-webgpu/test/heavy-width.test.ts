/**
 * W26 G0 — the heavy tap as a parameter: the three candidates' shape, and that all
 * three are inert at their defaults (W26 Decision Log 1; the measured cause in
 * claims §5.116 §2).
 *
 * The spike lands three mechanisms and lands them off, so what this file pins is
 * what each of them is for and what none of them may reach:
 *
 *  1. **Inert at the defaults.** The level offset is one addition of zero to
 *     `scatterLod`, the second-level share one `mix` at zero, and the Gaussian
 *     tap's σ resolves to a plan whose enable is false — so the optics uniform's
 *     four new slots are zero and the pass takes the single `textureSampleLevel`
 *     the material has always taken. The pins here are on the arithmetic and on
 *     the uniform's bytes; the 33 renderer goldens and the bed's `rrect-sm` cells
 *     are the pin on the pixels.
 *  2. **The chain's own width is measured, not assumed.** `CHAIN_LEVEL_SIGMA` is
 *     the simulation's reading of `WGSL_DOWNSAMPLE_PASS` and is what
 *     `heavyTapPlan` subtracts in quadrature. It is deliberately NOT
 *     `CHAIN_SIGMA_AT_LEVEL_1`, which is 24 % narrower and says of itself that it
 *     is advisory — the body blur can absorb that and the heavy tap cannot,
 *     because the heavy tap's whole claim is that the σ it is given comes back out
 *     of reader A.
 *  3. **The plan is monotone and unbounded by `chainMaxLod`.** The whole point of
 *     candidate (ii) is that a target the chain is too short to reach is still
 *     drawn, because the residual Gaussian carries the octave the chain lacks —
 *     which is exactly what the clamp on `scatterLod` cannot do.
 *  4. **The residual never exceeds what the tap can integrate.** The level is the
 *     deepest at or below the target, so the residual is bounded in that level's
 *     own texels, and the shader's 9 × 9 grid at one-texel spacing is at least
 *     three of them in every direction.
 *
 * No fitted value is asserted anywhere here, on purpose: G0 measures the
 * mechanism and G1 fits the constant.
 */

import { describe, expect, it } from "vitest";

import {
  DEFAULT_MATERIAL_PROFILE,
  heavyTapSigmaAtScale,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "../src/material";
import {
  CHAIN_LEVEL_SIGMA,
  CHAIN_SIGMA_AT_LEVEL_1,
  chainLevelSigma,
  heavyTapPlan,
  planPyramid,
} from "../src/pyramid-plan";
import type { GroupRenderInput } from "../src/render-model";
import { createWebGPURenderer, type DrawFrameArgs } from "../src/renderer";
import { WGSL_OPTICS_PASS } from "../src/wgsl";
import { createGradientProvider, linearGradientStops } from "../src/backdrop";

import { createFakeGpu, type FakeGpu } from "./harness/fake-gpu";

const P = DEFAULT_MATERIAL_PROFILE;
/** The bed's own backdrop: a 320 × 200 raster, whose chain is five levels deep. */
const BED = planPyramid(320, 200, { scale: 1, maxDimension: 2048 });

describe("W26 the three candidates are inert at their defaults", () => {
  it("names all four constants at zero", () => {
    expect(P.sizeHeavyLevelOffset).toBe(0);
    expect(P.sizeHeavyTapSigma).toBe(0);
    expect(P.sizeHeavyTapSigma2x).toBe(0);
    expect(P.sizeHeavySecondShare).toBe(0);
  });

  it("resolves the tap σ to zero at every ratio, so no scale can switch it on", () => {
    for (const dpr of [0.5, 1, 1.5, 2, 3]) {
      expect(heavyTapSigmaAtScale(P, dpr)).toBe(0);
    }
  });

  it("plans nothing at σ 0 — level 0, no residual, no step", () => {
    const plan = heavyTapPlan(0, BED);
    expect(plan.level).toBe(0);
    expect(plan.residualSigmaTexels).toBe(0);
  });
});

describe("W26 the tap σ is a per-scale constant", () => {
  it("interpolates between its two anchors and holds outside them", () => {
    // The pattern `sizeScatterGainMax2x` established: the reference's heavy
    // component is a device-px quantity that halves between the scales, so one
    // number cannot serve both.
    const both = withMaterialOverrides(P, { sizeHeavyTapSigma: 20, sizeHeavyTapSigma2x: 12 });
    expect(heavyTapSigmaAtScale(both, 0.5)).toBeCloseTo(20, 12);
    expect(heavyTapSigmaAtScale(both, 1)).toBeCloseTo(20, 12);
    expect(heavyTapSigmaAtScale(both, 1.5)).toBeCloseTo(16, 12);
    expect(heavyTapSigmaAtScale(both, 2)).toBeCloseTo(12, 12);
    expect(heavyTapSigmaAtScale(both, 4)).toBeCloseTo(12, 12);
  });
});

describe("W26 the chain's own width, and the plan built on it", () => {
  it("is the measured table and not the advisory constant", () => {
    // Both exist on purpose and they are not interchangeable: the body blur's
    // residual pass absorbs whatever `CHAIN_SIGMA_AT_LEVEL_1` misses, and the
    // heavy tap has nothing to absorb it with.
    expect(chainLevelSigma(1)).toBeGreaterThan(CHAIN_SIGMA_AT_LEVEL_1 * 1.2);
    expect(chainLevelSigma(0)).toBe(0);
    for (let level = 1; level < CHAIN_LEVEL_SIGMA.length; level += 1) {
      expect(chainLevelSigma(level)).toBe(CHAIN_LEVEL_SIGMA[level]);
    }
    // Past the table, the doubling the table itself settles into.
    const last = CHAIN_LEVEL_SIGMA.length - 1;
    expect(chainLevelSigma(last + 2)).toBeCloseTo(
      (CHAIN_LEVEL_SIGMA[last] as number) * 4,
      12,
    );
  });

  it("takes the deepest level at or below the target, and never a deeper one", () => {
    for (const sigma of [0.5, 1.6, 3.5, 7, 14, 30, 120]) {
      const plan = heavyTapPlan(sigma, BED);
      expect(plan.level).toBeLessThanOrEqual(BED.maxLod);
      expect(chainLevelSigma(plan.level)).toBeLessThanOrEqual(sigma + 1e-12);
      if (plan.level < BED.maxLod) {
        expect(chainLevelSigma(plan.level + 1)).toBeGreaterThan(sigma);
      }
    }
  });

  it("reaches past `chainMaxLod` on the residual, which is what the clamp cannot do", () => {
    // The bed's chain stops at level 4, whose own width is about 13.4 texels. A
    // target of 30 is beyond every level the chain has; the plan still returns it,
    // by asking the Gaussian for the octave the pyramid is too short to supply.
    const beyond = heavyTapPlan(30, BED);
    expect(beyond.level).toBe(BED.maxLod);
    const total = Math.hypot(
      chainLevelSigma(beyond.level),
      beyond.residualSigmaTexels * Math.pow(2, beyond.level),
    );
    expect(total).toBeCloseTo(30, 6);
  });

  it("keeps the residual inside the grid the shader integrates it over", () => {
    // The shader's grid is 9 × 9 at one-texel spacing, so it reaches four texels
    // in every direction. While the chain still has a level to grow into, the
    // plan's rule bounds the residual at about 1.46 of the chosen level's texels,
    // which is 2.7 σ inside the grid — and renormalising the weights costs the
    // kernel no mass there.
    for (let sigma = 0.1; sigma < 200; sigma *= 1.07) {
      const plan = heavyTapPlan(sigma, BED);
      if (plan.level === BED.maxLod) continue;
      expect(plan.residualSigmaTexels).toBeLessThan(1.5);
    }
  });

  it("names its own ceiling: past twice the chain's last level the grid truncates", () => {
    // The honest limit of candidate (ii) on THIS bed. Level 4 is the last the
    // 320 × 200 chain has and is 13.4 texels wide, so a target up to about 26.8
    // still lands inside the grid; past that the residual leaves it and the tap
    // draws narrower than it was asked for. The wave's range is 10–25 device px
    // at dpr 1, which is inside — but a wider fit at G1 needs a deeper chain or a
    // wider grid, and the ceiling is stated here so that cannot be discovered by
    // a capture.
    const ceiling = 2 * chainLevelSigma(BED.maxLod);
    expect(heavyTapPlan(ceiling * 0.99, BED).residualSigmaTexels).toBeLessThan(1.5);
    expect(heavyTapPlan(ceiling * 2, BED).residualSigmaTexels).toBeGreaterThan(3);
  });

  it("is monotone in the target width", () => {
    let previous = -Infinity;
    for (let sigma = 0.5; sigma < 60; sigma += 0.25) {
      const plan = heavyTapPlan(sigma, BED);
      const total = Math.hypot(
        chainLevelSigma(plan.level),
        plan.residualSigmaTexels * Math.pow(2, plan.level),
      );
      expect(total).toBeGreaterThanOrEqual(previous - 1e-9);
      previous = total;
    }
  });

  it("states the step as one tap-level texel in uv, so the shader needs no extent", () => {
    const plan = heavyTapPlan(14, BED);
    expect(plan.stepUv[0]).toBeCloseTo(Math.pow(2, plan.level) / BED.width, 12);
    expect(plan.stepUv[1]).toBeCloseTo(Math.pow(2, plan.level) / BED.height, 12);
  });
});

/* The uniform's bytes are the claim, so they are read off the fake device. */

const VIEWPORT = { widthCss: 320, heightCss: 200, devicePixelRatio: 1 };

const GROUP: GroupRenderInput = {
  groupId: "g",
  surfaces: [
    {
      nodeId: "n",
      family: "fixed-rounded-rect",
      shape: {
        center: [160, 100],
        size: [160, 96],
        radii: [20, 20, 20, 20],
        smoothing: 0.5,
        thickness: 10,
      },
    },
  ],
  backdropSourceId: "bg",
  refraction: "true",
  analysisExact: true,
};

const view = () => ({}) as GPUTextureView;
const frameArgs = (id: number): DrawFrameArgs => ({
  frame: { id, timeMs: id * 16.7 },
  optics: view(),
  highlight: view(),
});

function opticsUniformWrites(gpu: FakeGpu): Float32Array[] {
  const writes: Float32Array[] = [];
  const queue = gpu.device.queue as unknown as { writeBuffer: (...args: unknown[]) => void };
  queue.writeBuffer = (buffer, _offset, data, dataOffset, size) => {
    if (!String((buffer as { label?: string }).label ?? "").includes("uniform:optics")) return;
    const view_ = new Float32Array(
      data as ArrayBuffer,
      Number(dataOffset ?? 0),
      Number(size ?? (data as ArrayBuffer).byteLength) / 4,
    );
    writes.push(Float32Array.from(view_));
  };
  return writes;
}

/** `heavyTap` lands at d[108..111] and `heavyStep` at d[112..115] (see `passes.ts`). */
function heavyOf(write: Float32Array) {
  return {
    levelOffset: write[108],
    residualSigmaTexels: write[109],
    tapLevel: write[110],
    secondShare: write[111],
    stepUv: [write[112], write[113]],
    enabled: write[114],
  };
}

function lastOpticsUniform(overrides?: MaterialProfilePatch) {
  const gpu = createFakeGpu();
  const writes = opticsUniformWrites(gpu);
  const renderer = createWebGPURenderer({
    viewport: VIEWPORT,
    ...(overrides === undefined ? {} : { materialProfile: overrides }),
  });
  renderer.attachDevice(gpu.device, "vitrea");
  renderer.setGroup(GROUP);
  renderer.registerBackdrop(
    createGradientProvider({
      id: "bg",
      device: gpu.device,
      stops: linearGradientStops([0, 0, 0], [1, 1, 1]),
      generation: 1,
      width: 320,
      height: 200,
    }),
  );
  renderer.drawFrame(frameArgs(1));
  const last = writes.at(-1);
  expect(last).toBeDefined();
  return heavyOf(last as Float32Array);
}

describe("W26 the slot plumbing", () => {
  it("writes eight zeros on the landed material", () => {
    const heavy = lastOpticsUniform();
    expect(heavy.levelOffset).toBe(0);
    expect(heavy.residualSigmaTexels).toBe(0);
    expect(heavy.tapLevel).toBe(0);
    expect(heavy.secondShare).toBe(0);
    expect(heavy.stepUv).toEqual([0, 0]);
    expect(heavy.enabled).toBe(0);
  });

  it("carries the level offset and the second-level share straight through", () => {
    const heavy = lastOpticsUniform({ sizeHeavyLevelOffset: -0.75, sizeHeavySecondShare: 0.3 });
    expect(heavy.levelOffset).toBeCloseTo(-0.75, 6);
    expect(heavy.secondShare).toBeCloseTo(0.3, 6);
    // Neither of them switches the Gaussian tap on: three candidates, three
    // constants, and a ladder rung moves exactly one.
    expect(heavy.enabled).toBe(0);
  });

  it("resolves the tap σ through the pyramid rather than passing it on", () => {
    // The shader is handed a level, a residual σ in that level's texels and a uv
    // step — never the profile's device-px σ, because only the pyramid knows the
    // source's texels per CSS px and the downscale the plan applied.
    const heavy = lastOpticsUniform({ sizeHeavyTapSigma: 20, sizeHeavyTapSigma2x: 20 });
    expect(heavy.enabled).toBe(1);
    const want = heavyTapPlan(20, BED);
    expect(heavy.tapLevel).toBe(want.level);
    expect(heavy.residualSigmaTexels).toBeCloseTo(want.residualSigmaTexels, 5);
    expect(heavy.stepUv[0]).toBeCloseTo(want.stepUv[0] as number, 6);
    expect(heavy.stepUv[1]).toBeCloseTo(want.stepUv[1] as number, 6);
  });
});

/*
 * The shader is where the per-pixel half of this lives, and there is no WGSL
 * compiler in a Node test — `e2e/gpu` compiles it on a real adapter. What can be
 * checked here is what the string must contain, in the spirit of
 * `wgsl-contract.test.ts`.
 */
describe("W26 the optics pass's statement of the tap", () => {
  it("carries both uniform slots the CPU writes", () => {
    expect(WGSL_OPTICS_PASS).toContain("heavyTap : vec4f");
    expect(WGSL_OPTICS_PASS).toContain("heavyStep : vec4f");
  });

  it("adds the level offset inside the same clamp the gain has always taken", () => {
    // Inside, not outside: the offset is a candidate for the width and not a way
    // around the chain's own last level, and a fractional level past `maxLod` is
    // a level the chain does not have.
    expect(WGSL_OPTICS_PASS).toContain(
      "let scatterLod = clamp(ou.size.w + log2(max(gainEff, 1e-4)) + ou.heavyTap.x, 0.0, ou.lens.w);",
    );
  });

  it("gates the Gaussian on its own enable and not on the residual σ", () => {
    // A target width that lands exactly on a chain level has residual σ 0 and is
    // still a width the profile asked for.
    expect(WGSL_OPTICS_PASS).toContain("if (ou.heavyStep.z > 0.5)");
    expect(WGSL_OPTICS_PASS).not.toContain("if (ou.heavyTap.y > 0.0)");
  });

  it("integrates a 9 x 9 grid and renormalises it", () => {
    expect(WGSL_OPTICS_PASS).toContain("for (var j = -4; j <= 4; j = j + 1)");
    expect(WGSL_OPTICS_PASS).toContain("for (var i = -4; i <= 4; i = i + 1)");
    // Renormalised rather than pre-weighted, so the truncation costs no mass and
    // the premultiplied alpha the tap averages stays the alpha the unpremultiply
    // below it divides by.
    expect(WGSL_OPTICS_PASS).toContain("scatterSample = acc / wsum;");
  });

  it("keeps the single tap as the path a default material takes", () => {
    expect(WGSL_OPTICS_PASS).toContain(
      "var scatterSample = textureSampleLevel(backdropChain, backdropSampler, refractedUv, scatterLod);",
    );
  });
});
