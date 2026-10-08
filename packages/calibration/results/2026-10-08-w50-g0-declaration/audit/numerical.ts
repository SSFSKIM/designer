/**
 * W50's pre-render numerical referee. This reads candidate documents and measured
 * arguments, never native pixels. Missing structured evidence is UNMEASURED; the
 * synthetic test helper is not a candidate report. CLI domain is fixed below.
 *
 * Run from calibration: pnpm exec tsx results/2026-10-08-w50-g0-declaration/audit/numerical.ts
 *   --cohort <repo-relative cohort.json> --out <new report.json>
 *
 * Cohort schema w50-numerical-cohort-1: candidates [{position,path,sha256}] at
 * 0.25/0.5, structuredArguments {path,sha256}. The latter pins a manifest with
 * schema w50-structured-arguments-1, candidateSha256s, references {path,sha256},
 * requiredIds and records. The required IDs are derived from the fixed exposed
 * reference population, not chosen by the candidate. Records state profile,
 * renderer, scene, variant, pose, scale, span, independent encoded/linear means
 * and linear RGB; id is profile|renderer|scene. Each pins an evidence JSON with
 * schema w50-measured-tone-argument-1 and identical fields (no evidence key).
 * Sources and documents are repository-relative pins.
 */
import { createHash } from "node:crypto";
import { existsSync, readFileSync, realpathSync, writeFileSync } from "node:fs";
import { registerHooks } from "node:module";
import { isAbsolute, relative, resolve } from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { isDeepStrictEqual } from "node:util";
import type { MaterialProfilePatch } from "../../../../renderer-webgpu/src/material";
import type { ResolvedMaterialPolicy } from "@vitreajs/vitrea";

type Pose = "active" | "receded";
type Pin = { readonly path: string; readonly sha256: string };
export interface NumericalEndpoint {
  readonly position: number;
  readonly pose: Pose;
  readonly profile: MaterialProfilePatch;
}
export interface StructuredArgument {
  readonly id: string;
  readonly profile: string;
  readonly renderer: "webgpu" | "css";
  readonly scene: string;
  readonly variant: "regular" | "clear";
  readonly position: number;
  readonly pose: Pose;
  readonly dpr: number;
  readonly span: number;
  readonly role: string;
  readonly candidateSha256: string;
  /** Encoded-space group/silhouette mean, not the encoding of the linear mean. */
  readonly encodedLuminance: number;
  readonly linearLuminance: number;
  readonly rgb: readonly [number, number, number];
}
export const FULL_DOMAIN = {
  inputCodeMin: 0, inputCodeMax: 64, stepCode: 1 / 64,
  spanMin: 32, spanMax: 224, scales: [1, 2], positions: [0.25, 0.5],
  poses: ["active", "receded"] as readonly Pose[],
};
type Domain = typeof FULL_DOMAIN;
const ROOT = realpathSync(fileURLToPath(new URL("../../../../../", import.meta.url)));
const SELF = fileURLToPath(import.meta.url);
const HASH = /^[0-9a-f]{64}$/;
const nominal: ResolvedMaterialPolicy = {
  glass: "material", colorSource: "material", frost: "nominal", refraction: "nominal",
  occlusion: "nominal", border: "nominal", ambientTint: "nominal", foreground: "adaptive",
};
const decode = (v: number): number => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
const encode = (v: number): number => v <= 0.0031308 ? v * 12.92 : 1.055 * v ** (1 / 2.4) - 0.055;
const sha = (path: string): string => createHash("sha256").update(readFileSync(path)).digest("hex");
const record = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const canonical = (value: unknown): unknown => Array.isArray(value) ? value.map(canonical)
  : record(value) ? Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonical(value[key])]))
    : value;
const key = (value: { position: number; pose: string; dpr?: number }): string =>
  `${value.position}:${value.pose}${value.dpr === undefined ? "" : `:${value.dpr}`}`;

