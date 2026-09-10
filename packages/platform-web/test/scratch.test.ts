import { describe, it } from "vitest";
import { resolveAccessibilityPolicy, NOMINAL_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";
import { samplingPaddingFor, resolveProxyGeometry } from "../src/index";

describe("scratch", () => {
  it("prints numbers", () => {
    const nominalMaterial = NOMINAL_ACCESSIBILITY_POLICY.material;
    const reducedMaterial = resolveAccessibilityPolicy(
      { reducedTransparency: true, reducedMotion: false, increasedContrast: false, forcedColors: false, reducedTransparencySupported: true },
      {},
    ).material;

    const box = [420, 52] as const;

    for (const material of [
      { name: "nominal", m: nominalMaterial },
      { name: "reducedTransparency", m: reducedMaterial },
    ]) {
      const regular = samplingPaddingFor({ members: [box], material: material.m });
      const clear = samplingPaddingFor({ members: [box], material: material.m, variant: "clear" });
      console.log(material.name, "regular padding", regular, "clear padding", clear);

      // toolbar-level groupProps has no variant declared -> gap uses "regular"
      const gapToolbarWouldOpen = Math.max(24, regular);
      console.log(material.name, "gap toolbar opens (ignores hidden-item's own variant=clear)", gapToolbarWouldOpen);

      // Now show real overlap: hidden item's own group is variant "clear", authored samplingPadding undefined
      // so resolveSamplingGeometry would default its samplingPadding to requiredSamplingPadding(blurRadius for clear)
      // simulate what root.ts would feed resolveProxyGeometry for the "clear" partition:
      const clearFloor = clear; // samplingPaddingFor already applies 3-sigma via requiredSamplingPadding
      console.log(material.name, "clear partition's own required floor", clearFloor, "vs gap", gapToolbarWouldOpen, "OVERLAP RISK:", clearFloor > gapToolbarWouldOpen);
    }
  });
});
