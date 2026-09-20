/**
 * W30 G3 — retire the four macOS 27 supersession records, in the commit that
 * re-seals the documents they stood in for.
 *
 *   npx tsx results/2026-09-20-w30-g3-operators/retire-27-records.ts
 *
 * W30 G2 could not re-seal the four macOS 27 documents: `atAShippedDocument`
 * hashes every document's BYTES, so moving them would have emptied the 455
 * committed macOS 27 rows out of every bound before a read existed to replace
 * them (claims §5.158 §4). Decision Log 4 (a) therefore recorded all six shipped
 * documents in `digest-supersessions.json` and 4 (b) ruled that a re-seal and
 * its canonical read land in ONE merge from then on.
 *
 * This is that merge. `seal.ts` gives the four macOS 27 documents their own
 * current digests back, so the indirection those four records existed to carry
 * has nothing left to carry: the document's own field IS the digest its material
 * resolves to again. The record keeps exactly the two macOS 26.5 documents,
 * whose bytes can never move and whose pins therefore need it permanently.
 *
 * The two that stay are **recomputed here from the documents on disk** rather
 * than copied through, and the script refuses to write if either reading
 * disagrees — the same closed loop `reseal.ts` took after the G2 review closure
 * found a digest taken over a material nothing draws. A retirement that carried
 * a stale reading through would be the same failure one commit later.
 *
 * Nothing under a macOS 26.5-keyed path is written (X1): the two frozen
 * documents are read.
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
const RECORD = resolve(PROFILES, "digest-supersessions.json");

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

const KEPT = [
  "apple-macos-26.5-1x-light-standard",
  "apple-macos-26.5-1x-dark-standard",
];

interface Record_ {
  profileKey: string;
  recordedSha256: string;
  currentSha256: string;
  resolvedOverActiveDocument?: string;
  leaves: string[];
  decisionLog: string;
  date: string;
}

const file = JSON.parse(readFileSync(RECORD, "utf8")) as {
  supersessions: Record_[];
};

const kept: Record_[] = [];
for (const key of KEPT) {
  const record = file.supersessions.find((entry) => entry.profileKey === key);
  if (record === undefined) throw new Error(`${key}: no record to keep`);
  const document = JSON.parse(readFileSync(resolve(PROFILES, `${key}.json`), "utf8")) as {
    patch: MaterialProfilePatch;
    resolvedMaterialSha256: string;
  };
  const current = fingerprint(
    withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, document.patch),
  );
  if (document.resolvedMaterialSha256 !== record.recordedSha256) {
    throw new Error(
      `${key}: the document's own digest is ${document.resolvedMaterialSha256}, the record ` +
        `holds ${record.recordedSha256} — a frozen document's bytes moved (X1)`,
    );
  }
  if (current !== record.currentSha256) {
    throw new Error(
      `${key}: the material resolves to ${current}, the record holds ${record.currentSha256}`,
    );
  }
  kept.push(record);
  console.log(`kept ${key}: recorded ${record.recordedSha256} -> current ${current} (recomputed)`);
}

const retired = file.supersessions.filter((entry) => !KEPT.includes(entry.profileKey));
for (const record of retired) {
  const document = JSON.parse(
    readFileSync(resolve(PROFILES, `${record.profileKey}.json`), "utf8"),
  ) as { resolvedMaterialSha256: string };
  console.log(
    `retired ${record.profileKey}: the record held ${record.currentSha256}; the document now ` +
      `carries ${document.resolvedMaterialSha256} in its own field`,
  );
}
if (retired.length !== 4) {
  throw new Error(`expected the four macOS 27 records, found ${String(retired.length)}`);
}

writeFileSync(
  RECORD,
  `${JSON.stringify(
    {
      $comment: [
        "The digests the two FROZEN macOS 26.5 documents' pins resolve to, recorded",
        "BESIDE the documents rather than in them — W30 Decision Log 1 (a), spending the",
        "one-time X1 exemption W29 Decision Log 7 (a) granted.",
        "",
        "`recordedSha256` is the document's own `resolvedMaterialSha256`: the digest it",
        "was sealed at, and still the reading. `currentSha256` is what the same",
        "fingerprint resolves to over a default that now carries W30's eight operator",
        "leaves. The two differ because the digest is taken over the FULLY RESOLVED",
        "material and the material gained eight keys; no macOS 26.5 pixel moved, and",
        "`results/2026-09-20-w30-g2-leaves/` carries the proofs.",
        "",
        "WHY ONLY TWO RECORDS, WHERE W30 G2 WROTE SIX. G2 could not re-seal the four",
        "macOS 27 documents: `test/adopted-thresholds.test.ts` builds",
        "`SHIPPED_DOCUMENT_HASHES` from the documents' own BYTES and `atAShippedDocument`",
        "keeps only matrix rows whose `capturePath` names a current hash, so moving those",
        "bytes would have emptied the 455 committed macOS 27 rows out of every bound",
        "before a read existed to replace them (claims §5.158 §4). Decision Log 4 (a)",
        "therefore covered all six, and 4 (b) ruled that a re-seal and its canonical read",
        "land in ONE merge from then on. W30 G3 is that merge: it gives the eight leaves",
        "values, re-seals the four macOS 27 documents and reads the whole bed at those",
        "bytes in the same commit (claims §5.159). Their own fields are their current",
        "digests again, so the indirection has nothing left to carry and the four records",
        "are RETIRED — the readings they held are kept in each document's own",
        "`$comment-sha-history`, beside the digest they superseded.",
        "",
        "The two below are permanent: the frozen documents' bytes can never move, so",
        "their pins will always need the indirection this file is.",
        "",
        "The exemption is spent once. No later wave adds a record to this file without a",
        "new grant from the user.",
      ],
      recordedBy: "W30 G2, reduced to the frozen pair by W30 G3",
      claims: "docs/doperpowers/specs/c9a-fidelity-claims.md §5.158, §5.159",
      supersessions: kept,
    },
    null,
    2,
  )}\n`,
);
console.log(`wrote profiles/digest-supersessions.json (${String(kept.length)} records)`);
