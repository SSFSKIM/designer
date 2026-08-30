/**
 * Backdrop tone adaptation (W7) — the axis Apple's material has and this one did
 * not, and the four properties every measured number rests on.
 *
 * The constants ARE measured, against the settled bed, so unlike the tint tone
 * map this file may assert what they mean: full adaptation at the darkest
 * calibration backdrop for a 44 px surface, roughly a quarter of it for a 96 px
 * one, and exactly none of it anywhere in the ordinary range. What it does not
 * assert is the shape of the knee between those, which the bed does not identify
 * — see `MaterialProfile.backdropToneLow` for the gap and what would close it.
 */

import { describe, expect, it } from "vitest";

import { WGSL_OPTICS_PASS } from "../src/wgsl";
import {
  adaptedTintAlpha,
  adaptedTintColour,
  backdropToneAdaptation,
  backdropToneSizeBiasUnderPolicy,
  backdropToneUnderPolicy,
  DEFAULT_MATERIAL_PROFILE,
  sizeThickness,
  sizeThicknessUnderPolicy,
  tintedTintColour,
  withMaterialOverrides,
  type MaterialPolicyView,
  type Rgb,
} from "../src/index";

const white: Rgb = [1, 1, 1];
const nearBlack: Rgb = [0.0117, 0.0117, 0.0117];

const policy = (patch: Partial<MaterialPolicyView> = {}): MaterialPolicyView => ({
  glass: "material",
  frost: "nominal",
  refraction: "nominal",
  occlusion: "nominal",
  border: "nominal",
  ambientTint: "nominal",
  foreground: "adaptive",
  ...patch,
});

/** The canonical spans, and the thicknesses the size law gives them. */
const ALPHA = DEFAULT_MATERIAL_PROFILE.optics.regular.tintAlpha;
const CAPSULE = sizeThickness(44);
const RRECT_MD = sizeThickness(96);
const RRECT_SM = sizeThickness(32);

