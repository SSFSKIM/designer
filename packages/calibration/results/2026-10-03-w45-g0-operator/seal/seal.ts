/**
 * W45 G0 (b): freeze a landed candidate as the two LIGHT `-glass0.25` profile documents — W44 G1's
 * prepared, never-run seal (`results/2026-10-03-w44-g1-refit/seal/seal.ts`) ported for W45 (charter
 * clauses 2, 5 and 8; Decision Log 2; X44 as narrowed; X48; X58). W44's committed copy is untouched.
 *
 *   cd packages/calibration
 *   pnpm exec tsx results/2026-10-03-w45-g0-operator/seal/seal.ts <label> <method.json> \
 *     [--candidates DIR] [--profiles DIR] [--manifest FILE]
 *
 * Defaults: the candidate is `<G1>/fit/candidates/<label>/` (G1 = `results/2026-10-03-w45-g1-refit`),
 * the documents are written into `packages/calibration/profiles/`, and the record is
 * `<G1>/seal/sealed-manifest.json`. G0's rehearsal points `--profiles` at a scratch COPY of the
 * profiles directory and `--manifest` beside it, so the seal of c05's own bytes runs end to end
 * without touching a shipped document (`test_seal.py`).
 *
 * What W45 changes from W44's seal, each a refusal rather than a convention:
 * - **The operator's key** (Decision Log 2; X44 narrowed). The active light document names exactly
 *   its 0.5 twin's leaves and MAY add `sizeHeavySecondShareFar2x`; the receded light document names
 *   exactly its 0.5 twin's leaves and MAY add the second tap's keys `sizeHeavySecondShare`,
 *   `sizeHeavySecondSigma` and `sizeHeavySecondSigma2x` (W44 Decision Log 7 item 1, kept) and
 *   `sizeHeavySecondShareFar2x`, each as a difference over its active document — exactly what W45's
 *   builder admits (part 2's second amendment, the charter's Decision Log 7 item 6: the port had
 *   admitted the receded share and the operator's key and not W44's receded widths). Any other extra
 *   leaf, in either document, refuses.
 * - **W45's bindings, never W44's** (X58): a candidate, a profiles directory or a manifest inside a W44
 *   evidence directory or W44's scratch refuses; the spec read is the candidate folder's own
 *   `spec.json` (what W45's builder wrote); the record names W45's charter and G1.
 *
 * Unchanged from W44's seal: the dark documents do not move by a byte (the candidate's dark endpoints
 * patch- and digest-identical to the shipped dark documents; their files are not written); each light
 * file it replaces must be the published c05 document at the file hash the c05 generation's index
 * names (`6d18c059eb42…` active, `4d5f23d9d312…` receded), so a seal never runs twice and never over
 * a stranger's bytes; the patch is the candidate's, leaf for leaf, and every leaf it moves from c05 is
 * one of the candidate's declared overrides; `resolvedMaterialSha256` under the current digest rule
 * (the active over the unmoved `DEFAULT_MATERIAL_PROFILE`, the receded over the SEALED light active
 * document) must equal the candidate's own endpoint digest; `entries` keeps c05's record for every
 * leaf W45 left where c05 put it and records each moved leaf with its c05 and 0.5 values and its
 * method (`<method.json>`, keyed by leaf); the CSS mapping is c05's, unchanged.
 */

import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  DEFAULT_MATERIAL_PROFILE,
  MATERIAL_DIGEST_RULE_VERSION,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

import { readCandidateDocument, resolvedDigest } from "../../../scripts/candidate-document";

const HERE = resolve(fileURLToPath(new URL(".", import.meta.url)));
const PACKAGE = resolve(HERE, "../../..");
const REPO = resolve(PACKAGE, "../..");
const G1 = join(PACKAGE, "results", "2026-10-03-w45-g1-refit");
const CHARTER = "docs/doperpowers/specs/2026-10-03-w45-span-selective-texture.md";
const OPERATOR_KEY = "sizeHeavySecondShareFar2x";
const MAY_ADD: Readonly<Record<"active" | "receded", readonly string[]>> = {
  active: [OPERATOR_KEY],
  receded: ["sizeHeavySecondShare", "sizeHeavySecondSigma", "sizeHeavySecondSigma2x", OPERATOR_KEY],
};
const C05_FILE_SHA: Readonly<Record<string, string>> = {
  "apple-macos-27.0-1x-light-standard-glass0.25": "6d18c059eb42",
  "apple-macos-27.0-1x-light-standard-glass0.25-receded": "4d5f23d9d312",
};

