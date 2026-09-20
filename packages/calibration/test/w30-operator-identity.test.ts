/**
 * W30 — the operator wave's identity test: the exemption, proved inert at the
 * material level.
 *
 * The wave adds leaves to the renderer's `DEFAULT_MATERIAL_PROFILE` for two
 * operators (the span-graded shadow σ and the scale-selective scatter). Every
 * profile document's `resolvedMaterialSha256` is a digest over the FULLY
 * RESOLVED material, so those leaves move the digest of every document —
 * including the two frozen macOS 26.5 ones, whose pixels do not move at all.
 * That is the one-time X1 exemption W29 Decision Log 7 (a) granted and W30
 * Decision Log 1 (a) shaped.
 *
 * A moved digest is exactly as loud as a moved material, which is what makes it
 * a useful pin and useless as a proof of inertness. This file supplies the proof
 * the digest cannot: G0 wrote the fully resolved macOS 26.5 light and dark
 * materials to disk BEFORE any leaf existed, through the fingerprint's own path
 * (`results/2026-09-20-w30-g0-cut/resolve-pre-wave.ts`), and this test resolves
 * each document again today, removes the leaves the wave added by name, and
 * requires the rest to be deep-equal to the committed pre-wave value.
 *
 * So the pair of guarantees is:
 *   - `tuned-profiles.test.ts` pins each document's digest, and says WHETHER the
 *     material moved.
 *   - this file says WHAT moved, and requires it to be nothing but the named
 *     leaves — one deep equality over every other constant in the material.
 *
 * It was written and green with an EMPTY leaf list, which is the point: the test
 * passed before the commit it exists to judge, so G2 could not be the commit
 * that also wrote its own proof. G2 filled the list in the commit that added the
 * leaves (claims §5.158), and the two beds below now differ from the pre-wave
 * files in exactly eight leaves and in nothing else.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

/**
 * Every leaf W30's operators add to `MaterialProfile`, as a flat key path — the
 * only differences this wave may make to the resolved macOS 26.5 materials.
 *
 * **Filled by G2, in the same commit that added the leaves** (claims §5.158;
 * W30 Decision Log 2 (d) is the list this has to equal). The list is a
 * declaration rather than a convenience: a leaf added without being named here
 * fails the identity below, and a name here that no leaf matches fails the
 * completeness case. G2 therefore could not add a leaf silently and could not
 * claim one it did not add.
 *
 * A path names one leaf of the resolved material, dotted from the root — for
 * example `outerShadow.sigmaSlopePerSpan`. Nested objects are walked; array leaves are
 * named by their containing key, because the material's arrays are ordinate
 * vectors read whole.
 *
 * Exported because G2 edits it and G3's fit reads it back to say which leaves it
 * is allowed to move; nothing else should grow off it.
 */
export const W30_OPERATOR_LEAVES: readonly string[] = [
  // The shadow's σ law (claims §5.156 §2), three leaves on `MaterialOuterShadow`:
  // σ(span) = sigmaPx + max(sigmaThinOffsetPx, sigmaSlopePerSpan · (span − sigmaSpanRefPx)).
  // Every one of them 0, where the law is `sigmaPx` at every span.
  "outerShadow.sigmaSlopePerSpan",
  "outerShadow.sigmaSpanRefPx",
  "outerShadow.sigmaThinOffsetPx",
  // The scatter's spanning set (claims §5.156 §3; W30 Decision Log 2 (d)), five
  // leaves on `MaterialProfile`: a second heavy width per scale with a signed
  // share, and a gain on `kScatter` keyed on the source's measured scale
  // statistic about a reference. Every one of them 0.
  "sizeHeavySecondSigma",
  "sizeHeavySecondSigma2x",
  "sizeHeavySecondShare",
  "sizeScatterScaleGain",
  "sizeScatterScaleRef",
];

const HERE = import.meta.dirname;
const PROFILES = resolve(HERE, "..", "profiles");
const EVIDENCE = resolve(HERE, "..", "results", "2026-09-20-w30-g0-cut");

const DOCUMENTS = [
  ["apple-macos-26.5-1x-light-standard", "resolved-26.5-light.json", "b2b570e4adcea8fb"],
  ["apple-macos-26.5-1x-dark-standard", "resolved-26.5-dark.json", "874be66ea501621b"],
] as const;

function readJson(path: string): Record<string, unknown> {
  return JSON.parse(readFileSync(path, "utf8")) as Record<string, unknown>;
}

/** Every dotted leaf path of a resolved material, in no particular order. */
function leafPaths(value: unknown, prefix = ""): string[] {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? Object.entries(value).flatMap(([key, child]) =>
        leafPaths(child, prefix === "" ? key : `${prefix}.${key}`),
      )
    : [prefix];
}

/**
 * A copy of `value` with the named dotted paths removed.
 *
 * Removal rather than substitution, so that the comparison cannot be satisfied
 * by a leaf that happens to hold the same sentinel on both sides, and so that a
 * leaf named but absent is visible as a difference in the key sets rather than
 * silently ignored.
 */
function without(value: unknown, paths: readonly string[], prefix = ""): unknown {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return value;
  return Object.fromEntries(
    Object.entries(value)
      .map(([key, child]) => [prefix === "" ? key : `${prefix}.${key}`, key, child] as const)
      .filter(([path]) => !paths.includes(path))
      .map(([path, key, child]) => [key, without(child, paths, path)]),
  );
}

describe("W30's exemption is inert at the material level (acceptance clause 1, X1)", () => {
  it("names only leaves the resolved material actually has", () => {
    // The completeness half. A path that matches nothing would make the
    // identity below pass while hiding a leaf that really did move, which is the
    // failure a list of names has that a diff does not.
    const present = new Set(leafPaths(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {})));
    for (const leaf of W30_OPERATOR_LEAVES) {
      expect(present, `${leaf}: named as a W30 operator leaf, absent from the material`).toContain(
        leaf,
      );
    }
  });

  for (const [key, evidence, pinned] of DOCUMENTS) {
    it(`resolves ${key} to its pre-wave material outside the named leaves`, () => {
      const document = readJson(resolve(PROFILES, `${key}.json`)) as unknown as {
        patch: MaterialProfilePatch;
        resolvedMaterialSha256: string;
      };
      const resolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, document.patch);
      const preWave = readJson(resolve(EVIDENCE, evidence));

      // The pre-wave file was written at the digest the document still records,
      // which is what makes it that document's material and not some other one.
      // After G2 the document's own field still reads this — the current digest
      // lives in `profiles/digest-supersessions.json` beside it, never in the
      // frozen bytes (W30 Decision Log 1 (a)).
      expect(document.resolvedMaterialSha256).toBe(pinned);

      // `toStrictEqual` rather than `toEqual`, because `toEqual` treats a key
      // holding `undefined` as absent — so a leaf added at an undefined default,
      // and not named in `W30_OPERATOR_LEAVES`, would pass the identity it exists
      // to fail (W30 Decision Log 3 (e), claims §5.156 §9).
      expect(
        without(resolved, W30_OPERATOR_LEAVES),
        `${key}: the resolved material differs from the pre-wave evidence outside ` +
          `W30_OPERATOR_LEAVES — the exemption is for the digest, not for the material`,
      ).toStrictEqual(without(preWave, W30_OPERATOR_LEAVES));
    });
  }

  it("keeps the two pre-wave materials distinct, so the comparison discriminates", () => {
    const light = readJson(resolve(EVIDENCE, "resolved-26.5-light.json"));
    const dark = readJson(resolve(EVIDENCE, "resolved-26.5-dark.json"));
    expect(light).not.toEqual(dark);
  });
});
