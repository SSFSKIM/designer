/**
 * W22 — the specular sweep gated on the shimmer running.
 *
 * The band is a Gaussian in the rim's angular coordinate centred at the `sweep`
 * channel, and that coordinate covers the whole contour: 0 radians is the LEFT
 * edge, not nowhere. So the idle phase drew a stationary band of gain
 * `sweepGain` on the left of every resting surface, in both colour schemes,
 * since the pass landed — isolated on the dark bed at 0.12–0.15 of luminance
 * above the other three sides (claims §5.90 §4). The gate is an amplitude:
 * `shimmer`, 0 at `IDLE_CHANNELS`, multiplied into the gain the CPU packs.
 *
 * What is pinned here is the uniform's own bytes, read off the fake device's
 * `writeBuffer` the way `unsampled-material.test.ts` reads the optics uniform:
 * the claim is a number in a buffer, and a test on `material.sweepGain` would
 * restate the profile rather than the pass. The press glow shares the uniform
 * and is asserted beside it, because the wave's clause is that the sweep alone
 * went.
 */

import { describe, expect, it } from "vitest";

import { DEFAULT_MATERIAL_PROFILE } from "../src/material";
import { IDLE_CHANNELS, type GroupRenderInput, type SurfaceChannels } from "../src/render-model";
import { createWebGPURenderer, type DrawFrameArgs } from "../src/renderer";

import { createFakeGpu, type FakeGpu } from "./harness/fake-gpu";

const VIEWPORT = { widthCss: 400, heightCss: 300, devicePixelRatio: 2 };

const surface = (channels: SurfaceChannels) => ({
  nodeId: "n",
  family: "fixed-rounded-rect" as const,
  shape: {
    center: [200, 150] as [number, number],
    size: [160, 80] as [number, number],
    radii: [20, 20, 20, 20] as [number, number, number, number],
    smoothing: 0.5,
    thickness: 10,
  },
  channels,
});

const frameArgs = (id: number): DrawFrameArgs => ({
  frame: { id, timeMs: id * 16.7 },
  optics: {} as GPUTextureView,
  highlight: {} as GPUTextureView,
});

/** Every float array written into the highlight uniform, in write order. */
function highlightUniformWrites(gpu: FakeGpu): Float32Array[] {
  const writes: Float32Array[] = [];
  const queue = gpu.device.queue as unknown as { writeBuffer: (...args: unknown[]) => void };
  queue.writeBuffer = (buffer, _offset, data, dataOffset, size) => {
    if (!String((buffer as { label?: string }).label ?? "").includes("uniform:highlight")) return;
    const view = new Float32Array(
      data as ArrayBuffer,
      Number(dataOffset ?? 0),
      Number(size ?? (data as ArrayBuffer).byteLength) / 4,
    );
    writes.push(Float32Array.from(view));
  };
  return writes;
}

/** `sweep` lands at d[4], the band width at d[5], the gain at d[6] (`passes.ts`). */
const sweepOf = (write: Float32Array) => ({
  phase: write[4],
  bandRadians: write[5],
  gain: write[6],
  glowGain: write[11],
});

function lastHighlightUniform(channels: SurfaceChannels): ReturnType<typeof sweepOf> {
  const gpu = createFakeGpu();
  const writes = highlightUniformWrites(gpu);
  const renderer = createWebGPURenderer({ viewport: VIEWPORT });
  renderer.attachDevice(gpu.device, "vitrea");
  const group: GroupRenderInput = {
    groupId: "g",
    surfaces: [surface(channels)],
    refraction: "approximate",
    analysisExact: false,
  };
  renderer.setGroup(group);
  renderer.drawFrame(frameArgs(1));
  const last = writes.at(-1);
  expect(last).toBeDefined();
  return sweepOf(last as Float32Array);
}

describe("the highlight pass's sweep gain is the shimmer's amplitude (W22)", () => {
  it("packs gain 0 for a surface at IDLE_CHANNELS", () => {
    const uniform = lastHighlightUniform(IDLE_CHANNELS);
    expect(uniform.gain).toBe(0);
    // Exactly zero rather than small: the shader multiplies the band by this, so
    // zero is the whole term gone and nothing is written on the rim.
    expect(uniform.phase).toBe(0);
    // And the press glow is untouched by the gate — the profile's gain reaches
    // the uniform whatever the shimmer does.
    expect(uniform.glowGain).toBeCloseTo(DEFAULT_MATERIAL_PROFILE.glowGain, 6);
  });

  it("packs sweepGain x shimmer for a driven surface, at the driven phase", () => {
    const uniform = lastHighlightUniform({ ...IDLE_CHANNELS, sweep: 0.15, shimmer: 1 });
    expect(uniform.gain).toBeCloseTo(DEFAULT_MATERIAL_PROFILE.sweepGain, 6);
    expect(uniform.phase).toBeCloseTo(0.15, 6);
    expect(uniform.bandRadians).toBeCloseTo(DEFAULT_MATERIAL_PROFILE.sweepBandRadians, 6);
  });

  it("is linear in the amplitude, so a driver can fade the band in", () => {
    const half = lastHighlightUniform({ ...IDLE_CHANNELS, sweep: 0.5, shimmer: 0.5 });
    expect(half.gain).toBeCloseTo(DEFAULT_MATERIAL_PROFILE.sweepGain * 0.5, 6);
  });
});
