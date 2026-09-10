import { describe, it } from "vitest";
import { samplingPaddingFor, resolveProxyGeometry } from "../src/index";
import { NOMINAL_ACCESSIBILITY_POLICY, REDUCED_TRANSPARENCY_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";

describe("scratch", () => {
  it("prints numbers", () => {
    const material = NOMINAL_ACCESSIBILITY_POLICY.material;
    const box = [420, 52] as const;

    const regular = samplingPaddingFor({ members: [box], material });
    const clear = samplingPaddingFor({ members: [box], material, variant: "clear" });
    console.log("regular padding", regular);
    console.log("clear padding", clear);

    const gapUsedByToolbar = Math.max(24, regular); // groupProps.variant undefined at toolbar level
    console.log("gap toolbar would open (regular default)", gapUsedByToolbar);
    console.log("actual clear-variant partition needs >=", clear);
  });
});
