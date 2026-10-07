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
  MACOS_27_GLASS025_RESOLVED_MATERIAL_SHA256,
  macos27Glass025CssTierMapping,
  macos27Glass025DarkMaterialProfile,
  macos27Glass025LightMaterialProfile,
  macos27Glass025MaterialProfileDocument,
  macos27Glass025RecededMaterialProfile,
  SHIPPED_MATERIAL_PROFILE_DOCUMENTS,
  macos27CssTierMapping,
  macos27DarkMaterialProfile,
  macos27LightMaterialProfile,
  macos27MaterialProfileDocument,
  macos27RecededMaterialProfile,
  macos26MaterialProfileDocument,
  DEFAULT_MATERIAL_PROFILE_DOCUMENT,
} from "@vitreajs/vitrea-web";
import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

import { supersessionFor } from "./digest-supersessions";
import { resolvedDigest } from "../scripts/candidate-document";

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
    // And it states the slider position it was measured at, the system default (W43
    // Decision Log 1 (a), charter clause 12), which is the one change X41 admits to it.
    expect(macos27MaterialProfileDocument.glassTintAmount).toBe(0.5);
  });

  it("names each endpoint's document and the digest its pin resolves to", () => {
    /*
     * The readout's provenance. `root.material` reports these two fields, so a
     * capture cell and the demo's capabilities panel can say which document drew
     * — and a digest that did not come from the document it claims would make
     * that readout a decoration.
     *
     * For exactly one wave the digest an endpoint reported was the CURRENT one,
     * read from `profiles/digest-supersessions.json` rather than from the
     * document's own field: W30 G2 added eight operator leaves to the renderer's
     * default at values that are algebraic identities, which moves a digest
     * taken over the fully resolved material while moving no pixel, and it could
     * not re-seal these four because `adopted-thresholds.test.ts` hashes their
     * bytes and moving them would have emptied their bed out of every bound
     * before a read existed to replace them (claims §5.158 §4).
     *
     * **W30 G3 closed that interval** (Decision Log 4 (b); claims §5.159): it
     * gave the eight leaves values, re-sealed these four documents and read the
     * whole bed at those bytes in the same commit, so each document's own field
     * is its current digest again and the four records are retired. The two
     * frozen macOS 26.5 documents keep theirs, because their bytes cannot move.
     * `tuned-profiles.test.ts` recomputes all six from the materials themselves,
     * each through its own construction, so this case's equality ends at a
     * material and not at a field.
     */
    const endpoints = [
      [macos27MaterialProfileDocument.active.light, LIGHT],
      [macos27MaterialProfileDocument.active.dark, DARK],
      [macos27MaterialProfileDocument.receded.light, RECEDED_LIGHT],
      [macos27MaterialProfileDocument.receded.dark, RECEDED_DARK],
    ] as const;
    for (const [endpoint, document] of endpoints) {
      expect(endpoint.profileKey).toBe(document.profileKey);
      expect(endpoint.resolvedMaterialSha256).toBe(document.resolvedMaterialSha256);
      // And no macOS 27 document carries a supersession record any more: the
      // exemption's indirection is the frozen pair's alone.
      expect(() => supersessionFor(document.profileKey)).toThrow();
    }
  });
});

