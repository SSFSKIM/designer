/**
 * W43 G3 (ii): freeze candidate c05 as the four `-glass0.25` profile documents (charter clause 10
 * step 4; Decision Logs 5 and 7 as RULED 2026-10-02, (e) exercised: "All named misses; proceed to
 * G3 (ii)").
 *
 *   cd packages/calibration && npx tsx results/2026-10-02-w43-g3-refit/seal/seal.ts
 *
 * Writes `profiles/apple-macos-27.0-1x-{light,dark}-standard-glass0.25{,-receded}.json` under the
 * repository's document conventions, the 0.5 documents' own (`profiles/README.md`):
 * - each `patch` is c05's endpoint patch BYTE FOR BYTE as values, and names exactly its 0.5 twin's
 *   leaves (X44), refused otherwise;
 * - `resolvedMaterialSha256` is taken over the resolved material under the current digest rule
 *   (rule 2, `MATERIAL_DIGEST_RULE_VERSION`, which drops the identity table's entries at their
 *   identities): an active document over the unmoved `DEFAULT_MATERIAL_PROFILE`, a receded one
 *   over its own scheme's SEALED active document. Each must equal the digest c05 recorded, or the
 *   seal refuses;
 * - `derivedFromCandidate` names `fit/candidates/c05/candidate.json` by its SHA-256 and the endpoint
 *   file the patch came from, so a sealed document says which scratch read it is the freeze of;
 * - `twin` names its 0.5 counterpart by path and SHA-256, and `entries` records every moved leaf
 *   with its 0.5 value as `previous` and every held family with the ruling that held it;
 * - the CSS mapping is the 0.5 light document's, unchanged (the dark document names its one key).
 *
 * A file that already exists refuses: a sealed document's bytes never move. Writes
 * `seal/sealed-manifest.json` beside this script.
 */

import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
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
const CANDIDATE = join(HERE, "..", "fit", "candidates", "c05", "candidate.json");

type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
type Slot = "active.light" | "active.dark" | "receded.light" | "receded.dark";
const SLOTS: readonly Slot[] = ["active.light", "active.dark", "receded.light", "receded.dark"];

const sha256 = (bytes: string | Buffer): string => createHash("sha256").update(bytes).digest("hex");
const rel = (path: string): string => relative(REPO, path);

const leaves = (patch: Json, prefix = ""): Record<string, Json> =>
  Object.fromEntries(Object.entries(patch as Record<string, Json>).flatMap(([key, value]) =>
    value !== null && typeof value === "object" && !Array.isArray(value)
      ? Object.entries(leaves(value, `${prefix}${key}.`))
      : [[`${prefix}${key}`, value]]));

const keyOf = (slot: Slot, glass: "0.5" | "0.25"): string => {
  const [pose, scheme] = slot.split(".") as ["active" | "receded", "light" | "dark"];
  return `apple-macos-27.0-1x-${scheme}-standard-glass${glass}${pose === "receded" ? "-receded" : ""}`;
};

/** What held each family, so a reader of the document never has to reopen the charter. */
const HELD: Readonly<Record<string, string>> = {
  rimAndHighlight: "every rim and highlight leaf holds its 0.5 value (Decision Log 7 item 6)",
  outerShadow: "every outerShadow leaf holds, the receded zeros included (item 7); C1 reads identically to the pre-fit render on every cell",
  lens: "every lens leaf holds (the geometry did not move, §5.200 §4)",
  bodyChromaRetention: "held (item 4): M1 passes on the candidate, so the retention does not move",
  tintShade: "held (item 5): no tint cell misses a gate; the light receded tint reads +0.023 OKLab L light on average, a named gap",
  darkScatter: "held at the 0.5 values (item 2): the dark probes c01d / c01g and c02's step found no net gain on the calibration set",
  accessibility: "the accessibility leaves carry the 0.5 values, unmeasured at 0.25 (Decision Log 2 (b))",
};