describe("the adaptation curve", () => {
  it("is inert across the whole ordinary backdrop range, at every span", () => {
    // The four backdrops the bed calls ordinary: photo, checkerboard, hc-text,
    // light-solid. Every cell over them is byte-unchanged by this axis, which is
    // what lets it land without re-fitting anything else.
    for (const backdrop of [0.205, 0.5, 0.53, 0.891]) {
      for (const thickness of [RRECT_SM, CAPSULE, RRECT_MD]) {
        expect(backdropToneAdaptation(backdrop, thickness)).toBe(0);
      }
    }
  });

  it("adapts a small surface completely over the darkest calibration backdrop", () => {
    // `dark-solid`, linear 0.0117 — where the reference's capsule is byte-identical
    // to its own background in every standard profile, at both scales.
    expect(backdropToneAdaptation(0.0117, CAPSULE)).toBeCloseTo(1, 4);
    expect(backdropToneAdaptation(0.0117, RRECT_SM)).toBeCloseTo(1, 6);
  });

  it("holds ALL of a large surface's own appearance over the same backdrop", () => {
    /*
     * REFITTED 2026-08-31, and the assertion flipped from "most" to "all".
     *
     * W7 fitted this against the light-versus-dark separation estimator, which
     * put the 96 px surface's adaptation at 0.256 and the curve at 0.241. The
     * active bed's own interior LEVEL disagrees: the reference reads 0.4844
     * there, against 0.466 for an unadapted surface at the refitted tint alpha
     * and 0.3566 for one adapted by a quarter.
     *
     * The tie was broken on `impulse__rrect-md__rest`, which is a validation
     * scene and was fitted to by neither setting. At the old size bias vitrea
     * renders 0.2858 against a reference of 0.4358 (ΔE 0.02344); at the refitted
     * 0.13 it renders 0.4594 (ΔE 0.00378) — six times better. So the size gate is
     * harder than W7 measured: a 96 pt surface over the darkest calibration
     * backdrop does not adapt at all.
     *
     * The estimator was not wrong so much as inapplicable — its algebra cancels
     * the transmission only if both colour schemes share one tint alpha, and the
     * refitted profiles are at 0.46 and 0.97. Claims §5.13.
     */
    expect(backdropToneAdaptation(0.0117, RRECT_MD)).toBe(0);
    // Still a size GATE rather than an off switch: the same backdrop under a
    // capsule adapts completely, which is the contrast the axis exists to draw.
    expect(backdropToneAdaptation(0.0117, CAPSULE)).toBeCloseTo(1, 4);
  });

  it("is monotone in the backdrop and in the span", () => {
    const backdrops = [0, 0.01, 0.02, 0.04, 0.06, 0.09, 0.12, 0.15, 0.2, 0.4];
    for (const thickness of [0, 0.25, 0.5, 0.75, 1]) {
      const levels = backdrops.map((b) => backdropToneAdaptation(b, thickness));
      for (let i = 1; i < levels.length; i += 1) {
        expect(levels[i] as number).toBeLessThanOrEqual(levels[i - 1] as number);
      }
    }
    for (const backdrop of [0, 0.02, 0.05, 0.08]) {
      const levels = [0, 0.25, 0.5, 0.75, 1].map((t) => backdropToneAdaptation(backdrop, t));
      for (let i = 1; i < levels.length; i += 1) {
        expect(levels[i] as number).toBeLessThanOrEqual(levels[i - 1] as number);
      }
    }
  });

  it("is continuous — no step anywhere across the transition", () => {
    // A step would be the failure mode this axis is most exposed to: two extreme
    // backdrops in the bed and nothing in between. 2000 samples across the whole
    // range, and no neighbouring pair may move by more than the smoothstep's own
    // maximum slope allows.
    const steps = 2000;
    for (const thickness of [0, CAPSULE, 0.5, RRECT_MD]) {
      let previous = backdropToneAdaptation(0, thickness);
      for (let i = 1; i <= steps; i += 1) {
        const value = backdropToneAdaptation(i / steps, thickness);
        expect(Math.abs(value - previous)).toBeLessThan(0.01);
        previous = value;
      }
    }
  });

  it("has a zero derivative at both ends, so nothing kinks where it turns on", () => {
    const { backdropToneLow: low, backdropToneHigh: high } = DEFAULT_MATERIAL_PROFILE;
    const h = 1e-4;
    const slope = (x: number): number =>
      Math.abs(backdropToneAdaptation(x + h, 0) - backdropToneAdaptation(x - h, 0)) / (2 * h);
    // The steepest point of a smoothstep is its midpoint; the edges must be flat
    // against it, or the material would visibly click on as a backdrop darkens.
    const steepest = slope((low + high) / 2);
    expect(slope(low)).toBeLessThan(steepest / 100);
    expect(slope(high)).toBeLessThan(steepest / 100);
  });

  it("saturates at the profile's ceiling and never past it", () => {
    for (const backdrop of [-1, 0, 0.005]) {
      expect(backdropToneAdaptation(backdrop, 0)).toBeLessThanOrEqual(
        DEFAULT_MATERIAL_PROFILE.backdropToneMax,
      );
    }
    expect(backdropToneAdaptation(0, 0)).toBe(DEFAULT_MATERIAL_PROFILE.backdropToneMax);
  });

  it("switches off as data, so a profile can decline the axis entirely", () => {
    const off = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { backdropToneMax: 0 });
    for (const backdrop of [0, 0.01, 0.5, 1]) {
      expect(backdropToneAdaptation(backdrop, 0, off)).toBe(0);
    }
  });

  it("degrades to a step rather than to NaN when a patch collapses the band", () => {
    const collapsed = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      backdropToneLow: 0.3,
      backdropToneHigh: 0.3,
    });
    expect(backdropToneAdaptation(0.1, 0, collapsed)).toBe(1);
    expect(backdropToneAdaptation(0.5, 0, collapsed)).toBe(0);
  });
});

