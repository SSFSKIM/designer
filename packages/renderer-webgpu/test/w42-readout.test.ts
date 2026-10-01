/**
 * W42 G2 step 3, U6 — the WebGPU tier's law readout (`GlassRenderer.bodyLawReadout`, which the
 * platform folds onto `GlassGroupState.bodyLaw`; `implementation-design.md` §5, "The readout").
 *
 * The readout is written where the fold is, in `drawGroups`, so it says what the frame did rather
 * than what the document asked: `drawn` where the stage built A and the optics pass was handed the
 * law, `stood-down` where the material asks and the fold or the frame said no, and nothing at all
 * where the material asks for no law. It is kept per plane: a plane the group has no member on
 * retires its part, the read folds the rest with the weaker answer winning, and a group with no
 * plane left is stood down.
 */

import { describe, expect, it } from "vitest";

import { createGradientProvider, linearGradientStops } from "../src/backdrop";
import {
  NOMINAL_MATERIAL_POLICY,
  type MaterialPolicyView,
  type MaterialProfilePatch,
} from "../src/material";
import type { GroupRenderInput } from "../src/render-model";
import { createWebGPURenderer, type GlassRenderer } from "../src/renderer";
import { createFakeGpu } from "./harness/fake-gpu";

const LAW: MaterialProfilePatch = { bodyLawStrength: 1, bodyLawWidthUnit: 1, bodyLawEncodedAveraging: 1 };

const SURFACE = {
  nodeId: "s", family: "fixed-rounded-rect" as const,
  shape: { center: [120, 80] as [number, number], size: [160, 96] as [number, number],
    radii: [20, 20, 20, 20] as [number, number, number, number], smoothing: 0, thickness: 8 },
};

function drawn(over: {
  patch?: MaterialProfilePatch; sampled?: boolean; policy?: MaterialPolicyView;
  variant?: "regular" | "clear"; centre?: [number, number];
} = {}): GlassRenderer {
  const gpu = createFakeGpu();
  const renderer = createWebGPURenderer({ viewport: { widthCss: 240, heightCss: 160,
    devicePixelRatio: 1 } });
  renderer.attachDevice(gpu.device, "vitrea");
  renderer.setMaterialProfile(over.patch ?? LAW);
  renderer.setAccessibility(over.policy ?? NOMINAL_MATERIAL_POLICY);
  if (over.sampled !== false) {
    renderer.registerBackdrop(createGradientProvider({ id: "bg", device: gpu.device,
      stops: linearGradientStops([0.1, 0.2, 0.3], [0.5, 0.6, 0.7]), generation: 1 }));
  }
  const group: GroupRenderInput = {
    groupId: "g",
    surfaces: [{ ...SURFACE, shape: { ...SURFACE.shape, center: over.centre ?? [120, 80] } }],
    refraction: "true", analysisExact: true, variant: over.variant ?? "regular",
    ...(over.sampled === false ? {} : { backdropSourceId: "bg" }),
  };
  renderer.setGroup(group);
  renderer.drawFrame({ frame: { id: 1, timeMs: 16 }, optics: {} as GPUTextureView });
  return renderer;
}

describe("W42 U6: the WebGPU tier's law readout", () => {
  it("reports nothing where the material asks for no law", () => {
    const renderer = drawn({ patch: {} });
    expect(renderer.bodyLawReadout("g")).toBeUndefined();
    renderer.destroy();
  });

  it("reports drawn where the stage ran, and nothing for a group it never drew", () => {
    const renderer = drawn();
    expect(renderer.bodyLawReadout("g")).toBe("drawn");
    expect(renderer.bodyLawReadout("elsewhere")).toBeUndefined();
    renderer.destroy();
  });

  it.each([
    ["Reduce Transparency", { policy: { ...NOMINAL_MATERIAL_POLICY, frost: "increased",
      refraction: "reduced", occlusion: "increased" } as MaterialPolicyView }],
    ["forced colours", { policy: { ...NOMINAL_MATERIAL_POLICY, occlusion: "opaque" } as
      MaterialPolicyView }],
    ["the clear variant", { variant: "clear" as const }],
    ["an unsampled group", { sampled: false }],
    ["a group entirely off the canvas", { centre: [2000, 2000] as [number, number] }],
  ])("reports stood-down under %s", (_name, over) => {
    const renderer = drawn(over);
    expect(renderer.bodyLawReadout("g")).toBe("stood-down");
    renderer.destroy();
  });

  it("retires a plane the group has left, and a group with no member anywhere stood down", () => {
    const renderer = drawn();
    const group = (surfaces: GroupRenderInput["surfaces"]): GroupRenderInput => ({
      groupId: "g", surfaces, refraction: "true", analysisExact: true, variant: "regular",
      backdropSourceId: "bg",
    });
    const draw = (id: number, plane: string) => renderer.drawFrame({
      frame: { id, timeMs: id * 16 }, optics: {} as GPUTextureView, plane });
    expect(renderer.bodyLawReadout("g")).toBe("drawn");
    // An overlay plane the group has no member on contributes nothing to retire.
    renderer.setGroup(group([]));
    draw(2, "overlay");
    expect(renderer.bodyLawReadout("g")).toBe("drawn");
    // The base plane's members leave too: the law draws nothing of the group.
    draw(3, "");
    expect(renderer.bodyLawReadout("g")).toBe("stood-down");
    // And drawing it again on either plane reports what that frame did.
    renderer.setGroup(group([SURFACE]));
    draw(4, "overlay");
    expect(renderer.bodyLawReadout("g")).toBe("drawn");
    renderer.destroy();
    expect(renderer.bodyLawReadout("g")).toBeUndefined();
  });

  it("stops reporting as soon as the material stops asking, and forgets a removed group", () => {
    const renderer = drawn();
    renderer.setMaterialProfile({ ...LAW, bodyLawStrength: 0 });
    expect(renderer.bodyLawReadout("g")).toBeUndefined();
    renderer.setMaterialProfile(LAW);
    expect(renderer.bodyLawReadout("g")).toBe("drawn");
    renderer.removeGroup("g");
    expect(renderer.bodyLawReadout("g")).toBeUndefined();
    renderer.destroy();
  });
});
