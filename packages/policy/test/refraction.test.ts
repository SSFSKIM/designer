/**
 * The ladder's algebra, exhaustively — the half of the dual-cap rule that can be
 * checked without a resolver.
 *
 * This file and `platform-web/test/refraction.test.ts` are deliberately not the
 * same test. That one feeds core's real `resolveAccessibilityPolicy` into the cap
 * and pins the *wiring* — reduced transparency actually reaches `approximate`,
 * forced colours actually reach `none` — and it has to live above core to do it.
 * This one owns the algebra, and because there are only three rungs and three
 * regimes it can sweep every input rather than sampling six of the nine pairs:
 * the properties below (symmetry, idempotence, monotonicity, "a cap can only
 * lower") are what the two tiers are relying on when each folds two caps into one
 * scalar, and none of them was asserted anywhere before this package existed.
 */

import { describe, expect, it } from "vitest";

import {
  accessibilityRefractionCap,
  DEFAULT_REFRACTION_SCALE,
  effectiveRefraction,
  REFRACTION_LADDER,
  refractionRank,
  type RefractionRegime,
} from "../src/index";

const REGIMES = ["nominal", "reduced", "none"] as const satisfies readonly RefractionRegime[];

describe("the refraction ladder (Decision Log #19)", () => {
  it("orders the rungs weakest first, so 'lower' means something", () => {
    expect(REFRACTION_LADDER).toEqual(["none", "approximate", "true"]);
    expect(refractionRank("none")).toBeLessThan(refractionRank("approximate"));
    expect(refractionRank("approximate")).toBeLessThan(refractionRank("true"));
  });

  it("covers X2's three refraction levels and nothing else", () => {
    expect([...REFRACTION_LADDER].sort()).toEqual(["approximate", "none", "true"]);
    expect(new Set(REFRACTION_LADDER).size).toBe(REFRACTION_LADDER.length);
  });

  it("ranks every rung, and only by its position", () => {
    for (const [index, rung] of REFRACTION_LADDER.entries()) {
      expect(refractionRank(rung), rung).toBe(index);
    }
  });
});

describe("effectiveRefraction — the lower of two caps", () => {
  it("returns the weaker of every one of the nine pairs", () => {
    for (const a of REFRACTION_LADDER) {
      for (const b of REFRACTION_LADDER) {
        const weaker = refractionRank(a) <= refractionRank(b) ? a : b;
        expect(effectiveRefraction(a, b), `${a} ∧ ${b}`).toBe(weaker);
      }
    }
  });

  it("is symmetric — neither input is privileged", () => {
    for (const a of REFRACTION_LADDER) {
      for (const b of REFRACTION_LADDER) {
        expect(effectiveRefraction(a, b), `${a} ∧ ${b}`).toBe(effectiveRefraction(b, a));
      }
    }
  });

  it("is idempotent, so folding a cap in twice changes nothing", () => {
    // Both tiers fold the accessibility cap in at more than one site — the CSS
    // tier through `sizeThicknessUnderPolicy` and again through the state, the
    // renderer through the profile scale and again in the shader's bias. A
    // second application must be free, or those foldings would compound.
    for (const a of REFRACTION_LADDER) {
      expect(effectiveRefraction(a, a), a).toBe(a);
      for (const b of REFRACTION_LADDER) {
        const once = effectiveRefraction(a, b);
        expect(effectiveRefraction(once, b), `${a} ∧ ${b}`).toBe(once);
      }
    }
  });

  it("is associative, so the order the caps arrive in cannot matter", () => {
    for (const a of REFRACTION_LADDER) {
      for (const b of REFRACTION_LADDER) {
        for (const c of REFRACTION_LADDER) {
          expect(
            effectiveRefraction(effectiveRefraction(a, b), c),
            `${a} ∧ ${b} ∧ ${c}`,
          ).toBe(effectiveRefraction(a, effectiveRefraction(b, c)));
        }
      }
    }
  });

  it("never raises either input", () => {
    for (const a of REFRACTION_LADDER) {
      for (const b of REFRACTION_LADDER) {
        const result = effectiveRefraction(a, b);
        expect(refractionRank(result), `${a} ∧ ${b}`).toBeLessThanOrEqual(refractionRank(a));
        expect(refractionRank(result), `${a} ∧ ${b}`).toBeLessThanOrEqual(refractionRank(b));
      }
    }
  });
});

describe("accessibilityRefractionCap — the regime as a rung", () => {
  it("maps each of the three regimes onto the ladder", () => {
    expect(accessibilityRefractionCap({ refraction: "nominal" })).toBe("true");
    expect(accessibilityRefractionCap({ refraction: "reduced" })).toBe("approximate");
    expect(accessibilityRefractionCap({ refraction: "none" })).toBe("none");
  });

  it("is total over the regimes and lands on the ladder every time", () => {
    for (const refraction of REGIMES) {
      expect(REFRACTION_LADDER, refraction).toContain(accessibilityRefractionCap({ refraction }));
    }
  });

  it("is monotone: a stricter regime never permits more refraction", () => {
    const ranks = REGIMES.map((refraction) => refractionRank(accessibilityRefractionCap({ refraction })));
    expect(ranks).toEqual([...ranks].sort((x, y) => y - x));
  });

  it("reads only the one axis, so any fuller policy satisfies it", () => {
    // core's `ResolvedMaterialPolicy` and the renderer's `MaterialPolicyView` are
    // both wider than `RefractionPolicyView`; the cap must not notice.
    const wider = { glass: "material", refraction: "reduced", border: "strong" } as const;
    expect(accessibilityRefractionCap(wider)).toBe("approximate");
  });

  it("caps a texture group's true refraction under reduced transparency", () => {
    expect(effectiveRefraction("true", accessibilityRefractionCap({ refraction: "reduced" }))).toBe(
      "approximate",
    );
  });

  it("never talks a CSS-tier group above the 'none' its state already declares", () => {
    // The CSS tier reports refraction "none" because backdrop-filter blurs, it
    // never bends. A nominal accessibility policy must not raise that.
    expect(effectiveRefraction("none", accessibilityRefractionCap({ refraction: "nominal" }))).toBe(
      "none",
    );
  });
});

describe("DEFAULT_REFRACTION_SCALE", () => {
  it("is keyed by the ladder, exactly", () => {
    expect(Object.keys(DEFAULT_REFRACTION_SCALE).sort()).toEqual([...REFRACTION_LADDER].sort());
  });

  it("holds the numbers both tiers shipped before they shared them", () => {
    // Decision Log #23(d) collapsed three copies of this table into one. The
    // collapse was required to move no number, so the values are pinned here as
    // literals rather than derived from anything.
    expect(DEFAULT_REFRACTION_SCALE.none).toBe(0);
    expect(DEFAULT_REFRACTION_SCALE.approximate).toBe(0.45);
    expect(DEFAULT_REFRACTION_SCALE.true).toBe(1);
  });

  it("rises with the ladder, and spans the closed unit interval", () => {
    // A scale is "how much of a depth simulation this rung allows": a weaker rung
    // allowing more depth would invert the ladder wherever a tier multiplies by it.
    let previous = -Infinity;
    for (const rung of REFRACTION_LADDER) {
      const scale = DEFAULT_REFRACTION_SCALE[rung];
      expect(scale, rung).toBeGreaterThan(previous);
      expect(scale, rung).toBeGreaterThanOrEqual(0);
      expect(scale, rung).toBeLessThanOrEqual(1);
      previous = scale;
    }
  });
});
