import { createHash } from "node:crypto";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, symlinkSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, expect, test } from "vitest";
import type { CellResult } from "../src/report";
import { loadCurrentRows, loadGeneration, legacyEnvelopeDigest, iterateRecordedRows } from "../src/matrix-store";

const A = "aaaaaaaaaaaa", B = "bbbbbbbbbbbb", R = "cccccccccccc", S = "dddddddddddd";
const dirs: string[] = [];
afterEach(() => { for (const d of dirs.splice(0)) rmSync(d, { recursive: true, force: true }); });
function row(active = A, receded: string | null = R, scene = "x", frozen = false): CellResult {
  return { key: { profileKey: frozen ? "apple-macos-26.5-1x-light-standard" : "apple-macos-27.0-1x-light-standard-glass0.5", sceneId: scene,
    web: { engine: "chromium", engineVersion: "1", renderer: "webgpu", samplingBackend: "gpu-texture", gpuAdapter: "test", colorSpace: "srgb",
      capturePath: `materialProfile=profiles/active.json sha256:${active}${receded ? ` recededProfile=profiles/receded.json sha256:${receded}` : ""}` } },
    tier: "texture", fixtureSet: "calibration", capturedAt: "test" } as CellResult;
}
const sha = (s: string) => createHash("sha256").update(s).digest("hex");
const text = (rows: CellResult[]) => JSON.stringify({ schemaVersion: 5, cells: rows }, null, 2) + "\n";
function fixture() {
  const dir = mkdtempSync(join(tmpdir(), "matrix-store-")); dirs.push(dir);
  mkdirSync(join(dir, "generations")); mkdirSync(join(dir, "superseded"));
  writeFileSync(join(dir, "matrix.json"), text([row("eeeeeeeeeeee", null, "frozen", true)]));
  const index = { schemaVersion: 1, files: {} as Record<string, object>, byDocumentSha256: {} as Record<string, string[]>, currentByProfile: {} as Record<string, string> };
  function add(active = A, receded: string | null = R, current = true, filename = `${active}.json`) {
    const rows = [row(active, receded)]; const raw = text(rows);
    writeFileSync(join(dir, "generations", filename), raw);
    index.files[filename] = { activeDocumentSha256: active,
      documents: [{ path: "profiles/active.json", sha256: active }, ...(receded ? [{ path: "profiles/receded.json", sha256: receded }] : [])],
      rowCount: 1, rowsByProfileKey: { [rows[0]!.key.profileKey]: 1 }, bytes: Buffer.byteLength(raw), sha256: sha(raw), status: current ? "current" : "retired" };
    for (const h of [active, ...(receded ? [receded] : [])]) (index.byDocumentSha256[h] ??= []).push(filename);
    if (current) index.currentByProfile[rows[0]!.key.profileKey] = filename;
    save(); return filename;
  }
  function save() { writeFileSync(join(dir, "generations/index.json"), JSON.stringify(index)); }
  return { dir, index, add, save, options: { resultsDir: dir } };
}
test("both layouts preserve exact legacy envelope bytes without serializing rows", () => {
  const f = fixture(); rmSync(join(f.dir, "generations"), { recursive: true });
  const raw = text([row("eeeeeeeeeeee", null, "frozen", true), row()]);
  writeFileSync(join(f.dir, "matrix.json"), raw);
  expect(legacyEnvelopeDigest(loadCurrentRows(f.options))).toBe(sha(raw));
  mkdirSync(join(f.dir, "generations")); f.add();
  writeFileSync(join(f.dir, "matrix.json"), text([row("eeeeeeeeeeee", null, "frozen", true)]));
  expect(loadCurrentRows(f.options)).toHaveLength(2);
  expect(legacyEnvelopeDigest(loadCurrentRows(f.options))).toBe(sha(raw));
});
test("reseals keep every owner and refuse ambiguous active and receded aliases", () => {
  const f = fixture(); f.add(A, R, false); f.add(B, R, false); f.add(A, S, true, `${A}-${S}.json`);
  expect(() => loadGeneration(A, undefined, f.options)).toThrow(/ambiguous/i);
  expect(() => loadGeneration(R, undefined, f.options)).toThrow(/ambiguous/i);
  expect(loadGeneration(A, R, f.options)[0]!.key.web.capturePath).toContain(R);
  expect(loadGeneration(A, S, f.options)[0]!.key.web.capturePath).toContain(S);
  expect(loadGeneration(B, R, f.options)).toHaveLength(1);
  expect([...iterateRecordedRows(f.options)]).toHaveLength(4);
});
test("missing file and altered bytes are refused", () => {
  const f = fixture(); const name = f.add();
  writeFileSync(join(f.dir, "generations", name), "{}");
  expect(() => loadCurrentRows(f.options)).toThrow(/bytes|hash|sha/i);
  rmSync(join(f.dir, "generations", name));
  expect(() => loadCurrentRows(f.options)).toThrow();
});
test("duplicates and generation rows filed under frozen are refused", () => {
  const f = fixture(); f.add();
  writeFileSync(join(f.dir, "matrix.json"), text([row()]));
  expect(() => loadCurrentRows(f.options)).toThrow(/frozen|duplicate/i);
});
test("scratch override bypasses the indexed layout but not schema validation", () => {
  const f = fixture(); f.add(); const path = join(f.dir, "scratch.json");
  writeFileSync(path, text([row(B)]));
  expect(loadCurrentRows({ ...f.options, matrixPath: path })).toEqual([row(B)]);
  process.env["VITREA_MATRIX_PATH"] = path;
  try { expect(loadCurrentRows(f.options)).toEqual([row(B)]); }
  finally { delete process.env["VITREA_MATRIX_PATH"]; }
  writeFileSync(path, '{"schemaVersion":4,"cells":[]}');
  expect(() => loadCurrentRows({ matrixPath: path })).toThrow(/schema/i);
});
test("archive sharedReceded owners join current aliases without repointing history", () => {
  const f = fixture(); const old = f.add(A, R, false);
  const newer = f.add(B, R);
  const archived = f.index.files[old];
  const raw = text([row(A, R)]);
  writeFileSync(join(f.dir, "superseded", old), raw);
  writeFileSync(join(f.dir, "superseded/index.json"), JSON.stringify({
    files: { [old]: archived }, byDocumentSha256: { [A]: old, [R]: old }, sharedReceded: { [R]: [old] },
  }));
  delete f.index.files[old]; delete f.index.byDocumentSha256[A]; f.index.byDocumentSha256[R] = [newer]; f.save();
  expect(() => loadGeneration(R, undefined, f.options)).toThrow(/ambiguous/i);
  expect(loadGeneration(A, R, f.options)).toEqual([row(A, R)]);
  expect(loadGeneration(B, R, f.options)).toEqual([row(B, R)]);
});
test("a hash-valid file cannot claim another generation or omit its receded clause", () => {
  const f = fixture(); const name = f.add();
  for (const replacement of [row(B, R), row(A, null)]) {
    const raw = text([replacement]);
    writeFileSync(join(f.dir, "generations", name), raw);
    Object.assign(f.index.files[name]!, { bytes: Buffer.byteLength(raw), sha256: sha(raw) }); f.save();
    expect(() => loadCurrentRows(f.options)).toThrow(/ownership|completeness/i);
  }
});
test("duplicate keys inside a file are rejected rather than overwritten", () => {
  const f = fixture(); const name = f.add(); const raw = text([row(), row()]);
  writeFileSync(join(f.dir, "generations", name), raw);
  Object.assign(f.index.files[name]!, { bytes: Buffer.byteLength(raw), sha256: sha(raw), rowCount: 2 }); f.save();
  expect(() => loadCurrentRows(f.options)).toThrow(/duplicate/i);
});
test("an omitted owner alias and incomplete profile selection are rejected", () => {
  const f = fixture(); f.add(); delete f.index.byDocumentSha256[R]; f.save();
  expect(() => loadCurrentRows(f.options)).toThrow(/aliases/i);
  f.index.byDocumentSha256[R] = [`${A}.json`]; f.index.currentByProfile = {}; f.save();
  expect(() => loadCurrentRows(f.options)).toThrow(/selection/i);
});
test("an empty scratch matrix has the ordinary empty legacy envelope", () => {
  const f = fixture(); const path = join(f.dir, "empty.json"); const raw = text([]);
  writeFileSync(path, raw);
  expect(legacyEnvelopeDigest(loadCurrentRows({ matrixPath: path }))).toBe(sha(raw));
});
test("a generation without receded document and an active-only reseal remain addressable", () => {
  const f = fixture(); f.add(A, null, false); f.add(B, null);
  expect(loadGeneration(A, undefined, f.options)).toEqual([row(A, null)]);
  expect(loadGeneration(B, undefined, f.options)).toEqual([row(B, null)]);
  expect(loadCurrentRows(f.options).map(r => r.key.web.capturePath)).toContain(row(B, null).key.web.capturePath);
});
test("both historical sharedReceded owners resolve with qualified identities", () => {
  const f = fixture(); const one = f.add(A, R, false); const two = f.add(B, R, false);
  const archive = { files: { ...f.index.files }, byDocumentSha256: { [A]: one, [B]: two, [R]: one }, sharedReceded: { [R]: [one, two] } };
  for (const [name, active] of [[one, A], [two, B]]) writeFileSync(join(f.dir, "superseded", name!), text([row(active!, R)]));
  writeFileSync(join(f.dir, "superseded/index.json"), JSON.stringify(archive));
  f.index.files = {}; f.index.byDocumentSha256 = {}; f.save();
  expect(() => loadGeneration(R, undefined, f.options)).toThrow(/ambiguous/i);
  expect(loadGeneration(A, R, f.options)).toEqual([row(A, R)]);
  expect(loadGeneration(B, R, f.options)).toEqual([row(B, R)]);
});
test("an explicit null qualifier resolves the no-receded member of an ambiguous active alias", () => {
  const f = fixture(); f.add(A, null, false); f.add(A, R, true, `${A}-${R}.json`);
  expect(() => loadGeneration(A, undefined, f.options)).toThrow(/ambiguous/i);
  expect(loadGeneration(A, null, f.options)).toEqual([row(A, null)]);
  expect(loadGeneration(A, R, f.options)).toEqual([row(A, R)]);
});

test("an explicit symlink to the frozen authority still reads the current union", () => {
  const f = fixture(); f.add(); const alias = join(f.dir, "alias.json");
  symlinkSync(join(f.dir, "matrix.json"), alias);
  expect(loadCurrentRows({ ...f.options, matrixPath: alias })).toHaveLength(2);
});
