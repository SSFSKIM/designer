/**
 * Measurement is scratch-only. The one sanctioned publication entry below
 * preserves the same filesystem-identity boundary as the scratch refusal.
 */
import { closeSync, existsSync, fsyncSync, lstatSync, mkdirSync, openSync, readdirSync, realpathSync, renameSync, rmdirSync, statSync, unlinkSync, writeFileSync } from "node:fs";
import { dirname, extname, isAbsolute, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { randomUUID } from "node:crypto";
import { prepareGeneration } from "./generation-stage";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const FROZEN_MATRIX = destinationPath(resolve(PACKAGE_ROOT, "results/matrix.json"));
const GENERATIONS_DIR = destinationPath(resolve(PACKAGE_ROOT, "results/generations"));
const SUPERSEDED_DIR = destinationPath(resolve(PACKAGE_ROOT, "results/superseded"));

/** Canonicalize the longest existing prefix, including symlinked parent directories. */
function destinationPath(path: string): string {
  const absolute = resolve(path);
  if (existsSync(absolute)) return realpathSync.native(absolute);
  const parent = dirname(absolute);
  if (parent === absolute) return absolute;
  return resolve(destinationPath(parent), relative(parent, absolute));
}

function insideJsonDirectory(directory: string, path: string): boolean {
  const within = relative(directory, path);
  return within !== "" && within !== ".." && !within.startsWith(`..${sep}`)
    && !isAbsolute(within) && extname(path).toLowerCase() === ".json";
}

function isCanonicalJson(path: string): boolean {
  return path === FROZEN_MATRIX || insideJsonDirectory(GENERATIONS_DIR, path)
    || insideJsonDirectory(SUPERSEDED_DIR, path);
}

/** Files with different names can still be the same writable inode (including hardlinks). */
export function sameFilesystemFile(path: string, other: string): boolean {
  if (!existsSync(path) || !existsSync(other)) return false;
  const candidate = statSync(path);
  const authority = statSync(other);
  return candidate.dev === authority.dev && candidate.ino === authority.ino;
}

function isCanonicalFileIdentity(path: string): boolean {
  if (!existsSync(path)) return false;
  if (sameFilesystemFile(path, FROZEN_MATRIX)) return true;
  for (const directory of [GENERATIONS_DIR, SUPERSEDED_DIR]) {
    if (!existsSync(directory)) continue;
    for (const name of readdirSync(directory)) {
      if (extname(name).toLowerCase() === ".json" && sameFilesystemFile(path, join(directory, name))) {
        return true;
      }
    }
  }
  return false;
}

/** Throw before any write to the frozen matrix or immutable recorded generation JSON. */
export function assertScratchDestination(path: string): void {
  const absolute = resolve(path);
  if (isCanonicalJson(absolute) || isCanonicalJson(destinationPath(absolute)) ||
      isCanonicalFileIdentity(absolute)) {
    throw new Error(
      `${absolute} is canonical, immutable matrix evidence; G1's publisher must publish ` +
      "complete generations. Measurement accepts only a separate scratch JSON destination.",
    );
  }
}

/**
 * The only canonical writer. The index is the commit point: both complete files
 * are fsynced before installation and the index moves last. A caught failure
 * rolls back the unindexed generation. A process crash before the index rename
 * can leave only a complete, unindexed orphan (never authoritative partial rows);
 * its colliding name fails closed on retry and needs operator inspection.
 */
export function publishGeneration(stage: string): { file: string; sha256: string; bytes: number } {
  const directory = resolve(PACKAGE_ROOT, "results/generations");
  const index = join(directory, "index.json");
  // Use the same identity predicates as scratch refusal, with a narrower grant:
  // one fresh generation and this regular, unaliased index, never another inode.
  if (destinationPath(directory) !== directory || !isCanonicalJson(index) ||
      lstatSync(index).isSymbolicLink() || statSync(index).nlink !== 1 ||
      sameFilesystemFile(index, FROZEN_MATRIX)) throw new Error("publisher: aliased canonical destination refused");
  for (const dir of [GENERATIONS_DIR, SUPERSEDED_DIR]) {
    if (!existsSync(dir)) continue;
    for (const name of readdirSync(dir)) {
      const path = join(dir, name);
      if (path !== index && sameFilesystemFile(index, path)) throw new Error("publisher: index aliases immutable evidence");
    }
  }
  const lock = join(directory, ".publish-lock");
  mkdirSync(lock); // Serialises preflight and installation; a crash leaves an explicit stale lock.
  const token = randomUUID();
  const tempFile = join(directory, `.${token}.generation.tmp`);
  const tempIndex = join(directory, `.${token}.index.tmp`);
  let installed: string | undefined;
  let committed = false;
  try {
    const prepared = prepareGeneration(stage, resolve(PACKAGE_ROOT, "results"));
    const target = join(directory, prepared.filename);
    if (!isCanonicalJson(target) || destinationPath(target) !== target || existsSync(target)) {
      throw new Error("publisher: colliding or aliased target");
    }
    for (const [path, raw] of [[tempFile, prepared.raw], [tempIndex, prepared.index]] as const) {
      const fd = openSync(path, "wx");
      try { writeFileSync(fd, raw); fsyncSync(fd); } finally { closeSync(fd); }
    }
    renameSync(tempFile, target);
    installed = target;
    syncDirectory(directory);
    renameSync(tempIndex, index);
    committed = true;
    syncDirectory(directory);
    return { file: target, sha256: prepared.sha256, bytes: prepared.bytes };
  } catch (error) {
    if (installed && !committed) { unlinkSync(installed); syncDirectory(directory); }
    throw error;
  } finally {
    for (const path of [tempFile, tempIndex]) if (existsSync(path)) unlinkSync(path);
    rmdirSync(lock);
  }
}
function syncDirectory(path: string) {
  const fd = openSync(path, "r");
  try { fsyncSync(fd); } finally { closeSync(fd); }
}
