/**
 * W30 G3 — seal the four macOS 27 documents at the fitted operators, and record
 * their hashes before the canonical read.
 *
 *   npx tsx results/2026-09-20-w30-g3-operators/seal.ts <candidate-dir>
 *
 * W29 G3b's `results/2026-09-19-w29-g3b-shadow-recede/seal.ts` is the shape —
 * the two active documents re-resolved over the renderer's default, the two
 * RECEDED ones over the active document of their own scheme, because a digest
 * over the recede alone is a digest of a material nothing draws. Three things
 * are added, and each closes something a later reader found:
 *
 *  1. **It seals the material that was READ**, rather than a material it
 *     composes a second time. The candidate directory is the one the final fit
 *     round rendered from; this file copies each candidate's `patch` wholesale
 *     into the committed document. A seal that re-derived the constants could
 *     seal a material no round ever drew.
 *  2. **It asserts its own construction before it writes** (claims §5.158 §8,
 *     finding 1, and the general lesson beside it: the guard is a closed loop
 *     where the digest is produced). For every document, the material it
 *     resolves to AS IT STANDS — before a byte of this seal — must fingerprint
 *     to the `currentSha256` W30 G2's supersession record holds for it, and
 *     that same material minus W30's eight leaves must fingerprint to the
 *     document's own `resolvedMaterialSha256`. Only the construction the
 *     document was sealed under reproduces either, and the receded pair's two
 *     compositions give different digests, so the wrong one cannot pass.
 *  3. **It refuses a candidate that moved anything but the outer shadow** (X3).
 *     This child fits the σ law, the six occlusion anchors and `liftAmplitude`
 *     and nothing else; a candidate that moved a scatter leaf, a tone knot or a
 *     rim constant is a contract breach, and the place to catch it is before
 *     the bytes that every row of the read will name.
 *
 * The prior digest is kept in the document's own `$comment-sha-history` rather
 * than being overwritten, because a recorded reading is never rewritten — and
 * the history says what moved it, including the interval in which W30 G2's
 * eight inert leaves moved what the pin resolved to without moving these bytes.
 *
 * Nothing under a macOS 26.5-keyed path is opened for writing (X1); the two
 * frozen documents are read, and their own pins are re-asserted on every run.
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

/** W29 G3's fingerprint, duplicated deliberately: that file is committed evidence. */
function digest(resolved: unknown): string {
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
  return createHash("sha256").update(JSON.stringify(canonical(resolved))).digest("hex");
}

/**
 * The digest a document's pin carries: the first sixteen hex of the same sha256.
 *
 * The full digest is printed beside it because
 * `platform-web/e2e/shared/window-activation.spec.ts` pins the WHOLE sha256 of
 * the material the renderer is handed, and its first sixteen digits are this
 * fingerprint — one measurement, read from a browser there and from the
 * documents here. Printing both is what lets that spec's four macOS 27 literals
 * be re-recorded from this run rather than from a failing assertion's message.
 */
const fingerprint = (resolved: unknown): string => digest(resolved).slice(0, 16);

/** The eight leaves W30 G2 landed, exactly as `w30-operator-identity.test.ts` names them. */
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

const path = (name: string): string => resolve(PROFILES, `${name}.json`);
const read = (name: string): Record<string, unknown> =>
  JSON.parse(readFileSync(path(name), "utf8")) as Record<string, unknown>;
const patchOf = (document: Record<string, unknown>): MaterialProfilePatch =>
  document["patch"] as MaterialProfilePatch;

function withoutLeaves(material: object): object {
  const copy = JSON.parse(JSON.stringify(material)) as Record<string, unknown>;
  for (const leaf of LEAVES) {
    const parts = leaf.split(".");
    let node = copy;
    for (const part of parts.slice(0, -1)) node = node[part] as Record<string, unknown>;
    const last = parts[parts.length - 1] ?? "";
    if (!(last in node)) throw new Error(`${leaf}: not a leaf of the resolved material`);
    delete node[last];
  }
  return copy;
}

const supersessions = (
  JSON.parse(readFileSync(resolve(PROFILES, "digest-supersessions.json"), "utf8")) as {
    supersessions: { profileKey: string; recordedSha256: string; currentSha256: string }[];
  }
).supersessions;

