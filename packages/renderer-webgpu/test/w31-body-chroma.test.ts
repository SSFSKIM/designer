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
 * `α`, so the nominal retention restores a fraction of a chromaticity the
 * preference asked to have covered up. Measured on the untinted `photo` beds it
 * took `R` from 0.9096 to 3.0374 (reduced transparency, active) and from 0.8147
 * to 2.9489 (increased contrast, active), inside bounds too loose to trip.
 *
 * The rule is `r_eff = r · (1 − lift)` — the retention acting on the plate's
 * un-lifted share, which is the same `(1 − lift)` the backdrop's own survival
 * is scaled by. What these cases hold is the identity half and the fold half
 * separately, because they are different claims: the identity is what lets the
 * 34 goldens, every document digest and every standard matrix row be unmoved,
 * and the fold is the fix.
 */
describe("W31 G3c's accessibility fold on the retention (claims §5.164 §13)", () => {
  // core's `ACCESSIBILITY_BEHAVIOR_TABLE` rows, as this package's slice of them
  // (`packages/core/src/accessibility.ts`). Reduce Transparency is the occlusion
  // lift; Increase Contrast reduces the ambient tint, which is the axis
  // `occlusionLiftForPolicy` reads to tell the two preferences' lifts apart;
  // the calibration bed's `increased-contrast-coupled` profile is both at once,
  // which is the only state macOS 26.5 could produce and the state the fixture
  // was captured in.
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

  it("is the document's own retention, to the bit, at every policy carrying no lift", () => {
    // The identity half. `occlusionLiftForPolicy` returns a NON-ZERO number for
    // a nominal policy — it answers "what lift would this material use", not
    // "what lift applies" — so a fold that multiplied by `1 − that` on every
    // path would have scaled every standard row by 0.25 and passed a test
    // written against the function instead of against the policy.
    for (const profile of [ACTIVE, RECEDED, DEFAULT_MATERIAL_PROFILE]) {
      expect(
        bodyChromaRetentionUnderPolicy(profile.bodyChromaRetention, NOMINAL_MATERIAL_POLICY, profile),
      ).toBe(profile.bodyChromaRetention);
      // And it is an identity for any value, not only for the one this profile
      // carries — the shipped default is 0 and would satisfy the line above by
      // being 0.
      for (const retention of RETENTIONS) {
        expect(bodyChromaRetentionUnderPolicy(retention, NOMINAL_MATERIAL_POLICY, profile)).toBe(
          retention,
        );
      }
    }
  });

  it("is `r · (1 − lift)` under an increased occlusion, at the document's own lift", () => {
    // The fold half, at the four numbers the four light beds draw at.
    expect(bodyChromaRetentionUnderPolicy(0.282, REDUCE_TRANSPARENCY, ACTIVE)).toBeCloseTo(
      0.282 * 0.25,
      15,
    );
    expect(bodyChromaRetentionUnderPolicy(0.282, INCREASED_CONTRAST_COUPLED, ACTIVE)).toBeCloseTo(
      0.282 * 0.25,
      15,
    );
    // The receded document splits the lift by preference, so one fitted
    // retention produces two: 0.88 for reduced transparency and 0.98 for
    // increased contrast (Decision Log 3 (c) defers giving those beds their own
    // retentions behind exactly this).
    expect(bodyChromaRetentionUnderPolicy(0.349, REDUCE_TRANSPARENCY, RECEDED)).toBeCloseTo(
      0.349 * 0.12,
      15,
    );
    expect(bodyChromaRetentionUnderPolicy(0.349, INCREASED_CONTRAST_COUPLED, RECEDED)).toBeCloseTo(
      0.349 * 0.02,
      15,
    );
    // And the two preferences really do differ on the document that splits them,
    // so the `ambientTint` branch above is exercised rather than merely present.
    expect(bodyChromaRetentionUnderPolicy(0.349, REDUCE_TRANSPARENCY, RECEDED)).toBeGreaterThan(
      bodyChromaRetentionUnderPolicy(0.349, INCREASED_CONTRAST_COUPLED, RECEDED),
    );
  });

  it("stands down entirely where the plate is opaque", () => {
    // `occlusion: "opaque"` is `α_eff = 1`, a lift of exactly 1: no backdrop
    // survives the plate and there is no chromaticity to restore. It arrives
    // only with `glass: "none"`, so it draws nothing either way — the branch is
    // written because the unreachable case is the one a later policy row makes
    // reachable without anyone noticing.
    for (const profile of [ACTIVE, RECEDED]) {
      expect(bodyChromaRetentionUnderPolicy(profile.bodyChromaRetention, FORCED_COLORS, profile)).toBe(0);
    }
  });

  it("never restores more than the un-lifted policy would", () => {
    // The property the two cases above are instances of, over the whole bed:
    // a lift can only take the retention DOWN, because a lift can only take the
    // backdrop's surviving share down.
    for (const profile of [ACTIVE, RECEDED]) {
      for (const retention of RETENTIONS) {
        for (const policy of [REDUCE_TRANSPARENCY, INCREASED_CONTRAST_COUPLED, FORCED_COLORS]) {
          const folded = bodyChromaRetentionUnderPolicy(retention, policy, profile);
          expect(folded).toBeGreaterThanOrEqual(0);
          expect(folded).toBeLessThanOrEqual(retention);
        }
      }
    }
  });
});
