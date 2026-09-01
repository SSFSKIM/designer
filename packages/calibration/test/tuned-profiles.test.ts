/**
 * The seam between a recorded measurement and a running renderer.
 *
 * §Calibration's rule is that the delegated unknowns are "named here, answered
 * by the harness, recorded into calibration profiles". C9a's answers live in
 * `profiles/apple-macos-26.5-1x-*.json`, and the whole point of recording them
 * is that the runtime carries the same numbers. Nothing enforces that on its
 * own: the renderer's defaults are TypeScript and the profile is JSON, so the two
 * can drift apart in either direction with nothing to notice.
 *
 * These tests are what notices. They deliberately do NOT make the runtime read
 * the JSON at run time — a published package that loads a calibration file would
 * be shipping a data dependency for a number that never changes between releases,
 * and X7 keeps the published surface to two packages with bundled internals.
 * Instead the profile is the authority, the renderer's default mirrors the one
 * profile it targets, and the mirror is pinned here.
 *
 * The other thing pinned here is the shape of the patches: they have to remain
 * applicable to the real `withMaterialOverrides`, because a profile that no
 * longer type-checks against the renderer is a recorded measurement nobody can
 * apply.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { CSS_TIER_MAPPING, type CssTierMapping } from "@vitreajs/vitrea-web";
import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

interface TunedProfile {
  readonly profileKey: string;
  readonly colorSpace: string;
  readonly patch: MaterialProfilePatch;
  /** K5's half of the same document: what the crossing to the CSS tier costs. */
  readonly cssTierMapping?: Partial<CssTierMapping>;
  readonly identityWithRuntimeDefault?: boolean;
  /** Digest over the RESOLVED material — see the profile's `$comment-provenance`. */
  readonly resolvedMaterialSha256: string;
  readonly measurement: {
    readonly objectiveBefore: number;
    readonly objectiveAfter: number;
    readonly cellsUsedForFitting: number;
  };
  readonly entries: Readonly<Record<string, { readonly status: string }>>;
}

/**
 * Every constant the calibration pipeline fitted or measured for the
 * light-standard profile, as a flat key path into the patch.
 *
 * This list is the deliberate, maintained half of the provenance guard — the
 * fingerprint case below is the half that needs no maintenance. It is kept
 * because the fingerprint can only say *that* something moved, and a reader
 * asking "is this number recorded anywhere?" needs an answer that names it.
 *
 * A constant belongs here when a measurement chose its value. Structural
 * defaults the wave never fitted are deliberately absent — `rimAlpha`,
 * `specularGain`, the glow and sweep constants — and the profile's own `entries`
 * record why each of those was left alone.
 */
const FITTED_CONSTANTS = [
  // C9a and the recalibration cascade, on the optics
  "optics.regular.blurSigma",
  "optics.regular.tintAlpha",
  "optics.regular.shadowAlpha",
  "adaptiveTintDark",
  "adaptiveTintLight",
  // W2's size law, and the cascade's refit of the gain the bed could finally see
  "sizeSpanMin",
  "sizeSpanMax",
  "lensSizeGainMax",
  "sizeScatterGainMax",
  "sizeOcclusionGain",
  "sizeShadowGainMax",
  // W3's tint tone map
  "tintToneFloor",
  "tintToneCeilMix",
  "tintToneLow",
  "tintToneHigh",
  // W7's backdrop tone adaptation
  "backdropToneMax",
  "backdropToneLow",
  "backdropToneHigh",
  "backdropToneSizeBias",
  // W8's outer shadow, fitted under the cascade's shadow objective
  "outerShadow.offsetPx",
  "outerShadow.sigmaPx",
  "outerShadow.spreadPx",
  "outerShadow.occlusion",
  "outerShadow.reducedTransparencyOcclusion",
  "outerShadow.sizeGain",
  // The accessibility fold, one constant serving both coupled profiles
  "increasedOcclusionLift",
] as const;

/**
 * A digest over a resolved material profile: keys sorted, then SHA-256, first 16
 * hex. Sorting makes the digest a property of the values rather than of
 * declaration order, so re-ordering the renderer's literal cannot fail the pin.
 */