/**
 * **The four sealed `-glass0.25` documents** (W43 G3 (ii), charter clause 10; X44; Decision Logs 5
 * and 7 as RULED 2026-10-02).
 *
 * The 0.25 generation's runtime module does not exist yet: it is generated from these documents at
 * the landing (Decision Log 1), and its pin is this file's cases above repeated for it then. What
 * the sealed documents can be held to now is what they claim: each names EXACTLY the leaves of its
 * 0.5 twin, in both directions (X44, one leaf space: no operator added, none dropped); each patch
 * is the frozen candidate c05's, leaf for leaf, and names that candidate's declaration by the
 * SHA-256 of its bytes; each recorded digest reproduces over the unmoved default (active) or over
 * its scheme's sealed 0.25 active document (receded); and the CSS crossing is the shipped 0.5 one,
 * unchanged.
 *
 * **W45 G1 re-sealed the two LIGHT documents** (claims §5.206; charter
 * `2026-10-03-w45-span-selective-texture.md` Decision Logs 1 and 2; X44 as narrowed there). The
 * leaf-set pin admits exactly the ruled keys beyond the twin's leaves and nothing else: the light
 * active document adds the span-graded tap's operator `sizeHeavySecondShareFar2x`, and the light
 * receded document adds it and `sizeHeavySecondShare`, each as a difference over its active document
 * (W44 Decision Log 7 item 1 for the share). The dark pair names exactly its twins' leaves, as
 * before. The light pair's patches are W45's frozen candidate's; the dark pair's are still c05's.
 *
 * **W48 G1 re-sealed the two DARK documents** (claims §5.213; charter
 * `2026-10-06-w48-dark-operators-fit.md`, G1 child; X64 and X67, W46's and W47's narrowings of X44).
 * The dark pair's patches are W48 Decision Log 9's post-gate selection (part 2's amendment
 * `50eccbe41e46`), the frozen candidate `d-dl9-g-0.5-rq0.25-rw15-rw25`, and each names, beyond its twin's leaves, exactly the keys X64 and X67 admit on its
 * slot that the candidate states: the active its stage-1 leaves (operator 1's far deltas, the span
 * tops, the occlusion gain) and the rest-scatter keys X64 lets it name; the receded every admitted key,
 * materialised at the stage-1 active's values where it holds them (X67: the span tops, the gain,
 * operator 1's leaves; operator 2's leaves at 0 and the body width at 1.25, both at their identity, so
 * digest-neutral) and moved where its own scatter moved them (X64). The frozen candidate is the pair W48
 * Decision Log 9 and its addendum select over the fit's rendered points (part 2's amendment `50eccbe41e46`:
 * the gain −0.5 active over the landed receded document with its second heavy tap at 0.25, 5 / 5), which
 * supersedes the first freeze's pair (`129316b87df6c562` / `aa1a1b198ee72850`, the procedure's landed point).
 */