type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
const sha256 = (bytes: string | Buffer): string => createHash("sha256").update(bytes).digest("hex");
const rel = (path: string): string => relative(REPO, path);
const leaves = (patch: Json, prefix = ""): Record<string, Json> =>
  Object.fromEntries(Object.entries(patch as Record<string, Json>).flatMap(([key, value]) =>
    value !== null && typeof value === "object" && !Array.isArray(value)
      ? Object.entries(leaves(value, `${prefix}${key}.`))
      : [[`${prefix}${key}`, value]]));
const listed = (keys: readonly string[]): string =>
  keys.length < 2 ? keys.join("") : `${keys.slice(0, -1).join(", ")} and ${keys[keys.length - 1]!}`;
const keyOf = (pose: "active" | "receded", scheme: "light" | "dark", glass: "0.5" | "0.25"): string =>
  `apple-macos-27.0-1x-${scheme}-standard-glass${glass}${pose === "receded" ? "-receded" : ""}`;

/** X58: never W44's evidence, scratch or stage. */
const notW44 = (path: string, what: string): string => {
  const full = resolve(path);
  if (/(^|\/)2026-10-03-w44-[^/]*(\/|$)/.test(full) || /(^|\/)vitrea-w44(\/|$)/.test(full)) {
    throw new Error(`${what}: ${full} is W44's evidence or scratch; W45 seals its own (X58)`);
  }
  return full;
};

const argv = process.argv.slice(2);
const flag = (name: string): string | undefined => {
  const at = argv.indexOf(`--${name}`);
  return at < 0 ? undefined : argv[at + 1];
};
const positional = argv.filter((a, i) => !a.startsWith("--") && !(i > 0 && argv[i - 1]!.startsWith("--")));
const [label, methodPath] = positional;
if (label === undefined || methodPath === undefined) {
  throw new Error("usage: seal.ts <label> <method.json> [--candidates DIR] [--profiles DIR] [--manifest FILE]");
}
const CANDIDATES = notW44(flag("candidates") ?? join(G1, "fit", "candidates"), "the candidates");
const PROFILES = notW44(flag("profiles") ?? join(PACKAGE, "profiles"), "the profiles directory");
const MANIFEST = notW44(flag("manifest") ?? join(G1, "seal", "sealed-manifest.json"), "the seal's record");
const METHOD = JSON.parse(readFileSync(resolve(methodPath), "utf8")) as Record<string, string[]>;
const FOLDER = notW44(join(CANDIDATES, label), "the candidate");
const CANDIDATE = join(FOLDER, "candidate.json");
const candidate = readCandidateDocument(CANDIDATE);
const candidateSha = sha256(readFileSync(CANDIDATE));
const spec = JSON.parse(readFileSync(join(FOLDER, "spec.json"), "utf8")) as {
  overrides?: Record<string, Record<string, Json>>;
};

// The dark endpoints: patch- and digest-identical to the shipped dark documents, files untouched.
for (const pose of ["active", "receded"] as const) {
  const slot = `${pose}.dark` as const;
  const endpoint = JSON.parse(readFileSync(candidate.endpoints[slot].path, "utf8")) as Record<string, Json>;
  const shipped = JSON.parse(readFileSync(join(PROFILES, `${keyOf(pose, "dark", "0.25")}.json`), "utf8")) as
    Record<string, Json>;
  if (JSON.stringify(endpoint["patch"]) !== JSON.stringify(shipped["patch"]) ||
      endpoint["resolvedMaterialSha256"] !== shipped["resolvedMaterialSha256"]) {
    throw new Error(`${slot}: the candidate's dark endpoint is not the shipped dark document (X48)`);
  }
}

