import {
  NOMINAL_ACCESSIBILITY_POLICY,
  resolveAccessibilityPolicy,
  type RefractionQuality,
} from "@vitrea/core";
import { describe, expect, it } from "vitest";

import {
  accessibilityRefractionCap,
  effectiveRefraction,
  REFRACTION_LADDER,
  refractionRank,
} from "../src/refraction";

const systemWith = (flags: Partial<Record<string, boolean>> = {}) => ({
  reducedTransparency: false,
  reducedMotion: false,
  increasedContrast: false,
  forcedColors: false,
  reducedTransparencySupported: true,
  ...flags,
});

describe("the dual-cap rule (Decision Log #19)", () => {
  it("orders the refraction ladder so 'lower' means something", () => {
    expect(REFRACTION_LADDER).toEqual(["none", "approximate", "true"]);
    expect(refractionRank("none")).toBeLessThan(refractionRank("approximate"));
    expect(refractionRank("approximate")).toBeLessThan(refractionRank("true"));
  });

  it("honours the lower of the accessibility cap and the state's refraction level", () => {
    const cases: readonly [RefractionQuality, RefractionQuality, RefractionQuality][] = [
      ["true", "true", "true"],
      ["true", "approximate", "approximate"],
      ["true", "none", "none"],
      ["approximate", "true", "approximate"],
      ["approximate", "approximate", "approximate"],
      ["none", "true", "none"],
    ];

    for (const [state, cap, expected] of cases) {
      expect(effectiveRefraction(state, cap)).toBe(expected);
    }
  });

  it("is symmetric — neither input is privileged", () => {
    for (const a of REFRACTION_LADDER) {
      for (const b of REFRACTION_LADDER) {
        expect(effectiveRefraction(a, b)).toBe(effectiveRefraction(b, a));
      }
    }
  });

  it("maps the accessibility policy's regime onto the same ladder", () => {
    expect(accessibilityRefractionCap(NOMINAL_ACCESSIBILITY_POLICY.material)).toBe("true");
    expect(
      accessibilityRefractionCap(
        resolveAccessibilityPolicy(systemWith({ reducedTransparency: true })).material,
      ),
    ).toBe("approximate");
    expect(
      accessibilityRefractionCap(
        resolveAccessibilityPolicy(systemWith({ forcedColors: true })).material,
      ),
    ).toBe("none");
  });

  it("caps a texture group's true refraction under reduced transparency", () => {
    const policy = resolveAccessibilityPolicy(systemWith({ reducedTransparency: true }));

    expect(effectiveRefraction("true", accessibilityRefractionCap(policy.material))).toBe(
      "approximate",
    );
  });

  it("never raises a CSS-tier group above the 'none' its state already declares", () => {
    // The CSS tier reports refraction "none" because backdrop-filter blurs, it
    // never bends. A nominal accessibility policy must not talk it upward.
    expect(effectiveRefraction("none", "true")).toBe("none");
  });
});
