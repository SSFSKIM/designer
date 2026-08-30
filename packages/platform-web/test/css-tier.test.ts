import {
  NOMINAL_ACCESSIBILITY_POLICY,
  resolveAccessibilityPolicy,
  type ResolvedAccessibilityPolicy,
} from "@vitreajs/vitrea";
import { describe, expect, it } from "vitest";

import {
  cssTierDeclarations,
  foregroundDeclarations,
  foregroundInk,
  hintedBackdropLuminance,
  CSS_TIER_TOKENS,
} from "../src/css-tier";
import {
  CSS_TIER_MAPPING,
  INCREASED_OCCLUSION_LIFT,
  MATERIAL_OPTICS,
  MATERIAL_SOURCE_OPTICS,
  MATERIAL_SOURCE_OUTER_SHADOW,
  MATERIAL_SOURCE_SIZE,
  REDUCED_TRANSPARENCY_FROST,
  cssTierOptics,
  cssTierForegroundLevel,
  cssTintAlpha,
  gpuTierForegroundLevel,
  occlusionAlphaUnderPolicy,
  outerShadowAlpha,
  outerShadowFalloff,
  resolvedPolicyFold,
  sourceOuterShadow,
} from "../src/optics";

const surface = {
  radii: [22, 22, 22, 22] as const,
  optics: MATERIAL_OPTICS.regular,
  policy: NOMINAL_ACCESSIBILITY_POLICY,
};