describe("the size gate and the size law's band", () => {
  it("is what the band 32…96 buys: the two dark cells cannot both be right otherwise", () => {
    /*
     * Measured (W7, re-measured by the cascade 2026-08-31): a band ending at 64
     * lifts the 44 px capsule's effective backdrop past the curve's low edge and
     * it stops adapting fully; a band ending at 128 makes the 96 px surface adapt
     * where the fitted band leaves it alone. The tone axis pins the same 32…96 W2
     * set from the reference's transmission — two independent measurements, one
     * band, and the band survived a refit of every constant around it.
     *
     * The wide arm's figure moved with the size bias (0.09 → 0.13): the 96 px
     * surface reads 0.2047 at a band of 128 against exactly 0 at the fitted band,
     * where before it read over 0.4 against 0.241. The discriminator is the same
     * and it is now a cleaner one — a band that is too wide turns the axis on for
     * a surface the reference says it is off for.
     */
    const narrow = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { sizeSpanMax: 64 });
    const wide = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { sizeSpanMax: 128 });
    expect(backdropToneAdaptation(0.0117, sizeThickness(44, narrow), narrow)).toBeLessThan(0.95);
    expect(backdropToneAdaptation(0.0117, sizeThickness(96, wide), wide)).toBeGreaterThan(0.15);
    expect(backdropToneAdaptation(0.0117, RRECT_MD)).toBe(0);
  });
});

describe("the accessibility fold", () => {
  it("runs at full strength under the nominal regime", () => {
    expect(backdropToneUnderPolicy(policy())).toBe(1);
  });

  it("narrows under increased contrast, on the axis the composition contract names", () => {
    // Increased contrast is coupled to reduced transparency on macOS, so both
    // folds apply — which is the state a real user is actually in.
    expect(backdropToneUnderPolicy(policy({ ambientTint: "reduced" }))).toBeCloseTo(
      DEFAULT_MATERIAL_PROFILE.reducedTintAdaptation,
      12,
    );
    expect(
      backdropToneUnderPolicy(policy({ ambientTint: "reduced", refraction: "reduced" })),
    ).toBeCloseTo(
      DEFAULT_MATERIAL_PROFILE.reducedTintAdaptation *
        DEFAULT_MATERIAL_PROFILE.refractionScale.approximate,
      12,
    );
  });

  it("narrows under reduced transparency, which touches no tint axis at all", () => {
    // The policy wins. At full strength this axis dissolves a surface into its
    // backdrop, and dissolving is the opposite of the raised occlusion reduced
    // transparency asked for.
    expect(backdropToneUnderPolicy(policy({ refraction: "reduced" }))).toBe(
      DEFAULT_MATERIAL_PROFILE.refractionScale.approximate,
    );
    expect(backdropToneUnderPolicy(policy({ refraction: "reduced" }))).toBeLessThan(1);
  });

  it("stops entirely under forced colours, from either fold", () => {
    expect(backdropToneUnderPolicy(policy({ ambientTint: "none", refraction: "none" }))).toBe(0);
  });

  it("hands the shader a bias that restores the geometric thickness exactly", () => {
    // The shader multiplies by the POLICY-FOLDED thickness, because there is one
    // thickness in the pipeline and it rides `aux.z`. Pre-dividing by the same cap
    // is what makes the gate geometric on both sides of that channel.
    for (const p of [
      policy(),
      policy({ refraction: "reduced" }),
      policy({ ambientTint: "reduced", refraction: "reduced" }),
    ]) {
      for (const span of [32, 44, 60, 96, 160]) {
        expect(
          backdropToneSizeBiasUnderPolicy(p) * sizeThicknessUnderPolicy(span, p),
        ).toBeCloseTo(DEFAULT_MATERIAL_PROFILE.backdropToneSizeBias * sizeThickness(span), 12);
      }
    }
  });

  it("returns a finite bias where the cap is zero, rather than an infinity", () => {
    expect(backdropToneSizeBiasUnderPolicy(policy({ refraction: "none" }))).toBe(0);
  });
});