/** X1: the two frozen documents still resolve to what the record holds for them. */
for (const name of ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-1x-dark-standard"]) {
  const document = read(name);
  const record = supersessions.find((entry) => entry.profileKey === name);
  if (record === undefined) throw new Error(`${name}: no supersession record`);
  const got = fingerprint(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patchOf(document)));
  if (document["resolvedMaterialSha256"] !== record.recordedSha256 || got !== record.currentSha256) {
    throw new Error(
      `${name}: recorded ${String(document["resolvedMaterialSha256"])} / resolved ${got} against ` +
        `the record's ${record.recordedSha256} / ${record.currentSha256} — X1`,
    );
  }
  process.stdout.write(`X1 ok  ${name} records ${record.recordedSha256}, resolves to ${got}\n`);
}

const candidates = resolve(process.cwd(), process.argv[2] ?? "");
if (process.argv[2] === undefined) {
  throw new Error("seal: name the candidate directory the final fit round rendered from");
}

const ACTIVE = {
  light: "apple-macos-27.0-1x-light-standard-glass0.5",
  dark: "apple-macos-27.0-1x-dark-standard-glass0.5",
} as const;

/**
 * The assertion of §2 above, run on every macOS 27 document BEFORE any of them
 * is written — so a construction error stops the seal rather than being caught
 * half way through it.
 */
for (const scheme of ["light", "dark"] as const) {
  for (const name of [ACTIVE[scheme], `${ACTIVE[scheme]}-receded`]) {
    const document = read(name);
    const over = document["resolvedOverActiveDocument"];
    const base =
      typeof over === "string"
        ? withMaterialOverrides(
            DEFAULT_MATERIAL_PROFILE,
            patchOf(read(over.replace(/\.json$/, ""))),
          )
        : DEFAULT_MATERIAL_PROFILE;
    const material = withMaterialOverrides(base, patchOf(document)) as object;
    const record = supersessions.find((entry) => entry.profileKey === name);
    if (record === undefined) throw new Error(`${name}: no supersession record`);
    const current = fingerprint(material);
    const stripped = fingerprint(withoutLeaves(material));
    if (current !== record.currentSha256) {
      throw new Error(
        `${name}: the unchanged material fingerprints to ${current}, not to the record's ` +
          `${record.currentSha256} — either the material already moved or this is not the ` +
          `construction the record was taken through`,
      );
    }
    if (stripped !== document["resolvedMaterialSha256"]) {
      throw new Error(
        `${name}: the unchanged material minus the eight leaves fingerprints to ${stripped}, ` +
          `not to the document's own ${String(document["resolvedMaterialSha256"])} — this is ` +
          `not the construction the document was sealed under`,
      );
    }
    process.stdout.write(
      `construction ok  ${name}  over ` +
        `${typeof over === "string" ? over : "DEFAULT_MATERIAL_PROFILE"}  ` +
        `current ${current}  minus the leaves ${stripped}\n`,
    );
  }
}

/**
 * X3: the candidate moved the two named structures and nothing else.
 *
 * The outer shadow's block — the σ law together with the six occlusion anchors
 * and `liftAmplitude`, which carry the compensation for the σ they were fitted
 * beside — and the scatter's five leaves, which are the spanning set W30
 * Decision Log 2 (d) landed. Anything else is a contract breach, and the place
 * to catch it is before the bytes that every row of the read will name.
 */
const SCATTER_LEAVES = new Set([
  "sizeHeavySecondSigma",
  "sizeHeavySecondSigma2x",
  "sizeHeavySecondShare",
  "sizeScatterScaleGain",
  "sizeScatterScaleRef",
]);