/** The shipped surface with one optic overridden — for pinning a single seam. */
const declarationsOf = (optics: Partial<typeof MATERIAL_OPTICS.regular>) =>
  cssTierDeclarations({ ...surface, optics: { ...MATERIAL_OPTICS.regular, ...optics } });

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

    expect(declarations["background-color"]).toBeTruthy();
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

  it("frosts harder under reduced transparency, and never occludes less", () => {
    const nominal = cssTierDeclarations(surface);
    const reduced = cssTierDeclarations({
      ...surface,
      policy: resolveAccessibilityPolicy(systemWith({ reducedTransparency: true })),
    });

    const blurOf = (value: string | undefined) => Number(/blur\(([\d.]+)px\)/.exec(value ?? "")?.[1]);
    expect(blurOf(reduced["backdrop-filter"])).toBeGreaterThan(blurOf(nominal["backdrop-filter"]));
    expect(reduced["--vitrea-occlusion"]).toBeDefined();
    expect(Number(reduced["--vitrea-occlusion"])).toBeGreaterThanOrEqual(
      Number(nominal["--vitrea-occlusion"]),
    );
  });

  it("frosts by the multiplier the profile patch names, not the shipped one", () => {
    // Same defect class as the lift one field along: `reducedTransparencyFrost`
    // is patchable and the renderer already scales its blur sigma by the patched
    // value, so this tier folding its own mirrored copy would frost a demoted
    // surface by a factor the GPU tier never used.
    const policy = resolveAccessibilityPolicy(systemWith({ reducedTransparency: true }));
    const blurOf = (value: string | undefined): number =>
      Number(/blur\(([\d.]+)px\)/.exec(value ?? "")?.[1]);
    const frostedWith = (reducedTransparencyFrost?: number): number =>
      blurOf(
        cssTierDeclarations({
          ...surface,
          policy,
          ...(reducedTransparencyFrost === undefined
            ? {}
            : { policyFold: resolvedPolicyFold({ reducedTransparencyFrost }) }),
        })["backdrop-filter"],
      );

    // The blur is emitted to two decimals, so the expectation rounds the same way
    // rather than settling for a tolerance the shipped multiplier would also pass.
    const sigma = surface.optics.blurRadius;
    const emitted = (radius: number): number => Math.round(radius * 100) / 100;
    expect(frostedWith(1.1)).toBe(emitted(sigma * 1.1));
    expect(frostedWith(3)).toBe(emitted(sigma * 3));
    // Both directions: a patch may thin the frost as well as thicken it, and a
    // multiplier — unlike a floor — expresses that without a special case.
    expect(frostedWith(1.1)).toBeLessThan(frostedWith());
    expect(frostedWith(3)).toBeGreaterThan(frostedWith());
    // And no patch is byte-identical to before the field could be threaded.
    expect(frostedWith()).toBe(emitted(sigma * REDUCED_TRANSPARENCY_FROST));
    expect(frostedWith()).toBe(frostedWith(REDUCED_TRANSPARENCY_FROST));
  });

  /*
   * The occlusion lift is RELATIVE, and these are the tests that would have caught
   * it dying (Decision Log #32(d)).
   *
   * §Accessibility promises reduced transparency "higher occlusion". That used to
   * be an absolute floor, `Math.max(nominal, 0.62)` — a real lift while the
   * nominal tint alpha was the advisory 0.28, and a no-op from the moment C9a
   * measured nominal at 0.62. It had been dead on the GPU tier for a whole child
   * with nothing noticing. A fraction of the remaining transparency cannot die
   * that way, and the second test is the one that says so at nominals nobody has
   * measured yet.
   */
  it("lifts the occlusion above nominal under reduced transparency", () => {
    const nominal = Number(cssTierDeclarations(surface)["--vitrea-occlusion"]);
    const reduced = Number(
      cssTierDeclarations({
        ...surface,
        policy: resolveAccessibilityPolicy(systemWith({ reducedTransparency: true })),
      })["--vitrea-occlusion"],
    );

    // The shipped material, as converted for this tier, and the lift it gets.
    // 0.781/0.884 were the conversion of C9a's inactive-bed tint alpha of 0.62;
    // these are the conversion of the cascade's refitted 0.46 (2026-08-31).
    expect(nominal).toBeCloseTo(0.665, 3);
    expect(reduced).toBeCloseTo(0.823, 3);
    expect(reduced).toBeGreaterThan(nominal);
  });

  it("lifts at any nominal, including the ones no tuning pass has reached", () => {
    // The property, not the value: whatever a future profile makes the material's
    // alpha, reduced transparency still hides more of the backdrop than nominal.
    for (const tintAlpha of [0, 0.05, 0.28, 0.62, 0.9, 0.999]) {
      const optics = cssTierOptics({ optics: { regular: { tintAlpha } } });
      const at = (policy: ResolvedAccessibilityPolicy): number =>
        Number(
          cssTierDeclarations({ ...surface, optics: optics.regular, policy })["--vitrea-occlusion"],
        );
      const nominal = at(resolveAccessibilityPolicy(systemWith({})));
      const reduced = at(resolveAccessibilityPolicy(systemWith({ reducedTransparency: true })));

      expect(reduced, `tintAlpha ${tintAlpha}`).toBeGreaterThan(nominal);
    }

    // And a fully opaque material has nothing left to hide, which is the one place
    // "strictly greater" cannot hold and must not be asserted.
    expect(occlusionAlphaUnderPolicy(1, "increased")).toBe(1);
  });

  it("folds the lift the profile patch names, not the shipped one", () => {
    // The lift is a profile field the renderer already honours, so a patch that
    // names it moves the material the GPU tier composites. This tier has to fold
    // the same number or a demoted surface would paint an occlusion the renderer
    // never drew — K5's gap, reappearing through the patch rather than through a
    // second copy of the constant.
    const optics = cssTierOptics({ optics: { regular: { tintAlpha: 0.1 } } });
    const policy = resolveAccessibilityPolicy(systemWith({ reducedTransparency: true }));
    const foldedWith = (increasedOcclusionLift?: number): number =>
      Number(
        cssTierDeclarations({
          ...surface,
          optics: optics.regular,
          policy,
          ...(increasedOcclusionLift === undefined
            ? {}
            : { policyFold: resolvedPolicyFold({ increasedOcclusionLift }) }),
        })["--vitrea-occlusion"],
      );

    // The token is emitted to three decimals, so the expectation rounds the same
    // way rather than settling for a tolerance that would also pass on the
    // shipped lift.
    const nominal = optics.regular.tintAlpha;
    const emitted = (alpha: number): number => Math.round(alpha * 1000) / 1000;
    expect(foldedWith(0.05)).toBe(emitted(nominal + 0.05 * (1 - nominal)));
    expect(foldedWith(0.9)).toBe(emitted(nominal + 0.9 * (1 - nominal)));
    // A patched lift below the shipped one lifts less, which is the direction an
    // absolute-floor reading of the policy could not express at all.
    expect(foldedWith(0.05)).toBeLessThan(foldedWith());
    expect(foldedWith(0.9)).toBeGreaterThan(foldedWith());
    // And no patch is byte-identical to before the field could be threaded.
    expect(foldedWith()).toBe(foldedWith(INCREASED_OCCLUSION_LIFT));
  });

  it("restores the pre-C9a lift, expressed relatively", () => {
    // The fraction is not a new number: it is the old floor read as a proportion
    // of the headroom it closed, so at the old nominal the policy is unchanged.
    expect(occlusionAlphaUnderPolicy(0.28, "increased")).toBeCloseTo(0.62, 3);
    expect(INCREASED_OCCLUSION_LIFT).toBeCloseTo((0.62 - 0.28) / (1 - 0.28), 4);
  });

  it("strengthens the border under increased contrast", () => {
    const strong = cssTierDeclarations({
      ...surface,
      policy: resolveAccessibilityPolicy(systemWith({ increasedContrast: true })),
    });

    expect(Number.parseFloat(strong["border-width"] ?? "0")).toBeGreaterThan(1);
  });

  it("draws the strong border the profile patch names, not the shipped one", () => {
    // The third and last of the fold's mirrored constants. `strongBorderRim` is
    // patchable and the renderer already draws with the patched rim, so this tier
    // holding its own copy would put a different accessibility floor on a demoted
    // surface than on the one the renderer paints. The pair crosses unconverted —
    // see `STRONG_BORDER` for why the nominal rim's mapping has nothing to say
    // about a near-opaque line — which is what makes `toBe` the right assertion
    // here rather than a tolerance.
    const policy = resolveAccessibilityPolicy(systemWith({ increasedContrast: true }));
    const drawnWith = (
      strongBorderRim?: { rimWidth?: number; rimAlpha?: number },
    ): { width: string | undefined; colour: string | undefined } => {
      const declarations = cssTierDeclarations({
        ...surface,
        policy,
        ...(strongBorderRim === undefined
          ? {}
          : { policyFold: resolvedPolicyFold({ strongBorderRim }) }),
      });
      return { width: declarations["border-width"], colour: declarations["--vitrea-border-color"] };
    };

    expect(drawnWith({ rimWidth: 4, rimAlpha: 0.5 }).width).toBe("4px");
    expect(drawnWith({ rimWidth: 4, rimAlpha: 0.5 }).colour).toContain("0.5)");
    // Both directions: thinner and more transparent as readily as thicker and
    // more opaque, since a patch is a calibration result and not a floor.
    expect(drawnWith({ rimWidth: 1, rimAlpha: 0.2 }).width).toBe("1px");
    expect(drawnWith({ rimWidth: 1, rimAlpha: 0.2 }).colour).toContain("0.2)");
    // The renderer merges this rim per field, so a patch naming only the width
    // has to keep the mirrored alpha rather than dropping it.
    expect(drawnWith({ rimWidth: 4 }).colour).toBe(drawnWith().colour);
    // And no patch is byte-identical to before the field could be threaded.
    expect(drawnWith()).toEqual(drawnWith({ rimWidth: 2, rimAlpha: 0.95 }));
    expect(drawnWith().width).toBe("2px");
    expect(drawnWith().colour).toContain("0.95)");
  });

  it("drops the glass entirely under forced colors and uses system colors", () => {
    const forced = cssTierDeclarations({
      ...surface,
      policy: resolveAccessibilityPolicy(systemWith({ forcedColors: true })),
    });

    expect(forced["backdrop-filter"]).toBe("none");
    expect(forced["background-color"]).toBe("Canvas");
    expect(forced["--vitrea-foreground"]).toBe("CanvasText");
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

  /*
   * K5's seam. The property under test is not a value but a dependency: this
   * tier's paint must be a function of the material profile, so that a retune
   * cannot leave the two tiers rendering different materials the way C9a
   * measured (GPU 0.62 against CSS 0.28, a visible change on demotion).
   */
  describe("deriving the material from the profile (corrective K5)", () => {
    it("holds no optical literal of its own — every painted number comes from the optics", () => {
      const declarations = cssTierDeclarations(surface);
      const optics = MATERIAL_OPTICS.regular;

      expect(declarations["background-color"]).toBe(
        `rgba(${optics.tint.join(", ")}, ${optics.tintAlpha.toFixed(3)})`,
      );
      expect(declarations["border-color"]).toBe(
        `rgba(${optics.border.join(", ")}, ${optics.borderAlpha.toFixed(3)})`,
      );
      // The outer shadow (W8) is derived the same way: nothing in this file
      // chooses its lengths, and a profile that declines it stops it being drawn.
      const shadow = MATERIAL_SOURCE_OUTER_SHADOW;
      expect(declarations["box-shadow"]).toBe(
        `0 ${shadow.offsetPx}px ${2 * shadow.sigmaPx}px ${shadow.spreadPx}px ` +
          `rgba(0, 0, 0, ${Math.round(outerShadowAlpha(shadow.occlusion) * 1000) / 1000})`,
      );
      expect(
        cssTierDeclarations({
          ...surface,
          outerShadow: { ...shadow, occlusion: 0 },
        })["box-shadow"],
      ).toBe("none");
    });

    it("paints the press illumination the GPU tier draws, keyed off the glow channel", () => {
      // W1/coherence: this tier drew no glow at all, so the two tiers agreed on a
      // resting surface and diverged the moment one was held down — 1.96x on the
      // dark-scheme pressed capsule, where a lerp toward white over a dark
      // material is the whole interior rather than 2% of it.
      const optics = MATERIAL_OPTICS.regular;
      const layer = cssTierDeclarations(surface)["background-image"] ?? "";

      // The renderer's radius, and its `pressPoint ?? centre` fallback.
      expect(layer).toContain(`circle ${optics.glowRadius}px`);
      expect(layer).toContain("at var(--vitrea-press-x, 50%) var(--vitrea-press-y, 50%)");
      // The peak is the gain, scaled by the driver's own output rather than
      // baked in — the declarations stay frame-invariant and the browser tracks
      // the channel.
      const white = optics.glow.join(", ");
      expect(layer).toContain(
        `rgba(${white}, calc(var(--vitrea-glow, 0) * ${optics.glowGain})) 0%`,
      );
      // `radial²` falloff, sampled: a quarter of the way out the renderer is at
      // (1 - 0.25)^2 = 0.5625 of the gain.
      const quarterOut = Math.round(optics.glowGain * 0.5625 * 10000) / 10000;
      expect(layer).toContain(
        `rgba(${white}, calc(var(--vitrea-glow, 0) * ${quarterOut})) 25%`,
      );
      expect(layer).toContain(`rgba(${white}, 0) 100%`);

      // And the tint stays on its own longhand: an app writing a malformed
      // `--vitrea-glow` may lose the illumination, never the contrast floor.
      expect(declarationsOf({ glowGain: 0 })["background-image"]).toBe("none");
      expect(declarationsOf({ glowGain: 0 })["background-color"]).toBe(
        cssTierDeclarations(surface)["background-color"],
      );
    });

    it("converts the profile's alpha rather than copying it", () => {
      // The two tiers composite in different spaces, so the same material is a
      // different alpha here. Copying the source number across would have been
      // the mistake C9a declined to make; the conversion is what the seam exists
      // for. The source is the cascade's 0.46 (2026-08-31), not C9a's 0.62.
      const source = MATERIAL_SOURCE_OPTICS.regular.tintAlpha;
      expect(source).toBe(0.46);
      expect(MATERIAL_OPTICS.regular.tintAlpha).not.toBe(source);
      expect(MATERIAL_OPTICS.regular.tintAlpha).toBeGreaterThan(source);
    });

    it("moves with a profile patch, and only where the patch reaches", () => {
      const patched = cssTierOptics({ optics: { regular: { tintAlpha: 0.2 } } });

      expect(patched.regular.tintAlpha).toBeLessThan(MATERIAL_OPTICS.regular.tintAlpha);
      // A patch names leaves; siblings and the other variant survive it.
      expect(patched.regular.blurRadius).toBe(MATERIAL_OPTICS.regular.blurRadius);
      expect(patched.clear).toEqual(MATERIAL_OPTICS.clear);
    });

    it("carries a profile's tint colour into the declaration, not just its alpha", () => {
      // The dark-scheme profile tints to a near-black in linear light. A tier
      // that had hardcoded white would have drawn the dark material as a white
      // veil at a dark material's alpha — the failure mode a derived colour
      // removes rather than mitigates.
      const dark = cssTierOptics({
        optics: { regular: { tint: [0.05, 0.05, 0.05], tintAlpha: 0.97 } },
      });

      expect(dark.regular.tint).toEqual([63, 63, 63]);
      // The rim reads from the profile's highlight, which the patch left white.
      expect(dark.regular.border).toEqual([255, 255, 255]);
      expect(dark.regular.tintAlpha).toBeGreaterThan(0.9);
    });

    it("agrees with the GPU tier at the reference backdrop level and nowhere else", () => {
      // The coherence floor, as arithmetic rather than as a screenshot: one
      // scalar alpha cannot match a pre-blend transfer function, so the solved
      // alpha moves with the level it is solved at. That spread IS the residual
      // the tier-coherence claim is worded around.
      const source = MATERIAL_SOURCE_OPTICS.regular;
      const atDark = cssTintAlpha(source, { ...CSS_TIER_MAPPING, referenceBackdropLuminance: 0.05 });
      const atLight = cssTintAlpha(source, { ...CSS_TIER_MAPPING, referenceBackdropLuminance: 0.8 });

      expect(atDark).toBeGreaterThan(atLight);
      expect(atDark / atLight).toBeGreaterThan(1.1);
    });

    it("passes an alpha through unconverted when the tint has no contrast to solve for", () => {
      // A tint sitting at the reference backdrop's own level is invisible in
      // both pipelines, so there is no alpha to solve for — and the division
      // that would find one is by ~0.
      const level = CSS_TIER_MAPPING.referenceBackdropLuminance;
      const flat = cssTintAlpha({
        blurSigma: 8,
        tint: [level, level, level],
        tintAlpha: 0.44,
        rimAlpha: 0.18,
        highlight: [1, 1, 1],
      });

      expect(flat).toBe(0.44);
    });
  });

  describe("X6's hint reaching the tier (Decision Log #28(b), corrective K4)", () => {
    /*
     * K4's mechanism, with K5's arithmetic. The hint still decides the
     * foreground; what changed is that it decides it against the level behind
     * the glyphs rather than against the backdrop alone.
     *
     * A dark hint under the *regular* material now resolves to the DARK token,
     * and that inversion is the fix rather than the regression: the regular
     * material is 78% opaque, so a reader sees the white tint and not the dark
     * backdrop. Measured on the demo before this changed — near-white ink on a
     * near-white surface, WCAG contrast 1.24 against a 4.5 floor.
     *
     * The old outcome is still reachable and still correct where it belongs: the
     * clear variant over the same hint keeps the light token, because at its
     * alpha the backdrop really does dominate. The pair below is the whole
     * property — the tone matters, and so does how much of it survives the
     * material.
     */
    it("decides a dark-hinted foreground against the material, not against the backdrop", () => {
      const regular = cssTierDeclarations({
        ...surface,
        foreground: { mode: "author-hint", tone: "dark" },
      });
      const clear = cssTierDeclarations({
        ...surface,
        optics: MATERIAL_OPTICS.clear,
        foreground: { mode: "author-hint", tone: "dark" },
      });

      // Opaque enough that the tint is what the text sits on.
      expect(regular["--vitrea-foreground"]).toBe("#1c1c1e");
      expect(regular["--vitrea-foreground"]).not.toContain("light-dark");
      // Transparent enough that the dark backdrop is.
      expect(clear["--vitrea-foreground"]).toBe("#f5f5f7");
    });

    it("prefers the hint's own luminance over the tone's coarse reading", () => {
      // X6's hint carries an optional luminance and it is the finer statement.
      // On the clear variant the two answers differ, which is what makes this a
      // test of the precedence rather than of the arithmetic.
      const coarse = cssTierDeclarations({
        ...surface,
        optics: MATERIAL_OPTICS.clear,
        foreground: { mode: "author-hint", tone: "dark" },
      });
      const declared = cssTierDeclarations({
        ...surface,
        optics: MATERIAL_OPTICS.clear,
        foreground: { mode: "author-hint", tone: "dark", luminance: 0.45 },
      });

      expect(coarse["--vitrea-foreground"]).toBe("#f5f5f7");
      expect(declared["--vitrea-foreground"]).toBe("#1c1c1e");
    });

    it("gives a group hinted with a light backdrop the explicit dark foreground token", () => {
      const declarations = cssTierDeclarations({
        ...surface,
        foreground: { mode: "author-hint", tone: "light" },
      });

      expect(declarations["--vitrea-foreground"]).toBe("#1c1c1e");
    });

    it("leaves an unhinted group byte-identical to today's light-dark() default", () => {
      const unhinted = cssTierDeclarations(surface);
      const noHintAvailable = cssTierDeclarations({ ...surface, foreground: { mode: "fixed" } });

      expect(unhinted["--vitrea-foreground"]).toBe("light-dark(#1c1c1e, #f5f5f7)");
      expect(noHintAvailable).toEqual(unhinted);
    });

    it("keeps light-dark() for a mixed tone — there is no single explicit answer", () => {
      const declarations = cssTierDeclarations({
        ...surface,
        foreground: { mode: "author-hint", tone: "mixed" },
      });

      expect(declarations["--vitrea-foreground"]).toBe("light-dark(#1c1c1e, #f5f5f7)");
    });

    it("keeps light-dark() for a fixed mode, even if a tone somehow rode along", () => {
      const declarations = cssTierDeclarations({
        ...surface,
        foreground: { mode: "fixed", tone: "dark" },
      });

      expect(declarations["--vitrea-foreground"]).toBe("light-dark(#1c1c1e, #f5f5f7)");
    });

    it("keeps light-dark() for a sampled-async mode — the CSS tier never gets exact analysis", () => {
      const declarations = cssTierDeclarations({
        ...surface,
        foreground: { mode: "sampled-async", tone: "dark" },
      });

      expect(declarations["--vitrea-foreground"]).toBe("light-dark(#1c1c1e, #f5f5f7)");
    });

    it("lets increased contrast's near-monochrome outrank a dark-backdrop hint", () => {
      const declarations = cssTierDeclarations({
        ...surface,
        policy: resolveAccessibilityPolicy(systemWith({ increasedContrast: true })),
        foreground: { mode: "author-hint", tone: "dark" },
      });

      // Accessibility policy wins: still the near-monochrome light-dark(), not
      // the hint's explicit light token.
      expect(declarations["--vitrea-foreground"]).toBe("light-dark(#000, #fff)");
    });

    it("lets forced-colors outrank a dark-backdrop hint", () => {
      const declarations = cssTierDeclarations({
        ...surface,
        policy: resolveAccessibilityPolicy(systemWith({ forcedColors: true })),
        foreground: { mode: "author-hint", tone: "dark" },
      });

      expect(declarations["--vitrea-foreground"]).toBe("CanvasText");
      expect(declarations["background-color"]).toBe("Canvas");
    });
  });
});