const manifest: Record<string, Json> = {};
const texts: Record<string, string> = {};
let sealedActive: unknown;
for (const pose of ["active", "receded"] as const) {
  const slot = `${pose}.light` as const;
  const key = keyOf(pose, "light", "0.25");
  const out = join(PROFILES, `${key}.json`);
  const c05Text = readFileSync(out, "utf8");
  const c05Sha = sha256(c05Text);
  if (!c05Sha.startsWith(C05_FILE_SHA[key]!)) {
    throw new Error(`${rel(out)} hashes to ${c05Sha.slice(0, 12)}, not the published c05 document `
      + `${C05_FILE_SHA[key]}; the seal runs once, over c05`);
  }
  const c05 = JSON.parse(c05Text) as Record<string, Json>;
  const endpointFile = candidate.endpoints[slot].path;
  const endpoint = JSON.parse(readFileSync(endpointFile, "utf8")) as Record<string, Json>;
  const twinPath = join(PROFILES, `${keyOf(pose, "light", "0.5")}.json`);
  const twinText = readFileSync(twinPath, "utf8");
  const twin = JSON.parse(twinText) as Record<string, Json>;
  const patch = endpoint["patch"] as Record<string, Json>;

  const mine = leaves(patch);
  const theirs = leaves(twin["patch"]!);
  const before = leaves(c05["patch"]!);
  const extra = Object.keys(mine).filter((k) => !(k in theirs)).sort();
  const dropped = Object.keys(theirs).filter((k) => !(k in mine)).sort();
  if (dropped.length > 0 || extra.some((k) => !MAY_ADD[pose].includes(k))) {
    throw new Error(`${slot}: the leaf set is not the 0.5 twin's (plus ${MAY_ADD[pose].join(", ")})`
      + `: extra ${extra.join(", ") || "none"}, dropped ${dropped.join(", ") || "none"} (X44)`);
  }
  const movedFromC05 = Object.keys(mine).filter((k) => JSON.stringify(mine[k]) !== JSON.stringify(before[k])).sort();
  const declared = Object.keys(spec.overrides?.[slot] ?? {});
  const undeclared = movedFromC05.filter((k) => !declared.includes(k));
  if (undeclared.length > 0) throw new Error(`${slot}: moves undeclared leaves ${undeclared.join(", ")} (clause 5)`);

  const base = pose === "active" ? DEFAULT_MATERIAL_PROFILE : sealedActive;
  if (base === undefined) throw new Error(`${slot}: the sealed light active document is not built`);
  const resolvedMaterial = withMaterialOverrides(base as typeof DEFAULT_MATERIAL_PROFILE,
    patch as unknown as MaterialProfilePatch);
  if (pose === "active") sealedActive = resolvedMaterial;
  const digest = resolvedDigest(resolvedMaterial);
  if (digest !== endpoint["resolvedMaterialSha256"]) {
    throw new Error(`${slot}: resolves to ${digest}, and the candidate recorded ${String(endpoint["resolvedMaterialSha256"])}`);
  }

  const entries: Record<string, Json> = {};
  const c05Entries = (c05["entries"] ?? {}) as Record<string, Json>;
  for (const [leaf, entry] of Object.entries(c05Entries)) {
    if (leaf !== "held" && !movedFromC05.includes(leaf)) entries[leaf] = entry;
  }
  for (const leaf of movedFromC05) {
    if (METHOD[leaf] === undefined) throw new Error(`${slot}: no method recorded for ${leaf}`);
    entries[leaf] = {
      status: "measured", value: mine[leaf]!, previous: before[leaf] ?? null,
      previousAt05: theirs[leaf] ?? null, method: METHOD[leaf]!,
    };
  }
  entries["held"] = c05Entries["held"] ?? { status: "held" };
  const activeFile = `${keyOf("active", "light", "0.25")}.json`;
  const document: Record<string, Json> = {
    "$comment": [
      `The macOS 27 light ${pose === "active" ? "standard" : "RECEDED"} material at the Glass`,
      "appearance slider's 0.25 position (`NSGlassTintAmount` 0.25, the clearer glass), as a " +
        (pose === "active" ? "PATCH over the unmoved runtime" : "difference over"),
      pose === "active"
        ? "default — W43 Decision Log 6; it is not a difference over the 0.5 document."
        : `${activeFile}, its own scheme's 0.25 active document (W43 Decision Log 7 item 8).`,
      "",
      "W45 G1, claims §5.206: the refit of W43's c05 at 2x through the span-graded tap (the second",
      "heavy tap's share graded on the scatter's far curve, sizeHeavySecondShareFar2x), fitted in two",
      "stages from two starting points in scratch under the hashed part 2, on the 2x light WebGPU fit",
      "cells, T1 read against Apple's texture with its bar from the seven-run archive. Only",
      "2x-anchored leaves moved, so the 1x light rows are W43's byte for byte (X48). It supersedes the",
      "c05 document named in `supersedes`; `entries` keeps W43's record for every leaf W45 left where",
      "c05 put it and records each leaf W45 moved with its c05 and 0.5 values. By Decision Log 2 it",
      `may name ${listed(MAY_ADD[pose])} beside its 0.5 twin's leaves (X44 narrowed).`,
    ],
    profileKey: key,
    schemaVersion: (c05["schemaVersion"] as number | undefined) ?? 1,
    recordedAt: new Date().toISOString().slice(0, 10),
    recordedBy: "W45 G1",
    colorSpace: (c05["colorSpace"] as string | undefined) ?? "srgb",
    ...(pose === "active"
      ? { supersedesDefaultsOf: "@vitrea/renderer-webgpu DEFAULT_MATERIAL_PROFILE" }
      : { kind: (c05["kind"] as string | undefined) ?? "receded-endpoint",
          appliesOver: `packages/calibration/profiles/${activeFile}`,
          resolvedOverActiveDocument: activeFile }),
    glassTintAmount: 0.25,
    twin: { path: rel(twinPath), sha256: sha256(twinText) },
    derivedFromCandidate: {
      declaration: rel(CANDIDATE), declarationSha256: candidateSha,
      endpoint: rel(endpointFile), endpointSha256: candidate.endpoints[slot].sha256,
    },
    supersedes: { path: `packages/calibration/profiles/${key}.json`, sha256: c05Sha,
      resolvedMaterialSha256: c05["resolvedMaterialSha256"]!,
      generation: "packages/calibration/results/generations/6d18c059eb42.json" },
    resolvedMaterialSha256: digest,
    resolvedMaterialSha256Rule: MATERIAL_DIGEST_RULE_VERSION,
    measurement: {
      gate: `W45 G1, claims §5.206; charter ${CHARTER} clauses 5-8; Decision Logs 1-4`,
      fixtures: "apps/reference-apple/fixtures/apple-macos-27.0-{1x,2x}-light-standard-glass0.25, the W43 G1a bed " +
        "at seven runs per cell, slider 0.25 (§5.199); T1's bar from those runs (§5.202 §2)",
      fixtureSets: "the fit cells (2x light T1 cells less the canonical holdout and the referee manifest) fitted; " +
        "no holdout or referee read to fit",
      webCell: "renderer webgpu, samplingBackend gpu-texture, adapter apple/metal-3, candidate mode (W43 G0 (f))",
      objective: "part 2's stage objectives (T1's selection metric over each stage's cells) under its search " +
        "procedure and selection rule, from c05 and W44's joint point (results/2026-10-03-w45-g1-refit/fit/path/)",
      cuts: `results/2026-10-03-w45-g1-refit/fit/candidates/${label}/cuts.json.gz`,
    },
    entries,
    patch,
    ...(pose === "active" && c05["cssTierMapping"] !== undefined ? { cssTierMapping: c05["cssTierMapping"]! } : {}),
  };
  texts[out] = `${JSON.stringify(document, null, 2)}\n`;
  manifest[`${key}.json`] = {
    fileSha256: sha256(texts[out]!), resolvedMaterialSha256: digest, c05ResolvedMaterialSha256: c05["resolvedMaterialSha256"]!,
    movedFromC05, addedToTwinLeafSet: extra, supersedes: c05Sha, twinSha256: sha256(twinText),
    candidateEndpointSha256: candidate.endpoints[slot].sha256,
  };
}

// Every check above passed for BOTH light documents before either file is written.
for (const [out, text] of Object.entries(texts)) writeFileSync(out, text);
writeFileSync(MANIFEST, `${JSON.stringify({
  what: `W45 G1 step 3: candidate ${label} sealed as the two light -glass0.25 documents; the dark two untouched`,
  charter: CHARTER,
  candidate: { declaration: rel(CANDIDATE), sha256: candidateSha },
  profiles: rel(PROFILES),
  digestRule: MATERIAL_DIGEST_RULE_VERSION,
  documents: manifest,
  darkUnchanged: Object.fromEntries((["active", "receded"] as const).map((pose) => {
    const file = join(PROFILES, `${keyOf(pose, "dark", "0.25")}.json`);
    return [`${keyOf(pose, "dark", "0.25")}.json`, sha256(readFileSync(file))];
  })),
}, null, 2)}\n`);
console.log(JSON.stringify(manifest, null, 2));
