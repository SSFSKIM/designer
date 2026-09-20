/**
 * The supersession record beside the profile documents, read once for the three
 * files that pin it.
 *
 * Not a test file (the vitest `include` is `test/**\/*.test.ts`): it is the
 * reader `tuned-profiles.test.ts`, `macos26-document-selection.test.ts` and
 * `macos27-profile-export.test.ts` share. The `fingerprint` beside it in those
 * files is deliberately duplicated — an algorithm restated is an algorithm two
 * places can check — but a RECORD has one copy by definition, and three readers
 * that disagreed about which entry belongs to which document would be three
 * different pins.
 *
 * ## What the record is
 *
 * W30's operator wave added eight leaves to `DEFAULT_MATERIAL_PROFILE` for two
 * operators, at values that are algebraic identities (claims §5.156 §2 and §3,
 * §5.158). Every profile document's `resolvedMaterialSha256` is a digest over
 * the FULLY RESOLVED material, so a material that gains a key moves every
 * document's digest whatever that key holds — and none of the six documents'
 * pixels moved at all. That is the one-time X1 exemption W29 Decision Log 7 (a)
 * granted.
 *
 * It is spent as a record BESIDE the documents rather than as a re-recorded
 * digest inside them (W30 Decision Log 1 (a)), and the record covers **all six
 * shipped documents rather than only the two frozen ones** (Decision Log 4 (a)).
 * The reason is one mechanism read twice: `adopted-thresholds.test.ts` builds
 * `SHIPPED_DOCUMENT_HASHES` from the documents' own BYTES and `atAShippedDocument`
 * keeps only matrix rows whose `capturePath` names a current hash. An edit to a
 * frozen macOS 26.5 document would empty all 1,107 frozen rows out of every
 * bound, floor and predicate; G2 measured that an edit to the four macOS 27
 * documents does the same to their bed — 230 gated cells across six profiles,
 * `adopted-thresholds` red by 15 cases and `tier-coherence` by 8.
 *
 * So each entry states both readings, and a pin asserts both: the document's own
 * field must still be `recordedSha256`, and the material it resolves to today
 * must fingerprint to `currentSha256`. Neither can move quietly.
 *
 * ## Which material "resolves to" means
 *
 * Not one construction for all six. Four of the documents are patches over the
 * renderer's `DEFAULT_MATERIAL_PROFILE`. The two `-receded` ones are differences
 * over the ACTIVE document of their own scheme, which they name in their own
 * `resolvedOverActiveDocument` field and the record repeats — so their digests
 * are taken over `withMaterialOverrides(withMaterialOverrides(DEFAULT, active),
 * receded)`, the composition a root performs when the window loses focus. A
 * digest over the recede alone is a digest of a material nothing draws, which is
 * how the first record carried two readings the browser disagreed with (W30 G2
 * review closure, claims §5.158 §8, finding 1).
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

export interface DigestSupersession {
  /** The document's `profileKey`, which is also its file name. */
  readonly profileKey: string;
  /** The document's own `resolvedMaterialSha256` — the digest it was sealed at. */
  readonly recordedSha256: string;
  /** What that pin resolves to over a default carrying W30's eight leaves. */
  readonly currentSha256: string;
  /**
   * For a RECEDED document, the active document of its own scheme — the patch
   * the difference is composed over before either digest is taken. Absent on the
   * four documents that are patches over the renderer's default.
   */
  readonly resolvedOverActiveDocument?: string;
  /** The leaves the difference is, by dotted path into the resolved material. */
  readonly leaves: readonly string[];
  readonly decisionLog: string;
  readonly date: string;
}

export const DIGEST_SUPERSESSIONS: readonly DigestSupersession[] = (
  JSON.parse(
    readFileSync(
      resolve(import.meta.dirname, "..", "profiles", "digest-supersessions.json"),
      "utf8",
    ),
  ) as { readonly supersessions: readonly DigestSupersession[] }
).supersessions;

/** The record for one document, or a throw naming the document that has none. */
export function supersessionFor(profileKey: string): DigestSupersession {
  const record = DIGEST_SUPERSESSIONS.find((entry) => entry.profileKey === profileKey);
  if (record === undefined) {
    throw new Error(
      `${profileKey}: no digest supersession recorded beside the document — see ` +
        `packages/calibration/profiles/digest-supersessions.json and claims §5.158`,
    );
  }
  return record;
}