function fingerprint(resolved: unknown): string {
  const canonical = (value: unknown): unknown =>
    Array.isArray(value)
      ? value.map(canonical)
      : value !== null && typeof value === "object"
        ? Object.fromEntries(
            Object.keys(value as object)
              .sort()
              .map((key) => [key, canonical((value as Record<string, unknown>)[key])]),
          )
        : value;
  return createHash("sha256").update(JSON.stringify(canonical(resolved))).digest("hex").slice(0, 16);
}

const PROFILES = resolve(import.meta.dirname, "..", "profiles");

function load(key: string): TunedProfile {
  return JSON.parse(readFileSync(resolve(PROFILES, `${key}.json`), "utf8")) as TunedProfile;
}

const LIGHT = load("apple-macos-26.5-1x-light-standard");
const DARK = load("apple-macos-26.5-1x-dark-standard");

describe("tuned calibration profiles", () => {
  it("carry the profile key they are named for, in the locked colour space", () => {
    expect(LIGHT.profileKey).toBe("apple-macos-26.5-1x-light-standard");
    expect(DARK.profileKey).toBe("apple-macos-26.5-1x-dark-standard");
    // X5 locks v1 calibration to sRGB; a number measured in another space is not
    // comparable to anything else in the pipeline.
    expect(LIGHT.colorSpace).toBe("srgb");
    expect(DARK.colorSpace).toBe("srgb");
  });

  it("pins the runtime default to the light-standard profile", () => {
    // The claim the light profile makes about itself. If someone retunes the
    // renderer's defaults without re-recording, or re-records without retuning,
    // this is the test that fails.
    expect(LIGHT.identityWithRuntimeDefault).toBe(true);
    const applied = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, LIGHT.patch);
    expect(applied).toEqual(DEFAULT_MATERIAL_PROFILE);
  });

  /*
   * The identity above is necessary and it is NOT sufficient, which is what the
   * landing review found on 2026-09-01 and what the next two cases exist for.
   *
   * `withMaterialOverrides` leaves any key the patch omits at its default, so a
   * patch that stays silent about a constant passes the identity whatever that
   * constant is set to. `sizeOcclusionGain` was refitted 0 -> 0.05 against the
   * frozen bed, the rendered material changed, and every assertion in this file
   * still passed — while `capture-web.ts` went on hashing an unchanged profile
   * into every cell's `capturePath` as the record of what had been applied.
   *
   * Two different guarantees are needed, so there are two cases.
   */

  it("makes the light patch NAME every fitted constant, not just the ones that differ", () => {
    /*
     * The named-set guarantee, for a human reading the file. The light patch is
     * the identity by construction, so this cannot be checked by comparing
     * values — only by requiring the keys to be present. A constant the
     * calibration pipeline chose and the patch does not mention is a number with
     * no recorded provenance, whatever its value happens to be.
     */
    const leaves = (patch: object, prefix = ""): string[] =>
      Object.entries(patch).flatMap(([key, value]) =>
        value !== null && typeof value === "object" && !Array.isArray(value)
          ? leaves(value as object, `${prefix}${key}.`)
          : [`${prefix}${key}`],
      );
    const named = new Set(leaves(LIGHT.patch));
    for (const constant of FITTED_CONSTANTS) {
      expect(named, `${constant}: fitted by the calibration pipeline, unnamed in the patch`).toContain(
        constant,
      );
    }
  });

  it("pins the RESOLVED material by fingerprint, so a default cannot move unrecorded", () => {
    /*
     * The completeness guarantee, and the one that does not depend on anybody
     * maintaining a list. The digest is over the fully resolved material rather
     * than over the patch, so it moves when the rendered material moves — whatever
     * moved it, and wherever that constant lives. A renderer default can no longer
     * change without either the profile being re-recorded or this going red.
     *
     * Keys are sorted before hashing so the digest is a property of the values and
     * not of anyone's declaration order.
     */
    for (const profile of [LIGHT, DARK]) {
      const resolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, profile.patch);
      expect(
        fingerprint(resolved),
        `${profile.profileKey}: the resolved material no longer matches the recorded ` +
          `fingerprint — re-record resolvedMaterialSha256 and say in the profile what moved`,
      ).toBe(profile.resolvedMaterialSha256);
    }

    // And the two profiles resolve differently, so the fingerprint is discriminating
    // rather than a constant that would match anything.
    expect(LIGHT.resolvedMaterialSha256).not.toBe(DARK.resolvedMaterialSha256);
  });

  it("records the measured light-scheme tint alpha, not the advisory one", () => {
    // Named explicitly rather than only through the identity above, so the number
    // that moves most is legible in the test as well as in the profile.
    //
    // 0.28 was the advisory, 0.62 was C9a's fit against the INACTIVE material,
    // and 0.46 is the recalibration cascade's fit against the active bed
    // (2026-08-31). The three are on the record here in order because the middle
    // one is the kind of number a reader would otherwise assume had never moved.
    expect(LIGHT.patch.optics?.regular?.tintAlpha).toBe(0.46);
    expect(DEFAULT_MATERIAL_PROFILE.optics.regular.tintAlpha).toBe(0.46);
  });

  it("leaves the backdrop tint crossover inert by default", () => {
    // The measured finding: the reference keys its tint on the colour scheme, not
    // on the backdrop behind it. Both ends equal means the crossover cannot fire.
    expect(DEFAULT_MATERIAL_PROFILE.adaptiveTintDark).toEqual(
      DEFAULT_MATERIAL_PROFILE.adaptiveTintLight,
    );
  });

  it("applies the dark patch as a real change, and only where it claims to", () => {
    const dark = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, DARK.patch);
    expect(dark).not.toEqual(DEFAULT_MATERIAL_PROFILE);
    expect(dark.optics.regular.tintAlpha).toBe(0.97);
    expect(dark.optics.regular.tint).toEqual([0.05, 0.05, 0.05]);
    expect(dark.adaptiveTintDark).toEqual(dark.adaptiveTintLight);

    // A patch names leaves; it must not quietly drop their siblings. These are
    // the constants the dark profile explicitly declines to retune, and they have
    // to survive the merge for that declining to mean anything.
    expect(dark.optics.regular.blurSigma).toBe(DEFAULT_MATERIAL_PROFILE.optics.regular.blurSigma);
    expect(dark.optics.regular.rimAlpha).toBe(DEFAULT_MATERIAL_PROFILE.optics.regular.rimAlpha);
    expect(dark.optics.regular.specularGain).toBe(
      DEFAULT_MATERIAL_PROFILE.optics.regular.specularGain,
    );
    expect(dark.optics.clear).toEqual(DEFAULT_MATERIAL_PROFILE.optics.clear);
  });

  it("states an improvement on the objective it was fitted against", () => {
    for (const profile of [LIGHT, DARK]) {
      expect(profile.measurement.objectiveAfter).toBeLessThan(profile.measurement.objectiveBefore);
      expect(profile.measurement.cellsUsedForFitting).toBeGreaterThan(0);
    }
  });

  it("pins the CSS tier's shipped mapping to the light-standard profile too (K5)", () => {
    // The same both-directions pin as the renderer's, one tier along. Without it
    // the mapping's tuned constant and its record can drift, which is the exact
    // shape of the gap K5 closed — one tier retuned, the other left behind.
    expect(LIGHT.cssTierMapping?.referenceBackdropLuminance).toBe(0.02);
    expect(CSS_TIER_MAPPING.referenceBackdropLuminance).toBe(
      LIGHT.cssTierMapping?.referenceBackdropLuminance,
    );
    // The dark profile deliberately records no mapping: the crossing is a
    // property of the two pipelines, not of the colour scheme, and one fitted
    // level serves both. Recorded so its absence reads as a decision.
    expect(DARK.cssTierMapping).toBeUndefined();
  });

  it("gives every entry a status from the closed set the profiles use", () => {
    // An entry with an unrecognised status is a number whose provenance nobody
    // has to read — which is the failure the seed profile's status field exists
    // to prevent. `declined` and `not-discriminating` are outcomes, not gaps.
    const allowed = new Set([
      "measured",
      "measured-with-a-caveat",
      "unchanged-deliberately",
      "not-discriminating",
      "not-discriminable",
      "not-measurable-by-this-matrix",
      "not-measurable-by-this-objective",
      "unmeasurable-as-specified",
      "declined",
    ]);
    for (const profile of [LIGHT, DARK]) {
      for (const [name, entry] of Object.entries(profile.entries)) {
        expect(allowed, `${profile.profileKey} / ${name}`).toContain(entry.status);
      }
    }
  });
});
