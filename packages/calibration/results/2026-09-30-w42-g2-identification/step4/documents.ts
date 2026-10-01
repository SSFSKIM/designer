/**
 * W42 G2 step 4, item 1: the scratch candidate documents of the improvement landing
 * (`../improvement-landing-addendum.md`, SHA-256 0398c9c8…; charter Decision Log 7).
 *
 * Writes `documents/<set>/<shipped basename>.json` and `documents/documents.json`. No file under
 * `profiles/` is read for writing; each candidate is the shipped document's bytes as parsed, its
 * `patch` extended by the W42 leaves, its provenance fields restated, and its
 * `resolvedMaterialSha256` taken under the current digest rule over the material the page resolves.
 * Every document passes the runtime's own patch boundary twice: the calibration reader
 * (`readMaterialProfileFile` / `readRecededProfileFile`, which call `validateBodyE3Patch` and
 * `validateBodyLawPatch`) and `withMaterialOverrides`, the merge the root performs.
 *
 * Sets:
 * - `c1`: candidate 1. Light active and dark receded carry LT over the landed solve (the black-join
 *   bridge is the shader's own); light receded adds E3 (W41's sealed F and gains) with the F
 *   extension. Dark active stays the shipped file (Decision Log 5f).
 * - `c2`: candidate 2. LT with the native-T table and the landing chroma scale; E3 off. The runtime
 *   table is ONE row set read on encoded luma, so the per-channel row sets the addendum names are
 *   realised by their Rec.709 combination (`bodyToneTableCodesRec709`). The departure is a size
 *   change the runtime does not carry; it is measured and reported in documents.json, not hidden.
 * - `c1ref`: clause 7's light-receded reference for candidate 1, E3 with its extended F alone
 *   (every W42 law leaf at its identity).
 *
 *   cd packages/calibration && pnpm exec tsx results/2026-09-30-w42-g2-identification/step4/documents.ts
 */
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  DEFAULT_MATERIAL_PROFILE,
  MATERIAL_DIGEST_RULE_VERSION,
  materialDigestInput,
  withMaterialOverrides,
  type MaterialProfile,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

import { readMaterialProfileFile, readRecededProfileFile } from "../../../scripts/material-profile-file.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const CAL = resolve(HERE, "../../..");
const REPO = resolve(CAL, "../..");
const STEP2 = resolve(HERE, "../step2");
const PROFILES = resolve(CAL, "profiles");
const OUT = resolve(HERE, "documents");

const sha = (raw: string | Buffer) => createHash("sha256").update(raw).digest("hex");
const json = (path: string) => JSON.parse(readFileSync(path, "utf8")) as Record<string, unknown>;
const rel = (path: string) => relative(REPO, path);

const ADDENDUM = resolve(HERE, "../improvement-landing-addendum.md");
const ADDENDUM_SHA = "0398c9c85509729d7d3be73ac12bafe6af477b62d2b194820762f9a06cf5911f";
if (sha(readFileSync(ADDENDUM)) !== ADDENDUM_SHA) throw new Error("the addendum moved");

// ------------------------------------------------------------------------------- the values

const fit = (json(join(STEP2, "fits/main/LT@k@global__all__n.json")) as {
  ls: { params: { "k@all": number }; lam: Record<string, number> };
}).ls;
const scale = json(join(STEP2, "landing-scale.json")) as {
  k: number; endpoints: Record<string, { scale: number; gCoefficients: [number, number, number] }>;
};
const cands = (json(join(STEP2, "candidates.json")) as { endpoints: Record<string, any> }).endpoints;
const w41Sealed = json(resolve(CAL,
  "results/2026-09-29-w41-g2-landing/retired-documents/" +
  "apple-macos-27.0-1x-light-standard-glass0.5-receded.003940b4c7da.json")) as {
  patch: { bodyE3Strength: number; bodyE3Gains: [number, number, number];
    bodyE3Neutral: [number, number, number, number, number, number, number] };
};

