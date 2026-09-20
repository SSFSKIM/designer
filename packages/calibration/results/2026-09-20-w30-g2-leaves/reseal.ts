/**
 * W30 G2 — the digests, after the leaves. Writes the supersession record and
 * **edits no profile document**.
 *
 *   npx tsx results/2026-09-20-w30-g2-leaves/reseal.ts
 *
 * Every profile document's `resolvedMaterialSha256` is a digest over the FULLY
 * RESOLVED material, so eight inert leaves move all six of them while moving no
 * pixel on either tier. That is the one-time X1 exemption W29 Decision Log 7 (a)
 * granted, and W30 Decision Log 1 (a) shaped it as a supersession recorded
 * BESIDE the two frozen macOS 26.5 documents rather than inside them, because
 * `test/adopted-thresholds.test.ts` builds `SHIPPED_DOCUMENT_HASHES` from the
 * documents' own bytes: an edit to either would empty all 1,107 frozen macOS
 * 26.5 rows out of every bound, floor and predicate, silently and passing.
 *
 * **W30 Decision Log 4 (a) extends that to all six.** This child re-sealed the
 * four macOS 27 documents in place — the step the brief asked for, because they
 * are not frozen — and measured the same failure on the bed nobody had checked:
 * the 455 committed macOS 27 rows (230 gated cells across six profiles) left
 * every bound the moment the bytes moved, `adopted-thresholds.test.ts` went red
 * by 15 cases and `tier-coherence.test.ts` by 8. So no document is re-sealed
 * here at all. The record below carries one entry per SHIPPED document — six,
 * not two — and each entry states both readings:
 *
 *   - `recordedSha256`, the document's own field: the digest it was sealed at,
 *     and still the reading.
 *   - `currentSha256`, what the same fingerprint resolves to over a default that
 *     now carries the eight leaves.
 *
 * A re-seal and its canonical read land in one merge from here on (Decision Log
 * 4 (b)), so the gated bed is never empty on main and no count is ever written
 * down to zero to make a merge green. G3 seals the macOS 27 documents when it
 * genuinely moves their material, and reads at those bytes in the same child.
 *
 * `fingerprint` is `results/2026-09-19-w29-g3-refit/seal.ts`'s, duplicated
 * deliberately: that file is committed evidence of W29's own sealing and is not
 * edited by a later wave.
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const PROFILES = resolve(import.meta.dirname, "..", "..", "profiles");

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

const path = (name: string): string => resolve(PROFILES, `${name}.json`);
const read = (name: string): Record<string, unknown> =>
  JSON.parse(readFileSync(path(name), "utf8")) as Record<string, unknown>;

const resolvedOf = (document: Record<string, unknown>): string =>
  fingerprint(
    withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, document["patch"] as MaterialProfilePatch),
  );

/** The leaves, exactly as `test/w30-operator-identity.test.ts` names them. */
const LEAVES = [
  "outerShadow.sigmaSlopePerSpan",
  "outerShadow.sigmaSpanRefPx",
  "outerShadow.sigmaThinOffsetPx",
  "sizeHeavySecondSigma",
  "sizeHeavySecondSigma2x",
  "sizeHeavySecondShare",
  "sizeScatterScaleGain",
  "sizeScatterScaleRef",
];

const DECISION_LOG = "W30 Decision Log 1 (a); W30 Decision Log 4 (a); W29 Decision Log 7 (a)";
const DATE = "2026-09-20";

/**
 * Every shipped document, with the digest its own field carries — transcribed
 * here so the script REFUSES to write a record from a tree where any document's
 * bytes have already moved. The record is a statement about the documents as
 * they stand, and a statement produced from a moved document would be one.
 *
 * The seed (`apple-macos-26.5.seed.json`) is not a material patch document and
 * carries no `resolvedMaterialSha256`; it is not here and is not edited.
 */
