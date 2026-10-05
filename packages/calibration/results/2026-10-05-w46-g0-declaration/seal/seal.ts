/**
 * W46 G0 (a): freeze a landed candidate as the two DARK `-glass0.25` profile documents — W45 G0's
 * seal (`results/2026-10-03-w45-g0-operator/seal/seal.ts`) ported for W46 (charter clauses 1, 5 and 8;
 * X60, X62, X64). W45's committed copy is untouched.
 *
 *   cd packages/calibration
 *   pnpm exec tsx results/2026-10-05-w46-g0-declaration/seal/seal.ts <label> <method.json> \
 *     [--candidates DIR] [--profiles DIR] [--manifest FILE]
 *
 * Defaults: the candidate is `<G1>/fit/candidates/<label>/` (G1 = `results/2026-10-05-w46-g1-refit`),
 * the documents are written into `packages/calibration/profiles/`, and the record is
 * `<G1>/seal/sealed-manifest.json`. G0's test points `--profiles` at a scratch COPY of the profiles
 * directory and `--manifest` beside it (`test_seal.py`).
 *
 * What W46 changes from W45's seal, each a refusal rather than a convention:
 * - **The dark pair is sealed; the light pair never moves (X60).** The candidate's light endpoints
 *   must be patch- and digest-identical to the light snapshots, and the light files are neither read
 *   as a start nor written.
 * - **Each dark file it replaces must be the snapshot's bytes** (X62: `d0219cd684bf…` active,
 *   `f0b36a71772a…` receded, the full SHA-256 the snapshots carry), so a seal never runs twice and
 *   never over a stranger's bytes; the snapshot's record (`entries`, the CSS mapping) is read from the
 *   snapshot itself, never the live file.
 * - **X64.** The leaf set is the dark 0.5 twin's (X44) plus, at most, the slot's X64 keys; any other
 *   extra leaf refuses. A key named at its inherited value moves neither the material nor its digest.
 * - **W46's bindings, never W44's or W45's**: a candidate, a profiles directory or a manifest inside
 *   their evidence or scratch refuses; the record names W46's charter and G1; the documents supersede
 *   the dark generation `d0219cd684bf`.
 *
 * Unchanged from W45's seal: the patch is the candidate's, leaf for leaf, and every leaf it moves
 * from the snapshot is one of the candidate's declared overrides (its own `spec.json`);
 * `resolvedMaterialSha256` under the current digest rule (the active over the unmoved
 * `DEFAULT_MATERIAL_PROFILE`, the receded over the SEALED dark active document) must equal the
 * candidate's own endpoint digest (an X64 key at the value its base resolves it to is recorded as
 * `materialised` and needs no method); `entries` keeps the snapshot's record for every leaf left where it
 * was and records each moved leaf with its snapshot and 0.5 values and its method (`<method.json>`,
 * keyed by leaf); every check passes for BOTH documents before either file is written.
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
const EVIDENCE = resolve(HERE, "..");
const PACKAGE = resolve(HERE, "../../..");
const REPO = resolve(PACKAGE, "../..");
const G1 = join(PACKAGE, "results", "2026-10-05-w46-g1-refit");
const DOCUMENTS = join(EVIDENCE, "documents");
const CHARTER = "docs/doperpowers/specs/2026-10-05-w46-dark-texture-at-0-25.md";
/** X64 (bindings.X64): the inherited leaves each dark document may name beside its twin's. */
const MAY_ADD: Readonly<Record<"active" | "receded", readonly string[]>> = {
  active: ["sizeScatterFloor2x", "sizeScatterRampStartThin1x", "sizeScatterRampStartThick1x",
    "sizeScatterRampStartFar1x", "sizeScatterRampStartThin2x", "sizeScatterRampStartThick2x",
    "sizeScatterRampStartFar2x", "sizeHeavySecondShareFar2x"],
  receded: ["sizeScatterRampStartFar1x", "sizeScatterFloor", "sizeScatterFloor2x", "sizeHeavyTapSigma",
    "sizeHeavySecondShare", "sizeHeavySecondShareFar2x", "sizeHeavySecondSigma", "sizeHeavySecondSigma2x",
    "sizeScatterScaleGain"],
};
/** The snapshots (X62, bindings.DOCUMENT_SHA): the dark files a seal replaces, the light ones it holds. */
const SNAPSHOT: Readonly<Record<string, string>> = {
  "active.dark": "d0219cd684bff75b2ba5c34d4f6cb2f6d49e32aab7cc27464220a05910f2638f",
  "receded.dark": "f0b36a71772a00a647c10a280ae73b92d21be1f0c65599334c4e3cdf36cb7f86",
  "active.light": "ebc3d9105a4a40565278845071113c6a5368b304910362786b8cbfb4cc66bb44",
  "receded.light": "12712d534b78017f68fee440cb9d9d451178aae1b80db36c0043fdfb1b591203",
};
const TWIN_05: Readonly<Record<string, string>> = {
  "apple-macos-27.0-1x-dark-standard-glass0.5": "0eac5b294cc2",
  "apple-macos-27.0-1x-dark-standard-glass0.5-receded": "5cec8c961201",
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
const snapshot = (slot: string): { text: string; doc: Record<string, Json> } => {
  const text = readFileSync(join(DOCUMENTS, `${SNAPSHOT[slot]!.slice(0, 12)}.json`), "utf8");
  if (sha256(text) !== SNAPSHOT[slot]) throw new Error(`${slot}: the snapshot does not hash to its name (X62)`);
  return { text, doc: JSON.parse(text) as Record<string, Json> };
};

/** Never W44's or W45's evidence, scratch or stage (clause 1). */
const ours = (path: string, what: string): string => {
  const full = resolve(path);
  if (/(^|\/)2026-10-03-w4[45]-[^/]*(\/|$)/.test(full) || /(^|\/)vitrea-w4[45](\/|$)/.test(full)) {
    throw new Error(`${what}: ${full} is W44's or W45's evidence or scratch; W46 seals its own (clause 1)`);
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
const CANDIDATES = ours(flag("candidates") ?? join(G1, "fit", "candidates"), "the candidates");
const PROFILES = ours(flag("profiles") ?? join(PACKAGE, "profiles"), "the profiles directory");
const MANIFEST = ours(flag("manifest") ?? join(G1, "seal", "sealed-manifest.json"), "the seal's record");
const METHOD = JSON.parse(readFileSync(resolve(methodPath), "utf8")) as Record<string, string[]>;
const FOLDER = ours(join(CANDIDATES, label), "the candidate");
const CANDIDATE = join(FOLDER, "candidate.json");
const candidate = readCandidateDocument(CANDIDATE);
const candidateSha = sha256(readFileSync(CANDIDATE));
const spec = JSON.parse(readFileSync(join(FOLDER, "spec.json"), "utf8")) as {
  overrides?: Record<string, Record<string, Json>>;
};

// The light endpoints: patch- and digest-identical to the light snapshots, files untouched (X60).
for (const pose of ["active", "receded"] as const) {
  const slot = `${pose}.light` as const;
  if (Object.keys(spec.overrides?.[slot] ?? {}).length > 0) {
    throw new Error(`${slot}: the candidate's spec moves the light material (X60)`);
  }
  const endpoint = JSON.parse(readFileSync(candidate.endpoints[slot].path, "utf8")) as Record<string, Json>;
  const { doc } = snapshot(slot);
  if (JSON.stringify(endpoint["patch"]) !== JSON.stringify(doc["patch"]) ||
      endpoint["resolvedMaterialSha256"] !== doc["resolvedMaterialSha256"]) {
    throw new Error(`${slot}: the candidate's light endpoint is not the light snapshot (X60)`);
  }
}

const manifest: Record<string, Json> = {};
const texts: Record<string, string> = {};
let sealedActive: unknown;
for (const pose of ["active", "receded"] as const) {
  const slot = `${pose}.dark` as const;
  const key = keyOf(pose, "dark", "0.25");
  const out = join(PROFILES, `${key}.json`);
  const liveSha = sha256(readFileSync(out));
  if (liveSha !== SNAPSHOT[slot]) {
    throw new Error(`${rel(out)} hashes to ${liveSha.slice(0, 12)}, not the snapshot ${SNAPSHOT[slot]!.slice(0, 12)}; `
      + "the seal runs once, over the published dark 0.25 document (X62)");
  }
  const { doc: before0 } = snapshot(slot);
  const endpointFile = candidate.endpoints[slot].path;
  const endpoint = JSON.parse(readFileSync(endpointFile, "utf8")) as Record<string, Json>;
  const twinPath = join(PROFILES, `${keyOf(pose, "dark", "0.5")}.json`);
  const twinText = readFileSync(twinPath, "utf8");
  if (!sha256(twinText).startsWith(TWIN_05[keyOf(pose, "dark", "0.5")]!)) {
    throw new Error(`${rel(twinPath)} is not its X41-frozen ${TWIN_05[keyOf(pose, "dark", "0.5")]}`);
  }
  const twin = JSON.parse(twinText) as Record<string, Json>;
  const patch = endpoint["patch"] as Record<string, Json>;

  const mine = leaves(patch);
  const theirs = leaves(twin["patch"]!);
  const before = leaves(before0["patch"]!);
  const extra = Object.keys(mine).filter((k) => !(k in theirs)).sort();
  const dropped = Object.keys(theirs).filter((k) => !(k in mine)).sort();
  if (dropped.length > 0 || extra.some((k) => !MAY_ADD[pose].includes(k))) {
    throw new Error(`${slot}: the leaf set is not the 0.5 twin's (plus X64's ${MAY_ADD[pose].join(", ")})`
      + `: extra ${extra.join(", ") || "none"}, dropped ${dropped.join(", ") || "none"} (X44, X64)`);
  }
  const movedFromSnapshot = Object.keys(mine).filter((k) => JSON.stringify(mine[k]) !== JSON.stringify(before[k])).sort();
  const declared = Object.keys(spec.overrides?.[slot] ?? {});
  const undeclared = movedFromSnapshot.filter((k) => !declared.includes(k));
  if (undeclared.length > 0) throw new Error(`${slot}: moves undeclared leaves ${undeclared.join(", ")} (clause 5)`);

  const base = pose === "active" ? DEFAULT_MATERIAL_PROFILE : sealedActive;
  if (base === undefined) throw new Error(`${slot}: the sealed dark active document is not built`);
  const resolvedMaterial = withMaterialOverrides(base as typeof DEFAULT_MATERIAL_PROFILE,
    patch as unknown as MaterialProfilePatch);
  if (pose === "active") sealedActive = resolvedMaterial;
  const digest = resolvedDigest(resolvedMaterial);
  if (digest !== endpoint["resolvedMaterialSha256"]) {
    throw new Error(`${slot}: resolves to ${digest}, and the candidate recorded ${String(endpoint["resolvedMaterialSha256"])}`);
  }

  const entries: Record<string, Json> = {};
  const beforeEntries = (before0["entries"] ?? {}) as Record<string, Json>;
  for (const [leaf, entry] of Object.entries(beforeEntries)) {
    if (leaf !== "held" && !movedFromSnapshot.includes(leaf)) entries[leaf] = entry;
  }
  // X64: a key the snapshot did not name, stated at the value the base already resolves it to, is
  // MATERIALISED rather than moved (digest-neutral); it is recorded as such and needs no method.
  const inheritedValue = (leaf: string): unknown => (base as Record<string, unknown>)[leaf];
  const materialised = movedFromSnapshot.filter((k) => !(k in before) && MAY_ADD[pose].includes(k)
    && JSON.stringify(inheritedValue(k)) === JSON.stringify(mine[k]));
  for (const leaf of materialised) {
    entries[leaf] = { status: "materialised", value: mine[leaf]!, inheritedFrom:
      pose === "active" ? "DEFAULT_MATERIAL_PROFILE" : `${keyOf("active", "dark", "0.25")}.json (resolved)` };
  }
  for (const leaf of movedFromSnapshot.filter((k) => !materialised.includes(k))) {
    if (METHOD[leaf] === undefined) throw new Error(`${slot}: no method recorded for ${leaf}`);
    entries[leaf] = {
      status: "measured", value: mine[leaf]!, previous: before[leaf] ?? null,
      previousAt05: theirs[leaf] ?? null, method: METHOD[leaf]!,
    };
  }
  entries["held"] = beforeEntries["held"] ?? { status: "held" };
  const activeFile = `${keyOf("active", "dark", "0.25")}.json`;
  const document: Record<string, Json> = {
    "$comment": [
      `The macOS 27 dark ${pose === "active" ? "standard" : "RECEDED"} material at the Glass`,
      "appearance slider's 0.25 position (`NSGlassTintAmount` 0.25, the clearer glass), as a " +
        (pose === "active" ? "PATCH over the unmoved runtime" : "difference over"),
      pose === "active"
        ? "default — W43 Decision Log 6; it is not a difference over the 0.5 document."
        : `${activeFile}, its own scheme's 0.25 active document (W43 Decision Log 7 item 8).`,
      "",
      "W46 G1, claims §5.209: the dark texture refit of d0219cd684bf (the transmission and the scatter,",
      "the tone ordinates held), fitted in two stages in scratch under the hashed part 2 on the dark",
      "WebGPU fit cells at both scales, T1 read against Apple's texture. The light 0.25 pair, the 0.5",
      "generations and the 26.5 rows did not move (X60). It supersedes the document named in",
      "`supersedes`; `entries` keeps the snapshot's record for every leaf W46 left where it was and",
      "records each leaf W46 moved with its previous and 0.5 values. By X64 it may name",
      `${listed(MAY_ADD[pose])} beside its 0.5 twin's leaves (X44 narrowed).`,
    ],
    profileKey: key,
    schemaVersion: (before0["schemaVersion"] as number | undefined) ?? 1,
    recordedAt: new Date().toISOString().slice(0, 10),
    recordedBy: "W46 G1",
    colorSpace: (before0["colorSpace"] as string | undefined) ?? "srgb",
    ...(pose === "active"
      ? { supersedesDefaultsOf: "@vitrea/renderer-webgpu DEFAULT_MATERIAL_PROFILE" }
      : { kind: (before0["kind"] as string | undefined) ?? "receded-endpoint",
          appliesOver: `packages/calibration/profiles/${activeFile}`,
          resolvedOverActiveDocument: activeFile }),
    glassTintAmount: 0.25,
    twin: { path: rel(twinPath), sha256: sha256(twinText) },
    derivedFromCandidate: {
      declaration: rel(CANDIDATE), declarationSha256: candidateSha,
      endpoint: rel(endpointFile), endpointSha256: candidate.endpoints[slot].sha256,
    },
    supersedes: { path: `packages/calibration/profiles/${key}.json`, sha256: liveSha,
      resolvedMaterialSha256: before0["resolvedMaterialSha256"]!,
      generation: "packages/calibration/results/generations/d0219cd684bf.json" },
    resolvedMaterialSha256: digest,
    resolvedMaterialSha256Rule: MATERIAL_DIGEST_RULE_VERSION,
    measurement: {
      gate: `W46 G1, claims §5.209; charter ${CHARTER} clauses 5-8; Decision Logs 1-7`,
      fixtures: "apps/reference-apple/fixtures/apple-macos-27.0-{1x,2x}-dark-standard-glass0.25, the W43 G1a bed " +
        "at seven runs per cell, slider 0.25 (§5.199); T1's bar from those runs (§5.202 §2)",
      fixtureSets: "the dark fit cells (the T1 gate cells less the canonical holdout and the W46 referee manifest, " +
        "with L1's calibration and validation population) fitted; no holdout or referee read to fit",
      webCell: "renderer webgpu, samplingBackend gpu-texture, adapter apple/metal-3, candidate mode (W43 G0 (f))",
      objective: "part 2's stage objectives (T1's selection metric over each stage's cells, both scales) under its " +
        "search procedure, tie rule and selection rule, from d0219cd684bf (results/2026-10-05-w46-g1-refit/fit/path/)",
      cuts: `results/2026-10-05-w46-g1-refit/fit/candidates/${label}/cuts.json.gz`,
    },
    entries,
    patch,
    ...(pose === "active" && before0["cssTierMapping"] !== undefined ? { cssTierMapping: before0["cssTierMapping"]! } : {}),
  };
  texts[out] = `${JSON.stringify(document, null, 2)}\n`;
  manifest[`${key}.json`] = {
    fileSha256: sha256(texts[out]!), resolvedMaterialSha256: digest,
    previousResolvedMaterialSha256: before0["resolvedMaterialSha256"]!,
    movedFromSnapshot, materialised, addedToTwinLeafSet: extra, supersedes: liveSha, twinSha256: sha256(twinText),
    candidateEndpointSha256: candidate.endpoints[slot].sha256,
  };
}

// Every check above passed for BOTH dark documents before either file is written.
for (const [out, text] of Object.entries(texts)) writeFileSync(out, text);
writeFileSync(MANIFEST, `${JSON.stringify({
  what: `W46 G1: candidate ${label} sealed as the two dark -glass0.25 documents; the light two untouched (X60)`,
  charter: CHARTER,
  candidate: { declaration: rel(CANDIDATE), sha256: candidateSha },
  profiles: rel(PROFILES),
  digestRule: MATERIAL_DIGEST_RULE_VERSION,
  documents: manifest,
  lightUnchanged: Object.fromEntries((["active", "receded"] as const).map((pose) => {
    const file = join(PROFILES, `${keyOf(pose, "light", "0.25")}.json`);
    return [`${keyOf(pose, "light", "0.25")}.json`, sha256(readFileSync(file))];
  })),
}, null, 2)}\n`);
console.log(JSON.stringify(manifest, null, 2));
