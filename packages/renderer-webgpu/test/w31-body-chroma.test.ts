/**
 * W31 G3 — the body's chroma retention, as an identity at 0 and as an exact
 * luma-preserver everywhere else (claims §5.161 §5, §5.164).
 *
 * The leaf is an operator in `wgsl/optics.ts` and a WGSL function cannot be
 * called from a unit test, so the law is restated here as arithmetic — the
 * convention `w31-gate-groups.test.ts` and `w30-inert-laws.test.ts` already
 * follow — with the shader's own text asserted beside it so the restatement and
 * the source cannot drift apart silently.
 *
 * Three claims, and they are different claims:
 *
 *  1. **At retention 0 the composite is BIT-IDENTICAL.** Not "close": the
 *     shader returns `colour` before touching a divisor, so the value that
 *     leaves is the value that arrived. That is what lets the 34 goldens be
 *     byte-identical across the commit that added the leaf and what lets
 *     `MATERIAL_IDENTITY_TABLE` drop it from every document's fingerprint.
 *  2. **Linear luma is held at every retention, by construction.** Both
 *     endpoints of the mix carry luma exactly `Y` — `colour` by definition and
 *     the target because it is the backdrop scaled to `Y` — and linear luma is a
 *     linear functional. The renormalisation in the shader is an f32 rounding
 *     guard; in doubles the mix already lands on `Y`, and the sweep below shows
 *     the residual is at the arithmetic's own floor rather than at a tolerance
 *     somebody chose. The level stop of claims §5.161 §7 (c) rests on this.
 *  3. **Gamut is taken at a held luma, never per channel.** A per-channel clamp
 *     would move the level, which is the one thing this operator may not do.
 *
 * The fail-before half is explicit: a non-zero retention MOVES the colour on a
 * chromatic backdrop, so none of the identities above is a sweep over a law that
 * does nothing.
 */

import { describe, expect, it } from "vitest";

import {
  bodyChromaRetentionUnderPolicy,
  DEFAULT_MATERIAL_PROFILE,
  NOMINAL_MATERIAL_POLICY,
  occlusionLiftForPolicy,
  withMaterialOverrides,
  type MaterialPolicyView,
} from "../src/material";
import { WGSL_OPTICS_PASS } from "../src/wgsl";

const W: readonly [number, number, number] = [0.2126, 0.7152, 0.0722];
type Rgb = readonly [number, number, number];

const luma = (c: Rgb): number => c[0] * W[0] + c[1] * W[1] + c[2] * W[2];

/** `wgsl/optics.ts`'s `gamut_at_luma`, restated. */
function gamutAtLuma(c: Rgb, Y: number): Rgb {
  let t = 1;
  for (const channel of c) {
    const d = channel - Y;
    if (d > 1e-7) t = Math.min(t, (1 - Y) / d);
    else if (d < -1e-7) t = Math.min(t, -Y / d);
  }
  const k = Math.min(1, Math.max(0, t));
  return [Y + (c[0] - Y) * k, Y + (c[1] - Y) * k, Y + (c[2] - Y) * k];
}

/** `wgsl/optics.ts`'s `body_chroma_retention`, restated. */
function bodyChromaRetention(colour: Rgb, backdrop: Rgb, retention: number): Rgb {
  if (retention <= 0) return colour;
  const Y = luma(colour);
  if (!(Y > 1e-6 && Y <= 1)) return colour;
  const Yb = luma(backdrop);
  if (Yb <= 1e-6) return colour;
  const scale = Y / Yb;
  const r = Math.min(1, Math.max(0, retention));
  const mix = (i: 0 | 1 | 2): number => colour[i] + (backdrop[i] * scale - colour[i]) * r;
  let restored: Rgb = [mix(0), mix(1), mix(2)];
  const Yr = luma(restored);
  if (Yr > 1e-6) {
    const k = Y / Yr;
    restored = [restored[0] * k, restored[1] * k, restored[2] * k];
  }
  return gamutAtLuma(restored, Y);
}

