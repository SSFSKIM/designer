/**
 * W40's current matrix is a union, not a rewritten monolith. Raw row slices travel
 * with the parsed objects so a legacy whole-matrix witness stays checkable without
 * reserialising evidence. Scratch matrices retain the ordinary schema-5 boundary.
 */
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { serializeResultCellKey, type CellResult } from "./report";
import { sameFilesystemFile } from "./matrix-write-guard";

export interface MatrixStoreOptions {
  readonly resultsDir?: string;
  readonly matrixPath?: string;
}
export interface Document { readonly path: string; readonly sha256: string }
export interface Entry {
  readonly activeDocumentSha256: string;
  readonly documents: readonly Document[];
  readonly bytes: number;
  readonly sha256: string;
  readonly rowCount: number;
  readonly rowsByProfileKey: Readonly<Record<string, number>>;
  readonly status?: "current" | "retired";
}
export interface Index {
  readonly schemaVersion?: number;
  readonly files: Readonly<Record<string, Entry>>;
  readonly byDocumentSha256: Readonly<Record<string, string | readonly string[]>>;
  readonly sharedReceded?: Readonly<Record<string, readonly string[]>>;
  readonly currentByProfile?: Readonly<Record<string, string>>;
}
interface Owner { readonly file: string; readonly entry: Entry }
const DEFAULT_RESULTS = fileURLToPath(new URL("../results/", import.meta.url));
const rawRows = new WeakMap<CellResult, Buffer>();
const sha = (raw: Buffer) => createHash("sha256").update(raw).digest("hex");
const frozen = (row: CellResult) => row.key.profileKey.startsWith("apple-macos-26.5-");
function fail(message: string): never { throw new Error(`matrix store: ${message}`); }
function sorted(rows: readonly CellResult[]): readonly CellResult[] {
  const keyed = new Map<string, CellResult>();
  for (const row of rows) {
    const key = serializeResultCellKey(row.key);
    if (keyed.has(key)) fail(`duplicate serialized key ${key}`);
    keyed.set(key, row);
  }
  return [...keyed.keys()].sort().map((key) => keyed.get(key)!);
}

