/** W41 E3's declared encoded-domain law; synthetic vectors, no native/holdout reads. */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

import { resolveAccessibilityPolicy } from "../../core/src/accessibility";
import {
  applyBodyE3,
  bodyE3Encoded,
  bodyE3StrengthUnderPolicy,
  DEFAULT_MATERIAL_PROFILE,
  materialDigestDroppedLeaves,
  materialDigestInput,
  NOMINAL_MATERIAL_POLICY,
  validateBodyE3Patch,
  withMaterialOverrides,
  type BodyE3Gains,
  type BodyE3Neutral,
  type MaterialPolicyView,
  type MaterialProfile,
  type MaterialProfilePatch,
} from "../src/material";

const identityNeutral: BodyE3Neutral = [40, 56, 72, 88, 104, 128, 150];
const neutral: BodyE3Neutral = [150, 157, 164, 171, 178, 188, 197];
const gains: BodyE3Gains = [0.5, 1, 2];

function expectCodes(actual: readonly number[], expected: readonly number[]): void {
  expect(actual).toHaveLength(3);
  actual.forEach((value, i) => expect(value).toBeCloseTo(expected[i]!, 10));
}

describe("E3 encoded body reference", () => {
  // Holding outside instead of continuing F fails the 0/32/192/255 cases;
  // interpolating at gain knots instead of neutral knots fails the inner cases.
  it.each([
    [0, 132.5], [32, 146.5], [40, 150], [48, 153.5], [56, 157],
    [64, 160.5], [72, 164], [80, 167.5], [88, 171], [96, 174.5],
    [104, 178], [116, 183], [128, 188], [139, 192.5], [150, 197],
    [192, 197 + 42 * 9 / 22], [255, 197 + 105 * 9 / 22],
  ])("continues/interpolates neutral input %s to %s without chroma", (input, output) => {
    expectCodes(bodyE3Encoded([input, input, input], gains, neutral),
      [output, output, output]);
  });

  // This perturbation has zero encoded weighted sum. Linear-light weighting,
  // constant gain, or interpolation outside the held ends changes these values.
  it.each([[40, 0.5], [63, 0.5], [78, 0.75], [93, 1], [105.5, 1.5],
    [118, 2], [150, 2]])("interpolates/holds gain at encoded level %s", (level, gain) => {
    const rgb = [level + 7.152, level - 2.126, level] as const;
    expectCodes(bodyE3Encoded(rgb, gains, identityNeutral),
      [level + gain * 7.152, level - gain * 2.126, level]);
  });

  it("clips the continued neutral before adding chroma, then clips channel rails", () => {
    const offsetLow: BodyE3Neutral = [0, 16, 32, 48, 64, 88, 110];
    // L = 14.304; F would be -25.696 but is clipped to zero FIRST.
    expectCodes(bodyE3Encoded([0, 20, 0], [1, 1, 1], offsetLow), [0, 5.696, 0]);
    const offsetHigh: BodyE3Neutral = [140, 156, 172, 188, 204, 228, 250];
    // L = 251.029; F clips to 255 before blue's -51.029 chroma is added.
    expectCodes(bodyE3Encoded([255, 255, 200], [1, 1, 1], offsetHigh),
      [255, 255, 203.971]);
    expectCodes(bodyE3Encoded([255, 0, 0], [3, 3, 3], neutral), [255, 0, 0]);
  });

  it("uses the exact encoded weights on saturated bridge colours", () => {
    // Neutral identity and gain 0.5 produce (x + dot(x,W))/2.
    expectCodes(bodyE3Encoded([255, 0, 0], [0.5, 0.5, 0.5], identityNeutral),
      [154.6065, 27.1065, 27.1065]);
    expectCodes(bodyE3Encoded([0, 255, 0], [0.5, 0.5, 0.5], identityNeutral),
      [91.188, 218.688, 91.188]);
    expectCodes(bodyE3Encoded([0, 0, 255], [0.5, 0.5, 0.5], identityNeutral),
      [9.2055, 9.2055, 136.7055]);
  });
});

