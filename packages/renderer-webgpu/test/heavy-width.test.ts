/**
 * W26 — the heavy blur: one width in device px per scale, built into a texture of
 * its own by the pyramid's separable passes (W26 Decision Log 2; the measured
 * cause in claims §5.116 §2 and the mechanism in §5.119).
 *
 * G0 built three candidate taps and measured two of them **inert to the bit** at
 * dpr 1 — a fractional pyramid level and a blend of two levels both stop at
 * `chainMaxLod`, which is exactly where the gain already saturates — so G1 removed
 * them and built the third structurally. What this file pins:
 *
 *  1. **Inert at the default.** At σ 0 the pyramid allocates no heavy texture and
 *     encodes no heavy pass, the optics uniform's new slot is zero and the pass
 *     takes the single `textureSampleLevel` of the chain the material has always
 *     taken. The pins here are on the arithmetic, on the passes and on the
 *     uniform's bytes; the 33 renderer goldens and the bed's `rrect-sm` cells are
 *     the pin on the pixels.
 *  2. **The chain's own width is measured, not assumed.** `CHAIN_LEVEL_SIGMA` is
 *     the simulation's reading of `WGSL_DOWNSAMPLE_PASS` and is what
 *     `heavyTapPlan` subtracts in quadrature. It is deliberately NOT
 *     `CHAIN_SIGMA_AT_LEVEL_1`, which is 24 % narrower and says of itself that it
 *     is advisory — the body blur can absorb that and the heavy blur cannot,
 *     because its whole claim is that the σ it is given comes back out of reader A.
 *  3. **The plan is monotone and unbounded by `chainMaxLod`.** The whole point is
 *     that a target the chain is too short to reach is still drawn, because the
 *     residual Gaussian carries the octave the chain lacks — which is exactly what
 *     the clamp on `scatterLod` cannot do.
 *  4. **The residual never exceeds what the blur can integrate.** The level is the
 *     deepest at or below the target, so the residual is bounded in that level's
 *     own texels, and `fs_blur`'s nine taps at one-texel spacing reach four of
 *     them in every direction.
 *  5. **The structure is the pyramid's, not the fragment shader's.** The heavy
 *     texture is built once per source per frame beside the body, at the extent of
 *     the level it was blurred from, and the optics pass reads it once. That is
 *     what makes it 0.070 ms rather than the +1.1 ms G0 measured for a 9 × 9 grid
 *     at the tap, and it is also what makes the width one per source.
 *
 * No fitted value is asserted anywhere here, on purpose: the constants are fitted
 * on captures and declared in the profile documents.
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

describe("W26 the heavy blur is inert at its default", () => {
  it("names both constants at zero", () => {
    expect(P.sizeHeavyTapSigma).toBe(0);
    expect(P.sizeHeavyTapSigma2x).toBe(0);
  });

  it("resolves the tap σ to zero at every ratio, so no scale can switch it on", () => {
    for (const dpr of [0.5, 1, 1.5, 2, 3]) {
      expect(heavyTapSigmaAtScale(P, dpr)).toBe(0);
    }
  });

  it("plans nothing at σ 0 — level 0, no residual", () => {
    const plan = heavyTapPlan(0, BED);
    expect(plan.level).toBe(0);
    expect(plan.residualSigmaTexels).toBe(0);
  });
});

describe("W26 the heavy σ is a per-scale constant", () => {
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
    // `fs_blur` is nine taps at one-texel spacing, so it reaches four texels in
    // every direction. While the chain still has a level to grow into, the
    // plan's rule bounds the residual at about 1.46 of the chosen level's texels,
    // which is 2.7 σ inside the kernel — and renormalising the weights costs it
    // no mass there.
    for (let sigma = 0.1; sigma < 200; sigma *= 1.07) {
      const plan = heavyTapPlan(sigma, BED);
      if (plan.level === BED.maxLod) continue;
      expect(plan.residualSigmaTexels).toBeLessThan(1.5);
    }
  });

  it("names its own ceiling: past twice the chain's last level the kernel truncates", () => {
    // The honest limit of candidate (ii) on THIS bed. Level 4 is the last the
    // 320 × 200 chain has and is 13.4 texels wide, so a target up to about 26.8
    // still lands inside the kernel; past that the residual leaves it and the
    // blur draws narrower than it was asked for. The wave's range is 10–25 device
    // px at dpr 1, which is inside — but a wider fit needs a deeper chain or a
    // wider kernel, and the ceiling is stated here so that cannot be discovered
    // by a capture.
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

  it("lands the target width on the chain's own level where the chain has one", () => {
    // The rule is `bodyBlurPlan`'s: the deepest level at or below the target, so a
    // target that IS a chain level costs no residual pass width at all and a
    // target between two levels is carried the rest of the way by the Gaussian.
    const exact = heavyTapPlan(chainLevelSigma(3), BED);
    expect(exact.level).toBe(3);
    expect(exact.residualSigmaTexels).toBeCloseTo(0, 9);
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

/** The heavy blur's enable lands at d[108] (`heavyTap.x`; see `passes.ts`). */
const heavyEnabledOf = (write: Float32Array): number => write[108] as number;

