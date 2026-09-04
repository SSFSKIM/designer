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
  type CssTierLayer,
  type CssTierRender,
  type CssTierSurface,
  type StyleDeclarations,
} from "../src/css-tier";
import {
  CSS_TIER_MAPPING,
  INCREASED_OCCLUSION_LIFT,
  MATERIAL_OPTICS,
  MATERIAL_SOURCE_OPTICS,
  MATERIAL_SOURCE_OUTER_SHADOW,
  MATERIAL_SOURCE_SIZE,
  REDUCED_TRANSPARENCY_FROST,
  cssOpticsFromSource,
  cssTierOptics,
  cssTierForegroundLevel,
  cssTierShadowAlpha,
  cssTintAlpha,
  gpuTierForegroundLevel,
  occlusionAlphaUnderPolicy,
  OUTER_SHADOW_THIN_L,
  outerShadowAlpha,
  outerShadowFalloff,
  outerShadowThinOcclusion,
  POLICY_FOLD_CONSTANTS,
  resolvedPolicyFold,
  scatterHeavyEffectiveRatioAtScale,
  sizeOcclusionAlphaAt,
  sizeThicknessUnderPolicy,
  scatterThickness as cssScatterThickness,
  sizeThickness,
  groupScatterSigma,
  sizeScatterSigmaAt,
  sourceSize,
  sourceOuterShadow,
  type MaterialOptics,
  type MaterialSourceOptics,
  type MaterialSourceSize,
  type PolicyFoldConstants,
} from "../src/optics";

/**
 * The optics `root.ts` hands this tier, for one source under one regime and one
 * span — re-pointed at W17 G1 (charter Decision Log 2 (b)).
 *
 * The regime's occlusion lift and the size law's occlusion used to be applied by
 * `cssTierDeclarations`, on the alpha this tier had already converted. They land
 * on the SOURCE alpha now, before the W9 response solve and before the
 * conversion, because that is the order the shader takes them in: a solve run at
 * one alpha and a raise applied afterwards lands the interior's mean above the
 * response the solve exists to hit, by +0.015 to +0.027 of this tier's level
 * (claims §5.74 §3). The policies below are unchanged — the same lift, the same
 * gain, the same direction — and what moved is where in the chain they land, so
 * the pins move with them rather than being dropped.
 */
const occludedOptics = (
  source: MaterialSourceOptics,
  policy: ResolvedAccessibilityPolicy,
  options: {
    readonly spanPx?: number;
    readonly fold?: PolicyFoldConstants;
    readonly size?: MaterialSourceSize;
  } = {},
): MaterialOptics => {
  const fold = options.fold ?? POLICY_FOLD_CONSTANTS;
  const sizeConstants = options.size ?? MATERIAL_SOURCE_SIZE;
  const lifted = occlusionAlphaUnderPolicy(
    source.tintAlpha,
    policy.material.occlusion,
    fold.increasedOcclusionLift,
  );
  const sized =
    options.spanPx === undefined
      ? lifted
      : sizeOcclusionAlphaAt(
          lifted,
          sizeThicknessUnderPolicy(options.spanPx, policy.material, sizeConstants),
          sizeConstants,
        );
  return cssOpticsFromSource(MATERIAL_OPTICS.regular, { ...source, tintAlpha: sized });
};

const surface = {
  radii: [22, 22, 22, 22] as const,
  optics: MATERIAL_OPTICS.regular,
  policy: NOMINAL_ACCESSIBILITY_POLICY,
};

/** The shipped surface with one optic overridden — for pinning a single seam. */
const declarationsOf = (optics: Partial<typeof MATERIAL_OPTICS.regular>) =>
  cssTierDeclarations({ ...surface, optics: { ...MATERIAL_OPTICS.regular, ...optics } });

/*
 * The tier's element model, as these tests read it (W16 G1).
 *
 * `cssTierDeclarations` returns a `CssTierRender` rather than one flat record,
 * because the properties it writes go to four different elements: the host keeps
 * the geometry, the outer shadow and the five tokens, and the three created
 * layers carry the sharp `backdrop-filter`, the heavy one, and the tint, the
 * press glow and the rim. The readers below name the element a property lives
 * on; none of them merges the four back into one record, because which element
 * carries which declaration is the whole of what the wave changed.
 */

/** The host's own declarations. */
const hostOf = (surface: CssTierSurface): StyleDeclarations => cssTierDeclarations(surface).host;

/**
 * The three created layers of a render.
 *
 * It throws where the tier created none rather than handing back empty records:
 * the only surface without layers is the forced-colours one, whose whole
 * material is on the host, and a test reaching for a filter there is asking a
 * question that regime has no answer to.
 */
const layersOf = (render: CssTierRender): Readonly<Record<CssTierLayer, StyleDeclarations>> => {
  const { layers } = render;
  if (layers === undefined) throw new Error("the tier created no layers for this surface");
  return layers;
};

/** L1's declarations — the sharp `backdrop-filter` and the material's `saturate()`. */
const sharpOf = (surface: CssTierSurface): StyleDeclarations =>
  layersOf(cssTierDeclarations(surface)).sharp;

/** L3's declarations — the tint, the press glow and the rim. */
const overlayOf = (surface: CssTierSurface): StyleDeclarations =>
  layersOf(cssTierDeclarations(surface)).overlay;

/**
 * The scale the tier still projects onto ONE σ at — `--vitrea-blur`, and the
 * width the cost collapse degrades to.
 *
 * W13's `CSS_TIER_RAMP_SCALE` was this number as the whole tier's ramp scale,
 * because one `backdrop-filter` had to pick a scale to render the ramp's average
 * at. W16 G1 gave the body two layers and a mask and moved them to the live
 * ratio; the projection stayed at 1, because it is what the collapse degrades to
 * and what the public token publishes, and a degradation that was also a
 * re-derivation would be two changes wearing one name.
 */