function assertOnlyTheShadowMoved(name: string, before: MaterialProfilePatch,
                                  after: MaterialProfilePatch): string[] {
  const moved: string[] = [];
  const keys = new Set([...Object.keys(before), ...Object.keys(after)]);
  for (const key of keys) {
    const a = JSON.stringify((before as Record<string, unknown>)[key]);
    const b = JSON.stringify((after as Record<string, unknown>)[key]);
    if (a === b) continue;
    if (SCATTER_LEAVES.has(key)) {
      moved.push(`${key} ${a ?? "absent"} -> ${b ?? "absent"}`);
      continue;
    }
    if (key !== "outerShadow") {
      throw new Error(
        `${name}: the candidate moves \`${key}\`, which is outside this child's fit — X3 ` +
          `admits the σ law, the six occlusion anchors, liftAmplitude and the scatter's ` +
          `five leaves, and nothing else`,
      );
    }
    const shadowBefore = ((before as Record<string, unknown>)[key] ?? {}) as Record<string, unknown>;
    const shadowAfter = ((after as Record<string, unknown>)[key] ?? {}) as Record<string, unknown>;
    for (const leaf of new Set([...Object.keys(shadowBefore), ...Object.keys(shadowAfter)])) {
      if (JSON.stringify(shadowBefore[leaf]) !== JSON.stringify(shadowAfter[leaf])) {
        moved.push(`${leaf} ${JSON.stringify(shadowBefore[leaf])} -> ${JSON.stringify(shadowAfter[leaf])}`);
      }
    }
  }
  return moved;
}

const resolvedActive: Record<"light" | "dark", MaterialProfilePatch> = {} as never;
const lines: string[] = [];

for (const scheme of ["light", "dark"] as const) {
  for (const name of [ACTIVE[scheme], `${ACTIVE[scheme]}-receded`]) {
    const document = read(name);
    const candidate = JSON.parse(
      readFileSync(resolve(candidates, `${name}.json`), "utf8"),
    ) as Record<string, unknown>;
    if (candidate["profileKey"] !== name) {
      throw new Error(`${candidates}/${name}.json declares ${String(candidate["profileKey"])}`);
    }
    const moved = assertOnlyTheShadowMoved(name, patchOf(document), patchOf(candidate));
    /*
     * The candidate's patch AND its prose. A profile document carries its method
     * text beside its values — that is what makes it evidence rather than a
     * configuration file — and the text that describes this fit is written into
     * the candidate before the seal, so that the digest recorded here is the
     * digest of the bytes the canonical read is taken at. Everything the seal
     * itself owns is restored below.
     */
    document["patch"] = candidate["patch"];
    for (const field of ["$comment", "entries", "measurement"]) {
      if (candidate[field] !== undefined) document[field] = candidate[field];
    }
    if (name === ACTIVE[scheme]) resolvedActive[scheme] = patchOf(document);

    const material =
      name === ACTIVE[scheme]
        ? withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patchOf(document))
        : withMaterialOverrides(
            withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, resolvedActive[scheme]),
            patchOf(document),
          );
    const previous = String(document["resolvedMaterialSha256"]);
    const record = supersessions.find((entry) => entry.profileKey === name);
    const sealed = fingerprint(material);
    const history = Array.isArray(document["$comment-sha-history"])
      ? (document["$comment-sha-history"] as string[])
      : [];
    document["$comment-sha-history"] = [
      ...history,
      `${previous} — sealed by W29 G3b (claims §5.154 §7). Between that seal and this one, ` +
        `W30 G2's eight inert operator leaves moved what this document's pin RESOLVES to ` +
        `without moving its bytes, and profiles/digest-supersessions.json recorded the ` +
        `interval's reading as ${record?.currentSha256 ?? "—"} (claims §5.158 §3). This ` +
        `document is re-sealed at ${sealed} by W30 G3, which gives those leaves values ` +
        `(claims §5.159); the macOS 27 records leave that file in the same commit and the ` +
        `two frozen macOS 26.5 records stay.`,
    ];
    document["resolvedMaterialSha256"] = sealed;
    writeFileSync(path(name), `${JSON.stringify(document, null, 2)}\n`);
    const file = createHash("sha256").update(readFileSync(path(name))).digest("hex");
    lines.push(
      `sealed ${name}\n  resolvedMaterialSha256 ${sealed}\n` +
        `  material sha256 (full) ${digest(material)}\n` +
        `  document sha256        ${file}\n  capturePath sha256     ${file.slice(0, 12)}\n` +
        `  superseded             ${previous} (document) / ${record?.currentSha256 ?? "—"} (record)\n` +
        moved.map((entry) => `  moved                  ${entry}\n`).join(""),
    );
  }
}

process.stdout.write(`\n${lines.join("")}`);