function inside(root: string, path: string): string {
  if (isAbsolute(path)) throw new Error(`Expected repository-relative path: ${path}`);
  const absolute = realpathSync(resolve(root, path));
  const rel = relative(realpathSync(root), absolute);
  if (rel.startsWith("..") || isAbsolute(rel)) throw new Error(`Path escapes root: ${path}`);
  return absolute;
}
function readPin(root: string, value: unknown): { pin: Pin; absolute: string } {
  if (!record(value) || typeof value.path !== "string" || typeof value.sha256 !== "string" ||
      !HASH.test(value.sha256)) throw new Error("Missing content-addressed file pin");
  const absolute = inside(root, value.path);
  if (sha(absolute) !== value.sha256) throw new Error(`Pinned file hash/bytes changed: ${value.path}`);
  return { pin: { path: relative(root, absolute), sha256: value.sha256 }, absolute };
}
export function verifyPins(root: string, pins: readonly Pin[]): void {
  for (const pin of pins) readPin(root, pin);
}

const SELF_SHA = sha(SELF);
const WITNESS = fileURLToPath(new URL("./runtime-closure.json", import.meta.url));
const DECLARATION = fileURLToPath(new URL("../", import.meta.url));
const PARTS = ["declaration", "fit-declaration"] as const;

/** Checks repository code before nextLoad; the returned hook remains installed for late imports. */
export function installSourceGuard(root: string, expected: readonly Pin[] | undefined,
  observed = new Map<string, string>()) {
  const canonicalRoot = realpathSync(root);
  const wanted = expected === undefined ? undefined : new Map(expected.map((pin) => [pin.path, pin.sha256]));
  return registerHooks({
    load(url, context, nextLoad) {
      if (url.startsWith("file:")) {
        const path = realpathSync(fileURLToPath(url));
        const rel = relative(canonicalRoot, path);
        if (!rel.startsWith("..") && !isAbsolute(rel) && !rel.split("/").includes("node_modules")) {
          const digest = sha(path);
          if (wanted !== undefined && !wanted.has(rel)) throw new Error(`Unsealed runtime import: ${rel}`);
          if (wanted !== undefined && wanted.get(rel) !== digest) throw new Error(`Changed runtime import: ${rel}`);
          observed.set(path, digest);
        }
      }
      return nextLoad(url, context);
    },
  });
}

/** The fixed witness is authorised by both immutable root parts, never by a caller-supplied list. */
function authorisedRuntimePins(): Pin[] {
  const witnessPin = { path: relative(ROOT, WITNESS), sha256: sha(WITNESS) };
  for (const part of PARTS) {
    const path = resolve(DECLARATION, `${part}.json`);
    const seal = resolve(DECLARATION, `${part}.sha256`);
    if (!existsSync(seal) || readFileSync(seal, "utf8") !== `${sha(path)}  ${part}.json\n`) {
      throw new Error(`UNMEASURED: ${part} has no matching operational root seal`);
    }
    const document: unknown = JSON.parse(readFileSync(path, "utf8"));
    if (!record(document) || !Array.isArray(document.sources) ||
        !document.sources.some((pin) => record(pin) && pin.path === witnessPin.path && pin.sha256 === witnessPin.sha256)) {
      throw new Error(`Runtime closure is not authorised by ${part}`);
    }
    const producer = document.sources.find((pin) => record(pin) && pin.path === relative(ROOT, SELF));
    if (!record(producer) || producer.sha256 !== SELF_SHA) throw new Error(`Producer is not authorised by ${part}`);
  }
  const witness: unknown = JSON.parse(readFileSync(WITNESS, "utf8"));
  if (!record(witness) || witness.schema !== "w50-numerical-runtime-closure-1" ||
      !Array.isArray(witness.sources) || !witness.sources.length) throw new Error("Missing fixed runtime closure");
  const pins = witness.sources.map((pin) => readPin(ROOT, pin).pin);
  if (new Set(pins.map(({ path }) => path)).size !== pins.length ||
      !pins.some((pin) => pin.path === relative(ROOT, SELF) && pin.sha256 === SELF_SHA) ||
      !pins.some((pin) => pin.path === "pnpm-lock.yaml")) throw new Error("Incomplete or duplicated runtime closure");
  return pins;
}