const SHIPPED: Record<string, string> = {
  "apple-macos-26.5-1x-light-standard": "b2b570e4adcea8fb",
  "apple-macos-26.5-1x-dark-standard": "874be66ea501621b",
  "apple-macos-27.0-1x-light-standard-glass0.5": "e825cb034c9070e4",
  "apple-macos-27.0-1x-dark-standard-glass0.5": "8439eb808495f5bf",
  "apple-macos-27.0-1x-light-standard-glass0.5-receded": "8dc63b265c1de038",
  "apple-macos-27.0-1x-dark-standard-glass0.5-receded": "3264b6cdde64bc8b",
};

const supersessions: unknown[] = [];
for (const name of Object.keys(SHIPPED)) {
  const document = read(name);
  const recorded = document["resolvedMaterialSha256"] as string;
  const current = resolvedOf(document);
  if (recorded !== SHIPPED[name]) {
    throw new Error(`${name}: recorded ${recorded}, expected the sealed ${String(SHIPPED[name])}`);
  }
  if (recorded === current) {
    throw new Error(`${name}: the digest did not move — there is nothing to supersede`);
  }
  supersessions.push({
    profileKey: name,
    recordedSha256: recorded,
    currentSha256: current,
    leaves: LEAVES,
    decisionLog: DECISION_LOG,
    date: DATE,
  });
  console.log(`${name}: recorded ${recorded} -> current ${current} (document unedited)`);
}

writeFileSync(
  resolve(PROFILES, "digest-supersessions.json"),
  `${JSON.stringify(
    {
      $comment: [
        "The digests every shipped profile document's pin resolves to, recorded BESIDE",
        "the documents rather than in them — W30 Decision Log 1 (a) and 4 (a), spending",
        "the one-time X1 exemption W29 Decision Log 7 (a) granted.",
        "",
        "`recordedSha256` is the document's own `resolvedMaterialSha256`: the digest it",
        "was sealed at, and still the reading. `currentSha256` is what the same",
        "fingerprint resolves to over a default that now carries W30's eight inert",
        "leaves. The two differ because the digest is taken over the FULLY RESOLVED",
        "material and the material gained eight keys, every one of them at a value that",
        "is an algebraic identity; no pixel of either tier moved, and",
        "`results/2026-09-20-w30-g2-leaves/` carries the proofs.",
        "",
        "WHY NO DOCUMENT WAS EDITED, INCLUDING THE FOUR THAT ARE NOT FROZEN.",
        "`test/adopted-thresholds.test.ts` builds `SHIPPED_DOCUMENT_HASHES` from the",
        "BYTES of every file in this directory, and `atAShippedDocument` keeps only",
        "matrix rows whose `capturePath` names a current hash. That is what rules the",
        "frozen pair: re-recording a digest inside either would empty all 1,107 macOS",
        "26.5 rows out of every bound, floor, partition count and conditioning exclusion",
        "stated over that bed. G2 measured that the same is true of the macOS 27 four —",
        "re-sealing them dropped 230 gated cells across six profiles and turned",
        "`adopted-thresholds.test.ts` red by 15 cases and `tier-coherence.test.ts` by 8 —",
        "so the record covers all six and the documents keep their bytes.",
        "",
        "From here a re-seal and its canonical read land in ONE merge (Decision Log",
        "4 (b)), so the gated bed is never empty on main and no count is ever written",
        "down to zero to make a merge green. G3 seals the macOS 27 documents when it",
        "genuinely moves their material and reads at those bytes in the same child; the",
        "four macOS 27 entries below leave this file then, and the two frozen ones stay.",
        "",
        "The exemption is spent once. No later wave adds a record to this file without a",
        "new grant from the user.",
      ],
      recordedBy: "W30 G2",
      claims: "docs/doperpowers/specs/c9a-fidelity-claims.md §5.158",
      supersessions,
    },
    null,
    2,
  )}\n`,
);
console.log(`wrote profiles/digest-supersessions.json (${String(supersessions.length)} records)`);