function drawOnce(overrides?: MaterialProfilePatch) {
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
  return { gpu, write: last as Float32Array };
}

describe("W26 the slot plumbing", () => {
  it("writes the enable at zero on the landed material", () => {
    expect(heavyEnabledOf(drawOnce().write)).toBe(0);
  });

  it("switches the enable on when the profile names a width", () => {
    // The uniform carries the enable and nothing else: the width itself is
    // already in the texture, so the shader's only decision is which texture the
    // deep sample comes from.
    const { write } = drawOnce({ sizeHeavyTapSigma: 20, sizeHeavyTapSigma2x: 20 });
    expect(heavyEnabledOf(write)).toBe(1);
  });
});

describe("W26 the heavy blur is the pyramid's, not the fragment shader's", () => {
  const blurPasses = (gpu: FakeGpu, kind: string): readonly string[] =>
    gpu.passes.filter((pass) => pass.label.includes(`:${kind}-blur-`)).map((pass) => pass.label);

  it("encodes no heavy pass and allocates no heavy texture at σ 0", () => {
    // What makes the mechanism free where it is declined, and what the goldens'
    // byte-identity rests on: not a pass that writes the same pixels, but no pass.
    const { gpu } = drawOnce();
    expect(blurPasses(gpu, "body")).toHaveLength(2);
    expect(blurPasses(gpu, "heavy")).toHaveLength(0);
    expect(gpu.textures.filter((t) => t.label.endsWith(":heavy"))).toHaveLength(0);
  });

  it("encodes the same two separable passes as the body when a width is named", () => {
    // Two passes per source per frame — the structure G0 measured at 0.070 ms
    // against +1.1 ms for a 9 × 9 grid per covered pixel (W26 Decision Log 2 (b)).
    const { gpu } = drawOnce({ sizeHeavyTapSigma: 20, sizeHeavyTapSigma2x: 20 });
    expect(blurPasses(gpu, "heavy")).toHaveLength(2);
  });

  it("sizes the heavy texture at the extent of the level it was blurred from", () => {
    // The body's rule, and the reason the width costs one texture rather than a
    // full-resolution one: level 4 of the bed's chain is 20 × 12.
    const { gpu } = drawOnce({ sizeHeavyTapSigma: 20, sizeHeavyTapSigma2x: 20 });
    const level = heavyTapPlan(20, BED).level;
    const want = BED.levels[level] as { width: number; height: number };
    const heavy = gpu.textures.filter((t) => t.label.endsWith(":heavy"));
    expect(heavy).toHaveLength(1);
    expect([heavy[0]?.width, heavy[0]?.height]).toEqual([want.width, want.height]);
  });
});

/*
 * The shader is where the per-pixel half of this lives, and there is no WGSL
 * compiler in a Node test — `e2e/gpu` compiles it on a real adapter. What can be
 * checked here is what the string must contain, in the spirit of
 * `wgsl-contract.test.ts`.
 */
describe("W26 the optics pass's statement of the heavy blur", () => {
  it("carries the uniform slot and the texture binding the CPU writes", () => {
    expect(WGSL_OPTICS_PASS).toContain("heavyTap : vec4f");
    expect(WGSL_OPTICS_PASS).toContain("@group(0) @binding(8) var backdropHeavy : texture_2d<f32>");
  });

  it("leaves the gain's clamp exactly as the material has always taken it", () => {
    // G0's level offset came out again: it could not widen anything at dpr 1,
    // because there is no level past `ou.lens.w` to interpolate toward (W26
    // Decision Log 2 (a)).
    expect(WGSL_OPTICS_PASS).toContain(
      "let scatterLod = clamp(ou.size.w + log2(max(gainEff, 1e-4)), 0.0, ou.lens.w);",
    );
    expect(WGSL_OPTICS_PASS).not.toContain("heavyStep");
  });

  it("replaces the deep sample with one read of the heavy texture", () => {
    expect(WGSL_OPTICS_PASS).toContain("if (ou.heavyTap.x > 0.5)");
    expect(WGSL_OPTICS_PASS).toContain(
      "scatterSample = textureSampleLevel(backdropHeavy, backdropSampler, refractedUv, 0.0);",
    );
    // One read, not a grid: the width is in the texture.
    expect(WGSL_OPTICS_PASS).not.toContain("for (var j = -4; j <= 4; j = j + 1)");
  });

  it("keeps the single chain tap as the path a default material takes", () => {
    expect(WGSL_OPTICS_PASS).toContain(
      "var scatterSample = textureSampleLevel(backdropChain, backdropSampler, refractedUv, scatterLod);",
    );
  });
});