describe("adaptedTintColour, and the composition order", () => {
  it("is the identity at zero adaptation — the pre-W7 material, exactly", () => {
    expect(adaptedTintColour(white, nearBlack, 0, ALPHA)).toBe(white);
  });

  it("becomes the backdrop at full adaptation, which is what makes the surface vanish", () => {
    // The interior composite is mix(backdrop, tint, alpha). With tint === backdrop
    // that is the backdrop for ANY alpha, so the material keeps its rim and its
    // inner shadow and loses nothing else — the reference's capsule over
    // `dark-solid`, which is byte-identical to its own background.
    const adapted = adaptedTintColour(white, nearBlack, 1, ALPHA);
    for (const index of [0, 1, 2] as const) {
      expect(adapted[index]).toBeCloseTo(nearBlack[index], 12);
    }
    const alpha = DEFAULT_MATERIAL_PROFILE.optics.regular.tintAlpha;
    const interior = nearBlack[0] * (1 - alpha) + adapted[0] * alpha;
    expect(interior).toBeCloseTo(nearBlack[0], 12);
  });

  it("takes the backdrop's colour and not merely its level", () => {
    const warm: Rgb = [0.06, 0.02, 0.01];
    const adapted = adaptedTintColour(white, warm, 1, ALPHA);
    expect(adapted[0]).toBeGreaterThan(adapted[1]);
    expect(adapted[1]).toBeGreaterThan(adapted[2]);
  });

  it("comes BEFORE the author tint: a full-strength tint is its own adaptation", () => {
    // The contract, in one assertion. The shader mixes the tone onto the adapted
    // neutral, so at strength 1 the adaptation is replaced outright.
    const seed: Rgb = [0.8, 0.2, 0.05];
    const adapted = adaptedTintColour(white, nearBlack, 1, ALPHA);
    const tintedOverAdapted = tintedTintColour(adapted, { color: seed, strength: 1 }, 0.01, 1);
    const tintedOverNeutral = tintedTintColour(white, { color: seed, strength: 1 }, 0.01, 1);
    for (const index of [0, 1, 2] as const) {
      expect(tintedOverAdapted[index]).toBeCloseTo(tintedOverNeutral[index] as number, 12);
    }
  });

  it("and a partial tint moves with it", () => {
    const seed: Rgb = [0.8, 0.2, 0.05];
    const adapted = adaptedTintColour(white, nearBlack, 1, ALPHA);
    const half = tintedTintColour(adapted, { color: seed, strength: 0.5 }, 0.01, 1);
    const unadapted = tintedTintColour(white, { color: seed, strength: 0.5 }, 0.01, 1);
    expect(half[0]).toBeLessThan(unadapted[0] as number);
  });
});

describe("the scheme semantics — one law, applied inside whichever scheme is active", () => {
  it("adapts a dark-scheme material toward the same backdrop, from its own neutral", () => {
    // Measured: over `dark-solid` the DARK reference's capsule is also byte-identical
    // to the background, and its 96 px surface also holds most of its own level.
    // So the axis is within-scheme — the profile sets the neutral, this moves away
    // from it — rather than a crossover between two scheme tints, which would
    // double-adapt a profile whose neutral is already dark.
    const darkNeutral: Rgb = [0.05, 0.05, 0.05];
    const adapted = adaptedTintColour(darkNeutral, nearBlack, backdropToneAdaptation(0.0117, CAPSULE), ALPHA);
    for (const index of [0, 1, 2] as const) {
      expect(adapted[index]).toBeCloseTo(nearBlack[index], 4);
    }
    /*
     * A partial adaptation has to be read at a thickness the refitted size gate
     * still leaves inside the transition — the 96 px surface over this backdrop
     * now sits past the curve's high edge entirely (see "holds ALL of a large
     * surface's own appearance"), so it is no longer an example of a partial
     * anything. Half thickness is, and the property under test is the same one:
     * the material moves from its own scheme's neutral toward the backdrop
     * without ever crossing to the other scheme's tint.
     */
    const partialAdaptation = backdropToneAdaptation(0.0117, 0.5);
    expect(partialAdaptation).toBeGreaterThan(0);
    expect(partialAdaptation).toBeLessThan(1);
    const partial = adaptedTintColour(darkNeutral, nearBlack, partialAdaptation, ALPHA);
    expect(partial[0]).toBeGreaterThan(nearBlack[0]);
    expect(partial[0]).toBeLessThan(darkNeutral[0]);
  });

  it("is the same curve for both schemes — the profile carries no scheme of its own", () => {
    // The dark calibration profile patches tints, not this axis, and nothing here
    // reads a scheme. Stated as a test so a future scheme-keyed variant has to
    // change it deliberately.
    expect(DEFAULT_MATERIAL_PROFILE.backdropToneMax).toBe(1);
    expect(backdropToneAdaptation(0.0117, CAPSULE)).toBeCloseTo(
      backdropToneAdaptation(0.0117, CAPSULE, DEFAULT_MATERIAL_PROFILE),
      12,
    );
  });
});

