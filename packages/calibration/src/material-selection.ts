/**
 * Which material document a calibration capture draws, in two declared modes (W43 G0 (f);
 * charter `2026-10-01-w43-glass-0-25-generation.md`, Surprises 1, X45).
 *
 * Until W43 the scene page picked the shipped document whose `platform` matched the OS token
 * of the injected profile key, and nothing else. That was enough while macOS 27 had one
 * measured material. Once a second slider position ships, the OS token alone still returns
 * the 0.5 document, so a 0.25 read would recede with the 0.5 receded endpoint and price the
 * CSS tier with the 0.5 crossing: the "one seam" defect W29 G4 closed, one axis further on.
 *
 * **Strict shipped mode**, for every read of a shipped material: the page selects a shipped
 * document by the pair (OS, glass position) the profile key names, and refuses a pair no
 * shipped document carries and a pair more than one carries. A document's position is read
 * from what it states about itself: its `platform`, the glass token of every endpoint key it
 * names, and `glassTintAmount` where it carries one (Decision Log 1's readout). A document
 * whose statements disagree has no position, and a registry holding one is refused rather
 * than searched.
 *
 * **Candidate mode**, for every fit and pre-seal read: the driver declares a complete
 * document of its own, four endpoints and a CSS mapping, and the page builds the root from
 * that document alone. `validateCandidateDocument` is the page's half of the refusals; the
 * driver's half (file hashes, resolved digests over the unmoved runtime default, the mapping
 * hash) is in `scripts/candidate-document.ts`, which also runs this one.
 *
 * Pure and DOM-free on purpose: the page, the driver and the unit suite import the same
 * functions, and the shipped registry is a parameter, so the refusals are testable against
 * a synthetic ambiguous registry as well as against the real one.
 */

import { parseProfileKey } from "./profile";

export type MaterialScheme = "light" | "dark";
export const MATERIAL_SCHEMES: readonly MaterialScheme[] = ["light", "dark"];
export const MATERIAL_POSES = ["active", "receded"] as const;
export type MaterialPose = (typeof MATERIAL_POSES)[number];

/** The structural part of `GlassMaterialProfileDocument` these rules read. */
export interface MaterialEndpointLike {
  readonly profileKey?: string;
  readonly patch?: object;
  readonly resolvedMaterialSha256?: string;
}

export interface MaterialDocumentLike {
  readonly name: string;
  readonly platform: string;
  readonly glassTintAmount?: number;
  readonly active: Readonly<Record<MaterialScheme, MaterialEndpointLike>>;
  readonly receded: Readonly<Record<MaterialScheme, MaterialEndpointLike>>;
  readonly cssTierMapping: object;
}

/** Where a document sits: its OS version and its glass position, absent before macOS 27. */
export interface MaterialPosition {
  readonly osVersion: string;
  readonly glass: number | undefined;
}

/** The suffix a receded endpoint's key carries over the active key of its scheme. */
export const RECEDED_SUFFIX = "-receded";

const describe = (position: MaterialPosition): string =>
  `macOS ${position.osVersion}, ${position.glass === undefined ? "no glass token" : `glass ${position.glass}`}`;

/**
 * The (OS, glass) pair an endpoint key names, with the receded suffix taken off.
 * `undefined` for a key the profile grammar does not parse.
 */
export function keyPosition(profileKey: string): (MaterialPosition & { scheme: MaterialScheme }) | undefined {
  const stem = profileKey.endsWith(RECEDED_SUFFIX)
    ? profileKey.slice(0, -RECEDED_SUFFIX.length)
    : profileKey;
  const parsed = parseProfileKey(stem);
  if (parsed === null || parsed.platform !== "macos") return undefined;
  return { osVersion: parsed.osVersion, glass: parsed.glass, scheme: parsed.colorScheme };
}

const platformVersion = (platform: string): string | undefined =>
  /^macOS (\d+\.\d+)$/.exec(platform)?.[1];

const endpoints = (document: MaterialDocumentLike) =>
  MATERIAL_POSES.flatMap((pose) =>
    MATERIAL_SCHEMES.map((scheme) => ({
      pose,
      scheme,
      slot: `${pose}.${scheme}`,
      endpoint: document[pose][scheme],
    })),
  );

/**
 * A document's position from its own statements, or a reason it has none.
 *
 * Every statement must agree: the platform's version with every endpoint key's OS token, and
 * every key's glass token with every other and with `glassTintAmount`. A document with no key
 * at all states no glass position, which is what the macOS 26.5 receded endpoints are.
 */
export function documentPosition(document: MaterialDocumentLike): MaterialPosition | string {
  const osVersion = platformVersion(document.platform);
  if (osVersion === undefined) return `platform '${document.platform}' is not 'macOS <major>.<minor>'`;
  const glasses = new Set<number | undefined>();
  for (const { slot, endpoint } of endpoints(document)) {
    if (endpoint.profileKey === undefined) continue;
    const position = keyPosition(endpoint.profileKey);
    if (position === undefined) return `${slot} key '${endpoint.profileKey}' does not parse`;
    if (position.osVersion !== osVersion) {
      return `${slot} key '${endpoint.profileKey}' names macOS ${position.osVersion}, the platform ${osVersion}`;
    }
    glasses.add(position.glass);
  }
  if (document.glassTintAmount !== undefined) glasses.add(document.glassTintAmount);
  if (glasses.size > 1) {
    return `its keys and readout name more than one glass position (${[...glasses].map(String).join(", ")})`;
  }
  return { osVersion, glass: [...glasses][0] };
}