/*
 * The foreground decision, as the *shared* rule it became in C9d (Decision Log
 * #32(b)).
 *
 * K5 corrected the CSS tier's arithmetic and left the GPU tier's alone, because
 * the parent wanted the GPU tier measured before it was touched. It was, and the
 * defect reproduced in a shape K5 had not: the GPU tier published no foreground at
 * all, so an app reading `var(--vitrea-foreground, …)` fell back to its own ink —
 * measured on a dark-hinted GPU-tier surface at WCAG 1.57 against a 4.5 floor
 * (`e2e/gpu/foreground-audit.spec.ts`, which now measures 10.81).
 *
 * These hold the two halves the e2e cannot: that the rule is one rule, and that
 * the only thing differing between the tiers is the space their material
 * composites in.
 */
describe("the foreground rule, shared across the tiers", () => {
  it("reaches the same side of the crossover from either composite", () => {
    // The property that matters is the *ink*, not the number. Same material, same
    // backdrop, two compositing spaces: the two levels are genuinely different
    // quantities — the CSS tier reads higher here, because its converted alpha is
    // 0.781 where the renderer's is 0.62 — and they still land on the same side of
    // the crossover, which is why a demotion does not change the ink. That the
    // numbers differ at all is the coherence floor `optics.ts` states rather than
    // a defect in either, so it is asserted rather than smoothed over.
    const gpu = gpuTierForegroundLevel(MATERIAL_SOURCE_OPTICS.regular, 0.16);
    const css = cssTierForegroundLevel(MATERIAL_OPTICS.regular, 0.16);

    expect(gpu).not.toBe(css);
    expect(gpu).toBeGreaterThan(CSS_TIER_MAPPING.foregroundCrossover);
    expect(css).toBeGreaterThan(CSS_TIER_MAPPING.foregroundCrossover);

    // And the same on the other side of it: the clear variant's alpha is low
    // enough that the backdrop dominates on both tiers.
    expect(gpuTierForegroundLevel(MATERIAL_SOURCE_OPTICS.clear, 0.05)).toBeLessThan(
      CSS_TIER_MAPPING.foregroundCrossover,
    );
    expect(cssTierForegroundLevel(MATERIAL_OPTICS.clear, 0.05)).toBeLessThan(
      CSS_TIER_MAPPING.foregroundCrossover,
    );
  });

  it("follows the tint once the tint dominates, and the backdrop while it does not", () => {
    // The property K4's rule got backwards. At the shipped opacity a dark backdrop
    // still yields the dark ink, because what the reader sees is the white tint; at
    // the clear variant's opacity the same backdrop yields the light one.
    const regular = gpuTierForegroundLevel(MATERIAL_SOURCE_OPTICS.regular, 0.05);
    const clear = gpuTierForegroundLevel(MATERIAL_SOURCE_OPTICS.clear, 0.05);

    expect(regular).toBeGreaterThan(CSS_TIER_MAPPING.foregroundCrossover);
    expect(clear).toBeLessThan(CSS_TIER_MAPPING.foregroundCrossover);
  });

  /*
   * Decision Log #34(c). The runtime decides the ink and publishes it — as the
   * token, and as nothing else. It used to hand back `color` too, and the host
   * got both inline, which put the runtime's answer above every application
   * rule short of `!important`: an app styling a glass host watched its
   * declaration parse, cascade and silently never apply, while being told to
   * build on the token sitting on that same element.
   *
   * The colour itself is unchanged and still asserted, one call up, through
   * `foregroundInk`. What is asserted here is the *shape* of the write, which
   * is the half that was the defect.
   */
  it("publishes the ink as the token and never as an inline colour", () => {
    for (const level of [0, 0.4, 0.5, 1]) {
      const declarations = foregroundDeclarations({
        policy: NOMINAL_ACCESSIBILITY_POLICY,
        level,
      });
      expect(Object.keys(declarations)).toEqual(["--vitrea-foreground"]);
      expect(declarations["--vitrea-foreground"]).toBe(
        foregroundInk({ policy: NOMINAL_ACCESSIBILITY_POLICY, level }),
      );
    }

    // Every regime, including the two that take a platform palette rather than
    // the adaptive answer — a `color` leaking back in under forced colors would
    // be the same defect wearing the accessibility branch.
    for (const policy of [
      NOMINAL_ACCESSIBILITY_POLICY,
      resolveAccessibilityPolicy(systemWith({ increasedContrast: true })),
      resolveAccessibilityPolicy(systemWith({ forcedColors: true })),
    ]) {
      expect(Object.keys(foregroundDeclarations({ policy }))).toEqual(["--vitrea-foreground"]);
    }

    // And the full CSS-tier record, which composes the pair in: the tier writes
    // the whole material inline, so this is where a stray `color` would ride.
    expect(cssTierDeclarations(surface).color).toBeUndefined();
    expect(
      cssTierDeclarations({
        ...surface,
        policy: resolveAccessibilityPolicy(systemWith({ forcedColors: true })),
      }).color,
    ).toBeUndefined();
  });

  it("keeps accessibility policy above the hint, on either tier", () => {
    expect(
      foregroundDeclarations({
        policy: resolveAccessibilityPolicy(systemWith({ increasedContrast: true })),
        level: 0.95,
      })["--vitrea-foreground"],
    ).toBe("light-dark(#000, #fff)");
    expect(
      foregroundDeclarations({
        policy: resolveAccessibilityPolicy(systemWith({ forcedColors: true })),
        level: 0.95,
      })["--vitrea-foreground"],
    ).toBe("CanvasText");
  });

  it("resolves a hint's backdrop level from its luminance, or from its tone", () => {
    expect(hintedBackdropLuminance({ mode: "author-hint", tone: "dark", luminance: 0.16 })).toBe(0.16);
    expect(hintedBackdropLuminance({ mode: "author-hint", tone: "dark" })).toBe(
      CSS_TIER_MAPPING.toneLuminance.dark,
    );
    // Nothing to decide from: a mixed tone, a non-hint mode, no hint at all.
    expect(hintedBackdropLuminance({ mode: "author-hint", tone: "mixed" })).toBeUndefined();
    expect(hintedBackdropLuminance({ mode: "fixed", tone: "dark" })).toBeUndefined();
    expect(hintedBackdropLuminance(undefined)).toBeUndefined();
  });
});