describe("adaptedTintAlpha, and the surface's own appearance", () => {
  it("lifts the occlusion by the fraction of transparency the adaptation takes", () => {
    // The same "fraction of what is left" shape as `increasedOcclusionLift`, so it
    // lifts strictly for every nominal below 1 whatever a retune moves nominal to.
    expect(adaptedTintAlpha(ALPHA, 0)).toBe(ALPHA);
    expect(adaptedTintAlpha(ALPHA, 1)).toBe(1);
    expect(adaptedTintAlpha(0.1, 0.5)).toBeCloseTo(0.55, 12);
    expect(adaptedTintAlpha(ALPHA, 0.5)).toBeGreaterThan(ALPHA);
  });

  it("clamps rather than extrapolating past either end", () => {
    expect(adaptedTintAlpha(ALPHA, -1)).toBe(ALPHA);
    expect(adaptedTintAlpha(ALPHA, 2)).toBe(1);
  });
});

/*
 * The shader is where the per-pixel half of this axis lives, and there is no WGSL
 * compiler in a Node test — `e2e/gpu` compiles it on a real adapter. What can be
 * checked here is what the string must contain, in the spirit of
 * `wgsl-contract.test.ts`: three properties whose absence would be silent.
 */
describe("the optics pass's statement of the axis", () => {
  it("carries both uniform slots the CPU writes", () => {
    expect(WGSL_OPTICS_PASS).toContain("toneAdapt : vec4f");
    expect(WGSL_OPTICS_PASS).toContain("toneColour : vec4f");
  });

  it("stands the axis down with no backdrop and with no measured tone", () => {
    // Two guards, and both matter: the backdrop vector is a zero rather than a
    // measurement where there is none, and a group whose tone nobody could read
    // gets a strength of zero rather than a guessed level. Reading either as a
    // black backdrop would dissolve the surface into nothing.
    expect(WGSL_OPTICS_PASS).toContain("if (ou.flags.x > 0.5 && ou.toneAdapt.w > 0.0)");
  });

  it("evaluates the curve without smoothstep, so a collapsed band is not a NaN", () => {
    const body = WGSL_OPTICS_PASS.slice(WGSL_OPTICS_PASS.indexOf("var toneAdapt"));
    const curve = body.slice(0, body.indexOf("let sizedAlpha"));
    expect(curve).not.toContain("smoothstep");
    expect(curve).toContain("max(ou.toneAdapt.y - ou.toneAdapt.x, 1e-6)");
  });

  it("fades the rim, the specular and the inner shadow on the one factor", () => {
    // The marks that say a surface is here rather than what is behind it. All of
    // them, or the surface leaves an outline where the reference leaves nothing.
    expect(WGSL_OPTICS_PASS).toContain("let present = 1.0 - toneAdapt;");
    expect(WGSL_OPTICS_PASS).toContain("profile * shadowDepth * ou.light.w * present");
    expect(WGSL_OPTICS_PASS).toContain("rw * (ou.rim.y + spec) * present");
  });
});
