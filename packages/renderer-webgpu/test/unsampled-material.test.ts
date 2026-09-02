/**
 * W11a — the optics uniform a group with no pyramid is handed.
 *
 * The shader's unsampled path writes the material as a layer at `tint.w`; the
 * host resolves that alpha in the compositing space (`unsampledMaterial`) and
 * the renderer must put it, and only it, into the uniform — never the profile's
 * linear alpha, and never onto a group that samples a backdrop. Read off the
 * fake device's `writeBuffer`, since the uniform's bytes are the claim.
 */

import { describe, expect, it } from "vitest";

import { createGradientProvider, linearGradientStops } from "../src/backdrop";
import { DEFAULT_MATERIAL_PROFILE } from "../src/material";
import type { GroupRenderInput } from "../src/render-model";
import { createWebGPURenderer, type DrawFrameArgs } from "../src/renderer";

import { createFakeGpu, type FakeGpu } from "./harness/fake-gpu";

const VIEWPORT = { widthCss: 400, heightCss: 300, devicePixelRatio: 2 };

const surface = {
  nodeId: "n",
  family: "fixed-rounded-rect" as const,
  shape: { center: [200, 150] as [number, number], size: [160, 80] as [number, number], radii: [20, 20, 20, 20] as [number, number, number, number], smoothing: 0.5, thickness: 10 },
};

const frameArgs = (id: number): DrawFrameArgs => ({
  frame: { id, timeMs: id * 16.7 },
  optics: {} as GPUTextureView,
  highlight: {} as GPUTextureView,
});

/** Every float array written into the optics uniform, in write order. */
function opticsUniformWrites(gpu: FakeGpu): Float32Array[] {
  const writes: Float32Array[] = [];
  const queue = gpu.device.queue as unknown as { writeBuffer: (...args: unknown[]) => void };
  queue.writeBuffer = (buffer, _offset, data, dataOffset, size) => {
    if (!String((buffer as { label?: string }).label ?? "").includes("uniform:optics")) return;
    const view = new Float32Array(
      data as ArrayBuffer,
      Number(dataOffset ?? 0),
      Number(size ?? (data as ArrayBuffer).byteLength) / 4,
    );
    writes.push(Float32Array.from(view));
  };
  return writes;
}

const PAIR = { tint: [0.2, 0.4, 0.6] as const, tintAlpha: 0.66 };

/** `tint` lands at d[12..14] and `tintAlpha` at d[15] (see `passes.ts`). */
const tintOf = (write: Float32Array) => ({
  tint: [write[12], write[13], write[14]],
  tintAlpha: write[15],
});

describe("the unsampled layer pair reaches the optics uniform (W11a)", () => {
  it("replaces the profile's tint and alpha on a group with no backdrop", () => {
    const gpu = createFakeGpu();
    const writes = opticsUniformWrites(gpu);
    const renderer = createWebGPURenderer({ viewport: VIEWPORT });
    renderer.attachDevice(gpu.device, "vitrea");
    const group: GroupRenderInput = {
      groupId: "g",
      surfaces: [surface],
      refraction: "approximate",
      analysisExact: false,
      unsampledMaterial: PAIR,
    };
    renderer.setGroup(group);
    renderer.drawFrame(frameArgs(1));

    const last = writes.at(-1);
    expect(last).toBeDefined();
    if (last === undefined) return;
    const { tint, tintAlpha } = tintOf(last);
    expect(tint.map((v) => Number(v?.toFixed(5)))).toEqual([0.2, 0.4, 0.6]);
    expect(tintAlpha).toBeCloseTo(0.66, 5);
  });

  it("writes the profile's own pair where the host resolved none", () => {
    const gpu = createFakeGpu();
    const writes = opticsUniformWrites(gpu);
    const renderer = createWebGPURenderer({ viewport: VIEWPORT });
    renderer.attachDevice(gpu.device, "vitrea");
    renderer.setGroup({ groupId: "g", surfaces: [surface], refraction: "approximate", analysisExact: false });
    renderer.drawFrame(frameArgs(1));

    const last = writes.at(-1);
    expect(last).toBeDefined();
    if (last === undefined) return;
    expect(tintOf(last).tintAlpha).toBeCloseTo(DEFAULT_MATERIAL_PROFILE.optics.regular.tintAlpha, 5);
  });

  it("ignores the pair on a group that samples a backdrop", () => {
    const gpu = createFakeGpu();
    const writes = opticsUniformWrites(gpu);
    const renderer = createWebGPURenderer({ viewport: VIEWPORT });
    renderer.attachDevice(gpu.device, "vitrea");
    renderer.registerBackdrop(
      createGradientProvider({
        id: "bg",
        device: gpu.device,
        stops: linearGradientStops([0, 0, 0], [1, 1, 1]),
        generation: 1,
      }),
    );
    renderer.setGroup({
      groupId: "g",
      surfaces: [surface],
      backdropSourceId: "bg",
      refraction: "true",
      analysisExact: true,
      unsampledMaterial: PAIR,
    });
    renderer.drawFrame(frameArgs(1));

    const last = writes.at(-1);
    expect(last).toBeDefined();
    if (last === undefined) return;
    expect(tintOf(last).tintAlpha).toBeCloseTo(DEFAULT_MATERIAL_PROFILE.optics.regular.tintAlpha, 5);
  });
});