/** Install before importing any numerical runtime; discovery is an explicit pre-seal dry exercise only. */
let runtimePromise: ReturnType<typeof importRuntime> | undefined;
let runtimeMode: "discovery" | "authorised" | undefined;
async function importRuntime(expected: readonly Pin[] | undefined) {
  const sources = new Map<string, string>();
  // Deliberately permanent. Candidate parsing and evaluation may import a later measurement branch.
  installSourceGuard(ROOT, expected, sources);
  const [css, renderer, candidate, documents] = await Promise.all([
    import("../../../../platform-web/src/optics.ts"),
    import("../../../../renderer-webgpu/src/material.ts"),
    import("../../../scripts/candidate-document.ts"),
    import("../../../../platform-web/src/material-document.ts"),
  ]);
  sources.set(SELF, SELF_SHA);
  sources.set(resolve(ROOT, "pnpm-lock.yaml"), sha(resolve(ROOT, "pnpm-lock.yaml")));
  return { css, renderer, candidate, documents, sources };
}
export function loadRuntime(options: { readonly discovery?: boolean } = {}) {
  const discovery = options.discovery ?? runtimeMode === "discovery";
  if (discovery && PARTS.some((part) => existsSync(resolve(DECLARATION, `${part}.sha256`)))) {
    throw new Error("Runtime discovery refuses after an operational root seal");
  }
  const mode = discovery ? "discovery" : "authorised";
  if (runtimeMode !== undefined && runtimeMode !== mode) {
    throw new Error("A discovery runtime cannot be reused for production or vice versa");
  }
  if (runtimePromise === undefined) {
    const pins = discovery ? undefined : authorisedRuntimePins();
    runtimeMode = mode;
    runtimePromise = importRuntime(pins);
  }
  return runtimePromise;
}

function validateArgument(value: unknown): asserts value is StructuredArgument {
  if (!record(value) || typeof value.id !== "string" || !value.id ||
      !FULL_DOMAIN.positions.includes(value.position as number) ||
      !FULL_DOMAIN.poses.includes(value.pose as Pose) || !FULL_DOMAIN.scales.includes(value.dpr as number) ||
      typeof value.span !== "number" || !Number.isFinite(value.span) || value.span < 32 || value.span > 224 ||
      typeof value.candidateSha256 !== "string" || !HASH.test(value.candidateSha256)) {
    throw new Error("Malformed measured structured argument identity");
  }
  const match = typeof value.profile === "string"
    ? /^apple-macos-27\.0-([12])x-dark-standard-glass(0\.25|0\.5)$/.exec(value.profile) : null;
  if (!match || Number(match[1]) !== value.dpr || Number(match[2]) !== value.position ||
      !["webgpu", "css"].includes(value.renderer as string) ||
      !["regular", "clear"].includes(value.variant as string) || typeof value.scene !== "string" ||
      !value.scene.endsWith(value.pose === "receded" ? "__inactive" : "__rest") ||
      value.id !== `${value.profile}|${value.renderer}|${value.scene}`) {
    throw new Error("Measured argument profile/tier/scene/variant differs from its identity");
  }
  if (!["calibration", "validation", "recorded", "probe", "gate"].includes(value.role as string)) {
    throw new Error("Withheld or unknown measured argument role");
  }
  for (const name of ["encodedLuminance", "linearLuminance"] as const) {
    const v = value[name];
    if (typeof v !== "number" || !Number.isFinite(v) || v < 0 || v > 1) {
      throw new Error(`Measured argument ${name} is not finite in [0,1]`);
    }
  }
  if (!Array.isArray(value.rgb) || value.rgb.length !== 3 ||
      value.rgb.some((v) => typeof v !== "number" || !Number.isFinite(v) || v < 0 || v > 1)) {
    throw new Error("Measured low-end argument needs explicit finite linear RGB");
  }
  // Scene membership fixes the observed controls, not the packed argument's last bit.
  // A measured grey64 may lie just above64 after f32 storage. Keep it unchanged:
  // the production diagnostic owns compact-support eligibility, including its old-domain exit.
  const rgb = value.rgb as number[];
  const luma = 0.2126 * rgb[0]! + 0.7152 * rgb[1]! + 0.0722 * rgb[2]!;
  // γ8: three weighted products, two additions and separately stored input/output lanes.
  // This is a binary32 rounding bound, not a native-error budget or a replacement of measured Y.
  const u = 2 ** -24;
  const rounding = 8 * u / (1 - 8 * u) * Math.max(...rgb, value.linearLuminance as number)
    + 8 * 2 ** -149;
  if (Math.abs(luma - (value.linearLuminance as number)) > rounding) {
    throw new Error("Explicit measured RGB and independent linear mean disagree");
  }
}