const PROJECTION_SCALE = 1;

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
    //
    // Both terms moved to the overlay layer in W16 G1 and neither weakened. The
    // tint is that layer's `background-color`, above both filters rather than
    // under them; the rim is its inset `box-shadow`, because the host's own
    // border paints below the created layers and would be covered by them. The
    // border-box width the rim is drawn at is still the host's, since it is
    // layout and no created layer may move it.
    const overlay = overlayOf(surface);

    expect(overlay["background-color"]).toBeTruthy();
    expect(overlay["box-shadow"]).toContain("inset ");
    expect(hostOf(surface)["border-width"]).toBeTruthy();
  });

  it("emits both the unprefixed and the -webkit- backdrop-filter, on both filtered layers", () => {
    // The host carries no filter of its own since W16 G1: a filtered parent is a
    // backdrop root, so a `backdrop-filter` left on the host would make its own
    // children's inert. It still writes both properties, at `none`, because a
    // material that stops writing one of its declarations leaves whatever was
    // last there. A spanless surface collapses to one layer, so the pairing is
    // read on both forms: the collapsed body's single filter, and the two-layer
    // body's pair.
    for (const spanned of [surface, { ...surface, spanPx: 400 }]) {
      const render = cssTierDeclarations(spanned);
      expect(render.host["backdrop-filter"]).toBe("none");
      expect(render.host["-webkit-backdrop-filter"]).toBe("none");

      const layers = layersOf(render);
      const filtered =
        render.body.form === "two-layer" ? [layers.sharp, layers.heavy] : [layers.sharp];
      for (const layer of filtered) {
        expect(layer["backdrop-filter"]).toContain("blur(");
        expect(layer["-webkit-backdrop-filter"]).toBe(layer["backdrop-filter"]);
      }
    }
    // And the collapsed heavy layer is off rather than transparent: the collapse
    // exists to buy back a render surface, which an `opacity: 0` layer still costs.
    expect(cssTierDeclarations(surface).body.form).toBe("collapsed");
    expect(layersOf(cssTierDeclarations(surface)).heavy.display).toBe("none");
  });

  it("takes the corner radius from the shape channels", () => {
    // The radius stays the host's, and the created layers inherit it rather than
    // restating it, so there is exactly one place a corner is declared.
    const render = cssTierDeclarations({ ...surface, radii: [4, 8, 12, 16] });
    expect(render.host["border-radius"]).toBe("4px 8px 12px 16px");
    for (const layer of Object.values(layersOf(render))) {
      expect(layer["border-radius"]).toBe("inherit");
    }
  });

  it("frosts harder under reduced transparency, and never occludes less", () => {
    // The frost is read off the layer that runs it — L1, which is the whole body
    // on a spanless surface — and the occlusion off the token the host publishes.
    const reducedSurface = {
      ...surface,
      policy: resolveAccessibilityPolicy(systemWith({ reducedTransparency: true })),
    };

    const blurOf = (value: string | undefined) => Number(/blur\(([\d.]+)px\)/.exec(value ?? "")?.[1]);
    expect(blurOf(sharpOf(reducedSurface)["backdrop-filter"])).toBeGreaterThan(
      blurOf(sharpOf(surface)["backdrop-filter"]),
    );
    expect(hostOf(reducedSurface)["--vitrea-occlusion"]).toBeDefined();
    expect(Number(hostOf(reducedSurface)["--vitrea-occlusion"])).toBeGreaterThanOrEqual(
      Number(hostOf(surface)["--vitrea-occlusion"]),
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
        sharpOf({
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
    const reducedPolicy = resolveAccessibilityPolicy(systemWith({ reducedTransparency: true }));
    const nominal = Number(hostOf(surface)["--vitrea-occlusion"]);
    const reduced = Number(
      hostOf({
        ...surface,
        optics: occludedOptics(MATERIAL_SOURCE_OPTICS.regular, reducedPolicy),
        policy: reducedPolicy,
      })["--vitrea-occlusion"],
    );

    // The shipped material, as converted for this tier, and the lift it gets.
    // 0.781/0.884 were the conversion of C9a's inactive-bed tint alpha of 0.62;
    // 0.665/0.916 were the conversion of the cascade's refitted 0.46 with the
    // lift applied AFTER the conversion. 0.929 is the same lift applied before
    // it (W17 G1, Decision Log 2 (b)) — higher, because the conversion is
    // concave in the alpha and lifting first spends the headroom in the space
    // the renderer's own lift spends it in.
    expect(nominal).toBeCloseTo(0.665, 3);
    expect(reduced).toBeCloseTo(0.929, 3);
    expect(reduced).toBeGreaterThan(nominal);
  });

  it("lifts at any nominal, including the ones no tuning pass has reached", () => {
    // The property, not the value: whatever a future profile makes the material's
    // alpha, reduced transparency still hides more of the backdrop than nominal.
    for (const tintAlpha of [0, 0.05, 0.28, 0.62, 0.9, 0.999]) {
      const source = { ...MATERIAL_SOURCE_OPTICS.regular, tintAlpha };
      const at = (policy: ResolvedAccessibilityPolicy): number =>
        Number(
          hostOf({ ...surface, optics: occludedOptics(source, policy), policy })[
            "--vitrea-occlusion"
          ],
        );
      const nominal = at(resolveAccessibilityPolicy(systemWith({})));
      const reduced = at(resolveAccessibilityPolicy(systemWith({ reducedTransparency: true })));

      // At a nominal of exactly zero the conversion has nothing to convert and
      // both sides read the source's own alpha, which is the one place a
      // strictly-greater comparison of the CONVERTED numbers is a comparison of
      // the lift itself rather than of its conversion.
      expect(
        occlusionAlphaUnderPolicy(tintAlpha, "increased"),
        `tintAlpha ${tintAlpha}`,
      ).toBeGreaterThan(tintAlpha);
      expect(reduced, `tintAlpha ${tintAlpha}`).toBeGreaterThanOrEqual(nominal);
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
    const source = { ...MATERIAL_SOURCE_OPTICS.regular, tintAlpha: 0.1 };
    const policy = resolveAccessibilityPolicy(systemWith({ reducedTransparency: true }));
    const foldedWith = (increasedOcclusionLift?: number): number => {
      const fold =
        increasedOcclusionLift === undefined
          ? undefined
          : resolvedPolicyFold({ increasedOcclusionLift });
      return Number(
        hostOf({
          ...surface,
          optics: occludedOptics(source, policy, ...(fold === undefined ? [] : [{ fold }])),
          policy,
          ...(fold === undefined ? {} : { policyFold: fold }),
        })["--vitrea-occlusion"],
      );
    };

    // The token is emitted to three decimals, so the expectation rounds the same
    // way rather than settling for a tolerance that would also pass on the
    // shipped lift. The lift is taken in the SOURCE's alpha space since W17 G1
    // and the token reports the converted number, so the expectation converts
    // too — the fraction of the headroom is the assertion, not the digits.
    const nominal = source.tintAlpha;
    const emitted = (alpha: number): number =>
      Math.round(cssTintAlpha({ ...source, tintAlpha: alpha }) * 1000) / 1000;
    expect(foldedWith(0.05)).toBe(emitted(nominal + 0.05 * (1 - nominal)));
    expect(foldedWith(0.9)).toBe(emitted(nominal + 0.9 * (1 - nominal)));
    // A patched lift below the shipped one lifts less, which is the direction an
    // absolute-floor reading of the policy could not express at all.
    expect(foldedWith(0.05)).toBeLessThan(foldedWith());
    expect(foldedWith(0.9)).toBeGreaterThan(foldedWith());
    // And no patch is byte-identical to before the field could be threaded.
    expect(foldedWith()).toBe(foldedWith(INCREASED_OCCLUSION_LIFT));
  });

  it("is a fitted lift now, not the pre-C9a floor re-expressed", () => {
    // It used to be the old absolute floor read as a proportion of the headroom
    // it closed, so the policy was unchanged at the old nominal — a continuity
    // argument rather than a measurement. Round two fitted it against the active
    // bed on both accessibility profiles' calibration cells (claims §5.15/§5.16)
    // and it moved 0.4722 -> 0.75, so the old identity no longer holds. What is
    // worth pinning is the relative FORM, mirrored from the renderer.
    expect(INCREASED_OCCLUSION_LIFT).toBeCloseTo(0.75, 6);
    for (const nominal of [0.1, 0.28, 0.46, 0.8]) {
      expect(occlusionAlphaUnderPolicy(nominal, "increased"), `nominal ${nominal}`).toBeCloseTo(
        nominal + INCREASED_OCCLUSION_LIFT * (1 - nominal),
        12,
      );
    }
  });

  it("strengthens the border under increased contrast", () => {
    const strong = {
      ...surface,
      policy: resolveAccessibilityPolicy(systemWith({ increasedContrast: true })),
    };

    // The width is the host's, because it is layout. The rim drawn at that width
    // is the overlay's inset `box-shadow`, and it widens with it.
    expect(Number.parseFloat(hostOf(strong)["border-width"] ?? "0")).toBeGreaterThan(1);
    expect(overlayOf(strong)["box-shadow"]).toContain(
      `inset 0 0 0 ${hostOf(strong)["border-width"]}`,
    );
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
      const host = hostOf({
        ...surface,
        policy,
        ...(strongBorderRim === undefined
          ? {}
          : { policyFold: resolvedPolicyFold({ strongBorderRim }) }),
      });
      return { width: host["border-width"], colour: host["--vitrea-border-color"] };
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

    // This regime keeps the whole surface on the host and creates no layers at
    // all: the platform's palette is not a dimmer material but a different one,
    // and layers left standing would leave glass under system colours. So the
    // border here is a real `border-color` rather than the overlay's rim, which
    // is why this is the one branch that still reads like the pre-W16 record.
    expect(forced.layers).toBeUndefined();
    expect(forced.host["backdrop-filter"]).toBe("none");
    expect(forced.host["background-color"]).toBe("Canvas");
    expect(forced.host["--vitrea-foreground"]).toBe("CanvasText");
    expect(forced.host["border-color"]).toBe("CanvasText");
  });

  it("transitions nothing under reduced motion, and keeps the transition otherwise", () => {
    /*
     * A transition is declared on the element that carries the property, so W16
     * G1 split what was one list on the host across four elements: the outer
     * shadow stays with the host, the two filters go to L1 and L2, and the tint
     * and the rim go to L3. The duration and the easing are still one decision —
     * the material morphs as one thing — so the property is read on every
     * element the material now lives on rather than on the host alone. A spanned
     * surface is used because it is the one whose heavy layer is live and
     * therefore has a filter to morph.
     */
    const spanned = { ...surface, spanPx: 400 };
    const transitionsOf = (input: CssTierSurface): readonly string[] => {
      const render = cssTierDeclarations(input);
      return [render.host, ...Object.values(layersOf(render))].map((d) => d.transition ?? "");
    };

    for (const transition of transitionsOf(spanned)) {
      expect(transition).toContain("ms");
      expect(transition).toContain("cubic-bezier(0.34, 1.56");
    }
    // Reduced Motion removes overshoot and deformation; a CSS transition on a
    // material property is neither, so it survives — what goes is the elastic
    // easing, replaced by a monotonic one, and it goes on every element at once.
    for (const transition of transitionsOf({
      ...spanned,
      policy: resolveAccessibilityPolicy(systemWith({ reducedMotion: true })),
    })) {
      expect(transition).toContain("ms");
      expect(transition).not.toContain("cubic-bezier(0.34, 1.56");
    }
  });

  it("names its tokens once, so the CSS tier and the GPU tier cannot drift apart", () => {
    for (const token of CSS_TIER_TOKENS) {
      expect(token.startsWith("--vitrea-")).toBe(true);
    }
    // All five are published on the HOST, which is the element an app styles
    // against — a token on a created layer would be invisible to it.
    const host = hostOf(surface);
    for (const token of CSS_TIER_TOKENS) {
      expect(host[token]).toBeDefined();
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
      const render = cssTierDeclarations(surface);
      const { host } = render;
      const { overlay } = layersOf(render);
      const optics = MATERIAL_OPTICS.regular;

      expect(overlay["background-color"]).toBe(
        `rgba(${optics.tint.join(", ")}, ${optics.tintAlpha.toFixed(3)})`,
      );
      /*
       * The rim's colour used to be the host's `border-color` and this asserted
       * it there. Since W16 G1 the host's border is `transparent` — it is still
       * LAYOUT, and no created layer may move the author's content box, but it
       * paints below the negative-`z` layers and would be covered by them — so
       * the colour is drawn as an inset `box-shadow` on the overlay, which
       * follows `border-radius` exactly. The same number, on the construction
       * that now carries it, and still published unconverted on the token.
       */
      const rim = `rgba(${optics.border.join(", ")}, ${optics.borderAlpha.toFixed(3)})`;
      expect(host["border-color"]).toBe("transparent");
      expect(host["--vitrea-border-color"]).toBe(rim);
      // The rim is L3's FIRST shadow; the outer shadow joins the same list
      // behind it on the default carrier (W18 G1), so the rim is asserted as the
      // head of the list rather than as the whole of it.
      expect(overlay["box-shadow"]?.split(", 0 ")[0]).toBe(
        `inset 0 0 0 ${Math.round(optics.borderWidth * 100) / 100}px ${rim}`,
      );
      // The outer shadow (W8) is derived the same way: nothing in this file
      // chooses its lengths, and a profile that declines it stops it being drawn.
      const shadow = MATERIAL_SOURCE_OUTER_SHADOW;
      // The amplitude is a law since W14 G1: this surface declares no span and
      // no backdrop, so it resolves the thin regime at the unmeasured-backdrop
      // fallback, which is the mid plateau.
      const occlusion = outerShadowThinOcclusion(undefined, shadow);
      // The OUTER shadow is L3's second shadow since W18 G1, on the default
      // carrier: painted after both filters, so a surface never samples it. The
      // value is the material's and is reported on the render as well.
      expect(render.outerShadow).toBe(
        `0 ${shadow.offsetPx}px ${2 * shadow.sigmaPx}px ${shadow.spreadPx}px ` +
          `rgba(0, 0, 0, ${Math.round(outerShadowAlpha(occlusion) * 1000) / 1000})`,
      );
      expect(
        cssTierDeclarations({
          ...surface,
          outerShadow: {
            ...shadow,
            thinOcclusionDark: 0,
            thinOcclusionMid: 0,
            thinOcclusionBright: 0,
            thickOcclusionAt96: 0,
            thickOcclusionAt128: 0,
            thickOcclusionAt160: 0,
          },
        }).outerShadow,
      ).toBe("none");
    });

    it("paints the press illumination the GPU tier draws, keyed off the glow channel", () => {
      // W1/coherence: this tier drew no glow at all, so the two tiers agreed on a
      // resting surface and diverged the moment one was held down — 1.96x on the
      // dark-scheme pressed capsule, where a lerp toward white over a dark
      // material is the whole interior rather than 2% of it.
      //
      // The glow rides with the tint on the overlay, above both filters: a glow
      // painted beneath them would be blurred by the very body it lights.
      const optics = MATERIAL_OPTICS.regular;
      const layer = overlayOf(surface)["background-image"] ?? "";

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
      expect(layersOf(declarationsOf({ glowGain: 0 })).overlay["background-image"]).toBe("none");
      expect(layersOf(declarationsOf({ glowGain: 0 })).overlay["background-color"]).toBe(
        overlayOf(surface)["background-color"],
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
        ...MATERIAL_SOURCE_OPTICS.regular,
        blurSigma: 8,
        tint: [level, level, level],
        tintAlpha: 0.44,
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
      const regular = hostOf({
        ...surface,
        foreground: { mode: "author-hint", tone: "dark" },
      });
      const clear = hostOf({
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
      const coarse = hostOf({
        ...surface,
        optics: MATERIAL_OPTICS.clear,
        foreground: { mode: "author-hint", tone: "dark" },
      });
      const declared = hostOf({
        ...surface,
        optics: MATERIAL_OPTICS.clear,
        foreground: { mode: "author-hint", tone: "dark", luminance: 0.45 },
      });

      expect(coarse["--vitrea-foreground"]).toBe("#f5f5f7");
      expect(declared["--vitrea-foreground"]).toBe("#1c1c1e");
    });

    it("gives a group hinted with a light backdrop the explicit dark foreground token", () => {
      const host = hostOf({
        ...surface,
        foreground: { mode: "author-hint", tone: "light" },
      });

      expect(host["--vitrea-foreground"]).toBe("#1c1c1e");
    });

    it("leaves an unhinted group byte-identical to today's light-dark() default", () => {
      const unhinted = cssTierDeclarations(surface);
      const noHintAvailable = cssTierDeclarations({ ...surface, foreground: { mode: "fixed" } });

      expect(unhinted.host["--vitrea-foreground"]).toBe("light-dark(#1c1c1e, #f5f5f7)");
      // The whole render, so a hint that changed a layer or the resolved body
      // rather than the token would not slip past either.
      expect(noHintAvailable).toEqual(unhinted);
    });

    it("keeps light-dark() for a mixed tone — there is no single explicit answer", () => {
      const host = hostOf({
        ...surface,
        foreground: { mode: "author-hint", tone: "mixed" },
      });

      expect(host["--vitrea-foreground"]).toBe("light-dark(#1c1c1e, #f5f5f7)");
    });

    it("keeps light-dark() for a fixed mode, even if a tone somehow rode along", () => {
      const host = hostOf({
        ...surface,
        foreground: { mode: "fixed", tone: "dark" },
      });

      expect(host["--vitrea-foreground"]).toBe("light-dark(#1c1c1e, #f5f5f7)");
    });

    it("keeps light-dark() for a sampled-async mode — the CSS tier never gets exact analysis", () => {
      const host = hostOf({
        ...surface,
        foreground: { mode: "sampled-async", tone: "dark" },
      });

      expect(host["--vitrea-foreground"]).toBe("light-dark(#1c1c1e, #f5f5f7)");
    });

    it("lets increased contrast's near-monochrome outrank a dark-backdrop hint", () => {
      const host = hostOf({
        ...surface,
        policy: resolveAccessibilityPolicy(systemWith({ increasedContrast: true })),
        foreground: { mode: "author-hint", tone: "dark" },
      });

      // Accessibility policy wins: still the near-monochrome light-dark(), not
      // the hint's explicit light token.
      expect(host["--vitrea-foreground"]).toBe("light-dark(#000, #fff)");
    });

    it("lets forced-colors outrank a dark-backdrop hint", () => {
      const host = hostOf({
        ...surface,
        policy: resolveAccessibilityPolicy(systemWith({ forcedColors: true })),
        foreground: { mode: "author-hint", tone: "dark" },
      });

      expect(host["--vitrea-foreground"]).toBe("CanvasText");
      expect(host["background-color"]).toBe("Canvas");
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

    // And the full CSS-tier render, which composes the pair in: the tier writes
    // the whole material inline, so this is where a stray `color` would ride.
    // Every element it writes is checked, not only the host — a `color` on a
    // created layer would inherit into nothing, but a `color` on the host is the
    // defect itself, and both are the tier's own writes.
    for (const render of [
      cssTierDeclarations(surface),
      cssTierDeclarations({
        ...surface,
        policy: resolveAccessibilityPolicy(systemWith({ forcedColors: true })),
      }),
    ]) {
      for (const written of [render.host, ...Object.values(render.layers ?? {})]) {
        expect(written.color).toBeUndefined();
      }
    }
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
    // The scatter facet has its own span curve (W11c) with a depth ramp riding
    // on it (W13 G1): the floor is off here and the curve's top is the
    // thickness band's, so these cases keep testing the one-curve properties,
    // and the floor and the separate top get their own cases below. The ramp's
    // shape is the shipped one, because what these cases pin is that the tier
    // applies the projection and where — the magnitudes belong to the bed.
    sizeScatterFloor: 0,
    sizeScatterSpanMax: 200,
    // The second scale (W15 G1) set equal to this fixture's own 1x law, so the
    // fixture is scale-free and every case below reads the law it names. Since
    // W16 G1 the tier's body does read the live ratio, and all but one case
    // below declares none, so they get the 1x law either way — a scale-free
    // fixture is what keeps that a property of the law rather than of the
    // default, and it is what lets the one case that does declare a ratio read
    // the division as the ratio's own.
    sizeScatterGainMax2x: 2.5,
    sizeScatterFloor2x: 0,
    sizeScatterSpanMax2x: 200,
    // The 2x gain's span grading (W15 G1's re-form) equal to the fixture's 2x
    // gain, which keeps the gain curve flat as well as the fixture scale-free.
    sizeScatterGainFar2x: 2.5,
    sizeScatterRampStartThin1x: MATERIAL_SOURCE_SIZE.sizeScatterRampStartThin1x,
    sizeScatterRampStartThick1x: MATERIAL_SOURCE_SIZE.sizeScatterRampStartThick1x,
    sizeScatterRampStartThin2x: MATERIAL_SOURCE_SIZE.sizeScatterRampStartThin2x,
    sizeScatterRampStartThick2x: MATERIAL_SOURCE_SIZE.sizeScatterRampStartThick2x,
    sizeScatterRampStartFar1x: MATERIAL_SOURCE_SIZE.sizeScatterRampStartFar1x,
    sizeScatterRampStartFar2x: MATERIAL_SOURCE_SIZE.sizeScatterRampStartFar2x,
    sizeScatterRampReach1xPx: MATERIAL_SOURCE_SIZE.sizeScatterRampReach1xPx,
    sizeScatterRampReach2xPx: MATERIAL_SOURCE_SIZE.sizeScatterRampReach2xPx,
    sizeOcclusionGain: 0.4,
    refractionScale: MATERIAL_SOURCE_SIZE.refractionScale,
  } as const;
  // The size law's occlusion facet lands on the SOURCE alpha since W17 G1
  // (Decision Log 2 (b)), so a span reaches the tier's tint through the
  // conversion rather than after it — and these pins follow it there.
  const at = (spanPx: number, sizeConstants: MaterialSourceSize = size) =>
    cssTierDeclarations({
      ...surface,
      optics: occludedOptics(MATERIAL_SOURCE_OPTICS.regular, surface.policy, {
        spanPx,
        size: sizeConstants,
      }),
      spanPx,
      size: sizeConstants,
    });
  /*
   * Both readings come off the HOST, where the two tokens are published. Since
   * W16 G1 `--vitrea-blur` is the tier's single-σ PROJECTION rather than the
   * width of any one layer — the body carries two — and the projection is what
   * the size law's shape is stated in, which is why these cases still read it.
   * The two layer widths get their own case below.
   */
  const blurOf = (render: CssTierRender): number =>
    Number.parseFloat((render.host["--vitrea-blur"] ?? "0px").replace("px", ""));
  const occlusionOf = (render: CssTierRender): number =>
    Number.parseFloat(render.host["--vitrea-occlusion"] ?? "0");

  it("changes nothing at all for a caller that declares no span", () => {
    // The property that makes the law additive: every pre-law caller, every
    // golden, and the release path's clear-declarations call are untouched.
    expect(cssTierDeclarations({ ...surface, size })).toEqual(cssTierDeclarations(surface));
  });

  it("leaves a small control exactly where it was", () => {
    // Both facets are exactly inert at or below `sizeSpanMin`, which is what
    // keeps the law additive. The depth ramp does not break that: its excursion
    // is `max(0, s₀ − sDeep)` and on a span the curve leaves at a zero floor
    // the deep sharp share is already 1, so there is nothing above it to add.
    expect(at(size.sizeSpanMin)).toEqual(cssTierDeclarations(surface));
    expect(at(12)).toEqual(cssTierDeclarations(surface));
  });

  it("frosts at the floor when the ramp has nothing to add, and keeps rising past the thickness top", () => {
    // The measured shape of the scatter facet: a floor at any span (W11c), a
    // band top past the thickness curve's (W11c), and a depth ramp above the
    // curve near the contour (W13 G1). A spanless caller is still untouched; a
    // small control with a span frosts at the floor, because its deep sharp
    // share 1 − floor already exceeds the ramp's start and the excursion clamps
    // to zero there; and the occlusion — which rides the thickness curve — is
    // exactly where it was.
    const own = { ...size, sizeScatterFloor: 0.4, sizeScatterSpanMax: 400 } as const;
    const with_ = (spanPx: number) => at(spanPx, own);
    const base = blurOf(cssTierDeclarations(surface));
    expect(cssTierDeclarations({ ...surface, size: own })).toEqual(cssTierDeclarations(surface));
    // The shipped THIN start is 0.72 and 1 − 0.4 is 0.60, so on a span this far
    // below `sizeSpanMin` — where `sizeThickness` is 0 and the start is its thin
    // anchor exactly — the ramp has 0.12 of sharp share to add, and a 12 px
    // surface lies wholly inside the 80 device px reach. So the projection sits
    // WELL below the floor rather than at it: 0.283 against 0.4. The band is
    // sharper than the frost, which is what a band is, and the floor is the
    // fold's anchor rather than a pointwise minimum on the mix.
    expect(blurOf(with_(12))).toBeLessThan(base * (1 + 1.5 * 0.4));
    expect(blurOf(with_(12))).toBeGreaterThan(base * (1 + 1.5 * 0.27));
    expect(cssScatterThickness(12, 0, own, PROJECTION_SCALE)).toBeCloseTo(0.4, 12);
    expect(cssScatterThickness(400, 0, own, PROJECTION_SCALE)).toBeCloseTo(0.4, 12);
    expect(occlusionOf(with_(own.sizeSpanMin))).toBeCloseTo(occlusionOf(at(size.sizeSpanMin)), 6);
    // Past sizeSpanMax (200) the occlusion is saturated and the blur is not.
    expect(occlusionOf(with_(300))).toBeCloseTo(occlusionOf(with_(200)), 6);
    expect(blurOf(with_(300))).toBeGreaterThan(blurOf(with_(200)));
    // And it approaches the gain from below without reaching it: far above the
    // ramp's reach the sharp component survives in a rim of fixed width, whose
    // share of the area falls like 1/span.
    expect(blurOf(with_(40000))).toBeLessThan(base * 2.5);
    expect(blurOf(with_(40000))).toBeCloseTo(base * 2.5, 1);
  });

  it("frosts and occludes a platter more, and monotonically between", () => {
    const small = at(size.sizeSpanMin);
    const platter = at(400);
    expect(blurOf(platter)).toBeGreaterThan(blurOf(small));
    // The gain is the ceiling the projection approaches from below and never
    // reaches, because the ramp keeps a rim of the sharp component at every span.
    const base = blurOf(cssTierDeclarations(surface));
    expect(blurOf(at(40000))).toBeLessThan(base * size.sizeScatterGainMax);
    expect(blurOf(at(40000))).toBeCloseTo(base * size.sizeScatterGainMax, 1);
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

  it("writes the widened blur into the filters the browser actually runs", () => {
    /*
     * Not only the published token: `--vitrea-blur` is documentation and the
     * `backdrop-filter`s are the material, and the two moving apart would be a
     * surface that reports a frost it does not have.
     *
     * Since W16 G1 there is no single filter to hold the token against — the
     * body is two layers, the sharp one at the profile's own width and the heavy
     * one at a step that composes to the widened width over it. So the same fact
     * is asserted one level down: the two declarations are exactly the widths
     * the body reports, the step really does compose to the heavy width, the
     * widening reaches them, and the projection the token publishes lies between
     * the two components it stands for.
     */
    const platter = at(400);
    const { body } = platter;
    const { sharp, heavy } = layersOf(platter);
    const emitted = (radius: number): number => Math.round(radius * 100) / 100;

    expect(body.form).toBe("two-layer");
    expect(sharp["backdrop-filter"]).toContain(`blur(${emitted(body.sharpSigmaCssPx)}px)`);
    expect(heavy["backdrop-filter"]).toBe(`blur(${emitted(body.heavyStepSigmaCssPx)}px)`);
    expect(sharp["-webkit-backdrop-filter"]).toBe(sharp["backdrop-filter"]);
    expect(heavy["-webkit-backdrop-filter"]).toBe(heavy["backdrop-filter"]);
    // Two Gaussians in series add in quadrature, which is what makes the step
    // the declaration and the composed width the comparable quantity.
    expect(Math.hypot(body.sharpSigmaCssPx, body.heavyStepSigmaCssPx)).toBeCloseTo(
      body.heavySigmaCssPx,
      12,
    );
    // The widening is what reaches the filters: a platter's heavy component is
    // wider than the whole body of a control at `sizeSpanMin`.
    expect(body.heavySigmaCssPx).toBeGreaterThan(at(size.sizeSpanMin).body.heavySigmaCssPx);
    // And the token is the projection of that body onto one σ — between the two
    // widths it stands for, never outside them.
    expect(blurOf(platter)).toBeGreaterThan(body.sharpSigmaCssPx);
    expect(blurOf(platter)).toBeLessThanOrEqual(body.heavySigmaCssPx);
  });

  it("stays out of the way of forced colours, at every span", () => {
    // `glass: "none"` is a different surface, not a dimmer one — so the law has
    // nothing to gain there and must not smuggle a blur back in.
    const forced = resolveAccessibilityPolicy(systemWith({ forcedColors: true }));
    for (const span of [12, 96, 400]) {
      const render = cssTierDeclarations({ ...surface, policy: forced, spanPx: span, size });
      expect(render.host["backdrop-filter"], `span ${span}`).toBe("none");
      expect(render.host["--vitrea-blur"]).toBe("0px");
      expect(render.host["--vitrea-occlusion"]).toBe("1");
      // And no filtered layer at any span either: a body left standing would be
      // a blur the regime says is not there, wherever its declaration sits.
      expect(render.layers, `span ${span}`).toBeUndefined();
      expect(render.body.form).toBe("collapsed");
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
    // The law's own baseline is the surface that declares no span at all: since
    // W13 G1 there is no span at which the scatter is inert, so the reference the
    // fold is read against has to be the spanless declaration on each side.
    const nominalBase = blurOf(cssTierDeclarations(surface));
    const reducedBase = blurOf(cssTierDeclarations({ ...surface, policy: reduced }));

    // The preference's own frost still lands in full — the fold is on the size
    // law, not on the preference.
    expect(reducedBase).toBeCloseTo(nominalBase * REDUCED_TRANSPARENCY_FROST, 1);

    // And the size law's *addition* on top of it is scaled by the ladder's
    // reduced rung rather than applied whole.
    const added = (render: CssTierRender, base: number): number => blurOf(render) / base - 1;
    /*
     * A budget rather than six decimals, and the reason is the medium rather
     * than the law. `--vitrea-blur` is emitted through `px()`, which rounds to
     * two decimal places, so this ratio-of-ratios carries that quantisation. At
     * the σ = 8 this was written against the error sat under 1e-6; at the σ = 3
     * of 2026-08-31 every term still fell on the 0.01 grid; at the W11c base of
     * 1.25 (2026-09-03) the platters land off it (3.125, 3.664) and the rounding
     * shows. The identity itself is exact — it is the declaration that is
     * quantised.
     *
     * The budget is derived rather than picked. A ratio N/D of two rounded
     * declarations carries q/D from its numerator and q·(N/D)/D from its
     * denominator, with q = 0.005 the half-step; the nominal ratio's share
     * enters scaled by the same fold as the ratio itself.
     */
    const q = 0.005;
    const ratioBudget = (numerator: number, denominator: number): number =>
      (q * (1 + numerator / denominator)) / denominator;
    expect(
      Math.abs(
        added(reducedPlatter, reducedBase) -
          added(nominalPlatter, nominalBase) * MATERIAL_SOURCE_SIZE.refractionScale.approximate,
      ),
    ).toBeLessThan(
      ratioBudget(blurOf(reducedPlatter), reducedBase) +
        ratioBudget(blurOf(nominalPlatter), nominalBase) *
          MATERIAL_SOURCE_SIZE.refractionScale.approximate,
    );

    // Still a law, not an off switch: a platter under the preference is still
    // frostier than a control under it.
    expect(blurOf(reducedPlatter)).toBeGreaterThan(blurOf(reducedSmall));
    expect(occlusionOf(reducedPlatter)).toBeGreaterThanOrEqual(occlusionOf(reducedSmall));
    expect(occlusionOf(reducedPlatter)).toBeLessThanOrEqual(1);
  });

  /*
   * The projection is an AREA average, so it needs the surface's area and not
   * only its span (W13 G1, review finding). `root.ts` measures the host's border
   * box and declares both; a caller that declares only the span gets a square of
   * it, which is exactly right on a square and an over-estimate of the deep area
   * on a strip.
   */
  it("projects the ramp over the surface's own extents, not over a square of its span", () => {
    const own = { ...size, sizeScatterFloor: 0.4 } as const;
    const declared = (spanPx: number, extentsCssPx?: readonly [number, number]) =>
      blurOf(
        cssTierDeclarations({
          ...surface,
          spanPx,
          size: own,
          ...(extentsCssPx === undefined ? {} : { extentsCssPx }),
        }),
      );

    // A 320×160 bar and a 160×160 square share a span and do not share a mix.
    // The square is deeper on average than a strip of the same width is: its
    // mean depth is span/6 against span/4, because a square's corners pull area
    // toward the contour from two edges at once. So the bar keeps LESS of the
    // sharp component near its contour per unit area, and blurs more.
    expect(declared(160, [320, 160])).toBeGreaterThan(declared(160, [160, 160]));
    // A square's extents are what the span alone already implied.
    expect(declared(160, [160, 160])).toBe(declared(160));
    // And the tier writes the projection the optics module computes, over the
    // same extents — which is the number `size-law.test.ts` pins to a quadrature.
    const base = blurOf(cssTierDeclarations(surface));
    const emitted = (radius: number): number => Math.round(radius * 100) / 100;
    for (const [w, h] of [[320, 160], [160, 320], [1200, 44]] as const) {
      const mix = cssScatterThickness(Math.min(w, h), 1, own, PROJECTION_SCALE, [w, h]);
      expect(declared(Math.min(w, h), [w, h]), `${w}x${h}`).toBe(
        emitted(base * (1 + (own.sizeScatterGainMax - 1) * mix)),
      );
    }
  });

  /*
   * The device scale, which this tier took an input for in W16 G1.
   *
   * W13 Decision Log 5 refused one and W15 Decision Log 3 kept the refusal: the
   * candidate divided the single blur's width by the ratio, and the dry run on
   * the W14 bed measured that as −0.047 of `ssimMean` on the 2x large spans and
   * four broken dom-tier floors (claims §5.68). That measurement is about
   * projecting a MIX onto one Gaussian — the projection's best single σ really is
   * larger in CSS px at 2x — and it says nothing about either component's own
   * width. With the mix carried by a second layer and a mask, both widths are
   * device-pixel quantities and the ratio reaches them (charter Decision Log 2 (c)).
   *
   * What did not move is the projection. `--vitrea-blur` is a public number an
   * app matches with its own `blur()`, and the cost collapse degrades to the
   * form this tier drew before the wave, so both are still read at dpr 1 at
   * every ratio. Both halves are pinned here: a change to either has to say why.
   */
  it("keeps the projection on the 1x law while the body's widths follow the ratio", () => {
    const own = { ...size, sizeScatterFloor: 0.4 } as const;
    const base = blurOf(cssTierDeclarations(surface));
    const emitted = (radius: number): number => Math.round(radius * 100) / 100;
    let scaled = 0;
    let collapsed = 0;
    for (const span of [12, 96, 400]) {
      const mix = cssScatterThickness(span, 1, own, PROJECTION_SCALE);
      const nominal = base * (1 + (own.sizeScatterGainMax - 1) * mix);
      const at1x = cssTierDeclarations({ ...surface, spanPx: span, size: own });
      const at2x = cssTierDeclarations({
        ...surface,
        spanPx: span,
        size: own,
        devicePixelRatio: 2,
      });
      expect(blurOf(at1x), `span ${span}`).toBe(emitted(nominal));
      expect(blurOf(at2x), `span ${span} at dpr 2`).toBe(emitted(nominal));
      /*
       * The widths follow the ratio wherever there is a mix to carry. Where
       * there is none the body collapses onto the projection instead, and a
       * span may collapse at one ratio and not the other: the scatter floor is
       * a per-scale constant, so a span whose share vanishes at 2x has no heavy
       * component left to scale. Both outcomes are held below, and the two
       * counters are what stop the loop degrading into holding neither.
       */
      if (at1x.body.form === "two-layer" && at2x.body.form === "two-layer") {
        scaled += 1;
        /*
         * Both widths are the profile's own as DEVICE-pixel quantities, so both
         * would halve at dpr 2 but for the effective conversion — which is per
         * scale, 1.380 against 1.485, and so leaves the ratio of the two
         * conversions behind after the halving. The sharp component takes the
         * same conversion as the heavy one since W16 G1's re-form: one kernel,
         * one mip chain, one conversion (see `cssTierSharpSigmaCssPx`).
         */
        const conversion =
          scatterHeavyEffectiveRatioAtScale(2) / scatterHeavyEffectiveRatioAtScale(1);
        expect(at2x.body.sharpSigmaCssPx, `span ${span}`).toBeCloseTo(
          (at1x.body.sharpSigmaCssPx / 2) * conversion,
          12,
        );
        /*
         * The HEAVY width does not halve, and that is the second scale rather
         * than a bug. The fixture's two gains are equal, so the law itself is
         * scale-free here — but the renderer's kernel is not, and the effective
         * conversion the tier draws through is 1.38 at dpr 1 against 1.49 at
         * dpr 2 (measured on the renderer's own broadband captures; see
         * `SCATTER_HEAVY_EFFECTIVE_RATIO_1X`). So the 2x heavy width is the 1x
         * one halved and then carried by the ratio of the two conversions, and
         * the assertion says exactly that rather than asserting a halving that
         * would only pass while the conversion was inert.
         */
        expect(at2x.body.heavySigmaCssPx, `span ${span}`).toBeCloseTo(
          (at1x.body.heavySigmaCssPx / 2) * conversion,
          12,
        );
        expect(at2x.body.heavySigmaCssPx, `span ${span}`).toBeGreaterThan(
          at1x.body.heavySigmaCssPx / 2,
        );
      } else {
        // A collapsed body IS the projection — both of its widths are it — which
        // is what makes the collapse a degradation to one known form rather than
        // a second, scale-dependent material.
        for (const body of [at1x.body, at2x.body]) {
          if (body.form !== "collapsed") continue;
          collapsed += 1;
          expect(body.sharpSigmaCssPx, `span ${span}`).toBe(body.projectedSigmaCssPx);
          expect(body.heavySigmaCssPx, `span ${span}`).toBe(body.projectedSigmaCssPx);
        }
      }
    }
    expect(scaled).toBeGreaterThan(0);
    expect(collapsed).toBeGreaterThan(0);
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
  /*
   * These pin the shadow the MATERIAL resolved, which is `CssTierRender`'s own
   * field since W18 G1 and no longer a property of one element. The tier used to
   * write it on the host, and the host's three filter layers are its children —
   * so it sat inside its own body's `backdrop-filter` and its neighbours',
   * costing 0.0032 to 0.0096 of this tier's interior level where the renderer
   * moved by 0.00000 (claims §5.77 §3). It is now painted by one of three
   * carriers, and WHICH element paints it is the subject of the block below;
   * these read the resolved value so that the amplitude, the geometry and the
   * conversions are pinned once, on every carrier at once.
   */
  const shadowOf = (render: CssTierRender): string => render.outerShadow;
  /** The alpha out of a `box-shadow: … rgba(0, 0, 0, α)` declaration. */
  const alphaOf = (render: CssTierRender): number => {
    const value = shadowOf(render);
    if (value === "none") return 0;
    const match = /rgba\(0, 0, 0, ([\d.]+)\)$/.exec(value);
    if (match?.[1] === undefined) throw new Error(`unparsed box-shadow: ${value}`);
    return Number(match[1]);
  };

  /*
   * W18 G1's whole subject: WHICH element paints the shadow, and therefore
   * whether the tier's own `backdrop-filter` samples it.
   *
   * The order inside a stacking context is the element's own background and
   * border, then its negative-`z` children in `z-index` order, then its content.
   * The two filters are −3 and −2 and L3 is −1, so a shadow on L3 is painted
   * after both filters have sampled and a shadow on the host is painted before
   * them — which is the defect G0 measured at 0.0032 to 0.0096 of this tier's
   * interior level (claims §5.77 §3). Both branches are asserted, because the
   * fallback is a real branch a clipping host reaches.
   */
  it("hangs the shadow on L3 by default and on the host only under the fallback", () => {
    const value = shadowOf(cssTierDeclarations(surface));

    const carried = cssTierDeclarations({ ...surface, shadowCarrier: "layer" });
    expect(carried.host["box-shadow"]).toBe("none");
    expect(layersOf(carried).overlay["box-shadow"]?.endsWith(value)).toBe(true);
    // Written on every carrier, so a surface that changes carrier cannot leave
    // the other one's value behind.
    expect(cssTierDeclarations(surface).host["box-shadow"]).toBe("none");

    const fallback = cssTierDeclarations({ ...surface, shadowCarrier: "host" });
    expect(fallback.host["box-shadow"]).toBe(value);
    expect(layersOf(fallback).overlay["box-shadow"]).not.toContain(value);

    // Carrier B paints it from the group's last host, so neither element here
    // draws one — and the value still comes back for that host to use.
    const grouped = cssTierDeclarations({ ...surface, shadowCarrier: "group" });
    expect(grouped.host["box-shadow"]).toBe("none");
    expect(layersOf(grouped).overlay["box-shadow"]).not.toContain(value);
    expect(grouped.outerShadow).toBe(value);
  });

  it("writes the profile's own lengths, with box-shadow's blur convention applied", () => {
    // `filter: blur()` takes σ; `box-shadow` takes twice it (CSS Backgrounds 3).
    // Getting this wrong halves or doubles the shadow's reach in silence, so it
    // is asserted against the σ the profile states rather than against a literal.
    const shadow = MATERIAL_SOURCE_OUTER_SHADOW;
    expect(shadowOf(cssTierDeclarations(surface))).toBe(
      `0 ${shadow.offsetPx}px ${2 * shadow.sigmaPx}px ${shadow.spreadPx}px ` +
        `rgba(0, 0, 0, ${
          Math.round(outerShadowAlpha(outerShadowThinOcclusion(undefined, shadow)) * 1000) / 1000
        })`,
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
    const occlusion = MATERIAL_SOURCE_OUTER_SHADOW.thinOcclusionMid;
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

  it("goes flat under reduced transparency and out under forced colours", () => {
    /*
     * MEASURED, which the charter asked for before the fold was written. Under
     * the preference the reference's exterior is one level — flat at 0.192–0.202,
     * thin and thick together and over every backdrop (claims §5.62 §5) — so
     * this tier writes the profile's `reducedTransparencyOcclusion` itself rather
     * than a scaled anchor. It neither vanishes nor intensifies, and the
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
    const level = MATERIAL_SOURCE_OUTER_SHADOW.reducedTransparencyOcclusion;
    expect(reduced).toBe(Math.round(outerShadowAlpha(level) * 1000) / 1000);
    // The same level whatever the surface is standing over — a `box-shadow`
    // written from a scaled anchor would still carry the backdrop keying the
    // preference removes.
    for (const backdropLuminance of [0, 0.2141, 0.891]) {
      expect(
        alphaOf(
          cssTierDeclarations({
            ...surface,
            backdropLuminance,
            policy: resolveAccessibilityPolicy(systemWith({ reducedTransparency: true })),
          }),
        ),
        `backdrop ${backdropLuminance}`,
      ).toBe(reduced);
    }

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
    const patched = sourceOuterShadow({
      outerShadow: { thinOcclusionMid: 0.5, offsetPx: 12 },
    });
    expect(patched.thinOcclusionMid).toBe(0.5);
    expect(patched.offsetPx).toBe(12);
    // Unnamed fields keep the mirrored default, which is the renderer's own merge
    // rule and the reason a partial calibration patch is legal.
    expect(patched.sigmaPx).toBe(MATERIAL_SOURCE_OUTER_SHADOW.sigmaPx);

    expect(shadowOf(cssTierDeclarations({ ...surface, outerShadow: patched }))).toBe(
      `0 12px ${2 * patched.sigmaPx}px ${patched.spreadPx}px ` +
        `rgba(0, 0, 0, ${Math.round(outerShadowAlpha(0.5) * 1000) / 1000})`,
    );
    expect(
      shadowOf(
        cssTierDeclarations({
          ...surface,
          outerShadow: { ...patched, thinOcclusionMid: 0, thinOcclusionBright: 0 },
        }),
      ),
    ).toBe("none");
  });

  it("refuses a patch that still names W8's retired single amplitude", () => {
    /*
     * The same refusal the renderer makes, on the same profile document — a
     * patch one tier took and the other threw on would be a profile that means
     * two different things. `{ outerShadow: { occlusion: 0 } }` was the way to
     * stand the facet down and W14 G1 retired it (claims §5.62); merged in
     * silence it would render the shipped shadow while recording itself as the
     * configuration that ran.
     */
    const retired = { outerShadow: { occlusion: 0 } } as unknown as Parameters<
      typeof sourceOuterShadow
    >[0];
    expect(() => sourceOuterShadow(retired)).toThrow(/outerShadow\.occlusion was retired/);
    expect(() => sourceOuterShadow(retired)).toThrow(
      /thinOcclusionMid.*thickOcclusionAt160.*liftAmplitude/s,
    );
    expect(sourceOuterShadow({ outerShadow: { thinOcclusionMid: 0 } }).thinOcclusionMid).toBe(0);
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
    // The LENGTHS are what may not move with the span, and they do not.
    expect(shadowOf(small).split("rgba")[0]).toBe(shadowOf(platter).split("rgba")[0]);
    /*
     * The amplitude does, and since W14 G1 that is the law rather than the gain:
     * a thin surface resolves the thin regime's mid plateau and a platter
     * resolves the thick regime's span law, which the bed measures deeper
     * (0.370 at span 96 against 0.33 below the knee). The `sizeGain` seam is a
     * SECOND thing on top of that, and it is still the identity.
     *
     * The thin surface reads the anchor straight, because below the knee there is
     * no lift to fold; the platter reads the thick anchor MINUS the lift this tier
     * cannot paint, which is `cssTierShadowAlpha`'s derivation and is why the
     * platter's expectation is written through it (claims §5.65 §6(ii)).
     */
    expect(alphaOf(small)).toBeCloseTo(
      Math.round(outerShadowAlpha(MATERIAL_SOURCE_OUTER_SHADOW.thinOcclusionMid) * 1000) / 1000,
      12,
    );
    const platterAlpha = cssTierShadowAlpha(
      MATERIAL_SOURCE_OUTER_SHADOW,
      undefined,
      320,
      sizeThickness(320),
    );
    expect(alphaOf(platter)).toBeCloseTo(Math.round(platterAlpha * 1000) / 1000, 12);
    expect(platterAlpha).toBeLessThan(
      outerShadowAlpha(MATERIAL_SOURCE_OUTER_SHADOW.thickOcclusionAt160),
    );

    // With a gain, the same curve moves it — and only the amplitude, never the
    // lengths, which is the half of the facet the bed actually settled.
    const gained = { ...MATERIAL_SOURCE_OUTER_SHADOW, sizeGain: 0.5 };
    const thin = cssTierDeclarations({ ...surface, spanPx: 24, outerShadow: gained });
    const thick = cssTierDeclarations({ ...surface, spanPx: 320, outerShadow: gained });
    expect(alphaOf(thick)).toBeGreaterThan(alphaOf(thin));
    expect(shadowOf(thin).split("rgba")[0]).toBe(shadowOf(thick).split("rgba")[0]);
  });

  /*
   * W14 G1 on this tier (claims §5.62; W14 Decision Log 1 question 2, decided
   * (a)). The `box-shadow` stays pure BLACK — that is what makes it a multiply —
   * and what changes is the alpha: the same two-regime law the GPU tier runs,
   * resolved at the same backdrop luminance statistic. The LIFT is not here and
   * cannot be: it needs the backdrop's own light outside the element, which one
   * `box-shadow` has no access to.
   */
  it("keys the alpha on the backdrop, on each of the three measured anchors", () => {
    const alphaOver = (luminance: number | undefined): number =>
      alphaOf(
        cssTierDeclarations(
          luminance === undefined ? surface : { ...surface, backdropLuminance: luminance },
        ),
      );
    const rounded = (occlusion: number): number =>
      Math.round(outerShadowAlpha(occlusion) * 1000) / 1000;
    const shadow = MATERIAL_SOURCE_OUTER_SHADOW;

    // `mid-dark-solid` 0.06, `hc-text` 0.74, `light-solid` 0.891.
    expect(alphaOver(OUTER_SHADOW_THIN_L.midFrom)).toBe(rounded(shadow.thinOcclusionMid));
    expect(alphaOver(OUTER_SHADOW_THIN_L.midTo)).toBe(rounded(shadow.thinOcclusionMid));
    expect(alphaOver(OUTER_SHADOW_THIN_L.bright)).toBe(rounded(shadow.thinOcclusionBright));
    // Over `light-solid` the shadow is a third of what it is over the
    // checkerboard, which is the user's by-eye gap ("the shadow is darker on the
    // light-solid capsule") closing on this tier with no new element.
    expect(alphaOver(OUTER_SHADOW_THIN_L.bright)).toBeLessThan(
      alphaOver(OUTER_SHADOW_THIN_L.midTo) * 0.6,
    );
    // `dark-solid` and `impulse`: the declaration is not a faint shadow, it is
    // no shadow at all.
    expect(shadowOf(cssTierDeclarations({ ...surface, backdropLuminance: 0.0039 }))).toBe("none");
    // And an unmeasured backdrop keeps the mid plateau, which is the same
    // fallback the renderer takes, so the tiers cannot diverge there.
    expect(alphaOver(undefined)).toBe(rounded(shadow.thinOcclusionMid));
  });

  it("carries the geometry and the adaptive alpha and no lift, which is Decision Log 1 (a)", () => {
    // The colour is still exactly black at every backdrop and every span: the
    // lift would need a second element with `backdrop-filter`, and this tier does
    // not grow one in this wave.
    for (const backdropLuminance of [0.06, 0.5, 0.891]) {
      for (const spanPx of [32, 96, 160]) {
        expect(
          shadowOf(cssTierDeclarations({ ...surface, backdropLuminance, spanPx })),
          `L ${backdropLuminance} span ${spanPx}`,
        ).toMatch(/^0 [\d.]+px [\d.]+px [\d.-]+px rgba\(0, 0, 0, [\d.]+\)$/);
      }
    }
    // The constants are mirrored even though this tier does not draw them, so a
    // profile patch cannot mean two different things on the two sides.
    expect(MATERIAL_SOURCE_OUTER_SHADOW.liftAmplitude).toBeGreaterThan(0);
    expect(MATERIAL_SOURCE_OUTER_SHADOW.liftBlurSigmaCss).toBe(40);
  });
});

describe("the two review findings on the ramp's projection (W13 G1)", () => {
  it("takes the group's sigma as the maximum PROJECTED sigma over its members, in any order", () => {
    // Two members of the same short span and different aspect: the strip's
    // projection is heavier than the square's, because the ramp's area average
    // is over the member's own box. The old rule picked by short span with a
    // strict greater-than, so the square registered first kept its smaller σ.
    const square: readonly [number, number] = [160, 160];
    const strip: readonly [number, number] = [1200, 160];
    const fold = MATERIAL_SOURCE_SIZE.refractionScale.true;
    const base = MATERIAL_OPTICS.regular.blurRadius;
    const alone = (member: readonly [number, number]): number =>
      groupScatterSigma(base, fold, [member]);
    expect(alone(strip)).toBeGreaterThan(alone(square));
    expect(groupScatterSigma(base, fold, [square, strip])).toBeCloseTo(alone(strip), 12);
    expect(groupScatterSigma(base, fold, [strip, square])).toBeCloseTo(alone(strip), 12);
    // Nothing measured: the projection at span 0, where the old rule left an
    // unmeasured group too.
    expect(groupScatterSigma(base, fold, [])).toBeCloseTo(
      sizeScatterSigmaAt(base, cssScatterThickness(0, fold)),
      12,
    );
  });

  it("a zero mix is the policy optics unchanged, and the body collapses onto it", () => {
    /*
     * A patched profile with no floor, on a surface at or below `sizeSpanMin`,
     * has sizeK 0 and scatterK 0, so the fast path is exact and the 1x width is
     * what it must emit — on the token, and on the one layer that draws it.
     *
     * A zero share is also the third way into W16 G1's cost collapse: with no
     * heavy component there is no mix to carry, so the body is the single
     * `backdrop-filter` this tier drew before the wave, at exactly the width it
     * drew then. The ratio is left at its default of 1, which is what a caller
     * with no viewport reading honestly has — and the patch stands down the 1x
     * floor, so this is a statement about that ratio rather than about every
     * one, which is why the title no longer claims all of them.
     */
    const size = sourceSize({ sizeScatterFloor: 0 });
    const render = cssTierDeclarations({
      ...surface,
      size,
      spanPx: MATERIAL_SOURCE_SIZE.sizeSpanMin,
    });
    const blur = Number.parseFloat((render.host["--vitrea-blur"] ?? "0px").replace("px", ""));
    expect(blur).toBe(Number(MATERIAL_OPTICS.regular.blurRadius.toFixed(2)));
    expect(render.body.form).toBe("collapsed");
    expect(render.body.projectedSigmaCssPx).toBe(MATERIAL_OPTICS.regular.blurRadius);
    expect(layersOf(render).sharp["backdrop-filter"]).toContain(`blur(${blur}px)`);
    expect(layersOf(render).heavy.display).toBe("none");
  });
});

