/**
 * The glass position a row was drawn at, derived from its documents and never from its stamp
 * (W43 G0 review, finding 1; charter `2026-10-01-w43-glass-0-25-generation.md`, X45).
 *
 * A row's `capturePath` names the documents that drew it by path and hash. The hash is what
 * makes the path evidence: each document is read, its bytes checked against the hash the row
 * carries, and its own `profileKey` read for the position. A strict row's documents are the
 * profile documents `--material-profile` and `--receded-profile` named; a candidate row's is
 * its declaration, whose four endpoint files are checked against the hashes it records. The
 * `crossPosition=` clause is then a label whose only job is to say what the documents already
 * say; a label that disagrees with them is refused, never believed.
 *
 * Node code (it reads files), so it is kept out of `material-selection.ts`, which the scene
 * page imports.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

import {
  crossPositionClause,
  glassToken,
  keyPosition,
  type CrossPositionSource,
} from "./material-selection";

export type RowPosition =
  | {
      readonly kind: "positioned";
      readonly source: CrossPositionSource;
      readonly glass: number | undefined;
    }
  | { readonly kind: "unpositioned"; readonly why: string };

const sha = (bytes: Buffer): string => createHash("sha256").update(bytes).digest("hex");

/** A document's bytes, refused unless they hash to what the row recorded. */
function verified(path: string, expected: string, what: string): Record<string, unknown> {
  let bytes: Buffer;
  try {
    bytes = readFileSync(path);
  } catch {
    throw new Error(`${what} ${path} is not on disk, so the row's position cannot be derived`);
  }
  const actual = sha(bytes);
  if (!actual.startsWith(expected)) {
    throw new Error(`${what} ${path} hashes to ${actual.slice(0, expected.length)}, and the row ` +
      `records ${expected}, so the row's position cannot be derived from it`);
  }
  return JSON.parse(bytes.toString("utf8")) as Record<string, unknown>;
}

/** The one glass position a set of keys names, or a refusal when they disagree or do not parse. */
function agreedGlass(keys: readonly string[], what: string): number | undefined {
  const glasses = new Set<number | undefined>();
  for (const key of keys) {
    const position = keyPosition(key);
    if (position === undefined) throw new Error(`${what}: profileKey '${key}' does not parse`);
    glasses.add(position.glass);
  }
  if (glasses.size !== 1) throw new Error(`${what}: its documents name more than one glass position`);
  return [...glasses][0];
}

/**
 * The position the documents a `capturePath` names were drawn at. Throws when a named
 * document is missing, does not hash to the row's record, or states a position its siblings
 * contradict; returns `unpositioned` for a capture that names no keyed document (the runtime's
 * default, or a bare patch), which has no declared position to compare.
 */
export function capturePathPosition(capturePath: string, repoRoot: string): RowPosition {
  const candidate = /materialProfile=candidate candidateDocument=(\S+) declarationSha256=([0-9a-f]{12})/
    .exec(capturePath);
  if (candidate !== null) {
    const path = resolve(repoRoot, candidate[1]!);
    const declaration = verified(path, candidate[2]!, "the candidate declaration");
    const endpoints = Object.entries(
      (declaration["endpoints"] ?? {}) as Record<string, { path: string; sha256: string }>);
    if (endpoints.length !== 4) {
      throw new Error(`the candidate declaration ${path} names no four endpoints`);
    }
    const keys = endpoints.map(([slot, entry]) => {
      const file = resolve(dirname(path), entry.path);
      const key = verified(file, entry.sha256, `candidate ${slot}`)["profileKey"];
      if (typeof key !== "string") throw new Error(`candidate ${slot} names no profileKey`);
      return key;
    });
    return { kind: "positioned", source: "candidate", glass: agreedGlass(keys, `candidate ${path}`) };
  }
  const clauses =
    [...capturePath.matchAll(/(materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})/g)];
  if (clauses.length === 0) return { kind: "unpositioned", why: "it names no material document" };
  const keys: string[] = [];
  for (const [, role, shown, hash] of clauses) {
    const key = verified(resolve(repoRoot, shown!), hash!, `the ${role} document`)["profileKey"];
    if (typeof key !== "string") {
      if (role === "materialProfile") return { kind: "unpositioned", why: `${shown} is a bare patch` };
      throw new Error(`the receded document ${shown} names no profileKey`);
    }
    keys.push(key);
  }
  return { kind: "positioned", source: "shipped", glass: agreedGlass(keys, "the row") };
}

/** The `crossPosition=` clause a `capturePath` carries, with its leading separator, if any. */
export function stampOf(capturePath: string): string | undefined {
  const match = /, crossPosition=[^,\s]+/.exec(capturePath);
  return match?.[0];
}

/**
 * Whether a row may be written where it is going, judged from its documents.
 *
 * - Documents at the row profile's glass position: admitted, and refused if stamped, because
 *   a stamp there is false.
 * - Documents at another position: refused outright at an authoritative destination (a stage,
 *   a publication); refused in scratch unless the run declared `--cross-position`; and under
 *   the flag, admitted only when the capture's stamp is the clause the documents derive. A
 *   capture taken without the stamp is refused rather than re-stamped, so every stamped row is
 *   one whose capture was taken as a cross-position reading.
 * - No keyed document: nothing to compare, refused only if stamped or flagged.
 * Returns the refusal, or `undefined`.
 */
export function crossPositionVerdict(
  row: { readonly profileKey: string; readonly capturePath: string },
  options: { readonly crossPosition: boolean; readonly authoritative: boolean; readonly repoRoot: string },
): string | undefined {
  let position: RowPosition;
  try {
    position = capturePathPosition(row.capturePath, options.repoRoot);
  } catch (error) {
    return error instanceof Error ? error.message : String(error);
  }
  const stamp = stampOf(row.capturePath);
  if (position.kind === "unpositioned") {
    if (stamp !== undefined || options.crossPosition) {
      return `the capture carries or asks for a cross-position stamp, and ${position.why}, so no ` +
        "position can be derived for it";
    }
    return undefined;
  }
  const rowGlass = keyPosition(row.profileKey)?.glass;
  if (position.glass === rowGlass) {
    return stamp === undefined ? undefined
      : `the capture is stamped${stamp}, and its documents are at the profile's own glass ` +
        `${glassToken(rowGlass)}, so the stamp is false`;
  }
  const pair = `its documents are at glass ${glassToken(position.glass)} and the profile ` +
    `${row.profileKey} at glass ${glassToken(rowGlass)}`;
  if (options.authoritative) {
    return `${pair}; a cross-position row never enters a stage or a publication`;
  }
  if (!options.crossPosition) return `${pair}; declare it with --cross-position, into scratch`;
  const expected = crossPositionClause(position.source, position.glass, glassToken(rowGlass));
  if (stamp !== expected) {
    return `${pair}, so the capture must carry${expected}, and it carries ` +
      `${stamp === undefined ? "no stamp" : stamp.slice(2)}; re-capture it with --cross-position`;
  }
  return undefined;
}
