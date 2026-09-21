/**
 * Selecting the macOS 26.5 document still draws the macOS 26.5 material (W29 G4
 * review closure, claims §5.155).
 *
 * `macos26MaterialProfileDocument` is what a page pinned to the material it was
 * designed against gets, and the README, the CHANGELOG and the upgrade note all
 * say that pinning it "keeps exactly what 0.18.0 drew". Until this file nothing
 * checked that sentence from the selection's own side. `tuned-profiles.test.ts`
 * pins the two macOS 26.5 profile DOCUMENTS against the renderer, and
 * `dark-profile-export.test.ts` pins the shipped dark patch against the dark
 * document — but the runtime does not draw a document or a patch, it draws
 * whatever `colorSchemeMaterialProfile` selects out of the document the root was
 * given, and that seam moved at W29 G4. A wiring change there would leave every
 * existing pin green while a page asking for macOS 26.5 drew macOS 27.
 *
 * So this reads the SELECTION and resolves it, in the two places it is recorded:
 *
 *  1. the material the document's active endpoints select, resolved over the
 *     renderer's defaults, against the `resolvedMaterialSha256` the two macOS
 *     26.5 profile documents carry — the same fingerprint over the same fully
 *     resolved material that `tuned-profiles.test.ts` computes, so a drift in
 *     either file is a disagreement between two readings of one number;
 *  2. the two digests written BY HAND into `material-document.ts` — the only
 *     hand-written digests in either shipped document, because the macOS 26.5
 *     documents predate the generator — against the same two files.
 *
 * The receded pair is not read here and that is deliberate: the macOS 26.5
 * receded endpoints were fitted straight into `receded-profile.ts` in W27c and
 * W28 G1 and there is no document on disk to join them to, so their pin is the
 * browser's — `platform-web/e2e/shared/window-activation.spec.ts` hashes the
 * material the renderer is actually handed in both poses under both documents.
 * Inventing a digest here for a document that does not exist would be the thing
 * `GlassMaterialEndpoint`'s own comment refuses.
 *
 * What is read is the SHIPPED artifact, for `macos27-profile-export.test.ts`'s
 * reason: `@vitreajs/vitrea-web` resolves to `dist/`, so this is the selection a
 * consumer would install.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { colorSchemeMaterialProfile, macos26MaterialProfileDocument } from "@vitreajs/vitrea-web";

import {
  DEFAULT_MATERIAL_PROFILE,
  materialDigestInput,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

interface ProfileDocument {
  readonly profileKey: string;
  readonly patch: MaterialProfilePatch;
  readonly identityWithRuntimeDefault?: boolean;
  readonly resolvedMaterialSha256: string;
}

const load = (key: string): ProfileDocument =>
  JSON.parse(
    readFileSync(resolve(import.meta.dirname, "..", "profiles", `${key}.json`), "utf8"),
  ) as ProfileDocument;

const DOCUMENTS = {
  light: load("apple-macos-26.5-1x-light-standard"),
  dark: load("apple-macos-26.5-1x-dark-standard"),
} as const;

/**
 * **The two frozen documents' own fields are the pin again** (W31 Decision Log
 * 1 (a); claims §5.164).
 *
 * Between W30 G2 and W31 G3 this file read the digests through
 * `profiles/digest-supersessions.json`, because W30's eight inert leaves moved
 * every document's resolved fingerprint without moving a pixel and a frozen
 * document's bytes could not be re-recorded. The digest rule removes the
 * indirection: the fingerprint drops a leaf at its declared inert identity, so
 * the material a root selects fingerprints to the number the document records,
 * and `root.material` reports that same number.
 *
 * The record is kept as history and pinned by `digest-supersessions.test.ts`.
 */

/** `tuned-profiles.test.ts`'s fingerprint: sorted keys, sha256, first 16 hex. */
const fingerprint = (resolved: unknown): string => {
  const canonical = (value: unknown): unknown =>
    Array.isArray(value)
      ? value.map(canonical)
      : value !== null && typeof value === "object"
        ? Object.fromEntries(
            Object.keys(value as Record<string, unknown>)
              .sort()
              .map((key) => [key, canonical((value as Record<string, unknown>)[key])]),
          )
        : value;
  return createHash("sha256").update(JSON.stringify(canonical(resolved))).digest("hex").slice(0, 16);
};

/**
 * The live fingerprint, under the digest rule (W31; claims §5.161 §7b).
 *
 * The hash above is deliberately restated in three places; the RULE is not —
 * `materialDigestInput` is the one implementation, beside
 * `DEFAULT_MATERIAL_PROFILE`, because a table walk whose drift would be silent
 * is the half a second copy could not check.
 */
const liveDigest = (resolved: unknown): string => fingerprint(materialDigestInput(resolved));

describe("the macOS 26.5 document, as a root selects it", () => {
  for (const scheme of ["light", "dark"] as const) {
    it(`${scheme}: the selected patch resolves to the document's own recorded material`, () => {
      const selected = colorSchemeMaterialProfile(scheme, macos26MaterialProfileDocument);
      const resolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, selected ?? {});
      expect(
        liveDigest(resolved),
        `${DOCUMENTS[scheme].profileKey}: selecting macos26MaterialProfileDocument no longer ` +
          `draws the material that document records — a page pinned to macOS 26.5 is drawing ` +
          `something else`,
      ).toBe(DOCUMENTS[scheme].resolvedMaterialSha256);
      // And the document's bytes are untouched, which is what X1 protects: the
      // pin returns to the recorded field by a rule, never by an edit.
      expect(DOCUMENTS[scheme].resolvedMaterialSha256).toBe(
        scheme === "light" ? "b2b570e4adcea8fb" : "874be66ea501621b",
      );
    });

    it(`${scheme}: the endpoint's hand-written digest is the current one`, () => {
      // These two are hand-written rather than generated — the macOS 26.5
      // documents predate `generate-macos27-profile.mjs` and its sibling — so
      // they are the two digests in either shipped document with nothing
      // upstream of them. This is that missing upstream, and since W31 G3 the
      // upstream is the document's own field again: `root.material` names what
      // actually drew, and under the digest rule what draws fingerprints to the
      // number the document was sealed at.
      expect(macos26MaterialProfileDocument.active[scheme].resolvedMaterialSha256).toBe(
        DOCUMENTS[scheme].resolvedMaterialSha256,
      );
      expect(macos26MaterialProfileDocument.active[scheme].profileKey).toBe(
        DOCUMENTS[scheme].profileKey,
      );
    });
  }

  it("selects the renderer's own defaults for light, and something else for dark", () => {
    // The light endpoint ships no patch because that document IS the identity
    // with the runtime default (`identityWithRuntimeDefault` in the file), and
    // the absence is the statement — an empty patch would be a second name for
    // it. The dark endpoint's being a real patch is what makes the pair above
    // discriminating rather than two readings of one material.
    expect(colorSchemeMaterialProfile("light", macos26MaterialProfileDocument)).toBeUndefined();
    expect(DOCUMENTS.light.identityWithRuntimeDefault).toBe(true);
    expect(colorSchemeMaterialProfile("dark", macos26MaterialProfileDocument)).toBeDefined();
    expect(DOCUMENTS.light.resolvedMaterialSha256).not.toBe(DOCUMENTS.dark.resolvedMaterialSha256);
  });
});
