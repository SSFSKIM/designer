/** A declaration precedes measurement. Presence means every named fixture, not one row per set. */
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { assertScratchDestination } from "./matrix-write-guard";
import { documents, generationEnvelope, iterateRecordedRows, loadCurrentRows, readIndex,
  readRows, type Document, type Entry, type Index } from "./matrix-store";
import { serializeResultCellKey, type CellResult } from "./report";

const PACKAGE = fileURLToPath(new URL("../", import.meta.url));
const REPO_ROOT = resolve(PACKAGE, "../..");
const REFERENCE = resolve(REPO_ROOT, "apps/reference-apple");
const sha = (raw: Buffer) => createHash("sha256").update(raw).digest("hex");
export interface Membership {
  readonly schemaVersion: 1;
  readonly profiles: readonly string[];
  readonly tiers: readonly string[];
  readonly sets: readonly string[];
  readonly active: Document;
  readonly receded?: Document;
  readonly cells: readonly { profileKey: string; renderer: string; fixtureSet: string; sceneId: string }[];
}
function fail(message: string): never { throw new Error(`generation: ${message}`); }
function json(path: string): unknown { return JSON.parse(readFileSync(path, "utf8")); }
/** Match capture-web's document labels so measured rows can enter a declared stage. */
function document(path: string): Document {
  const absolute = resolve(path);
  const shown = relative(REPO_ROOT, absolute);
  return { path: shown.startsWith("..") ? absolute : shown,
    sha256: sha(readFileSync(absolute)).slice(0, 12) };
}
function unique(values: readonly string[], label: string) {
  if (!values.length || new Set(values).size !== values.length || values.some((s) => !s)) {
    fail(`declare nonempty unique ${label}`);
  }
}
function declaredCells(options: Pick<Membership, "profiles" | "tiers" | "sets">): Membership["cells"] {
  unique(options.profiles, "profiles"); unique(options.tiers, "tiers"); unique(options.sets, "sets");
  if (options.profiles.some((p) => !p.startsWith("apple-macos-27."))) fail("only macOS 27 generations publish");
  if (options.tiers.some((t) => !["webgpu", "css"].includes(t))) fail("unknown renderer");
  const spec = json(join(REFERENCE, "scenes.json")) as { scenes: { id: string }[]; split: Record<string, string[]> };
  const manifest = json(join(REFERENCE, "fixtures/manifest.json")) as {
    profiles: { profileKey: string; fixtures: { sceneId: string; fixtureSet: string }[] }[];
  };
  const cells: Membership["cells"][number][] = [];
  for (const profileKey of options.profiles) {
    const profile = manifest.profiles.find((p) => p.profileKey === profileKey);
    if (!profile) fail(`profile absent from canonical fixture manifest: ${profileKey}`);
    for (const fixtureSet of options.sets) {
      const fixtures = profile.fixtures.filter((f) => f.fixtureSet === fixtureSet);
      if (!fixtures.length) fail(`no ${fixtureSet} fixtures for ${profileKey}`);
      for (const fixture of fixtures) {
        if (!spec.scenes.some((s) => s.id === fixture.sceneId) || !spec.split[fixtureSet]?.includes(fixture.sceneId)) {
          fail(`fixture not in canonical scene membership: ${fixture.sceneId}`);
        }
        for (const renderer of options.tiers) cells.push({ profileKey, renderer, fixtureSet, sceneId: fixture.sceneId });
      }
    }
  }
  return cells;
}
export function createStage(directory: string, options: {
  profiles: readonly string[]; tiers: readonly string[]; sets: readonly string[];
  active: string; receded?: string;
}): Membership {
  const path = resolve(directory);
  assertScratchDestination(join(path, "membership.json"));
  assertScratchDestination(join(path, "matrix.json"));
  if (existsSync(path)) fail("stage already exists; membership cannot be redeclared");
  const cells = declaredCells(options);
  const membership: Membership = { schemaVersion: 1, profiles: options.profiles,
    tiers: options.tiers, sets: options.sets, active: document(options.active),
    ...(options.receded ? { receded: document(options.receded) } : {}), cells };
  mkdirSync(path, { recursive: true });
  writeFileSync(join(path, "membership.json"), `${JSON.stringify(membership, null, 2)}\n`, { flag: "wx" });
  return membership;
}
export function readMembership(directory: string): Membership {
  const path = join(resolve(directory), "membership.json");
  assertScratchDestination(path);
  const m = json(path) as Membership;
  if (m.schemaVersion !== 1 || !Array.isArray(m.cells) || !m.cells.length) fail("invalid membership");
  const expected = declaredCells(m);
  if (JSON.stringify(m.cells.map(memberKey).sort()) !== JSON.stringify(expected.map(memberKey).sort())) {
    fail("declared cells differ from canonical profile, tier and set membership");
  }
  for (const d of [m.active, ...(m.receded ? [m.receded] : [])]) {
    if (!/^[0-9a-f]{12}$/.test(d.sha256) || document(resolve(REPO_ROOT, d.path)).sha256 !== d.sha256) {
      fail(`document digest differs from declaration: ${d.path}`);
    }
  }
  return m;
}
const memberKey = (c: Membership["cells"][number]) => JSON.stringify([c.profileKey, c.renderer, c.fixtureSet, c.sceneId]);
export function validateStageRows(directory: string, rows: readonly CellResult[]) {
  const m = readMembership(directory);
  const expected = new Set(m.cells.map(memberKey));
  if (expected.size !== m.cells.length) fail("duplicate declared member");
  const seen = new Set<string>();
  for (const row of rows) {
    const key = memberKey({ profileKey: row.key.profileKey, renderer: row.key.web.renderer,
      fixtureSet: row.fixtureSet, sceneId: row.key.sceneId });
    if (!expected.has(key)) fail(`row outside declared membership: ${key}`);
    if (seen.has(key)) fail(`multiple rows for declared member: ${key}`);
    seen.add(key);
    const named = documents(row);
    if (JSON.stringify(named.active) !== JSON.stringify(m.active) ||
        JSON.stringify(named.receded) !== JSON.stringify(m.receded)) fail("row document digests differ from declaration");
  }
  return { membership: m, declared: expected.size, present: seen.size,
    missing: [...expected].filter((k) => !seen.has(k)).length };
}
export function stageMatrixPath(directory: string, explicit?: string): string {
  const path = join(resolve(directory), "matrix.json");
  if (explicit && resolve(explicit) !== path) fail("--out-matrix must name the stage's matrix.json");
  assertScratchDestination(path);
  return path;
}
export function stageStatus(directory: string) {
  const path = stageMatrixPath(directory);
  return validateStageRows(directory, existsSync(path) ? readRows(path) : []);
}
/** Preflight a compare invocation before it captures, and validate every resulting row before writing. */
export function assertStageRun(directory: string, options: {
  profileKeys?: readonly string[] | undefined; renderer: string; sets: readonly string[];
  materialProfile?: string | undefined; recededProfile?: string | undefined;
}) {
  const m = readMembership(directory);
  for (const [name, canonical] of [["VITREA_SCENES", join(REFERENCE, "scenes.json")],
    ["VITREA_FIXTURES", join(REFERENCE, "fixtures")]] as const) {
    if (process.env[name] && resolve(process.env[name]!) !== canonical) {
      fail("wave-owned fixture or scene overrides cannot enter a declared canonical stage");
    }
  }
  if (!options.profileKeys?.length || options.profileKeys.some((p) => !m.profiles.includes(p)) ||
      !m.tiers.includes(options.renderer) || options.sets.some((s) => !m.sets.includes(s))) {
    fail("run outside declared profiles, tiers or sets; pass --profile explicitly");
  }
  if (!options.materialProfile || JSON.stringify(document(options.materialProfile)) !== JSON.stringify(m.active) ||
      JSON.stringify(options.recededProfile ? document(options.recededProfile) : undefined) !== JSON.stringify(m.receded)) {
    fail("run document digests differ from declaration");
  }
  stageStatus(directory);
}