/** The bed: colours the composite can produce and backdrops it looks through. */
const BACKDROPS: readonly Rgb[] = [
  [0.02, 0.02, 0.02],
  [0.6, 0.12, 0.9], // `mid-chroma-solid`, sRGB (213, 2, 255) in linear light
  [0.05, 0.42, 0.08],
  [0.9, 0.2, 0.06],
  [0.13, 0.13, 0.13],
  [0.35, 0.4, 0.62],
  [0.95, 0.95, 0.9],
  [0.0004, 0.0004, 0.0004],
];
const NEUTRALS: readonly Rgb[] = [
  [0.02, 0.02, 0.02],
  [0.17, 0.17, 0.17],
  [0.5, 0.5, 0.5],
  [0.82, 0.82, 0.82],
];
const ALPHAS = [0, 0.095, 0.3, 0.513, 0.75, 0.9, 1];
const RETENTIONS = [0, 0.05, 0.25, 0.5, 0.75, 0.9, 0.97, 1];

/** Every composite the bed produces: `mix(backdrop, neutral, presentAlpha)`. */
const COMPOSITES: readonly { colour: Rgb; backdrop: Rgb }[] = BACKDROPS.flatMap((backdrop) =>
  NEUTRALS.flatMap((neutral) =>
    ALPHAS.map((alpha) => ({
      colour: [
        backdrop[0] + (neutral[0] - backdrop[0]) * alpha,
        backdrop[1] + (neutral[1] - backdrop[1]) * alpha,
        backdrop[2] + (neutral[2] - backdrop[2]) * alpha,
      ] as Rgb,
      backdrop,
    })),
  ),
);

describe("W31's body chroma retention (claims §5.161 §5, §5.164)", () => {
  it("ships at its inert identity 0", () => {
    // A post-seal leaf's default IS its identity, forever: the digests recorded
    // under `MATERIAL_IDENTITY_TABLE` are taken with this leaf dropped at this
    // value.
    expect(DEFAULT_MATERIAL_PROFILE.bodyChromaRetention).toBe(0);
  });

  it("the composite is bit-identical at retention 0", () => {
    for (const { colour, backdrop } of COMPOSITES) {
      const out = bodyChromaRetention(colour, backdrop, 0);
      expect(out[0]).toBe(colour[0]);
      expect(out[1]).toBe(colour[1]);
      expect(out[2]).toBe(colour[2]);
    }
  });

  it("linear luma is held at every retention", () => {
    // The by-construction proof, numerically. The worst relative movement over
    // the bed is 4.35e-16, under TWO ULP of a double (`Number.EPSILON` is
    // 2.22e-16); the bound is four, for headroom on another platform's libm.
    // It is a statement about the arithmetic and not a tolerance chosen to
    // admit a measurement — the shader's renormalisation is an f32 rounding
    // guard, and in doubles the mix already lands on `Y`.
    let worst = 0;
    for (const { colour, backdrop } of COMPOSITES) {
      const before = luma(colour);
      if (!(before > 1e-6)) continue;
      for (const retention of RETENTIONS) {
        const after = luma(bodyChromaRetention(colour, backdrop, retention));
        worst = Math.max(worst, Math.abs(after - before) / before);
      }
    }
    expect(worst).toBeLessThan(4 * Number.EPSILON);
  });

  it("keeps every channel in gamut at every retention", () => {
    for (const { colour, backdrop } of COMPOSITES) {
      for (const retention of RETENTIONS) {
        for (const channel of bodyChromaRetention(colour, backdrop, retention)) {
          expect(channel).toBeGreaterThanOrEqual(-1e-12);
          expect(channel).toBeLessThanOrEqual(1 + 1e-12);
        }
      }
    }
  });

  it("restores toward the backdrop's chromaticity, monotonically", () => {
    // The fail-before half, and the operator's own claim. Chromaticity here is
    // the colour normalised by its luma, and the distance to the backdrop's
    // falls with the retention on every cell of the bed that has a chromaticity
    // to move toward.
    const chromaticity = (c: Rgb): Rgb => {
      const Y = luma(c);
      return [c[0] / Y, c[1] / Y, c[2] / Y];
    };
    const distance = (a: Rgb, b: Rgb): number =>
      Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
    let moved = 0;
    for (const { colour, backdrop } of COMPOSITES) {
      if (luma(colour) <= 1e-6 || luma(backdrop) <= 1e-6) continue;
      const target = chromaticity(backdrop);
      const base = distance(chromaticity(colour), target);
      if (base < 1e-9) continue;
      let previous = base;
      for (const retention of RETENTIONS.filter((r) => r > 0)) {
        const now = distance(
          chromaticity(bodyChromaRetention(colour, backdrop, retention)),
          target,
        );
        expect(now).toBeLessThanOrEqual(previous + 1e-12);
        previous = now;
      }
      expect(previous).toBeLessThan(base);
      moved += 1;
    }
    // And the bed really exercises it, so the monotonicity above is not a sweep
    // over cases that were already at the target.
    expect(moved).toBeGreaterThan(100);
  });

  it("is the shader's expression, term for term", () => {
    // The restatement above is arithmetic and the operator is WGSL, so the
    // source is asserted rather than trusted. These are the lines the law is,
    // and a change to any of them fails here before it reaches a golden.
    expect(WGSL_OPTICS_PASS).toContain("bodyChroma : vec4f");
    expect(WGSL_OPTICS_PASS).toContain(
      "fn body_chroma_retention(colour : vec3f, backdrop : vec3f, retention : f32) -> vec3f {",
    );
    expect(WGSL_OPTICS_PASS).toContain("  if (retention <= 0.0) { return colour; }");
    expect(WGSL_OPTICS_PASS).toContain("  if (!(Y > 1e-6 && Y <= 1.0)) { return colour; }");
    expect(WGSL_OPTICS_PASS).toContain("  if (Yb <= 1e-6) { return colour; }");
    // `toward` and not `target`: WGSL reserves the latter, which the first
    // draft of this operator found on a real adapter and not in a unit test.
    expect(WGSL_OPTICS_PASS).toContain("  let toward = backdrop * (Y / Yb);");
    expect(WGSL_OPTICS_PASS).toContain(
      "  var restored = mix(colour, toward, clamp(retention, 0.0, 1.0));",
    );
    expect(WGSL_OPTICS_PASS).toContain("  return gamut_at_luma(restored, Y);");
    expect(WGSL_OPTICS_PASS).toContain("fn gamut_at_luma(c : vec3f, Y : f32) -> vec3f {");
    expect(WGSL_OPTICS_PASS).toContain("  return mix(vec3f(Y), c, clamp(t, 0.0, 1.0));");
    // And it is applied where §5 puts it: immediately after the composite, and
    // before `var materialColour = colour` — so the tint composition below sees
    // the restored body and the tint's own shade law reads a luminance the
    // retention preserved exactly.
    const body = WGSL_OPTICS_PASS.slice(
      WGSL_OPTICS_PASS.indexOf("var colour = mix(backdrop, adapted, presentAlpha);"),
    );
    const call = body.indexOf("colour = body_chroma_retention(colour, backdrop, ou.bodyChroma.x);");
    const material = body.indexOf("var materialColour = colour;");
    expect(call).toBeGreaterThan(0);
    expect(material).toBeGreaterThan(call);
  });
});

