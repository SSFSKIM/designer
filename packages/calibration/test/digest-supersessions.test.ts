/**
 * The supersession record stays TRUE as history (W31 Decision Log 1 (a); claims
 * §5.164).
 *
 * `profiles/digest-supersessions.json` recorded, per shipped document, the
 * digest it was sealed at and the digest its pin resolved to after W30's eight
 * inert operator leaves moved the plain fingerprint of every material
 * (claims §5.158). W31's digest rule removed the reason for the record: a leaf
 * at its declared inert identity is dropped, so a document's own field is the
 * live fingerprint again and the three files that read this record now read the
 * documents instead.
 *
 * The record is **kept**, because a recorded number is added beside and never
 * deleted — and a record nothing checks is a record that quietly becomes false.
 * So this file is its pin, and it asserts both halves against materials rather
 * than against literals:
 *
 *  - every `recordedSha256` is what the document's material fingerprints to
 *    **under the rule** — which is the same statement as "the pins returned to
 *    the documents' own fields", read from the record's side;
 *  - every `currentSha256` is what the PLAIN fingerprint gives over the
 *    material **as it stood at W30's close** — today's resolved material with
 *    every identity-table entry added after W30 dropped at its identity.
 *
 * The second half is what makes this history rather than an assertion about
 * today. It also fails loudly if a later wave adds a leaf to the material
 * without an identity-table entry, which is the one failure mode the rule's own
 * holes list calls the loud one.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import {
  DEFAULT_MATERIAL_PROFILE,
  MATERIAL_IDENTITY_TABLE,
  materialDigestInput,
  materialLeafAt,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

import { DIGEST_SUPERSESSIONS } from "./digest-supersessions";

/** `tuned-profiles.test.ts`'s fingerprint: sorted keys, sha256, first 16 hex. */
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

/**
 * The waves whose leaves existed when the record was written. Everything the
 * identity table has gained since is removed before the plain fingerprint, which
 * is what reconstructs the material W30's close actually hashed.
 */
const WAVES_AT_THE_RECORD = new Set(["W29", "W30"]);

function withoutPostRecordLeaves(resolved: unknown): unknown {
  const dropped = MATERIAL_IDENTITY_TABLE.filter(
    (entry) => !WAVES_AT_THE_RECORD.has(entry.wave),
  ).flatMap((entry) => [...Object.keys(entry.gate), ...entry.gated]);
  const strip = (value: unknown, prefix = ""): unknown => {
    if (value === null || typeof value !== "object" || Array.isArray(value)) return value;
    return Object.fromEntries(
      Object.entries(value)
        .map(([key, child]) => [prefix === "" ? key : `${prefix}.${key}`, key, child] as const)
        .filter(([path]) => !dropped.includes(path))
        .map(([path, key, child]) => [key, strip(child, path)]),
    );
  };
  return strip(resolved);
}

const PROFILES = resolve(import.meta.dirname, "..", "profiles");
const load = (key: string): { patch: MaterialProfilePatch; resolvedMaterialSha256: string } =>
  JSON.parse(readFileSync(resolve(PROFILES, `${key}.json`), "utf8")) as never;

const resolvedFor = (entry: (typeof DIGEST_SUPERSESSIONS)[number]): unknown => {
  const base =
    entry.resolvedOverActiveDocument === undefined
      ? DEFAULT_MATERIAL_PROFILE
      : withMaterialOverrides(
          DEFAULT_MATERIAL_PROFILE,
          load(entry.resolvedOverActiveDocument.replace(/\.json$/, "")).patch,
        );
  return withMaterialOverrides(base, load(entry.profileKey).patch);
};

describe("the digest supersession record, as history (claims §5.164)", () => {
  it("is the two frozen documents and no more — the exemption was spent once", () => {
    // W29 Decision Log 7 (a) granted one exemption and W30 Decision Log 4 (a)
    // scoped the record; the four macOS 27 records were retired at W30 G3 when
    // those documents were re-sealed. A third entry would be a second exemption,
    // which needs a grant and not a test edit — and under W31's rule no wave has
    // a reason to want one.
    expect(DIGEST_SUPERSESSIONS.length).toBe(2);
    expect(new Set(DIGEST_SUPERSESSIONS.map((entry) => entry.profileKey))).toEqual(
      new Set(["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-1x-dark-standard"]),
    );
  });

  for (const entry of DIGEST_SUPERSESSIONS) {
    it(`${entry.profileKey}: its recordedSha256 is what the material fingerprints to under the rule`, () => {
      const resolved = resolvedFor(entry);
      expect(fingerprint(materialDigestInput(resolved))).toBe(entry.recordedSha256);
      // And the document's own field agrees with the record's, which is what
      // "the pins returned to the documents" means from this side.
      expect(load(entry.profileKey).resolvedMaterialSha256).toBe(entry.recordedSha256);
    });

    it(`${entry.profileKey}: its currentSha256 still reproduces under rule 1, at W30's material`, () => {
      const resolved = resolvedFor(entry);
      expect(
        fingerprint(withoutPostRecordLeaves(resolved)),
        `${entry.profileKey}: the record's currentSha256 no longer reproduces — either a ` +
          `leaf landed without a MATERIAL_IDENTITY_TABLE entry, or a constant moved that ` +
          `W30's close did not have. The record is history and may not be edited; find what ` +
          `moved instead (claims §5.164)`,
      ).toBe(entry.currentSha256);
      // The two readings are different numbers, so neither case above is the
      // other one restated.
      expect(entry.currentSha256).not.toBe(entry.recordedSha256);
    });

    it(`${entry.profileKey}: names the leaves the interval's difference was`, () => {
      // The record says which leaves moved its reading. Every one of them is a
      // leaf the material actually has, and every one is dropped by the table
      // today — which is exactly why the interval closed.
      const resolved = resolvedFor(entry);
      const droppedNow = new Set(
        MATERIAL_IDENTITY_TABLE.flatMap((tableEntry) => [
          ...Object.keys(tableEntry.gate),
          ...tableEntry.gated,
        ]),
      );
      for (const leaf of entry.leaves) {
        expect(materialLeafAt(resolved, leaf), `${leaf}: named in the record, absent`).not.toBe(
          undefined,
        );
        expect(droppedNow, `${leaf}: named in the record, not in the identity table`).toContain(
          leaf,
        );
      }
    });
  }
});