const RULED_EXTRA_LEAVES: Readonly<Record<string, readonly string[]>> = {
  "apple-macos-27.0-1x-light-standard-glass0.25": ["sizeHeavySecondShareFar2x"],
  "apple-macos-27.0-1x-light-standard-glass0.25-receded": ["sizeHeavySecondShare", "sizeHeavySecondShareFar2x"],
  "apple-macos-27.0-1x-dark-standard-glass0.25": [
    "sizeOcclusionGain", "sizeScatterFloor2x", "sizeScatterRampStartThin1x", "sizeScatterRampStartThin2x",
    "sizeScatterSpanMax", "sizeScatterSpanMax2x", "tintAlphaFar1x", "tintAlphaFar2x",
  ],
  "apple-macos-27.0-1x-dark-standard-glass0.25-receded": [
    "optics.regular.blurSigma", "sizeFineTapShare", "sizeFineTapSigma", "sizeFineTapSigma2x",
    "sizeHeavySecondShare", "sizeHeavySecondShareFar2x", "sizeHeavySecondSigma", "sizeHeavySecondSigma2x",
    "sizeHeavyTapSigma", "sizeOcclusionGain", "sizeScatterFloor", "sizeScatterFloor2x",
    "sizeScatterRampStartFar1x", "sizeScatterScaleGain", "sizeScatterSpanMax", "sizeScatterSpanMax2x",
    "tintAlphaFar1x", "tintAlphaFar2x",
  ],
};
const FROZEN_CANDIDATE: Readonly<Record<string, string>> = {
  "apple-macos-27.0-1x-light-standard-glass0.25":
    "packages/calibration/results/2026-10-03-w45-g1-refit/fit/candidates/c-s2x-t0.65-rcq0.25-rcd-0.125-rcs18-rcf0-rck0-rct0.1/candidate.json",
  "apple-macos-27.0-1x-light-standard-glass0.25-receded":
    "packages/calibration/results/2026-10-03-w45-g1-refit/fit/candidates/c-s2x-t0.65-rcq0.25-rcd-0.125-rcs18-rcf0-rck0-rct0.1/candidate.json",
  "apple-macos-27.0-1x-dark-standard-glass0.25":
    "packages/calibration/results/2026-10-06-w48-g1-refit/fit/candidates/d-dl9-g-0.5-rq0.25-rw15-rw25/candidate.json",
  "apple-macos-27.0-1x-dark-standard-glass0.25-receded":
    "packages/calibration/results/2026-10-06-w48-g1-refit/fit/candidates/d-dl9-g-0.5-rq0.25-rw15-rw25/candidate.json",
};
describe("the four sealed -glass0.25 documents (W43 G3 (ii); the light pair re-sealed by W45 G1)", () => {
  const sealed = (key: string): ProfileDocument & {
    readonly derivedFromCandidate: {
      readonly declaration: string; readonly declarationSha256: string;
      readonly endpoint: string; readonly endpointSha256: string;
    };
    readonly twin: { readonly path: string; readonly sha256: string };
    readonly glassTintAmount: number;
  } => JSON.parse(readFileSync(resolve(import.meta.dirname, "..", "profiles", `${key}.json`), "utf8"));
  const pairs = [
    ["apple-macos-27.0-1x-light-standard-glass0.25", LIGHT],
    ["apple-macos-27.0-1x-dark-standard-glass0.25", DARK],
    ["apple-macos-27.0-1x-light-standard-glass0.25-receded", RECEDED_LIGHT],
    ["apple-macos-27.0-1x-dark-standard-glass0.25-receded", RECEDED_DARK],
  ] as const;
  const REPO = resolve(import.meta.dirname, "..", "..", "..");
  const sha = (path: string): string => createHash("sha256").update(readFileSync(resolve(REPO, path))).digest("hex");

  for (const [key, twin] of pairs) {
    it(`${key} names exactly its 0.5 twin's leaves and the ruled keys, and records the twin's bytes`, () => {
      const document = sealed(key);
      expect(document.profileKey).toBe(key);
      expect(document.glassTintAmount).toBe(0.25);
      expect(twin.profileKey).toBe(key.replace("-glass0.25", "-glass0.5"));
      expect(leaves(document.patch as object).sort())
        .toEqual([...leaves(twin.patch as object), ...RULED_EXTRA_LEAVES[key]!].sort());
      expect(document.twin.path).toBe(`packages/calibration/profiles/${twin.profileKey}.json`);
      expect(document.twin.sha256).toBe(sha(document.twin.path));
    });

    it(`${key} is its frozen candidate's patch, leaf for leaf`, () => {
      const document = sealed(key);
      const from = document.derivedFromCandidate;
      expect(from.declaration).toBe(FROZEN_CANDIDATE[key]);
      expect(from.declarationSha256).toBe(sha(from.declaration));
      expect(from.endpointSha256).toBe(sha(from.endpoint));
      const endpoint = JSON.parse(readFileSync(resolve(REPO, from.endpoint), "utf8")) as ProfileDocument;
      expect(document.patch).toStrictEqual(endpoint.patch);
      expect(document.resolvedMaterialSha256).toBe(endpoint.resolvedMaterialSha256);
    });
  }

  it("reproduces every recorded digest from the material, and keeps the 0.5 crossing", () => {
    // Through the same functions the driver's reader and the seal use, over the unmoved default
    // (active) and over the scheme's sealed 0.25 active document (receded).
    for (const scheme of ["light", "dark"] as const) {
      const active = sealed(`apple-macos-27.0-1x-${scheme}-standard-glass0.25`);
      const receded = sealed(`apple-macos-27.0-1x-${scheme}-standard-glass0.25-receded`);
      const activeMaterial = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, active.patch);
      expect(resolvedDigest(activeMaterial), active.profileKey).toBe(active.resolvedMaterialSha256);
      expect(resolvedDigest(withMaterialOverrides(activeMaterial, receded.patch)), receded.profileKey)
        .toBe(receded.resolvedMaterialSha256);
    }
    expect(sealed("apple-macos-27.0-1x-light-standard-glass0.25").cssTierMapping).toEqual(macos27CssTierMapping);
    expect(sealed("apple-macos-27.0-1x-dark-standard-glass0.25").cssTierMapping).toEqual(DARK.cssTierMapping);
  });
});

/**
 * **The shipped 0.25 material and its four sealed documents are the same numbers** (W43 G3 (ii);
 * Decision Log 1, RULED (a), executed one step early because the generation's publication reads a
 * shipped material in strict mode). The 0.5 cases above, repeated for the module
 * `scripts/generate-macos27-glass025-profile.mjs` writes: each pair deep-equal in both
 * directions, each digest the document's own, the crossing the 0.5 one, and the document
 * selectable by its (OS, glass) pair and not the default.
 */
