/**
 * W41 G1 scratch candidate only (clause 11, c9a §5.192). Run with tsx from any cwd.
 * Reads committed profile documents, never native pixels, holdout or fit payloads.
 * The CLI writes only beside this script; no historical sealing writer is invoked.
 */
import { createHash } from "node:crypto";
import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { relative, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import {
  DEFAULT_MATERIAL_PROFILE, MATERIAL_DIGEST_RULE_VERSION, materialDigestInput,
  withMaterialOverrides, type MaterialProfile, type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const HERE = import.meta.dirname;
const CALIBRATION = resolve(HERE, "../../..");
const REPOSITORY = resolve(CALIBRATION, "../..");
const PROFILES = resolve(CALIBRATION, "profiles");
const LIGHT = "apple-macos-27.0-1x-light-standard-glass0.5.json";
const RECEDED = LIGHT.replace(".json", "-receded.json");
const DARK = LIGHT.replace("light", "dark");
const DARK_RECEDED = DARK.replace(".json", "-receded.json");
interface Document extends Record<string, unknown> {
  patch: MaterialProfilePatch;
  resolvedMaterialSha256: string;
  resolvedOverActiveDocument?: string;
}
const read = (name: string): Document =>
  JSON.parse(readFileSync(resolve(PROFILES, name), "utf8")) as Document;
const sha = (value: string | Buffer): string => createHash("sha256").update(value).digest("hex");
function canonical(value: unknown): unknown {
  return Array.isArray(value) ? value.map(canonical) :
    value !== null && typeof value === "object" ? Object.fromEntries(
      Object.keys(value).sort().map((key) =>
        [key, canonical((value as Record<string, unknown>)[key])]),
    ) : value;
}
const digest = (material: MaterialProfile): string =>
  sha(JSON.stringify(canonical(materialDigestInput(material)))).slice(0, 16);
function sourceMaterial(name: string): MaterialProfile {
  const doc = read(name);
  return withMaterialOverrides(doc.resolvedOverActiveDocument === undefined ?
    DEFAULT_MATERIAL_PROFILE : sourceMaterial(doc.resolvedOverActiveDocument), doc.patch);
}

/** The explicit destination supports an isolated temporary directory in the unit test. */
export function generateScratchCandidate(outDir = resolve(HERE, "candidate")): void {
  const pins = JSON.parse(readFileSync(resolve(HERE, "source-document-pins.json"), "utf8")) as
    Record<string, { sha256: string; resolvedMaterialSha256: string }>;
  if (MATERIAL_DIGEST_RULE_VERSION !== 2) throw new Error("W41 scratch requires digest rule 2");
  // Fail before writing if the baseline has changed; do not silently reseal new input bytes.
  for (const [name, pin] of Object.entries(pins)) {
    if (sha(readFileSync(resolve(PROFILES, name))) !== pin.sha256 ||
      digest(sourceMaterial(name)) !== pin.resolvedMaterialSha256) {
      throw new Error(`W41 source pin changed: ${name}`);
    }
  }
  const receded = read(RECEDED);
  const patch: MaterialProfilePatch = {
    ...receded.patch,
    bodyE3Strength: 1,
    bodyE3Gains: [0.929205829365914, 0.9597570955316058, 0.9383102545096953],
    bodyE3Neutral: [150, 157, 164, 171, 178, 188, 197],
  };
  const candidateMaterial = withMaterialOverrides(sourceMaterial(LIGHT), patch);
  const candidate: Document = {
    ...receded,
    patch,
    appliesOver: relative(REPOSITORY, resolve(outDir, LIGHT)),
    resolvedOverActiveDocument: LIGHT,
    resolvedMaterialSha256: digest(candidateMaterial),
    resolvedMaterialSha256Rule: 2,
    "$comment-w41-candidate": "SCRATCH ONLY, not selected or published. Full existing light-receded " +
      "patch plus E3; frozen B1 upper-witness gains, no refit. At presence 1 E3 replaces prior " +
      "tone-solve, retention and black-branch output before author tint; rim is unchanged. " +
      "Nominal material policy, regular variant, actual sampled texture only. CSS step 9 deferred.",
  };
  mkdirSync(outDir, { recursive: true });
  for (const name of [LIGHT, DARK, DARK_RECEDED]) {
    copyFileSync(resolve(PROFILES, name), resolve(outDir, name));
  }
  writeFileSync(resolve(outDir, RECEDED), `${JSON.stringify(candidate, null, 2)}\n`);
  const documents = Object.fromEntries([LIGHT, RECEDED, DARK, DARK_RECEDED].map((name) => {
    const bytes = readFileSync(resolve(outDir, name));
    const doc = JSON.parse(bytes.toString("utf8")) as Document;
    return [name, {
      sha256: sha(bytes), captureSha256: sha(bytes).slice(0, 12),
      resolvedMaterialSha256: doc.resolvedMaterialSha256,
      bodyE3Strength: name === RECEDED ? 1 : 0,
      byteEqualBaseline: name !== RECEDED,
    }];
  }));
  writeFileSync(resolve(outDir, "evidence.json"), `${JSON.stringify({
    status: "scratch only; no browser render, native reread, fit replay or publication",
    sourceDocuments: pins,
    documents,
    domain: {
      endpoint: "light-receded only; the other three endpoints are byte-equal baseline documents",
      materialPolicy: "fully nominal material axes; Reduced Motion alone does not disable E3",
      variant: "regular only",
      sampling: "actual sampled texture only; post-refraction blurred/scatter backdrop, not group mean",
      input: "encoded sRGB cube; selected document's convex mix, no signed unsharp/HDR extension",
      presence1: "identified E3 replaces old tone-solve, retention and black-branch body output",
      presenceIntermediate: "linear-light mix(backdrop, decode(E3(encode(backdrop))), presence); unmeasured extension",
      presence0: "exact skip",
      fractionalStrength: "linear-light interpolation from old body to replacement; unmeasured extension",
      placement: "before author tint; rim, alpha, coverage, lens and shadow unchanged",
    },
    css: "unchanged; step 9 projection and residual measurement deferred, not a measured E3 decline",
    bridgeInputs: [[192, 32, 32], [32, 192, 32]],
    neutralContinuation: [
      { input: 0, output: 150 + (0 - 40) * (157 - 150) / (56 - 40), w36Native: 133 },
      { input: 32, output: 150 + (32 - 40) * (157 - 150) / (56 - 40) },
      { input: 192, output: 197 + (192 - 150) * (197 - 188) / (150 - 128) },
    ],
    continuationContext: "Pre-G2 algebra, not new native readings. F(0)=132.5 beside W36 receded-light " +
      "native 133. Bridge channel inputs 32/192 have neutral continuations F(32)=146.5 and " +
      "F(192)=214.1818181818182; E3 evaluates F at each full RGB input's encoded weighted L, " +
      "not independently at its channel values.",
    digestConvention: "resolved: sorted-key materialDigestInput, array order retained, SHA256 first16hex, rule2; " +
      "capture: complete file SHA256 first12hex; full SHA256 also recorded",
  }, null, 2)}\n`);
}

if (process.argv[1] !== undefined && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  generateScratchCandidate();
}
