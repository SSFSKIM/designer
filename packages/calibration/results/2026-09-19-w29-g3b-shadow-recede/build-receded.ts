/**
 * W29 G3b — write the two macOS 27 RECEDED documents from this child's own
 * numbers.
 *
 *   npx tsx results/2026-09-19-w29-g3b-shadow-recede/build-receded.ts
 *
 * The shape is G3's `build-documents.py` one axis over. Each 27 receded document
 * is the SHIPPED 26.5 endpoint — `recededMaterialProfile[scheme]`, read through
 * the published package entry exactly as `receded-profile-export.test.ts` reads
 * it — with this child's fitted overrides merged on top, plus its own
 * provenance. Written by a script rather than by hand for the reason G3 gives:
 * a document that "names every fitted constant" has to inherit the whole named
 * set from the endpoint it supersedes, and a hand-copied set is a set with a
 * typo in it.
 *
 * `fitted-receded.json` holds the ONLY numbers this half of the child chose.
 * Every other key in the output is the 26.5 endpoint's, unchanged and still
 * named, which is what makes the document readable as a difference — the same
 * property the 27 active documents have against the 26.5 ones.
 *
 * TypeScript rather than Python, unlike its active-document sibling, for one
 * reason: the base here is not a JSON file, it is a constant exported from
 * `@vitreajs/vitrea-web`. Reading it through the package entry means the
 * document cannot drift from the endpoint the runtime actually ships, and a
 * Python script would have to re-type it.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import { recededMaterialProfile } from "@vitreajs/vitrea-web";

const HERE = import.meta.dirname;
const PROFILES = resolve(HERE, "..", "..", "profiles");

type Patch = Record<string, unknown>;

const isRecord = (value: unknown): value is Patch =>
  value !== null && typeof value === "object" && !Array.isArray(value);

/**
 * The same leaf-by-leaf composition `mergeMaterialProfiles` performs in the
 * page, so the document this writes and the material the page resolves cannot
 * disagree about what an override means. Arrays are leaves — a response curve is
 * one measurement and not four.
 */
function merge(base: Patch, over: Patch): Patch {
  const out: Patch = { ...base };
  for (const [key, value] of Object.entries(over)) {
    const held = out[key];
    out[key] = isRecord(held) && isRecord(value) ? merge(held, value) : value;
  }
  return out;
}

interface Spec {
  readonly documents: readonly {
    readonly profileKey: string;
    readonly scheme: "light" | "dark";
    readonly supersedes: string;
    readonly comment: readonly string[];
    readonly measurement: unknown;
    readonly patch: Patch;
    readonly entries: unknown;
  }[];
}

const spec = JSON.parse(readFileSync(resolve(HERE, "fitted-receded.json"), "utf8")) as Spec;

for (const entry of spec.documents) {
  const base = recededMaterialProfile[entry.scheme] as unknown as Patch;
  const document = {
    $comment: entry.comment,
    profileKey: entry.profileKey,
    schemaVersion: 1,
    recordedAt: "2026-09-19",
    recordedBy: "W29 G3b",
    colorSpace: "srgb",
    kind: "receded-endpoint",
    supersedes: entry.supersedes,
    appliesOver: `packages/calibration/profiles/apple-macos-27.0-1x-${entry.scheme}-standard-glass0.5.json`,
    measurement: entry.measurement,
    patch: merge(base, entry.patch),
    entries: entry.entries,
  };
  const path = resolve(PROFILES, `${entry.profileKey}.json`);
  writeFileSync(path, `${JSON.stringify(document, null, 2)}\n`);
  process.stdout.write(`wrote ${entry.profileKey}.json\n`);
}