const K = fit.params["k@all"];
// The addendum's section 3 table, stated before any render; the files must agree with it.
const DECLARED = {
  k: 2.1378819065300068,
  lambda: { "light-rest": 0.868087996132754, "light-inactive": 0.7668713671405096,
    "dark-inactive": 0.7588099764934113 },
  scale: { "light-rest": 0.976496, "light-inactive": 0.987365, "dark-inactive": 0.909586 },
  neutralHigh: [201.9278, 208, 215, 221, 228, 234, 240],
  e3Neutral: [150, 157, 164, 171, 178, 188, 197],
} as const;
const close = (a: number, b: number, tol: number) => Math.abs(a - b) <= tol;
if (K !== DECLARED.k || scale.k !== K) throw new Error(`k ${K} is not the addendum's`);
for (const [ep, lam] of Object.entries(DECLARED.lambda)) {
  if (fit.lam[ep] !== lam) throw new Error(`lambda ${ep} ${fit.lam[ep]} is not the addendum's`);
  if (!close(scale.endpoints[ep]!.scale, DECLARED.scale[ep as keyof typeof DECLARED.scale], 5e-7)) {
    throw new Error(`scale ${ep} is not the addendum's`);
  }
}
const high = cands["light-inactive"].candidate1.bodyE3NeutralHigh as number[];
if (JSON.stringify(high) !== JSON.stringify(DECLARED.neutralHigh)) throw new Error("F extension");
if (JSON.stringify(w41Sealed.patch.bodyE3Neutral) !== JSON.stringify(DECLARED.e3Neutral)) {
  throw new Error("E3's F is not W41's seven ordinates");
}

type Ep = "light-rest" | "light-inactive" | "dark-inactive";
const law = (ep: Ep): MaterialProfilePatch => ({
  bodyLawStrength: 1,
  bodyLawK: [K, K],
  bodyLawLambda: fit.lam[ep]!,
  bodyLawNormal: 0.5,
  bodyLawHinge: ep.startsWith("light") ? 1 : -1,
  bodyLawPose: ep.endsWith("rest") ? 0 : 1,
  bodyLawKnee: 0,
  bodyLawEdgeSwap: 0,
  bodyLawWidthUnit: 1,
  bodyLawEncodedAveraging: 1,
} as MaterialProfilePatch);
const e3: MaterialProfilePatch = {
  bodyE3Strength: 1,
  bodyE3Gains: w41Sealed.patch.bodyE3Gains,
  bodyE3Neutral: w41Sealed.patch.bodyE3Neutral,
  bodyE3HighStrength: 1,
  bodyE3NeutralHigh: high,
} as MaterialProfilePatch;
const table = (ep: Ep): MaterialProfilePatch => {
  const c2 = cands[ep].candidate2;
  return {
    bodyToneTableStrength: 1,
    bodyToneTableLevels: c2.bodyToneTableLevels,
    bodyToneTableSpans: c2.bodyToneTableSpans,
    bodyToneTableCodes: c2.bodyToneTableCodesRec709,
    bodyToneChromaGains: scale.endpoints[ep]!.gCoefficients,
    bodyToneChromaScale: scale.endpoints[ep]!.scale,
  } as MaterialProfilePatch;
};

// ------------------------------------------------------------------------------- the documents

const BASE = {
  light: "apple-macos-27.0-1x-light-standard-glass0.5.json",
  lightReceded: "apple-macos-27.0-1x-light-standard-glass0.5-receded.json",
  dark: "apple-macos-27.0-1x-dark-standard-glass0.5.json",
  darkReceded: "apple-macos-27.0-1x-dark-standard-glass0.5-receded.json",
} as const;
type Base = keyof typeof BASE;

interface Spec { readonly set: string; readonly note: string;
  readonly docs: Partial<Record<Base, { endpoint: string; add: MaterialProfilePatch }>> }