/** Called only under the guard's publication lock. No writes occur in this preparation. */
export function prepareGeneration(directory: string, results: string) {
  const rows = readRows(stageMatrixPath(directory));
  const status = validateStageRows(directory, rows);
  if (status.missing) fail(`incomplete membership: ${status.present}/${status.declared}`);
  const m = status.membership;
  if (m.profiles.some((p) => !p.startsWith("apple-macos-27."))) fail("frozen profile cannot publish");
  // Ignore reader scratch overrides: publication always checks the complete authoritative history.
  loadCurrentRows({ resultsDir: results, matrixPath: join(results, "matrix.json") });
  const recorded = [...iterateRecordedRows({ resultsDir: results })];
  // Frozen aliases resolve from the frozen file, outside either index. An indexed
  // owner with the same hash would shadow that fallback even without a key clash.
  const frozenHashes = new Set(recorded.filter((r) => r.key.profileKey.startsWith("apple-macos-26.5-"))
    .flatMap((r) => { const d = documents(r); return [d.active.sha256, d.receded?.sha256]; }));
  if (frozenHashes.has(m.active.sha256) || (m.receded && frozenHashes.has(m.receded.sha256))) {
    fail("frozen document identity cannot acquire an indexed generation alias");
  }
  const keys = new Set(recorded.map((r) => serializeResultCellKey(r.key)));
  if (rows.some((r) => keys.has(serializeResultCellKey(r.key)))) fail("serialized key already exists in authoritative evidence");
  const index = readIndex(results, "generations");
  if (!index) fail("generation index is required");
  const all = [index, readIndex(results, "superseded")].filter((i): i is Index => !!i);
  const owners = all.flatMap((i) => Object.values(i.files));
  const activeOwners = owners.filter((e) => e.activeDocumentSha256 === m.active.sha256);
  const receded = (e: Entry) => e.documents.find((d) => d.sha256 !== e.activeDocumentSha256)?.sha256;
  if (activeOwners.some((e) => receded(e) === m.receded?.sha256)) fail("generation already published; append refused");
  const filename = `${m.active.sha256}${activeOwners.length && m.receded ? `-${m.receded.sha256}` : ""}.json`;
  if (existsSync(join(results, "generations", filename))) fail(`colliding generation filename ${filename}`);
  // A hash may gain an owner, never lose or change its role/path. Historical primary aliases stay put.
  for (const d of [m.active, ...(m.receded ? [m.receded] : [])]) {
    for (const owner of owners.filter((e) => e.documents.some((old) => old.sha256 === d.sha256))) {
      if (!owner.documents.some((old) => old.sha256 === d.sha256 && old.path === d.path) ||
          (owner.activeDocumentSha256 === d.sha256) !== (d === m.active)) fail("alias repoint or document role change refused");
    }
  }
  const raw = generationEnvelope(rows);
  const counts: Record<string, number> = {};
  for (const row of rows) counts[row.key.profileKey] = (counts[row.key.profileKey] ?? 0) + 1;
  const files: Record<string, Entry> = { ...index.files };
  const current = { ...index.currentByProfile };
  for (const profile of m.profiles) {
    const previous = current[profile];
    if (previous) {
      if (Object.keys(files[previous]!.rowsByProfileKey).some((p) => !m.profiles.includes(p))) {
        fail("publication must replace the previous generation's whole profile membership");
      }
      files[previous] = { ...files[previous]!, status: "retired" };
    }
    current[profile] = filename;
  }
  files[filename] = { activeDocumentSha256: m.active.sha256,
    documents: [m.active, ...(m.receded ? [m.receded] : [])], bytes: raw.length, sha256: sha(raw),
    rowCount: rows.length, rowsByProfileKey: counts, status: "current" };
  const aliases = { ...index.byDocumentSha256 };
  for (const d of files[filename]!.documents) {
    const held = aliases[d.sha256];
    aliases[d.sha256] = held ? [...new Set([...(typeof held === "string" ? [held] : held), filename])] : filename;
  }
  const next = { ...index, files, byDocumentSha256: aliases, currentByProfile: current };
  return { filename, raw, index: Buffer.from(`${JSON.stringify(next, null, 2)}\n`),
    sha256: sha(raw), bytes: raw.length };
}