describe("E3 patch boundary and atomic digest identity", () => {
  const invalid: readonly [string, unknown][] = [
    ...[undefined, null, "1", NaN, Infinity, -Infinity, -0.01, 1.01]
      .map((value) => ["bodyE3Strength", value] as [string, unknown]),
    ...[undefined, null, "1,1,1", {}, [1, 1], [1, 1, 1, 1], new Array(3),
      [1, undefined, 1], [1, null, 1], [1, "1", 1], [1, NaN, 1], [Infinity, 1, 1],
      [-0.01, 1, 1], [1, 3.01, 1]]
      .map((value) => ["bodyE3Gains", value] as [string, unknown]),
    ...[undefined, null, "0,0,0,0,0,0,0", {}, [0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0], new Array(7), Object.assign(new Array(7), { 0: 0, 6: 0 }),
      [0, 0, 0, NaN, 0, 0, 0], [0, 0, 0, Infinity, 0, 0, 0],
      [0, 0, 0, -1, 0, 0, 0], [0, 0, 0, 256, 0, 0, 0]]
      .map((value) => ["bodyE3Neutral", value] as [string, unknown]),
  ];
  it.each(invalid)("rejects malformed %s (%j) even behind gate zero", (key, value) => {
    const patch = { [key]: value };
    expect(() => validateBodyE3Patch(patch)).toThrow(TypeError);
    expect(() => withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,
      patch as MaterialProfilePatch)).toThrow(TypeError);
  });

  it("accepts inclusive ranges and nonmonotone ordinates; merges complete tuples", () => {
    const patch = {
      bodyE3Strength: 1,
      bodyE3Gains: [0, 3, 1.25] as const,
      bodyE3Neutral: [255, 0, 128, 0, 255, 1, 2] as const,
    };
    expect(() => validateBodyE3Patch(patch)).not.toThrow();
    expect(() => validateBodyE3Patch({})).not.toThrow();
    const merged = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    expect(merged.bodyE3Gains).toEqual(patch.bodyE3Gains);
    expect(merged.bodyE3Neutral).toEqual(patch.bodyE3Neutral);
    const inherited = withMaterialOverrides(merged, { bodyE3Strength: 0 });
    expect(inherited.bodyE3Gains).toEqual(patch.bodyE3Gains);
    expect(inherited.bodyE3Neutral).toEqual(patch.bodyE3Neutral);
    const replaced = withMaterialOverrides(inherited, { bodyE3Gains: gains });
    expect(replaced.bodyE3Gains).toEqual(gains);
    expect(replaced.bodyE3Neutral).toEqual(patch.bodyE3Neutral);
    expect(DEFAULT_MATERIAL_PROFILE.bodyE3Strength).toBe(0);
  });

  it("drops the whole zero-gate group but discriminates enabled coefficients", () => {
    const dropped = ["bodyE3Gains", "bodyE3Neutral", "bodyE3Strength"];
    const original = materialDigestInput(DEFAULT_MATERIAL_PROFILE);
    for (const bodyE3Gains of [[0, 3, 2], [3, 0, 1]] as const) {
      for (const bodyE3Neutral of [neutral, [255, 0, 3, 4, 5, 6, 7]] as const) {
        const off = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,
          { bodyE3Strength: 0, bodyE3Gains, bodyE3Neutral });
        expect(materialDigestDroppedLeaves(off)).toEqual(expect.arrayContaining(dropped));
        expect(materialDigestInput(off)).toEqual(original);
        for (const key of dropped) expect(original).not.toHaveProperty(key);
        const on = withMaterialOverrides(off, { bodyE3Strength: 1 });
        const onInput = materialDigestInput(on);
        expect(onInput).toHaveProperty("bodyE3Gains", bodyE3Gains);
        expect(onInput).toHaveProperty("bodyE3Neutral", bodyE3Neutral);
        expect(onInput).not.toEqual(original);
        expect(onInput).not.toEqual(materialDigestInput(withMaterialOverrides(on,
          { bodyE3Gains: [1, 1, 1], bodyE3Neutral: identityNeutral })));
      }
    }
  });
});

