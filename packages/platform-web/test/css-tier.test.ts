import { NOMINAL_ACCESSIBILITY_POLICY, resolveAccessibilityPolicy } from "@vitrea/core";
import { describe, expect, it } from "vitest";

import { cssTierDeclarations, CSS_TIER_TOKENS } from "../src/css-tier";
import { MATERIAL_OPTICS } from "../src/optics";

const surface = {
  radii: [22, 22, 22, 22] as const,
  optics: MATERIAL_OPTICS.regular,
  policy: NOMINAL_ACCESSIBILITY_POLICY,
};

const systemWith = (flags: Record<string, boolean>) => ({
  reducedTransparency: false,
  reducedMotion: false,
  increasedContrast: false,
  forcedColors: false,
  reducedTransparencySupported: true,
  ...flags,
});

describe("the CSS tier (the fallback is the design)", () => {
  it("always paints a real tint and a real border, never relying on the blur", () => {
    // S1: no probe can catch "the engine renders nothing", so a *missed*
    // demotion must be a fidelity loss and not a broken UI. A surface whose
    // filter silently no-ops still has to read as a legible surface.
    const declarations = cssTierDeclarations(surface);

    expect(declarations.background).toBeTruthy();
    expect(declarations["border-color"]).toBeTruthy();
    expect(declarations["border-width"]).toBeTruthy();
  });

  it("emits both the unprefixed and the -webkit- backdrop-filter", () => {
    const declarations = cssTierDeclarations(surface);

    expect(declarations["backdrop-filter"]).toContain("blur(");
    expect(declarations["-webkit-backdrop-filter"]).toBe(declarations["backdrop-filter"]);
  });

  it("takes the corner radius from the shape channels", () => {
    expect(cssTierDeclarations({ ...surface, radii: [4, 8, 12, 16] })["border-radius"]).toBe(
      "4px 8px 12px 16px",
    );
  });

  it("frosts harder and occludes more under reduced transparency", () => {
    const nominal = cssTierDeclarations(surface);
    const reduced = cssTierDeclarations({
      ...surface,
      policy: resolveAccessibilityPolicy(systemWith({ reducedTransparency: true })),
    });

    const blurOf = (value: string | undefined) => Number(/blur\(([\d.]+)px\)/.exec(value ?? "")?.[1]);
    expect(blurOf(reduced["backdrop-filter"])).toBeGreaterThan(blurOf(nominal["backdrop-filter"]));
    expect(reduced["--vitrea-occlusion"]).toBeDefined();
    expect(Number(reduced["--vitrea-occlusion"])).toBeGreaterThan(
      Number(nominal["--vitrea-occlusion"]),
    );
  });

  it("strengthens the border under increased contrast", () => {
    const strong = cssTierDeclarations({
      ...surface,
      policy: resolveAccessibilityPolicy(systemWith({ increasedContrast: true })),
    });

    expect(Number.parseFloat(strong["border-width"] ?? "0")).toBeGreaterThan(1);
  });

  it("drops the glass entirely under forced colors and uses system colors", () => {
    const forced = cssTierDeclarations({
      ...surface,
      policy: resolveAccessibilityPolicy(systemWith({ forcedColors: true })),
    });

    expect(forced["backdrop-filter"]).toBe("none");
    expect(forced.background).toBe("Canvas");
    expect(forced.color).toBe("CanvasText");
    expect(forced["border-color"]).toBe("CanvasText");
  });

  it("transitions nothing under reduced motion, and keeps the transition otherwise", () => {
    const nominal = cssTierDeclarations(surface);
    const reduced = cssTierDeclarations({
      ...surface,
      policy: resolveAccessibilityPolicy(systemWith({ reducedMotion: true })),
    });

    expect(nominal.transition).toContain("ms");
    // Reduced Motion removes overshoot and deformation; a CSS transition on a
    // material property is neither, so it survives — what goes is the elastic
    // easing, replaced by a monotonic one.
    expect(reduced.transition).not.toContain("cubic-bezier(0.34, 1.56");
  });

  it("names its tokens once, so the CSS tier and the GPU tier cannot drift apart", () => {
    for (const token of CSS_TIER_TOKENS) {
      expect(token.startsWith("--vitrea-")).toBe(true);
    }
    const declarations = cssTierDeclarations(surface);
    for (const token of CSS_TIER_TOKENS) {
      expect(declarations[token]).toBeDefined();
    }
  });
});