/** Every exposed target is priced, not a hand-picked eight-configuration smoke cohort. */
export function requiredArgumentIds(inventory: unknown): string[] {
  if (!record(inventory) || inventory.schema !== "w50-reference-inventory-1" || !Array.isArray(inventory.cells)) {
    throw new Error("Missing declared reference population");
  }
  const ids = new Set<string>();
  for (const cell of inventory.cells) {
    if (!record(cell) || typeof cell.profile !== "string" || typeof cell.scene !== "string" ||
        !["webgpu", "css"].includes(cell.renderer as string)) throw new Error("Malformed reference identity");
    if (["blind", "historical-prediction-check"].includes(cell.role as string)) continue;
    const uniform = /^cell-grey-(\d{3})-s\d+__(rest|inactive)$/.exec(cell.scene);
    const selected = /^impulse__rrect-(ml|lg)__(rest|inactive)$/.test(cell.scene) ||
      /^dark-solid__[^_]+__(rest|inactive)$/.test(cell.scene) ||
      /^cell-(impulse-sparse|checker-low)-s\d+__(rest|inactive)$/.test(cell.scene) ||
      (uniform !== null && Number(uniform[1]) <= 64);
    if (selected) ids.add(`${cell.profile}|${cell.renderer}|${cell.scene}`);
  }
  if (!ids.size) throw new Error("UNMEASURED: declared low-end argument population is empty");
  return [...ids].sort();
}

export function readStructuredArguments(path: string, expectedSha: string, candidates: readonly string[], root = ROOT) {
  const pin = readPin(root, { path: relative(root, path), sha256: expectedSha });
  const manifest: unknown = JSON.parse(readFileSync(path, "utf8"));
  if (!record(manifest) || manifest.schema !== "w50-structured-arguments-1" ||
      !Array.isArray(manifest.candidateSha256s) ||
      !isDeepStrictEqual([...manifest.candidateSha256s].sort(), [...candidates].sort()) ||
      !Array.isArray(manifest.records) || !manifest.records.length) {
    throw new Error("UNMEASURED: missing or mismatched measured argument cohort");
  }
  const referencePin = readPin(root, manifest.references);
  const requiredIds = requiredArgumentIds(JSON.parse(readFileSync(referencePin.absolute, "utf8")));
  if (!isDeepStrictEqual(manifest.requiredIds, requiredIds) ||
      !isDeepStrictEqual(manifest.records.map((value) => record(value) ? value.id : null).sort(), requiredIds)) {
    throw new Error("UNMEASURED: measured records do not equal the complete declared low-end population");
  }
  const pins = [pin.pin, referencePin.pin];
  const ids = new Set<string>();
  const records = manifest.records.map((raw) => {
    validateArgument(raw);
    if (ids.has(raw.id) || !candidates.includes(raw.candidateSha256)) {
      throw new Error("Duplicate or wrong-cohort measured argument");
    }
    ids.add(raw.id);
    const input = raw as StructuredArgument & { evidence?: Pin };
    const evidence = readPin(root, input.evidence);
    const measured: unknown = JSON.parse(readFileSync(evidence.absolute, "utf8"));
    const fields = { ...input };
    delete fields.evidence;
    if (!isDeepStrictEqual(canonical(measured), canonical({ schema: "w50-measured-tone-argument-1", ...fields }))) {
      throw new Error(`Measured argument differs from its pinned evidence: ${raw.id}`);
    }
    pins.push(evidence.pin);
    return fields;
  });
  return { records, pins, requiredIds, references: referencePin.pin };
}

