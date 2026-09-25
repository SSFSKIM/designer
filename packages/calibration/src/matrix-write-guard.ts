/**
 * G0 cannot publish canonical generations. Refuse their write targets before a
 * capture or measurement, including paths reached through existing symlinks.
 */
import { existsSync, readdirSync, realpathSync, statSync } from "node:fs";
import { dirname, extname, isAbsolute, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

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
      "complete generations. G0 accepts only a separate scratch JSON destination.",
    );
  }
}
