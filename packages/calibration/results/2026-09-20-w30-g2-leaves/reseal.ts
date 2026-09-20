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
 *
 * ## The construction, and the assertion that it is the right one
 *
 * **Amended 2026-09-20 (G2 review closure; claims §5.158 §8, finding 1).** The
 * first version of this file computed every record as
 * `fingerprint(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch))`. That is
 * the construction for the four documents that are patches over the default, and
 * it is the wrong one for the two RECEDED documents: a receded document is a
 * difference over the ACTIVE document of its own scheme — it says so in its own
 * `appliesOver` and `resolvedOverActiveDocument` fields — so its digest is taken
 * over `withMaterialOverrides(withMaterialOverrides(DEFAULT, active), receded)`,
 * the composition the page performs, in the page's order, exactly as W29 G3b's
 * `results/2026-09-19-w29-g3b-shadow-recede/seal.ts` takes it. A digest over the
 * recede alone is a digest of a material nothing draws, and the two it produced
 * (`91a22b7ad3473d51`, `1b40966487534d1c`) were superseded by the composed
 * readings (`035f537d9c27e3ed`, `4763b0d195fdb077`) — which are what the browser
 * prints in `platform-web/e2e/shared/window-activation.spec.ts`.
 *
 * So the branch is read off the document rather than off a list here, and it is
 * backed by an ASSERTION rather than by care: for every document, the resolved
 * material MINUS the eight leaves by name must fingerprint to the document's own
 * `resolvedMaterialSha256`. That is a statement about the construction and not
 * about the values — the sealed digest was taken over the pre-leaf material
 * through the same composition, so only the construction the document was
 * actually sealed under can reproduce it. A record produced by any other one now
 * throws here instead of being written.
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
const patchOf = (document: Record<string, unknown>): MaterialProfilePatch =>
  document["patch"] as MaterialProfilePatch;

/**
 * The document this one is a difference OVER, by file name, or `undefined` where
 * it is a patch over the renderer's default.
 *
 * Read from the document's own two fields rather than from a list here.
 * `resolvedOverActiveDocument` is what W29 G3b's `seal.ts` wrote when it sealed
 * the receded pair and is the authority. `appliesOver` is the human-facing
 * statement of the same relation and is NOT a synonym: on the frozen macOS 26.5
 * dark document it names `@vitrea/renderer-webgpu DEFAULT_MATERIAL_PROFILE`,
 * which is the default and not a document. So it is read only where it names a
 * document file, and then only to cross-check — a document whose two fields
 * disagreed would leave "which material is this a difference from" with two
 * answers.
 */
function activeDocumentOf(document: Record<string, unknown>): string | undefined {
  const sealed = document["resolvedOverActiveDocument"];
  if (typeof sealed !== "string") return undefined;
  const declared = document["appliesOver"];
  if (typeof declared === "string" && declared.endsWith(".json") && !declared.endsWith(sealed)) {
    throw new Error(
      `${String(document["profileKey"])}: resolvedOverActiveDocument ${sealed} and appliesOver ` +
        `${declared} name different documents`,
    );
  }
  return sealed.replace(/\.json$/, "");
}

/**
 * The material a document RESOLVES to, in the order the page composes it: the
 * renderer's default, then the active patch where this document is a difference
 * over one, then the document's own patch.
 */
function resolvedMaterialOf(document: Record<string, unknown>): object {
  const over = activeDocumentOf(document);
  const base =
    over === undefined
      ? DEFAULT_MATERIAL_PROFILE
      : withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patchOf(read(over)));
  return withMaterialOverrides(base, patchOf(document)) as object;
}

/** The same material with the eight leaves removed by name, for the assertion. */
function withoutLeaves(material: object, paths: readonly string[]): object {
  const copy = JSON.parse(JSON.stringify(material)) as Record<string, unknown>;
  for (const leaf of paths) {
    const parts = leaf.split(".");
    let node = copy;
    for (const part of parts.slice(0, -1)) node = node[part] as Record<string, unknown>;
    const last = parts[parts.length - 1] ?? "";
    if (!(last in node)) throw new Error(`${leaf}: not a leaf of the resolved material`);
    delete node[last];
  }
  return copy;
}

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
  const material = resolvedMaterialOf(document);
  const current = fingerprint(material);
  if (recorded !== SHIPPED[name]) {
    throw new Error(`${name}: recorded ${recorded}, expected the sealed ${String(SHIPPED[name])}`);
  }
  if (recorded === current) {
    throw new Error(`${name}: the digest did not move — there is nothing to supersede`);
  }
  /*
   * The construction is the one the document was sealed under, proved rather
   * than asserted by a comment: strip W30's eight leaves out of the material
   * this file just composed and the rest must fingerprint to the document's own
   * field. It cannot, if the composition is wrong — the recede-over-default
   * merge this file first used reproduces nothing.
   */
  const stripped = fingerprint(withoutLeaves(material, LEAVES));
  if (stripped !== recorded) {
    throw new Error(
      `${name}: the resolved material minus the eight leaves fingerprints to ${stripped}, not ` +
        `to the document's own ${recorded} — this is not the construction the document was ` +
        `sealed under (a receded document is a difference over its scheme's ACTIVE document; ` +
        `see results/2026-09-19-w29-g3b-shadow-recede/seal.ts and claims §5.158 §8)`,
    );
  }
  const over = activeDocumentOf(document);
  supersessions.push({
    profileKey: name,
    recordedSha256: recorded,
    currentSha256: current,
    // Named in the record itself, so a reader of the file can see which of the
    // two constructions each digest was taken through without running anything.
    ...(over === undefined ? {} : { resolvedOverActiveDocument: `${over}.json` }),
    leaves: LEAVES,
    decisionLog: DECISION_LOG,
    date: DATE,
  });
  console.log(
    `${name}: recorded ${recorded} -> current ${current} (document unedited; resolved over ` +
      `${over === undefined ? "DEFAULT_MATERIAL_PROFILE" : `${over}.json`}; ` +
      `minus the eight leaves ${stripped})`,
  );
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
        "WHICH MATERIAL EACH DIGEST IS TAKEN OVER. Four of the six documents are patches",
        "over the renderer's `DEFAULT_MATERIAL_PROFILE`. The two `-receded` ones are not:",
        "a receded document is a difference over the ACTIVE document of its own scheme,",
        "which it names in `appliesOver` and `resolvedOverActiveDocument`, so its digest",
        "is taken over `withMaterialOverrides(withMaterialOverrides(DEFAULT, active),",
        "receded)` — the composition the page performs, in the page's order, as W29 G3b",
        "sealed them. The entries below repeat that field so the construction is legible",
        "from the record. The generating script asserts it rather than assuming it: the",
        "resolved material minus the eight leaves must fingerprint to the document's own",
        "`resolvedMaterialSha256`, which only the right construction can reproduce.",
        "(2026-09-20, G2 review closure — the first run of the script took both receded",
        "digests over the recede alone and recorded `91a22b7ad3473d51` and",
        "`1b40966487534d1c`, a merge nothing draws; claims §5.158 §8, finding 1.)",
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