/**
 * W31 G3c — the retention under the accessibility fold (Decision Log 3 (d);
 * claims §5.164 §8 (b) and §13).
 *
 * The leaf as G3 shipped it was applied unconditionally, and Reduce
 * Transparency and Increase Contrast are the light document plus an OCCLUSION
 * LIFT: the plate covers `α + lift·(1 − α)` of the backdrop there instead of
 * `α`, so the nominal retention restored a fraction of a chromaticity the
 * preference had just asked to have covered up. Measured on the untinted
 * `photo` beds it took `R` from 0.9096 to 3.0514 (reduced transparency,
 * active), from 0.8294 to 2.1195 (reduced transparency, inactive) and from
 * 0.8147 to 3.1700 (increased contrast, active) — three beds that sat inside
 * the wave's own 0.80–1.20 band before the leaf.
 *
 * The rule is the HARD GATE: under any lifted occlusion the operator is the
 * identity. Decision Log 3 (d) ruled the smaller rule first — the retention on
 * the plate's un-lifted share, `r · (1 − lift)` — with the hard gate as its
 * fallback if the measured `R` did not come back inside the band, and it did
 * not: 1.7897, 1.1507 and 1.8324 under that rule (claims §5.164 §13). The
 * choice is a measurement.
 *
 * What these cases hold is the identity half and the stand-down half
 * separately, because they are different claims: the identity is what lets the
 * 34 goldens, every document digest and every standard matrix row be unmoved,
 * and the stand-down is the fix.
 */