describe("E3 claimed policy/variant/sampling domain", () => {
  it("retains nominal and Reduced Motion only; disables RT, IC-only, coupled and forced", () => {
    for (const flags of [{}, { reducedMotion: true }, { reducedTransparency: true },
      { increasedContrast: true }, { reducedTransparency: true, increasedContrast: true },
      { forcedColors: true }]) {
      const policy = resolveAccessibilityPolicy({
        reducedTransparency: false, reducedMotion: false, increasedContrast: false,
        forcedColors: false, reducedTransparencySupported: true, ...flags,
      });
      const expected = flags.reducedTransparency || flags.increasedContrast || flags.forcedColors
        ? 0 : 0.75;
      expect(bodyE3StrengthUnderPolicy(0.75, policy.material, "regular", true)).toBe(expected);
    }
    expect(bodyE3StrengthUnderPolicy(1, NOMINAL_MATERIAL_POLICY, "clear", true)).toBe(0);
    expect(bodyE3StrengthUnderPolicy(1, NOMINAL_MATERIAL_POLICY, "regular", false)).toBe(0);
    expect(bodyE3StrengthUnderPolicy(0, NOMINAL_MATERIAL_POLICY, "regular", true)).toBe(0);
  });

  it.each([
    { glass: "none" }, { frost: "increased" }, { refraction: "reduced" },
    { occlusion: "increased" }, { border: "strong" }, { ambientTint: "reduced" },
    { foreground: "near-monochrome" },
  ] satisfies Partial<MaterialPolicyView>[])("stands down for each material axis %j", (axis) => {
    expect(bodyE3StrengthUnderPolicy(1, { ...NOMINAL_MATERIAL_POLICY, ...axis },
      "regular", true)).toBe(0);
  });
});


describe("E3 compute identity and presence extension", () => {
  it("returns the original colour at gate zero across all policy and sampling states", () => {
    const original = [0.123456, 0.234567, 0.345678] as const;
    for (let bits = 0; bits < 16; bits++) {
      const policy = resolveAccessibilityPolicy({
        reducedTransparency: !!(bits & 1), reducedMotion: !!(bits & 2),
        increasedContrast: !!(bits & 4), forcedColors: !!(bits & 8),
        reducedTransparencySupported: true,
      }).material;
      for (const sampled of [false, true]) {
        for (const variant of ["regular", "clear"] as const) {
          for (const backdrop of [[0, 0, 0], [1, 1, 1], [0, 0.5, 1]] as const) {
            for (const bodyE3Gains of [[0, 3, 1], [3, 0, 2]] as const) {
              for (const bodyE3Neutral of [neutral, [255, 0, 1, 2, 3, 4, 5]] as const) {
                const fields = {
                  bodyE3Strength: bodyE3StrengthUnderPolicy(0, policy, variant, sampled),
                  bodyE3Gains, bodyE3Neutral,
                };
                for (const presence of [0, 0.4, 1]) {
                  expect(applyBodyE3(original, backdrop, presence, fields)).toBe(original);
                }
              }
            }
          }
        }
      }
    }
  });

  it("does not evaluate either tuple behind zero strength or zero presence", () => {
    const original = [0.1, 0.2, 0.3] as const;
    const unread = {
      get bodyE3Gains(): BodyE3Gains { throw new Error("gains read behind identity gate"); },
      get bodyE3Neutral(): BodyE3Neutral { throw new Error("neutral read behind identity gate"); },
    };
    for (const [bodyE3Strength, presence] of [[0, 1], [1, 0]] as const) {
      const fields = Object.assign(Object.create(unread) as typeof unread, { bodyE3Strength });
      expect(applyBodyE3(original, [1, 0, 1], presence, fields)).toBe(original);
    }
  });

  it("replaces the old body at full presence and blends both controls in linear light", () => {
    const original = [0.2, 0.4, 0.6] as const;
    const backdrop = [0, 0, 0] as const;
    const fields = {
      bodyE3Strength: 1, bodyE3Gains: [1, 1, 1] as const,
      bodyE3Neutral: [255, 255, 255, 255, 255, 255, 255] as const,
    };
    expectCodes(applyBodyE3(original, backdrop, 1, fields), [1, 1, 1]);
    expectCodes(applyBodyE3(original, backdrop, 0.25, fields), [0.25, 0.25, 0.25]);
    expectCodes(applyBodyE3(original, backdrop, 0.25, { ...fields, bodyE3Strength: 0.5 }),
      [0.225, 0.325, 0.425]);
    // A mid-code target distinguishes decoding before interpolation from mixing encoded codes.
    const mid = { ...fields, bodyE3Neutral: [128, 128, 128, 128, 128, 128, 128] as const };
    expectCodes(applyBodyE3(original, backdrop, 1, mid),
      [0.21586050011389926, 0.21586050011389926, 0.21586050011389926]);
  });
});