/**
 * Strict shipped mode: the one shipped document at the pair the profile key names.
 *
 * Refuses an unparseable key, a pair no shipped document carries, a pair more than one
 * carries, and a registry with a document whose position cannot be read.
 */
export function selectShippedDocument<D extends MaterialDocumentLike>(
  profileKey: string,
  shipped: readonly D[],
): D {
  const wanted = keyPosition(profileKey);
  if (wanted === undefined) {
    throw new Error(
      `strict shipped mode: the material profile key '${profileKey}' does not parse as a macOS ` +
        `profile key, so it names no (OS, glass) pair to select a shipped document by`,
    );
  }
  const positions = shipped.map((document) => ({ document, position: documentPosition(document) }));
  const unreadable = positions.filter((p) => typeof p.position === "string");
  if (unreadable.length > 0) {
    throw new Error(
      `strict shipped mode: the shipped registry holds a document with no readable position ` +
        `(${unreadable.map((p) => `${p.document.name}: ${String(p.position)}`).join("; ")}), so ` +
        `no selection from it can be unambiguous`,
    );
  }
  const matches = positions.filter(({ position }) =>
    typeof position !== "string" &&
    position.osVersion === wanted.osVersion && position.glass === wanted.glass);
  if (matches.length === 0) {
    throw new Error(
      `strict shipped mode: '${profileKey}' names (${describe(wanted)}), and ` +
        `@vitreajs/vitrea-web ships no material at that pair (it ships ` +
        `${positions.map((p) => `${p.document.name} at ${describe(p.position as MaterialPosition)}`).join("; ")}). ` +
        `A patch over another position's document is not the material this profile records; ` +
        `read an unshipped material through candidate mode`,
    );
  }
  if (matches.length > 1) {
    throw new Error(
      `strict shipped mode: '${profileKey}' names (${describe(wanted)}), and ` +
        `${matches.length} shipped documents sit there (${matches.map((m) => m.document.name).join(", ")}), ` +
        `so the pair does not say which one this capture is read against`,
    );
  }
  return matches[0]!.document;
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === "object" && !Array.isArray(value);

/**
 * Candidate mode's page-side refusals, returned as a list so every defect is named at once.
 * Empty means the candidate may be drawn.
 *
 * - **Partial:** every endpoint has a key, a non-empty patch and a sixteen-hex resolved
 *   digest; the CSS mapping is a non-empty record; the name, platform and declared position
 *   are present. A candidate missing any of these would draw part of a shipped or default
 *   material under the candidate's name.
 * - **Glass token:** every key's glass token equals the declared `glassTintAmount`, and its
 *   OS token the platform's. Each key's scheme matches its slot, and each receded key is a
 *   receded key.
 * - **Names a shipped document:** neither the name nor any endpoint key is a shipped
 *   document's. A shipped material is read in strict mode, where the runtime's own document
 *   draws; a candidate under its name would be a second, unchecked copy of it.
 */
export function candidateDocumentRefusals(
  candidate: MaterialDocumentLike,
  shipped: readonly MaterialDocumentLike[],
): string[] {
  const problems: string[] = [];
  if (typeof candidate.name !== "string" || candidate.name === "") problems.push("partial: no name");
  const osVersion = typeof candidate.platform === "string" ? platformVersion(candidate.platform) : undefined;
  if (osVersion === undefined) problems.push(`partial: platform '${String(candidate.platform)}' is not 'macOS <major>.<minor>'`);
  const glass = candidate.glassTintAmount;
  if (typeof glass !== "number" || !Number.isFinite(glass) || glass < 0 || glass > 1) {
    problems.push(`partial: no declared position (glassTintAmount ${String(glass)}, a number in [0, 1])`);
  }
  if (!isRecord(candidate.cssTierMapping) || Object.keys(candidate.cssTierMapping).length === 0) {
    problems.push("partial: no CSS tier mapping");
  }
  for (const pose of MATERIAL_POSES) {
    for (const scheme of MATERIAL_SCHEMES) {
      const slot = `${pose}.${scheme}`;
      const endpoint = isRecord(candidate[pose]) ? (candidate[pose] as Record<string, unknown>)[scheme] : undefined;
      if (!isRecord(endpoint)) {
        problems.push(`partial: no ${slot} endpoint`);
        continue;
      }
      const { profileKey, patch, resolvedMaterialSha256 } = endpoint as MaterialEndpointLike;
      if (!isRecord(patch) || Object.keys(patch).length === 0) problems.push(`partial: ${slot} has no patch`);
      if (typeof resolvedMaterialSha256 !== "string" || !/^[0-9a-f]{16}$/.test(resolvedMaterialSha256)) {
        problems.push(`partial: ${slot} has no sixteen-hex resolvedMaterialSha256`);
      }
      if (typeof profileKey !== "string") {
        problems.push(`partial: ${slot} has no profileKey`);
        continue;
      }
      const position = keyPosition(profileKey);
      if (position === undefined) {
        problems.push(`${slot} key '${profileKey}' does not parse as a macOS profile key`);
        continue;
      }
      if (position.glass !== glass) {
        problems.push(
          `glass token: ${slot} key '${profileKey}' names glass ${String(position.glass)}, ` +
            `the candidate declares ${String(glass)}`,
        );
      }
      if (osVersion !== undefined && position.osVersion !== osVersion) {
        problems.push(`${slot} key '${profileKey}' names macOS ${position.osVersion}, the platform ${osVersion}`);
      }
      if (position.scheme !== scheme) problems.push(`${slot} key '${profileKey}' is a ${position.scheme} key`);
      if ((pose === "receded") !== profileKey.endsWith(RECEDED_SUFFIX)) {
        problems.push(`${slot} key '${profileKey}' ${pose === "receded" ? "is not" : "is"} a receded key`);
      }
    }
  }
  const shippedNames = new Set(shipped.map((document) => document.name));
  const shippedKeys = new Set(
    shipped.flatMap((document) => endpoints(document).map((e) => e.endpoint.profileKey))
      .filter((key): key is string => key !== undefined),
  );
  if (shippedNames.has(candidate.name)) {
    problems.push(`names a shipped document: '${candidate.name}' is a shipped document's name`);
  }
  for (const pose of MATERIAL_POSES) {
    for (const scheme of MATERIAL_SCHEMES) {
      const key = (candidate[pose]?.[scheme] as MaterialEndpointLike | undefined)?.profileKey;
      if (key !== undefined && shippedKeys.has(key)) {
        problems.push(`names a shipped document: ${pose}.${scheme} key '${key}' is a shipped endpoint's`);
      }
    }
  }
  return problems;
}

/** The same refusals, thrown: what the page and the driver call before anything draws. */
export function validateCandidateDocument(
  candidate: MaterialDocumentLike,
  shipped: readonly MaterialDocumentLike[],
): void {
  const problems = candidateDocumentRefusals(candidate, shipped);
  if (problems.length > 0) {
    throw new Error(`candidate mode refuses this document: ${problems.join("; ")}`);
  }
}

/**
 * A candidate read against fixtures at another glass position, refused unless declared
 * (W43 G0 (f), the parent's ruling on X45).
 *
 * A candidate at one position measured against native fixtures at another is a comparison
 * between two materials, never a fit of either, and nothing in a row would otherwise say so
 * beyond two numbers in two strings. So a run is one of two things, declared up front: every
 * profile at the candidate's position, or, under `--cross-position`, every profile at another
 * one, each output stamped. The flag over a same-position profile is refused too, because the
 * stamp it writes would be false. Returns the refusal, or `undefined`.
 */
export function crossPositionRefusal(
  candidateGlass: number,
  profileKeys: readonly string[],
  crossPosition: boolean,
): string | undefined {
  const glassOf = (key: string): number | undefined => keyPosition(key)?.glass;
  const same = profileKeys.filter((key) => glassOf(key) === candidateGlass);
  const other = profileKeys.filter((key) => glassOf(key) !== candidateGlass);
  if (!crossPosition && other.length > 0) {
    return (
      `the candidate is at glass ${candidateGlass} and is read against ` +
      `${other.map((k) => `${k} (glass ${String(glassOf(k) ?? "none")})`).join(", ")}. A ` +
      `cross-position reading is a comparison between two materials; declare it with ` +
      `--cross-position, which stamps every output, or select profiles at glass ${candidateGlass}`
    );
  }
  if (crossPosition && same.length > 0) {
    return (
      `--cross-position was declared, and ${same.join(", ")} ${same.length === 1 ? "is" : "are"} at ` +
      `the candidate's own glass ${candidateGlass}, so the stamp would be false there; run the ` +
      `same-position profiles without the flag`
    );
  }
  return undefined;
}

/** The `capturePath` clause a cross-position output carries, after the candidate's own. */
export function crossPositionClause(candidateGlass: number, againstGlass: string): string {
  return `, crossPosition=candidate-glass${candidateGlass}-against-glass${againstGlass}`;
}

/**
 * How a capture's `capturePath` names a candidate, so every output carries the stamp.
 *
 * It replaces the `materialProfile=` clause rather than following it, and its hash is not
 * written as a `materialProfile=… sha256:` clause, so a candidate row can never be read as a
 * row of a shipped generation by the document-clause parser in `matrix-store.ts`.
 */
export function candidateMaterialLabel(stamp: {
  readonly declaration: string;
  readonly sha256: string;
  readonly name: string;
  readonly glassTintAmount: number;
}): string {
  return (
    `materialProfile=candidate candidateDocument=${stamp.declaration} ` +
    `declarationSha256=${stamp.sha256} name=${stamp.name} glassTintAmount=${stamp.glassTintAmount}`
  );
}