/** A smaller domain is available only to imported tests, never through the CLI. */
export async function evaluateNumerical(endpoints: readonly NumericalEndpoint[],
  arguments_: readonly StructuredArgument[], domain: Domain = FULL_DOMAIN) {
  const { css } = await loadRuntime();
  const expected = domain.positions.flatMap((position) => domain.poses.map((pose) => key({ position, pose })));
  if (endpoints.length !== expected.length || !isDeepStrictEqual(endpoints.map(key).sort(), expected.sort())) {
    throw new Error("UNMEASURED: numerical cohort must contain all four dark endpoints exactly once");
  }
  for (const argument of arguments_) validateArgument(argument);
  let samples = 0;
  let maxRunningDrawdownCode = 0;
  let minimumRequestedNeutral = Infinity;
  let fixedJoinPass = true;
  let standDownPass = true;
  const negativeRequests: { kind: string; endpoint: string; span: number; dpr: number;
    inputCode: number; minimum: number; id?: string }[] = [];
  const inspect = (request: readonly number[] | undefined, reading: Omit<typeof negativeRequests[number], "minimum">) => {
    if (request === undefined) return;
    const minimum = Math.min(...request);
    if (!Number.isFinite(minimum)) throw new Error("Nonfinite unclamped neutral request");
    minimumRequestedNeutral = Math.min(minimumRequestedNeutral, minimum);
    if (minimum < 0 && negativeRequests.length < 64) negativeRequests.push({ ...reading, minimum });
    return minimum;
  };
  const toneAt = (input: number, linear = decode(input), rgb: readonly [number, number, number] = [linear, linear, linear]) =>
    ({ luminance: decode(input), linearLuminance: linear, rgb });
  const configured = endpoints.map((endpoint) => {
    const size = css.sourceSize(endpoint.profile);
    const response = css.resolvedBackdropToneResponse(endpoint.profile);
    if (response.lowEndStrength !== 1) throw new Error("W50 candidate strength must be1 at every dark endpoint");
    const source = css.sourceOptics(endpoint.profile).regular;
    const constants = css.resolvedBackdropTone(endpoint.profile);
    const strength = (css.backdropToneUnderPolicy(nominal, css.resolvedTintShade(endpoint.profile),
      size.refractionScale) >= 0.999 ? 1 : 0) * Math.min(1, Math.max(0, constants.max));
    return { ...endpoint, size, response, source, strength };
  });
  for (const endpoint of configured) {
    const { profile, size, response, source, strength } = endpoint;
    const off = { ...profile, lowEndStrength: 0 };
    const offResponse = css.resolvedBackdropToneResponse(off);
    for (const dpr of domain.scales) {
      for (let span = domain.spanMin; span <= domain.spanMax; span++) {
        const thickness = css.sizeThickness(span, size);
        const far = css.sizeToneLevelFar(span, size, dpr);
        const alpha = css.sizeOcclusionAlphaAt(css.spanGradedTintAlpha(source.tintAlpha, span, size, dpr),
          thickness, size);
        const sized = { ...source, tintAlpha: alpha };
        const old64 = css.backdropToneResponseLevel(64 / 255, thickness, offResponse, far, span);
        const on64 = css.backdropToneResponseLevel(64 / 255, thickness, response, far, span);
        const on40 = css.backdropToneResponseLevel(40 / 255, thickness, response, far, span);
        const near64 = css.backdropToneResponseLevel(64 / 255 - 1e-10, thickness, response, far, span);
        fixedJoinPass &&= on64 === old64 && on40 <= old64 &&
          Math.abs(encode(near64) - encode(old64)) * 255 <= 1e-3;
        let runningMax = -Infinity;
        const steps = Math.round((domain.inputCodeMax - domain.inputCodeMin) / domain.stepCode);
        for (let step = 0; step <= steps; step++) {
          const code = domain.inputCodeMin + step * domain.stepCode;
          const tone = toneAt(code / 255);
          const material = css.materialAtBackdrop(profile, "regular", tone, span, nominal, dpr);
          const output = encode(material.level) * 255;
          if (!Number.isFinite(output)) throw new Error("Nonfinite composed response");
          maxRunningDrawdownCode = Math.max(maxRunningDrawdownCode, runningMax - output);
          runningMax = Math.max(runningMax, output);
          inspect(css.lowEndNeutralRequest(sized, tone, thickness, material.adaptation,
            strength, response, far, span),
          { kind: "uniform", endpoint: key(endpoint), span, dpr, inputCode: code });
          samples++;
        }
      }
    }
    // No tone/no sample and policy gates are checked through the actual material owner.
    for (const policy of [nominal, { ...nominal, refraction: "none", frost: "increased", occlusion: "increased" },
      { ...nominal, ambientTint: "reduced" }] as ResolvedMaterialPolicy[]) {
      for (const tone of policy === nominal ? [undefined] : [undefined, toneAt(0)]) {
        standDownPass &&= isDeepStrictEqual(css.materialAtBackdrop(profile, "regular", tone, 160, policy),
          css.materialAtBackdrop(off, "regular", tone, 160, policy));
      }
    }
    for (const [alpha, adaptation, callerStrength, profileStrength] of [
      [0, 0, 1, response.strength], [0.001, 0, 1, response.strength],
      [source.tintAlpha, 0.995, 1, response.strength], [source.tintAlpha, 1, 1, response.strength],
      [source.tintAlpha, 0, 0, response.strength], [source.tintAlpha, 0, 1, 0],
    ]) {
      const input = { ...source, tintAlpha: alpha! };
      const curve = { ...response, strength: profileStrength! };
      standDownPass &&= css.toneRespondedSourceOptics(input, toneAt(0), 1, adaptation!, callerStrength!, curve) === input;
      standDownPass &&= css.lowEndNeutralRequest(input, toneAt(0), 1, adaptation!, callerStrength!, curve) === undefined;
    }
  }
  const structuredCoverage = new Set<string>();
  let structuredHasNegative = false;
  for (const argument of arguments_) {
    const endpoint = configured.find((value) => value.position === argument.position && value.pose === argument.pose)!;
    const tone = toneAt(argument.encodedLuminance, argument.linearLuminance, argument.rgb);
    const material = css.materialAtBackdrop(endpoint.profile, argument.variant, tone, argument.span, nominal, argument.dpr);
    const source = css.sourceOptics(endpoint.profile)[argument.variant];
    const sized = { ...source, tintAlpha: css.sizeOcclusionAlphaAt(
      css.spanGradedTintAlpha(source.tintAlpha, argument.span, endpoint.size, argument.dpr),
      material.thickness, endpoint.size) };
    const request = css.lowEndNeutralRequest(sized, tone, material.thickness, material.adaptation,
      endpoint.strength, endpoint.response, css.sizeToneLevelFar(argument.span, endpoint.size, argument.dpr), argument.span);
    const minimum = inspect(request, { kind: "structured", endpoint: key(endpoint), span: argument.span,
      dpr: argument.dpr, inputCode: argument.encodedLuminance * 255, id: argument.id });
    structuredHasNegative ||= minimum !== undefined && minimum < 0;
    if (request !== undefined && Math.abs(decode(argument.encodedLuminance) - argument.linearLuminance) > 1e-12) {
      structuredCoverage.add(key(argument));
    }
  }
  const requiredCoverage = expected.flatMap((endpoint) => domain.scales.map((dpr) => `${endpoint}:${dpr}`));
  const measured = requiredCoverage.every((entry) => structuredCoverage.has(entry));
  const structuredArgumentPass = measured && !structuredHasNegative;
  const minimum = Number.isFinite(minimumRequestedNeutral) ? minimumRequestedNeutral : null;
  const pass = maxRunningDrawdownCode <= 1e-4 && minimum !== null && minimum >= 0 &&
    fixedJoinPass && standDownPass && structuredArgumentPass;
  return {
    status: !measured || minimum === null ? "UNMEASURED" : pass ? "PASS" : "FAIL",
    domain, samples, maxRunningDrawdownCode, minimumRequestedNeutral: minimum,
    fixedJoinPass, standDownPass, structuredArgumentPass, negativeRequests,
    structuredArgumentIds: arguments_.map(({ id }) => id).sort(),
    structuredArguments: arguments_.map(({ id, candidateSha256, position, pose, dpr, span, role, profile, renderer, scene, variant }) =>
      ({ id, candidateSha256, position, pose, dpr, span, role, profile, renderer, scene, variant })),
    structuredCoverage: [...structuredCoverage].sort(),
    scope: "Numerical eligibility only; measured structured identities are not a claim of complete native identification",
  };
}