interface SealedDocument {
  readonly patch: MaterialProfilePatch;
  readonly resolvedMaterialSha256: string;
  readonly resolvedOverActiveDocument?: string;
}
const readDocument = (name: string): SealedDocument => JSON.parse(readFileSync(
  new URL(`../../calibration/profiles/${name}.json`, import.meta.url), "utf8")) as SealedDocument;
function sorted(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sorted);
  if (value === null || typeof value !== "object") return value;
  return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b))
    .map(([key, item]) => [key, sorted(item)]));
}
const digest = (material: MaterialProfile): string => createHash("sha256")
  .update(JSON.stringify(sorted(materialDigestInput(material)))).digest("hex").slice(0, 16);

it.each([
  "apple-macos-26.5-1x-light-standard", "apple-macos-26.5-1x-dark-standard",
  "apple-macos-27.0-1x-light-standard-glass0.5",
  "apple-macos-27.0-1x-dark-standard-glass0.5",
  "apple-macos-27.0-1x-light-standard-glass0.5-receded",
  "apple-macos-27.0-1x-dark-standard-glass0.5-receded",
])("preserves sealed digest for %s while sweeping unread E3 tuples", (name) => {
  const document = readDocument(name);
  const base = document.resolvedOverActiveDocument
    ? withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,
      readDocument(document.resolvedOverActiveDocument.replace(/\.json$/, "")).patch)
    : DEFAULT_MATERIAL_PROFILE;
  const material = withMaterialOverrides(base, document.patch);
  expect(digest(material)).toBe(document.resolvedMaterialSha256);
  // W41 G2 (c9a §5.193; Decision Log 2): only the light receded document enables E3. Held
  // at its gate, its whole group drops and the document reads its pre-seal digest, which
  // is the statement that the seal moved E3 and no other leaf. Every other document still
  // reads its own recorded digest there.
  const enabled = document.patch.bodyE3Strength === 1;
  expect(enabled).toBe(name === "apple-macos-27.0-1x-light-standard-glass0.5-receded");
  const atGate = enabled ? PRE_E3_DIGEST : document.resolvedMaterialSha256;
  for (const bodyE3Gains of [[0, 3, 1], [3, 0, 2]] as const) {
    for (const bodyE3Neutral of [neutral, [255, 0, 1, 2, 3, 4, 5]] as const) {
      expect(digest(withMaterialOverrides(material,
        { bodyE3Strength: 0, bodyE3Gains, bodyE3Neutral })))
        .toBe(atGate);
      if (enabled) {
        expect(digest(withMaterialOverrides(material, { bodyE3Gains, bodyE3Neutral })))
          .not.toBe(document.resolvedMaterialSha256);
      }
    }
  }
});

/** The light receded document's rule-2 digest before W41 G2 enabled E3 (W36 G1, §5.179). */
const PRE_E3_DIGEST = "b0d0d8dacc6a03af";
