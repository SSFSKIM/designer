/**
 * W44 G1 step 3: freeze the landed candidate as the two LIGHT `-glass0.25` profile documents
 * (charter G1 step 3; clauses 5 and 8; X44 narrowed by Decision Log 7 item 1; X48).
 *
 *   cd packages/calibration && npx tsx results/2026-10-03-w44-g1-refit/seal/seal.ts <label> <method.json>
 *
 * W43 G3 (ii)'s seal (`results/2026-10-02-w43-g3-refit/seal/seal.ts`), carried to a refit of the
 * light pair over the published generation. It writes
 * `profiles/apple-macos-27.0-1x-light-standard-glass0.25{,-receded}.json` and nothing else:
 * - **The dark documents do not move by a byte.** The candidate's dark endpoints must be patch- and
 *   digest-identical to the shipped dark documents (part 2's candidateIdentity), and the files are
 *   not written (X48).
 * - **What it supersedes.** Each light file it replaces must be the published c05 document, at the
 *   file hash the c05 generation's index entry names (`6d18c059eb42…` active, `4d5f23d9d312…`
 *   receded); anything else refuses, so a seal never runs twice and never over a stranger's bytes.
 *   The superseded document stays in git and is named by its hash in the new one (`supersedes`).
 * - **One leaf space.** The active document names exactly its 0.5 twin's leaves (X44). The
 *   receded document names exactly its 0.5 twin's leaves and, by Decision Log 7 item 1, MAY name
 *   `sizeHeavySecondShare` beside them as a difference over its active document; any other
 *   difference refuses.
 * - **The patch is the candidate's**, leaf for leaf, and every leaf it moves from c05 is one of the
 *   candidate's declared overrides (its `spec.json`).
 * - **Digests.** `resolvedMaterialSha256` under the current digest rule: the active document over the
 *   unmoved `DEFAULT_MATERIAL_PROFILE`, the receded one over the SEALED light active document; each
 *   must equal the candidate's own endpoint digest, or the seal refuses.
 * - **The record.** `twin` (the 0.5 counterpart by path and SHA-256), `derivedFromCandidate` (the
 *   W44 declaration and endpoint by SHA-256), `supersedes` (the c05 document by path and SHA-256),
 *   `glassTintAmount` 0.25, and `entries`: W43's entries for the leaves W44 left where c05 put them,
 *   unchanged, and for each leaf W44 moved its value, its c05 value as `previous`, its 0.5 value as
 *   `previousAt05` and the method (`<method.json>`, keyed by leaf), plus W43's `held` families.
 *   The CSS mapping is c05's, unchanged.
 *
 * Writes `seal/sealed-manifest.json` beside this script.
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
const PROFILES = join(PACKAGE, "profiles");
const RECEDED_MAY_ADD = ["sizeHeavySecondShare"];
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
const keyOf = (pose: "active" | "receded", scheme: "light" | "dark", glass: "0.5" | "0.25"): string =>
  `apple-macos-27.0-1x-${scheme}-standard-glass${glass}${pose === "receded" ? "-receded" : ""}`;

const [label, methodPath] = process.argv.slice(2);
if (label === undefined || methodPath === undefined) throw new Error("usage: seal.ts <label> <method.json>");
const METHOD = JSON.parse(readFileSync(resolve(methodPath), "utf8")) as Record<string, string[]>;
const FOLDER = join(HERE, "..", "fit", "candidates", label);
const CANDIDATE = join(FOLDER, "candidate.json");
const candidate = readCandidateDocument(CANDIDATE);
const candidateSha = sha256(readFileSync(CANDIDATE));
const spec = JSON.parse(readFileSync(join(HERE, "..", "fit", "specs", `${label}.json`), "utf8")) as {
  overrides: Record<string, Record<string, Json>>;
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
  const allowed = pose === "receded" ? RECEDED_MAY_ADD : [];
  if (dropped.length > 0 || extra.some((k) => !allowed.includes(k))) {
    throw new Error(`${slot}: the leaf set is not the 0.5 twin's${pose === "receded" ? " (plus the receded share)" : ""}`
      + `: extra ${extra.join(", ") || "none"}, dropped ${dropped.join(", ") || "none"} (X44)`);
  }
  const movedFromC05 = Object.keys(mine).filter((k) => JSON.stringify(mine[k]) !== JSON.stringify(before[k])).sort();
  const declared = Object.keys(spec.overrides[slot] ?? {});
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
      "W44 G1, claims §5.203: the refit of W43's c05 at 2x (the texture at 0.25), fitted move by move",
      "in scratch under the hashed fit declaration (G0 part 2, amended once by Decision Log 7) on the",
      "2x light WebGPU fit cells, T1 read against Apple's texture with its bar from the seven-run",
      "archive. Only 2x-anchored scatter leaves and the second heavy tap at an inert 1x width moved,",
      "so the 1x light rows are W43's byte for byte (X48). It supersedes the c05 document named in",
      "`supersedes`; `entries` keeps W43's record for every leaf W44 left where c05 put it and records",
      "each leaf W44 moved with its c05 and 0.5 values." +
        (pose === "receded" ? " By Decision Log 7 item 1 it may name sizeHeavySecondShare beside" : ""),
      ...(pose === "receded" ? ["its 0.5 twin's leaves (X44 narrowed by that one difference)."] : []),
    ],
    profileKey: key,
    schemaVersion: (c05["schemaVersion"] as number | undefined) ?? 1,
    recordedAt: "2026-10-03",
    recordedBy: "W44 G1",
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
    supersedes: { path: rel(out), sha256: c05Sha, resolvedMaterialSha256: c05["resolvedMaterialSha256"]!,
      generation: "packages/calibration/results/generations/6d18c059eb42.json" },
    resolvedMaterialSha256: digest,
    resolvedMaterialSha256Rule: MATERIAL_DIGEST_RULE_VERSION,
    measurement: {
      gate: "W44 G1, claims §5.203; charter 2026-10-03-w44-texture-at-0-25.md clauses 5-8; Decision Logs 4, 5 and 7",
      fixtures: "apps/reference-apple/fixtures/apple-macos-27.0-{1x,2x}-light-standard-glass0.25, the W43 G1a bed " +
        "at seven runs per cell, slider 0.25 (§5.199); T1's bar from those runs (§5.202 §2)",
      fixtureSets: "the fit cells (2x light T1 cells less the canonical holdout and the referee manifest) fitted; " +
        "no holdout or referee read to fit",
      webCell: "chromium 151.0.7922.34, renderer webgpu, samplingBackend gpu-texture, adapter apple/metal-3, " +
        "candidate mode (W43 G0 (f))",
      objective: "part 2's move objectives (T1's selection metric over each move's cells) under its search " +
        "procedure and selection rule (results/2026-10-03-w44-g1-refit/fit/path/)",
      cuts: `results/2026-10-03-w44-g1-refit/fit/candidates/${label}/cuts.json.gz`,
      reproduce: `python3.12 -B packages/calibration/results/2026-10-03-w44-g1-refit/fit/search.py full ${label}`,
    },
    entries,
    patch,
    ...(pose === "active" && c05["cssTierMapping"] !== undefined ? { cssTierMapping: c05["cssTierMapping"]! } : {}),
  };
  const text = `${JSON.stringify(document, null, 2)}\n`;
  writeFileSync(out, text);
  manifest[`${key}.json`] = {
    fileSha256: sha256(text), resolvedMaterialSha256: digest, movedFromC05: movedFromC05,
    addedToTwinLeafSet: extra, supersedes: c05Sha, twinSha256: sha256(twinText),
    candidateEndpointSha256: candidate.endpoints[slot].sha256,
  };
}

writeFileSync(join(HERE, "sealed-manifest.json"), `${JSON.stringify({
  what: `W44 G1 step 3: candidate ${label} sealed as the two light -glass0.25 documents; the dark two untouched`,
  candidate: { declaration: rel(CANDIDATE), sha256: candidateSha },
  digestRule: MATERIAL_DIGEST_RULE_VERSION,
  documents: manifest,
  darkUnchanged: Object.fromEntries((["active", "receded"] as const).map((pose) => {
    const file = join(PROFILES, `${keyOf(pose, "dark", "0.25")}.json`);
    return [`${keyOf(pose, "dark", "0.25")}.json`, sha256(readFileSync(file))];
  })),
}, null, 2)}\n`);
console.log(JSON.stringify(manifest, null, 2));