export function parseArguments(args: readonly string[]): { cohort: string; out: string } {
  const options: Record<string, string> = {};
  for (let i = 0; i < args.length; i += 2) {
    const name = args[i];
    if (name !== "--cohort" && name !== "--out") throw new Error(`Unknown numerical option: ${name}`);
    const value = args[i + 1];
    if (!value || value.startsWith("--") || options[name]) throw new Error(`Missing or duplicate ${name}`);
    options[name] = value;
  }
  if (!options["--cohort"] || !options["--out"]) throw new Error("Requires --cohort and --out; no partial-domain CLI exists");
  return { cohort: options["--cohort"], out: options["--out"] };
}

async function main(args: readonly string[]) {
  const options = parseArguments(args);
  const cohortPath = inside(ROOT, isAbsolute(options.cohort) ? relative(ROOT, options.cohort) : options.cohort);
  const cohort: unknown = JSON.parse(readFileSync(cohortPath, "utf8"));
  if (!record(cohort) || cohort.schema !== "w50-numerical-cohort-1" || !Array.isArray(cohort.candidates) ||
      cohort.candidates.length !== 2) throw new Error("UNMEASURED: missing complete candidate cohort");
  const { renderer, candidate, documents, sources } = await loadRuntime({ discovery: false });
  const cohortPin = { path: relative(ROOT, cohortPath), sha256: sha(cohortPath) };
  const inputs: Pin[] = [cohortPin];
  const candidateDocuments: (Pin & { position: number })[] = [];
  const endpoints: NumericalEndpoint[] = [];
  const byPosition = new Map<number, string>();
  const withoutChart = (profile: unknown) => record(profile) ? canonical(Object.fromEntries(
    Object.entries(profile).filter(([name]) => !["lowEndStrength", "lowEnd44", "lowEnd96", "lowEnd160"].includes(name)))) : profile;
  for (const raw of cohort.candidates) {
    if (!record(raw) || !FULL_DOMAIN.positions.includes(raw.position as number) || byPosition.has(raw.position as number)) {
      throw new Error("Candidate cohort must contain positions0.25/0.5 exactly once");
    }
    const pin = readPin(ROOT, raw);
    const current = candidate.readCandidateDocument(pin.absolute);
    if (current.document.glassTintAmount !== raw.position) throw new Error("Candidate position differs from cohort");
    inputs.push(pin.pin);
    candidateDocuments.push({ position: raw.position as number, ...pin.pin });
    byPosition.set(raw.position as number, pin.pin.sha256);
    for (const endpoint of Object.values(current.endpoints)) {
      inputs.push({ path: relative(ROOT, endpoint.path), sha256: endpoint.sha256 });
    }
    const shipped = raw.position === 0.25 ? documents.macos27Glass025MaterialProfileDocument
      : documents.macos27MaterialProfileDocument;
    for (const scheme of ["light", "dark"] as const) {
      let resolved = renderer.withMaterialOverrides(renderer.DEFAULT_MATERIAL_PROFILE,
        current.document.active[scheme].patch as MaterialProfilePatch);
      let baseline = renderer.withMaterialOverrides(renderer.DEFAULT_MATERIAL_PROFILE, shipped.active[scheme].patch ?? {});
      for (const pose of FULL_DOMAIN.poses) {
        if (pose === "receded") {
          resolved = renderer.withMaterialOverrides(resolved, current.document.receded[scheme].patch as MaterialProfilePatch);
          baseline = renderer.withMaterialOverrides(baseline, shipped.receded[scheme].patch ?? {});
        }
        if (scheme === "light" ? !isDeepStrictEqual(canonical(resolved), canonical(baseline))
          : !isDeepStrictEqual(withoutChart(resolved), withoutChart(baseline))) {
          throw new Error(`Candidate moves material outside W50 chart scope: ${raw.position} ${pose} ${scheme}`);
        }
        if (scheme === "dark") endpoints.push({ position: raw.position as number, pose, profile: resolved });
      }
    }
  }
  const candidateSha256s = [...byPosition.values()].sort();
  const argumentPin = readPin(ROOT, cohort.structuredArguments);
  const measured = readStructuredArguments(argumentPin.absolute, argumentPin.pin.sha256, candidateSha256s);
  const references = relative(ROOT, resolve(fileURLToPath(new URL("../references.json", import.meta.url))));
  if (measured.references.path !== references) throw new Error("Measured population is not the fixed W50 reference inventory");
  for (const argument of measured.records) {
    if (byPosition.get(argument.position) !== argument.candidateSha256) throw new Error("Measured argument candidate/position mismatch");
  }
  inputs.push(...measured.pins);
  const result = await evaluateNumerical(endpoints, measured.records);
  const pins = [...sources].map(([path, sha256]) => ({ path: relative(ROOT, path), sha256 }))
    .sort((a, b) => a.path.localeCompare(b.path));
  const all = [...new Map([...pins, ...inputs].map((pin) => [pin.path, pin])).values()].sort((a, b) => a.path.localeCompare(b.path));
  verifyPins(ROOT, all);
  const report = { schema: "w50-candidate-numerical-referee-1", candidateSha256s,
    ...result, requiredStructuredArgumentIds: measured.requiredIds,
    producer: { path: relative(ROOT, SELF), sha256: SELF_SHA },
    cohort: cohortPin, argumentManifest: argumentPin.pin, referenceInventory: measured.references,
    candidateDocuments, runtimeSources: pins,
    sources: all, environment: { node: process.version, executable: process.execPath,
      executableSha256: sha(realpathSync(process.execPath)),
      closure: "Permanent Node registerHooks pre-execution source guard; input bytes verified before and after" } };
  writeFileSync(resolve(options.out), `${JSON.stringify(report, null, 2)}\n`, { flag: "wx" });
  process.stdout.write(`${report.status}: ${report.samples} uniform samples; ${report.structuredArguments.length} measured argument identities\n`);
  if (report.status !== "PASS") process.exitCode = 1;
}

if (process.argv[1] && resolve(process.argv[1]) === SELF) {
  main(process.argv.slice(2)).catch((error: unknown) => {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  });
}