const METHOD: Readonly<Record<string, string[]>> = {
  backdropToneResponseThin: [
    "The light thin row, solved on the calibration set under L1's clauses (|err| <= 0.055 and",
    "growth <= 0.005 against the pre-fit render, 0.003 margin) over a MEASURED Jacobian: one +0.02",
    "probe per ordinate (fit/specs/j-*.json, fit/solve_tone.py). The impulse anchor is not identified",
    "on calibration and carries Apple's own 0.25-0.5 change at that knot (G2's delta).",
  ],
  backdropToneResponseThick: [
    "Light: solved with the thin row (above). Dark: least squares on the dark calibration thick",
    "cells, its knot-2 step bounded by L1's growth clause on the dark checkerboard rrect-md cells",
    "(Decision Log 7 item 3: only the thick row moves in dark).",
  ],
  backdropToneBlackThin: [
    "Not identified on the calibration set (its untinted impulse cells are validation cells):",
    "Apple's own measured change at the impulse knot (light active -0.0527, receded -0.0542), thin",
    "equal to thick as W36 declared them. Validation reads the light impulse within L1.",
  ],
  backdropToneBlackThick: ["Equal to backdropToneBlackThin, as W36 declared them."],
  "optics.regular.tintAlpha": [
    "The structure step (Decision Log 7 items 1-2): 0.46 -> 0.30 raises the body's transmission of",
    "the backdrop's structure x1.2-1.3 and moves the level by under 0.001 (the tone solve holds it).",
    "The comparison twin without it (c05t) reads worse on every gated row.",
  ],
  sizeScatterFloor2x: [
    "The deep heavy share at 2x, 1.0 -> 0.6 (item 2): Apple's 0.25 body keeps more of the narrow",
    "detail (memo F: the Normal weight w halves). The 1x floor stays at 0.25: 0.15 added E2 failures.",
  ],
  sizeScatterFloor: [
    "The light receded deep share at 1x, 0.7 -> 1.0, against the receded checkerboards the active",
    "transmission step would otherwise over-structure further (the receded document names no",
    "transmission leaf of its own, X44).",
  ],
};

const candidate = readCandidateDocument(CANDIDATE);
const candidateSha = sha256(readFileSync(CANDIDATE));
const manifest: Record<string, Json> = {};
const sealedActive: Record<string, unknown> = {};