const SETS: Spec[] = [
  { set: "c1", note: "candidate 1: LT over the landed solve (black-join bridge); light receded E3 " +
      "with the F extension; dark active the shipped file",
    docs: {
      light: { endpoint: "light active", add: law("light-rest") },
      lightReceded: { endpoint: "light receded", add: { ...law("light-inactive"), ...e3 } },
      darkReceded: { endpoint: "dark receded", add: law("dark-inactive") },
    } },
  { set: "c2", note: "candidate 2: LT with the native-T table (Rec.709 realisation of the per-channel " +
      "row sets) and the landing chroma scale; dark active the shipped file",
    docs: {
      light: { endpoint: "light active", add: { ...law("light-rest"), ...table("light-rest") } },
      lightReceded: { endpoint: "light receded",
        add: { ...law("light-inactive"), ...table("light-inactive") } },
      darkReceded: { endpoint: "dark receded",
        add: { ...law("dark-inactive"), ...table("dark-inactive") } },
    } },
  { set: "c1ref", note: "clause 7's light-receded reference for candidate 1: E3 with its extended F " +
      "alone, every W42 law leaf at its identity",
    docs: { lightReceded: { endpoint: "light receded", add: e3 } } },
];

const fingerprint = (resolved: unknown): string => {
  const canonical = (value: unknown): unknown =>
    Array.isArray(value) ? value.map(canonical)
      : value !== null && typeof value === "object"
        ? Object.fromEntries(Object.keys(value as object).sort()
          .map((key) => [key, canonical((value as Record<string, unknown>)[key])]))
        : value;
  return sha(JSON.stringify(canonical(resolved))).slice(0, 16);
};
const digest = (m: MaterialProfile) => fingerprint(materialDigestInput(m));

if (existsSync(OUT)) throw new Error(`${rel(OUT)} exists; documents are written once`);
const record: Record<string, unknown> = {
  schema: "w42-g2-step4-documents-1",
  addendum: { path: rel(ADDENDUM), sha256: ADDENDUM_SHA },
  digestRule: MATERIAL_DIGEST_RULE_VERSION,
  values: {
    k: K, lambda: DECLARED.lambda, landingScale: Object.fromEntries(
      Object.entries(scale.endpoints).map(([ep, v]) => [ep, v.scale])),
    candidate1LightRecededE3: { source: "W41 G2's sealed receded document 003940b4c7da",
      bodyE3Gains: w41Sealed.patch.bodyE3Gains, bodyE3Neutral: w41Sealed.patch.bodyE3Neutral,
      bodyE3NeutralHigh: high },
  },
  sets: {} as Record<string, unknown>,
};

