/**
 * One source for the macOS 27 material: the shipped patches and the four macOS
 * 27 profile documents are the same numbers (W29 G4, claims §5.155).
 *
 * The sibling of `dark-profile-export.test.ts`, and the same argument one
 * material along. macOS 27 is measured here and drawn there, and W29 G4 made it
 * what a page draws by default — so from 0.19.0 the numbers a published package
 * renders with live in two files, and the drift `tuned-profiles.test.ts` opens
 * by describing becomes possible one package away.
 *
 * This is the pin. The exports are GENERATED from the documents by
 * `packages/platform-web/scripts/generate-macos27-profile.mjs`, so closing the
 * drift is one command; this test is what makes forgetting to run it loud.
 *
 * Four documents rather than one, because the runtime selects between four
 * endpoints — the active material per colour scheme, and the receded difference
 * per colour scheme — and any one of them drifting would ship a material no
 * measurement records. The receded pair matters most: the endpoints were fitted
 * in W29 G3b through the calibration harness's own `--receded-profile` seam
 * (claims §5.154 §6), and until G4 nothing at runtime read them at all.
 *
 * What is read here is the SHIPPED artifact: `@vitreajs/vitrea-web` resolves to
 * `dist/`, so this is what a consumer would install, and the chain runs `build`
 * before `test` for exactly that reason. The same comparison against the source
 * modules is `packages/platform-web/test/color-scheme.test.ts`'s — two readings
 * of one claim, and neither is redundant, because a source module that matches
 * the documents and a bundle that does not is a build nobody re-ran.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import {
  macos27CssTierMapping,
  macos27DarkMaterialProfile,
  macos27LightMaterialProfile,
  macos27MaterialProfileDocument,
  macos27RecededMaterialProfile,
  DEFAULT_MATERIAL_PROFILE_DOCUMENT,
} from "@vitreajs/vitrea-web";
import type { MaterialProfilePatch } from "@vitrea/renderer-webgpu";

interface ProfileDocument {
  readonly profileKey: string;
  readonly patch: MaterialProfilePatch;
  readonly cssTierMapping?: Record<string, unknown>;
  readonly resolvedMaterialSha256: string;
}

const load = (key: string): ProfileDocument =>
  JSON.parse(
    readFileSync(resolve(import.meta.dirname, "..", "profiles", `${key}.json`), "utf8"),
  ) as ProfileDocument;

const LIGHT = load("apple-macos-27.0-1x-light-standard-glass0.5");
const DARK = load("apple-macos-27.0-1x-dark-standard-glass0.5");
const RECEDED_LIGHT = load("apple-macos-27.0-1x-light-standard-glass0.5-receded");
const RECEDED_DARK = load("apple-macos-27.0-1x-dark-standard-glass0.5-receded");

/** Every leaf as a flat key path, so a missing one is named rather than diffed. */
const leaves = (patch: object, prefix = ""): string[] =>
  Object.entries(patch).flatMap(([key, value]) =>
    value !== null && typeof value === "object" && !Array.isArray(value)
      ? leaves(value as object, `${prefix}${key}.`)
      : [`${prefix}${key}`],
  );

/**
 * A digest over one patch, key order included.
 *
 * The deep comparison below is the substantive claim and this is the one-line
 * form of it — what the ledger quotes when it says the rows W29 G3b read were
 * read under the bytes the runtime now ships. The generator prints the document
 * in the document's own key order, so equality here is over the serialisation
 * and not only over the values.
 */
const digest = (patch: unknown): string =>
  createHash("sha256").update(JSON.stringify(patch)).digest("hex").slice(0, 16);

const CASES = [
  ["the light active material", macos27LightMaterialProfile, LIGHT],
  ["the dark active material", macos27DarkMaterialProfile, DARK],
  ["the light receded difference", macos27RecededMaterialProfile.light, RECEDED_LIGHT],
  ["the dark receded difference", macos27RecededMaterialProfile.dark, RECEDED_DARK],
] as const;

describe("the shipped macOS 27 material and the macOS 27 profile documents", () => {
  for (const [what, shipped, document] of CASES) {
    it(`${what} is the same patch, leaf for leaf`, () => {
      expect(shipped).toEqual(document.patch);
    });

    it(`${what} names the same constants, in both directions`, () => {
      const inPackage = new Set(leaves(shipped as object));
      const recorded = new Set(leaves(document.patch as object));

      for (const constant of recorded) {
        expect(
          inPackage,
          `${constant}: recorded in ${document.profileKey} and absent from the shipped ` +
            `patch — regenerate packages/platform-web/src/macos27-profile.ts ` +
            `(pnpm --filter @vitreajs/vitrea-web run profile:macos27)`,
        ).toContain(constant);
      }
      for (const constant of inPackage) {
        expect(
          recorded,
          `${constant}: shipped in the macOS 27 material and recorded nowhere — a number ` +
            `with no provenance is not a measurement`,
        ).toContain(constant);
      }
    });

    it(`${what} hashes to the document's own bytes`, () => {
      expect(digest(shipped)).toBe(digest(document.patch));
    });
  }

  it("carries the CSS crossing the light document records, with the dark document agreeing", () => {
    // One mapping per material family, not one per scheme: it is the crossing to
    // `backdrop-filter`, and the root resolves a scheme after that crossing's
    // constants are fixed. The light document is where the whole mapping lives;
    // the dark document names the subset refit with it, and the two must agree
    // on every key they share or "which mapping is the macOS 27 mapping" has two
    // answers.
    expect(macos27CssTierMapping).toEqual(LIGHT.cssTierMapping);
    for (const [key, value] of Object.entries(DARK.cssTierMapping ?? {})) {
      expect(macos27CssTierMapping, key).toMatchObject({ [key]: value });
    }
  });

  it("is what a root draws when an app asks for nothing (W29 Decision Log 2)", () => {
    // The selection itself, read from the package rather than from the ledger.
    // `DEFAULT_MATERIAL_PROFILE` in the renderer did NOT move (Decision Log 1
    // (i)); what moved is which patch over it a root resolves by default, and
    // this is the one assertion that states that in one place.
    expect(DEFAULT_MATERIAL_PROFILE_DOCUMENT).toBe(macos27MaterialProfileDocument);
    expect(DEFAULT_MATERIAL_PROFILE_DOCUMENT.platform).toBe("macOS 27.0");
  });

  it("names each endpoint's document and its recorded digest", () => {
    // The readout's provenance. `root.material` reports these two fields, so a
    // capture cell and the demo's capabilities panel can say which document drew
    // — and a digest that did not come from the document it claims would make
    // that readout a decoration.
    const endpoints = [
      [macos27MaterialProfileDocument.active.light, LIGHT],
      [macos27MaterialProfileDocument.active.dark, DARK],
      [macos27MaterialProfileDocument.receded.light, RECEDED_LIGHT],
      [macos27MaterialProfileDocument.receded.dark, RECEDED_DARK],
    ] as const;
    for (const [endpoint, document] of endpoints) {
      expect(endpoint.profileKey).toBe(document.profileKey);
      expect(endpoint.resolvedMaterialSha256).toBe(document.resolvedMaterialSha256);
    }
  });
});