describe("W31 G3c's accessibility fold on the retention (claims §5.164 §13)", () => {
  // core's `ACCESSIBILITY_BEHAVIOR_TABLE` rows, as this package's slice of them
  // (`packages/core/src/accessibility.ts`). Reduce Transparency is the occlusion
  // lift; Increase Contrast reduces the ambient tint, and the calibration bed's
  // `increased-contrast-coupled` profile is both at once, which is the only
  // state macOS 26.5 could produce and the state its fixture was captured in.
  const REDUCE_TRANSPARENCY: MaterialPolicyView = {
    ...NOMINAL_MATERIAL_POLICY,
    frost: "increased",
    refraction: "reduced",
    occlusion: "increased",
  };
  const INCREASED_CONTRAST_COUPLED: MaterialPolicyView = {
    ...REDUCE_TRANSPARENCY,
    border: "strong",
    foreground: "near-monochrome",
    ambientTint: "reduced",
  };
  const FORCED_COLORS: MaterialPolicyView = {
    ...NOMINAL_MATERIAL_POLICY,
    glass: "none",
    frost: "none",
    refraction: "none",
    occlusion: "opaque",
    border: "strong",
    ambientTint: "none",
    foreground: "near-monochrome",
  };

  /**
   * The two macOS 27 LIGHT documents' own numbers
   * (`packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5{,-receded}.json`),
   * restated as a patch so the fold is exercised at the values that actually
   * ship rather than at the runtime default's 0 — at which every case below
   * would pass by arithmetic.
   */
  const ACTIVE = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
    increasedOcclusionLift: 0.75,
    bodyChromaRetention: 0.282,
  });
  const RECEDED = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
    increasedOcclusionLift: 0.96,
    increasedOcclusionLiftByPolicy: { reduceTransparency: 0.88, increaseContrast: 0.98 },
    bodyChromaRetention: 0.349,
  });

  it("is the document's own retention, to the bit, where no preference lifts the occlusion", () => {
    // The identity half, and it is a claim about the POLICY and not about the
    // value: the shipped default is 0 and would satisfy a single assertion by
    // being 0, so the whole retention sweep is run through it.
    for (const profile of [ACTIVE, RECEDED, DEFAULT_MATERIAL_PROFILE]) {
      expect(
        bodyChromaRetentionUnderPolicy(profile.bodyChromaRetention, NOMINAL_MATERIAL_POLICY),
      ).toBe(profile.bodyChromaRetention);
      for (const retention of RETENTIONS) {
        expect(bodyChromaRetentionUnderPolicy(retention, NOMINAL_MATERIAL_POLICY)).toBe(retention);
      }
    }
  });

  it("stands down under every lifted occlusion, at every retention", () => {
    // The fix. Both accessibility rows and the opaque one, over the whole
    // sweep — `0` and not "small", because the claim is that 0.20.0's rendering
    // is restored EXACTLY on those beds and the retention is the only thing
    // this wave moved there.
    for (const policy of [REDUCE_TRANSPARENCY, INCREASED_CONTRAST_COUPLED, FORCED_COLORS]) {
      for (const retention of [...RETENTIONS, 0.282, 0.349]) {
        expect(bodyChromaRetentionUnderPolicy(retention, policy)).toBe(0);
      }
    }
  });

  it("the lift rule it was measured against would not have been the identity there", () => {
    // The fail-before half of the choice, stated as arithmetic so the ledger's
    // reason survives without a browser: `r · (1 − lift)` is NOT 0 on any of
    // the four beds, which is why it left `R` at 1.79 and 1.83 rather than back
    // at 0.91 and 0.81. If a later wave re-opens Decision Log 3 (d), this is
    // the quantity it would be re-measuring.
    expect(0.282 * (1 - occlusionLiftForPolicy(REDUCE_TRANSPARENCY, ACTIVE))).toBeCloseTo(
      0.0705,
      12,
    );
    expect(0.349 * (1 - occlusionLiftForPolicy(REDUCE_TRANSPARENCY, RECEDED))).toBeCloseTo(
      0.04188,
      12,
    );
    expect(0.349 * (1 - occlusionLiftForPolicy(INCREASED_CONTRAST_COUPLED, RECEDED))).toBeCloseTo(
      0.00698,
      12,
    );
    // And the two preferences really do resolve different lifts on the document
    // that splits them, so `ambientTint` is the axis that tells them apart.
    expect(occlusionLiftForPolicy(REDUCE_TRANSPARENCY, RECEDED)).toBe(0.88);
    expect(occlusionLiftForPolicy(INCREASED_CONTRAST_COUPLED, RECEDED)).toBe(0.98);
  });
});