/*
 * The size law on this tier (W2). Apple's rule is about the material, so it has
 * to reach the tier most visitors get, not only the shader — a demoted platter
 * that stopped being thick would be K5's gap on a new axis.
 *
 * The constants are patched here rather than read from the shipped profile
 * deliberately. What is being pinned is that the tier *applies* the law and where
 * it applies it; the shipped magnitudes belong to the bed, and a test written
 * over them would fail every time the bed is re-measured while proving nothing
 * about this file.
 */
describe("the size law reaches the CSS tier", () => {
  const size = {
    sizeSpanMin: 40,
    sizeSpanMax: 200,
    sizeScatterGainMax: 2.5,
    sizeOcclusionGain: 0.4,
    refractionScale: MATERIAL_SOURCE_SIZE.refractionScale,
  } as const;
  const at = (spanPx: number) => cssTierDeclarations({ ...surface, spanPx, size });
  const blurOf = (declarations: Record<string, string>): number =>
    Number.parseFloat((declarations["--vitrea-blur"] ?? "0px").replace("px", ""));
  const occlusionOf = (declarations: Record<string, string>): number =>
    Number.parseFloat(declarations["--vitrea-occlusion"] ?? "0");

  it("changes nothing at all for a caller that declares no span", () => {
    // The property that makes the law additive: every pre-law caller, every
    // golden, and the release path's clear-declarations call are untouched.
    expect(cssTierDeclarations({ ...surface, size })).toEqual(cssTierDeclarations(surface));
  });

  it("leaves a small control exactly where it was", () => {
    expect(at(size.sizeSpanMin)).toEqual(cssTierDeclarations(surface));
    expect(at(12)).toEqual(cssTierDeclarations(surface));
  });

  it("frosts and occludes a platter more, and monotonically between", () => {
    const small = at(size.sizeSpanMin);
    const platter = at(400);
    expect(blurOf(platter)).toBeCloseTo(blurOf(small) * size.sizeScatterGainMax, 6);
    expect(occlusionOf(platter)).toBeGreaterThan(occlusionOf(small));

    let previousBlur = -Infinity;
    let previousOcclusion = -Infinity;
    for (const span of [0, 40, 60, 96, 140, 200, 400]) {
      const declarations = at(span);
      expect(blurOf(declarations), `blur at span ${span}`).toBeGreaterThanOrEqual(previousBlur);
      expect(occlusionOf(declarations), `occlusion at span ${span}`).toBeGreaterThanOrEqual(
        previousOcclusion,
      );
      previousBlur = blurOf(declarations);
      previousOcclusion = occlusionOf(declarations);
    }
  });

  it("writes the widened blur into the filter the browser actually runs", () => {
    // Not only the published token: `--vitrea-blur` is documentation and
    // `backdrop-filter` is the material, and the two moving apart would be a
    // surface that reports a frost it does not have.
    const platter = at(400);
    expect(platter["backdrop-filter"]).toContain(`blur(${blurOf(platter)}px)`);
    expect(platter["-webkit-backdrop-filter"]).toBe(platter["backdrop-filter"]);
  });

  it("stays out of the way of forced colours, at every span", () => {
    // `glass: "none"` is a different surface, not a dimmer one — so the law has
    // nothing to gain there and must not smuggle a blur back in.
    const forced = resolveAccessibilityPolicy(systemWith({ forcedColors: true }));
    for (const span of [12, 96, 400]) {
      const declarations = cssTierDeclarations({ ...surface, policy: forced, spanPx: span, size });
      expect(declarations["backdrop-filter"], `span ${span}`).toBe("none");
      expect(declarations["--vitrea-blur"]).toBe("0px");
      expect(declarations["--vitrea-occlusion"]).toBe("1");
    }
  });

  /*
   * The fold, which is not decoration: the law was first landed without it and
   * the calibration regeneration caught both accessibility profiles' large-span
   * cells crossing their adopted ΔE bounds. Under reduce-transparency Apple's
   * material is nearly opaque and its interior level is flat in span, so a size
   * term has nothing to add there — which is the rule the rest of the material
   * already followed through `opticsUnderPolicy`.
   */
  it("weakens under reduced transparency, and stops under forced colours", () => {
    const reduced = resolveAccessibilityPolicy(systemWith({ reducedTransparency: true }));
    const nominalPlatter = at(400);
    const reducedPlatter = cssTierDeclarations({ ...surface, policy: reduced, spanPx: 400, size });
    const reducedSmall = cssTierDeclarations({ ...surface, policy: reduced, spanPx: 40, size });

    // The preference's own frost still lands in full — the fold is on the size
    // law, not on the preference.
    expect(blurOf(reducedSmall)).toBeCloseTo(blurOf(at(40)) * REDUCED_TRANSPARENCY_FROST, 6);

    // And the size law's *addition* on top of it is scaled by the ladder's
    // reduced rung rather than applied whole.
    const added = (declarations: Record<string, string>, base: number): number =>
      blurOf(declarations) / base - 1;
    /*
     * Three decimals rather than six, and the reason is the medium rather than
     * the law. `--vitrea-blur` is emitted through `px()`, which rounds to two
     * decimal places, so this ratio-of-ratios carries that quantisation divided
     * by the blur it is taken over. At the σ = 8 this was written against the
     * error sat under 1e-6; at the cascade's refitted σ = 3 (2026-08-31) the same
     * 0.005px rounding is 2.7× larger relative to the number, and lands at 7e-4.
     * The identity itself is exact — it is the declaration that is quantised.
     */
    expect(
      Math.abs(
        added(reducedPlatter, blurOf(reducedSmall)) -
          added(nominalPlatter, blurOf(at(40))) * MATERIAL_SOURCE_SIZE.refractionScale.approximate,
      ),
      // The budget, derived rather than picked: `px()` rounds to 0.01, the ratio
      // is taken over a blur of `blurOf(reducedSmall)`, and two rounded terms
      // enter it — so 2 x 0.005 / blur, which at the shipped sigma is 1.9e-3.
    ).toBeLessThan((2 * 0.005) / blurOf(reducedSmall));

    // Still a law, not an off switch: a platter under the preference is still
    // frostier than a control under it.
    expect(blurOf(reducedPlatter)).toBeGreaterThan(blurOf(reducedSmall));
    expect(occlusionOf(reducedPlatter)).toBeGreaterThanOrEqual(occlusionOf(reducedSmall));
    expect(occlusionOf(reducedPlatter)).toBeLessThanOrEqual(1);
  });
});