for (const slot of SLOTS) {
  const [pose, scheme] = slot.split(".") as ["active" | "receded", "light" | "dark"];
  const endpointFile = candidate.endpoints[slot].path;
  const endpoint = JSON.parse(readFileSync(endpointFile, "utf8")) as Record<string, Json>;
  const twinPath = join(PROFILES, `${keyOf(slot, "0.5")}.json`);
  const twinText = readFileSync(twinPath, "utf8");
  const twin = JSON.parse(twinText) as Record<string, Json>;
  const patch = endpoint["patch"] as Record<string, Json>;

  const mine = leaves(patch);
  const theirs = leaves(twin["patch"]!);
  const a = Object.keys(mine).sort().join("\n");
  const b = Object.keys(theirs).sort().join("\n");
  if (a !== b) throw new Error(`${slot}: the leaf set differs from ${rel(twinPath)} (X44)`);
  const moved = Object.keys(mine).filter((k) => JSON.stringify(mine[k]) !== JSON.stringify(theirs[k])).sort();

  const base = pose === "active" ? DEFAULT_MATERIAL_PROFILE : sealedActive[scheme];
  if (base === undefined) throw new Error(`${slot}: its scheme's sealed active document is not built`);
  const resolvedMaterial = withMaterialOverrides(base as typeof DEFAULT_MATERIAL_PROFILE,
    patch as unknown as MaterialProfilePatch);
  if (pose === "active") sealedActive[scheme] = resolvedMaterial;
  const digest = resolvedDigest(resolvedMaterial);
  if (digest !== endpoint["resolvedMaterialSha256"]) {
    throw new Error(`${slot}: resolves to ${digest}, and c05 recorded ${String(endpoint["resolvedMaterialSha256"])}`);
  }

  const key = keyOf(slot, "0.25");
  const activeFile = `${keyOf(`active.${scheme}` as Slot, "0.25")}.json`;
  const entries: Record<string, Json> = {};
  for (const leaf of moved) {
    entries[leaf] = { status: "measured", value: mine[leaf]!, previous: theirs[leaf]!,
      method: METHOD[leaf] ?? ["Fitted in W43 G3 (i); see results/2026-10-02-w43-g3-refit/."] };
  }
  entries["held"] = { status: "held", families: HELD as unknown as Json };
  const document: Record<string, Json> = {
    "$comment": [
      `The macOS 27 ${scheme} ${pose === "active" ? "standard" : "RECEDED"} material at the Glass`,
      "appearance slider's 0.25 position (`NSGlassTintAmount` 0.25, the clearer glass), as a " +
        (pose === "active" ? "PATCH over the unmoved runtime" : "difference over"),
      pose === "active"
        ? "default — W43 Decision Log 6; it is not a difference over the 0.5 document."
        : `${activeFile}, its own scheme's 0.25 active document (Decision Log 7 item 8).`,
      "",
      "W43 G3 (ii), claims §5.201: the freeze of G3 (i)'s scratch candidate c05, fitted on the",
      "WebGPU tier on the calibration rows of the W43 G1a bed (seven runs, plurality-published,",
      "side bundle), transferred to validation, the CSS tier derived from the same document. It names",
      "exactly the leaves of its 0.5 twin (X44); `entries` records every leaf that moved, with its 0.5",
      "value, and every family that held, with the ruling that held it. The holdout was not read to",
      "fit it. Every non-holdout miss it reads was ruled a named miss by the user on 2026-10-02",
      "(Decision Log 5 (e); results/2026-10-02-w43-g3-refit/read/misses.md).",
    ],
    profileKey: key,
    schemaVersion: (twin["schemaVersion"] as number | undefined) ?? 1,
    recordedAt: "2026-10-02",
    recordedBy: "W43 G3 (ii)",
    colorSpace: (twin["colorSpace"] as string | undefined) ?? "srgb",
    ...(pose === "active"
      ? { supersedesDefaultsOf: "@vitrea/renderer-webgpu DEFAULT_MATERIAL_PROFILE" }
      : { kind: (twin["kind"] as string | undefined) ?? "receded-endpoint",
          appliesOver: `packages/calibration/profiles/${activeFile}`,
          resolvedOverActiveDocument: activeFile }),
    glassTintAmount: 0.25,
    twin: { path: rel(twinPath), sha256: sha256(twinText) },
    derivedFromCandidate: {
      declaration: rel(CANDIDATE), declarationSha256: candidateSha,
      endpoint: rel(endpointFile), endpointSha256: candidate.endpoints[slot].sha256,
    },
    resolvedMaterialSha256: digest,
    resolvedMaterialSha256Rule: MATERIAL_DIGEST_RULE_VERSION,
    measurement: {
      gate: "W43 G3 (i)-(ii), claims §5.201; charter clause 10; Decision Logs 5 and 7 as RULED 2026-10-02",
      fixtures: `apps/reference-apple/fixtures/apple-macos-27.0-{1x,2x}-${scheme}-standard-glass0.25, ` +
        "the W43 G1a bed at seven runs per cell, slider 0.25 (§5.199)",
      fixtureSets: "calibration fitted; validation checked and never fitted; holdout not read to fit",
      webCell: "chromium 151.0.7922.34, renderer webgpu, samplingBackend gpu-texture, adapter apple/metal-3, " +
        "candidate mode (W43 G0 (f))",
      objective: "L1's own clauses as constraints over the light calibration cells (solve_tone.py); " +
        "the structure step chosen on the gated rows against the comparison twin c05t",
      cuts: "results/2026-10-02-w43-g3-refit/read/c05-cuts.json",
      reproduce: "python3.12 -B packages/calibration/results/2026-10-02-w43-g3-refit/fit/fit.py render c05 " +
        "--set calibration,validation,recorded,probe",
    },
    entries,
    patch,
    ...(pose === "active"
      ? { cssTierMapping: (scheme === "light" ? twin["cssTierMapping"] : twin["cssTierMapping"]) ?? null }
      : {}),
  };
  if (document["cssTierMapping"] === null) delete document["cssTierMapping"];
  const out = join(PROFILES, `${key}.json`);
  if (existsSync(out)) throw new Error(`${rel(out)} exists; a sealed document's bytes never move`);
  const text = `${JSON.stringify(document, null, 2)}\n`;
  writeFileSync(out, text);
  manifest[`${key}.json`] = {
    fileSha256: sha256(text), resolvedMaterialSha256: digest, movedLeaves: moved,
    twinSha256: sha256(twinText), candidateEndpointSha256: candidate.endpoints[slot].sha256,
  };
}

writeFileSync(join(HERE, "sealed-manifest.json"), `${JSON.stringify({
  what: "W43 G3 (ii): candidate c05 sealed as the four -glass0.25 profile documents",
  candidate: { declaration: rel(CANDIDATE), sha256: candidateSha },
  digestRule: MATERIAL_DIGEST_RULE_VERSION,
  documents: manifest,
}, null, 2)}\n`);
console.log(JSON.stringify(manifest, null, 2));