for (const spec of SETS) {
  const dir = join(OUT, spec.set);
  mkdirSync(dir, { recursive: true });
  const out: Record<string, unknown> = {};
  const activePatch: Record<"light" | "dark", MaterialProfilePatch> = {
    light: json(join(PROFILES, BASE.light)).patch as MaterialProfilePatch,
    dark: json(join(PROFILES, BASE.dark)).patch as MaterialProfilePatch,
  };
  const activePath: Record<"light" | "dark", string> = {
    light: join(PROFILES, BASE.light), dark: join(PROFILES, BASE.dark),
  };
  for (const base of ["light", "dark", "lightReceded", "darkReceded"] as Base[]) {
    const want = spec.docs[base];
    const scheme = base.startsWith("light") ? "light" : "dark";
    const receded = base.endsWith("Receded");
    if (want === undefined) {
      out[base] = { path: rel(join(PROFILES, BASE[base])), shipped: true,
        sha256: sha(readFileSync(join(PROFILES, BASE[base]))).slice(0, 12) };
      continue;
    }
    const shipped = json(join(PROFILES, BASE[base]));
    const patch = { ...(shipped.patch as MaterialProfilePatch), ...want.add } as MaterialProfilePatch;
    for (const key of Object.keys(want.add)) {
      if (key in (shipped.patch as object)) throw new Error(`${base}: the shipped patch already names ${key}`);
    }
    const resolved = receded
      ? withMaterialOverrides(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, activePatch[scheme]), patch)
      : withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    const path = join(dir, BASE[base]);
    const document: Record<string, unknown> = {
      "$comment-w42-g2-step4": [
        `SCRATCH CANDIDATE, never shipped: W42 G2 step 4, set ${spec.set} (${spec.note}).`,
        `The ${want.endpoint} endpoint under the improvement-landing addendum (SHA-256 ${ADDENDUM_SHA}).`,
        `It is the shipped ${BASE[base]} as parsed, with these W42 leaves added to its patch:`,
        Object.keys(want.add).join(", ") + ".",
        "Everything else, the provenance comments included, is the shipped document's and describes",
        "the shipped material; resolvedMaterialSha256 below is this document's own, under the current",
        "digest rule, written by step4/documents.ts.",
      ],
      ...shipped,
      recordedAt: "2026-10-01",
      recordedBy: `W42 G2 step 4 (scratch candidate ${spec.set})`,
      patch,
      resolvedMaterialSha256: digest(resolved),
      resolvedMaterialSha256Rule: MATERIAL_DIGEST_RULE_VERSION,
    };
    if (receded) {
      document["appliesOver"] = rel(activePath[scheme]);
      document["resolvedOverActiveDocument"] = activePath[scheme].split("/").pop();
    }
    const text = `${JSON.stringify(document, null, 2)}\n`;
    writeFileSync(path, text, { flag: "wx" });
    // The page's boundary, as capture-web reads it, and the root's merge above.
    const read = receded ? readRecededProfileFile(path) : readMaterialProfileFile(path);
    if (read.profileKey !== shipped["profileKey"]) throw new Error(`${path}: profileKey`);
    for (const [key, value] of Object.entries(want.add)) {
      if (JSON.stringify((resolved as unknown as Record<string, unknown>)[key]) !== JSON.stringify(value)) {
        throw new Error(`${path}: ${key} did not resolve as written`);
      }
    }
    if (!receded) {
      activePatch[scheme] = patch;
      activePath[scheme] = path;
    }
    out[base] = { path: rel(path), shipped: false, endpoint: want.endpoint, sha256: read.sha256,
      fileSha256: sha(text), resolvedMaterialSha256: digest(resolved), leaves: want.add,
      shippedResolvedMaterialSha256: shipped["resolvedMaterialSha256"] };
  }
  (record.sets as Record<string, unknown>)[spec.set] = out;
}

// What the luma table departs from the addendum's per-channel row sets by, in codes.
const realisation: Record<string, unknown> = {};
for (const ep of ["light-rest", "light-inactive", "dark-inactive"] as Ep[]) {
  const c2 = cands[ep].candidate2;
  let worst = 0;
  for (const channel of ["R", "G", "B"]) {
    (c2.bodyToneTableCodes[channel] as number[][]).forEach((row, r) => row.forEach((v, i) => {
      worst = Math.max(worst, Math.abs(v - c2.bodyToneTableCodesRec709[r][i]));
    }));
  }
  realisation[ep] = { worstChannelDepartureCodes: worst, channelSpreadCodes: c2.channelSpreadCodes };
}
record["candidate2TableRealisation"] = {
  note: "the runtime's bodyToneTableCodes is one 5 x 11 row set read on encoded luma " +
    "(body_table_codes); the addendum's candidate 2 names one row set per channel. The documents " +
    "carry the Rec.709 combination, which preserves each grey's output luma; a grey's channel " +
    "departs from its own row set by at most the worst below",
  ...realisation,
};
writeFileSync(join(OUT, "documents.json"), `${JSON.stringify(record, null, 1)}\n`, { flag: "wx" });
process.stdout.write(`${JSON.stringify(record, null, 1)}\n`);