/** A brace walk, derived from W30's splitter, preserves each row's original bytes. */
export function readRows(file: string, entry?: Entry): readonly CellResult[] {
  const raw = readFileSync(file);
  if (entry && (raw.length !== entry.bytes || sha(raw) !== entry.sha256)) {
    fail(`${file}: metadata bytes or SHA-256 mismatch`);
  }
  const parsed = JSON.parse(raw.toString("utf8")) as { schemaVersion?: number; cells?: CellResult[] };
  if (parsed.schemaVersion !== 5 || !Array.isArray(parsed.cells)) fail(`${file}: expected schema 5 cells`);
  const cellsKey = raw.indexOf('"cells"');
  let depth = 0, start = 0, rowIndex = 0, quoted = false, escaped = false;
  for (let i = raw.indexOf("[", cellsKey) + 1; i < raw.length; i++) {
    const c = raw[i];
    if (quoted) {
      if (escaped) escaped = false;
      else if (c === 92) escaped = true;
      else if (c === 34) quoted = false;
    } else if (c === 34) quoted = true;
    else if (c === 123 || c === 91) { if (depth++ === 0) start = i; }
    else if (c === 125 || c === 93) {
      if (depth === 0) break;
      if (--depth === 0) {
        const row = parsed.cells[rowIndex++];
        if (!row || typeof row.key?.profileKey !== "string" || typeof row.key.sceneId !== "string") {
          fail(`${file}: malformed row key`);
        }
        rawRows.set(row, raw.subarray(start, i + 1));
      }
    }
  }
  if (rowIndex !== parsed.cells.length) fail(`${file}: raw row span count differs`);
  const rows = sorted(parsed.cells);
  if (entry) validateOwnership(file, rows, entry);
  return rows;
}
export function documents(row: CellResult): { active: Document; receded?: Document } {
  const path = row.key.web.capturePath;
  const matches = [...path.matchAll(/(materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})(?![0-9a-f])/g)];
  const active = matches.filter((m) => m[1] === "materialProfile");
  const receded = matches.filter((m) => m[1] === "recededProfile");
  if (active.length !== 1 || receded.length > 1 || matches.length !== (path.match(/sha256:/g) ?? []).length) {
    fail(`incomplete document clauses in ${path}`);
  }
  return { active: { path: active[0]![2]!, sha256: active[0]![3]! },
    ...(receded[0] ? { receded: { path: receded[0][2]!, sha256: receded[0][3]! } } : {}) };
}
function recededHash(entry: Entry): string | undefined {
  const others = entry.documents.filter((d) => d.sha256 !== entry.activeDocumentSha256);
  if (others.length > 1 || entry.documents.length < 1 || entry.documents.length > 2 ||
      entry.documents.filter((d) => d.sha256 === entry.activeDocumentSha256).length !== 1) {
    fail("generation must name one active and at most one receded document");
  }
  return others[0]?.sha256;
}
function validateOwnership(file: string, rows: readonly CellResult[], entry: Entry) {
  const receded = recededHash(entry);
  const counts: Record<string, number> = {};
  const expected = new Set(entry.documents.map((d) => `${d.path}|${d.sha256}`));
  for (const row of rows) {
    if (frozen(row)) fail(`${file}: frozen row in generation`);
    const named = documents(row);
    if (named.active.sha256 !== entry.activeDocumentSha256 || named.receded?.sha256 !== receded ||
        !expected.has(`${named.active.path}|${named.active.sha256}`) ||
        (named.receded && !expected.has(`${named.receded.path}|${named.receded.sha256}`))) {
      fail(`${file}: row ownership or document clause completeness differs`);
    }
    counts[row.key.profileKey] = (counts[row.key.profileKey] ?? 0) + 1;
  }
  if (rows.length !== entry.rowCount || JSON.stringify(Object.entries(counts).sort()) !==
      JSON.stringify(Object.entries(entry.rowsByProfileKey).sort())) fail(`${file}: row metadata differs`);
}
export function readIndex(results: string, directory: string): Index | undefined {
  const file = join(results, directory, "index.json");
  if (!existsSync(file)) return undefined;
  const index = JSON.parse(readFileSync(file, "utf8")) as Index;
  if (!index.files || !index.byDocumentSha256 ||
      (directory === "generations" && (index.schemaVersion !== 1 || !index.currentByProfile))) {
    fail(`${file}: invalid index schema`);
  }
  const actual = new Map<string, Set<string>>();
  for (const [name, entry] of Object.entries(index.files)) {
    if (!/^[0-9a-f]{12}(?:-[0-9a-f]{12})?\.json$/.test(name)) fail(`${file}: invalid generation filename`);
    recededHash(entry);
    if (directory === "generations" && entry.status !== "current" && entry.status !== "retired") fail(`${file}: invalid status`);
    for (const doc of entry.documents) {
      if (!/^[0-9a-f]{12}$/.test(doc.sha256)) fail(`${file}: invalid document hash`);
      const owners = actual.get(doc.sha256) ?? new Set<string>(); owners.add(name); actual.set(doc.sha256, owners);
    }
  }
  const declared = new Map<string, Set<string>>();
  for (const [hash, names] of Object.entries(index.byDocumentSha256)) {
    declared.set(hash, new Set(typeof names === "string" ? [names] : names));
  }
  for (const [hash, names] of Object.entries(index.sharedReceded ?? {})) {
    const owners = declared.get(hash) ?? new Set<string>();
    for (const name of names) owners.add(name);
    declared.set(hash, owners);
  }
  if (actual.size !== declared.size || [...actual].some(([hash, names]) => {
    const aliases = declared.get(hash);
    return !aliases || names.size !== aliases.size || [...names].some((name) => !aliases.has(name));
  })) fail(`${file}: document aliases do not enumerate every owner`);
  return index;
}
function resultsPath(options: MatrixStoreOptions): string { return resolve(options.resultsDir ?? DEFAULT_RESULTS); }