describe("the shipped macOS 27 glass 0.25 material and its sealed documents (W43 G3 (ii))", () => {
  const SEALED = {
    light: load("apple-macos-27.0-1x-light-standard-glass0.25"),
    dark: load("apple-macos-27.0-1x-dark-standard-glass0.25"),
    recededLight: load("apple-macos-27.0-1x-light-standard-glass0.25-receded"),
    recededDark: load("apple-macos-27.0-1x-dark-standard-glass0.25-receded"),
  };
  const CASES_025 = [
    ["the light active material", macos27Glass025LightMaterialProfile, SEALED.light],
    ["the dark active material", macos27Glass025DarkMaterialProfile, SEALED.dark],
    ["the light receded difference", macos27Glass025RecededMaterialProfile.light, SEALED.recededLight],
    ["the dark receded difference", macos27Glass025RecededMaterialProfile.dark, SEALED.recededDark],
  ] as const;
  for (const [what, shipped, document] of CASES_025) {
    it(`${what} is the same patch, leaf for leaf, in both directions`, () => {
      expect(shipped).toEqual(document.patch);
      expect(leaves(shipped as object).sort()).toEqual(leaves(document.patch as object).sort());
      expect(digest(shipped)).toBe(digest(document.patch));
    });
  }

  it("names each endpoint's sealed document and the digest it resolves to", () => {
    const endpoints = [
      [macos27Glass025MaterialProfileDocument.active.light, SEALED.light, "light"],
      [macos27Glass025MaterialProfileDocument.active.dark, SEALED.dark, "dark"],
      [macos27Glass025MaterialProfileDocument.receded.light, SEALED.recededLight, "recededLight"],
      [macos27Glass025MaterialProfileDocument.receded.dark, SEALED.recededDark, "recededDark"],
    ] as const;
    for (const [endpoint, document, key] of endpoints) {
      expect(endpoint.profileKey).toBe(document.profileKey);
      expect(endpoint.resolvedMaterialSha256).toBe(document.resolvedMaterialSha256);
      expect(MACOS_27_GLASS025_RESOLVED_MATERIAL_SHA256[key]).toBe(document.resolvedMaterialSha256);
    }
    expect(macos27Glass025CssTierMapping).toEqual(macos27CssTierMapping);
    expect(macos27Glass025MaterialProfileDocument.cssTierMapping).toBe(macos27Glass025CssTierMapping);
  });

  it("is shipped and selectable, and is not what a root draws by default", () => {
    expect(SHIPPED_MATERIAL_PROFILE_DOCUMENTS).toContain(macos27Glass025MaterialProfileDocument);
    expect(DEFAULT_MATERIAL_PROFILE_DOCUMENT).toBe(macos27MaterialProfileDocument);
    expect(macos27Glass025MaterialProfileDocument.platform).toBe("macOS 27.0");
    expect(macos27Glass025MaterialProfileDocument.name).toBe("apple-macos-27.0-glass0.25");
    expect(macos27Glass025MaterialProfileDocument.glassTintAmount).toBe(0.25);
  });

  it("states its position beside the 0.5 document's; the 26.5 document states none", () => {
    // W43 Decision Log 1 (a), charter clause 12. The field is ABSENT on macOS 26.5 rather than
    // defaulted, as `NativeProfile.glass` is on a 26.5 key: that material was measured on a
    // system with no slider, so it says nothing about a position.
    expect(SHIPPED_MATERIAL_PROFILE_DOCUMENTS.map((d) => [d.name, d.glassTintAmount])).toEqual([
      ["apple-macos-27.0-glass0.5", 0.5],
      ["apple-macos-27.0-glass0.25", 0.25],
      ["apple-macos-26.5", undefined],
    ]);
    expect(Object.hasOwn(macos26MaterialProfileDocument, "glassTintAmount")).toBe(false);
    // And the sealed documents the 0.25 module is generated from say the same.
    for (const document of Object.values(SEALED)) {
      expect((document as ProfileDocument & { glassTintAmount?: number }).glassTintAmount)
        .toBe(macos27Glass025MaterialProfileDocument.glassTintAmount);
    }
  });
});
