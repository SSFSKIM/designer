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
 *  1. **Inert where a material declines it.** At σ 0 the pyramid allocates no
 *     heavy texture and encodes no heavy pass, the optics uniform's new slot is
 *     zero and the pass takes the single `textureSampleLevel` of the chain the
 *     material has always taken. The pins here are on the arithmetic, on the
 *     passes and on the uniform's bytes. **The landed default is no longer that
 *     material** — W26 G2 declared 9 device px at both anchors (claims §5.122) —
 *     so the cases below name the declining profile explicitly, and what pins the
 *     landed width on the pixels is the isolation proof's `W26_HASHES` and the
 *     bed.
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

/**
 * The material that DECLINES the mechanism, which is what these cases were written
 * against when the landed default was still 0 (W26 G1). Since G2's declaration the
 * default names 9 at both anchors, so "inert" is a property of a profile rather
 * than of the shipped material, and the cases below say which profile. What they
 * assert has not changed: at exactly 0 there is no texture, no pass and no
 * uniform, and that is what makes the mechanism free where it is not asked for.
 */
const DECLINED = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
  sizeHeavyTapSigma: 0,
  sizeHeavyTapSigma2x: 0,
});
const DECLINE: MaterialProfilePatch = { sizeHeavyTapSigma: 0, sizeHeavyTapSigma2x: 0 };

describe("W26 the heavy blur is inert where a material declines it", () => {
  it("names the fitted width at both anchors on the landed material", () => {
    // W26 G2's declaration (claims §5.122 §4): 9 device px at both scales, fitted
    // on the family reader against a control. The two anchors are equal by
    // measurement rather than by construction — the reference asks 9.48 / 8.63 /
    // 9.19 at dpr 1 and 8.13 / 9.79 / 8.37 at dpr 2 — so this pins the values and
    // the case below pins that the ramp still has two ends.
    expect(P.sizeHeavyTapSigma).toBe(9);
    expect(P.sizeHeavyTapSigma2x).toBe(9);
  });

  it("resolves the tap σ to zero at every ratio where both anchors are 0", () => {
    for (const dpr of [0.5, 1, 1.5, 2, 3]) {
      expect(heavyTapSigmaAtScale(DECLINED, dpr)).toBe(0);
    }
  });

  it("resolves the landed width at every ratio, since both anchors carry it", () => {
    for (const dpr of [0.5, 1, 1.5, 2, 3]) {
      expect(heavyTapSigmaAtScale(P, dpr)).toBeCloseTo(9, 12);
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

/**
 * A renderer with one group over one gradient source, drawn once.
 *
 * `size` is the SOURCE's, not the viewport's: the leak below is a per-source
 * allocation and the review's scenario states it at 1024², where the heavy
 * texture and its scratch are 16 MiB of rgba16float apiece.
 */
function harness(overrides?: MaterialProfilePatch, size = 320) {
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
      width: size,
      height: size === 320 ? 200 : size,
    }),
  );
  return { gpu, renderer, writes };
}

function drawOnce(overrides?: MaterialProfilePatch) {
  const { gpu, renderer, writes } = harness(overrides);
  renderer.drawFrame(frameArgs(1));
  const last = writes.at(-1);
  expect(last).toBeDefined();
  return { gpu, write: last as Float32Array };
}

/** Every heavy texture the fake device ever made for the source, and whether it is still alive. */
const heavyTextures = (gpu: FakeGpu) =>
  gpu.textures.filter((t) => t.label.endsWith(":heavy") || t.label.endsWith(":heavy-scratch"));

describe("W26 the heavy blur is given back when the material stops asking for it", () => {
  it("releases the heavy texture AND its scratch when the width returns to 0", () => {
    // The review's scenario, and the leak it found: dropping `heavy` from the
    // record leaves the pool holding both allocations, which nothing will bind
    // and only `forget` would reclaim — 16 MiB of rgba16float each on a 1024²
    // source, held until the source is unregistered.
    const { gpu, renderer } = harness({ sizeHeavyTapSigma: 1, sizeHeavyTapSigma2x: 1 }, 1024);
    renderer.drawFrame(frameArgs(1));
    const built = heavyTextures(gpu);
    expect(built.length).toBe(2);
    expect(built.every((t) => !t.destroyed)).toBe(true);

    renderer.setMaterialProfile(DECLINE);
    renderer.drawFrame(frameArgs(2));
    expect(
      heavyTextures(gpu).filter((t) => !t.destroyed),
      "the heavy texture and its scratch are still held after the width returned to 0",
    ).toEqual([]);
  });

  it("rebuilds a source whose width was a hair above 0, rather than calling it unchanged", () => {
    // The tolerance comparison's blind spot: `same` is relative, so around zero it
    // is an absolute tolerance of 1e-6 and it calls σ 1e-7 and σ 0 equal. They are
    // not — at 1e-7 the plan resolves to level 0 with no residual, an unsampled
    // copy of the backdrop, which is the FURTHEST thing from the chain tap σ 0
    // means. A clean source would have kept it and the pass would have kept
    // reading it.
    const { gpu, renderer, writes } = harness({
      sizeHeavyTapSigma: 1e-7,
      sizeHeavyTapSigma2x: 1e-7,
    });
    renderer.drawFrame(frameArgs(1));
    expect(heavyEnabledOf(writes.at(-1) as Float32Array)).toBe(1);
    expect(heavyTextures(gpu).filter((t) => !t.destroyed).length).toBe(2);

    renderer.setMaterialProfile(DECLINE);
    renderer.drawFrame(frameArgs(2));
    expect(
      heavyEnabledOf(writes.at(-1) as Float32Array),
      "the optics pass is still bound to a heavy texture the material stopped asking for",
    ).toBe(0);
    expect(heavyTextures(gpu).filter((t) => !t.destroyed)).toEqual([]);
  });
});

describe("W26 the slot plumbing", () => {
  it("writes the enable at zero where the material declines the width", () => {
    expect(heavyEnabledOf(drawOnce(DECLINE).write)).toBe(0);
  });

  it("writes the enable at one on the landed material, which names a width", () => {
    expect(heavyEnabledOf(drawOnce().write)).toBe(1);
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
    const { gpu } = drawOnce(DECLINE);
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