/*
 * W8. The reference's active material casts an outer shadow across up to a third
 * of the canvas and vitrea rendered exactly zero of it — the largest fidelity gap
 * the project has measured. These pin the MECHANISM rather than the fitted
 * constants: the constants are provisional and the cascade owns them, but a
 * shadow that stopped being multiplicative, or that started painting over black,
 * would be a different facet wearing the same numbers.
 */
describe("the outer shadow reaches the CSS tier", () => {
  const shadowOf = (declarations: Record<string, string>): string => {
    const value = declarations["box-shadow"];
    if (value === undefined) throw new Error("no box-shadow written");
    return value;
  };
  /** The alpha out of a `box-shadow: … rgba(0, 0, 0, α)` declaration. */
  const alphaOf = (declarations: Record<string, string>): number => {
    const value = shadowOf(declarations);
    if (value === "none") return 0;
    const match = /rgba\(0, 0, 0, ([\d.]+)\)$/.exec(value);
    if (match?.[1] === undefined) throw new Error(`unparsed box-shadow: ${value}`);
    return Number(match[1]);
  };

  it("writes the profile's own lengths, with box-shadow's blur convention applied", () => {
    // `filter: blur()` takes σ; `box-shadow` takes twice it (CSS Backgrounds 3).
    // Getting this wrong halves or doubles the shadow's reach in silence, so it
    // is asserted against the σ the profile states rather than against a literal.
    const shadow = MATERIAL_SOURCE_OUTER_SHADOW;
    expect(shadowOf(cssTierDeclarations(surface))).toBe(
      `0 ${shadow.offsetPx}px ${2 * shadow.sigmaPx}px ${shadow.spreadPx}px ` +
        `rgba(0, 0, 0, ${Math.round(outerShadowAlpha(shadow.occlusion) * 1000) / 1000})`,
    );
    // Downward, never up: the reference's shadow is offset toward the bottom of
    // the screen on every profile, backdrop, span and scale in the bed.
    expect(shadow.offsetPx).toBeGreaterThan(0);
  });

  it("is a multiplicative occlusion, and therefore analytically zero over black", () => {
    /*
     * The claim the whole facet rests on. A `box-shadow` is a constant colour
     * composited source-over, which is not a multiply — UNLESS the colour is
     * black, and then `(1 - a)·backdrop + a·0` IS `backdrop·(1 - a)`. So the
     * colour is load-bearing and this asserts it, and then asserts the property
     * it buys: over a black backdrop the shadow changes nothing at all, which is
     * exactly what the reference's `dark-solid` cells measure (byte-identical to
     * their own background).
     */
    expect(shadowOf(cssTierDeclarations(surface))).toContain("rgba(0, 0, 0, ");

    const alpha = alphaOf(cssTierDeclarations(surface));
    const over = (backdrop: number): number => backdrop * (1 - alpha);
    expect(over(0)).toBe(0);
    // And in proportion everywhere else: twice the light behind it, twice the
    // light removed.
    expect(over(0.5)).toBeCloseTo(over(1) / 2, 12);
  });

  it("converts the reference's LINEAR occlusion into the alpha a browser composites with", () => {
    /*
     * The one honest gap on this tier, measured rather than waved at. The
     * reference removes a fraction of the backdrop's linear light; a browser
     * composites `box-shadow` in encoded sRGB. `outerShadowAlpha` inverts the
     * transfer function's power law, which makes the conversion independent of
     * the backdrop — and what is left is the transfer function's linear toe.
     *
     * This measures that residual across the whole backdrop range and holds it
     * under one 8-bit code step's worth of slack, against a reference bed whose
     * own run-to-run reproducibility is +/-4 of 255 (Decision Log 10).
     */
    const occlusion = MATERIAL_SOURCE_OUTER_SHADOW.occlusion;
    const alpha = outerShadowAlpha(occlusion);
    const encode = (linear: number): number =>
      linear <= 0.0031308 ? 12.92 * linear : 1.055 * linear ** (1 / 2.4) - 0.055;

    let worstCodes = 0;
    for (let i = 0; i <= 200; i += 1) {
      const linear = 0.004 * (1 / 0.004) ** (i / 200);
      const reference = encode(linear * (1 - occlusion));
      const painted = encode(linear) * (1 - alpha);
      worstCodes = Math.max(worstCodes, Math.abs(reference - painted) * 255);
    }
    expect(worstCodes).toBeLessThan(3);

    // Exact at the ends, whatever the constants become: no occlusion is no
    // shadow, and total occlusion is opaque black.
    expect(outerShadowAlpha(0)).toBe(0);
    expect(outerShadowAlpha(1)).toBe(1);
  });

  it("falls off as a Gaussian's integral — the shape a box-shadow's blur is", () => {
    const sigma = MATERIAL_SOURCE_OUTER_SHADOW.sigmaPx;
    // Half exactly on the silhouette's own edge, monotone outward, and gone by
    // three sigma — the three properties that make it a blurred silhouette
    // rather than a ramp or a step.
    expect(outerShadowFalloff(0, sigma)).toBeCloseTo(0.5, 6);
    expect(outerShadowFalloff(-3 * sigma, sigma)).toBeGreaterThan(0.998);
    expect(outerShadowFalloff(3 * sigma, sigma)).toBeLessThan(0.002);
    let previous = 1;
    for (let d = -2 * sigma; d <= 2 * sigma; d += sigma / 8) {
      const value = outerShadowFalloff(d, sigma);
      expect(value).toBeLessThanOrEqual(previous);
      previous = value;
    }
  });

  it("dims under reduced transparency and goes out under forced colours", () => {
    /*
     * MEASURED, which the charter asked for before the fold was written. The
     * reference's shadow under reduce-transparency is the same shadow at 0.566
     * of the amplitude — it neither vanishes nor intensifies — and the
     * increased-contrast reference reproduces the reduced-transparency number to
     * four decimals, because macOS force-couples the toggles (Decision Log 8).
     */
    const nominal = alphaOf(cssTierDeclarations(surface));
    const reduced = alphaOf(
      cssTierDeclarations({
        ...surface,
        policy: resolveAccessibilityPolicy(systemWith({ reducedTransparency: true })),
      }),
    );
    expect(reduced).toBeGreaterThan(0);
    expect(reduced).toBeLessThan(nominal);

    // Forced colours is not a dimmer material, it is a different surface — and a
    // shadow that outlived the glass it belonged to would be the one composition
    // the regime exists to prevent.
    expect(
      shadowOf(
        cssTierDeclarations({
          ...surface,
          policy: resolveAccessibilityPolicy(systemWith({ forcedColors: true })),
        }),
      ),
    ).toBe("none");
  });

  it("follows a profile patch, and a profile may decline it outright", () => {
    const patched = sourceOuterShadow({ outerShadow: { occlusion: 0.5, offsetPx: 12 } });
    expect(patched.occlusion).toBe(0.5);
    expect(patched.offsetPx).toBe(12);
    // Unnamed fields keep the mirrored default, which is the renderer's own merge
    // rule and the reason a partial calibration patch is legal.
    expect(patched.sigmaPx).toBe(MATERIAL_SOURCE_OUTER_SHADOW.sigmaPx);

    expect(shadowOf(cssTierDeclarations({ ...surface, outerShadow: patched }))).toBe(
      `0 12px ${2 * patched.sigmaPx}px ${patched.spreadPx}px ` +
        `rgba(0, 0, 0, ${Math.round(outerShadowAlpha(0.5) * 1000) / 1000})`,
    );
    expect(
      shadowOf(cssTierDeclarations({ ...surface, outerShadow: { ...patched, occlusion: 0 } })),
    ).toBe("none");
  });

  it("rides the size law's one curve, and is inert at the shipped gain", () => {
    /*
     * The seam, and its measured emptiness. The reference's THREE LENGTHS are
     * span-invariant across 32…160 px, so nothing but the amplitude may couple;
     * the amplitude's own coupling points in opposite directions in the two
     * colour schemes, so the shipped gain is the identity and this pins that a
     * span cannot move the shadow until somebody fits one.
     */
    expect(MATERIAL_SOURCE_OUTER_SHADOW.sizeGain).toBe(0);
    const small = cssTierDeclarations({ ...surface, spanPx: 24, size: MATERIAL_SOURCE_SIZE });
    const platter = cssTierDeclarations({ ...surface, spanPx: 320, size: MATERIAL_SOURCE_SIZE });
    expect(shadowOf(platter)).toBe(shadowOf(small));

    // With a gain, the same curve moves it — and only the amplitude, never the
    // lengths, which is the half of the facet the bed actually settled.
    const gained = { ...MATERIAL_SOURCE_OUTER_SHADOW, sizeGain: 0.5 };
    const thin = cssTierDeclarations({ ...surface, spanPx: 24, outerShadow: gained });
    const thick = cssTierDeclarations({ ...surface, spanPx: 320, outerShadow: gained });
    expect(alphaOf(thick)).toBeGreaterThan(alphaOf(thin));
    expect(shadowOf(thin).split("rgba")[0]).toBe(shadowOf(thick).split("rgba")[0]);
  });
});
