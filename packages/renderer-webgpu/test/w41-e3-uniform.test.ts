/** W41: the real renderer must pack E3 only in its measured execution domain. */
import { describe, expect, it } from "vitest";
import { createGradientProvider, linearGradientStops } from "../src/backdrop";
import { NOMINAL_MATERIAL_POLICY, type MaterialPolicyView, type MaterialProfilePatch } from "../src/material";
import type { GroupRenderInput } from "../src/render-model";
import { createWebGPURenderer } from "../src/renderer";
import { createFakeGpu } from "./harness/fake-gpu";

const patch: MaterialProfilePatch = {
  bodyE3Strength: 1,
  bodyE3Gains: [0.929205829365914, 0.9597570955316058, 0.9383102545096953],
  bodyE3Neutral: [150, 157, 164, 171, 178, 188, 197],
};
const surface = {
  nodeId: "s", family: "fixed-rounded-rect" as const,
  shape: { center: [100, 70] as [number, number], size: [120, 44] as [number, number],
    radii: [22, 22, 22, 22] as [number, number, number, number], smoothing: 0, thickness: 8 },
};

function draw(over: {
  patch?: MaterialProfilePatch; sampled?: boolean; dom?: boolean;
  policy?: MaterialPolicyView; variant?: "regular" | "clear";
} = {}): Float32Array {
  const gpu = createFakeGpu();
  const renderer = createWebGPURenderer({ viewport: {
    widthCss: 240, heightCss: 160, devicePixelRatio: 1,
  } });
  renderer.attachDevice(gpu.device, "vitrea");
  renderer.setMaterialProfile(over.patch ?? patch);
  renderer.setAccessibility(over.policy ?? NOMINAL_MATERIAL_POLICY);
  if (over.sampled !== false) {
    renderer.registerBackdrop(createGradientProvider({ id: "bg", device: gpu.device,
      stops: linearGradientStops([0.1, 0.2, 0.3], [0.5, 0.6, 0.7]), generation: 1 }));
  }
  const group: GroupRenderInput = {
    groupId: "g", surfaces: [surface], refraction: "true", analysisExact: true,
    variant: over.variant ?? "regular",
    ...(over.sampled === false ? {} : { backdropSourceId: "bg" }),
    ...(over.dom ? { unsampledMaterial: {
      referenceBackdropLuminance: 0.2, minimumTintContrast: 0.001,
    } } : {}),
  };
  renderer.setGroup(group);
  renderer.drawFrame({ frame: { id: 1, timeMs: 1 }, optics: {} as GPUTextureView,
    highlight: {} as GPUTextureView });
  const writes = gpu.uniformWrites.filter(w => w.label.includes("uniform:optics"));
  expect(writes).toHaveLength(1);
  const data = writes[0]!.data;
  renderer.destroy();
  return data;
}

describe("W41 E3 optics packing", () => {
  it("appends the complete 3+7 tuple block without borrowing old lanes", () => {
    const on = draw();
    expect([...on.slice(140, 152)]).toEqual([...new Float32Array([
      1, 0.929205829365914, 0.9597570955316058, 0.9383102545096953,
      150, 157, 164, 171, 178, 188, 197, 0,
    ])]);
    const off = draw({ patch: { ...patch, bodyE3Strength: 0 } });
    expect([...off.slice(0, 140)]).toEqual([...on.slice(0, 140)]);
    expect(off[140]).toBe(0);
  });

  it("keeps every shipped-default old lane and uses an identity gate", () => {
    const original = draw({ patch: {} });
    const modifiedBacking = draw({ patch: { bodyE3Strength: 0,
      bodyE3Gains: [0, 2, 3], bodyE3Neutral: [3, 40, 79, 110, 142, 220, 254],
    } });
    expect(original[140]).toBe(0);
    expect(modifiedBacking[140]).toBe(0);
    expect([...original.slice(0, 140)]).toEqual([...modifiedBacking.slice(0, 140)]);
    expect([...original.slice(141, 151)]).not.toEqual([...modifiedBacking.slice(141, 151)]);
  });

  it.each([
    ["RT", { ...NOMINAL_MATERIAL_POLICY, frost: "increased", refraction: "reduced", occlusion: "increased" }],
    ["IC-only", { ...NOMINAL_MATERIAL_POLICY, border: "strong", ambientTint: "reduced", foreground: "near-monochrome" }],
    ["coupled", { ...NOMINAL_MATERIAL_POLICY, frost: "increased", refraction: "reduced", occlusion: "increased", border: "strong", ambientTint: "reduced", foreground: "near-monochrome" }],
  ] as const)("stands down under %s without changing its policy fold", (_name, policy) => {
    const on = draw({ policy });
    const off = draw({ policy, patch: {} });
    expect(on[140]).toBe(0);
    expect([...on.slice(0, 140)]).toEqual([...off.slice(0, 140)]);
  });

  it("stands down for clear, absent texture, and fabricated DOM material", () => {
    for (const over of [{ variant: "clear" as const }, { sampled: false },
      { sampled: false, dom: true }]) {
      expect(draw(over)[140]).toBe(0);
    }
    expect(draw()[140]).toBe(1);
  });
});