export function loadCurrentRows(options: MatrixStoreOptions = {}): readonly CellResult[] {
  const results = resultsPath(options);
  const explicit = options.matrixPath ?? process.env["VITREA_MATRIX_PATH"];
  const matrix = join(results, "matrix.json");
  if (explicit && !sameFilesystemFile(resolve(explicit), matrix)) {
    return readRows(resolve(explicit));
  }
  const rows = readRows(matrix);
  const index = readIndex(results, "generations");
  if (!index) return rows;
  if (rows.some((row) => !frozen(row))) fail("non-frozen row in frozen matrix file");
  for (const row of rows) documents(row);
  const selected = index.currentByProfile!;
  const filenames = new Set(Object.values(selected));
  const current: CellResult[] = [...rows];
  for (const [name, entry] of Object.entries(index.files)) {
    const chosen = filenames.has(name);
    if (chosen !== (entry.status === "current")) fail(`${name}: current selection/status differs`);
    if (!chosen) continue;
    for (const profile of Object.keys(entry.rowsByProfileKey)) {
      if (selected[profile] !== name) fail(`${name}: incomplete current profile selection`);
    }
    current.push(...readRows(join(results, "generations", name), entry));
  }
  for (const [profile, name] of Object.entries(selected)) {
    if (!index.files[name]?.rowsByProfileKey[profile]) fail(`${profile}: missing current generation`);
  }
  return sorted(current);
}
export function loadCurrentProfile(profileKey: string, options: MatrixStoreOptions = {}): readonly CellResult[] {
  return loadCurrentRows(options).filter((row) => row.key.profileKey === profileKey);
}
function owners(results: string): Owner[] {
  const out: Owner[] = [];
  for (const directory of ["generations", "superseded"]) {
    const index = readIndex(results, directory);
    for (const [name, entry] of Object.entries(index?.files ?? {})) out.push({ file: join(results, directory, name), entry });
  }
  return out;
}
/** An omitted qualifier resolves an alias; null explicitly selects no receded document. */
export function loadGeneration(active: string, receded?: string | null, options: MatrixStoreOptions = {}): readonly CellResult[] {
  const results = resultsPath(options);
  const found = owners(results).filter(({ entry }) => receded === undefined
    ? entry.documents.some((doc) => doc.sha256 === active)
    : entry.activeDocumentSha256 === active && recededHash(entry) === (receded ?? undefined));
  if (found.length > 1) fail(`ambiguous document ${active}; qualify the active/receded pair`);
  if (found[0]) return readRows(found[0].file, found[0].entry);
  // Frozen generations predate the indexed layout; their documents still name them.
  const frozenRows = readRows(join(results, "matrix.json")).filter((row) => {
    const named = documents(row);
    return named.active.sha256 === active && (receded === undefined || named.receded?.sha256 === (receded ?? undefined));
  });
  const identities = new Set(frozenRows.map((row) => documents(row).receded?.sha256 ?? "none"));
  if (identities.size > 1) fail(`ambiguous document ${active}; qualify the active/receded pair`);
  if (!frozenRows.length) fail(`no generation owns document ${active}`);
  return frozenRows;
}
/** History is opt-in: no current reader pays to load the archive. */
export function* iterateRecordedRows(options: MatrixStoreOptions = {}): IterableIterator<CellResult> {
  const results = resultsPath(options);
  yield* readRows(join(results, "matrix.json"));
  for (const owner of owners(results)) yield* readRows(owner.file, owner.entry);
}
/** Stream the historical pretty-printed envelope, never a regenerated matrix file. */
export function legacyEnvelopeDigest(rows: readonly CellResult[]): string {
  const ordered = sorted(rows);
  const hash = createHash("sha256");
  if (ordered.length === 0) return hash.update('{\n  "schemaVersion": 5,\n  "cells": []\n}\n').digest("hex");
  hash.update('{\n  "schemaVersion": 5,\n  "cells": [\n    ');
  ordered.forEach((row, i) => {
    const raw = rawRows.get(row);
    if (!raw) fail("legacy envelope requires rows loaded with their raw bytes");
    if (i) hash.update(",\n    ");
    hash.update(raw);
  });
  hash.update("\n  ]\n}\n");
  return hash.digest("hex");
}

/** Preserve recorded row slices in the splitter's original, key-ordered envelope. */
export function generationEnvelope(rows: readonly CellResult[]): Buffer {
  const ordered = sorted(rows);
  if (!ordered.length) return Buffer.from('{\n  "schemaVersion": 5,\n  "cells": []\n}\n');
  return Buffer.concat([Buffer.from('{\n  "schemaVersion": 5,\n  "cells": [\n    '),
    ...ordered.flatMap((row, i) => {
      const raw = rawRows.get(row);
      if (!raw) fail("generation envelope requires raw row bytes");
      return i ? [Buffer.from(",\n    "), raw] : [raw];
    }), Buffer.from("\n  ]\n}\n")]);
}
